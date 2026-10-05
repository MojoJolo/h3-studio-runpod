# Handover: operating H3 Studio (for any agent or person)

Everything needed to run, operate and maintain H3 Studio without prior context. Read `AGENTS.md` (rules) first;
this file is the operating manual. Related: `SETUP.md` (install), `docs/RUNPOD.md` (engine internals +
troubleshooting), `docs/DECISIONS-AND-LESSONS.md`, `docs/BENCHMARKS.md`.

---

## 1. The system in one page

```
 Browser UI (gui/index.html) ─┐
                              ├─► gui/server.py  (127.0.0.1:7833, stdlib HTTP + SSE)
 Agents / scripts (HTTP API) ─┘        │
                                       ├─ JobRunner: one queue, one job at a time ──► engine
                                       │     engines: "runpod" (cloud), "h3"/"vpipe" (local Mac, optional)
                                       ├─ AutoLoop: claude CLI writes script → submits a Sequence → waits → repeats
                                       └─ RunpodManager (gui/runpod_engine.py): owns the pod
                                             create → boot → network check → update ComfyUI → models → ready
                                             run_job(): upload images → ComfyUI /prompt → websocket progress → MP4
```

- **A job** = one clip (e.g. 8 s, 576×1024). **A sequence** = several clips, each chained from the previous clip's
  last frame (or sharing reference images), merged into one MP4 at the end (an "episode").
- **History** (`gui/history.jsonl`) has one line per finished job and one per merged episode. The UI shows episodes
  as one card with links to their clips.
- **Money**: a pod bills ~$0.78/hr from creation until deletion, rendering or idle. Clip ≈ $0.04, episode ≈ $0.11.

---

## 2. Quick health check

```bash
curl -s localhost:7833/api/gpu/state  | python3 -m json.tool | head -30   # GPU: state, pod, cost, balance
curl -s localhost:7833/api/auto/state | python3 -m json.tool | head -20   # Auto: running? phase? rotation
curl -s localhost:7833/api/state      | python3 -c 'import json,sys;q=json.load(sys.stdin)["queue"];print("current:",bool(q["current"]),"pending:",len(q["pending"]))'
runpodctl pod list                                                       # ground truth: what is billing
tail -50 gui/server.log                                                  # server output, AutoLoop errors
```

GPU states: `off` → `creating` → `booting` → `updating` → `downloading` → `starting` → `ready` ⇄ `busy`; also `stopping`, `error`.
Only `ready`/`busy` accept jobs.

---

## 3. HTTP API reference

Base URL `http://127.0.0.1:7833`. JSON in and out. Errors: HTTP 400 `{"error": "..."}` (bad input) or 500.
All POST bodies are JSON (`curl -X POST -d '{...}'`), except `/api/upload` (raw bytes).

### GPU (Runpod)

| Method + path | Body | Does |
|---|---|---|
| `GET /api/gpu/state` | | State, `pod_id`, `pod` (`cost_per_hr`, `uptime_s`, `spent`), `comfy_version`, `idle_minutes`, `dl_bytes`, `billing` (`today`, `week`, `month`, `balance`, `hours_left`, `sessions`, `render_clips`, `render_total`), last 200 `logs` |
| `POST /api/gpu/start` | `{}` | Create + set up a pod (or retry setup if `error` with a live pod). **Starts billing.** Returns immediately; poll state |
| `POST /api/gpu/stop` | `{}` | Terminate the pod (deletes everything on it); billing stops. Poll until `off` |
| `POST /api/gpu/config` | `{"idle_minutes": 20}` | Auto-terminate after N idle minutes (0 = never). Only works while the server runs |
| `GET /api/gpu/comfylog` | | `{"log": "..."}`, the last 200 lines of ComfyUI's log on the pod |

### Rendering

| Method + path | Body | Does |
|---|---|---|
| `POST /api/generate` | see below | Queue one clip. Returns `{"ok", "id", "outfile"}` |
| `POST /api/sequence` | see below | Queue a chained multi-clip episode. Returns `{"ok", "seq_id", "clips"}` |
| `POST /api/upload?name=ref.png` | raw image bytes | Store an image in `inputs/` (deduplicated by content). Returns `{"ok", "name"}`: use that `name` in `refs` / `first_frame` |
| `POST /api/cancel` | `{"id": 123}` | Remove a pending job, or cancel the running one |
| `GET /api/state` | | `queue` (`current`, `pending`), recent `history`, engine availability (`h3_available`, `vpipe_available`, `runpod_available`), `gpu` |
| `GET /api/events` | | Server-Sent Events stream; see §3.1 |

`/api/generate` body:

```json
{
  "prompt": "integrated_multimodal_description: ...",
  "mode": "text",                    // "text" | "firstlast" | "refs"
  "engine": "runpod",
  "params": {"width": 576, "height": 1024, "frames": 192, "steps": 6, "turbo": true,
             "seed": 12345, "reuse": 2, "layers": 50},
  "refs": ["mama-ref.jpeg", "jen-ref.jpeg"],   // mode "refs": names returned by /api/upload (or files in inputs/)
  "first_frame": null, "last_frame": null       // mode "firstlast"
}
```

- `frames` must be 17n+5 (124 = 5 s, 192 = 8 s); other values are snapped. Width/height: multiples of 32.
- `reuse`/`layers` are h3-only but must be present and valid (2 / 50 are fine).
- Turbo on → use `steps: 6`. Turbo off → `steps: 20`.
- In refs mode, address images in the prompt as `<Picture 1>`, `<Picture 2>`… in `refs` order.
- **Submitting several jobs from a script?** Use a different `seed` per job (filenames include seed + timestamp).

`/api/sequence` body: `{"items": [{"prompt": "...", "frames": 192}, ...], "params": {...same...}, "refs": [], "engine": "runpod"}`
(2–20 clips). Without `refs`, clip 2+ is conditioned on the previous clip's last frame. With `refs`, every clip gets the
refs, and the last frame is added as one more ref. The merged MP4 lands in `outputs/final/`.

### Auto

| Method + path | Body | Does |
|---|---|---|
| `GET /api/auto/state` | | `running`, `phase` (`writing`/`generating`/`captioning`/null), `prefetch` (next script: `writing`/`ready`/`failed`), `current_profile`, `current_topic`, `last_status`, `last_script`, `cycle_count`, `config` |
| `POST /api/auto/start` | `{}` | Start Auto. Refuses if the `claude` CLI is missing or a profile has no prompt. On the runpod engine it also starts the GPU if it's off |
| `POST /api/auto/stop` | `{}` | Stop after the current episode finishes (the episode still completes) |
| `POST /api/auto/config` | see §4.4 | Update settings. **Only the profiles and fields you send change** |

### History, files, server

| Method + path | Body | Does |
|---|---|---|
| `GET /api/history?limit=50&offset=0&source=auto&kind=video` | | `{"entries", "total"}`, newest first; episodes include `clip_entries` |
| `POST /api/delete` | `{"ts": [ts, ...]}` or `{"all": true}` | Remove history entries (by `ts`) and trash their files |
| `GET /videos/<file>` · `GET /inputs/<file>` | | Serve an output video/image or an input image |
| `GET /api/bench` · `GET /benchmarks` | | Timing data (JSON) / sortable table (HTML) |
| `POST /api/shutdown` | `{"force": true}` | Stop the server (`force` cancels a running local job). **Doesn't stop the pod** |
| `POST /api/image` | `{"prompt", "width", "height", "steps", "seed", "refs"}` | Still image with the local Krea 2 / FLUX.2 klein models (macOS + vpipe only) |

### 3.1 Live events (`GET /api/events`)

Each line is `data: {json}`. Types: `queue` (current + pending), `progress` (`job`, `phase`, `done`, `total`,
`elapsed`: denoise steps arrive as `phase: "denoise"`), `done` (`entry`: the history entry), `gpu` (GPU state),
`gpu-log` (one setup log line), `seq-error`.

---

## 4. Auto mode, fully explained

### 4.1 What one cycle does
1. **Pick the profile:** the next one in `rotation` (round robin), or `active_profile` if rotation is empty.
2. **Pick a topic** from that profile's `topics`: a random one not used yet this round (progress persists in
   `gui/auto_used_topics.json`; when all are used, a new round starts). No topics → Claude invents a scenario.
3. **Write the script:** runs, from the repo root,
   `claude -p "<profile prompt>\n\n<topic instruction>\n\n<don't-copy list>" --output-format json --permission-mode dontAsk --model opus`.
   The profile prompt names the brand's skill; the Claude CLI loads it from `.claude/skills/`. The don't-copy list is
   the opening lines of the last 150 clip-1s in history ("topics may repeat; scripts may not").
4. **Parse:** the output must be plain text blocks `8 | <prompt>` separated by lines of `=====` (≥ 2 clips). Code fences
   and markdown headers are tolerated and stripped.
5. **Submit** as a Sequence on the configured engine with the engine's defaults (runpod: 576×1024, Turbo 6 steps,
   random seed). Output files are prefixed with the profile id (e.g. `tagalog-drama-seq-…mp4` in `outputs/final/`).
6. **Pipelining:** right after submitting, it starts writing the *next* script in the background, so the GPU never waits.
7. **Wait** for the episode to merge; for profiles with `caption: true` (english-pov), burn a caption (a second Claude call).
8. **Rest** `cooldown_s` seconds (0 recommended on Runpod), then repeat.

### 4.2 Safety behavior
- Script-writing failures (`claude-failed`, e.g. a usage limit, or `parse-failed`) back off 1 → 2 → 4 … 15 minutes.
- Auto **stops itself** if the GPU is `off`/`error`/`stopping`, or the Runpod balance is below $0.30 (the pod is also terminated).
- A server restart always comes back with Auto **stopped**.
- `last_status` / `server.log` lines starting `AutoLoop` explain failures.

### 4.3 Profiles (stored in `gui/auto_config.json`)

```json
{
  "active_profile": "modern-divide",
  "engine": "runpod",
  "cooldown_s": 0,
  "rotation": ["tagalog-drama", "english-drama", "modern-divide", "clocked-out"],
  "profiles": {
    "tagalog-drama": {"label": "...", "caption": false, "prompt": "Write a Filipino ... skill's rules ...", "topics": ["...", "..."]},
    "...": {}
  }
}
```

Profile ids are fixed in `AutoLoop.DEFAULT_PROFILES` (`server.py`): `tagalog-drama`, `english-drama`, `english-pov`,
`modern-divide`, `clocked-out`. Adding a brand = add an id there + an `<option>` and the id in `AUTO_PROFILE_IDS` in
`index.html` + a skill in `.claude/skills/<name>/SKILL.md` + a prompt and topics via the API.

A profile prompt follows a fixed pattern: "Write a <brand> script, 3 clips × 8 s, following the <skill-name> skill's
rules … format each clip using the video-prompt-writing-guide skill … Output ONLY the 3 clip blocks, plain text, no
code fences, separated by `=====`, each starting `8 | integrated_multimodal_description:` …". Copy an existing one.

### 4.4 Changing Auto settings via the API

```bash
# rotate only two brands, no rest
curl -X POST localhost:7833/api/auto/config -d '{"rotation": ["modern-divide","clocked-out"], "cooldown_s": 0}'

# replace one profile's topics (other profiles untouched)
curl -X POST localhost:7833/api/auto/config -d '{"profiles": {"clocked-out": {"topics": ["...", "..."]}}}'

# switch engine / single profile
curl -X POST localhost:7833/api/auto/config -d '{"engine": "runpod", "rotation": [], "active_profile": "english-drama"}'
```

Fields: `active_profile`, `engine` (`runpod`|`h3`|`vpipe`), `cooldown_s`, `rotation` (list; `[]` = single profile),
`profiles: {id: {prompt?, topics?}}`. To **append** topics: GET the state, extend the list, POST it back.
**Topic rules:** new topics must follow the brand skill's own formula (see `AGENTS.md` rule 7) and be shown to the
user before being added.

### 4.5 Using Auto without the Claude CLI
Auto's writer is Claude-only (`AutoLoop._run_claude`). On a machine without `claude`, Auto refuses to start. An agent
can do the same job by hand: read the brand's `SKILL.md`, write 3 clip prompts in the format above, and submit them
with `POST /api/sequence`. That's "manual Auto", which only runs while the agent runs.

---

## 5. Playbooks

**Start a session and run Auto**
1. `GET /api/gpu/state`. Check the `billing.balance` (warn the user if < ~$2).
2. Tell the user the price (~$0.78/hr), then `POST /api/auto/start` (it starts the GPU), or `POST /api/gpu/start` first.
3. Poll `/api/gpu/state` every ~10 s. Expect `ready` in ~3–5 min. **If any step exceeds 2× its normal time, investigate**
   (`logs`, `/api/gpu/comfylog`); don't wait silently.
4. Confirm the first job: `/api/state` shows a `runpod` job with `steps: 6`.

**End a session**
`POST /api/auto/stop` → poll until `/api/state` has no current/pending jobs → `POST /api/gpu/stop` → poll until `off`
→ `runpodctl pod list` must be `[]`.

**Restart the server without losing work** (e.g. after a code change)
Stop Auto → wait for an empty queue → `POST /api/shutdown` → start `python3 gui/server.py` → the GPU manager re-adopts
the running pod (~15 s; wait until it's not `off` before starting Auto, or you'll create a second pod) → `POST /api/auto/start`.

**Render a custom episode by hand**
Write 3 prompts following the brand skill (every clip needs the full character/identity/speaker/LOCATION LOCK blocks;
clips are generated independently) → `POST /api/sequence` with `"engine": "runpod"` → watch `/api/events` or poll
`/api/history?limit=1` → the merged file is in `outputs/final/`.

**Reference-mode piece (consistent faces, camera cuts)**
Make reference images (characters on a neutral background, a location plate with no people) → `POST /api/upload` each
→ `POST /api/generate` per clip with `"mode": "refs"`, the same `refs` list for every clip, a unique seed per clip
(don't chain refs-mode clips via last frame) → concatenate with ffmpeg into `outputs/final/`.

**The GPU is in `error`**
Read `logs` in `/api/gpu/state`. If a pod still exists, `POST /api/gpu/start` retries setup on the same pod. Known
failures and fixes: `docs/RUNPOD.md` → Troubleshooting.

---

## 6. Where everything lives

| Path | Content | In git? |
|---|---|---|
| `gui/server.py`, `gui/runpod_engine.py`, `gui/index.html` | The app | yes |
| `.claude/skills/` | Brand rules + H3 prompt format | yes |
| `gui/auto_config.json` | Auto profiles, topics, rotation | yes (edited on each machine) |
| `.env` | `RUNPOD_API_KEY`, `HF_TOKEN`, optional `H3_POD_NAME`, `H3_STUDIO_PORT`, `RUNPODCTL` | **no** |
| `gui/history.jsonl` | Every render | no |
| `gui/auto_used_topics.json` | Topic rotation progress | no |
| `gui/runpod_config.json`, `gui/runpod_sessions.jsonl` | Auto-off minutes; per-pod cost ledger | no |
| `outputs/final/` · `outputs/` | Merged episodes · clips | no |
| `inputs/` | Uploaded / reference images | no |
| `benchmarks.md` | Per-render timing | no |

Tunables in `gui/runpod_engine.py`: `GPU_ID`, `CLOUD_TYPE`, `DISK_GB`, `COMFY_VERSION`, `MIN_COMFY`, model filenames,
`RUNPOD_PARAMS` (default size/steps), `VIDEO_CRF`, `MIN_DL_MBPS` (network check), `LOW_BALANCE_STOP`, `POD_NAME`.

---

## 7. Gotchas (each cost real time or money once)

- **Pod names:** each machine adopts only `h3-studio-<hostname>` (plus the legacy `h3-studio`/`h3-render`). Two machines
  on one Runpod account must not share a pod name.
- Starting Auto while the GPU is `off` starts the GPU. Starting it right after a server restart (before the running pod
  is re-adopted) **creates a second pod**: wait until the GPU state isn't `off`.
- The Runpod proxy rejects Python's default User-Agent (HTTP 403, error 1010); the engine sends its own.
- Never edit `gui/history.jsonl` while the server runs (stop it first).
- The Claude CLI shares the plan's usage limit with interactive sessions; long sessions plus Auto on Opus drain it fast.
- Video quality depends on `VIDEO_CRF` (ComfyUI's default "auto" was ~0.75 Mbps and blocky).
- ComfyUI < 0.31 produces noise-like voices: setup refuses to report ready on old versions.
- `runpodctl pod list` is the ground truth for billing; check it at the end of every session.
