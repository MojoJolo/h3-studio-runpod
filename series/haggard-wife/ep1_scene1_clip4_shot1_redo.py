"""Regenerate ONLY Shot 1 of Scene 1 clip 4 (seed 100504), which had a phantom
extra hand/arm at the bottom-left frame edge. Shot 2 (Marco's close-up) was
clean and will be reused by trimming the original file instead of
regenerating the whole 8s clip.

After this job completes, concat: [this new Shot-1-only clip] + [original
seed100504 file trimmed from 4.0s onward] -> replacement clip 4.
"""
import json
import urllib.request

SUBJECT_DEFS = """subject_definitions:
<Subject 1> is TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes. In this scene she wears a simple worn cotton house dress, standing in a modest bedroom at night.
<Subject 2> is MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, sharp jawline, wearing a plain white ribbed crew-neck undershirt with short fitted sleeves and grey pajama pants, standing in the same bedroom.
<Picture 3> is the bedroom set: plain cream walls, wall-mounted split-type AC unit, sheer white curtains, wooden dresser with mirror and warm bedside lamp, bed with floral-pattern sheets. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Only her clothing and expression change per shot.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Only his clothing and expression change per shot.
<Picture 3> is used only for the room's walls, furniture and lighting layout — do not add any character or person from this picture; only Subject 1 and Subject 2 are ever visible. Exactly two people are visible in this shot: Teresa and Marco. No third person, hand, or limb of any kind."""

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by Subject 1 (S1) and Subject 2 (S2). Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT replace "mo" with "ko" or "ko" with "mo." Do NOT alter verb aspect. Do NOT paraphrase, normalize, or rewrite the dialogue."""

SHOT_1 = '[Shot 1] Medium two-shot, fixed camera, only Teresa and Marco visible, both fully in frame, no other hand, arm or person anywhere in the shot. Teresa\'s jaw tightens, disbelief turning to anger. TERESA (S1), sharp, incredulous, speaks the VERY FIRST LINE: <d>[Tagalog] So ako ang mali dito?</d>'

PROMPT = f"""{SUBJECT_DEFS}

summary:
[reference generation] Teresa's hurt turns to anger; she confronts Marco directly.

{RETENTION}

detailed_description:
{AUDIO_RULES}

{SHOT_1}

overall_soundscape:
Quiet bedroom at night, a faint electric fan hum. Only TERESA speaks in this clip.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 90, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 100510, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "marco-ref.jpeg", "bedroom-ref.jpeg"]

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
