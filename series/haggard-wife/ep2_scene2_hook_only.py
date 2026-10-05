"""Minimal new hook clip for Episode 2's opening: just Teresa alone,
delivering one raw line, nothing else. Prepends the existing good
instruction clip (seed200111) rather than replacing/merging with it.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman with fine delicate features and high cheekbones, now composed and elegant — hair loose and smooth instead of a tired ponytail, calm controlled posture, no longer haggard or tired-looking, wearing a tailored dark charcoal silk blouse"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing alone by the window in her private office.
<Picture 2> is the office: large dark wood executive desk, tall bookshelf filled with books, deep green leather chair, warm brass desk lamp, heavy curtains, old-money decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Alone, Teresa voices a raw, humiliating truth about her marriage under her breath.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly one person is visible in every frame of this clip: Teresa alone. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY Teresa speaks, and only the single line written below in <d>...</d>. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak the <d> line EXACTLY as written. Do NOT paraphrase or rewrite it.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame.

[Shot 1] From the very first frame, the camera is already in the office. Teresa stands alone by the window at a three-quarter angle, staring out at nothing in particular, composed exterior. TERESA (S1), flat, quiet, almost disbelieving of her own words, speaks the VERY FIRST LINE: <d>[Tagalog] Pinagpalit ako ng asawa ko sa sugar mommy niya.</d> A flicker of real hurt crosses her face for just a moment before she steadies it, her jaw tightening. Hard cut.

overall_soundscape:
A quiet private office at night, a faint clock ticking, warm lamp light. Only TERESA speaks.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 107, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 200302, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "office-ref.jpeg"]

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
