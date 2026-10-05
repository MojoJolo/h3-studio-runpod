"""Breadwinner / operation money / sabong — 3 clips x 8s, Tagalog.

Dialogue approved by the user as plain text; stress marks added here only,
words unchanged. Marks go on polysyllabic CONTENT words (nouns, verbs,
adjectives). Particles and short pronouns (ka, na, lang, ko, mo, ni, pa, ang,
may, sa, naman, 'yon, kang, ako) are left unmarked — §7.3 warns that locking
everything produces robotic pacing.

Per §7.1 the accent block is repeated in EVERY clip (it does not carry between
independently generated clips). Per §7.4 all pronunciation guidance sits OUTSIDE
<d>. Per §7.5 standalone "ako" is written in full, never "'ko".
"""
import os

ACCENT = """Both characters are native Metro Manila Filipino speakers.
They speak natural contemporary Tagalog with authentic Metro Manila Filipino pronunciation.
Use clear Filipino vowels and natural Filipino rhythm.
Do NOT use an American, English, Spanish, or other foreign accent when speaking Tagalog.
Do NOT anglicize Filipino vowels.
Accented vowels (á, í, ú, é, ó) mark WHICH SYLLABLE IS STRESSED. They are pronunciation guides only — never spell them out, never mention them, never read them aloud as separate sounds.
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
Natural vernacular contractions such as "'to," "'yan," and "'yon" are allowed.
Do NOT paraphrase, normalize, or rewrite the dialogue."""

JUN = ("JUN, a 29-year-old Filipino man in a plain faded t-shirt and shorts, slippers, completely relaxed, "
       "sitting sideways on the arm of the sofa with his phone in one hand, asking for something he expects to get.")
ANNA = ("ANNA, a 32-year-old Filipina woman still in her office blouse with her work ID lanyard on and a bag "
        "over one shoulder, just arrived home, standing, tired.")
LOC = ("the living room of a modest Filipino family home in the evening, a small sofa, an electric fan, a closed "
       "bedroom door at the back of the room")
REL = "brother and older sister — Anna supports the household"
SOUND = "Quiet family-home ambience in the evening, an electric fan, faint street noise and a distant tricycle."


def clip(shot, action, lines, locks, tail=""):
    lockblock = "\n".join(f"- {l}" for l in locks)
    return f"""8 | integrated_multimodal_description: [Shot {shot}] Photorealistic contemporary Filipino drama inside {LOC}. Natural restrained acting, realistic Filipino family tension, believable behavior — nobody shouts.

There are exactly two visible adult characters.

CHARACTER A is {JUN}

CHARACTER B is {ANNA}

They are {REL}.

{ACCENT}

{AUDIO}

PRONUNCIATION LOCK:
{lockblock}
- These pronunciation instructions are SILENT and must never be spoken aloud.

The camera holds one continuous medium two-shot. Both are already in position from the very first frame — nobody walks into frame. Exactly two people are visible and no one else; do not duplicate or clone either character. Do NOT render any on-screen subtitles, captions, or burned-in text of any kind.

{action}

{lines}

overall_soundscape: {SOUND} No narrator or voice-over. Only JUN and ANNA speak.{tail}

non_diegetic_music: N/A"""


c1 = clip(1,
    "Jun does not look up from his phone. He says it casually, the way you would mention a small errand, and the "
    "second sentence slips out as an afterthought.",
    """JUN (S1), casual, unbothered, speaks the VERY FIRST LINE: <d>[Tagalog] Magpadalá ka na lang úlit. Natálo ko na kasí.</d>

Anna stops with the bag still on her shoulder. She does not put it down.

ANNA (S2), quiet, flat: <d>[Tagalog] Natálo?</d>

Jun finally glances up, mildly surprised she is making something of it.

JUN (S1), matter-of-fact, minimizing: <d>[Tagalog] Sa sábong. Maliít lang naman.</d>""",
    ["magpadalá = mag-pa-da-LA, four syllables, stress on the final LA",
     "úlit = U-lit, two syllables, stress on U",
     "natálo = na-TA-lo, three syllables, stress on the middle TA — never \"na-ta-LO\"",
     "kasí = ka-SI, two syllables, stress on SI",
     "sábong = SA-bong, two syllables, stress on SA, keep the final NG as one clear Filipino sound",
     "maliít = ma-li-IT, three syllables — the two i vowels are separate, never collapsed into one long English \"ee\""])

c2 = clip(2,
    "Anna sets the bag down on the sofa without taking her eyes off him.",
    """ANNA (S2), quiet, precise, speaks the VERY FIRST LINE: <d>[Tagalog] Pang-ópera 'yon ni Tátay.</d>

Jun does not flinch and does not deny it. He shifts to reassurance, as if the problem is her worrying.

JUN (S1), confident, reassuring: <d>[Tagalog] Babáwi ako. Malápit na.</d>

Anna looks at the closed bedroom door at the back of the room, then back at him.

ANNA (S2), flat: <d>[Tagalog] Malápit na?</d>""",
    ["pang-ópera = pang-O-pe-ra, stress on the O; keep the hyphen as a small break, not a smooth glide",
     "Tátay = TA-tay, two syllables, stress on TA",
     "babáwi = ba-BA-wi, three syllables, stress on the middle BA",
     "malápit = ma-LA-pit, three syllables, stress on LA",
     "Keep all Filipino vowels pure and short. Do NOT anglicize them."])

c3 = clip(3,
    "Jun puts the phone down and explains it patiently, genuinely believing he is being reasonable.",
    """JUN (S1), patient, entitled, speaks the VERY FIRST LINE: <d>[Tagalog] Ikáw naman ang may trabáho. Kayá mo naman.</d>

Anna does not raise her voice at all.

ANNA (S2), quiet, final: <d>[Tagalog] Gágo ka.</d>

Jun glances at the closed bedroom door, then lowers his voice — not ashamed, just practical, asking her to help him keep it quiet.

JUN (S1), low, matter-of-fact: <d>[Tagalog] Wag kang maíngay. Hindi pa niya alám.</d>

Hold on Anna's face. CUT ABRUPTLY.""",
    ["ikáw = i-KAW, two syllables, stress on KAW",
     "trabáho = tra-BA-ho, three syllables, stress on BA",
     "kayá = ka-YA, two syllables, stress on YA",
     "gágo = GA-go, two syllables, stress on GA — never \"ga-GO\"",
     "maíngay = ma-I-ngay, three syllables, stress on the I; NG is one Filipino sound",
     "alám = a-LAM, two syllables, stress on LAM"],
    " Abrupt audio cut at the end.")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "script.txt")
    with open(path, "w") as fh:
        fh.write("\n\n=====\n\n".join([c1, c2, c3]) + "\n")
    print("wrote", path)
