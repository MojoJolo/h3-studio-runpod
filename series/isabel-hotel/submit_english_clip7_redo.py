"""Redo of the ENGLISH clip 7 (seed 520107 -> 520127): ISABEL -> CLAIRE.

The Filipino-English accent rendered the name "Isabel" poorly. "Claire" is one
syllable with a hard /kl/ onset and no vowel cluster to smear — the opposite
shape to I-sa-bel, and it sits cleanly against the "ma'am" later in the line.

This is the ONLY clip in the English cut that SPEAKS her name. Every other
mention lives in subject_definitions and staging prose, which is never
vocalised, so nothing else needs regenerating.

The name is changed throughout this clip's prompt, not only in the dialogue —
leaving the definitions saying ISABEL while the line says "Ms. Claire" would be
internally inconsistent. Visual drift risk is low because the face is pinned by
<Picture 1>.

NOTE: submit_english.py is deliberately NOT edited. It is the record of what
actually produced the approved renders, and clips 1-10 were all generated with
the old internal name. Since the name is never spoken in any of them, they stay
valid as-is. If one is ever regenerated, rename it there at that point — it is
a fresh draw either way.

The Tagalog cut's clip 7 (510107) still says "Ma'am Isabel" and needs no
change: "Isabel" is a native Spanish/Filipino name and renders correctly in
Tagalog. This is an English-accent problem only.
"""
import json
import urllib.request

from submit_english import (
    AMBIENCE, EXECUTIVE_P2, ISABEL, ISABEL_BEIGE, LOBBY_P3, NO_CHARS_FROM, OPEN,
    PARAMS_BASE, TWO_PEOPLE, build,
)

NAME = "CLAIRE"
CLAIRE = ISABEL.replace("ISABEL", NAME)

PROMPT = build(
    f"<Subject 1> is {CLAIRE}\n<Subject 2> is {EXECUTIVE_P2}\n{LOBBY_P3}",
    f"A senior hotel executive stands before {NAME.title()} and greets her with deep deference, apologising for not "
    "knowing she had arrived.",
    f"{ISABEL_BEIGE}\n<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. His hair is "
    f"clearly grey-streaked and he wears a navy THREE-PIECE suit with a visible waistcoat.\n"
    f"<Picture 3> {NO_CHARS_FROM} {TWO_PEOPLE}",
    OPEN + f"Medium two-shot, fixed camera, the executive already standing in front of {NAME.title()}, slightly "
    "bowed toward her, both fully in frame. His whole posture is deferential — the opposite of how the staff have "
    "treated her. EXECUTIVE (S2), urgent and respectful, speaks the VERY FIRST LINE: "
    "<d>[English] Ms. Claire. My apologies, ma'am — we didn't know you were here.</d> "
    "PRONUNCIATION: the name is \"Claire\", one syllable, rhyming with \"air\" — spoken clearly and not stretched "
    f"into two syllables. {NAME.title()} says nothing. She simply looks past him, toward where the manager is "
    "standing off-camera.",
    f"{AMBIENCE} Only the EXECUTIVE speaks in this clip.",
)

SEED = 520127
REFS = ["isabel-ref.jpeg", "hotel-executive-ref.jpeg", "hotel-lobby-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": PROMPT, "mode": "refs", "engine": "h3",
               "params": dict(PARAMS_BASE, frames=175, seed=SEED), "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
