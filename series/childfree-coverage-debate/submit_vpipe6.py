"""Childfree Coverage debate (Jessica/Amy) — vpipe 6-step redo of the h3/20-step
original (seq_id 26). Same script.txt, reused as-is. User asked for this queued
ahead of the auto-generation pipeline for English vindication-formula scripts.
"""
import json
import re
import urllib.request

API = "http://127.0.0.1:7833/api/sequence"
SCRIPT = __file__.rsplit("/", 1)[0] + "/script.txt"

PARAMS = {"width": 576, "height": 1024, "frames": 192, "steps": 6, "seed": 811901,
          "reuse": 2, "layers": 50, "ssd_streaming": True}


def parse_sequence(text, default_frames):
    out = []
    for block in re.split(r"\n\s*[-=]{3,}\s*\n", text):
        block = block.strip()
        if not block:
            continue
        m = re.match(r"^(\d+(?:\.\d+)?)\s*(s|sec|secs|seconds|f|frames)?\s*\|\s*([\s\S]*)$",
                     block, re.I)
        if not m:
            out.append({"prompt": block, "frames": default_frames})
            continue
        val = float(m.group(1))
        unit = m.group(2) or ""
        frames = round(val) if unit.lower().startswith("f") else round(val * 24)
        prompt = m.group(3).strip()
        if prompt:
            out.append({"prompt": prompt, "frames": frames})
    return out


if __name__ == "__main__":
    items = parse_sequence(open(SCRIPT).read(), PARAMS["frames"])
    for i, it in enumerate(items, 1):
        assert (it["frames"] - 5) % 17 == 0, f"clip {i}: {it['frames']} would be snapped by the server"
        lines = re.findall(r"<d>\[English\](.*?)</d>", it["prompt"], re.S)
        print(f"clip {i}: {it['frames']}f  {len(lines)} line(s)")

    body = {"items": items, "params": PARAMS, "refs": [], "engine": "vpipe"}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
