# AGENTS.md — guide for AI coding agents (Claude Code, Codex, Grok, …) and humans

H3 Studio is a local web app for generating short-form AI drama videos with the **MiniMax H3** model.
It renders on a rented **Runpod RTX 4090** running ComfyUI (the "runpod" engine), and optionally on a
local Apple Silicon Mac (the original "h3" and "vpipe" engines). An "Auto" mode writes scripts with the
`claude` CLI and renders them unattended.

Start here, then read `docs/`:

- **`docs/HANDOVER.md` — the operating manual: full HTTP API, how Auto works, step-by-step playbooks, gotchas**
- `SETUP.md` — install on a new machine (macOS, Linux, Windows/WSL)
- `docs/RUNPOD.md` — how the Runpod engine works, operating it, troubleshooting
- `docs/DECISIONS-AND-LESSONS.md` — decisions already made and why, and mistakes not to repeat
- `docs/BENCHMARKS.md` — measured speed and cost
- `.claude/skills/*/SKILL.md` — the creative rules for each content brand (plain Markdown; any model can read them)

## Architecture (stdlib Python + one HTML file)

| File | Role |
|---|---|
| `gui/server.py` | HTTP server (127.0.0.1:7833), job queue (`JobRunner`), Auto mode (`AutoLoop`), history, merging, benchmarks |
| `gui/runpod_engine.py` | Runpod engine: `RunpodManager` (pod lifecycle, setup, cost, balance guard) and `run_job()` (ComfyUI API client) |
| `gui/index.html` | The whole UI (GPU panel, Studio, Auto, Image tabs). Served fresh on every page load |
| `gui/auto_config.json` | Auto profiles: prompt + topic list per brand, rotation, rest time, engine |
| `.claude/skills/` | One skill per brand + `video-prompt-writing-guide` (H3 prompt format) |
| `series/<name>/` | Hand-made episodes: `script.txt`, `submit.py`, build scripts |
| `tools/runpod-manual/` | Shell/Python fallback to drive a pod without H3 Studio |

Per-machine, git-ignored: `.env` (keys), `gui/history.jsonl` (render history), `gui/runpod_config.json`,
`gui/runpod_sessions.jsonl` (cost ledger), `gui/auto_used_topics.json`, `outputs/` (videos; merged episodes in
`outputs/final/`), `inputs/` (uploaded/reference images).

Run: `python3 gui/server.py` (or the `studio` launcher on macOS). Python 3.9+, Pillow, ffmpeg, runpodctl.

## Content brands (Auto profiles)

| Profile | Skill | One-line formula |
|---|---|---|
| `tagalog-drama` | `filipino-ragebait-short-drama-writer` | Absurd-but-plausible Filipino conflict; final line makes the antagonist worse; strict pronunciation locks |
| `english-drama` | `english-short-drama-writer` | Vindication: judged on sight → calm → demand that undoes the judger → flat status reveal |
| `modern-divide` | `modern-divide-debate-writer` | Two-sided debate; both sides defensible; unresolved hard cut |
| `clocked-out` | `clocked-out-ragebait` | Workplace entitlement; every justification makes it worse; shameless final line |
| `english-pov` | `pov-social-media-short-writer` | 2-clip POV social-media short, captioned |

Every episode: 3 clips × 8 s, 576×1024 (9:16), Turbo LoRA at 6 steps, exactly two visible characters.

## Rules for agents working on this repo

1. **Billing is real.** A Runpod pod costs ~$0.78/hr from creation to deletion. State the hourly price before
   creating anything billable. Never leave a pod running without saying so. Quote cost from the pod's actual
   `uptimeSeconds`, never estimated from elapsed chat time.
2. **Automate every manual fix, then test the cold path.** If you work around a problem by hand on a pod, put the
   exact fix into `runpod_engine.py` in the same step, and test it on a fresh pod (or say plainly it's untested).
3. **Watch billable setup.** Poll each setup step against its expected time (boot ~1 min incl. network check,
   ComfyUI update <1 min, model download ~1–10 min depending on host). Investigate at 2× expected.
4. **Don't restart the server mid-render.** Auto: stop Auto (it finishes the current episode), wait for an empty
   queue, then restart. A restart starts Auto stopped.
5. **Never commit secrets.** Keys live in `.env` / `~/.runpod/config.toml`; never paste them into chat logs.
6. **Pronunciation is user-verified.** The Tagalog skill's "USER-VERIFIED WORD LIST" overrides everything else.
   Ask the user before changing a stress mark.
7. **New topics must follow the brand's own skill rules** ("the mantra"); show drafts to the user before adding.
8. **Every multi-shot / multi-clip prompt needs a LOCATION LOCK** (fixed props and positions; only the camera moves;
   damage persists).
9. Topics may repeat; **scripts may not** (Auto passes recent opening lines as a don't-copy list).
10. Match the surrounding code style: stdlib only, comments explain *why*, no new dependencies without a reason.
