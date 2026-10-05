"""New Episode 2 opening clip, replacing both the old S2 clip 1 (give
instruction) and clip 2 (Tatay Lino's soft backstory setup) with one merged
clip: Teresa alone voices a raw, humiliating truth, then composes herself
and gives the investigate-Selina instruction. This becomes literally the
first thing viewers see in the interleaved episode cut.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman with fine delicate features and high cheekbones, now composed and elegant — hair loose and smooth instead of a tired ponytail, calm controlled posture, no longer haggard or tired-looking, wearing a tailored dark charcoal silk blouse"
STAFF_LOOK = "TATAY LINO, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing alone by the window in her private office.
<Subject 2> is {STAFF_LOOK}, standing a respectful distance away near the desk, having entered quietly moments earlier and waiting.
<Picture 3> is the office: large dark wood executive desk, tall bookshelf filled with books, deep green leather chair, warm brass desk lamp, heavy curtains, old-money decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Alone, Teresa voices a raw, humiliating truth about her marriage under her breath, then composes herself completely and gives Tatay Lino a decisive instruction to investigate Selina.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Teresa and Tatay Lino, and no one else.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame.

[Shot 1] Medium shot, fixed camera, Teresa standing alone by the window at a three-quarter angle, staring out at nothing in particular, composed exterior. TERESA (S1), flat, quiet, almost disbelieving of her own words, speaks the VERY FIRST LINE: <d>[Tagalog] Pinagpalit ako ng asawa ko sa sugar mommy niya.</d> A flicker of real hurt crosses her face for just a moment before she steadies it, her jaw tightening.

[Shot 2] At 00:04.000, cut to a wider medium two-shot, revealing Tatay Lino standing respectfully near the desk, having been quietly present the whole time. Teresa turns to face him, composure fully restored, businesslike. TERESA (S1), composed, quietly commanding, continues: <d>[Tagalog] Alamin mo kung saan talaga nanggagaling ang pera ni Selina. Gusto kong malaman lahat.</d> Tatay Lino gives a small, immediate bow of the head. TATAY LINO (S2), respectful, without hesitation, replies: <d>[Tagalog] Opo, Ma'am. Gagawin ko na po agad.</d>

overall_soundscape:
A quiet private office at night, a faint clock ticking, warm lamp light. Only TERESA and TATAY LINO speak.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 175, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 200301, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "staff-ref.jpeg", "office-ref.jpeg"]

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
