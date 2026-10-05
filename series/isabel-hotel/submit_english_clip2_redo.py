"""Redo of the ENGLISH clip 2 (seed 520102 -> 520122).

Defect: the receptionist rendered out from behind the counter and never looked
at Isabel.

Root cause — a prompt bug I carried over from submit.py without noticing:

    "Medium two-shot, fixed camera, SAME POSITIONS at the reception desk."

Every clip is generated independently. There is no previous clip in the model's
context, so "same positions" references nothing and specifies nothing. The
staging was effectively blank and the result was a coin flip. The Tagalog cut
happened to win that flip; the English one lost it.

Fixes:
  1. Staging spelled out explicitly, mirroring the approved clip 1 redo:
     receptionist BEHIND the counter on the staff side, Isabel in FRONT on the
     guest side, facing each other across it, both already in position.
  2. "Barely glances at her computer screen" is replaced. That direction pulled
     her eyeline away from Isabel, and it also undersold the insult. She now
     never looks at the screen at all and holds eye contact with Isabel the
     whole time — refusing to even check is a sharper beat than pretending to.

Seed changed rather than held: the single-variable rule exists for when the
cause is uncertain. Here the defect is an instruction that referenced a
nonexistent prior clip, so there is nothing to isolate. 520122 mirrors the
510122 convention already used for the clip 1 redo.
"""
import json
import urllib.request

from submit_english import (
    AMBIENCE, ISABEL, ISABEL_BEIGE, LOBBY_P3, NO_CHARS_FROM, OPEN, PARAMS_BASE,
    RECEPTIONIST, TWO_PEOPLE, build,
)

PROMPT = build(
    f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
    "The receptionist refuses to even check, insisting there is no record and the hotel is full. Isabel asks her "
    "calmly to check again and is shut down without the receptionist so much as touching her keyboard.",
    f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as "
    f"specified above.\n<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
    OPEN + "Medium two-shot, fixed camera, framed so both women fill most of the frame from the waist up, with the "
    "marble counter running across the bottom of the frame between them. The RECEPTIONIST stands BEHIND the "
    "reception counter on the staff side, with the computer monitor beside her. ISABEL stands in FRONT of the "
    "counter on the guest side, facing her directly across it. They are face to face across the counter. Both are "
    "ALREADY in position from the very first frame — nobody walks into frame and nobody moves out from behind the "
    "counter at any point. "
    "The receptionist looks directly AT Isabel the entire time and never turns toward the computer monitor. She does "
    "not touch the keyboard once — refusing to even check is the insult. RECEPTIONIST (S2), dismissive, holding "
    "Isabel's gaze, speaks the VERY FIRST LINE: "
    "<d>[English] We don't have any record of that. And we're fully booked.</d> "
    "Isabel remains calm, her hands still folded on her handbag. ISABEL (S1), patient, asks: "
    "<d>[English] Could you check again, please?</d> "
    "The receptionist still does not look at the screen and still does not touch the keyboard. RECEPTIONIST (S2), "
    "clipped and final, still looking straight at Isabel, replies: "
    "<d>[English] Ma'am. I know how to do my job.</d>",
    f"{AMBIENCE} Only the RECEPTIONIST and ISABEL speak.",
)

SEED = 520122
REFS = ["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": PROMPT, "mode": "refs", "engine": "h3",
               "params": dict(PARAMS_BASE, frames=192, seed=SEED), "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
