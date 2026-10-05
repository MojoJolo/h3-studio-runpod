"""Third attempt at the 'manager mocks the call' clip (row 7).

  510106 — "tatawagan" slurred.
  510132 — switched to "tinatawagan"; came out "tinatawaNGan". WORSE.

Diagnosis: not a seed problem. The TTS inserts a phantom /ng/ into a
medial g between vowels (-aga-). Tagalog writes /ng/ as a digraph and it
is extremely frequent, so a bare intervocalic g gets pulled toward it.
Lengthening the word added another syllable to exactly the broken part.

Fix: retire the tawag family entirely and write the line with NO
intervocalic g. User's combined line, with "ginagawa" (gi-na-GA-wa, the
same trap) swapped for "Bakit ka pa nandito?" and "pwede" written
uncontracted. Frames 141 -> 158 so three sentences are not rushed.
"""
import json
import urllib.request

from submit_redos_2 import (
    AMBIENCE, ISABEL, LOBBY_P3, MANAGER, NO_ARTIFACTS, NO_FOOD, PARAMS_BASE, build,
)

MOCK = build(
    f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER}\n{LOBBY_P3}",
    "The manager does not mock the call — he simply orders her out of his hotel, seconds before that call ends his "
    "career.",
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
    "each other, the manager several steps away from Isabel with his arms folded, looking at her with open contempt. "
    "Isabel stands holding her phone at her side, having just finished a call. They are NOT leaning together and are "
    "NOT looking at the phone jointly — he is dismissing her from a distance, not helping her. MANAGER (S2), cold and "
    "dismissive, every word unhurried and distinctly enunciated, speaks the VERY FIRST LINE: "
    "<d>[Tagalog] Bakit ka pa nandito? Hindi ka nga puwede dito. Umalis ka na.</d> "
    "Isabel does not answer him and does not look away. She simply waits.",
    f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    NO_FOOD,
)

SEED = 510134
REFS = ["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": MOCK, "mode": "refs", "engine": "h3",
               "params": dict(PARAMS_BASE, frames=158, seed=SEED), "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
