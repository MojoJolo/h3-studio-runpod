"""Bea/Mama Lyn wedding-venue betrayal — Tagalog family drama, h3 engine, 20 steps.

User flagged a prior generation where the mother character rendered as looking like
the daughter (age/identity swap between the two Filipina characters). Added an
explicit "CRITICAL CHARACTER IDENTITY LOCK" block to each clip reinforcing that Mama
Lyn (55, grey-streaked hair, older features) must never be rendered as young or
resemble Bea (29), and vice versa — on top of strengthening Mama Lyn's physical
description itself (added grey hair, fine lines, more matronly build) so the age gap
is unambiguous even before the lock instruction. Also added the "EXACTLY TWO people,
no third person" visual rule from the Mara/Vince incident, since this is the same
risk profile (Tagalog family living-room drama).

Submitted as a SEQUENCE (/api/sequence): clip 1 renders from text and each later clip
is conditioned on the previous clip's last frame, matching the script's "Continue
immediately in the exact same living room..." continuity instructions.

parse_sequence() mirrors gui/index.html's parseSequence exactly, so this submits
byte-for-byte what pasting script.txt into the GUI would.
"""
import json
import re
import urllib.request

API = "http://127.0.0.1:7833/api/sequence"
SCRIPT = __file__.rsplit("/", 1)[0] + "/script.txt"

PARAMS = {"width": 576, "height": 1024, "frames": 192, "steps": 20, "seed": 811701,
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
        lines = re.findall(r"<d>\[Tagalog\](.*?)</d>", it["prompt"], re.S)
        print(f"clip {i}: {it['frames']}f  {len(lines)} line(s)")

    body = {"items": items, "params": PARAMS, "refs": [], "engine": "h3"}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
