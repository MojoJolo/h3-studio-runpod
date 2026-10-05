"""English-language version of the Isabel hotel episode, for the international channel.

Same story, staging, refs, framing and frame counts as the Tagalog cut — only the
dialogue language changes. Delivery is FILIPINO ENGLISH (educated Manila accent), which
matches the Filipino faces in the refs and is the mode already proven to work in the
Tagalog cut's clip 6.

THREE CLIPS ARE NOT REGENERATED — they are silent and reused verbatim from the Tagalog
cut: clip 4 (Isabel's angst beat) and both arrival bridges (2.5 manager, 6.5 executive).
So this is 9 generations, not 12.

Each clip is ported from its LATEST APPROVED version, not from the original submit.py:
    clip 1  <- submit_clip1_redo.py  (counter staging, tight framing, NO_TEXT)
    clip 5  <- submit_redos_2.py CALL
    clip 6  <- submit_mock_v5.py     (the Taglish fix; middle sentence now fully English)
    clip 10 <- submit_redos_2.py CLOSER
    others  <- submit.py

Lessons learned AFTER the originals were written are applied to every clip here, so the
English cut does not re-hit bugs already fixed once:
  - NO_TEXT: no in-world nameplates/signage (the desk once rendered "ISABEL")
  - Isabel's beige blouse triple-locked (it once rendered charcoal)
  - NO_FOOD: no restaurant props (a plated meal once appeared on the counter)
"""
import json
import time
import urllib.request

API = "http://127.0.0.1:7833/api/generate"

ISABEL = ("ISABEL, using <Picture 1> for her identity: a plain, completely unremarkable Filipina woman in her "
          "early 40s, no makeup, dark hair simply tied back, wearing a simple LIGHT BEIGE short-sleeve blouse — a "
          "warm sand/tan colour, definitely NOT white, NOT grey, NOT charcoal, NOT black, NOT navy — with dark navy "
          "slacks, holding a modest handbag. She looks ordinary, not poor.")

RECEPTIONIST = ("the HOTEL RECEPTIONIST, using <Picture 2> for her identity: a Filipina woman in her mid-20s, "
                "sleek dark hair pulled back into a tight bun, polished makeup, wearing a crisp dark navy hotel "
                "uniform blazer with a small gold name tag.")

MANAGER_P2 = ("the HOTEL MANAGER, using <Picture 2> for his identity: a Filipino man with slicked-back BLACK hair, "
              "clean-shaven, wearing a CHARCOAL GREY two-piece suit with a gold hotel lapel pin and a grey tie. "
              "He has NO waistcoat and NO grey in his hair.")

EXECUTIVE_P2 = ("the SENIOR EXECUTIVE, using <Picture 2> for his identity: an older, distinguished Filipino man in "
                "his 50s with clearly GREY-STREAKED hair, wearing a dark NAVY THREE-PIECE suit with a visible "
                "waistcoat and navy tie. He is visibly older and more senior than the hotel manager.")

LOBBY_P3 = ("<Picture 3> is the hotel lobby: polished marble floors, a long reception desk with brass accents and a "
            "marble counter, warm ambient lighting, a tall floral arrangement, high ceilings, elegant seating visible "
            "in the background. Composition/location anchor only — no characters appear in this picture.")

LOBBY_P2 = LOBBY_P3.replace("<Picture 3>", "<Picture 2>")

ISABEL_BEIGE = ("<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Her blouse MUST be "
                "light beige / warm sand-tan and must never render as white, grey, charcoal, black or navy.")

NO_TEXT = ("Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere "
           "in the frame. Additionally, do NOT render any readable text inside the scene itself — no desk "
           "nameplates, no name signs on the counter, no placards, no printed signage, no legible lettering on "
           "badges or documents.")

NO_FOOD = ("There is NO food, NO plates, NO dishes, NO trays, NO cutlery and NO dining table anywhere in this shot. "
           "This is a hotel reception lobby, not a restaurant. The marble surfaces are clear and bare.")

ACCENT = ("DELIVERY AND ACCENT: every speaker is FILIPINO and speaks FILIPINO ENGLISH — the natural English accent "
          "of an educated Manila professional. NOT American, NOT British, NOT neutral international English, and "
          "not a foreigner speaking. The accent is authentic and clearly intelligible, never exaggerated or comedic.")

AUDIO = f"""CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Do NOT swap pronouns, do NOT alter verb tense, do NOT paraphrase, normalize, or rewrite the dialogue. Contractions are written deliberately and must be spoken as written. Every word must be clearly and distinctly enunciated, unhurried, never mumbled, slurred or rushed.
{ACCENT}
CRITICAL VISUAL RULE: {NO_TEXT} {NO_FOOD}"""

AMBIENCE = ("Quiet upscale hotel lobby ambience, soft footsteps on marble, distant murmured conversation, a faint "
            "lobby piano far in the background.")

NO_ARTIFACTS = ("No visual artifacts, streaks, lines, or chromatic fringing anywhere in frame — clean photographic "
                "image quality throughout. Each character's garment keeps its own exact colour for the entire clip "
                "and never drifts toward another character's colour.")

TWO_PEOPLE = ("Exactly two people are visible in every shot of this clip, and no one else. Do not duplicate, clone, "
              "or generate a second version of either subject. No third person, no extra hand, arm, or limb of any "
              "kind anywhere in frame. Background hotel guests may appear only as distant, blurred, out-of-focus "
              f"figures far behind them, never near the two subjects and never interacting. {NO_ARTIFACTS}")

ONE_PERSON = ("Exactly one person is visible in every frame of this clip: Isabel alone, and no one else. Do not "
              "duplicate or clone her. No second person, hand, arm, or limb of any kind anywhere in frame. "
              "Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind her. "
              f"{NO_ARTIFACTS}")

NO_CHARS_FROM = "is used only for the lobby layout and lighting — do not add any character from this picture."


def build(subjects, summary, retention, shots, soundscape):
    return f"""subject_definitions:
{subjects}

summary:
[reference generation] {summary}

retention_analysis:
{retention}

detailed_description:
{AUDIO}

{shots}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


OPEN = ("[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears "
        "at any point in this clip. ")

clips = []

# ---- 1. Hook (ported from submit_clip1_redo.py) ----
clips.append(dict(
    n=1, frames=192, seed=520101,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "Already mid-confrontation at the reception desk, the receptionist publicly tells Isabel she does not belong "
        "in this hotel, loud enough that other guests turn to look. Isabel stays quietly polite.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as "
        f"specified above.\n<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "TIGHT medium two-shot, fixed camera, framed close so both women fill most of the frame from the "
        "waist up, with only a little of the marble counter visible along the bottom edge. Isabel is wearing her "
        "light beige sand-coloured blouse, clearly lighter and warmer than the receptionist's dark navy uniform. The "
        "RECEPTIONIST stands BEHIND the reception counter on the staff side; ISABEL stands in front of it on the "
        "guest side, facing her across the counter. Both are ALREADY in position, the confrontation already in "
        "progress — nobody walks into frame. The receptionist looks Isabel slowly up and down, not hiding her "
        "contempt, and raises her voice slightly so it carries across the lobby. RECEPTIONIST (S2), openly "
        "disdainful, speaks the VERY FIRST LINE: "
        "<d>[English] Ma'am, I've already told you. This isn't the kind of place for someone like you.</d> "
        "Isabel does not flinch or raise her voice. ISABEL (S1), quiet, still polite, replies: "
        "<d>[English] I have a reservation.</d>",
        f"{AMBIENCE} Only the RECEPTIONIST and ISABEL speak.",
    ),
))

# ---- 2. Refusal ----
clips.append(dict(
    n=2, frames=192, seed=520102,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "The receptionist refuses to even check properly, insisting there is no record and the hotel is full. Isabel "
        "asks her calmly to check again and is shut down.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as "
        f"specified above.\n<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, same positions at the reception desk. The receptionist barely glances "
        "at her computer screen before answering. RECEPTIONIST (S2), dismissive, speaks the VERY FIRST LINE: "
        "<d>[English] We don't have any record of that. And we're fully booked.</d> "
        "Isabel remains calm, her hands still folded on her handbag. ISABEL (S1), patient, asks: "
        "<d>[English] Could you check again, please?</d> "
        "The receptionist does not touch the keyboard at all. RECEPTIONIST (S2), clipped and final, replies: "
        "<d>[English] Ma'am. I know how to do my job.</d>",
        f"{AMBIENCE} Only the RECEPTIONIST and ISABEL speak.",
    ),
))

# ---- 3. Manager, contemptuous ----
clips.append(dict(
    n=3, frames=175, seed=520103,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The hotel manager steps in and, instead of helping, insults Isabel's clothes and threatens to call security.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is "
        f"black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, the manager already standing beside the reception desk facing Isabel, "
        "both fully in frame, the lobby visible around them. He looks her over with open disdain, one hand gesturing "
        "toward the entrance. MANAGER (S2), contemptuous, speaks the VERY FIRST LINE: "
        "<d>[English] Is there a problem here? Ma'am. Look at what you're wearing. Now leave, before I call "
        "security.</d> "
        "Isabel says nothing. She holds his gaze for a moment, absolutely still. He turns his back on her "
        "dismissively and walks off toward the far side of the lobby, leaving her standing alone.",
        f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    ),
))

# ---- 5. The call (ported from submit_redos_2.py CALL) ----
clips.append(dict(
    n=5, frames=124, seed=520105,
    refs=["isabel-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n{LOBBY_P2}",
        "Isabel makes one short phone call. No explanation, no threat — just an instruction.",
        f"{ISABEL_BEIGE}\n<Picture 2> {NO_CHARS_FROM} {ONE_PERSON}",
        OPEN + "Medium close shot, fixed camera, Isabel alone, phone already raised to her ear, her expression "
        "completely calm and unreadable. ISABEL (S1), quiet, commanding and clearly articulated, speaks the VERY "
        "FIRST LINE: <d>[English] I'm in the lobby. Get here now.</d> "
        "She lowers the phone without waiting for a reply.",
        "Quiet upscale hotel lobby ambience, a faint lobby piano far in the background. Only ISABEL speaks.",
    ),
))

# ---- 6. Manager orders her out (ported from submit_mock_v5.py) ----
clips.append(dict(
    n=6, frames=141, seed=520106,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The manager orders her out of his hotel, seconds before the call she just made ends his career.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is "
        f"black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, both already in position and standing clearly APART from each other, "
        "the manager several steps away from Isabel with his arms folded, looking at her with open contempt. Isabel "
        "stands holding her phone at her side, having just finished a call. They are NOT leaning together and are NOT "
        "looking at the phone jointly — he is dismissing her from a distance, not helping her. MANAGER (S2), cold and "
        "dismissive, his polished register cracking into open anger on the last two words, speaks the VERY FIRST "
        "LINE: <d>[English] Why are you still here? You're not welcome in this hotel. GET OUT!</d> "
        "The final \"GET OUT!\" is BARKED — sharply louder, harder and angrier than everything before it, the one "
        "moment his composure breaks. Isabel does not answer him and does not look away. She simply waits.",
        f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    ),
))

# ---- 7. The reveal ----
clips.append(dict(
    n=7, frames=175, seed=520107,
    refs=["isabel-ref.jpeg", "hotel-executive-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {EXECUTIVE_P2}\n{LOBBY_P3}",
        "A senior hotel executive stands before Isabel and greets her with deep deference, apologising for not "
        "knowing she had arrived.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is "
        f"clearly grey-streaked and he wears a navy THREE-PIECE suit with a visible waistcoat.\n"
        f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, the executive already standing in front of Isabel, slightly bowed "
        "toward her, both fully in frame. His whole posture is deferential — the opposite of how the staff have "
        "treated her. EXECUTIVE (S2), urgent and respectful, speaks the VERY FIRST LINE: "
        "<d>[English] Ms. Isabel. My apologies, ma'am — we didn't know you were here.</d> "
        "Isabel says nothing. She simply looks past him, toward where the manager is standing off-camera.",
        f"{AMBIENCE} Only the EXECUTIVE speaks in this clip.",
    ),
))

# ---- 8. The payback ----
clips.append(dict(
    n=8, frames=175, seed=520108,
    refs=["hotel-executive-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {EXECUTIVE_P2.replace('<Picture 2>', '<Picture 1>')}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The executive turns on the manager and fires him on the spot, in the middle of the lobby. The manager tries "
        "to protest that he did not know who she was.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. He is the OLDER man with "
        f"GREY-STREAKED hair in the NAVY THREE-PIECE suit with a visible waistcoat.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. He is the YOUNGER man with "
        f"slicked-back BLACK hair in the CHARCOAL two-piece suit with NO waistcoat. The two men must look clearly "
        f"different from each other and must never be confused or swapped.\n"
        f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, the two men facing each other in the lobby. The manager's smug "
        "expression is completely gone — he has gone pale and rigid. The executive does not raise his voice at all. "
        "EXECUTIVE (S1), ice cold, speaks the VERY FIRST LINE: <d>[English] Collect your things.</d> "
        "The manager takes a half step forward, panicking, hands lifting. MANAGER (S2), stammering, replies: "
        "<d>[English] Sir, I didn't know—</d> "
        "The executive cuts him off without blinking. EXECUTIVE (S1), flat and final: "
        "<d>[English] No. You didn't. That's exactly the problem.</d>",
        f"{AMBIENCE} Only the EXECUTIVE and the MANAGER speak.",
    ),
))

# ---- 9. Vicious ----
clips.append(dict(
    n=9, frames=141, seed=520109,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The manager grovels toward Isabel. She finally turns and looks at him, and tells him this is not over.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is "
        f"black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera, the manager turned toward Isabel, his hands half-raised in a pleading "
        "gesture, desperate. Isabel turns her head and looks directly at him for the first time, completely calm. "
        "ISABEL (S1), quiet and merciless, speaks the VERY FIRST LINE: "
        "<d>[English] It's not only your job you're going to lose.</d> "
        "The manager's face collapses. He says nothing.",
        f"{AMBIENCE} Only ISABEL speaks in this clip.",
    ),
))

# ---- 10. Cliffhanger (ported from submit_redos_2.py CLOSER) ----
clips.append(dict(
    n=10, frames=141, seed=520110,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "Isabel turns to the receptionist who started all of this and who thought she had been forgotten. One line, "
        "then a hard cut.",
        f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as "
        f"specified above.\n<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
        OPEN + "Medium two-shot, fixed camera. The receptionist is frozen behind the desk, having watched "
        "everything, clearly hoping she has gone unnoticed. Isabel turns her head slowly and looks straight at her. "
        "ISABEL (S1), quiet, almost gentle, every word clearly and unhurriedly enunciated, speaks the VERY FIRST "
        "LINE: <d>[English] And now, it's your turn.</d> "
        "The receptionist's face drains of colour. Hold on her stricken expression. Hard cut to black.",
        f"{AMBIENCE} Only ISABEL speaks in this clip.",
    ),
))


PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}


def submit(clip):
    payload = {
        "prompt": clip["prompt"], "mode": "refs", "engine": "h3",
        "params": dict(PARAMS_BASE, frames=clip["frames"], seed=clip["seed"]),
        "refs": clip["refs"],
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    for c in clips:
        r = submit(c)
        print(f"clip {c['n']:>2} (seed {c['seed']}, frames {c['frames']}): {r}")
        time.sleep(0.4)
