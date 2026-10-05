"""Build 3 Tagalog ragebait scripts (3 clips x 8s each) as sequence files.

Applies filipino-ragebait-short-drama-writer:
  §0  six-beat formula, gender-free roles, accidental-information hook,
      final line that makes them worse, no apology
  §7.1 accent block repeated in EVERY shot (it does not carry between clips)
  §7.3 3-8 pronunciation locks per clip, negative instructions preferred
  §7.4 locks live OUTSIDE <d>, never inside
  §7.5 standalone "ako" never "'ko"; 'to/'yan/'yon are fine

Outrage sources rotated, no cheating and no pregnancy in any of the three.
Shameless escalator is female / male / female across the batch.
"""
import os

ACCENT = """Both characters are native Metro Manila Filipino speakers.
They speak natural contemporary Tagalog with authentic Metro Manila Filipino pronunciation.
Use clear Filipino vowels and natural Filipino rhythm.
Do NOT use an American, English, Spanish, or other foreign accent when speaking Tagalog.
Do NOT anglicize Filipino vowels.
Do NOT speak any pronunciation instructions aloud."""

AUDIO = """CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Preserve all Tagalog pronouns and verb forms exactly.
Do NOT replace "mo" with "ko" or "ko" with "mo."
Do NOT alter verb aspect.
Never shorten standalone "ako" into "'ko."
Normal grammatical "ko" remains "ko."
Natural vernacular contractions such as "'to," "'yan," and "'yon" are allowed.
Do NOT paraphrase, normalize, or rewrite the dialogue."""


def clip(shot, location, a_desc, b_desc, rel, action, lines, locks, soundscape):
    body = "\n\n".join(action) if isinstance(action, list) else action
    lockblock = "\n".join(f"- {l}" for l in locks)
    return f"""8 | integrated_multimodal_description: [Shot {shot}] Photorealistic contemporary Filipino drama inside {location}. Natural restrained acting, realistic emotional tension, believable Filipino behavior. Handheld-steady continuous medium two-shot.

There are exactly two visible adult characters.

CHARACTER A is {a_desc}

CHARACTER B is {b_desc}

They are {rel}.

{ACCENT}

{AUDIO}

PRONUNCIATION LOCK:
{lockblock}
- These pronunciation instructions are SILENT and must never be spoken aloud.

The camera holds one continuous medium two-shot. Both characters are already in position from the very first frame — nobody walks into frame. Do NOT render any on-screen subtitles, captions, or burned-in text of any kind.

{body}

{lines}

overall_soundscape: {soundscape} No narrator or voice-over. Only CHARACTER A and CHARACTER B speak.

non_diegetic_music: N/A"""


# ---------------------------------------------------------------- SCRIPT 1
# Outrage: inheritance / funeral. Shameless escalator: the SISTER (female).
S1_LOC = "the cramped living room of an old family house at night, a folded funeral program on the table"
S1_A = ("MARIVIC, a 41-year-old Filipina woman in a plain black blouse, hair tied back, businesslike and completely "
        "unbothered, holding her phone and a folder of papers.")
S1_B = ("DANI, a 36-year-old Filipino man in a rumpled grey polo, exhausted, standing across the low table from her.")
S1_REL = "sister and younger brother, the night before their mother's funeral"
S1_SOUND = "Quiet old-house ambience at night, an electric fan, faint street noise outside."

s1c1 = clip(1, S1_LOC, S1_A, S1_B, S1_REL,
    "Marivic slides the folder aside without looking up from her phone and says it like a small admin correction.",
    """MARIVIC (S1), brisk, matter-of-fact, speaks the VERY FIRST LINE: <d>[Tagalog] Wag mo nang ilagay sa obituary yung address. Hindi na atin 'yon.</d>

Dani stops moving completely.

DANI (S2), quiet, not yet angry: <d>[Tagalog] Hindi na atin?</d>

Marivic finally looks up, mildly impatient at having to explain.

MARIVIC (S1), flat, unbothered: <d>[Tagalog] Binenta ko na. Noong isang buwan pa.</d>""",
    ["atin = A-tin, two syllables, stress on A, never pronounced like the English \"eighteen\"",
     "binenta = bi-nen-TA, three syllables, stress on TA",
     "obituary is an English word — say it naturally in English, then return to Filipino pronunciation",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S1_SOUND)

s1c2 = clip(2, S1_LOC, S1_A, S1_B, S1_REL,
    "Dani picks up the funeral program and holds it, not raising his voice.",
    """DANI (S2), low, disbelieving, speaks the VERY FIRST LINE: <d>[Tagalog] Hindi pa nga siya nalilibing.</d>

Marivic shrugs, already moving on to the next thing on her phone.

MARIVIC (S1), reasonable, as if explaining a schedule: <d>[Tagalog] Kailangan nilang lumipat bago matapos ang buwan.</d>

Dani sets the program down very carefully.

DANI (S2), quiet: <d>[Tagalog] Bukas ang libing.</d>""",
    ["nalilibing = na-li-li-BING, four syllables, stress on BING",
     "libing = li-BING, two syllables, stress on BING, keep the final NG clear",
     "lumipat = lu-MI-pat, three syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S1_SOUND)

s1c3 = clip(3, S1_LOC, S1_A, S1_B, S1_REL,
    "Marivic nods, agreeing with him, completely missing that it is an objection.",
    """MARIVIC (S1), agreeable, practical, speaks the VERY FIRST LINE: <d>[Tagalog] Kaya nga bukas na rin sila lilipat. Sabay na.</d>

Dani stares at her.

DANI (S2), quiet, final: <d>[Tagalog] Gago ka ba?</d>

Marivic looks genuinely puzzled by the reaction, and answers without any cruelty in her tone at all — she means it as logic.

MARIVIC (S1), mild, sincere: <d>[Tagalog] Bakit? Gagamitin pa ba niya?</d>

Hold on Dani's face. CUT ABRUPTLY.""",
    ["gago = GA-go, two syllables, stress on GA",
     "gagamitin = ga-ga-MI-tin, four syllables, stress on MI",
     "sabay = SA-bay, two syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S1_SOUND + " Abrupt audio cut at the end.")


# ---------------------------------------------------------------- SCRIPT 2
# Outrage: household labour / entitlement. Shameless escalator: the HUSBAND (male).
S2_LOC = "a small modern condominium kitchen in the early evening, laundry folded in a basket on the counter"
S2_A = ("REY, a 34-year-old Filipino man in a fresh polo shirt, relaxed, scrolling his phone at the counter, "
        "completely at ease.")
S2_B = ("JHEN, a 33-year-old Filipina woman in a loose house shirt, sleeves pushed up, mid-way through folding "
        "laundry, tired.")
S2_REL = "husband and wife"
S2_SOUND = "Quiet condominium kitchen ambience, a refrigerator hum, faint traffic from outside."

s2c1 = clip(1, S2_LOC, S2_A, S2_B, S2_REL,
    "Rey says it casually, without looking up from his phone, as if it were already settled.",
    """REY (S1), casual, pleased with himself, speaks the VERY FIRST LINE: <d>[Tagalog] Sabi ko kay Ate, sa gamit ko lang siya maglilinis.</d>

Jhen stops folding.

JHEN (S2), flat: <d>[Tagalog] Sa gamit mo lang?</d>

Rey shrugs, as if the answer is obvious and slightly generous of him.

REY (S1), reasonable: <d>[Tagalog] Ako naman nagbabayad sa kanya.</d>""",
    ["gamit = GA-mit, two syllables, stress on GA",
     "maglilinis = mag-li-LI-nis, four syllables",
     "nagbabayad = nag-ba-BA-yad, four syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S2_SOUND)

s2c2 = clip(2, S2_LOC, S2_A, S2_B, S2_REL,
    "Jhen sets the shirt down on the pile and finally turns to face him.",
    """JHEN (S2), quiet, precise, speaks the VERY FIRST LINE: <d>[Tagalog] Sa joint account galing yung sahod niya.</d>

Rey does not flinch, does not deny it.

REY (S1), mild, unbothered: <d>[Tagalog] Pareho naman tayong may pera doon.</d>

Jhen looks at the laundry basket, then back at him.

JHEN (S2), quiet: <d>[Tagalog] Tapos akin pa rin lahat ng iba?</d>""",
    ["sahod = SA-hod, two syllables, stress on SA",
     "galing = GA-ling, two syllables, keep the final NG clear",
     "joint account is English — say it naturally in English, then return to Filipino pronunciation",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S2_SOUND)

s2c3 = clip(3, S2_LOC, S2_A, S2_B, S2_REL,
    "Rey sets the phone face down, finally giving her his full attention, and explains it patiently.",
    """REY (S1), patient, completely sincere, speaks the VERY FIRST LINE: <d>[Tagalog] Eh nasa bahay ka naman buong araw.</d>

Jhen does not raise her voice at all.

JHEN (S2), flat, final: <d>[Tagalog] Gago ka.</d>

Rey spreads his hands, genuinely offended, as if she is refusing a fair arrangement.

REY (S1), reasonable, almost kind: <d>[Tagalog] Mag-ambag ka kung gusto mo rin ng tulong.</d>

Hold on Jhen's face. CUT ABRUPTLY.""",
    ["mag-ambag = mag-am-BAG, stress on BAG, keep the hyphen break audible as a small glottal stop",
     "gago = GA-go, two syllables, stress on GA",
     "buong = BU-ong, two syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S2_SOUND + " Abrupt audio cut at the end.")


# ---------------------------------------------------------------- SCRIPT 3
# Outrage: in-laws / property. Shameless escalator: the MOTHER-IN-LAW (female).
S3_LOC = "the dining area of a modest two-storey family home in the afternoon, a brown envelope of documents on the table"
S3_A = ("LOLIT, a 62-year-old Filipina woman in a floral house dress, calm and maternal, hands folded on the table, "
        "speaking warmly throughout.")
S3_B = ("CAMILLE, a 35-year-old Filipina woman in a travel jacket, a suitcase still standing by the doorway behind "
        "her, just arrived home.")
S3_REL = "mother-in-law and daughter-in-law"
S3_SOUND = "Quiet afternoon household ambience, a wall clock, distant tricycle noise from the street."

s3c1 = clip(1, S3_LOC, S3_A, S3_B, S3_REL,
    "Lolit pats the brown envelope on the table, reassuring her, as if delivering good news.",
    """LOLIT (S1), warm, motherly, speaks the VERY FIRST LINE: <d>[Tagalog] Wag kang mag-alala sa bahay. Nasa pangalan ko na.</d>

Camille stops with her hand still on her jacket zipper.

CAMILLE (S2), quiet: <d>[Tagalog] Nasa pangalan mo?</d>

Lolit smiles, pleased to have taken care of it.

LOLIT (S1), helpful, warm: <d>[Tagalog] Inayos ko noong nasa abroad ka.</d>""",
    ["pangalan = pa-NGA-lan, three syllables — the NG is a single Filipino sound, never \"pan-ga-lan\"",
     "mag-alala = mag-a-LA-la, keep the hyphen break audible as a small glottal stop",
     "inayos = i-NA-yos, three syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S3_SOUND)

s3c2 = clip(2, S3_LOC, S3_A, S3_B, S3_REL,
    "Camille sets her bag down slowly and stays standing.",
    """CAMILLE (S2), quiet, steady, speaks the VERY FIRST LINE: <d>[Tagalog] Apat na taon kaming naghulog niyan.</d>

Lolit nods sympathetically, agreeing with her, and explains the precaution.

LOLIT (S1), gentle, reasonable: <d>[Tagalog] Mas safe. Baka kasi maghiwalay kayo.</d>

Camille does not move.

CAMILLE (S2), flat: <d>[Tagalog] Kami ang bumili.</d>""",
    ["naghulog = nag-HU-log, three syllables, keep the final G clear and do NOT turn it into NG",
     "maghiwalay = mag-hi-wa-LAY, four syllables, stress on LAY",
     "bumili = bu-MI-li, three syllables",
     "safe is English — say it naturally in English, then return to Filipino pronunciation",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S3_SOUND)

s3c3 = clip(3, S3_LOC, S3_A, S3_B, S3_REL,
    "Lolit reaches over and pats Camille's hand on the table, still entirely warm.",
    """LOLIT (S1), affectionate, sincere, speaks the VERY FIRST LINE: <d>[Tagalog] Anak ko yung asáwa mo. Protektado lang siya.</d>

Camille pulls her hand back.

CAMILLE (S2), quiet, final: <d>[Tagalog] Kapal ng mukha mo.</d>

Lolit looks briefly hurt, then recovers and says it kindly, as if nothing has changed.

LOLIT (S1), gentle, practical: <d>[Tagalog] Tuloy mo lang yung hulog. Walang magbabago.</d>

Hold on Camille's face. CUT ABRUPTLY.""",
    ["asáwa = a-SA-wa, three syllables, stress on SA",
     "kapal = ka-PAL, two syllables, stress on PAL",
     "mukha = muk-HA, two syllables, stress on HA",
     "magbabago = mag-ba-BA-go, four syllables",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."],
    S3_SOUND + " Abrupt audio cut at the end.")


SCRIPTS = {
    "01_inheritance": [s1c1, s1c2, s1c3],
    "02_household":   [s2c1, s2c2, s2c3],
    "03_inlaws":      [s3c1, s3c2, s3c3],
}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, clips in SCRIPTS.items():
        path = os.path.join(here, f"{name}.txt")
        with open(path, "w") as fh:
            fh.write("\n\n=====\n\n".join(clips) + "\n")
        print(f"wrote {path}  ({len(clips)} clips)")
