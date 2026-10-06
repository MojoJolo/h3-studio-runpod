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
import random
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import pty
import queue as queue_mod
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from PIL import Image, ImageDraw, ImageFont

import runpod_engine

GUI_DIR = os.path.dirname(os.path.abspath(__file__))
H3_ROOT = os.path.dirname(GUI_DIR)


def _load_dotenv(path):
    """KEY=VALUE lines from the repo's .env into os.environ (never overrides
    variables already set). Per-machine settings like RUNPOD_API_KEY and
    HF_TOKEN live there, never in git."""
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip("'\""))
    except OSError:
        pass


_load_dotenv(os.path.join(H3_ROOT, ".env"))
IS_MAC = sys.platform == "darwin"
H3_BIN = os.path.join(H3_ROOT, "h3")
# The local h3.c engine is optional: without it (any non-Mac machine, or a Mac
# without the weights) H3 Studio runs with the Runpod engine only.
H3_AVAILABLE = os.access(H3_BIN, os.X_OK) and os.path.isdir(os.path.join(H3_ROOT, "MiniMax-H3"))
MODEL_DIR = "MiniMax-H3"
OUTPUTS = os.path.join(H3_ROOT, "outputs")
# Merged episodes (and their captioned variants) go in their own folder so
# they can be copied out in one go; individual clips stay in outputs/.
FINALS = os.path.join(OUTPUTS, "final")
INPUTS = os.path.join(H3_ROOT, "inputs")
HISTORY = os.path.join(GUI_DIR, "history.jsonl")
PORT = int(os.environ.get("H3_STUDIO_PORT", "7833"))
# The page renders one <video preload="metadata"> element per history entry;
# with the Auto loop generating continuously, an unbounded/200-entry list
# grew the DOM enough to crash the tab. Cap what the initial page load shows.
STATE_HISTORY_LIMIT = 50

# vpipe / MiniMax H3 Turbo — a second, optional engine. VPIPE_AVAILABLE gates
# the engine picker in the UI; if false the app behaves exactly as it did
# with h3 alone, so the repo stays portable for anyone without vpipe set up.
VPIPE_BIN = "/Applications/Vpipe Manager.app/Contents/Helpers/vpipe"
VPIPE_WORK = os.path.expanduser("~/vpipe-work")
VPIPE_MODEL = "local/MiniMax-H3-FL2VA-8bit"
VPIPE_LORA = "larryvrh/MiniMax-H3-Turbo-Lora-v4-600-ema"
VPIPE_AVAILABLE = os.access(VPIPE_BIN, os.X_OK) and os.path.isdir(
    os.path.join(VPIPE_WORK, "models", VPIPE_MODEL))

# Krea 2 Turbo — text-to-image, a separate model/pipeline from the video
# engine above. Checked live (not frozen at startup like VPIPE_AVAILABLE)
# since the model is fetched separately and may finish downloading after
# this server process has already started.
VPIPE_KREA2_MODEL = "krea/Krea-2-Turbo"
KREA2_PARAMS = {"width": 1024, "height": 1024, "steps": 8, "shift": 0.3, "i8_gemm": True}


# A byte-count threshold on the model directory was tried first and proved
# unreliable in both directions (false-positived mid-download at 30 GB while
# a large file was still transferring; the real finished total, 33.2 GB,
# turned out to sit below a since-raised 35 GB guess). vpipe's own
# model-fetch stage only writes a registry record for a model AFTER its
# files pass checksum verification (confirmed against the actual fetch log:
# "...matched the checksum" then "registered ... in the model registry"), so
# checking that registry directly is the real signal instead of guessing
# from directory size.
VPIPE_REGISTRY_DB = os.path.join(VPIPE_WORK, "data.mdb")


def _registered_in_vpipe(model_path):
    if not os.access(VPIPE_BIN, os.X_OK):
        return False
    try:
        with open(VPIPE_REGISTRY_DB, "rb") as fh:
            data = fh.read()
    except OSError:
        return False
    return model_path.encode() in data


def krea2_available():
    return _registered_in_vpipe(VPIPE_KREA2_MODEL)


# FLUX.2 klein-9B (plain, not -kv) — identity-preserving multi-reference
# (up to 2 images) image generation, a separate model/pipeline from Krea 2.
# Krea 2 handles text-only stills; this handles "keep this face/character,
# recompose with that" requests. Deliberately the baseline checkpoint, not
# klein-9b-kv: per vpipe's own KLEIN.md, klein-9B is the quality reference
# point and -kv is an opt-in speed tradeoff that can "sometimes" look worse.
VPIPE_KLEIN_MODEL = "black-forest-labs/FLUX.2-klein-9B"
KLEIN_PARAMS = {"width": 768, "height": 512, "steps": 4, "i8_gemm": True}
KLEIN_MAX_REFS = 2


def klein_available():
    return _registered_in_vpipe(VPIPE_KLEIN_MODEL)

# Auto tab — an unattended loop that writes its own scripts via the `claude`
# CLI and submits them through the same Sequence pipeline a person would use
# by hand. See AutoLoop below.
CLAUDE_BIN = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")
CLAUDE_MODEL = "opus"
AUTO_CONFIG_PATH = os.path.join(GUI_DIR, "auto_config.json")
AUTO_PARAMS = {
    # vpipe's generate-video stage (build_vpipe_spec) only ever reads
    # width/height/frames/fps/steps/seed — "reuse" and "layers" below are
    # h3-only CLI flags (see JobRunner._argv) that vpipe's pipeline never
    # looks at, so they're inert for vpipe and only take effect on h3.
    # 8 steps is the Turbo LoRA's own recommended step count for better
    # quality than the earlier 6-step draft setting.
    "width": 576, "height": 1024, "steps": 8, "reuse": 2, "layers": 40,
    "ssd_streaming": True,
}
# Plain h3 has no Turbo LoRA, so it needs real values for steps/layers (which
# vpipe ignores) — every h3 render in this project's own history
# (gui/history.jsonl) used steps=20, layers=50, reuse=2 (the Studio UI's own
# "quality"/"exact"/"fast" defaults), so match that precedent for h3 Auto runs.
H3_AUTO_PARAMS = dict(AUTO_PARAMS, steps=20, layers=50)
AUTO_CLIP_FRAMES = 192  # 8s @ 24fps — fallback duration for a script block that
                         # omits its own "N |" prefix
AUTO_CLAUDE_TIMEOUT_S = 300
AUTO_CLAUDE_STOP_PCT = 90  # plan usage (5-hour or weekly) at which Auto stops and the GPU shuts down
AUTO_USED_TOPICS_PATH = os.path.join(GUI_DIR, "auto_used_topics.json")  # survives restarts
AUTO_AVOID_HOOKS = 150  # how many past opening lines Claude is told not to repeat
DIALOGUE_RE = re.compile(r"<d>\s*(?:\[[^\]]*\]\s*)?(.*?)</d>", re.S)

# Classic Snapchat-style caption bar, burned onto the merged video in post
# (not baked in by H3 itself — text rendered by a video model is unreliable
# and inconsistent between clips; a post-process overlay is deterministic).
CAPTION_FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
CAPTION_BAR_RGBA = (45, 45, 45, 190)
CAPTION_TEXT_COLOR = (255, 255, 255, 255)


def _find_ffmpeg():
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if os.access(candidate, os.X_OK):
            return candidate
    return "ffmpeg"


FFMPEG = _find_ffmpeg()
ENGINES = ("h3", "vpipe", "runpod")
SEQ_MAX_CLIPS = 20
SEQ_REF_CAP = 8  # leaves one of h3's 9 --ref-image slots for chained continuity


def _duration_label(frames):
    return f"{round(frames / 24, 2):g}"


def _clip_mode_label(first_frame, refs):
    """Display-only label for a sequence/episode clip's conditioning —
    _advance_sequence never sets both at once (see there for why), and argv
    building in JobRunner._argv is field-based, not gated on this label."""
    if refs:
        return "refs"
    if first_frame:
        return "firstlast"
    return "text"


SEQ_BLOCK_RE = re.compile(r"\n\s*[-=]{3,}\s*\n")
SEQ_ITEM_RE = re.compile(
    r"^(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|f|frames)?\s*\|\s*([\s\S]*)$", re.IGNORECASE)
# A block from an LLM (unlike a human pasting into the Sequence tab) often
# arrives wrapped in a fenced code block with a "## Clip N" header before it
# and/or trailing sign-off text after — confirmed by direct testing against
# the actual video-prompt-writing skill. If a fence is present, the real
# "N | prompt" content is what's inside it; anything before/after is noise
# to discard rather than let leak into the prompt or get parsed as a
# nonsense extra clip.
SEQ_FENCE_RE = re.compile(r"```\w*\s*\n([\s\S]*?)\n```")
SEQ_LEADING_MD_RE = re.compile(r"^(?:#{1,6}\s[^\n]*\n+|\*{1,3}[^\n*]*\*{1,3}[^\n]*\n+)")


def _clean_sequence_block(block):
    block = block.strip()
    m = SEQ_FENCE_RE.search(block)
    if m:
        return m.group(1).strip()
    while True:
        m = SEQ_LEADING_MD_RE.match(block)
        if not m:
            break
        block = block[m.end():].lstrip()
    return block


def parse_sequence_text(text, default_frames):
    """Python port of the frontend's parseSequence() (index.html) — same
    block-splitting/regex contract, so a script that would work pasted into
    the Sequence tab by hand also works when AutoLoop parses it. Also
    tolerates markdown wrapping an LLM might add despite being asked for raw
    text (code fences, "## Clip N" headers, a title/character preamble
    before the first clip, a sign-off line after the last) — a block that
    still doesn't match after best-effort cleanup is dropped rather than
    smuggled in as a bogus clip, so a garbled response degrades to "too few
    items" (caught by the caller) instead of submitting nonsense. Frame-count
    range/snapping validation happens later, in validate_sequence."""
    items = []
    for raw_block in SEQ_BLOCK_RE.split(text):
        block = _clean_sequence_block(raw_block)
        if not block:
            continue
        m = SEQ_ITEM_RE.match(block)
        if not m:
            continue
        val = float(m.group(1))
        unit = (m.group(2) or "")
        frames = round(val) if unit.lower().startswith("f") else round(val * 24)
        prompt = m.group(3).strip()
        if prompt:
            items.append({"prompt": prompt, "frames": frames})
    return items

VALID_REUSE = {1, 2, 3}
VALID_LAYERS = {50, 45, 40}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}

PROGRESS_RE = re.compile(rb"([A-Za-z][A-Za-z0-9 _-]*?)\s+(\d+)/(\d+)\s*$")
# vpipe's own logger emits two line shapes for the same progress, and a
# short job (few denoise steps) may only ever produce the second one:
#   "[PROGRESS] 40% of 'denoise' completed at 11:51:33 (100/250)"
#   "[PROGRESS] 'denoise' ended at 11:54:12, last reported 99% (248/250)"
# Lazy .*? around the quoted phase name matches both regardless of whether
# the percent comes before or after it; groups line up with PROGRESS_RE's
# (phase, done, total) so _run() doesn't need per-engine group-index logic.
VPIPE_PROGRESS_RE = re.compile(rb"\[PROGRESS\]\s+.*?'([^']+)'.*?\((\d+)/(\d+)\)")
ANSI_RE = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")


def now_ms():
    return int(time.time() * 1000)


def safe_name(name):
    base = os.path.basename(name)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("._") or "file"
    return base


def _pick_error(tail, engine):
    """Find the most useful failure line in a job's captured tail output.
    h3 only ever prefixes real errors with "h3:", so the naive last-match
    works. vpipe prefixes its OWN success confirmation the same way it
    prefixes real CLI-level failures ("vpipe: launched pipeline 'x'" vs
    "vpipe: launch failed for 'x'..."), and that success line — printed the
    moment the pipeline is accepted, well before any actual work happens —
    was winning by default on every mid-run failure (e.g. an out-of-memory
    refusal), hiding the real reason. vpipe's real per-stage failures are
    logged as "[ERROR] ..." instead, so check those first."""
    if engine == "vpipe":
        err = next((t for t in reversed(tail) if t.startswith("[ERROR]")), None)
        if err:
            return err
        return next((t for t in reversed(tail)
                     if t.startswith("vpipe:") and not t.startswith("vpipe: launched")), None)
    return next((t for t in reversed(tail) if t.startswith(f"{engine}:")), None)


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


def build_vpipe_spec(job):
    """Build the vpipe pipeline graph (a plain dict, --launch takes inline
    JSON) for one job. Mirrors the verified minimax-h3-text-to-video-turbo
    shape; first/last-frame conditioning adds its own load-image ->
    image-resample -> vae-encode trio per provided image, wired into
    generate-video's fixed 10-slot iports (5=first-frame, 6=last-frame) —
    not the docs' single-photo "zoom" demo, which is a different use case
    from h3 Studio's two-independent-images First/Last tab."""
    p = job["params"]
    stages = [
        {"id": "model-select", "type": "model-select", "iports": [],
         "config": {"hf_dir": VPIPE_MODEL}},
        {"id": "text-prompt", "type": "text-prompt", "iports": [],
         "config": {"text": job["prompt"]}},
        {"id": "diffusion-conditioner", "type": "diffusion-conditioner",
         "iports": [
             {"src": "text-prompt", "oport": 0},
             {"src": "", "oport": 0},
             {"src": "model-select", "oport": 0},
         ],
         "config": {"unload_when_idle": "always"}},
        {"id": "minimax-h3-model-config", "type": "minimax-h3-model-config", "iports": [],
         "config": {
             "video_shift": 12.0, "audio_shift": 3.0,
             "condition_timestep": 1.0, "audio_seconds": 0.0,
             "lora": VPIPE_LORA, "lora_scale": 1.0,
         }},
    ]

    gv_iports = [
        {"src": "diffusion-conditioner", "oport": 0},  # 0: text conditioning
        {"src": "", "oport": 0},                       # 1
        {"src": "model-select", "oport": 0},            # 2
        {"src": "", "oport": 0},                       # 3
        {"src": "", "oport": 0},                       # 4
        {"src": "", "oport": 0},                       # 5: first-frame vae-encode
        {"src": "", "oport": 0},                       # 6: last-frame vae-encode
        {"src": "", "oport": 0},                       # 7
        {"src": "", "oport": 0},                       # 8
        {"src": "minimax-h3-model-config", "oport": 0}, # 9
    ]

    def add_cond_image(rel_path, port_idx, prefix):
        abspath = os.path.join(H3_ROOT, rel_path)
        stages.append({"id": f"{prefix}-load", "type": "load-image", "iports": [],
                        "config": {"url": [abspath]}})
        stages.append({"id": f"{prefix}-resample", "type": "image-resample",
                        "iports": [{"src": f"{prefix}-load", "oport": 0}],
                        "config": {"width": p["width"], "height": p["height"],
                                   "fit": "crop", "algorithm": "lanczos"}})
        stages.append({"id": f"{prefix}-encode", "type": "vae-encode",
                        "iports": [{"src": f"{prefix}-resample", "oport": 0},
                                   {"src": "model-select", "oport": 0}],
                        "config": {"unload_when_idle": "always"}})
        gv_iports[port_idx] = {"src": f"{prefix}-encode", "oport": 0}

    if job.get("first_frame"):
        add_cond_image(job["first_frame"], 5, "first-frame")
    if job.get("last_frame"):
        add_cond_image(job["last_frame"], 6, "last-frame")

    stages.append({"id": "generate-video", "type": "generate-video", "iports": gv_iports,
                    "config": {
                        "height": p["height"], "width": p["width"], "frames": p["frames"],
                        "fps": 24, "steps": p["steps"], "seed": p["seed"],
                        "i8_gemm": True, "unload_when_idle": "always",
                    }})
    stages.append({"id": "audio-vae-decode", "type": "audio-vae-decode",
                    "iports": [{"src": "generate-video", "oport": 1},
                               {"src": "model-select", "oport": 0}],
                    "config": {}})
    stages.append({"id": "vae-decode", "type": "vae-decode",
                    "iports": [{"src": "generate-video", "oport": 0},
                               {"src": "model-select", "oport": 0}],
                    "config": {}})
    stages.append({"id": "rgb-to-video", "type": "rgb-to-video",
                    "iports": [{"src": "vae-decode", "oport": 0}],
                    "config": {"fps": 24}})
    stages.append({"id": "save-video", "type": "save-video",
                    "iports": [{"src": "rgb-to-video", "oport": 0},
                               {"src": "audio-vae-decode", "oport": 0}],
                    "config": {
                        "output_url": os.path.join(H3_ROOT, job["outfile"]),
                        "enable_video": True, "enable_audio": True,
                    }})
    return {"id": "h3-studio-vpipe-job", "stages": stages, "subpipelines": []}


def build_krea2_spec(job):
    """Krea 2 Turbo text-to-image pipeline. Mirrors vpipe's own
    docs/pipelines/krea-2-text-to-image.vpipeline stage-for-stage, minus the
    M87 LoRA: krea2-model-config is left with an empty config (no lora/
    lora_scale keys) and the prompt carries no --preview trigger, since this
    project runs Krea 2 without any LoRA."""
    p = job["params"]
    return {
        "id": "krea2-text-to-image",
        "stages": [
            {"id": "model-select", "type": "model-select", "iports": [],
             "config": {"hf_dir": VPIPE_KREA2_MODEL}},
            {"id": "text-prompt", "type": "text-prompt", "iports": [],
             "config": {"text": job["prompt"]}},
            {"id": "krea2-model-config", "type": "krea2-model-config", "iports": [], "config": {}},
            {"id": "scheduler-select", "type": "scheduler-select", "iports": [],
             "config": {"steps": p["steps"], "shift": p.get("shift", KREA2_PARAMS["shift"])}},
            {"id": "diffusion-conditioner", "type": "diffusion-conditioner",
             "iports": [
                 {"src": "text-prompt", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "model-select", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "krea2-model-config", "oport": 0},
             ], "config": {}},
            {"id": "generate-image", "type": "generate-image",
             "iports": [
                 {"src": "diffusion-conditioner", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "model-select", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "scheduler-select", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "", "oport": 0},
                 {"src": "krea2-model-config", "oport": 0},
             ],
             "config": {"height": p["height"], "width": p["width"], "steps": p["steps"],
                        "seed": p["seed"], "i8_gemm": p.get("i8_gemm", KREA2_PARAMS["i8_gemm"])}},
            {"id": "vae-decode", "type": "vae-decode",
             "iports": [{"src": "generate-image", "oport": 0}, {"src": "model-select", "oport": 0}],
             "config": {}},
            {"id": "save-image", "type": "save-image",
             "iports": [{"src": "vae-decode", "oport": 0}],
             "config": {"path": os.path.join(H3_ROOT, job["outfile"]), "quality": 95}},
        ],
        "subpipelines": [],
    }


def build_klein_multiref_spec(job):
    """FLUX.2 klein-9B identity-preserving multi-reference pipeline. Mirrors
    vpipe's own docs/pipelines/klein-multi-ref.vpipeline stage-for-stage,
    generalized to 1 or 2 references (that example hardcodes 2), pointed at
    our own bf16 hf_dir instead of the example's 4-bit local one, and with
    no flux2-model-config stage — that's only needed for the -kv checkpoint
    variant, which this project doesn't use.

    Unlike Krea 2's single ref-latent (which doubles as an img2img init),
    FLUX.2 treats each reference as its own conditioning token stream, so
    there's no strength/blend knob here — the prompt itself must say what to
    keep from which reference image."""
    p = job["params"]
    refs = job["refs"][:KLEIN_MAX_REFS]
    stages = [
        {"id": "model-select", "type": "model-select", "iports": [],
         "config": {"hf_dir": VPIPE_KLEIN_MODEL}},
        {"id": "text-prompt", "type": "text-prompt", "iports": [],
         "config": {"text": job["prompt"]}},
        {"id": "diffusion-conditioner", "type": "diffusion-conditioner",
         "iports": [
             {"src": "text-prompt", "oport": 0},
             {"src": "", "oport": 0},
             {"src": "model-select", "oport": 0},
         ], "config": {}},
    ]
    ref_encode_ids = []
    for i, rel in enumerate(refs, start=1):
        load_id, resample_id, encode_id = f"load-image-{i}", f"image-resample-{i}", f"vae-encode-{i}"
        stages.append({"id": load_id, "type": "load-image", "iports": [],
                        "config": {"url": [os.path.join(H3_ROOT, rel)]}})
        stages.append({"id": resample_id, "type": "image-resample",
                        "iports": [{"src": load_id, "oport": 0}],
                        "config": {"width": 512, "height": 512, "fit": "crop"}})
        stages.append({"id": encode_id, "type": "vae-encode",
                        "iports": [{"src": resample_id, "oport": 0}, {"src": "model-select", "oport": 0}],
                        "config": {}})
        ref_encode_ids.append(encode_id)

    gen_iports = [
        {"src": "diffusion-conditioner", "oport": 0},
        {"src": "", "oport": 0},
        {"src": "model-select", "oport": 0},
        {"src": "", "oport": 0},
        {"src": "", "oport": 0},
    ]
    for encode_id in ref_encode_ids:
        gen_iports.append({"src": encode_id, "oport": 0})

    stages.append({"id": "generate-image", "type": "generate-image", "iports": gen_iports,
                    "config": {"width": p["width"], "height": p["height"], "steps": p["steps"],
                               "seed": p["seed"], "i8_gemm": p.get("i8_gemm", KLEIN_PARAMS["i8_gemm"])}})
    stages.append({"id": "vae-decode", "type": "vae-decode",
                    "iports": [{"src": "generate-image", "oport": 0}, {"src": "model-select", "oport": 0}],
                    "config": {}})
    stages.append({"id": "save-image", "type": "save-image",
                    "iports": [{"src": "vae-decode", "oport": 0}],
                    "config": {"path": os.path.join(H3_ROOT, job["outfile"]), "quality": 95}})
    return {"id": "klein-multi-ref", "stages": stages, "subpipelines": []}


class JobRunner:
    def __init__(self, bus):
        self.bus = bus
        self.lock = threading.Lock()
        self.pending = []
        self.current = None
        self.proc = None
        self.cancel_event = None  # set while a runpod job runs (no local process to kill)
        self.counter = 0
        self.sequences = {}
        self.seq_counter = 0
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()

    def snapshot(self):
        with self.lock:
            return {
                "current": dict(self.current) if self.current else None,
                "pending": [dict(j) for j in self.pending],
            }

    def enqueue(self, job, front=False):
        # front=True is for a sequence's own next leg: it should resume the
        # instant its predecessor finishes, ahead of anything else waiting,
        # so an in-flight chain runs to completion instead of interleaving
        # leg-by-leg with whatever else got queued in the meantime.
        with self.lock:
            self.counter += 1
            job["id"] = self.counter
            job["state"] = "pending"
            if front:
                self.pending.insert(0, job)
            else:
                self.pending.append(job)
        self.bus.publish({"type": "queue", **self.snapshot()})
        return job["id"]

    def start_sequence(self, items, params, refs=None, engine="h3", source=None, tag=None):
        """Enqueue the first clip of a chain; the rest are enqueued one at a
        time as each prior clip finishes, conditioned on its last frame (see
        _advance_sequence). `refs` are standing character/scene reference
        images attached to every clip in the chain (an "episode"). `source`
        is an internal-only tag (e.g. "auto" from AutoLoop) — never read from
        untrusted request data, only passed directly by trusted callers.
        `tag` prefixes every output filename in the chain (the auto profile id,
        e.g. "english-pov"); it defaults to "gui" for manual submissions."""
        refs = refs or []
        with self.lock:
            self.seq_counter += 1
            seq_id = self.seq_counter
        first, rest = items[0], items[1:]
        stamp = time.strftime("%Y%m%d-%H%M%S")
        job = {
            "prompt": first["prompt"], "mode": _clip_mode_label(None, refs),
            "engine": engine, "source": source,
            "params": dict(params, frames=first["frames"]),
            "refs": refs, "first_frame": None, "last_frame": None,
            "outfile": f"outputs/{outfile_prefix(tag)}-{stamp}-seed{params['seed']}.mp4",
            "seq_id": seq_id, "seq_pos": 1, "seq_total": len(items),
        }
        self.sequences[seq_id] = {
            "items": rest, "params": params, "refs": refs, "engine": engine, "source": source,
            "tag": tag, "files": [], "elapsed": 0.0,
            # Full round-trippable text: paste this back into the Sequence
            # tab and you get the same chain of clips back (durations are
            # the actual, post-snap frame counts, not what was originally typed).
            "joined_prompt": "\n\n=====\n\n".join(
                f"{_duration_label(it['frames'])} | {it['prompt']}" for it in items
            ),
            "total": len(items),
        }
        self.enqueue(job)
        return seq_id

    def start_image(self, prompt, params, refs=None, source=None):
        """Enqueue a single still — Krea 2 (text-only) or, when refs are
        given, FLUX.2 klein-9B's identity-preserving multi-reference path.
        Reuses the exact same queue/worker/history/SSE machinery as a video
        job — job['kind'] == 'image' plus whether 'refs' is non-empty is all
        _argv()/_loop() need to route it differently."""
        stamp = time.strftime("%Y%m%d-%H%M%S")
        job = {
            "prompt": prompt, "mode": "image", "kind": "image",
            "engine": "vpipe", "source": source, "params": params,
            "refs": refs or [], "first_frame": None, "last_frame": None,
            "outfile": f"outputs/gui-image-{stamp}-seed{params['seed']}.jpeg",
        }
        return self.enqueue(job)

    def _advance_sequence(self, seq_id, job, entry):
        # Runs on the worker thread right after a sequence clip finishes.
        # Never call snapshot()/publish while holding self.lock (see cancel()).
        seq = self.sequences.get(seq_id)
        if not seq:
            return
        seq["files"].append(job["outfile"])
        seq["elapsed"] += entry["elapsed_s"]
        seq["cost"] = seq.get("cost", 0) + entry.get("cost_usd", 0)
        if seq["items"]:
            nxt = seq["items"].pop(0)
            pos = seq["total"] - len(seq["items"])
            try:
                last_frame = extract_last_frame(os.path.join(H3_ROOT, job["outfile"]))
            except Exception as exc:
                del self.sequences[seq_id]
                self.bus.publish({"type": "seq-error", "seq_id": seq_id,
                                   "error": f"could not extract last frame: {exc}"})
                return
            stamp = time.strftime("%Y%m%d-%H%M%S")
            # First-frame conditioning and reference images are never
            # combined on one h3 call: an episode with standing refs folds
            # the continuity frame into that same reference list instead of
            # passing it as --first-frame; only a plain (ref-less) sequence
            # still uses --first-frame for continuity.
            if seq["refs"]:
                clip_refs, first_frame = seq["refs"] + [last_frame], None
            else:
                clip_refs, first_frame = [], last_frame
            next_job = {
                "prompt": nxt["prompt"], "mode": _clip_mode_label(first_frame, clip_refs),
                "engine": seq["engine"], "source": seq.get("source"),
                "params": dict(seq["params"], frames=nxt["frames"]),
                "refs": clip_refs, "first_frame": first_frame, "last_frame": None,
                "outfile": f"outputs/{outfile_prefix(seq.get('tag'))}-{stamp}-seed{seq['params']['seed']}.mp4",
                "seq_id": seq_id, "seq_pos": pos, "seq_total": seq["total"],
            }
            self.enqueue(next_job, front=True)
        else:
            del self.sequences[seq_id]
            self._finish_sequence(seq)

    def _finish_sequence(self, seq):
        try:
            outfile = merge_videos(seq["files"], seq.get("tag"))
            ok, error = True, None
        except Exception as exc:
            outfile, ok, error = None, False, str(exc)
        with self.lock:
            self.counter += 1
            entry_id = self.counter
        entry = {
            "id": entry_id, "ts": now_ms(), "ok": ok, "error": error,
            "elapsed_s": round(seq["elapsed"], 1), "prompt": seq["joined_prompt"],
            "mode": "sequence", "engine": seq.get("engine", "h3"), "source": seq.get("source"),
            "params": seq["params"], "refs": seq.get("refs", []),
            "first_frame": None, "last_frame": None, "file": outfile,
            "seq": {"clips": len(seq["files"]), "total": seq["total"]},
            "clips": list(seq["files"]),
        }
        if seq.get("cost"):
            entry["cost_usd"] = round(seq["cost"], 4)
        with HISTORY_LOCK:
            with open(HISTORY, "a") as fh:
                fh.write(json.dumps(entry) + "\n")
        self.bus.publish({"type": "done", "entry": entry})

    def append_derived_entry(self, base_entry, **overrides):
        """Append a new history entry derived from an existing one — e.g. a
        captioned variant of an already-merged sequence — reusing the same
        counter/lock/SSE-publish machinery as a real job so it behaves
        identically in the gallery (including live SSE delivery)."""
        with self.lock:
            self.counter += 1
            entry_id = self.counter
        entry = dict(base_entry)
        entry.update(overrides)
        entry["id"] = entry_id
        entry["ts"] = now_ms()
        with HISTORY_LOCK:
            with open(HISTORY, "a") as fh:
                fh.write(json.dumps(entry) + "\n")
        self.bus.publish({"type": "done", "entry": entry})
        return entry

    def cancel(self, job_id):
        # NB: never call snapshot()/publish while holding self.lock —
        # snapshot() re-acquires the (non-reentrant) lock and deadlocks
        # the whole server. Decide under the lock, publish after.
        result = "not-found"
        with self.lock:
            for j in list(self.pending):
                if j["id"] == job_id:
                    self.pending.remove(j)
                    # A removed sequence clip ends its sequence; otherwise the
                    # entry lingers and AutoLoop waits on it forever.
                    if j.get("seq_id") is not None:
                        self.sequences.pop(j["seq_id"], None)
                    result = "removed"
                    break
            else:
                if self.current and self.current["id"] == job_id and self.cancel_event:
                    self.cancel_event.set()
                    result = "terminating"
                elif self.current and self.current["id"] == job_id and self.proc:
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
            if self.cancel_event:
                self.cancel_event.set()
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
                "engine": job.get("engine", "h3"),
                "source": job.get("source"),
                "params": job["params"],
                "refs": job.get("refs", []),
                "first_frame": job.get("first_frame"),
                "last_frame": job.get("last_frame"),
                "file": job["outfile"] if ok else None,
            }
            if job.get("kind") == "image":
                entry["kind"] = "image"
            if job.get("engine") == "runpod":
                # GPU time this job held the pod. An estimate (the pod bills
                # by uptime, idle or not), but it's what a clip costs to make.
                entry["cost_usd"] = round(elapsed * GPU.rate / 3600, 4)
            if job.get("seq_id") is not None:
                entry["seq"] = {"pos": job["seq_pos"], "total": job["seq_total"]}
            with HISTORY_LOCK:
                with open(HISTORY, "a") as fh:
                    fh.write(json.dumps(entry) + "\n")
            if ok and job.get("kind") != "image":
                # append_bench() assumes video-shaped params (frames/reuse/
                # layers), which a Krea 2 still doesn't have.
                try:
                    append_bench(entry)
                except Exception as exc:
                    print(f"benchmarks.md append failed: {exc}", flush=True)
            with self.lock:
                self.current = None
                self.proc = None
                self.cancel_event = None
            self.bus.publish({"type": "done", "entry": entry})
            self.bus.publish({"type": "queue", **self.snapshot()})
            seq_id = job.get("seq_id")
            if seq_id is not None:
                if ok:
                    self._advance_sequence(seq_id, job, entry)
                else:
                    self.sequences.pop(seq_id, None)

    def _argv(self, job):
        if job.get("kind") == "image":
            if job.get("refs"):
                return [VPIPE_BIN, "--launch", json.dumps(build_klein_multiref_spec(job))]
            return [VPIPE_BIN, "--launch", json.dumps(build_krea2_spec(job))]
        if job.get("engine") == "vpipe":
            return [VPIPE_BIN, "--launch", json.dumps(build_vpipe_spec(job))]
        return self._h3_argv(job)

    def _h3_argv(self, job):
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
        # Field-based, not mode-gated: a sequence/episode clip can carry
        # both first-frame continuity and standing reference images at once.
        if job.get("first_frame"):
            argv += ["--first-frame", job["first_frame"]]
        if job.get("last_frame"):
            argv += ["--last-frame", job["last_frame"]]
        for ref in job.get("refs", []):
            argv += ["--ref-image", ref]
        return argv

    def _run(self, job):
        if job.get("engine") == "runpod":
            event = threading.Event()
            with self.lock:
                self.cancel_event = event
            return runpod_engine.run_job(job, H3_ROOT, GPU, self.bus.publish, event)
        started = time.time()
        engine = job.get("engine", "h3")
        cwd = VPIPE_WORK if engine == "vpipe" else H3_ROOT
        # h3's C stdio block-buffers progress prints to a plain pipe (updates
        # arrive minutes late, in bursts); a pty makes it flush like it does
        # in Terminal. vpipe is the opposite: its own logger already flushes
        # fine on a plain pipe, but handing it a pty instead flips it into an
        # interactive/ANSI progress-bar mode that doesn't emit the plain
        # "[PROGRESS] ..." lines this parses — confirmed by direct testing
        # (a pty capture showed 412 lines and zero "PROGRESS", where the same
        # job through a plain pipe showed dozens). So vpipe runs on a plain
        # pipe; only h3 gets the pty.
        use_pty = engine != "vpipe"
        master = slave = None
        try:
            if use_pty:
                master, slave = pty.openpty()
                self.proc = subprocess.Popen(
                    self._argv(job), cwd=cwd,
                    stdout=slave, stderr=slave,
                    start_new_session=True,
                )
            else:
                self.proc = subprocess.Popen(
                    self._argv(job), cwd=cwd,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
        except Exception as exc:
            if master is not None:
                os.close(master)
            if slave is not None:
                os.close(slave)
            return False, f"failed to launch {engine}: {exc}", 0.0
        if use_pty:
            os.close(slave)
            read_fd = master
        else:
            read_fd = self.proc.stdout.fileno()
        progress_re = VPIPE_PROGRESS_RE if engine == "vpipe" else PROGRESS_RE
        buf = b""
        tail = []
        last_pub = 0.0
        while True:
            try:
                chunk = os.read(read_fd, 1024)
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
                m = progress_re.search(line.strip())
                if m and time.time() - last_pub > 0.15:
                    last_pub = time.time()
                    self.bus.publish({
                        "type": "progress", "job": job["id"],
                        "phase": m.group(1).decode("utf-8", "replace").strip(),
                        "done": int(m.group(2)), "total": int(m.group(3)),
                        "elapsed": round(time.time() - started, 1),
                    })
        if use_pty:
            os.close(master)
        else:
            self.proc.stdout.close()
        code = self.proc.wait()
        elapsed = time.time() - started
        if code == 0 and os.path.isfile(os.path.join(H3_ROOT, job["outfile"])):
            return True, None, elapsed
        err = _pick_error(tail, engine)
        if code < 0:
            err = "canceled"
        return False, err or f"{engine} exited with code {code}", elapsed


class AutoLoop:
    """Unattended loop: ask `claude` to write a multi-clip script, submit it
    through the same Sequence path a person would use by hand, wait for it
    to drain, rest, repeat. Deliberately doesn't duplicate JobRunner's own
    success/failure tracking — the resulting history entries (tagged
    source="auto") are the source of truth for what actually got generated;
    this only tracks whether each cycle got a usable script from Claude and
    successfully handed it off."""

    # Each profile is a distinct content style/language, with its own prompt,
    # topic pool, and skill — kept separate rather than a single language
    # toggle because "English drama" and "English POV/social-media" want
    # completely different rules despite sharing a language.
    DEFAULT_PROFILES = {
        "tagalog-drama": {"label": "Tagalog / Taglish — ragebait drama", "caption": False},
        "english-drama": {"label": "English / international — short drama", "caption": False},
        "english-pov": {"label": "English / international — POV social-media", "caption": True},
        "modern-divide": {"label": "Modern Divide — two-sided debate (English)", "caption": False},
        "clocked-out": {"label": "Clocked Out — workplace ragebait (English)", "caption": False},
    }

    def __init__(self, runner):
        self.runner = runner
        self.lock = threading.Lock()
        self.running = False
        self.cycle_count = 0
        self.last_status = None
        self.last_status_at = None
        self.last_script = None
        self.phase = None  # "writing" / "generating" / "captioning" while a cycle is in flight
        self.next_run_at = None
        self.active_profile = "tagalog-drama"
        self.engine = "vpipe"
        self.profiles = {pid: dict(base, prompt="", topics=[])
                          for pid, base in self.DEFAULT_PROFILES.items()}
        self.cooldown_s = 300
        self.topic_queues = {}  # profile_id -> shuffled working copy, refilled when exhausted
        self.current_topic = None
        # Pipelining: while one episode renders, the next script is written
        # in the background, so the GPU doesn't sit idle during the 1-3 min
        # Claude call. prefetch_state: None / "writing" / "ready" / "failed".
        self.rotation = []  # profile ids to cycle through, one per episode; empty = active_profile only
        self.rotation_idx = 0
        self.prefetched = None
        self.prefetch_state = None
        self.prefetch_thread = None
        self.claude_usage = {}  # rateLimitType -> {pct, resets_at, status, at}, see _note_rate_limit
        self.gpu_stop_pending = False
        self._load_config()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _load_config(self):
        try:
            with open(AUTO_CONFIG_PATH) as fh:
                cfg = json.load(fh)
            if "profiles" in cfg:
                profiles_in = cfg.get("profiles", {})
                for pid, base in self.DEFAULT_PROFILES.items():
                    p = profiles_in.get(pid, {})
                    self.profiles[pid] = {
                        "label": base["label"],
                        "caption": base["caption"],
                        "prompt": p.get("prompt", ""),
                        "topics": [t for t in p.get("topics", []) if t],
                    }
                active = cfg.get("active_profile", "tagalog-drama")
                self.active_profile = active if active in self.profiles else "tagalog-drama"
                engine = cfg.get("engine", "vpipe")
                self.engine = engine if engine in ENGINES else "vpipe"
            else:
                # migrate from the older {language, prompts, topics} shape
                language = cfg.get("language", "tagalog")
                prompts = cfg.get("prompts") or {}
                topics = cfg.get("topics") or {}
                if isinstance(prompts, dict):
                    self.profiles["tagalog-drama"]["prompt"] = prompts.get("tagalog", cfg.get("prompt_text", ""))
                    self.profiles["english-drama"]["prompt"] = prompts.get("english", "")
                else:
                    self.profiles["tagalog-drama"]["prompt"] = cfg.get("prompt_text", "")
                if isinstance(topics, dict):
                    self.profiles["tagalog-drama"]["topics"] = [t for t in topics.get("tagalog", []) if t]
                    self.profiles["english-drama"]["topics"] = [t for t in topics.get("english", []) if t]
                else:
                    self.profiles["tagalog-drama"]["topics"] = [t for t in (topics or []) if t]
                self.active_profile = "english-drama" if language == "english" else "tagalog-drama"
            self.cooldown_s = max(0, int(cfg.get("cooldown_s", 300)))
            self.rotation = [p for p in cfg.get("rotation", []) if p in self.profiles]
        except FileNotFoundError:
            pass
        except Exception as exc:
            print(f"auto_config.json: failed to load ({exc}), using defaults", flush=True)

    def save_config(self, active_profile, profiles, cooldown_s, engine=None, rotation=None):
        with self.lock:
            if rotation is not None:
                self.rotation = [p for p in rotation if p in self.profiles]
            if active_profile in self.profiles:
                self.active_profile = active_profile
            if engine in ENGINES:
                self.engine = engine
            for pid, base in self.profiles.items():
                p = profiles.get(pid) or {}
                if "prompt" in p:
                    base["prompt"] = str(p["prompt"])
                if "topics" in p:
                    base["topics"] = [str(t).strip() for t in p["topics"] if str(t).strip()]
            self.cooldown_s = max(0, int(cooldown_s))
            self.topic_queues = {}  # force a fresh shuffle against the new pools
            snap = {
                "active_profile": self.active_profile,
                "engine": self.engine,
                "cooldown_s": self.cooldown_s,
                "rotation": self.rotation,
                "profiles": {pid: {"label": p["label"], "caption": p["caption"],
                                    "prompt": p["prompt"], "topics": p["topics"]}
                             for pid, p in self.profiles.items()},
            }
        with open(AUTO_CONFIG_PATH, "w") as fh:
            json.dump(snap, fh)

    def _next_profile(self):
        """The profile for the next script written: the next one in the
        rotation if one is set, otherwise the active profile."""
        with self.lock:
            if not self.rotation:
                return self.active_profile
            pid = self.rotation[self.rotation_idx % len(self.rotation)]
            self.rotation_idx += 1
            return pid

    def _profile_still_wanted(self, pid):
        with self.lock:
            return pid in self.rotation if self.rotation else pid == self.active_profile

    def _next_topic(self, profile_id=None):
        """Orchestrator-driven rotation, not model-driven choice: Claude was
        picking the same scenario back-to-back when just handed the whole
        list and told to choose — LLM sampling across independent, stateless
        calls doesn't reliably self-diversify. A shuffled queue that's
        refilled only once fully drained guarantees every topic gets used
        once before any repeat, instead of leaving variety up to chance.
        Kept per-profile so switching profiles doesn't disturb another
        pool's rotation progress."""
        with self.lock:
            profile_id = profile_id or self.active_profile
            pool = self.profiles.get(profile_id, {}).get("topics", [])
            used = self._load_used_topics()
            fresh = [t for t in pool if t not in used.get(profile_id, [])]
            if not fresh:
                # Every topic used once: start another round. Topics may repeat;
                # scripts may not (see the don't-repeat list in _write_script).
                used[profile_id] = []
                fresh = list(pool)
            topic = random.choice(fresh)
            used.setdefault(profile_id, []).append(topic)
            try:
                with open(AUTO_USED_TOPICS_PATH, "w") as fh:
                    json.dump(used, fh, indent=1)
            except OSError as exc:
                print(f"auto_used_topics.json: {exc}", flush=True)
            return topic

    @staticmethod
    def _load_used_topics():
        try:
            with open(AUTO_USED_TOPICS_PATH) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}

    @staticmethod
    def _past_hooks(limit=AUTO_AVOID_HOOKS):
        """Opening spoken line of every clip-1 (or standalone clip) in history,
        newest first, deduplicated: what's already been made, manual or Auto."""
        hooks, seen = [], set()
        try:
            with open(HISTORY) as fh:
                lines = fh.readlines()
        except OSError:
            return hooks
        for line in reversed(lines):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("kind") == "image" or e.get("mode") == "sequence" or e.get("variant"):
                continue
            if (e.get("seq") or {}).get("pos", 1) != 1:
                continue
            m = DIALOGUE_RE.search(e.get("prompt") or "")
            if not m:
                continue
            hook = " ".join(m.group(1).split())
            if len(re.sub(r"[^A-Za-z]", "", hook)) < 4:
                continue  # skip "...", "Ha?" and similar non-premise lines
            if hook.lower() not in seen:
                seen.add(hook.lower())
                hooks.append(hook)
                if len(hooks) >= limit:
                    break
        return hooks

    def snapshot(self):
        with self.lock:
            return {
                "running": self.running, "cycle_count": self.cycle_count,
                "last_status": self.last_status, "last_status_at": self.last_status_at,
                "last_script": self.last_script, "phase": self.phase,
                "current_topic": self.current_topic, "next_run_at": self.next_run_at,
                "prefetch": self.prefetch_state, "current_profile": getattr(self, "current_profile", None),
                "claude_usage": dict(self.claude_usage), "claude_stop_pct": AUTO_CLAUDE_STOP_PCT,
                "gpu_stop_pending": self.gpu_stop_pending,
                "config": {"active_profile": self.active_profile, "engine": self.engine,
                           "cooldown_s": self.cooldown_s, "rotation": self.rotation,
                           "profiles": self.profiles},
            }

    def start(self):
        if not os.access(CLAUDE_BIN, os.X_OK):
            raise ValueError("Auto needs the Claude Code CLI (`claude`) to write scripts: install it from "
                              "claude.com/claude-code and log in once by running `claude` in a terminal")
        if self.engine == "vpipe" and not VPIPE_AVAILABLE:
            raise ValueError("vpipe engine isn't set up on this machine")
        if self.engine == "runpod":
            if not runpod_engine.runpod_available():
                raise ValueError("Runpod engine isn't set up (runpodctl has no API key)")
            if GPU.snapshot()["state"] in ("off", "error"):
                GPU.start()  # starting Auto on Runpod implies the GPU; jobs wait for setup
        with self.lock:
            for pid in (self.rotation or [self.active_profile]):
                if not self.profiles.get(pid, {}).get("prompt", "").strip():
                    raise ValueError(f"no prompt text saved for '{pid}' — "
                                      f"set one via /api/auto/config first")
            self.running = True
            self.gpu_stop_pending = False
            self.next_run_at = now_ms()

    def stop(self):
        with self.lock:
            self.running = False
            self.next_run_at = None

    def _run_claude(self, prompt):
        try:
            r = subprocess.run(
                # stream-json (not json) so the rate_limit_event messages come
                # through too: they carry the plan's usage, see _note_rate_limit.
                [CLAUDE_BIN, "-p", prompt, "--output-format", "stream-json", "--verbose",
                 "--permission-mode", "dontAsk", "--model", CLAUDE_MODEL],
                cwd=H3_ROOT, capture_output=True, timeout=AUTO_CLAUDE_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            return None, "claude CLI timed out"
        except Exception as exc:
            return None, f"failed to launch claude: {exc}"
        data = None
        for line in r.stdout.decode("utf-8", "replace").splitlines():
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue
            if msg.get("type") == "rate_limit_event":
                self._note_rate_limit(msg.get("rate_limit_info") or {})
            elif msg.get("type") == "result":
                data = msg
        if data is None:
            return None, f"claude CLI produced no result message: {r.stdout[-300:]!r}"
        if data.get("is_error"):
            err = str(data.get("result") or data)
            if any(k in err.lower() for k in ("session limit", "usage limit", "weekly limit", "hit your")):
                self._note_rate_limit({"status": "rejected", "rateLimitType": "limit-error"})
            return None, f"claude CLI reported an error: {err}"
        result = data.get("result")
        if not result:
            return None, "claude CLI returned no result text"
        return result, None

    def _note_rate_limit(self, info):
        """Record the plan's usage from a rate_limit_event. Utilization comes
        as a 0-1 fraction (treated as a percentage if > 1); a rejected status
        counts as 100%. At AUTO_CLAUDE_STOP_PCT or more, Auto stops writing
        and the GPU is shut down once the episode in flight finishes."""
        util = info.get("utilization")
        pct = None
        if isinstance(util, (int, float)):
            pct = util * 100 if util <= 1 else float(util)
        if info.get("status") == "rejected":
            pct = 100.0
        if pct is None:
            return
        kind = info.get("rateLimitType") or "unknown"
        with self.lock:
            self.claude_usage[kind] = {"pct": round(pct, 1), "resets_at": info.get("resetsAt"),
                                       "status": info.get("status"), "at": now_ms()}
            trip = pct >= AUTO_CLAUDE_STOP_PCT and self.running
            if trip:
                self.running = False
                self.next_run_at = None
                self.gpu_stop_pending = True
        if trip:
            print(f"AutoLoop: Claude usage {kind} at {pct:.0f}% (>= {AUTO_CLAUDE_STOP_PCT}%), "
                  f"stopping Auto; GPU stops once the current episode finishes", flush=True)

    def _gpu_stop_when_idle(self):
        """The GPU half of the Claude-usage stop: wait for the queue (and any
        sequence mid-chain) to drain, then stop the pod."""
        with self.lock:
            if not self.gpu_stop_pending:
                return
        q = self.runner.snapshot()
        if q["current"] or q["pending"] or self.runner.sequences:
            return
        with self.lock:
            self.gpu_stop_pending = False
        if GPU.snapshot()["state"] not in ("off", "stopping"):
            print("AutoLoop: queue empty after the Claude-usage stop, stopping the GPU", flush=True)
            GPU.stop()

    def _add_caption(self, script_text, min_history_id):
        """Post-process step: ask Claude for a short Snapchat-style caption
        based on the full script, then burn it onto the just-merged
        sequence's video as a separate history entry (the uncaptioned merge
        stays too — see append_derived_entry). Kept out of H3 generation
        itself because a video model rendering on-screen text is unreliable
        (misspellings, inconsistent style between clips); a deterministic
        post-process overlay isn't."""
        prompt = (
            "Here is the full script for a short video (visual direction + dialogue):\n\n"
            f"{script_text}\n\n"
            "Write ONE short Snapchat/TikTok-style caption for this video — the kind of "
            "punchy, curiosity-hooking phrase that appears as a text overlay at the top of "
            "a POV/confession-style social video (for example: \"the way he looked at her when "
            "she walked in\", \"POV: you just found out\", \"tell me why he said this\"). "
            "A few words to one short sentence. No quotation marks, no hashtags, no emoji, "
            "no markdown, no explanation before or after. Output ONLY the caption text itself."
        )
        text, err = self._run_claude(prompt)
        if err or not text:
            raise RuntimeError(err or "empty caption from claude")
        caption = " ".join(text.strip().split())
        caption = caption.strip("\"'“”‘’")
        if len(caption) > 120:
            caption = caption[:117].rstrip() + "..."
        if not caption:
            raise RuntimeError("caption sanitized to an empty string")

        # Must be a NEW entry from this cycle's own sequence — not a stale
        # entry from a previous cycle (e.g. if this cycle's sequence was
        # canceled/failed before ever merging, the most-recent "sequence"
        # entry in history would otherwise be an older, possibly already-
        # captioned one, and we'd burn a second caption on top of it.
        entry = next((h for h in read_history(limit=5)
                      if h.get("source") == "auto" and h.get("mode") == "sequence"
                      and h.get("id", 0) > min_history_id
                      and h.get("variant") != "captioned"), None)
        if not entry or not entry.get("ok") or not entry.get("file"):
            raise RuntimeError("no usable merged sequence entry found to caption")

        p = entry.get("params") or {}
        width, height = p.get("width", AUTO_PARAMS["width"]), p.get("height", AUTO_PARAMS["height"])
        captioned_file = burn_caption(entry["file"], caption, width, height)
        self.runner.append_derived_entry(entry, file=captioned_file, caption=caption, variant="captioned")

    def _write_script(self):
        """Pick the next topic and have Claude write a script, then parse and
        validate it. Returns (script, None) or (None, (status, detail))."""
        profile_id = self._next_profile()
        topic = self._next_topic(profile_id)
        with self.lock:
            prompt = self.profiles.get(profile_id, {}).get("prompt", "")
            engine = self.engine
        if topic:
            prompt += (f"\n\nFor this specific request, use EXACTLY this scenario — do not "
                       f"substitute a different one, do not blend it with another idea: {topic}")
        else:
            prompt += ("\n\nInvent a brand-new scenario for this request, following the skill's own "
                       "topic-rotation and variation rules.")
        hooks = self._past_hooks()
        if hooks:
            prompt += ("\n\nThese are the opening lines of videos ALREADY produced. The topic may "
                       "overlap with some of them, and that's fine, but the SCRIPT must be new: a different "
                       "opening line, different dialogue, a different escalation and a different final "
                       "line, with different characters and setting details. Do NOT copy or lightly "
                       "reword any of these lines:\n"
                       + "\n".join(f"- {h}" for h in hooks))
        text, err = self._run_claude(prompt)
        if err:
            return None, ("claude-failed", err)
        raw_items = parse_sequence_text(text, AUTO_CLIP_FRAMES)
        if len(raw_items) < 2:
            with self.lock:
                self.last_script = text
            return None, ("parse-failed", f"claude's output didn't parse into >=2 clips (got {len(raw_items)})")
        base_params = {"h3": H3_AUTO_PARAMS, "runpod": runpod_engine.RUNPOD_PARAMS}.get(engine, AUTO_PARAMS)
        data = {"engine": engine, "items": raw_items,
                "params": dict(base_params, seed=random.randint(0, 2**31 - 1))}
        try:
            items, params, refs, engine = validate_sequence(data)
        except ValueError as exc:
            with self.lock:
                self.last_script = text
            return None, ("parse-failed", str(exc))
        return {"text": text, "topic": topic, "profile": profile_id, "items": items,
                "params": params, "refs": refs, "engine": engine}, None

    def _prefetch(self):
        script, failure = self._write_script()
        with self.lock:
            self.prefetched = script
            self.prefetch_state = "ready" if script else "failed"
        if failure:
            print(f"AutoLoop prefetch: {failure[0]} — {failure[1]}", flush=True)

    def _run_cycle(self):
        # A prefetch still in flight from the previous cycle: wait for it
        # rather than starting a second, competing Claude call.
        thread = self.prefetch_thread
        if thread and thread.is_alive():
            with self.lock:
                self.phase = "writing"
            thread.join()
        with self.lock:
            script, self.prefetched = self.prefetched, None
            self.prefetch_state = None
            # Discard a prefetched script if the engine/profile changed since.
            engine_now = self.engine
        if script and (script["engine"] != engine_now or not self._profile_still_wanted(script["profile"])):
            script = None
        if not script:
            with self.lock:
                self.phase = "writing"
            script, failure = self._write_script()
            if failure:
                with self.lock:
                    self.phase = None
                return failure
        with self.lock:
            if not self.running:
                # Stopped while the script was being written (e.g. the
                # Claude-usage stop): don't start another episode.
                self.phase = None
                return "stopped", None
            self.current_topic = script["topic"]
            self.current_profile = script["profile"]
            self.last_script = script["text"]
            self.phase = "generating"
            caption_enabled = self.profiles.get(script["profile"], {}).get("caption", False)
        pre_history = read_history(limit=1)
        min_history_id = pre_history[0]["id"] if pre_history else 0
        seq_id = self.runner.start_sequence(script["items"], script["params"], script["refs"],
                                            script["engine"], source="auto", tag=script["profile"])
        with self.lock:
            if self.running:
                self.prefetch_state = "writing"
                self.prefetch_thread = threading.Thread(target=self._prefetch, daemon=True)
                self.prefetch_thread.start()
        while seq_id in self.runner.sequences:
            time.sleep(2)
        if caption_enabled:
            with self.lock:
                self.phase = "captioning"
            try:
                self._add_caption(script["text"], min_history_id)
            except Exception as exc:
                with self.lock:
                    self.phase = None
                return "submitted", f"caption step failed: {exc}"
        with self.lock:
            self.phase = None
        return "submitted", None

    def _loop(self):
        while True:
            with self.lock:
                running = self.running
            if running and self.engine == "runpod" and GPU.low_balance:
                print("AutoLoop: Runpod balance too low, stopping Auto", flush=True)
                self.stop()
                running = False
            if running and self.engine == "runpod" and GPU.snapshot()["state"] in ("off", "error", "stopping"):
                # Writing scripts the GPU can't render would just burn Claude usage
                # in a fail-fast loop (each episode fails instantly with "GPU is off").
                print("AutoLoop: GPU is not running, stopping Auto", flush=True)
                self.stop()
                running = False
            if not running:
                self._gpu_stop_when_idle()
                time.sleep(1)
                continue
            status, detail = self._run_cycle()
            with self.lock:
                self.cycle_count += 1
                self.last_status = status
                self.last_status_at = now_ms()
                still_running = self.running
                if still_running:
                    self.next_run_at = now_ms() + self.cooldown_s * 1000
            if detail:
                print(f"AutoLoop cycle {self.cycle_count}: {status} — {detail}", flush=True)
            if not still_running:
                continue
            # Back off on failed script writing instead of hammering claude
            # (with cooldown 0, a usage limit made it retry ~540 times while
            # the GPU sat idle). 1, 2, 4 ... 15 min; resets on any success.
            if status in ("claude-failed", "parse-failed"):
                self.fail_streak = getattr(self, "fail_streak", 0) + 1
                wait = min(900, 60 * 2 ** (self.fail_streak - 1))
            else:
                self.fail_streak = 0
                wait = self.cooldown_s
            with self.lock:
                self.next_run_at = now_ms() + wait * 1000
            slept = 0.0
            while slept < wait:
                time.sleep(min(1.0, wait - slept))
                slept += 1.0
                with self.lock:
                    if not self.running:
                        break


BUS = Broadcaster()
GPU = runpod_engine.RunpodManager(BUS, os.path.join(GUI_DIR, "runpod_config.json"),
                                  os.path.join(GUI_DIR, "runpod_sessions.jsonl"), HISTORY)
RUNNER = JobRunner(BUS)
AUTO = AutoLoop(RUNNER)
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
    "| when | mode | size | MP | frames | steps | reuse | layers | memory | time | engine | notes |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def bench_row(entry):
    p = entry["params"]
    mp = p["width"] * p["height"] / 1e6
    secs = float(entry["elapsed_s"])
    t = f"{int(secs // 60)}m{int(round(secs % 60)):02d}s"
    mode = {"text": "text", "firstlast": "first/last",
            "refs": f"refs x{len(entry.get('refs') or [])}"}.get(entry["mode"], entry["mode"])
    engine = entry.get("engine", "h3")
    mem = "remote" if engine == "runpod" else ("ssd-stream" if p.get("ssd_streaming", True) else "resident")
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(entry["ts"] / 1000))
    return (f"| {when} | {mode} | {p['width']}x{p['height']} | {mp:.2f} | {p['frames']} "
            f"| {p['steps']} | {p['reuse']} | {p['layers']} | {mem} | {t} | {engine} |  |\n")


def parse_bench():
    # New rows append an `engine` column (index 10) after `time`; older rows
    # written before vpipe existed lack it and default to "h3" — both widths
    # satisfy `len(c) >= 10` so existing positional reads (c[2]..c[9]) are
    # unaffected either way.
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
                    "engine": c[10] if len(c) > 10 and c[10] else "h3",
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


def extract_last_frame(video_abs_path):
    """Grab the last decoded frame of a clip and stash it in inputs/ under
    the same content-hash naming convention as uploads, so it can be fed
    straight back in as --first-frame."""
    tmp = os.path.join(INPUTS, f".tmp-lastframe-{now_ms()}.jpg")
    cmd = [FFMPEG, "-y", "-sseof", "-3", "-i", video_abs_path,
           "-update", "1", "-q:v", "2", tmp]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=60)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found on PATH")
    if r.returncode != 0 or not os.path.isfile(tmp):
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip()[-300:] or "ffmpeg failed")
    with open(tmp, "rb") as fh:
        data = fh.read()
    os.remove(tmp)
    digest = hashlib.sha256(data).hexdigest()[:10]
    final = f"{digest}-lastframe.jpg"
    if not os.path.isfile(os.path.join(INPUTS, final)):
        with open(os.path.join(INPUTS, final), "wb") as fh:
            fh.write(data)
    return os.path.join("inputs", final)


def _concat_escape(path):
    return path.replace("'", "'\\''")


def outfile_prefix(tag):
    """Leading filename segment for generated outputs.

    Auto-loop jobs pass their profile id ("english-pov", "tagalog-drama", ...)
    so a finished file says on its face what kind of drama it is. Manual
    submissions have no profile and keep the historic "gui" prefix. Sanitised
    because it lands in a filename."""
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", str(tag or "")).strip("-")
    return safe or "gui"


def merge_videos(files, tag=None):
    """Concatenate finished sequence clips (in order) into one MP4."""
    if not files:
        raise RuntimeError("no clips to merge")
    if len(files) == 1:
        return files[0]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    outfile = f"outputs/final/{outfile_prefix(tag)}-seq-{stamp}.mp4"
    listpath = os.path.join(OUTPUTS, f".concat-{stamp}.txt")
    with open(listpath, "w") as fh:
        for f in files:
            abspath = os.path.join(H3_ROOT, f)
            fh.write(f"file '{_concat_escape(abspath)}'\n")
    try:
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listpath,
               "-c", "copy", os.path.join(H3_ROOT, outfile)]
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode != 0:
            # streams weren't concat-copy-compatible (rare) — re-encode instead
            cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listpath,
                   "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                   "-c:a", "aac", "-b:a", "192k", os.path.join(H3_ROOT, outfile)]
            r = subprocess.run(cmd, capture_output=True, timeout=1800)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8", "replace").strip()[-400:] or "ffmpeg concat failed")
    finally:
        try:
            os.remove(listpath)
        except OSError:
            pass
    return outfile


def render_caption_bar(width, height, text):
    """Render a classic Snapchat-style caption bar (full-width translucent
    gray bar, centered white bold text, upper third of the frame) as an
    RGBA PNG the same size as the video, ready to be composited with
    ffmpeg's `overlay` filter. Bar height grows to fit wrapped text."""
    pad_x = int(width * 0.06)
    max_text_w = width - 2 * pad_x
    font_size = max(16, int(width * 0.042))
    font = ImageFont.truetype(CAPTION_FONT_PATH, font_size)

    scratch = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(scratch)

    def line_width(s):
        box = draw.textbbox((0, 0), s, font=font)
        return box[2] - box[0]

    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if line_width(trial) <= max_text_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lines = lines[:3]  # hard cap — a caption this long isn't "a few words" anymore

    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    line_spacing = int(line_h * 0.35)
    text_block_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
    pad_y = int(font_size * 0.6)
    bar_h = text_block_h + 2 * pad_y
    bar_top = int(height * 0.12)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, bar_top, width, bar_top + bar_h], fill=CAPTION_BAR_RGBA)

    y = bar_top + pad_y
    for line in lines:
        w = line_width(line)
        x = (width - w) // 2
        draw.text((x, y), line, font=font, fill=CAPTION_TEXT_COLOR)
        y += line_h + line_spacing
    return img


def burn_caption(src_rel, caption_text, width, height):
    """Composite a caption bar onto src_rel (an outputs/-relative mp4 path)
    and return the new file's outputs/-relative path. Re-encodes video
    (overlay always requires it); audio is stream-copied unchanged."""
    caption_img = render_caption_bar(width, height, caption_text)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    png_path = os.path.join(OUTPUTS, f".caption-{stamp}.png")
    caption_img.save(png_path)
    stem = os.path.splitext(os.path.basename(src_rel))[0]
    outfile = f"outputs/final/{stem}-captioned.mp4"
    try:
        cmd = [
            FFMPEG, "-y", "-i", os.path.join(H3_ROOT, src_rel), "-i", png_path,
            "-filter_complex", "[0:v][1:v]overlay=0:0[v]",
            "-map", "[v]", "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-c:a", "copy",
            os.path.join(H3_ROOT, outfile),
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode("utf-8", "replace").strip()[-400:] or "ffmpeg overlay failed")
    finally:
        try:
            os.remove(png_path)
        except OSError:
            pass
    return outfile


def output_file(name):
    """Absolute path of an output by basename: outputs/ or outputs/final/."""
    name = safe_name(os.path.basename(name))
    for d in (OUTPUTS, FINALS):
        full = os.path.join(d, name)
        if os.path.isfile(full):
            return full
    return os.path.join(OUTPUTS, name)


def trash_file(name):
    """Move an outputs/ file to the macOS Trash (recoverable, never rm)."""
    full = output_file(name)
    if not os.path.isfile(full):
        return False
    if IS_MAC:
        script = f'tell application "Finder" to delete POSIX file "{full}"'
        subprocess.run(["osascript", "-e", script], check=False,
                       capture_output=True, timeout=15)
    else:
        # No system trash to rely on everywhere: park it in outputs/.trash/.
        trash = os.path.join(OUTPUTS, ".trash")
        os.makedirs(trash, exist_ok=True)
        shutil.move(full, os.path.join(trash, os.path.basename(full)))
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


def collapse_sequences(entries):
    """Hide the individual clips of a merged sequence and attach them to the
    merged entry as `clip_entries`, so the gallery shows one card per episode
    with links to its clips. `entries` is chronological. Newer merged entries
    list their clip files in `clips`; older ones are matched by seed + engine,
    scanning back from the merge. Clips of sequences that never merged stay
    visible."""
    hidden = set()
    for i, e in enumerate(entries):
        if e.get("mode") != "sequence" or e.get("variant"):
            continue
        files = set(e.get("clips") or [])
        want = (e.get("seq") or {}).get("clips", 0)
        found = []
        for j in range(i - 1, max(-1, i - 1 - 4 * max(want, 1) - 6), -1):
            c = entries[j]
            if j in hidden or not c.get("seq") or "pos" not in c["seq"]:
                continue
            if files:
                match = c.get("file") in files
            else:
                match = ((c.get("params") or {}).get("seed") == (e.get("params") or {}).get("seed")
                         and c.get("engine", "h3") == e.get("engine", "h3") and c.get("ok"))
            if match:
                found.append(j)
                if len(found) >= want:
                    break
        if not found:
            continue
        hidden.update(found)
        e["clip_entries"] = sorted(
            ({k: entries[j].get(k) for k in ("id", "ts", "file", "elapsed_s", "cost_usd", "ok", "prompt")}
             | {"pos": entries[j]["seq"]["pos"]} for j in found), key=lambda c: c["pos"])
    # captioned variants reuse their source episode's clips
    by_file = {e.get("file"): e for e in entries if e.get("clip_entries")}
    for e in entries:
        if e.get("variant") == "captioned" and not e.get("clip_entries"):
            src = next((x for x in by_file.values() if x.get("seq") == e.get("seq")
                        and (x.get("params") or {}).get("seed") == (e.get("params") or {}).get("seed")), None)
            if src:
                e["clip_entries"] = src["clip_entries"]
    return [e for k, e in enumerate(entries) if k not in hidden]


def read_history(limit=200, offset=0, source=None, kind=None):
    entries = []
    if os.path.isfile(HISTORY):
        with open(HISTORY) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if source is not None and entry.get("source") != source:
                    continue
                if kind is not None and entry.get("kind", "video") != kind:
                    continue
                entries.append(entry)
    if kind != "image":
        entries = collapse_sequences(entries)
    entries.reverse()  # newest first
    return entries[offset:offset + limit]


def history_total(source=None, kind=None):
    # Same filtering and sequence collapsing as read_history, so pagination matches.
    return len(read_history(limit=10**9, source=source, kind=kind))


def resolve_input(rel):
    """Resolve an uploaded/generated inputs/ filename to a verified rel path."""
    if not rel:
        return None
    rel = os.path.join("inputs", safe_name(rel))
    if not os.path.isfile(os.path.join(H3_ROOT, rel)):
        raise ValueError(f"missing input image: {rel}")
    return rel


def _validate_engine(data):
    engine = data.get("engine", "h3")
    if engine not in ENGINES:
        raise ValueError("bad engine")
    if engine == "vpipe" and not VPIPE_AVAILABLE:
        raise ValueError("vpipe engine isn't set up on this machine")
    if engine == "h3" and not H3_AVAILABLE:
        raise ValueError("the local h3 engine isn't set up on this machine; use the Runpod engine")
    if engine == "runpod" and not runpod_engine.runpod_available():
        raise ValueError("Runpod engine isn't set up (runpodctl has no API key)")
    return engine


def validate_job(data):
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        raise ValueError("prompt is empty")
    engine = _validate_engine(data)
    mode = data.get("mode", "text")
    if mode not in ("text", "firstlast", "refs"):
        raise ValueError("bad mode")
    if mode == "refs" and engine == "vpipe":
        raise ValueError("references mode needs the vpipe Ref2VA model, which isn't prepared")
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

    refs = [resolve_input(r) for r in (data.get("refs") or [])][:9]
    refs = [r for r in refs if r]
    first = resolve_input(data.get("first_frame"))
    last = resolve_input(data.get("last_frame"))
    if mode == "refs" and not refs:
        raise ValueError("references mode needs at least one image")
    if mode == "firstlast" and not first and not last:
        raise ValueError("first/last mode needs at least one anchor image")

    # Milliseconds too: two jobs with the same seed submitted in the same second
    # (e.g. a script posting several clips) used to get the same filename and
    # overwrite each other.
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"{now_ms() % 1000:03d}"
    outfile = f"outputs/gui-{stamp}-seed{seed}.mp4"
    return {
        "prompt": prompt, "mode": mode, "engine": engine,
        "params": {
            "width": width, "height": height, "frames": frames,
            "steps": steps, "reuse": reuse, "layers": layers,
            "seed": seed, "ssd_streaming": bool(p.get("ssd_streaming", True)),
            **({"turbo": bool(p.get("turbo", True))} if engine == "runpod" else {}),
        },
        "refs": refs if mode == "refs" else [],
        "first_frame": first if mode == "firstlast" else None,
        "last_frame": last if mode == "firstlast" else None,
        "outfile": outfile,
    }


def validate_sequence(data):
    """Validate a chain of {prompt, frames} clips sharing one settings block.
    Clip 1 renders from text; each later clip is conditioned on the previous
    clip's last frame (mode "firstlast", filled in once that frame exists)."""
    engine = _validate_engine(data)
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or len(raw_items) < 2:
        raise ValueError("a sequence needs at least 2 prompts")
    if len(raw_items) > SEQ_MAX_CLIPS:
        raise ValueError(f"sequences are limited to {SEQ_MAX_CLIPS} clips")

    def frame_count(v, i):
        try:
            v = int(round(float(v)))
        except (TypeError, ValueError):
            raise ValueError(f"clip {i + 1}: duration must be a number")
        if not (22 <= v <= 361):
            raise ValueError(f"clip {i + 1}: duration out of range")
        if (v - 5) % 17:
            v = 22 + 17 * max(0, round((v - 22) / 17))
        return v

    items = []
    for i, it in enumerate(raw_items):
        if not isinstance(it, dict):
            raise ValueError(f"clip {i + 1} is malformed")
        prompt = (it.get("prompt") or "").strip()
        if not prompt:
            raise ValueError(f"clip {i + 1}: prompt is empty")
        items.append({"prompt": prompt, "frames": frame_count(it.get("frames"), i)})

    # Reuse validate_job's numeric/range checks for the shared settings block
    # by probing it with the first clip as a plain text job.
    probe = {
        "prompt": items[0]["prompt"], "mode": "text", "engine": engine,
        "params": dict(data.get("params") or {}, frames=items[0]["frames"]),
    }
    base = validate_job(probe)

    # Episode-standing reference images (characters/scenes): sent once,
    # attached to every clip. Capped at 8, not h3's usual 9 — clip 2 onward
    # folds the previous clip's last frame into this same list (in place of
    # --first-frame, never alongside it), so one slot is always reserved.
    # vpipe has no episode-refs path here (needs Ref2VA, not prepared).
    refs = [resolve_input(r) for r in (data.get("refs") or [])][:SEQ_REF_CAP]
    refs = [r for r in refs if r]
    if refs and engine == "vpipe":
        raise ValueError("episode references need the vpipe Ref2VA model, which isn't prepared")

    return items, base["params"], refs, engine


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
            return self._json({"queue": RUNNER.snapshot(),
                                "history": read_history(limit=STATE_HISTORY_LIMIT, kind="video"),
                                "vpipe_available": VPIPE_AVAILABLE,
                                "h3_available": H3_AVAILABLE,
                                "keep_awake_supported": IS_MAC,
                                "runpod_available": runpod_engine.runpod_available(),
                                "runpod_params": runpod_engine.RUNPOD_PARAMS,
                                "gpu": GPU.snapshot(),
                                "krea2_available": krea2_available(),
                                "klein_available": klein_available()})
        if path == "/api/history":
            from urllib.parse import parse_qs, urlparse
            q = parse_qs(urlparse(self.path).query)
            try:
                limit = min(max(int((q.get("limit") or ["50"])[0]), 1), 200)
                offset = max(int((q.get("offset") or ["0"])[0]), 0)
            except ValueError:
                return self._json({"error": "limit/offset must be integers"}, 400)
            source = (q.get("source") or [None])[0]
            kind = (q.get("kind") or [None])[0]
            entries = read_history(limit=limit, offset=offset, source=source, kind=kind)
            return self._json({"entries": entries, "total": history_total(source=source, kind=kind),
                                "offset": offset, "limit": limit})
        if path == "/api/auto/state":
            return self._json(AUTO.snapshot())
        if path == "/api/gpu/state":
            return self._json(GPU.snapshot())
        if path == "/api/gpu/comfylog":
            return self._json({"log": GPU.comfy_log()})
        if path == "/api/caffeinate/state":
            return self._json({"enabled": CAFFEINATE_PROC is not None and CAFFEINATE_PROC.poll() is None})
        if path == "/api/events":
            return self._sse()
        if path.startswith("/videos/"):
            name = safe_name(path[len("/videos/"):])
            ext = os.path.splitext(name)[1].lower()
            if ext in (".jpg", ".jpeg"):
                return self._file(output_file(name), "image/jpeg")
            return self._file(output_file(name), "video/mp4", ranged=True)
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
            if path == "/api/sequence":
                items, params, refs, engine = validate_sequence(json.loads(self._body() or b"{}"))
                seq_id = RUNNER.start_sequence(items, params, refs, engine)
                return self._json({"ok": True, "seq_id": seq_id, "clips": len(items)})
            if path == "/api/image":
                data = json.loads(self._body() or b"{}")
                prompt = (data.get("prompt") or "").strip()
                if not prompt:
                    raise ValueError("prompt is empty")
                refs = [resolve_input(r) for r in (data.get("refs") or [])][:KLEIN_MAX_REFS]
                refs = [r for r in refs if r]
                defaults = KLEIN_PARAMS if refs else KREA2_PARAMS
                if refs and not klein_available():
                    raise ValueError("FLUX.2 klein-9B model isn't downloaded on this machine yet")
                if not refs and not krea2_available():
                    raise ValueError("Krea 2 model isn't downloaded on this machine yet")
                width = int(data.get("width", defaults["width"]))
                height = int(data.get("height", defaults["height"]))
                if width % 16 or height % 16 or width < 256 or height < 256:
                    raise ValueError("width/height must be multiples of 16 and at least 256")
                steps = int(data.get("steps", defaults["steps"]))
                if steps < 1 or steps > 20:
                    raise ValueError("steps must be between 1 and 20")
                seed = int(data.get("seed", random.randint(0, 2**31 - 1)))
                if refs:
                    params = {"width": width, "height": height, "steps": steps,
                              "i8_gemm": KLEIN_PARAMS["i8_gemm"], "seed": seed}
                else:
                    params = {"width": width, "height": height, "steps": steps,
                              "shift": KREA2_PARAMS["shift"], "i8_gemm": KREA2_PARAMS["i8_gemm"], "seed": seed}
                job_id = RUNNER.start_image(prompt, params, refs=refs)
                return self._json({"ok": True, "id": job_id})
            if path == "/api/gpu/start":
                GPU.start()
                return self._json({"ok": True})
            if path == "/api/gpu/stop":
                GPU.stop()
                return self._json({"ok": True})
            if path == "/api/gpu/config":
                data = json.loads(self._body() or b"{}")
                GPU.set_idle_minutes(int(data.get("idle_minutes", GPU.idle_minutes)))
                return self._json({"ok": True})
            if path == "/api/auto/start":
                AUTO.start()
                return self._json({"ok": True})
            if path == "/api/auto/stop":
                AUTO.stop()
                return self._json({"ok": True})
            if path == "/api/auto/config":
                data = json.loads(self._body() or b"{}")
                active_profile = data.get("active_profile", AUTO.active_profile)
                if active_profile not in AUTO.profiles:
                    raise ValueError(f"active_profile must be one of {sorted(AUTO.profiles)}")
                # Only profiles (and fields) present in the request are changed, so an
                # API caller can update one profile without wiping the others.
                profiles_in = data.get("profiles") or {}
                profiles = {}
                for pid, p in profiles_in.items():
                    if pid not in AUTO.profiles or not isinstance(p, dict):
                        raise ValueError(f"unknown profile '{pid}'; profiles are {sorted(AUTO.profiles)}")
                    profiles[pid] = {}
                    if "prompt" in p:
                        profiles[pid]["prompt"] = (p.get("prompt") or "").strip()
                    if "topics" in p:
                        profiles[pid]["topics"] = [str(t).strip() for t in (p.get("topics") or []) if str(t).strip()]
                cooldown_s = int(data.get("cooldown_s", AUTO.cooldown_s))
                if cooldown_s < 0:
                    raise ValueError("cooldown_s must be >= 0")
                engine = data.get("engine", AUTO.engine)
                if engine not in ENGINES:
                    raise ValueError(f"engine must be one of {ENGINES}")
                rotation = data.get("rotation")
                if rotation is not None:
                    if not isinstance(rotation, list) or any(r not in AUTO.profiles for r in rotation):
                        raise ValueError(f"rotation must be a list of {sorted(AUTO.profiles)}")
                AUTO.save_config(active_profile, profiles, cooldown_s, engine=engine, rotation=rotation)
                return self._json({"ok": True})
            if path == "/api/caffeinate/toggle":
                data = json.loads(self._body() or b"{}")
                set_caffeinate(bool(data.get("enabled")))
                return self._json({"ok": True, "enabled": bool(data.get("enabled"))})
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
                    set_caffeinate(False)
                    SERVER[0].shutdown()
                threading.Thread(target=stop, daemon=True).start()
                return
            if path == "/api/reveal":
                data = json.loads(self._body() or b"{}")
                name = safe_name(os.path.basename(data.get("file") or ""))
                full = output_file(name)
                if not os.path.isfile(full):
                    return self._json({"error": "file not found"}, 404)
                reveal_in_file_manager(full)
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
                        cells = [c.strip() for c in line.split("|")[1:-1]]
                        if len(cells) == 11:  # pre-vpipe row, no engine column yet
                            cells.insert(10, "h3")
                        rows.append(cells)
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
                 "layers", "memory", "time", "engine", "notes"]
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
CAFFEINATE_PROC = None  # subprocess.Popen while the "keep awake" toggle is on, else None


def set_caffeinate(enabled):
    """Start/stop a caffeinate process tied to this server's own pid (-w),
    so it can never outlive the server even if this doesn't get called on
    the way out. Defaults off on every server start — same "don't silently
    resume a side effect the user didn't just ask for" reasoning as AutoLoop
    always starting stopped."""
    global CAFFEINATE_PROC
    if enabled and not IS_MAC:
        return  # keep-awake uses macOS `caffeinate`; the toggle is hidden elsewhere
    if enabled:
        if CAFFEINATE_PROC is None or CAFFEINATE_PROC.poll() is not None:
            CAFFEINATE_PROC = subprocess.Popen(
                ["caffeinate", "-dimsu", "-w", str(os.getpid())])
    else:
        if CAFFEINATE_PROC is not None and CAFFEINATE_PROC.poll() is None:
            CAFFEINATE_PROC.terminate()
        CAFFEINATE_PROC = None


def reveal_in_file_manager(path):
    """Show a file in the OS file manager (Finder / Linux file manager / Windows Explorer under WSL)."""
    if IS_MAC:
        subprocess.run(["open", "-R", path], check=False)
    elif shutil.which("explorer.exe"):  # WSL
        subprocess.run(["explorer.exe", "/select,", subprocess.run(
            ["wslpath", "-w", path], capture_output=True, text=True).stdout.strip()], check=False)
    elif shutil.which("xdg-open"):
        subprocess.run(["xdg-open", os.path.dirname(path)], check=False)


def open_browser(url):
    import webbrowser
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    os.makedirs(OUTPUTS, exist_ok=True)
    os.makedirs(FINALS, exist_ok=True)
    os.makedirs(INPUTS, exist_ok=True)
    print(f"h3 engine: {'available' if H3_AVAILABLE else 'not set up (Runpod engine only)'}")
    print(f"runpod engine: {'available' if runpod_engine.runpod_available() else 'not set up (add RUNPOD_API_KEY to .env)'}")
    print(f"vpipe engine: {'available (' + VPIPE_MODEL + ')' if VPIPE_AVAILABLE else 'not set up'}")
    url = f"http://127.0.0.1:{PORT}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as exc:
        if exc.errno == 48:
            print(f"H3 Studio is already running at {url} — opening it.")
            if "--no-open" not in sys.argv:
                open_browser(url)
            return
        raise
    SERVER[0] = server
    print(f"H3 Studio serving at {url}  (Ctrl-C to stop)")
    if "--no-open" not in sys.argv:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        RUNNER.shutdown()


if __name__ == "__main__":
    main()
