#!/usr/bin/env bash
# Render every clip of an H3 Studio script.txt on the pod (text mode, Turbo 6, 576x1024), then concat.
# Usage: ./render_script.sh <pod-id> <series-dir> [seed]
set -euo pipefail
POD=$1; DIR=$2; SEED=${3:-$RANDOM}
OUT="$DIR/runpod"; mkdir -p "$OUT"
python3 - "$DIR/script.txt" "$OUT" <<'PY'
import re,sys
t=open(sys.argv[1]).read()
for i,b in enumerate([x.strip() for x in re.split(r"\n\s*[-=]{3,}\s*\n",t) if x.strip()],1):
    m=re.match(r"^(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|f|frames)?\s*\|\s*([\s\S]*)$",b,re.I)
    open(f"{sys.argv[2]}/clip{i}.prompt","w").write(m.group(3) if m else b)
    open(f"{sys.argv[2]}/clip{i}.secs","w").write(m.group(1) if m else "8")
PY
for p in "$OUT"/clip*.prompt; do
  n=$(basename "$p" .prompt)
  ./render.py --pod "$POD" --mode text --width 576 --height 1024 --seconds "$(cat "$OUT/$n.secs")" \
    --seed "$SEED" --turbo --steps 6 --label "$(basename "$DIR") $n" --out "$OUT/$n" --prompt "$(cat "$p")" | grep -v "rendering…"
  mv "$OUT/$n"/*.mp4 "$OUT/$n.mp4" && rmdir "$OUT/$n"
done
ls "$OUT"/clip*.mp4 | sed "s/.*/file '&'/" > "$OUT/concat.txt"
ffmpeg -y -v error -f concat -safe 0 -i "$OUT/concat.txt" -c copy "$OUT/final.mp4"
echo "final: $OUT/final.mp4"
