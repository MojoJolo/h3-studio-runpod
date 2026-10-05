"""Fourth attempt at the 'manager orders her out' clip (row 7).

Failure log for this one beat:
  510106  "Sino ba naman ang tatawagan mo?"       -> "tatawagan" slurred
  510132  "...ang tinatawagan mo?"                -> "tinatawaNGan"   (intervocalic g)
  510134  "Bakit ka pa nandito? Hindi ka nga
           puwede dito. Umalis ka na."            -> "Bakit ka PANAY nandito?" (particle
                                                    merge) and "WALIS ka na." (word-initial
                                                    vowel elided onto a commoner word)
                                                    Middle sentence rendered CORRECTLY.

Generalised diagnosis: the TTS fails at weak prosodic boundaries.
  1. intervocalic g  -> phantom /ng/
  2. unstressed monosyllabic particle -> absorbed into the following word
  3. word-initial vowel -> elided, especially when the result is a more
     frequent real word (umalis -> walis, "broom")

Strategy change: stop rewriting the whole line each round. Anchor on the
ONE sentence that has rendered correctly and build minimally around it.
  - "Hindi ka nga puwede dito." kept VERBATIM - the only string that has
    rendered correctly on every attempt.
  - The two broken sentences are replaced with ENGLISH, at the user's
    suggestion. This sidesteps the Tagalog TTS entirely on the two beats
    that keep failing, and Taglish code-switching is authentic for an
    upper-class Manila hotel manager - it reads as class contempt, which
    is what the beat wants anyway.
  - "GET OUT!" is a hard, angry button - the manager finally drops the
    polished register.

NOTE ON THE EARLIER DIAGNOSES IN THIS FILE: both were overfitted to 2-3
samples. The manager's own earlier line (clip 3) contains "Umalis",
"bago" AND "tawagin" and renders correctly, and the failing clip was
SLOWER in syllables/sec than the working one. The word-level and
speech-rate theories are both disproven. Treat these failures as largely
stochastic; the reliable levers are rerolling and switching language.
"""
import json
import urllib.request

from submit_redos_2 import (
    AMBIENCE, ISABEL, LOBBY_P3, MANAGER, NO_ARTIFACTS, NO_FOOD, PARAMS_BASE, build,
)

MOCK = build(
    f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER}\n{LOBBY_P3}",
    "The manager orders her out of his hotel, seconds before the call she just made ends his career.",
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
    "dismissive, his polished register cracking into open anger on the last two words, speaks the VERY FIRST LINE: "
    "<d>[Tagalog] Why are you still here? Hindi ka nga puwede dito. GET OUT!</d> "
    "DELIVERY: the speaker is a FILIPINO man speaking FILIPINO ENGLISH. The English sentences must be spoken with a "
    "natural Tagalog accent — the accent of an educated Manila professional speaking English — NOT American, NOT "
    "British, NOT neutral international English. This is ordinary Filipino code-switching, not a foreigner speaking. "
    "The first sentence is cold and clipped. The middle sentence is Tagalog. The final \"GET OUT!\" is BARKED — "
    "sharply louder, harder and angrier than everything before it, the one moment his composure breaks. "
    "Isabel does not answer him and does not look away. She simply waits.",
    f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    NO_FOOD,
)

SEED = 510135
REFS = ["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": MOCK, "mode": "refs", "engine": "h3",
               "params": dict(PARAMS_BASE, frames=141, seed=SEED), "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
