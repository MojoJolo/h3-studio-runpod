#!/usr/bin/env bash
# Benchmark vs the local Mac setup: 576x1024, 8s (192 frames), same prompt + seed.
# Usage: ./bench.sh <pod-id>
set -u
POD=$1; P="$(cat bench_prompt.txt)"
run() { ./render.py --pod "$POD" --mode text --width 576 --height 1024 --seconds 8 --seed 812901 --prompt "$P" --out clips/bench "$@"; }
run --turbo --steps 6 --label "vpipe-equiv turbo6 (cold)"
run --turbo --steps 6 --label "vpipe-equiv turbo6 (warm)"
run --steps 20        --label "h3-equiv 20 steps"
