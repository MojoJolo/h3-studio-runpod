#!/usr/bin/env python3
"""H3 Studio — a localhost GUI for the h3.c engine.

Stdlib only. Serves gui/index.html, queues generation jobs, shells out to
../h3 (argv list, no shell), parses its \r progress stream, and broadcasts
state over Server-Sent Events. History (prompt + settings + output) is
appended to gui/history.jsonl so prompts are never lost.

Run via the ./studio launcher in the repo root (binds 127.0.0.1 only).
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import pty
import queue as queue_mod
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GUI_DIR = os.path.dirname(os.path.abspath(__file__))
H3_ROOT = os.path.dirname(GUI_DIR)
H3_BIN = os.path.join(H3_ROOT, "h3")
MODEL_DIR = "MiniMax-H3"
OUTPUTS = os.path.join(H3_ROOT, "outputs")
INPUTS = os.path.join(H3_ROOT, "inputs")
HISTORY = os.path.join(GUI_DIR, "history.jsonl")
PORT = 7833

VALID_REUSE = {1, 2, 3}
VALID_LAYERS = {50, 45, 40}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

PROGRESS_RE = re.compile(rb"([A-Za-z][A-Za-z0-9 _-]*?)\s+(\d+)/(\d+)\s*$")
ANSI_RE = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")


def now_ms():
    return int(time.time() * 1000)


def safe_name(name):
    base = os.path.basename(name)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._") or "file"
    return base


class Broadcaster:
    def __init__(self):
        self.lock = threading.Lock()
        self.clients = []

    def subscribe(self):
        q = queue_mod.Queue(maxsize=500)
        with self.lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            if q in self.clients:
                self.clients.remove(q)

    def publish(self, event):
        data = json.dumps(event)
        with self.lock:
            clients = list(self.clients)
        for q in clients:
            try:
                q.put_nowait(data)
            except queue_mod.Full:
                pass


class JobRunner:
    def __init__(self, bus):
        self.bus = bus
        self.lock = threading.Lock()
        self.pending = []
        self.current = None
        self.proc = None
        self.counter = 0
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()

    def snapshot(self):
        with self.lock:
            return {
                "current": dict(self.current) if self.current else None,
                "pending": [dict(j) for j in self.pending],
            }

    def enqueue(self, job):
        with self.lock:
            self.counter += 1
            job["id"] = self.counter
            job["state"] = "pending"
            self.pending.append(job)
        self.bus.publish({"type": "queue", **self.snapshot()})
        return job["id"]

    def cancel(self, job_id):
        # NB: never call snapshot()/publish while holding self.lock —
        # snapshot() re-acquires the (non-reentrant) lock and deadlocks
        # the whole server. Decide under the lock, publish after.
        result = "not-found"
        with self.lock:
            for j in list(self.pending):
                if j["id"] == job_id:
                    self.pending.remove(j)
                    result = "removed"
                    break
            else:
                if self.current and self.current["id"] == job_id and self.proc:
                    try:
                        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                    except Exception:
                        pass
                    result = "terminating"
        if result == "removed":
            self.bus.publish({"type": "queue", **self.snapshot()})
        return result

    def shutdown(self):
        with self.lock:
            if self.proc:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                except Exception:
                    pass

    def _loop(self):
        while True:
            job = None
            with self.lock:
                if self.pending:
                    job = self.pending.pop(0)
                    job["state"] = "running"
                    job["started"] = now_ms()
                    self.current = job
            if not job:
                time.sleep(0.2)
                continue
            self.bus.publish({"type": "queue", **self.snapshot()})
            ok, error, elapsed = self._run(job)
            entry = {
                "id": job["id"],
                "ts": now_ms(),
                "ok": ok,
                "error": error,
                "elapsed_s": round(elapsed, 1),
                "prompt": job["prompt"],
                "mode": job["mode"],
                "params": job["params"],
                "refs": job.get("refs", []),
                "first_frame": job.get("first_frame"),
                "last_frame": job.get("last_frame"),
                "file": job["outfile"] if ok else None,
            }
            with HISTORY_LOCK:
                with open(HISTORY, "a") as fh:
                    fh.write(json.dumps(entry) + "\n")
            if ok:
                try:
                    append_bench(entry)
                except Exception as exc:
                    print(f"benchmarks.md append failed: {exc}", flush=True)
            with self.lock:
                self.current = None
                self.proc = None
            self.bus.publish({"type": "done", "entry": entry})
            self.bus.publish({"type": "queue", **self.snapshot()})

    def _argv(self, job):
        p = job["params"]
        argv = [
            H3_BIN, "-d", MODEL_DIR,
            "-p", job["prompt"],
            "--width", str(p["width"]), "--height", str(p["height"]),
            "--frames", str(p["frames"]),
            "--steps", str(p["steps"]), "--reuse", str(p["reuse"]),
            "--layers", str(p["layers"]), "--seed", str(p["seed"]),
            "-o", job["outfile"],
        ]
        if p.get("ssd_streaming", True):
            argv.append("--ssd-streaming")
        if job["mode"] == "firstlast":
            if job.get("first_frame"):
                argv += ["--first-frame", job["first_frame"]]
            if job.get("last_frame"):
                argv += ["--last-frame", job["last_frame"]]
        elif job["mode"] == "refs":
            for ref in job.get("refs", []):
                argv += ["--ref-image", ref]
        return argv

    def _run(self, job):
        started = time.time()
        # Run h3 under a pseudo-terminal: to a plain pipe its C stdio
        # block-buffers progress prints (updates arrive minutes late, in
        # bursts); a pty makes it flush like it does in Terminal.
        master, slave = pty.openpty()
        try:
            self.proc = subprocess.Popen(
                self._argv(job), cwd=H3_ROOT,
                stdout=slave, stderr=slave,
                start_new_session=True,
            )
        except Exception as exc:
            os.close(master)
            os.close(slave)
            return False, f"failed to launch h3: {exc}", 0.0
        os.close(slave)
        buf = b""
        tail = []
        last_pub = 0.0
        while True:
            try:
                chunk = os.read(master, 1024)
            except OSError:
                chunk = b""
            if not chunk:
                break
            buf += chunk
            while True:
                cut = -1
                for sep in (b"\r", b"\n"):
                    i = buf.find(sep)
                    if i != -1 and (cut == -1 or i < cut):
                        cut = i
                if cut == -1:
                    break
                line, buf = buf[:cut], buf[cut + 1:]
                line = ANSI_RE.sub(b"", line)
                if not line.strip():
                    continue
                text = line.decode("utf-8", "replace").strip()
                tail.append(text)
                if len(tail) > 30:
                    tail.pop(0)
                m = PROGRESS_RE.search(line.strip())
                if m and time.time() - last_pub > 0.15:
                    last_pub = time.time()
                    self.bus.publish({
                        "type": "progress", "job": job["id"],
                        "phase": m.group(1).decode("utf-8", "replace").strip(),
                        "done": int(m.group(2)), "total": int(m.group(3)),
                        "elapsed": round(time.time() - started, 1),
                    })
        os.close(master)
        code = self.proc.wait()
        elapsed = time.time() - started
        if code == 0 and os.path.isfile(os.path.join(H3_ROOT, job["outfile"])):
            return True, None, elapsed
        err = next((t for t in reversed(tail) if t.startswith("h3:")), None)
        if code < 0:
            err = "canceled"
        return False, err or f"h3 exited with code {code}", elapsed


BUS = Broadcaster()
RUNNER = JobRunner(BUS)
try:
    _max_id = 0
    if os.path.isfile(HISTORY):
        with open(HISTORY) as _fh:
            for _line in _fh:
                _line = _line.strip()
                if _line:
                    _max_id = max(_max_id, json.loads(_line).get("id", 0))
    RUNNER.counter = _max_id
except Exception:
    RUNNER.counter = int(time.time()) % 100000
HISTORY_LOCK = threading.Lock()
BENCH = os.path.join(H3_ROOT, "benchmarks.md")
BENCH_HEADER = (
    "# H3 Generation Log\n\n"
    "Appended automatically by H3 Studio on every successful render "
    "(CLI runs are not logged). The `notes` column is yours to edit.\n\n"
    "| when | mode | size | MP | frames | steps | reuse | layers | memory | time | notes |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def bench_row(entry):
    p = entry["params"]
    mp = p["width"] * p["height"] / 1e6
    secs = float(entry["elapsed_s"])
    t = f"{int(secs // 60)}m{int(round(secs % 60)):02d}s"
    mode = {"text": "text", "firstlast": "first/last",
            "refs": f"refs x{len(entry.get('refs') or [])}"}.get(entry["mode"], entry["mode"])
    mem = "ssd-stream" if p.get("ssd_streaming", True) else "resident"
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(entry["ts"] / 1000))
    return (f"| {when} | {mode} | {p['width']}x{p['height']} | {mp:.2f} | {p['frames']} "
            f"| {p['steps']} | {p['reuse']} | {p['layers']} | {mem} | {t} |  |\n")


def parse_bench():
    rows = []
    if not os.path.isfile(BENCH):
        return rows
    with open(BENCH) as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("|") or line.startswith("|--") or "| when |" in line:
                continue
            c = [x.strip() for x in line.split("|")[1:-1]]
            if len(c) < 10:
                continue
            try:
                w, h = c[2].split("x")
                m = re.match(r"(\d+)m(\d+)s", c[9])
                rows.append({
                    "memory": c[8], "mp": float(c[3]), "frames": int(c[4]),
                    "steps": int(c[5]), "reuse": int(c[6]), "layers": int(c[7]),
                    "secs": int(m.group(1)) * 60 + int(m.group(2)) if m else None,
                })
            except (ValueError, AttributeError, IndexError):
                continue
    return [r for r in rows if r["secs"]]


def append_bench(entry):
    with HISTORY_LOCK:
        fresh = not os.path.isfile(BENCH)
        with open(BENCH, "a") as fh:
            if fresh:
                fh.write(BENCH_HEADER)
            fh.write(bench_row(entry))


def trash_file(name):
    """Move an outputs/ file to the macOS Trash (recoverable, never rm)."""
    full = os.path.join(OUTPUTS, safe_name(os.path.basename(name)))
    if not os.path.isfile(full):
        return False
    script = f'tell application "Finder" to delete POSIX file "{full}"'
    subprocess.run(["osascript", "-e", script], check=False,
                   capture_output=True, timeout=15)
    return not os.path.isfile(full)


def delete_history(ids=None, delete_all=False):
    with HISTORY_LOCK:
        entries = []
        if os.path.isfile(HISTORY):
            with open(HISTORY) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except ValueError:
                            pass
        if delete_all:
            removed, kept = entries, []
        else:
            wanted = set(ids or [])
            removed = [e for e in entries if e.get("ts") in wanted]
            kept = [e for e in entries if e.get("ts") not in wanted]
        with open(HISTORY, "w") as fh:
            for e in kept:
                fh.write(json.dumps(e) + "\n")
    trashed = 0
    for e in removed:
        if e.get("file") and trash_file(e["file"]):
            trashed += 1
    return len(removed), trashed


def read_history(limit=200):
    entries = []
    if os.path.isfile(HISTORY):
        with open(HISTORY) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except ValueError:
                        pass
    return entries[-limit:][::-1]


def validate_job(data):
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        raise ValueError("prompt is empty")
    mode = data.get("mode", "text")
    if mode not in ("text", "firstlast", "refs"):
        raise ValueError("bad mode")
    p = data.get("params") or {}

    def as_int(key, lo, hi, default=None):
        v = p.get(key, default)
        try:
            v = int(v)
        except (TypeError, ValueError):
            raise ValueError(f"{key} must be an integer")
        if not (lo <= v <= hi):
            raise ValueError(f"{key} out of range [{lo}, {hi}]")
        return v

    width = as_int("width", 256, 1536)
    height = as_int("height", 256, 1536)
    if width % 32 or height % 32:
        raise ValueError("width and height must be multiples of 32")
    frames = as_int("frames", 22, 361)
    if (frames - 5) % 17:
        frames = 22 + 17 * max(0, round((frames - 22) / 17))
    steps = as_int("steps", 1, 60)
    reuse = as_int("reuse", 1, 3)
    if reuse not in VALID_REUSE:
        raise ValueError("reuse must be 1, 2 or 3")
    layers = as_int("layers", 40, 50)
    if layers not in VALID_LAYERS:
        raise ValueError("layers must be 50, 45 or 40")
    seed = as_int("seed", 0, 2**63 - 1, 42)

    def check_input(rel):
        if not rel:
            return None
        rel = os.path.join("inputs", safe_name(rel))
        if not os.path.isfile(os.path.join(H3_ROOT, rel)):
            raise ValueError(f"missing input image: {rel}")
        return rel

    refs = [check_input(r) for r in (data.get("refs") or [])][:9]
    refs = [r for r in refs if r]
    first = check_input(data.get("first_frame"))
    last = check_input(data.get("last_frame"))
    if mode == "refs" and not refs:
        raise ValueError("references mode needs at least one image")
    if mode == "firstlast" and not first and not last:
        raise ValueError("first/last mode needs at least one anchor image")

    stamp = time.strftime("%Y%m%d-%H%M%S")
    outfile = f"outputs/gui-{stamp}-seed{seed}.mp4"
    return {
        "prompt": prompt, "mode": mode,
        "params": {
            "width": width, "height": height, "frames": frames,
            "steps": steps, "reuse": reuse, "layers": layers,
            "seed": seed, "ssd_streaming": bool(p.get("ssd_streaming", True)),
        },
        "refs": refs if mode == "refs" else [],
        "first_frame": first if mode == "firstlast" else None,
        "last_frame": last if mode == "firstlast" else None,
        "outfile": outfile,
    }


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            return self._file(os.path.join(GUI_DIR, "index.html"), "text/html; charset=utf-8")
        if path == "/api/bench":
            return self._json(parse_bench())
        if path == "/benchmarks":
            return self._bench_page()
        if path == "/api/state":
            return self._json({"queue": RUNNER.snapshot(), "history": read_history()})
        if path == "/api/events":
            return self._sse()
        if path.startswith("/videos/"):
            name = safe_name(path[len("/videos/"):])
            return self._file(os.path.join(OUTPUTS, name), "video/mp4", ranged=True)
        if path.startswith("/inputs/"):
            name = safe_name(path[len("/inputs/"):])
            ext = os.path.splitext(name)[1].lower()
            ctype = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                     ".webp": "image/webp", ".bmp": "image/bmp",
                     ".tiff": "image/tiff"}.get(ext, "application/octet-stream")
            return self._file(os.path.join(INPUTS, name), ctype)
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            if path == "/api/generate":
                job = validate_job(json.loads(self._body() or b"{}"))
                job_id = RUNNER.enqueue(job)
                return self._json({"ok": True, "id": job_id, "outfile": job["outfile"]})
            if path == "/api/upload":
                from urllib.parse import parse_qs, urlparse
                q = parse_qs(urlparse(self.path).query)
                name = safe_name((q.get("name") or ["image.png"])[0])
                ext = os.path.splitext(name)[1].lower()
                if ext not in IMAGE_EXT:
                    return self._json({"error": f"unsupported image type {ext}"}, 400)
                data = self._body()
                if not data or len(data) > 64 * 1024 * 1024:
                    return self._json({"error": "empty or oversized upload"}, 400)
                digest = hashlib.sha256(data).hexdigest()[:10]
                # reuse ANY existing input holding these bytes, whatever its
                # name (covers files that predate hash-prefixed naming)
                for existing in os.listdir(INPUTS):
                    fe = os.path.join(INPUTS, existing)
                    if not os.path.isfile(fe) or os.path.getsize(fe) != len(data):
                        continue
                    with open(fe, "rb") as fh:
                        if hashlib.sha256(fh.read()).hexdigest()[:10] == digest:
                            return self._json({"ok": True, "name": existing})
                final = f"{digest}-{name}"
                with open(os.path.join(INPUTS, final), "wb") as fh:
                    fh.write(data)
                return self._json({"ok": True, "name": final})
            if path == "/api/cancel":
                data = json.loads(self._body() or b"{}")
                return self._json({"ok": True, "result": RUNNER.cancel(int(data.get("id", 0)))})
            if path == "/api/delete":
                data = json.loads(self._body() or b"{}")
                removed, trashed = delete_history(
                    ids=[int(i) for i in (data.get("ts") or [])],
                    delete_all=bool(data.get("all")),
                )
                return self._json({"ok": True, "removed": removed, "trashed": trashed})
            if path == "/api/shutdown":
                data = json.loads(self._body() or b"{}")
                busy = RUNNER.snapshot()["current"] is not None
                if busy and not data.get("force"):
                    return self._json({"ok": False, "running": True})
                self._json({"ok": True})
                def stop():
                    print("H3 Studio: shutdown requested via /api/shutdown (Quit button)", flush=True)
                    RUNNER.shutdown()
                    SERVER[0].shutdown()
                threading.Thread(target=stop, daemon=True).start()
                return
            if path == "/api/reveal":
                data = json.loads(self._body() or b"{}")
                name = safe_name(os.path.basename(data.get("file") or ""))
                full = os.path.join(OUTPUTS, name)
                if not os.path.isfile(full):
                    return self._json({"error": "file not found"}, 404)
                subprocess.run(["open", "-R", full], check=False)
                return self._json({"ok": True})
            self._json({"error": "not found"}, 404)
        except ValueError as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"server error: {exc}"}, 500)

    def _bench_page(self):
        rows = []
        if os.path.isfile(BENCH):
            with open(BENCH) as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith("|") and not line.startswith("|--") and "| when |" not in line:
                        rows.append([c.strip() for c in line.split("|")[1:-1]])
        def sort_key(cells, i):
            v = cells[i] if i < len(cells) else ""
            m = re.match(r"(\d+)m(\d+)s", v)
            if m:
                return str(int(m.group(1)) * 60 + int(m.group(2))).rjust(8, "0")
            try:
                return ("%012.4f" % float(v))
            except ValueError:
                return v
        body_rows = "".join(
            "<tr>" + "".join(
                f'<td data-s="{sort_key(r, i)}">{c}</td>' for i, c in enumerate(r)
            ) + "</tr>" for r in rows
        )
        heads = ["when", "mode", "size", "MP", "frames", "steps", "reuse",
                 "layers", "memory", "time", "notes"]
        page = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>H3 Benchmarks</title>
<script>(function () {{ const t = localStorage.getItem("h3theme"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; }})();</script>
<style>
:root {{ --bg:#F7F8F6; --ink:#1C2320; --muted:#5A6660; --accent:#0F7B5F; --border:#D8DED9; --card:#FFF; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#121614; --ink:#E4EAE5; --muted:#93A099; --accent:#4FCB9B; --border:#2A322D; --card:#171C19; }} }}
:root[data-theme="dark"] {{ --bg:#121614; --ink:#E4EAE5; --muted:#93A099; --accent:#4FCB9B; --border:#2A322D; --card:#171C19; }}
body {{ background:var(--bg); color:var(--ink); font-family:-apple-system,system-ui,sans-serif; margin:0; padding:2rem 1.4rem; }}
h1 {{ font-family:ui-monospace,Menlo,monospace; font-size:1.15rem; }}
p {{ color:var(--muted); font-size:0.85rem; }}
.wrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--border); border-radius:10px; }}
table {{ border-collapse:collapse; width:100%; font-size:0.85rem; font-variant-numeric:tabular-nums; }}
th, td {{ text-align:left; padding:0.5rem 0.8rem; border-bottom:1px solid var(--border); white-space:nowrap; }}
td:last-child {{ white-space:normal; min-width:12rem; }}
th {{ font-family:ui-monospace,Menlo,monospace; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em;
     color:var(--muted); cursor:pointer; position:sticky; top:0; background:var(--card); user-select:none; }}
th:hover {{ color:var(--accent); }}
tr:hover td {{ background:rgba(127,127,127,0.06); }}
</style></head><body>
<h1>H3 Benchmarks</h1>
<p>{len(rows)} renders · click a column header to sort · source of truth: <code>~/h3.c/benchmarks.md</code> (notes column editable there)</p>
<div class="wrap"><table id="t"><thead><tr>{"".join(f"<th>{h}</th>" for h in heads)}</tr></thead>
<tbody>{body_rows}</tbody></table></div>
<script>
document.querySelectorAll("th").forEach((th, i) => {{
  let dir = 1;
  th.onclick = () => {{
    const tb = document.querySelector("#t tbody");
    [...tb.rows].sort((a, b) => dir * (a.cells[i]?.dataset.s || "").localeCompare(b.cells[i]?.dataset.s || "", undefined, {{numeric: true}}))
      .forEach(r => tb.appendChild(r));
    dir = -dir;
  }};
}});
</script></body></html>"""
        data = page.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _file(self, full, ctype, ranged=False):
        if not os.path.isfile(full):
            return self._json({"error": "not found"}, 404)
        size = os.path.getsize(full)
        start, end = 0, size - 1
        status = 200
        rng = self.headers.get("Range") if ranged else None
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)$", rng.strip())
            if m:
                if m.group(1):
                    start = int(m.group(1))
                    if m.group(2):
                        end = min(int(m.group(2)), size - 1)
                elif m.group(2):
                    start = max(0, size - int(m.group(2)))
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                status = 206
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        with open(full, "rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                remaining -= len(chunk)

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        q = BUS.subscribe()
        try:
            hello = json.dumps({"type": "queue", **RUNNER.snapshot()})
            self.wfile.write(f"data: {hello}\n\n".encode())
            self.wfile.flush()
            while True:
                try:
                    data = q.get(timeout=15)
                    self.wfile.write(f"data: {data}\n\n".encode())
                except queue_mod.Empty:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            BUS.unsubscribe(q)


SERVER = [None]


def main():
    os.makedirs(OUTPUTS, exist_ok=True)
    os.makedirs(INPUTS, exist_ok=True)
    if not os.access(H3_BIN, os.X_OK):
        sys.exit(f"h3 binary not found/executable at {H3_BIN}")
    url = f"http://127.0.0.1:{PORT}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        if exc.errno == 48:
            print(f"H3 Studio is already running at {url} — opening it.")
            if "--no-open" not in sys.argv:
                subprocess.run(["open", url], check=False)
            return
        raise
    SERVER[0] = server
    print(f"H3 Studio serving at {url}  (Ctrl-C to stop)")
    if "--no-open" not in sys.argv:
        subprocess.run(["open", url], check=False)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        RUNNER.shutdown()


if __name__ == "__main__":
    main()
