#!/usr/bin/env python3
"""Render one MiniMax H3 clip on the Runpod ComfyUI pod via its HTTP API.

Builds an API-format version of Comfy-Org's video_minimax_h3_r2v template
(swapped to the fp8/fp16 files we download), uploads reference images,
submits, waits, and downloads the MP4.

Usage:
  ./render.py --pod <pod-id> --prompt "..." [--ref img1.png --ref img2.png]
              [--seconds 5] [--turbo] [--mp 0.4] [--seed N] [--out clips/]
"""
import argparse, json, os, random, sys, time, urllib.request, uuid

def http(url, data=None, headers=None):
    # Runpod's Cloudflare proxy rejects Python's default User-Agent (error 1010)
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "h3-render/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def upload_image(base, path):
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + open(path, "rb").read() + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    r = json.loads(http(f"{base}/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return r["name"]

def frames_for(seconds, fps=24):
    # Same formula as the template's ComfyMathExpression: H3 wants 17n+5 frames
    f = max(5, round(seconds * fps))
    return f + (5 - f % 17) % 17

def build(prompt, refs, seconds, turbo, mp, seed, aspect, mode="ref", width=None, height=None, steps=None):
    # mode "ref":  Ref2VA model + MiniMaxH3ReferenceToVideo (Comfy-Org r2v template)
    # mode "text": FL2VA model + MiniMaxH3ImageToVideo with no frames (Comfy-Org t2v template; same base as vpipe)
    text = mode == "text"
    unet = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors" if text else "minimax_h3_ref2va_pruned_fp8_scaled.safetensors"
    lora = "minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors" if text else "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors"
    if steps is None:
        steps = (6 if text else 4) if turbo else 20
    size = {"width": width, "height": height} if width else {"width": ["res", 0], "height": ["res", 1]}
    g = {
        "unet":  {"class_type": "UNETLoader", "inputs": {"unet_name": unet, "weight_dtype": "default"}},
        "clip":  {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "vae":   {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "avae":  {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "res":   {"class_type": "ResolutionSelector", "inputs": {"aspect_ratio": aspect, "megapixels": mp, "multiple": 32}},
        "cond":  {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
                    "clip": ["clip", 0], "vae": ["vae", 0], "audio_vae": ["avae", 0], "prompt": prompt,
                    "length": frames_for(seconds), "ref_image_size": "match", **size}},
        "noise": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "samp":  {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "sched": {"class_type": "BasicScheduler", "inputs": {"model": ["unet", 0], "scheduler": "simple", "steps": steps, "denoise": 1}},
        "guide": {"class_type": "BasicGuider", "inputs": {"model": ["lora", 0] if turbo else ["unet", 0], "conditioning": ["cond", 0]}},
        "run":   {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["noise", 0], "guider": ["guide", 0], "sampler": ["samp", 0], "sigmas": ["sched", 0], "latent_image": ["cond", 1]}},
        "dec":   {"class_type": "VAEDecode", "inputs": {"samples": ["run", 0], "vae": ["vae", 0]}},
        "adec":  {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["run", 0], "vae": ["avae", 0]}},
        "video": {"class_type": "CreateVideo", "inputs": {"images": ["dec", 0], "audio": ["adec", 0], "fps": 24, "bit_depth": 8}},
        "save":  {"class_type": "SaveVideo", "inputs": {"video": ["video", 0], "filename_prefix": "video/H3", "format": "auto", "codec": "auto"}},
    }
    if turbo:
        g["lora"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["unet", 0], "lora_name": lora, "strength_model": 1}}
    if text:
        g["cond"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["clip", 0], "vae": ["vae", 0], "prompt": prompt, "length": frames_for(seconds), **size}}
        if width:
            del g["res"]
        return g
    if width:
        del g["res"]
    for i, name in enumerate(refs):
        g[f"ref{i}"] = {"class_type": "LoadImage", "inputs": {"image": name}}
        g["cond"]["inputs"][f"ref_images.ref_image_{i}"] = [f"ref{i}", 0]
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pod", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--ref", action="append", default=[], help="reference image (repeatable): <Picture 1>, <Picture 2>, ...")
    ap.add_argument("--seconds", type=float, default=5)
    ap.add_argument("--turbo", action="store_true", help="4-step Turbo LoRA instead of 20 steps")
    ap.add_argument("--mp", type=float, default=0.4, help="megapixels; only used with --width 0")
    ap.add_argument("--aspect", default="16:9 (Widescreen)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--mode", choices=["ref", "text"], default="ref")
    ap.add_argument("--width", type=int, default=576, help="exact width (default 576; 0 = use --mp/--aspect)")
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, help="override steps (default: 20, or Turbo 4 ref / 6 text)")
    ap.add_argument("--label", default="", help="tag for the benchmark log")
    ap.add_argument("--out", default="clips")
    a = ap.parse_args()

    base = f"https://{a.pod}-8188.proxy.runpod.net"
    seed = a.seed if a.seed is not None else random.randint(0, 2**48)
    refs = [upload_image(base, p) for p in a.ref]
    graph = build(a.prompt, refs, a.seconds, a.turbo, a.mp, seed, a.aspect, a.mode, a.width, a.height, a.steps)

    try:
        r = json.loads(http(f"{base}/prompt", json.dumps({"prompt": graph}).encode(), {"Content-Type": "application/json"}))
    except urllib.error.HTTPError as e:
        sys.exit(f"submit failed: {e.code} {e.read().decode()[:2000]}")
    pid = r["prompt_id"]
    print(f"submitted {pid} seed={seed} frames={frames_for(a.seconds)} turbo={a.turbo}", flush=True)

    t0 = time.time()
    while True:
        h = json.loads(http(f"{base}/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                sys.exit("render error: " + json.dumps(st.get("messages"))[:3000])
            if st.get("completed"):
                break
        print(f"  rendering… {int(time.time() - t0)}s", flush=True)
        time.sleep(10)
    elapsed = time.time() - t0

    os.makedirs(a.out, exist_ok=True)
    for node in h[pid]["outputs"].values():
        for item in node.get("images", []) + node.get("videos", []) + node.get("gifs", []):
            q = urllib.parse.urlencode({"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")})
            dest = os.path.join(a.out, item["filename"])
            open(dest, "wb").write(http(f"{base}/view?{q}"))
            print(f"saved {dest} ({elapsed:.0f}s render)")
    steps = graph["sched"]["inputs"]["steps"]
    size = f"{a.width}x{a.height}" if a.width else f"{a.mp}MP {a.aspect}"
    with open("benchmarks.md", "a") as f:
        f.write(f"| {time.strftime('%Y-%m-%d %H:%M')} | {a.label} | {a.mode} | {size} | {frames_for(a.seconds)} | {steps} | {a.turbo} | {seed} | {elapsed:.0f}s |\n")

if __name__ == "__main__":
    import urllib.parse, urllib.error
    main()
