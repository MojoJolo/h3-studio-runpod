"""Surrogate sister: 3 reference-mode clips with in-clip camera cuts.
Refs: Picture 1 = Mama, Picture 2 = Jen, Picture 3 = empty sala (location only)."""
import json, os

MAMA = ("MAMA, using <Picture 1> for her identity: a Filipina mother in her mid-50s, short permed black hair "
        "with visible grey streaks, round warm face with fine lines, slightly heavyset build, wearing a loose "
        "pastel floral house duster dress. Seated on SCREEN-LEFT. Speaker S1. Calm, sincere, completely "
        "unbothered, genuinely believes she is being practical.")
JEN = ("JEN, using <Picture 2> for her identity: a Filipina woman, age 26, long straight black hair in a high "
       "ponytail, slim athletic build, sharp defined features, wearing a plain fitted solid black t-shirt. "
       "Seated on SCREEN-RIGHT. Speaker S2. Increasingly stunned, controlled, not crying.")

LOCKS = """CRITICAL CHARACTER IDENTITY LOCK:
NEVER swap their faces, hairstyles, bodies, ages, wardrobe, screen positions, voices or dialogue. NEVER morph one character into the other. MAMA (mid-50s, permed grey-streaked short hair, floral duster) is ALWAYS SCREEN-LEFT. JEN (26, black high ponytail, solid black t-shirt) is ALWAYS SCREEN-RIGHT. They do not cross or exchange sides. Every camera angle stays on the same side of the two women, so Mama remains on the left of frame and Jen on the right in every shot. Maintain the same facial identity from first frame to last frame.

Both characters are native Metro Manila Filipino speakers.
They speak natural contemporary Tagalog/Taglish with authentic Metro Manila Filipino pronunciation.
Use clear Filipino vowels and natural Filipino rhythm.
Do NOT use an American, English, Spanish, or other foreign accent when speaking Tagalog.
Do NOT anglicize Filipino vowels.
Do NOT speak pronunciation instructions aloud.

PRONUNCIATION LOCK (silent):
{plocks}

CRITICAL AUDIO RULE:
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

CRITICAL VISUAL RULE:
Exactly two people are visible: Mama and Jen. Do NOT show another character. Ate and Marvin are mentioned only and remain OFF-SCREEN. No silhouettes, reflections or figures of a third person anywhere, including in the family photo on the shelf. Do NOT render any on-screen subtitles, captions, text overlays or watermarks of any kind. Natural restrained acting. Absurd situation played completely seriously. Do not exaggerate reactions. No teleserye acting."""

FINAL = """FINAL SPEAKER LOCK:
S1 = MAMA ONLY (SCREEN-LEFT, floral duster, permed grey-streaked hair).
S2 = JEN ONLY (SCREEN-RIGHT, black t-shirt, high ponytail).
Never exchange voices or dialogue. Only the active speaker moves her lips. The listener's mouth remains naturally closed."""

def clip(summary, retention_extra, plocks, shots, final_extra, soundscape):
    return f"""subject_definitions:
<Subject 1> is {MAMA}
<Subject 2> is {JEN}
<Picture 3> is the room: a modest Metro Manila living room in the daytime, small wooden dining table with two plastic monobloc chairs facing each other, a framed family photo and a small religious statue on a shelf, tiled floor, window with sheer curtains, natural daylight, electric fan in the corner. Location/composition anchor only — no characters appear in this picture.

summary:
[reference generation] {summary}

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the room's layout and lighting — do not add any person from this picture. {retention_extra}

detailed_description:
{LOCKS.format(plocks=plocks)}

{shots}

{FINAL}
{final_extra}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""

C1 = clip(
    "Mama calmly asks her daughter Jen to carry a pregnancy for her older sister.",
    "Exactly two people are visible in every shot of this clip: Mama and Jen.",
    "- anák = a-NAK, stress on NAK\n- magbuntís = mag-bun-TIS, stress on TIS\n- A-te = A-te, TWO syllables, Filipino vowels, NEVER \"eight\" or \"Eyte\"\n- magkaanák = mag-ka-a-NAK, stress on NAK",
    """[Shot 1] Wide two-shot at eye level. Start immediately mid-scene: Mama and Jen are ALREADY seated face to face at the small dining table, Mama on screen-left, Jen on screen-right. No one walks into frame. [0.3-3.0s] MAMA (S1), calm and sincere, speaks the VERY FIRST LINE: <d>[Tagalog] Anák, pwede bang ikaw magbuntís para kay A-te?</d>
[Shot 2] At 00:03.000, cut to a close-up on Jen (screen-right), her face frozen in disbelief. [3.1-4.6s] JEN (S2): <d>[Tagalog] Ha? Anong ibig mong sabihin?</d>
[Shot 3] At 00:04.800, cut to a medium close-up on Mama (screen-left), calm, matter-of-fact. [4.9-7.3s] MAMA (S1): <d>[Tagalog] Hindi kasi siya magkaanák.</d> [7.3-8.0s] Mama holds her calm gaze on Jen.""",
    "",
    "Quiet Metro Manila home in the daytime, the soft whir of the electric fan, faint street sounds through the window. No narrator or voice-over. Only Mama and Jen speak.")

C2 = clip(
    "Jen asks who the father would be, and Mama answers that it would be her sister's husband.",
    "Exactly two people are visible in every shot of this clip: Mama and Jen.",
    "- tátay = TA-tay, stress on TA\n- asáwa = a-SA-wa, stress on SA\n- A-te = A-te, TWO syllables, Filipino vowels, NEVER \"eight\" or \"Eyte\"\n- siyempre = si-YEM-pre",
    """[Shot 1] Continue mid-scene with no reset. Over-the-shoulder shot from behind Mama's shoulder (Mama's shoulder and back of her permed hair soft in the foreground screen-left) onto Jen's face screen-right. [0.2-2.0s] JEN (S2), cautious: <d>[Tagalog] Eh sino yung magiging tátay?</d>
[Shot 2] At 00:02.200, cut to a medium close-up on Mama (screen-left), completely calm. [2.3-3.4s] MAMA (S1): <d>[Tagalog] Si Marvin.</d>
[Shot 3] At 00:03.600, cut to a tight close-up on Jen (screen-right), shocked. [3.7-5.4s] JEN (S2): <d>[Tagalog] Asáwa ni A-te?!</d>
[Shot 4] At 00:05.600, cut back to a medium close-up on Mama (screen-left), flat, as if it is obvious. [5.7-7.0s] MAMA (S1): <d>[Tagalog] Eh siyempre.</d> [7.0-8.0s] Mama holds still, unbothered.""",
    "",
    "Same quiet home, soft electric fan whir. No narrator or voice-over. Only Mama and Jen speak.")

C3 = clip(
    "Jen asks if Mama means IVF; Mama says it is too expensive and suggests it happen naturally, just once.",
    "Exactly two people are visible in every shot of this clip: Mama and Jen.",
    "- buntís = bun-TIS, stress on TIS\n- mabubuntís = ma-bu-bun-TIS, stress on TIS\n- Isáng = i-SANG\n- besés = be-SES, stress on SES",
    """[Shot 1] Continue mid-scene with no reset. Medium two-shot, Mama screen-left, Jen screen-right, still seated at the table. [0.2-1.8s] JEN (S2), slowly: <d>[Tagalog] So gusto niyo mag-IVF ako?</d> [1.9-3.0s] MAMA (S1), dismissive, practical: <d>[Tagalog] Ang mahal nun.</d> [3.1-4.6s] JEN (S2), stunned: <d>[Tagalog] Eh paano ako mabubuntís?</d>
[Shot 2] At 00:04.700, cut to a close-up on Mama (screen-left), with a slow, small push-in. [4.8-7.4s] MAMA (S1), calm and completely sincere, not as a joke: <d>[Tagalog] Natural na lang. Isáng besés lang naman.</d> [7.4-8.0s] Hold on Mama's calm face. HARD CUT at 8.0 seconds.""",
    "The person saying \"Natural na lang. Isáng besés lang naman.\" MUST be MAMA: mid-50s, floral house duster, short permed grey-streaked hair, screen-left, S1. Jen does not speak after this line. Do not let Jen reply, cry or react aloud. Do not resolve it.",
    "Same quiet home, the electric fan, falling to near silence under Mama's final line. No narrator or voice-over. Only Mama and Jen speak.")

if __name__ == "__main__":
    out = os.path.dirname(os.path.abspath(__file__))
    for i, c in enumerate((C1, C2, C3), 1):
        open(os.path.join(out, f"clip{i}.prompt.txt"), "w").write(c)
    print("wrote 3 prompts", [len(c) for c in (C1, C2, C3)])
