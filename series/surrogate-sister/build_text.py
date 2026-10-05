"""Surrogate sister, normal Tagalog drama (text mode, chained Sequence).
Stress verified by the user 2026-10-03 (v2: A-te slower, magkaanák -> mabuntís): béses = BE-ses, siyempre unmarked, mahál = ma-HAL, ibig unmarked."""
import json

ENV = ("Photorealistic contemporary Filipino family drama in a modest Metro Manila living room in the daytime: "
       "a small wooden dining table with two plastic monobloc chairs facing each other, a small religious statue on a "
       "shelf, tiled floor, a window with sheer curtains and soft natural daylight, an electric fan in the corner. "
       "Single continuous 8-second shot.")

CHARS = """CHARACTER 1 — MAMA:
- age: mid-50s
- gender presentation: woman
- skin tone: medium-brown Filipina skin
- hair: short curly permed black hair with visible grey streaks
- clothing: loose pastel floral house duster dress
- body / visual characteristics: round warm face with fine lines, slightly heavyset build
- screen position: SCREEN-LEFT, seated at the table
- speaker ID: S1

CHARACTER 2 — JEN:
- age: 26
- gender presentation: woman
- skin tone: light-tan Filipina skin
- hair: long straight black hair in a high ponytail
- clothing: plain fitted solid black t-shirt
- body / visual characteristics: slim athletic build, sharp defined features, light makeup
- screen position: SCREEN-RIGHT, seated at the table facing Mama
- speaker ID: S2

CRITICAL CHARACTER IDENTITY LOCK:
NEVER swap their faces.
NEVER swap their hairstyles.
NEVER swap their bodies.
NEVER swap their ages.
NEVER swap their wardrobe.
NEVER swap their screen positions.
NEVER swap their voices.
NEVER swap their dialogue.
NEVER morph one character into the other.
MAMA = SCREEN-LEFT. JEN = SCREEN-RIGHT. They do NOT cross. They do NOT exchange sides.
Maintain the same facial identity from first frame to last frame."""

ACCENT = """Both characters are native Metro Manila Filipino speakers.
They speak natural contemporary Tagalog/Taglish with authentic Metro Manila Filipino pronunciation.
Use clear Filipino vowels and natural Filipino rhythm.
Do NOT use an American, English, Spanish, or other foreign accent when speaking Tagalog.
Do NOT anglicize Filipino vowels.
Do NOT speak pronunciation instructions aloud."""

RULES = """CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.
Never speak timestamps, character descriptions, actions, camera instructions, speaker labels, pronunciation guidance, or production notes.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Preserve all Tagalog pronouns and verb forms exactly.
Do NOT replace "mo" with "ko" or "ko" with "mo."
Never shorten standalone "ako" into "'ko."
Normal grammatical "ko" remains "ko."
Do NOT paraphrase, normalize, or rewrite the dialogue.

VISUAL RULES:
Exactly 2 visible characters: Mama and Jen. Do NOT show another character. A-te and Marvin are mentioned only and remain OFF-SCREEN. No silhouettes, reflections or figures of a third person anywhere. No on-screen text, no subtitles, no captions. Natural restrained acting. Absurd situation played completely seriously. Do not exaggerate reactions. No teleserye acting. Mama genuinely believes her logic is reasonable."""

FINAL = """FINAL SPEAKER LOCK:
S1 = MAMA ONLY (SCREEN-LEFT, floral house duster, short curly permed grey-streaked hair).
S2 = JEN ONLY (SCREEN-RIGHT, solid black t-shirt, high ponytail).
Never exchange voices or dialogue.
Only the active speaker moves their lips.
The listener's mouth remains naturally closed."""

CAMERA = ("CAMERA: Stable medium two-shot at eye level, both women fully visible across the table, Mama screen-left, "
          "Jen screen-right. Static with very subtle handheld realism. No cuts, no camera moves, no one walks.")

def clip(locks, timed, extra, sound):
    return f"""integrated_multimodal_description: {ENV}

{CHARS}

{ACCENT}

PRONUNCIATION LOCK (silent):
{locks}

{RULES}

{timed}

{FINAL}
{extra}

{CAMERA}

overall_soundscape: {sound}

non_diegetic_music: N/A"""

C1 = clip(
"""- anák = a-NAK, stress on NAK
- magbuntís = mag-bun-TIS, stress on TIS
- A-te = AH-teh, spoken SLOWLY as two clearly separated syllables with a tiny break between them (A... te), Filipino vowels, NEVER a quick one-syllable "ate", NEVER "eight" or "Eyte"
- mabuntís = ma-bun-TIS, stress on TIS
- sabihin = sa-bi-HIN, stress on HIN""",
"""[0.0-0.3s] Start immediately mid-scene. Mama and Jen are ALREADY seated face to face at the table. No one walks in. No greeting.
[0.3-3.2s] MAMA (S1), calm and sincere, speaks the VERY FIRST LINE: <d>[Tagalog] Anák, pwede bang ikaw magbuntís para kay A-te?</d>
[3.3-5.0s] JEN (S2), frozen in disbelief: <d>[Tagalog] Ha? Anong ibig mong sabihin?</d>
[5.1-7.4s] MAMA (S1), matter-of-fact: <d>[Tagalog] Hindi kasi siya mabuntís.</d>
[7.4-8.0s] Mama holds her calm gaze on Jen.""",
"",
"Quiet Metro Manila home in the daytime, the soft whir of the electric fan, faint street sounds through the window. No narrator or voice-over. Only Mama and Jen speak.")

C2 = clip(
"""- tátay = TA-tay, stress on TA
- asáwa = a-SA-wa, stress on SA
- A-te = AH-teh, spoken SLOWLY as two clearly separated syllables with a tiny break between them (A... te), Filipino vowels, NEVER a quick one-syllable "ate", NEVER "eight" or "Eyte"
- Marvin = MAR-vin, an ordinary first name""",
"""[0.0-0.2s] Continue mid-scene with no pause or reset. Both still seated.
[0.2-2.2s] JEN (S2), cautious: <d>[Tagalog] Eh sino yung magiging tátay?</d>
[2.3-3.5s] MAMA (S1), completely calm: <d>[Tagalog] Si Marvin.</d>
[3.6-5.4s] JEN (S2), shocked: <d>[Tagalog] Asáwa ni A-te?!</d>
[5.5-6.9s] MAMA (S1), flat, as if it is obvious: <d>[Tagalog] Eh siyempre.</d>
[6.9-8.0s] Mama holds still, unbothered.""",
"",
"Same quiet home, soft electric fan whir. No narrator or voice-over. Only Mama and Jen speak.")

C3 = clip(
"""- IVF = spoken as the English letters "ai-vi-ef"
- mahál = ma-HAL, stress on HAL (meaning expensive)
- mabubuntís = ma-bu-bun-TIS, stress on TIS
- isáng = i-SANG, stress on SANG
- béses = BE-ses, stress on BE""",
"""[0.0-0.2s] Continue mid-scene with no pause or reset. Both still seated.
[0.2-1.8s] JEN (S2), slowly: <d>[Tagalog] So gusto niyo mag-IVF ako?</d>
[1.9-3.0s] MAMA (S1), dismissive, practical: <d>[Tagalog] Ang mahál nun.</d>
[3.1-4.6s] JEN (S2), stunned: <d>[Tagalog] Eh paano ako mabubuntís?</d>
[4.7-7.4s] MAMA (S1), calm and completely sincere, not as a joke: <d>[Tagalog] Natural na lang. Isáng béses lang naman.</d>
[7.4-8.0s] Hold on both faces in silence. HARD CUT at 8.0 seconds.""",
"""The person saying "Natural na lang. Isáng béses lang naman." MUST be MAMA: mid-50s, floral house duster, short curly permed grey-streaked hair, SCREEN-LEFT, S1. Jen does not speak after this line. Do not let Jen reply, cry or react aloud. Do not resolve it.""",
"Same quiet home, the electric fan, falling to near silence under Mama's final line. No narrator or voice-over. Only Mama and Jen speak.")

if __name__ == "__main__":
    import urllib.request
    items = [{"prompt": c, "frames": 192} for c in (C1, C2, C3)]
    for i, c in enumerate((C1, C2, C3), 1):
        open(f"text_clip{i}.prompt.txt", "w").write(c)
    body = {"items": items, "engine": "runpod", "refs": [],
            "params": {"width": 576, "height": 1024, "frames": 192, "steps": 6, "reuse": 2, "layers": 50,
                       "seed": 630002, "turbo": True}}
    r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:7833/api/sequence",
                               data=json.dumps(body).encode(), method="POST"))
    print(r.read().decode())
