"""Submit a multi-clip sequence script to the H3 Studio queue.

A sequence script is the same text you would paste into the GUI's Sequence tab:
clip blocks separated by a line of "=====", each starting with "<duration> | ".
Clip 1 renders from text; every later clip is conditioned on the previous
clip's last frame, which is what gives a multi-shot scene its continuity.

    python3 tools/submit_sequence.py series/trisha-enzo/script.txt
    python3 tools/submit_sequence.py script.txt --seed 530102 --steps 8
    python3 tools/submit_sequence.py script.txt --engine h3 --steps 20
    python3 tools/submit_sequence.py script.txt --dry-run

parse_sequence() mirrors gui/index.html's parseSequence exactly, so submitting
a file here is byte-for-byte identical to pasting it into the GUI.

Notes earned the hard way:
  - reuse/layers/ssd_streaming are h3-only knobs that vpipe's pipeline never
    reads, but the server still range-checks them, so they must be sent on
    every engine. Omitting them fails with "reuse must be an integer".
  - vpipe has no Ref2VA model prepared, so it cannot take reference images;
    the server rejects episode refs on that engine outright.
  - The server snaps any frame count that breaks (frames - 5) %% 17 == 0, so
    this warns before submitting rather than letting a clip silently change
    length.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

API_BASE = "http://127.0.0.1:7833"
VALID_FRAMES = [22 + 17 * i for i in range(20)]


def parse_sequence(text, default_frames):
    """Mirror of gui/index.html parseSequence()."""
    out = []
    for block in re.split(r"\n\s*[-=]{3,}\s*\n", text):
        block = block.strip()
        if not block:
            continue
        m = re.match(r"^(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|f|frames)?\s*\|\s*([\s\S]*)$",
                     block, re.I)
        if not m:
            out.append({"prompt": block, "frames": default_frames})
            continue
        val, unit, prompt = float(m.group(1)), (m.group(2) or ""), m.group(3).strip()
        frames = round(val) if unit.lower().startswith("f") else round(val * 24)
        if prompt:
            out.append({"prompt": prompt, "frames": frames})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", help="path to the sequence script (===== separated)")
    ap.add_argument("--engine", default="vpipe", choices=["vpipe", "h3"])
    ap.add_argument("--steps", type=int, default=8, help="8 for vpipe Turbo, 20 for h3 quality")
    ap.add_argument("--seed", type=int, default=None, help="default: random")
    ap.add_argument("--width", type=int, default=576)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--frames", type=int, default=192,
                    help="fallback only; each clip's own 'N |' prefix overrides it")
    ap.add_argument("--refs", nargs="*", default=[],
                    help="episode reference images (h3 only; vpipe has no Ref2VA)")
    ap.add_argument("--dry-run", action="store_true", help="parse and report, do not submit")
    a = ap.parse_args()

    if a.refs and a.engine == "vpipe":
        sys.exit("error: vpipe cannot take reference images (no Ref2VA model prepared)")

    items = parse_sequence(open(a.script).read(), a.frames)
    if len(items) < 2:
        sys.exit("error: a sequence needs at least 2 clips separated by a line of =====")

    seed = a.seed if a.seed is not None else __import__("random").randint(0, 2**31 - 1)
    total = 0
    for i, it in enumerate(items, 1):
        f = it["frames"]
        total += f
        shot = re.search(r"\[Shot \d+\]", it["prompt"])
        lines = re.findall(r"<d>\[[^\]]+\](.*?)</d>", it["prompt"], re.S)
        warn = "" if (f - 5) % 17 == 0 else f"  !! invalid, server will snap it (use {VALID_FRAMES})"
        print(f"clip {i}: {f}f ({f / 24:.2f}s)  {shot.group(0) if shot else '?'}  "
              f"{len(lines)} line(s){warn}")
    print(f"total: {total}f ({total / 24:.2f}s) · {a.engine} · {a.steps} steps · seed {seed}")

    if a.dry_run:
        return

    body = {
        "items": items,
        "params": {"width": a.width, "height": a.height, "frames": a.frames,
                   "steps": a.steps, "seed": seed,
                   # h3-only, inert on vpipe, but range-checked on every engine
                   "reuse": 2, "layers": 50, "ssd_streaming": True},
        "refs": a.refs,
        "engine": a.engine,
    }
    req = urllib.request.Request(API_BASE + "/api/sequence", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(resp.status, resp.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode()}")


if __name__ == "__main__":
    main()
