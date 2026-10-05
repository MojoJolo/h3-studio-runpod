"""Three redos for the Isabel hotel episode.

  A. The call (was 510105) — "Nasa lobby ako" rendered slightly unclear.
     Same line, rerolled seed, plus an explicit clear-articulation note.
  B. Manager mocks the call (was 510106) — "tatawagan" mispronounced, and
     the shot contained a phantom table with a plated meal on it. Line
     switched to present-progressive "tinatawagan" (better Tagalog for a
     call in progress, different word shape for the TTS), and all food /
     table props explicitly forbidden.
  C. Closing line (was 510110) — "Ikaw naman." was incomprehensible; two
     short words give the TTS almost nothing to work with. Extended to
     "At ngayon, ikaw naman." for both clarity and a better button.
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

MANAGER = ("the HOTEL MANAGER, using <Picture 2> for his identity: a Filipino man with slicked-back BLACK hair, "
           "clean-shaven, wearing a CHARCOAL GREY two-piece suit with a gold hotel lapel pin and a grey tie. "
           "He has NO waistcoat and NO grey in his hair.")

LOBBY_P3 = ("<Picture 3> is the hotel lobby: polished marble floors, a long reception desk with brass accents and a "
            "marble counter, warm ambient lighting, a tall floral arrangement, high ceilings, elegant seating visible "
            "in the background. Composition/location anchor only — no characters appear in this picture.")

LOBBY_P2 = LOBBY_P3.replace("<Picture 3>", "<Picture 2>")

CLEAR_SPEECH = ("Dialogue must be delivered in clear, natural, well-articulated conversational Filipino — unhurried "
                "and distinctly enunciated, never mumbled, slurred or rushed.")

NO_TEXT = ("Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere "
           "in the frame, and no readable text inside the scene itself — no nameplates, placards or printed signage.")

NO_FOOD = ("There is NO food, NO plates, NO dishes, NO trays, NO cutlery and NO dining table anywhere in this shot. "
           "This is a hotel reception lobby, not a restaurant. The marble surfaces are clear and bare.")

NO_ARTIFACTS = ("No visual artifacts, streaks, lines, or chromatic fringing anywhere in frame — clean photographic "
                "image quality throughout. Each character's garment keeps its own exact colour for the entire clip "
                "and never drifts toward another character's colour.")

AMBIENCE = ("Quiet upscale hotel lobby ambience, soft footsteps on marble, distant murmured conversation, a faint "
            "lobby piano far in the background.")


def build(subjects, summary, retention, shots, soundscape, extra_visual=""):
    return f"""subject_definitions:
{subjects}

summary:
[reference generation] {summary}

retention_analysis:
{retention}

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue. {CLEAR_SPEECH}
CRITICAL VISUAL RULE: {NO_TEXT} {extra_visual}

{shots}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


# ---- A. The call (solo Isabel) ----
CALL = build(
    f"<Subject 1> is {ISABEL}\n{LOBBY_P2}",
    "Isabel makes one short phone call. No explanation, no threat — just an instruction.",
    f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Her blouse MUST be light beige / "
    f"warm sand-tan and must never render as white, grey, charcoal, black or navy.\n"
    f"<Picture 2> is used only for the lobby layout and lighting — do not add any character from this picture. "
    f"Exactly one person is visible in every frame of this clip: Isabel alone, and no one else. Do not duplicate or "
    f"clone her. No second person, hand, arm, or limb of any kind anywhere in frame. Background hotel guests may "
    f"appear only as distant, blurred, out-of-focus figures far behind her. {NO_ARTIFACTS}",
    "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at "
    "any point in this clip. Medium close shot, fixed camera, Isabel alone, phone already raised to her ear, her "
    "expression completely calm and unreadable. ISABEL (S1), quiet, commanding and clearly articulated, speaks the "
    "VERY FIRST LINE: <d>[Tagalog] Nasa lobby ako. Punta ka dito.</d> She lowers the phone without waiting for a reply.",
    "Quiet upscale hotel lobby ambience, a faint lobby piano far in the background. Only ISABEL speaks.",
    NO_FOOD,
)

# ---- B. Manager mocks the call ----
MOCK = build(
    f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER}\n{LOBBY_P3}",
    "The manager sees her on the phone and mocks her for it — seconds before that call destroys his career.",
    f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Her blouse MUST be light beige / "
    f"warm sand-tan and must never render as white, grey, charcoal, black or navy.\n"
    f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is black and slicked "
    f"back with NO grey, and his charcoal suit has NO waistcoat.\n"
    f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. "
    f"Exactly two people are visible in every shot of this clip, and no one else. Do not duplicate, clone, or "
    f"generate a second version of either subject. No third person, no extra hand, arm, or limb of any kind anywhere "
    f"in frame. Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind them. "
    f"{NO_ARTIFACTS}",
    "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at "
    "any point in this clip. Medium two-shot, fixed camera, both already in position and standing clearly APART from "
    "each other, the manager several steps away from Isabel with his arms folded, smirking across the space at the "
    "phone in her hand. They are NOT leaning together and are NOT looking at the phone jointly — he is mocking her "
    "from a distance, not helping her. MANAGER (S2), openly mocking and clearly articulated, speaks the VERY FIRST "
    "LINE: <d>[Tagalog] Sino ba naman ang tinatawagan mo? Walang makakatulong sa iyo dito.</d> "
    "Isabel does not answer him and does not look away. She simply waits.",
    f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    NO_FOOD,
)

# ---- C. Closing line ----
CLOSER = build(
    f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
    "Isabel turns to the receptionist who started all of this and who thought she had been forgotten. One line, then "
    "a hard cut.",
    f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Her blouse MUST be light beige / "
    f"warm sand-tan and must never render as white, grey, charcoal, black or navy.\n"
    f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.\n"
    f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. "
    f"Exactly two people are visible in every shot of this clip, and no one else. Do not duplicate, clone, or "
    f"generate a second version of either subject. No third person, no extra hand, arm, or limb of any kind anywhere "
    f"in frame. Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind them. "
    f"{NO_ARTIFACTS}",
    "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at "
    "any point in this clip. Medium two-shot, fixed camera. The receptionist is frozen behind the desk, having "
    "watched everything, clearly hoping she has gone unnoticed. Isabel turns her head slowly and looks straight at "
    "her. ISABEL (S1), quiet, almost gentle, every word clearly and unhurriedly enunciated, speaks the VERY FIRST "
    "LINE: <d>[Tagalog] At ngayon, ikaw naman.</d> The receptionist's face drains of colour. Hold on her stricken "
    "expression. Hard cut to black.",
    f"{AMBIENCE} Only ISABEL speaks in this clip.",
    NO_FOOD,
)

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}


def submit(prompt, frames, seed, refs):
    payload = {"prompt": prompt, "mode": "refs", "engine": "h3",
               "params": dict(PARAMS_BASE, frames=frames, seed=seed), "refs": refs}
    req = urllib.request.Request(API, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    print("call      :", submit(CALL, 124, 510131, ["isabel-ref.jpeg", "hotel-lobby-ref.jpeg"]))
    time.sleep(0.4)
    print("mock      :", submit(MOCK, 141, 510132,
                                ["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"]))
    time.sleep(0.4)
    print("closer    :", submit(CLOSER, 141, 510133,
                                ["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"]))
