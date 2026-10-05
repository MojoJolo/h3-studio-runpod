"""Short transitional clip for Scene 3, inserted between the porch/maid
welcome and the original phone-call cliffhanger. Teresa enters her room
alone, taking it in, then picks up her phone — a quiet beat that bridges
naturally into the cliffhanger clip which opens already mid-call.
No transformation, no new character, no dialogue needed. Short by design.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing the same simple worn cream cotton house dress with short sleeves"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, alone, just entering a quiet, well-kept but understated room.
<Picture 2> is the room: plain cream walls, simple wooden furniture, a large window with soft warm light, tasteful but modest decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Teresa enters her room alone, taking it in with a slow, searching look, then picks up her phone as it begins to ring — a quiet transitional beat before the call.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly one person is visible in every frame of this clip: Teresa alone. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. No dialogue in this clip at all — entirely silent visual direction, only ambient sound.

[Shot 1] From the very first frame, the camera is already inside the room. Teresa steps in slowly, her eyes moving across the space — the window, the furniture — taking it in with a quiet, searching look, still processing where she is. She pauses beside a small table where her phone sits, glances down at it as it begins to buzz and light up, and picks it up.

overall_soundscape:
Quiet room tone, a faint clock ticking somewhere, soft footsteps as she enters, a phone buzzing softly on the table.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 107, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 100690, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "sala-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": PROMPT, "mode": "refs", "engine": "h3", "params": PARAMS, "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
