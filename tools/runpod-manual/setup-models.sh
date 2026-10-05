#!/usr/bin/env bash
# Step 3: download MiniMax H3 weights onto the pod (~70GB, ~10 min at ~140MB/s).
# ComfyUI has native H3 nodes; no custom node pack needed.
# Usage: ./setup-models.sh <pod-id>     (runs the download on the pod in the background)
set -euo pipefail
POD=$1
SSH_CMD=$(~/.local/bin/runpodctl ssh info "$POD" | python3 -c 'import json,sys;print(json.load(sys.stdin)["ssh_command"])')
$SSH_CMD -o StrictHostKeyChecking=accept-new 'bash -s' <<'REMOTE'
# SSH shells don't inherit the container env; pull HF_TOKEN from PID 1
export HF_TOKEN=$(tr "\0" "\n" < /proc/1/environ | sed -n "s/^HF_TOKEN=//p")
cd /workspace/runpod-slim/ComfyUI/models
# Repo folder names match ComfyUI's models/ folders, so --local-dir . puts files in the right place
nohup hf download Comfy-Org/MiniMax-H3 \
  diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors \
  diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors \
  text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors \
  vae/minimax_h3_video_vae_fp16.safetensors \
  vae/minimax_h3_audio_vae_fp32.safetensors \
  loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors \
  loras/minimax_h3_fl2v_turbo_4step_v1.0_768p_comfyui_bf16.safetensors \
  loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors \
  --local-dir . > /workspace/download.log 2>&1 &
echo "download started, log: /workspace/download.log"
REMOTE
