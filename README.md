# H3 Studio (Runpod)

Generate short-form AI drama videos with the **MiniMax H3** video+audio model, rendered on a rented
**Runpod RTX 4090** and driven from a local web app. Write a script (or let **Auto** write one with Claude),
and get finished 24-second episodes with synchronized dialogue, sound and music.

- ~**2m45s per 8-second clip**, ~**8.5 min per 3-clip episode**, ~**$0.11 per episode**
- Runs on **macOS, Linux and Windows (WSL)**: Python stdlib + Pillow, ffmpeg and Runpod's CLI
- Everything stays on your machine except the GPU work; you start and stop the GPU yourself

## Quick start

```bash
git clone git@github.com:MojoJolo/h3-studio-runpod.git
cd h3-studio-runpod
cp .env.example .env          # add RUNPOD_API_KEY (and optionally HF_TOKEN)
bash scripts/setup.sh         # checks Python, Pillow, ffmpeg, runpodctl, keys; can install runpodctl
runpodctl doctor              # one time: creates + registers the SSH key used to set up pods
python3 gui/server.py         # opens http://127.0.0.1:7833
```

Full per-OS instructions: **[SETUP.md](SETUP.md)**.

## Requirements

- A **Runpod** account with credit and an API key (Settings → API Keys)
- **Python 3.9+** with **Pillow**, **ffmpeg**, **ssh**, **runpodctl**
- Optional: a **Hugging Face** token (faster model downloads)
- Optional: **Claude Code CLI** (`claude`), logged in, for Auto mode. Everything else works without it

## Using it

### 1. Start the GPU
**GPU · Runpod** panel → **Start GPU**. In ~3–5 minutes it creates an RTX 4090 pod, checks the host's bandwidth
(replacing slow hosts automatically), installs ComfyUI v0.38.2 and downloads the MiniMax H3 models (~65 GB).
The panel shows state, uptime, live cost, Runpod balance, spending history and setup/ComfyUI logs.

**Billing runs from Start to Stop (~$0.78/hr), rendering or idle.** Press **Stop GPU** when done. It deletes the pod.

### 2. Render by hand (Studio tab)
Pick the **Runpod · ComfyUI** engine, then:

| Mode | Use |
|---|---|
| **Text** | Prompt only |
| **First / Last** | Condition on a first and/or last frame |
| **References** | Up to several character/location images, addressed as `<Picture 1>`, `<Picture 2>`… Keeps faces and sets consistent; supports in-clip camera cuts |
| **Sequence** | Several clips (`8 \| prompt` blocks separated by `=====`), each chained from the previous clip's last frame, merged into one video |

Turbo (on by default) = 6 steps, about 2.5× faster than 20 steps with no audible difference in testing.

### 3. Or let Auto run (Auto tab)
Auto asks Claude to write a 3-clip script from a brand **profile** (prompt + topic list + skill), renders it, merges
it, and immediately starts the next one, writing the next script while the current one renders (~7 episodes/hour).

- **Rotate profiles**: tick the brands to alternate, one episode each
- **Topics** cycle per profile; **scripts never repeat** (recent opening lines are passed as a don't-copy list)
- Stops itself if the GPU goes off or the Runpod balance drops below $0.30

Engine **Runpod · ComfyUI**, rest **0**, **Start** (this starts the GPU too). **Stop** finishes the current episode.

### Brands included

| Profile | Skill (`.claude/skills/`) | Formula |
|---|---|---|
| Tagalog drama | `filipino-ragebait-short-drama-writer` | Absurd-but-plausible Filipino conflict; the final line makes the antagonist worse; user-verified pronunciation locks |
| English drama | `english-short-drama-writer` | Judged on sight → stays calm → the judger demands the thing that undoes them → flat status reveal |
| Modern Divide | `modern-divide-debate-writer` | Two-sided debate; both sides defensible; unresolved hard cut |
| Clocked Out | `clocked-out-ragebait` | Workplace entitlement; every justification makes it worse |
| English POV | `pov-social-media-short-writer` | 2-clip POV social-media short, captioned |

Skills are plain Markdown: edit them to change a brand's rules. Topics and prompts are edited in the Auto tab
(`gui/auto_config.json`).

## Where things go

| Path | What |
|---|---|
| `outputs/final/` | **Merged episodes**: copy this folder to wherever you publish from |
| `outputs/` | Individual clips (linked from each episode card in History) |
| `gui/history.jsonl` | Every render: prompt, settings, time, cost |
| `benchmarks.md` | Per-render timing log (also at `/benchmarks` in the app) |
| `series/` | Hand-made episodes: scripts and build/submit scripts |

## Docs

- **[SETUP.md](SETUP.md)**: install on macOS / Linux / Windows (WSL)
- **[docs/RUNPOD.md](docs/RUNPOD.md)**: how the Runpod engine works, settings, troubleshooting, manual fallback
- **[docs/BENCHMARKS.md](docs/BENCHMARKS.md)**: measured speed and cost
- **[docs/DECISIONS-AND-LESSONS.md](docs/DECISIONS-AND-LESSONS.md)**: what's been decided and why, and costly mistakes to avoid
- **[AGENTS.md](AGENTS.md)**: guide for AI coding agents (Claude Code, Codex, Grok…) working on this repo

## Optional: local Apple Silicon engines

The app grew out of a local GUI for [antirez/h3.c](https://github.com/antirez/h3.c) on Apple Silicon. The local
**h3** and **vpipe** engines still work if installed (`./h3` + `MiniMax-H3/` weights, or Vpipe Manager), and their
tabs appear automatically. Without them, H3 Studio runs with the Runpod engine only.

## Credits & license

MIT. Based on [H3 Studio](https://github.com/Neat2b/H3-Studio) by Neat2b (MIT); see `LICENSE`.
Model: [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3) via the ComfyUI repackage
([Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)), rendered with [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
on [Runpod](https://www.runpod.io). Respect the MiniMax H3 model license for anything you publish.
