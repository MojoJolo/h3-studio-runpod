# Decisions and lessons

Things already decided (don't re-litigate without new information) and mistakes not to repeat.
Newest lessons are at the bottom of each section.

## Infrastructure decisions

- **RTX 4090, Secure Cloud.** Best cost per clip; 24 GB VRAM is enough for the fp8 models. Community Cloud
  (~$0.34/hr, less than half) is an untested option for Auto.
- **Terminate, never stop.** No persistent storage between sessions; one 300 GB container disk, no network volume
  (avoids datacenter lock-in). Each start pays a few minutes of setup.
- **ComfyUI ≥ 0.31 is mandatory.** The Runpod template ships 0.30.0, which predates the MiniMax H3 audio fixes
  (ComfyUI PRs #15243, #15377, #15390): voices come out as noise with the right rhythm. Setup pins v0.38.2.
- **fp8 models**, not the recommended int8_convrot: int8 needs CUDA 13; the 4090 hosts run CUDA 12.8 drivers.
- **Turbo LoRA at 6 steps** is the default: in a same-seed A/B against 20 steps without Turbo there was "no
  noticeable difference", at less than half the time.
- **Video re-encoded at CRF 18.** ComfyUI's SaveVideo "auto" wrote ~0.75 Mbps (blocky); CRF 18 gives ~2 Mbps.
- **Reference mode with in-clip camera cuts works**, but plain text-mode sequences were judged better for drama.
  Reference mode is great for multi-character / action pieces with consistent faces.
- **Auto writes scripts with the Claude CLI** (Opus). It's a single switch point (`AutoLoop._run_claude`) if another
  writer is wanted later.
- **Each install is independent.** Per-machine keys, pod, history and videos; nothing is synced.

## Content decisions

- Every episode: 3 clips × 8 s, 576×1024, exactly two visible characters (except deliberate action pieces).
- **Topics may repeat; scripts may not.** Topic lists cycle; Auto sends the last 150 opening lines as a don't-copy list.
- New topics are generated **from each brand's own skill rules** and reviewed by the user before being added, so they
  don't drift from the formula.
- Auto rotates profiles one episode each (Tagalog drama → English drama → Modern Divide → Clocked Out).
- Merged episodes go to `outputs/final/`; individual clips stay in `outputs/` and are linked from the episode card.

## Prompting lessons (H3)

- **Characters already in position at frame one.** A walking-in opening cost measurable retention on a posted video.
- **Make the two characters obviously different** (gender, skin tone, age); similar-looking pairs get speaker swaps.
- **Speaker lock every clip**; only the speaker's lips move.
- **Say "exactly two people" and "no captions/subtitles/text" explicitly**, or H3 adds phantom extras and burned-in captions.
- **LOCATION LOCK in every clip and shot:** list fixed props and their positions, "only the camera moves", damage persists.
  Without it, a dining table vanished between clips.
- **Reference images:** shoot characters on a neutral background that won't leak; a dark studio backdrop leaked into
  one shot. Location plates must contain no people (people in a plate become phantom extras).
- **Tagalog pronunciation:** use the user-verified word list in the Tagalog skill. Notable: Nánay = NA-nay, báhay = BA-hay,
  béses = BE-ses, gágawin = GA-ga-win, A-te spoken slowly as two syllables (never "eight"), avoid "magkaanák" (use
  "mabuntís"), leave ulit / tanga / siyempre / ibig unmarked.
- Never chain reference-mode clips via last frame (artifacts compound); render each clip with the same fixed refs.

## Operating lessons (things that cost money)

- **Quote cost from the pod's real uptime**, never from how long a conversation felt.
- **A manual fix must go into the automation the same day, and the cold path must be tested.** A `git fetch --tags`
  failure was fixed by hand on one pod but not in the setup script, so the next fresh pod failed (plus a hung SSH
  went unnoticed for 15 minutes). Setup now fetches only the needed tag with `--force`, uses timeouts and SSH keepalives.
- **Host bandwidth varies wildly** (0.38 / 2.2 / 83 / 124 / 143 MB/s seen). Setup measures Hugging Face speed right
  after boot and replaces hosts under 30 MB/s.
- **Watch every billable setup step** against its expected time and act at 2×.
- **Auto must not run with the GPU off**: it would write unrenderable scripts in a fail-fast loop and burn Claude usage.
  Auto now stops itself when the GPU is off/error, and when the Runpod balance drops below $0.30.
- **Claude usage limits** stop Auto's script writing; Auto backs off (1→15 min). Long interactive sessions plus Auto on
  Opus drain a plan's limit fast.
- **Don't restart the server mid-render**; stop Auto, wait for an empty queue, restart, start Auto.
- When submitting several jobs from a script, give each a unique seed or wait a second: output filenames used to be
  second + seed (now include milliseconds).
