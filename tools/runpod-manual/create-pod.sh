#!/usr/bin/env bash
# Step 1: create a fresh RTX 4090 ComfyUI pod. Billing starts immediately (~$0.78/hr incl. disk).
# Needs: runpodctl key in ~/.runpod/config.toml, HF_TOKEN in env (or ~/.cache/huggingface/token).
set -euo pipefail
RUNPODCTL=~/.local/bin/runpodctl
HF_TOKEN=${HF_TOKEN:-$(cat ~/.cache/huggingface/token)}
ENVJSON=$(HF_TOKEN="$HF_TOKEN" python3 -c 'import json,os;print(json.dumps({"HF_TOKEN":os.environ["HF_TOKEN"]}))')

"$RUNPODCTL" pod create --name h3-render \
  --template-id cw3nka7d08 \
  --gpu-id "NVIDIA GeForce RTX 4090" --gpu-count 1 --cloud-type SECURE \
  --container-disk-in-gb 300 --volume-in-gb 0 \
  --ports "8188/http,22/tcp" --ssh \
  --env "$ENVJSON" -o json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["id"])'
