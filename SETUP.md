# Setting up H3 Studio on a new machine

Works on **macOS, Linux, and Windows (via WSL2)**. Each install is independent: its own keys, its own Runpod pod,
its own history and videos. Nothing is shared between machines.

You need: a Runpod account with credit, and (optionally) a Hugging Face token and the Claude Code CLI for Auto mode.

## 1. Install the prerequisites

| | macOS | Linux (Debian/Ubuntu) | Windows |
|---|---|---|---|
| Python 3.9+ | preinstalled (`python3`) or `brew install python` | `sudo apt install python3 python3-pip` | Install **WSL2** (`wsl --install` in PowerShell), then follow the Linux column inside Ubuntu |
| Pillow | `pip3 install pillow` | `pip3 install pillow` | (inside WSL) |
| ffmpeg | `brew install ffmpeg` | `sudo apt install ffmpeg` | (inside WSL) |
| git, curl, ssh | preinstalled | `sudo apt install git curl openssh-client` | (inside WSL) |

**runpodctl** (Runpod's CLI): download the release for your OS from
https://github.com/runpod/runpodctl/releases, extract it, and put the `runpodctl` binary on your PATH
(e.g. `~/.local/bin`). `scripts/setup.sh` can do this for you.

## 2. Get the code

```bash
git clone https://github.com/MojoJolo/h3-studio-runpod.git
cd h3-studio-runpod
```

## 3. Add your keys

```bash
cp .env.example .env
# edit .env:
#   RUNPOD_API_KEY=...   (console.runpod.io -> Settings -> API Keys, "All" or read/write)
#   HF_TOKEN=...         (optional, huggingface.co/settings/tokens)
```

Then let runpodctl create and register its SSH key (used to set up the pod):

```bash
runpodctl doctor
```

Never paste keys into an AI chat; edit `.env` in a normal editor or terminal.

## 4. Check everything

```bash
bash scripts/setup.sh
```

It checks Python, Pillow, ffmpeg, runpodctl, your keys and the SSH key, offers to install runpodctl if missing,
and tells you exactly what's left.

## 5. Run

```bash
python3 gui/server.py          # opens http://127.0.0.1:7833
```

(On macOS you can also double-click `studio`.)

In the browser:

1. **GPU · Runpod** panel → **Start GPU** (≈3–5 min; ~$0.78/hr from this moment). It checks the host's bandwidth
   and replaces slow hosts automatically.
2. Render: **Studio** tab → engine **Runpod · ComfyUI** → Text / First-Last / References / Sequence.
3. When done: **Stop GPU** (deletes the pod; billing stops).

Merged episodes land in `outputs/final/` — copy that folder wherever you publish from.

## 6. Optional: Auto mode

Auto writes scripts with the **Claude Code CLI** (`claude`). Install it from https://claude.com/claude-code and log in
once (`claude` in a terminal). Without it, everything else in H3 Studio works; only Auto is unavailable.

**Auto** tab → engine **Runpod · ComfyUI** → tick the profiles to rotate → rest 0 → **Start** (starts the GPU too).
Stop with **Stop**, then **Stop GPU**.

## Notes

- The original local engines (`h3` on Apple Silicon, `vpipe`) are optional and hidden when not installed.
- Each machine names its pod `h3-studio-<hostname>` (override with `H3_POD_NAME`), so installs sharing a Runpod
  account never touch each other's pod.
- Keep an eye on your Runpod balance (shown in the GPU panel). Below $0.30, Auto stops and the pod is terminated.
- Full operating guide and troubleshooting: `docs/RUNPOD.md`.
