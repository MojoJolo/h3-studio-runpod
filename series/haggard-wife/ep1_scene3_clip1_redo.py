"""Redo of Scene 3 clip 1 (seed 100601): a phantom duplicate of Tatay Lino
appeared from ~2s onward (a second man in an identical white barong,
standing behind him with a hand on his shoulder). Reinforcing the
no-third-person line more explicitly and rerolling the seed.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, still wearing the same simple worn cream cotton house dress with short sleeves she left in, carrying nothing"
STAFF_LOOK = "a composed household staff member, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing just outside a gate at dusk.
<Subject 2> is TATAY LINO, {STAFF_LOOK}, standing just inside the gate. There is no security guard, no watchman, no second household staff member, and no one else employed at this house anywhere in this clip. Tatay Lino is the sole staff member on the entire property.
<Picture 3> is the gate set: plain grey concrete perimeter wall, simple steel gate, a single warm porch light, dusk sky. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Teresa arrives on foot at a plain, modest-looking gate; the staff member waiting there greets her with immediate, genuine deference.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the gate/wall/lighting layout — do not add any character or person from this picture. EXACTLY TWO PEOPLE total appear anywhere in this clip, in every single frame: Teresa and Tatay Lino, and no one else. Do not duplicate, clone, or generate a second version of either subject. No third person, no security guard, no watchman, no bystander, no extra hand, arm, or limb of any kind anywhere in frame, at any timestamp.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.

[Shot 1] Tight close two-shot at the gate, both faces filling most of the frame, minimal background depth or empty space visible behind them, fixed camera. Only Teresa and Tatay Lino visible, no one else in frame at any point. Teresa on the street side, Tatay Lino just inside having opened the gate for her. He bows his head slightly, voice warm and relieved. TATAY LINO (S2), gentle, deeply respectful, speaks the VERY FIRST LINE: <d>[Tagalog] Salamat sa Diyos, nakauwi na po kayo.</d> Teresa gives a small, tired, grateful nod, stepping through the gate. TERESA (S1), quiet, replies: <d>[Tagalog] Salamat, Tatay Lino.</d>

overall_soundscape:
Quiet residential street at dusk, distant crickets starting, a soft breeze. Only TATAY LINO and TERESA speak.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 158, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 100620, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "staff-ref.jpeg", "gate-ref.jpeg"]

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
