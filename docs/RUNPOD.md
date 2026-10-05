# Runpod engine: operating guide

MiniMax H3 video generation on a rented Runpod RTX 4090, driven from **H3 Studio** (this repo).
Strategy: **start → render for hours → terminate.** Nothing persists between sessions; each start pays a ~12–15 min setup.

Last updated: 2026-10-05.

---

## Quick start (normal path)

1. Start H3 Studio: `python3 gui/server.py` (macOS: double-click `studio`). New machine? See `SETUP.md`.
2. **GPU · Runpod** panel (under the header) → **Start GPU**. Wait for **READY** (~12–15 min; the Logs → Setup tab shows each step).
   - Or go straight to the **Auto** tab and press **Start** with engine "Runpod · ComfyUI": it starts the GPU itself and jobs wait for setup.
3. Render:
   - **Studio** tab → engine tab **Runpod · ComfyUI** → Text / First-Last / References / Sequence, as with h3/vpipe. Turbo toggle on = 6 steps.
   - **Auto** tab → engine Runpod, tick the profiles to rotate, rest 0 → **Start**.
4. Stop: **Auto → Stop** (it finishes the current episode first), then **Stop GPU** and confirm the panel says *billing stopped*.

Check the **balance** in the GPU panel before a long run. Top up at https://console.runpod.io/user/billing. Runpod stops pods when it hits zero.

---

## What "Start GPU" does

Code: `gui/runpod_engine.py` (`RunpodManager`). Plain Python, no AI agent involved. Every step is logged to the panel.

| Step | What | Time |
|---|---|---|
| creating | `runpodctl pod create` named `h3-studio-<hostname>`: RTX 4090, Secure Cloud, template `cw3nka7d08` (ComfyUI CUDA 12.8), 300GB container disk, no volume, ports 8188/22, `HF_TOKEN` env | ~10s |
| booting | wait for SSH (runpodctl's key) + the ComfyUI proxy | ~35s |
| updating | over SSH: `git checkout v0.38.2` + `pip install -r requirements.txt` with the image's torch pinned | ~2–3 min |
| downloading | `hf download Comfy-Org/MiniMax-H3` for the 8 files below (~70GB at ~140 MB/s) | ~10 min |
| starting | restart ComfyUI, verify version ≥ 0.31 (refuses READY otherwise) | ~30s |

The setup script is idempotent: on an already-set-up pod it skips through in ~15s.
On H3 Studio startup, a running pod named `h3-studio` or `h3-render` is **adopted** automatically (setup re-runs, pod reused).

### Models (Comfy-Org/MiniMax-H3, ~70GB of a 525GB repo)

| Folder | File | Used for |
|---|---|---|
| diffusion_models | `minimax_h3_fl2va_pruned_fp8_scaled` (21GB) | text + first/last mode |
| diffusion_models | `minimax_h3_ref2va_pruned_fp8_scaled` (21GB) | references mode |
| text_encoders | `qwen3vl_32b_minimax_h3_nvfp4_awq` (15.7GB) | all |
| vae | `minimax_h3_video_vae_fp16`, `minimax_h3_audio_vae_fp32` | all |
| loras | `fl2v_turbo_8step_v1.0` (text, used at 6 steps), `ref2v_turbo_4step_v0.1` (refs), `fl2v_turbo_4step_v1.0_768p` | Turbo |

fp8 (not the recommended int8_convrot) because the 4090 hosts run CUDA 12.8 drivers; int8_convrot wants cu130.
ComfyUI's **native** MiniMax H3 nodes are used; no custom node pack is needed.

---

## How a render works

`run_job()` in `runpod_engine.py`: upload refs/frames → build an API-format ComfyUI graph (mirrors Comfy-Org's `video_minimax_h3_{t2v,i2v,r2v}` templates) → POST `/prompt` → per-step progress over ComfyUI's websocket (falls back to polling) → download the MP4 to `outputs/`.

- Modes: **text** = FL2VA + `MiniMaxH3ImageToVideo` (no frames). **first/last** = same node with frames. **refs** = Ref2VA + `MiniMaxH3ReferenceToVideo` (`<Picture N>` in the prompt).
- Sampler `res_multistep`, scheduler `simple`. Turbo on = LoRA + 6 steps; off = 20 steps.
- Frames must be 17n+5 (124 = 5s, 192 = 8s at 24fps).
- Output: H.264 re-encoded at **CRF 18** (`VIDEO_CRF`). ComfyUI's default "auto" wrote ~0.75 Mbps and looked blocky.
- Each job's cost (render time × pod rate) is saved in history as `cost_usd`.

---

## Auto mode

- Each episode: Claude (`claude -p`, opus) writes a 3-clip script from the profile's prompt + skill → submitted as a sequence on Runpod → merged.
- **Pipelining:** while an episode renders, the next script is written in parallel, so the GPU never waits on Claude.
- **Rotation:** ticked profiles take turns, one episode each (currently Tagalog drama → English drama → Modern Divide → Clocked Out).
- **Topics** cycle per profile (each used once per round; progress in `auto_used_topics.json`). Topics may repeat; **scripts may not**: every prompt includes the last 150 opening lines from history as a don't-copy list.
- Failed script writing backs off (1, 2, 4 … 15 min).
- **Balance guard:** below $0.30, Auto stops and the pod is terminated cleanly.

### Profiles and skills (`.claude/skills/`)

| Profile | Skill |
|---|---|
| tagalog-drama | `filipino-ragebait-short-drama-writer` (v2, 2026-10-03; v1 archived in `.claude/skills-archive/`) |
| english-drama | `english-short-drama-writer` (vindication formula) |
| english-pov | `pov-social-media-short-writer` (2 clips, captioned) |
| modern-divide | `modern-divide-debate-writer` (two-sided debate) |
| clocked-out | `clocked-out-ragebait` (workplace ragebait) |

Formatting for all: `video-prompt-writing-guide`. Auto's prompt demands plain text clip blocks separated by `=====` (no code fences: they make the parser drop clips).

---

## Settings and where they live (`gui/`)

| File | What |
|---|---|
| `runpod_config.json` | GPU auto-off minutes (0 = never) |
| `auto_config.json` | profiles (prompt + topics), rotation, rest seconds, engine |
| `auto_used_topics.json` | topic rotation progress per profile |
| `runpod_sessions.jsonl` | one line per terminated pod: uptime + cost |
| `history.jsonl` | every render (episodes show as one card; clips are linked from it) |
| `outputs/final/` | **merged episodes only** (and captioned variants), ready to copy to Drive. Individual clips stay in `outputs/`. |
| `runpod_engine.py` constants | `COMFY_VERSION`, `MIN_COMFY`, model files, `VIDEO_CRF`, `LOW_BALANCE_STOP`, `RUNPOD_PARAMS` |

Credentials (per machine): `RUNPOD_API_KEY` in `.env` or runpodctl's `~/.runpod/config.toml`; runpodctl SSH key `~/.runpod/ssh/runpodctl-ssh-key`; Hugging Face token in `.env` (`HF_TOKEN`) or `~/.cache/huggingface/token`.
Never paste keys into the Claude chat (`!` commands are recorded in the transcript).

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Voices are noise or garbled, timing right | ComfyUI < 0.31 (the template ships 0.30.0, before the H3 audio fixes, PRs #15243/#15377/#15390). Start GPU refuses READY on old versions; manual fix below. |
| Video blocky in cuts or dark shots | Save not re-encoding. Check `VIDEO_CRF` and the `format.codec.*` keys in `build_graph`. |
| HTTP 403 "error code: 1010" from the proxy | Runpod's Cloudflare blocks Python's default User-Agent; requests must send their own (`USER_AGENT`). |
| GPU panel ERROR during setup | Logs → Setup shows the failing step. **Retry setup** reuses the pod. |
| Setup stuck on "updating" for many minutes | A dropped SSH connection (fixed 2026-10-05 with keepalives; it now errors within ~2 min). If it happens anyway: Retry setup. |
| Setup very slow; network check fails | Bad-bandwidth host (seen 2026-10-05: 0.38 and 2.2 MB/s from Hugging Face). Start GPU now measures HF speed right after boot and replaces the pod if it's under 30 MB/s (up to 3 tries, `MIN_DL_MBPS`). |
| `ERROR git fetch … failed` | The image's own v0.30.0 tag conflicts with upstream, so a plain `git fetch --tags` refuses. The script now fetches only `refs/tags/v0.38.2` with `--force` (fixed 2026-10-05). |
| Auto making no episodes, log shows `claude-failed … session limit` | Claude usage limit. Auto backs off and resumes after the reset. Stop GPU if it'll be long. |
| Auto stopped by itself | Balance guard (< $0.30). Top up, then Start GPU + Start Auto. |
| Pod in the Runpod console that H3 Studio doesn't show | Only `h3-studio`/`h3-render` are adopted. Stop others in the console. |
| Restarting H3 Studio during Auto | **Auto → Stop first**, wait for the episode to finish, then restart. Otherwise the in-flight render is lost. (Auto starts stopped after a restart; press Start.) |
| Extra person in frame, or speaker swaps | Prompt-level: "exactly two people", identity + speaker locks, visibly different characters, location refs with no people in them. |

### Manual ComfyUI update (if ever needed)

```bash
ssh -i ~/.runpod/ssh/runpodctl-ssh-key root@<ip> -p <port>     # runpodctl ssh info <pod-id>
cd /workspace/runpod-slim/ComfyUI && git fetch --tags -q origin && git checkout -q v0.38.2
. .venv-cu128/bin/activate
grep -E "^(torch|torchvision|torchaudio)==" /opt/comfyui-runtime-constraints.txt > /tmp/torch-pin.txt
python -m pip install --no-cache-dir -r requirements.txt -c /tmp/torch-pin.txt
pkill -f "python main.py"     # start.sh falls through to `sleep infinity`; the container stays up
setsid nohup python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header > /workspace/comfyui.log 2>&1 < /dev/null &
```

---

## Manual fallback (without H3 Studio)

Scripts in `tools/runpod-manual/`:

```bash
POD=$(./create-pod.sh)                 # create (billing starts)
./wait-ready.sh "$POD"                 # wait for ComfyUI
./setup-models.sh "$POD"               # download weights (ComfyUI update: see above)
./render.py --pod "$POD" --mode text --width 576 --height 1024 --seconds 8 --turbo --prompt "..."
./render_script.sh "$POD" series/<name>   # all clips of a script.txt + concat (no chaining)
./terminate.sh "$POD"                  # delete + confirm
```

---

## Decisions (don't re-litigate without new info)

- **RTX 4090, Secure Cloud** ($0.74/hr + ~$0.04/hr disk). A Community Cloud test ($0.34/hr) is an open item.
- **Terminate, never stop**; one 300GB container disk, no network volume (no datacenter lock-in).
- **Turbo at 6 steps** is the default: the same-seed A/B with 20 steps had no noticeable difference, at less than half the time.
- **runpodctl + API key**, not MCP OAuth (runpodctl needs its own key).
- **Reference mode with in-clip camera cuts** (`[Shot N] At 00:04.000, cut to …`) works, but the user rated it "decent; the previous approach is still better" (Ref2V Turbo LoRA is v0.1; low bitrate was also a factor, now fixed).

---

## Benchmarks (RTX 4090, ComfyUI 0.38.2, fp8)

| Job | Time |
|---|---|
| 576×1024, 8s, Turbo 6 (text) | ~2m40s (158–177s) |
| 576×1024, 8s, 20 steps | 6m46s |
| 576×1024, 8s, refs ×3, Turbo 6, 3–4 camera cuts | ~3m10s |
| 3-clip episode | ~8–9 min; ~7 episodes/hour pipelined |

Denoise ≈ 18s/step at 576×1024×192. Mac baseline for the same clip: vpipe Turbo 6 ≈ 13 min, h3 20 steps ≈ 24 min.
Cost ≈ $0.035–0.04 per clip, ~$0.11 per episode. Live log: `benchmarks.md` (engine `runpod`).

---

