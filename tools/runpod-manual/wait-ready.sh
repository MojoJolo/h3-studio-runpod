#!/usr/bin/env bash
# Step 2: poll until ComfyUI answers. Usage: ./wait-ready.sh <pod-id>
set -uo pipefail
POD=$1
URL="https://$POD-8188.proxy.runpod.net"
until [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$URL/system_stats")" = 200 ]; do
  echo "$(date +%H:%M:%S) not ready yet"; sleep 10
done
echo "ComfyUI ready: $URL"
