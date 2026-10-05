"""Runpod + ComfyUI — a third, optional render engine for H3 Studio.

Unlike h3/vpipe (a local subprocess per job), this engine renders on a rented
RTX 4090 pod running ComfyUI with the native MiniMax H3 nodes. Two pieces:

  RunpodManager  owns the pod's lifecycle (create -> set up -> ready -> delete),
                 its status line and its setup log, and publishes "gpu" events
                 on the same SSE bus the rest of the UI listens to.
  run_job()      renders one H3 Studio job on the pod: uploads conditioning
                 images, submits an API-format ComfyUI graph, follows progress
                 over ComfyUI's websocket, downloads the MP4 to job["outfile"].

Stdlib only, like server.py. Pod control shells out to runpodctl (key in
~/.runpod/config.toml) and ssh (runpodctl's own key). Full background and the
manual equivalent of every step: ~/runpod-h3/RUNBOOK.md.
"""
import base64
import collections
import json
import os
import re
import shutil
import select
import socket
import ssl
import struct
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

RUNPODCTL = os.environ.get("RUNPODCTL") or shutil.which("runpodctl") or os.path.expanduser("~/.local/bin/runpodctl")
RUNPOD_CONFIG = os.path.expanduser("~/.runpod/config.toml")
SSH_KEY = os.path.expanduser("~/.runpod/ssh/runpodctl-ssh-key")
HF_TOKEN_FILE = os.path.expanduser("~/.cache/huggingface/token")

# Each machine names its pod after itself, so two installs sharing one Runpod
# account never adopt or terminate each other's GPU. Override with H3_POD_NAME.
POD_NAME = os.environ.get("H3_POD_NAME") or (
    "h3-studio-" + re.sub(r"[^a-z0-9-]+", "-", socket.gethostname().split(".")[0].lower()).strip("-"))
# Pods this machine may adopt on startup: its own, plus the names used before
# per-machine naming (only safe if one install per Runpod account used them).
ADOPTABLE_NAMES = (POD_NAME, "h3-studio", "h3-render")
TEMPLATE_ID = "cw3nka7d08"  # official "ComfyUI - CUDA 12.8"
GPU_ID = "NVIDIA GeForce RTX 4090"
CLOUD_TYPE = "SECURE"
DISK_GB = 300
DISK_COST_PER_HR = DISK_GB * 0.10 / 730  # container disk, ~$0.10/GB/month while running

# The template ships ComfyUI v0.30.0, which predates the MiniMax H3 audio fixes
# (PR #15243 audio schedule, #15377 audio VAE offload, #15390). Anything older
# than MIN_COMFY renders garbled, noise-only voices. Setup pins COMFY_VERSION.
COMFY_VERSION = "v0.38.2"
MIN_COMFY = (0, 31, 0)
COMFY_DIR = "/workspace/runpod-slim/ComfyUI"
COMFY_LOG = "/workspace/comfyui.log"

# Comfy-Org/MiniMax-H3 repackage, ~70GB of a 525GB repo. fp8 (not the
# recommended int8_convrot) because int8_convrot needs CUDA 13 and the 4090
# hosts run CUDA 12.8 drivers.
HF_REPO = "Comfy-Org/MiniMax-H3"
UNET_TEXT = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
UNET_REF = "minimax_h3_ref2va_pruned_fp8_scaled.safetensors"
TEXT_ENCODER = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
LORA_TEXT = "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors"
LORA_REF = "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
MODEL_FILES = [
    f"diffusion_models/{UNET_REF}",
    f"diffusion_models/{UNET_TEXT}",
    f"text_encoders/{TEXT_ENCODER}",
    f"vae/{VIDEO_VAE}",
    f"vae/{AUDIO_VAE}",
    f"loras/{LORA_REF}",
    "loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors",
    f"loras/{LORA_TEXT}",
]
MODEL_BYTES = 74_000_000_000  # approximate, for the download progress bar only

# Defaults for this engine's jobs. Turbo at 6 steps sounded the same as 20
# steps without Turbo in a same-seed A/B (2026-10-03) at less than half the
# time. reuse/layers/ssd_streaming are h3-only and ignored here; they're kept
# so the shared params shape (history, benchmarks.md) stays the same.
RUNPOD_PARAMS = {"width": 576, "height": 1024, "steps": 6, "reuse": 2, "layers": 50,
                 "ssd_streaming": False, "turbo": True}

# Some hosts have terrible bandwidth (2026-10-05: 0.38 MB/s from Hugging Face,
# i.e. ~50 h for the models). Measure right after boot and replace the pod if slow.
MIN_DL_MBPS = 30
SPEED_TEST_URL = "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors"
MAX_HOST_ATTEMPTS = 3
VIDEO_CRF = 18  # H.264 quality for saved clips (lower = better/larger)
USER_AGENT = "h3-studio/1.0"  # Runpod's Cloudflare proxy 403s (error 1010) Python's default UA

# Setup states, in order. READY/BUSY are the only ones that accept jobs.
BALANCE_WARN_HOURS = 2.0
LOW_BALANCE_STOP = 0.30  # $: below this, Auto stops and the pod is terminated cleanly  # panel turns the balance red below this many hours of runtime left

STATES = ("off", "creating", "booting", "updating", "downloading", "starting",
          "ready", "busy", "stopping", "error")
SETUP_STATES = ("creating", "booting", "updating", "downloading", "starting")


def runpod_available():
    """runpodctl present with an API key configured (RUNPOD_API_KEY in the
    environment/.env, or runpodctl's own config). Checked live, so adding a
    key while the server runs enables the engine without a restart."""
    if not os.access(RUNPODCTL, os.X_OK):
        return False
    if os.environ.get("RUNPOD_API_KEY"):
        return True
    try:
        with open(RUNPOD_CONFIG) as fh:
            m = re.search(r"apikey\s*=\s*['\"]([^'\"]*)['\"]", fh.read(), re.I)
        return bool(m and m.group(1).strip())
    except OSError:
        return False


def _version_tuple(v):
    nums = [int(x) for x in re.findall(r"\d+", v or "")[:3]]
    return tuple(nums + [0] * (3 - len(nums)))


def _http(url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _http_json(url, data=None, timeout=60):
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    return json.loads(_http(url, body, headers, timeout))


def _runpodctl(*args, timeout=60):
    r = subprocess.run([RUNPODCTL, *args, "-o", "json"], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[-400:] or f"runpodctl exited {r.returncode}")
    return json.loads(r.stdout) if r.stdout.strip() else None


# The remote half of setup, run over ssh as `bash -s`. Idempotent: a pod that
# already has the right ComfyUI and models skips straight through, so the same
# script serves a fresh pod and adopting an existing one. Lines starting with
# STEP / DL / ERROR are parsed by RunpodManager; everything else is just logged.
SETUP_SCRIPT = r"""
set -uo pipefail
export HF_TOKEN=$(tr '\0' '\n' < /proc/1/environ | sed -n 's/^HF_TOKEN=//p')
C=__COMFY_DIR__
VER=__COMFY_VERSION__
RESTART=0
cd "$C" || { echo "ERROR ComfyUI not found at $C"; exit 1; }

echo "STEP updating"
if [ "$(git describe --tags 2>/dev/null)" != "$VER" ]; then
  echo "ComfyUI $(git describe --tags 2>/dev/null) -> $VER"
  # Fetch only the tag we need, forced: the image ships its own v0.30.0 tag that
  # differs from upstream, so a plain `git fetch --tags` refuses ("would clobber
  # existing tag") and exits non-zero.
  timeout 300 git fetch -q --force origin "refs/tags/$VER:refs/tags/$VER" \
    || { echo "ERROR git fetch of $VER failed (network?)"; exit 1; }
  git checkout -q "$VER" || { echo "ERROR git checkout $VER failed"; exit 1; }
  . .venv-cu128/bin/activate
  # Pin the image's torch so requirements.txt can't swap the CUDA build
  grep -E '^(torch|torchvision|torchaudio)==' /opt/comfyui-runtime-constraints.txt > /tmp/torch-pin.txt
  timeout 900 python -m pip install -q --no-cache-dir -r requirements.txt -c /tmp/torch-pin.txt 2>&1 \
    | grep -v -i -E 'running pip as|notice' || true
  deactivate
  RESTART=1
else
  echo "ComfyUI already at $VER"
fi
pgrep -f "python main.py" >/dev/null || RESTART=1

echo "STEP downloading"
cd "$C/models"
base=$(du -sb . | cut -f1)
hf download __HF_REPO__ __MODEL_FILES__ --local-dir . > /workspace/download.log 2>&1 &
HFPID=$!
while kill -0 $HFPID 2>/dev/null; do
  echo "DL $(( $(du -sb . | cut -f1) - base ))"
  sleep 5
done
wait $HFPID || { echo "ERROR model download failed:"; tail -5 /workspace/download.log; exit 1; }
echo "models present: $(du -sh --exclude=.cache . | cut -f1)"

echo "STEP starting"
if [ "$RESTART" = 1 ]; then
  pkill -f "python main.py" || true
  sleep 3
  cd "$C" && . .venv-cu128/bin/activate
  setsid nohup python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header \
    > __COMFY_LOG__ 2>&1 < /dev/null &
  echo "ComfyUI restarted"
fi
echo "STEP done"
"""


class RunpodManager:
    def __init__(self, bus, config_path, sessions_path, history_path):
        self.bus = bus
        self.config_path = config_path
        self.sessions_path = sessions_path  # one JSON line per terminated pod (local cost ledger)
        self.history_path = history_path    # H3 Studio history.jsonl, for per-render cost totals
        self.billing = {}
        self.low_balance = False
        self.session_start = None  # epoch seconds the current pod started billing
        self.lock = threading.Lock()
        self.state = "off"
        self.detail = ""
        self.error = None
        self.pod_id = None
        self.pod = {}  # last `pod get` fields we show: cost, uptime, gpu, image
        self.ssh = None  # (host, port)
        self.comfy_version = None
        self.dl_bytes = 0
        self.logs = collections.deque(maxlen=400)
        self.idle_minutes = 20
        self.last_activity = time.time()
        self.active_jobs = 0
        self._flow = None  # thread running start/setup/stop
        self._load_config()
        threading.Thread(target=self._monitor, daemon=True).start()

    # ---- config / state -------------------------------------------------

    def _load_config(self):
        try:
            with open(self.config_path) as fh:
                self.idle_minutes = max(0, int(json.load(fh).get("idle_minutes", 20)))
        except (OSError, ValueError):
            pass

    def set_idle_minutes(self, minutes):
        with self.lock:
            self.idle_minutes = max(0, int(minutes))
        with open(self.config_path, "w") as fh:
            json.dump({"idle_minutes": self.idle_minutes}, fh)
        self._publish()

    def snapshot(self):
        with self.lock:
            idle_s = None
            if self.state == "ready" and self.active_jobs == 0:
                idle_s = int(time.time() - self.last_activity)
            return {
                "available": runpod_available(), "state": self.state, "detail": self.detail,
                "error": self.error, "pod_id": self.pod_id, "pod": dict(self.pod),
                "comfy_version": self.comfy_version, "idle_minutes": self.idle_minutes,
                "idle_s": idle_s, "dl_bytes": self.dl_bytes, "dl_total": MODEL_BYTES,
                "billing": dict(self.billing), "logs": list(self.logs)[-200:],
            }

    @property
    def rate(self):
        """Current $/hr including disk, or the list price if no pod is up."""
        with self.lock:
            return self.pod.get("cost_per_hr") or (0.74 + DISK_COST_PER_HR)

    def _publish(self):
        snap = self.snapshot()
        snap.pop("logs")
        self.bus.publish({"type": "gpu", **snap})

    def _set(self, state, detail="", error=None):
        with self.lock:
            self.state, self.detail, self.error = state, detail, error
            if state in ("ready", "off"):
                self.last_activity = time.time()
        self._log(f"[{state}] {detail or error or ''}".rstrip())
        self._publish()

    def _log(self, line):
        entry = {"t": int(time.time() * 1000), "line": line}
        with self.lock:
            self.logs.append(entry)
        self.bus.publish({"type": "gpu-log", **entry})

    @property
    def base_url(self):
        return f"https://{self.pod_id}-8188.proxy.runpod.net" if self.pod_id else None

    def is_ready(self):
        with self.lock:
            return self.state in ("ready", "busy")

    def job_started(self):
        with self.lock:
            self.active_jobs += 1
            if self.state == "ready":
                self.state = "busy"
        self._publish()

    def job_finished(self):
        with self.lock:
            self.active_jobs = max(0, self.active_jobs - 1)
            self.last_activity = time.time()
            if self.state == "busy" and self.active_jobs == 0:
                self.state = "ready"
        self._publish()

    # ---- public actions ------------------------------------------------

    def start(self):
        if not runpod_available():
            raise ValueError("runpodctl isn't set up (no API key in ~/.runpod/config.toml)")
        with self.lock:
            if self.state not in ("off", "error") or (self._flow and self._flow.is_alive()):
                raise ValueError(f"GPU is already {self.state}")
            adopt = self.pod_id is not None  # an error state with a live pod: retry setup only
            self.error = None
            # Leave "off" immediately (not when the thread gets going), so AutoLoop's
            # "GPU is off, stop Auto" guard can't race a Start it triggered itself.
            self.state = "booting" if adopt else "creating"
            self._flow = threading.Thread(target=self._start_flow, args=(adopt,), daemon=True)
            self._flow.start()

    def stop(self):
        with self.lock:
            if self.state in ("off", "stopping"):
                raise ValueError(f"GPU is already {self.state}")
            if not self.pod_id:
                self.state = "off"
                return
            self._flow = threading.Thread(target=self._stop_flow, daemon=True)
            self._flow.start()

    def comfy_log(self, lines=200):
        if not self.ssh:
            return "(no pod)"
        r = self._ssh(f"tail -n {int(lines)} {COMFY_LOG} 2>/dev/null || echo '(no ComfyUI log yet)'", timeout=20)
        return r.stdout[-60000:]

    # ---- flows ---------------------------------------------------------

    def _start_flow(self, adopt):
        try:
            for attempt in range(1, MAX_HOST_ATTEMPTS + 1):
                if not adopt:
                    self._create()
                self._wait_boot()
                mbps = self._net_speed()
                if mbps >= MIN_DL_MBPS:
                    self._log(f"network check: {mbps:.0f} MB/s from Hugging Face (ok)")
                    break
                self._log(f"network check: only {mbps:.1f} MB/s from Hugging Face (need {MIN_DL_MBPS}); "
                          f"replacing this pod (attempt {attempt}/{MAX_HOST_ATTEMPTS})")
                self._delete_pod(f"slow host ({mbps:.1f} MB/s)")
                adopt = False
            else:
                raise RuntimeError(f"{MAX_HOST_ATTEMPTS} slow hosts in a row; try again later")
            self._setup()
        except Exception as exc:
            self._set("error", error=str(exc))

    def _net_speed(self):
        """MB/s downloading from Hugging Face for up to 15s, measured on the pod."""
        r = self._ssh(f"curl -sL --max-time 15 -o /dev/null -w '%{{speed_download}}' {SPEED_TEST_URL}", timeout=40)
        try:
            return float(r.stdout.strip() or 0) / 1e6
        except ValueError:
            return 0.0

    def _delete_pod(self, why):
        """Delete the current pod without leaving the setup flow (used to swap a bad host)."""
        pod_id = self.pod_id
        self._record_session(pod_id, f"replaced: {why}")
        _runpodctl("pod", "delete", pod_id, timeout=90)
        with self.lock:
            self.pod_id, self.pod, self.ssh, self.comfy_version = None, {}, None, None
        self._log(f"pod {pod_id} deleted ({why})")

    def _stop_flow(self):
        pod_id = self.pod_id
        self._set("stopping", f"terminating pod {pod_id}")
        try:
            _runpodctl("pod", "delete", pod_id, timeout=90)
            for _ in range(12):
                pods = _runpodctl("pod", "list") or []
                if not any(p.get("id") == pod_id for p in pods):
                    break
                time.sleep(5)
            else:
                raise RuntimeError(f"pod {pod_id} still listed after delete")
        except Exception as exc:
            self._set("error", error=f"stop failed: {exc} — check the Runpod console")
            return
        self._record_session(pod_id, "stopped in H3 Studio")
        with self.lock:
            self.pod_id, self.pod, self.ssh, self.comfy_version = None, {}, None, None
        self._set("off", f"pod {pod_id} terminated, billing stopped")
        self._refresh_billing()

    def _create(self):
        self._set("creating", f"RTX 4090 · {CLOUD_TYPE.title()} · {DISK_GB}GB disk")
        env = {}
        token = os.environ.get("HF_TOKEN")
        if not token:
            try:
                with open(HF_TOKEN_FILE) as fh:
                    token = fh.read().strip()
            except OSError:
                pass
        if token:
            env["HF_TOKEN"] = token
        else:
            self._log("no Hugging Face token found; downloading anonymously")
        pod = _runpodctl(
            "pod", "create", "--name", POD_NAME, "--template-id", TEMPLATE_ID,
            "--gpu-id", GPU_ID, "--gpu-count", "1", "--cloud-type", CLOUD_TYPE,
            "--container-disk-in-gb", str(DISK_GB), "--volume-in-gb", "0",
            "--ports", "8188/http,22/tcp", "--ssh", "--env", json.dumps(env), timeout=120)
        with self.lock:
            self.pod_id = pod["id"]
            self.pod = {"cost_per_hr": pod.get("costPerHr"), "image": pod.get("imageName")}
        self._log(f"pod {pod['id']} created at ${pod.get('costPerHr')}/hr (billing started)")

    def _wait_boot(self):
        self._set("booting", "waiting for SSH and ComfyUI")
        deadline = time.time() + 900
        while time.time() < deadline:
            try:
                info = _runpodctl("ssh", "info", self.pod_id, timeout=30)
                if info and info.get("ip") and info.get("port"):
                    with self.lock:
                        self.ssh = (info["ip"], int(info["port"]))
                    if self._ssh("true", timeout=20).returncode == 0:
                        self._log(f"ssh ready at {info['ip']}:{info['port']}")
                        return
            except Exception:
                pass
            time.sleep(10)
        raise RuntimeError("pod didn't become reachable over SSH within 15 minutes")

    def _setup(self):
        script = (SETUP_SCRIPT.replace("__COMFY_DIR__", COMFY_DIR)
                  .replace("__COMFY_VERSION__", COMFY_VERSION)
                  .replace("__HF_REPO__", HF_REPO)
                  .replace("__MODEL_FILES__", " ".join(MODEL_FILES))
                  .replace("__COMFY_LOG__", COMFY_LOG))
        proc = subprocess.Popen(self._ssh_argv("bash -s"), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        proc.stdin.write(script)
        proc.stdin.close()
        labels = {"updating": f"updating ComfyUI to {COMFY_VERSION}",
                  "downloading": "downloading MiniMax H3 models (~70GB)",
                  "starting": "starting ComfyUI"}
        failed = None
        for line in proc.stdout:
            line = line.rstrip()
            if line.startswith("STEP "):
                step = line[5:]
                if step in labels:
                    self._set(step, labels[step])
            elif line.startswith("DL "):
                with self.lock:
                    self.dl_bytes = int(line[3:] or 0)
                self._publish()
            elif line:
                if line.startswith("ERROR"):
                    failed = line[6:]
                self._log(line)
        if proc.wait() != 0 or failed:
            raise RuntimeError(failed or "setup script failed (see log)")
        self._wait_comfy()

    def _wait_comfy(self):
        deadline = time.time() + 300
        while time.time() < deadline:
            try:
                stats = _http_json(f"{self.base_url}/system_stats", timeout=10)
                version = stats["system"]["comfyui_version"]
                if _version_tuple(version) < MIN_COMFY:
                    raise RuntimeError(f"ComfyUI {version} is older than the H3 audio fix "
                                       f"({'.'.join(map(str, MIN_COMFY))}); voices would be garbled")
                with self.lock:
                    self.comfy_version = version
                self._set("ready", f"ComfyUI {version} · MiniMax H3 models loaded on disk")
                return
            except RuntimeError:
                raise
            except Exception:
                time.sleep(5)
        raise RuntimeError("ComfyUI didn't come up within 5 minutes (see ComfyUI log)")

    # ---- monitor: status line, adoption, idle auto-off -----------------

    def _monitor(self):
        last_discover = 0.0
        last_billing = 0.0
        while True:
            billing_every = 60 if (self.billing.get("hours_left") or 99) < 1 else 300
            if time.time() - last_billing > billing_every and runpod_available():
                last_billing = time.time()
                try:
                    self._refresh_billing()
                except Exception as exc:
                    print(f"runpod billing: {exc}", flush=True)
            try:
                with self.lock:
                    state, pod_id = self.state, self.pod_id
                if pod_id and state != "stopping":
                    self._refresh_pod(pod_id)
                elif not pod_id and state == "off" and time.time() - last_discover > 60 and runpod_available():
                    last_discover = time.time()
                    self._discover()
                self._check_idle()
                self._check_balance()
            except Exception as exc:
                print(f"runpod monitor: {exc}", flush=True)
            time.sleep(15)

    def _refresh_pod(self, pod_id):
        try:
            pod = _runpodctl("pod", "get", pod_id, timeout=30)
        except RuntimeError as exc:
            if "not found" in str(exc).lower() or "404" in str(exc):
                self._record_session(pod_id, "terminated outside H3 Studio")
                with self.lock:
                    self.pod_id, self.pod, self.ssh, self.comfy_version = None, {}, None, None
                self._set("off", f"pod {pod_id} no longer exists (terminated outside H3 Studio)")
            return
        uptime = pod.get("uptimeSeconds") or 0
        rate = (pod.get("costPerHr") or 0) + DISK_COST_PER_HR
        with self.lock:
            self.session_start = time.time() - uptime
            self.pod.update({"cost_per_hr": round(rate, 3), "uptime_s": uptime,
                             "spent": round(uptime / 3600 * rate, 2),
                             "image": pod.get("imageName"), "status": pod.get("desiredStatus")})
        self._publish()

    def _discover(self):
        pods = _runpodctl("pod", "list", timeout=30) or []
        mine = [p for p in pods if p.get("name") in ADOPTABLE_NAMES and p.get("desiredStatus") == "RUNNING"]
        if not mine:
            return
        pod = mine[0]
        with self.lock:
            if self.state != "off" or self.pod_id:
                return
            self.pod_id = pod["id"]
            self._flow = threading.Thread(target=self._start_flow, args=(True,), daemon=True)
        self._log(f"found running pod {pod['id']} ({pod.get('name')}); checking its setup")
        self._flow.start()

    def _check_balance(self):
        """Terminate the pod ourselves before Runpod runs the balance dry and
        stops it mid-render (which leaves a dead pod H3 Studio still thinks is
        ready). Also tells AutoLoop to stand down via `low_balance`."""
        with self.lock:
            b = dict(self.billing)
            state, pod_id = self.state, self.pod_id
        bal = b.get("balance")
        self.low_balance = bal is not None and bal < LOW_BALANCE_STOP
        if self.low_balance and pod_id and state in ("ready", "busy"):
            self._log(f"balance ${bal:.2f} is below ${LOW_BALANCE_STOP:.2f}: terminating the pod before Runpod stops it")
            try:
                self.stop()
            except ValueError:
                pass

    def _check_idle(self):
        with self.lock:
            if (self.state != "ready" or self.active_jobs or not self.idle_minutes
                    or time.time() - self.last_activity < self.idle_minutes * 60):
                return
            minutes = self.idle_minutes
        self._log(f"idle for {minutes} min with no jobs; auto-stopping")
        try:
            self.stop()
        except ValueError:
            pass

    # ---- cost: local session ledger + Runpod billing ------------------

    def _record_session(self, pod_id, how):
        with self.lock:
            pod = dict(self.pod)
            start = self.session_start
        uptime = pod.get("uptime_s") or (time.time() - start if start else 0)
        rec = {"pod_id": pod_id, "start": int((start or time.time() - uptime) * 1000),
               "end": int(time.time() * 1000), "uptime_s": int(uptime),
               "cost_per_hr": pod.get("cost_per_hr"),
               "cost": round(uptime / 3600 * (pod.get("cost_per_hr") or 0), 3), "how": how}
        try:
            with open(self.sessions_path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
        except OSError as exc:
            print(f"runpod sessions ledger: {exc}", flush=True)

    def _sessions(self):
        try:
            with open(self.sessions_path) as fh:
                return [json.loads(l) for l in fh if l.strip()]
        except (OSError, ValueError):
            return []

    def _render_spend(self):
        clips, total = 0, 0.0
        try:
            with open(self.history_path) as fh:
                for line in fh:
                    if '"runpod"' not in line:
                        continue
                    e = json.loads(line)
                    if e.get("engine") == "runpod" and e.get("mode") != "sequence" and e.get("cost_usd"):
                        clips += 1
                        total += e["cost_usd"]
        except (OSError, ValueError):
            pass
        return clips, round(total, 2)

    def _refresh_billing(self):
        """Runpod's own billing (authoritative, but it lags real usage) plus
        the account balance. Pod billing only: this app uses no serverless
        endpoints or network volumes."""
        start = time.strftime("%Y-%m-%dT00:00:00Z", time.gmtime(time.time() - 90 * 86400))
        rows = _runpodctl("billing", "pods", "--bucket-size", "day", "--start-time", start, timeout=60) or []
        days = collections.defaultdict(float)
        for r in rows:
            days[r["time"][:10]] += r.get("amount") or 0
        today = time.strftime("%Y-%m-%d", time.gmtime())

        def since(n):
            cutoff = time.strftime("%Y-%m-%d", time.gmtime(time.time() - n * 86400))
            return round(sum(v for d, v in days.items() if d > cutoff), 2)
        user = _runpodctl("user", timeout=30) or {}
        balance = user.get("clientBalance")
        spend_hr = user.get("currentSpendPerHr") or 0
        clips, render_total = self._render_spend()
        sessions = self._sessions()
        with self.lock:
            self.billing = {
                "updated": int(time.time() * 1000),
                "today": round(days.get(today, 0), 2), "week": since(7), "month": since(30),
                "total90": since(90),
                "days": [{"day": d, "amount": round(v, 3)} for d, v in sorted(days.items(), reverse=True)[:30]],
                "balance": round(balance, 2) if balance is not None else None,
                "spend_per_hr": spend_hr,
                "hours_left": round(balance / spend_hr, 1) if balance and spend_hr else None,
                "warn_hours": BALANCE_WARN_HOURS,
                "render_clips": clips, "render_total": render_total,
                "sessions": sessions[-20:][::-1],
                "sessions_total": round(sum(x.get("cost") or 0 for x in sessions), 2),
            }
        self._publish()

    # ---- ssh -----------------------------------------------------------

    def _ssh_argv(self, command):
        host, port = self.ssh
        return ["ssh", "-i", SSH_KEY, "-p", str(port), "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=15", "-o", "BatchMode=yes", "-o", "LogLevel=ERROR",
                # A dropped connection once left setup waiting forever; keepalives
                # turn that into an ssh error within ~2 minutes.
                "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=4",
                f"root@{host}", command]

    def _ssh(self, command, timeout=60):
        return subprocess.run(self._ssh_argv(command), capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------------------
# Rendering one job
# ---------------------------------------------------------------------------

def frames_snap(frames):
    """H3 wants 17n+5 frames; validate_job already snaps, this is a guard."""
    return frames + (5 - frames % 17) % 17


def build_graph(job, uploaded):
    """API-format ComfyUI graph for one job. Mirrors Comfy-Org's
    video_minimax_h3_{t2v,i2v,r2v} templates, swapped to the fp8/fp16 files
    we download. `uploaded` maps H3_ROOT-relative input paths to the names
    ComfyUI's /upload/image returned."""
    p = job["params"]
    refs = job.get("refs") or []
    ref_mode = bool(refs)
    turbo = p.get("turbo", True)
    g = {
        "unet": {"class_type": "UNETLoader", "inputs": {
            "unet_name": UNET_REF if ref_mode else UNET_TEXT, "weight_dtype": "default"}},
        "clip": {"class_type": "CLIPLoader", "inputs": {
            "clip_name": TEXT_ENCODER, "type": "minimax", "device": "default"}},
        "vae": {"class_type": "VAELoader", "inputs": {"vae_name": VIDEO_VAE}},
        "avae": {"class_type": "VAELoader", "inputs": {"vae_name": AUDIO_VAE}},
        "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": int(p["seed"]) % 2**64}},
        "samp": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "sched": {"class_type": "BasicScheduler", "inputs": {
            "model": ["unet", 0], "scheduler": "simple", "steps": int(p["steps"]), "denoise": 1}},
        "guide": {"class_type": "BasicGuider", "inputs": {
            "model": ["lora", 0] if turbo else ["unet", 0], "conditioning": ["cond", 0]}},
        "run": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["noise", 0], "guider": ["guide", 0], "sampler": ["samp", 0],
            "sigmas": ["sched", 0], "latent_image": ["cond", 1]}},
        "dec": {"class_type": "VAEDecode", "inputs": {"samples": ["run", 0], "vae": ["vae", 0]}},
        "adec": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["run", 0], "vae": ["avae", 0]}},
        "video": {"class_type": "CreateVideo", "inputs": {
            "images": ["dec", 0], "audio": ["adec", 0], "fps": 24, "bit_depth": 8}},
        # Re-encode explicitly: SaveVideo's "auto" keeps a ~0.75 Mbps stream that
        # looked blocky in cuts and dark shots (vpipe writes ~2 Mbps). CRF 18 is
        # near-lossless; a CRF 16 test came out at 6.3 Mbps.
        "save": {"class_type": "SaveVideo", "inputs": {
            "video": ["video", 0], "filename_prefix": "video/h3studio", "format": "mp4",
            "format.codec": "h264", "format.codec.encoding": "re-encode", "format.codec.encoding.crf": VIDEO_CRF}},
    }
    if turbo:
        g["lora"] = {"class_type": "LoraLoaderModelOnly", "inputs": {
            "model": ["unet", 0], "lora_name": LORA_REF if ref_mode else LORA_TEXT, "strength_model": 1}}
    common = {"clip": ["clip", 0], "vae": ["vae", 0], "prompt": job["prompt"],
              "width": int(p["width"]), "height": int(p["height"]), "length": frames_snap(int(p["frames"]))}
    if ref_mode:
        cond = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": dict(
            common, audio_vae=["avae", 0], ref_image_size="match")}
        for i, rel in enumerate(refs):
            g[f"ref{i}"] = {"class_type": "LoadImage", "inputs": {"image": uploaded[rel]}}
            cond["inputs"][f"ref_images.ref_image_{i}"] = [f"ref{i}", 0]
    else:
        # Text and first/last share the FL2VA model; the frames are optional inputs.
        cond = {"class_type": "MiniMaxH3ImageToVideo", "inputs": dict(common)}
        for key in ("first_frame", "last_frame"):
            if job.get(key):
                g[key] = {"class_type": "LoadImage", "inputs": {"image": uploaded[job[key]]}}
                cond["inputs"][key] = [key, 0]
    g["cond"] = cond
    return g


PHASES = {"unet": "loading model", "clip": "loading text encoder", "cond": "encoding prompt",
          "lora": "loading Turbo LoRA", "run": "denoise", "dec": "decoding video",
          "adec": "decoding audio", "video": "muxing", "save": "saving"}


def _upload(base, root, rel):
    path = os.path.join(root, rel)
    boundary = uuid.uuid4().hex
    name = os.path.basename(rel)
    with open(path, "rb") as fh:
        data = fh.read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + (
            f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue"
            f"\r\n--{boundary}--\r\n").encode()
    r = json.loads(_http(f"{base}/upload/image", body,
                         {"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return r["name"]


def run_job(job, root, gpu, publish, cancel_event):
    """Render one job on the pod. Returns (ok, error, elapsed_s) like
    JobRunner._run. Waits for the GPU if it's still setting up; fails fast if
    it's off so a queued Runpod job can't silently block h3/vpipe jobs."""
    started = time.time()

    def progress(phase, done=0, total=0):
        publish({"type": "progress", "job": job["id"], "phase": phase, "done": done,
                 "total": total, "elapsed": round(time.time() - started, 1)})

    while not gpu.is_ready():
        if cancel_event.is_set():
            return False, "canceled", time.time() - started
        state = gpu.snapshot()["state"]
        if state in ("off", "error", "stopping"):
            return False, f"GPU is {state} — start it from the GPU panel, then retry", time.time() - started
        progress(f"waiting for GPU ({state})")
        time.sleep(3)

    gpu.job_started()
    try:
        return _render(job, root, gpu.base_url, progress, cancel_event, started)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:600]
        return False, f"ComfyUI rejected the job ({exc.code}): {detail}", time.time() - started
    except Exception as exc:
        return False, f"runpod: {exc}", time.time() - started
    finally:
        gpu.job_finished()


def _render(job, root, base, progress, cancel_event, started):
    progress("uploading images")
    uploaded = {}
    for rel in list(job.get("refs") or []) + [job.get("first_frame"), job.get("last_frame")]:
        if rel and rel not in uploaded:
            uploaded[rel] = _upload(base, root, rel)
    graph = build_graph(job, uploaded)

    client_id = uuid.uuid4().hex
    ws = None
    try:
        ws = _WebSocket(base.replace("https://", "wss://") + f"/ws?clientId={client_id}")
    except Exception as exc:
        print(f"runpod: websocket unavailable ({exc}); polling for progress instead", flush=True)
    prompt_id = _http_json(f"{base}/prompt", {"prompt": graph, "client_id": client_id})["prompt_id"]
    progress("queued on GPU")

    error = None
    last_poll = time.time()
    try:
        while True:
            if cancel_event.is_set():
                _cancel(base, prompt_id)
                return False, "canceled", time.time() - started
            msg = None
            if ws:
                try:
                    msg = ws.recv(timeout=10)
                except (ConnectionError, OSError, ValueError) as exc:
                    print(f"runpod: websocket dropped ({exc}); polling instead", flush=True)
                    ws.close()
                    ws = None
            if msg:
                kind, data = msg.get("type"), msg.get("data") or {}
                if data.get("prompt_id") not in (None, prompt_id):
                    continue
                if kind == "progress" and data.get("node") == "run":
                    progress("denoise", int(data.get("value", 0)), int(data.get("max", 0)))
                elif kind == "executing" and data.get("node") in PHASES:
                    progress(PHASES[data["node"]])
                elif kind == "execution_error":
                    error = f"{data.get('exception_type', 'error')}: {data.get('exception_message', '').strip()}"
                    break
                elif kind == "execution_interrupted":
                    return False, "canceled", time.time() - started
                elif kind == "execution_success" or (kind == "executing" and data.get("node") is None
                                                       and data.get("prompt_id") == prompt_id):
                    break
            if not ws or time.time() - last_poll > 30:
                # Also the safety net if the websocket drops mid-job.
                last_poll = time.time()
                hist = _http_json(f"{base}/history/{prompt_id}", timeout=30)
                if prompt_id in hist and hist[prompt_id].get("status", {}).get("completed"):
                    break
                if prompt_id in hist and hist[prompt_id].get("status", {}).get("status_str") == "error":
                    error = "render failed (see ComfyUI log)"
                    break
                if not ws:
                    time.sleep(5)
    finally:
        if ws:
            ws.close()
    if error:
        return False, error, time.time() - started

    progress("downloading video")
    hist = _http_json(f"{base}/history/{prompt_id}", timeout=30).get(prompt_id, {})
    for out in (hist.get("outputs") or {}).values():
        for item in out.get("images", []) + out.get("videos", []) + out.get("gifs", []):
            if not item.get("filename", "").endswith(".mp4"):
                continue
            q = urllib.parse.urlencode({"filename": item["filename"], "subfolder": item.get("subfolder", ""),
                                        "type": item.get("type", "output")})
            dest = os.path.join(root, job["outfile"])
            data = _http(f"{base}/view?{q}", timeout=300)
            with open(dest + ".part", "wb") as fh:
                fh.write(data)
            os.replace(dest + ".part", dest)
            return True, None, time.time() - started
    return False, "render finished but produced no MP4", time.time() - started


def _cancel(base, prompt_id):
    for url, body in ((f"{base}/queue", {"delete": [prompt_id]}), (f"{base}/interrupt", {"prompt_id": prompt_id})):
        try:
            _http_json(url, body, timeout=15)
        except Exception:
            pass


class _WebSocket:
    """Just enough of RFC 6455 to read ComfyUI's JSON status messages (stdlib
    has no websocket client). Text frames only; binary preview frames are
    skipped; pings are answered."""

    def __init__(self, url, timeout=20):
        u = urllib.parse.urlparse(url)
        port = u.port or (443 if u.scheme == "wss" else 80)
        sock = socket.create_connection((u.hostname, port), timeout=timeout)
        if u.scheme == "wss":
            sock = ssl.create_default_context().wrap_socket(sock, server_hostname=u.hostname)
        key = base64.b64encode(os.urandom(16)).decode()
        path = u.path + ("?" + u.query if u.query else "")
        sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {u.hostname}\r\nUpgrade: websocket\r\n"
                      f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
                      f"User-Agent: {USER_AGENT}\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("websocket handshake: connection closed")
            head += chunk
        status = head.split(b"\r\n", 1)[0]
        if b" 101 " not in status:
            raise ConnectionError(f"websocket handshake failed: {status.decode('latin-1')}")
        self.sock = sock
        self.buf = head.split(b"\r\n\r\n", 1)[1]

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("websocket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _send(self, opcode, payload=b""):
        mask = os.urandom(4)
        header = bytes([0x80 | opcode])
        n = len(payload)
        if n < 126:
            header += bytes([0x80 | n])
        elif n < 65536:
            header += bytes([0x80 | 126]) + struct.pack("!H", n)
        else:
            header += bytes([0x80 | 127]) + struct.pack("!Q", n)
        self.sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def recv(self, timeout=10):
        """Next JSON text message, or None on timeout. Only waits *between*
        frames: once a frame starts arriving it's read to the end, so a timeout
        can never leave the stream half-parsed."""
        if not self.buf and not (hasattr(self.sock, "pending") and self.sock.pending()):
            if not select.select([self.sock], [], [], timeout)[0]:
                return None
        self.sock.settimeout(120)
        message, msg_op = b"", None
        while True:
            b0, b1 = self._read(2)
            fin, opcode = b0 & 0x80, b0 & 0x0F
            n = b1 & 0x7F
            if n == 126:
                n = struct.unpack("!H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack("!Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            payload = self._read(n)
            if mask:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if opcode == 0x9:
                self._send(0xA, payload)
                continue
            if opcode == 0x8:
                raise ConnectionError("websocket closed by server")
            if opcode in (0x1, 0x2):
                msg_op, message = opcode, payload
            elif opcode == 0x0:
                message += payload
            else:
                continue
            if fin:
                if msg_op == 0x1:
                    return json.loads(message.decode("utf-8", "replace"))
                message, msg_op = b"", None  # binary preview frame: skip
                if not self.buf and not (hasattr(self.sock, "pending") and self.sock.pending()):
                    if not select.select([self.sock], [], [], timeout)[0]:
                        return None

    def close(self):
        try:
            self._send(0x8)
            self.sock.close()
        except Exception:
            pass
