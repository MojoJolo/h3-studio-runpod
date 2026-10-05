"""Redo of clip 1 (the hook) for the Isabel hotel episode.

Three fixes over seed 510101:
  1. The original generated a physical nameplate on the desk reading
     "ISABEL" — in-world signage, which slipped past the anti-caption rule
     because that rule targets subtitle/overlay text, not props. Worse, it
     labelled the RECEPTIONIST's desk with the protagonist's name. Now
     explicitly forbids nameplates, desk signs, badges with legible text,
     and any other readable text in the physical scene.
  2. Receptionist is now behind the counter with Isabel on the guest side,
     matching clip 2's staging (the original had both standing in the open,
     which was the inconsistent one).
  3. Tighter framing — the original was wide with an empty marble counter
     eating the bottom third and the characters small in frame, weak for a
     hook that has to land in two seconds.
"""
import json
import urllib.request

ISABEL = ("ISABEL, using <Picture 1> for her identity: a plain, completely unremarkable Filipina woman in her "
          "early 40s, no makeup, dark hair simply tied back, wearing a simple LIGHT BEIGE short-sleeve blouse — a "
          "warm sand/tan colour, definitely NOT white, NOT grey, NOT charcoal, NOT black, NOT navy — with dark navy "
          "slacks, holding a modest handbag. She looks ordinary, not poor.")

RECEPTIONIST = ("the HOTEL RECEPTIONIST, using <Picture 2> for her identity: a Filipina woman in her mid-20s, "
                "sleek dark hair pulled back into a tight bun, polished makeup, wearing a crisp dark navy hotel "
                "uniform blazer with a small gold name tag.")

NO_TEXT = ("Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere "
           "in the frame. Additionally, do NOT render any readable text inside the scene itself — no desk "
           "nameplates, no name signs on the counter, no placards, no printed signage, no legible lettering on "
           "badges or documents. The reception counter surface is clear and bare apart from a computer monitor.")

PROMPT = f"""subject_definitions:
<Subject 1> is {ISABEL}
<Subject 2> is {RECEPTIONIST}
<Picture 3> is the hotel lobby: polished marble floors, a long reception desk with brass accents and a marble counter, warm ambient lighting, a tall floral arrangement, high ceilings, elegant seating visible in the background. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Already mid-confrontation at the reception desk, the receptionist publicly tells Isabel she does not belong in this hotel, loud enough that other guests turn to look. Isabel stays quietly polite.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Her blouse MUST be light beige / warm sand-tan, exactly as in <Picture 1>, and must never render as white, grey, charcoal, black or navy.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. Exactly two people are visible in every shot of this clip, and no one else. Do not duplicate, clone, or generate a second version of either subject. No third person, no extra hand, arm, or limb of any kind anywhere in frame. Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind them, never near the two subjects and never interacting. No visual artifacts, streaks, lines, or chromatic fringing anywhere in frame — clean photographic image quality throughout. Each character's garment keeps its own exact colour for the entire clip and never drifts toward another character's colour.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
CRITICAL VISUAL RULE: {NO_TEXT}

[Shot 1] From the very first frame, the camera is already inside the hotel lobby at the reception desk — no other location appears at any point in this clip. TIGHT medium two-shot, fixed camera, framed close so both women fill most of the frame from the waist up, with only a little of the marble counter visible along the bottom edge. Isabel is wearing her light beige sand-coloured blouse, clearly lighter and warmer than the receptionist's dark navy uniform. The RECEPTIONIST stands BEHIND the reception counter on the staff side; ISABEL stands in front of it on the guest side, facing her across the counter. Both are ALREADY in position, the confrontation already in progress — nobody walks into frame. The receptionist looks Isabel slowly up and down, not hiding her contempt, and raises her voice slightly so it carries across the lobby. RECEPTIONIST (S2), openly disdainful, speaks the VERY FIRST LINE: <d>[Tagalog] Ma'am, sabi ko na po sa inyo — hindi po ito lugar para sa katulad niyo.</d> Isabel does not flinch or raise her voice. ISABEL (S1), quiet, still polite, replies: <d>[Tagalog] May reservation po ako.</d>

overall_soundscape:
Quiet upscale hotel lobby ambience, soft footsteps on marble, distant murmured conversation, a faint lobby piano far in the background. Only the RECEPTIONIST and ISABEL speak.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 192, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 510122, "ssd_streaming": True,
}
REFS = ["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": PROMPT, "mode": "refs", "engine": "h3", "params": PARAMS, "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
