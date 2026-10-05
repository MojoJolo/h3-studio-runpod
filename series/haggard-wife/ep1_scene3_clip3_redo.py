"""Redo of Scene 3 clip 3 (seed100603): the cut from outdoors-with-Tatay-Lino
straight to alone-indoors-on-a-phone-call was too abrupt, no bridge between
the two spaces. Fix: Shot 1 now opens with her walking in from a doorway
(alone) before the phone call begins, instead of starting static at the
window already mid-call. Same cliffhanger line and ending.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, now indoors, wearing the same simple worn cream cotton house dress with short sleeves"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, alone in a quiet, well-kept but understated room.
<Picture 2> is the room: plain cream walls, simple wooden furniture, a large window with soft warm light, tasteful but modest decor, a doorway connecting to the rest of the house. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Teresa walks in alone from the rest of the house, and a moment later takes a phone call; whoever it is addresses her with real weight, and she responds with a composed, quietly commanding line.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly one person is visible in every shot of this clip: Teresa alone. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
Teresa is on a phone call. The caller's voice is NOT rendered as audible dialogue — we only see Teresa's side: her listening, her expression shifting, and her own spoken lines. Do not write any dialogue for the caller.

[Shot 1] Medium shot, fixed camera near the window. Teresa walks in alone through the doorway from the rest of the house, crossing the room toward the window, her phone already ringing in her hand. She raises it to her ear as she reaches the window, her tired expression slowly shifting into something more composed and controlled as she listens.

[Shot 2] At 00:04.500, cut to a close-up on Teresa's face, phone still at her ear. She closes her eyes briefly, then opens them, calm and resolute. TERESA (S1), quiet but carrying unmistakable authority, speaks the VERY FIRST LINE: <d>[Tagalog] Hayaan mo silang maging masaya. Sa ngayon.</d> She lowers the phone slowly, her expression unreadable. Hard cut to black.

overall_soundscape:
Quiet room tone, a faint clock ticking somewhere, soft footsteps as she crosses the room, a soft breath as she lowers the phone. Only TERESA speaks.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 209, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 100640, "ssd_streaming": True,
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
