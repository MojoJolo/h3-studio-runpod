"""Episode 1, Scene 2: 'The Reason'. Continues directly from Scene 1's
cliffhanger, same night, same bedroom. Teresa demands why; Marco's shameless
justification is that Selina funds the life he wants and never makes him
feel small about money. Ends on Marco telling her to pack her things.

Lessons applied from Scene 1:
- Exact clothing spelled out in EVERY clip's subject_definitions (clip 5's
  outfit drift lesson), not just described once.
- Explicit "no third person/hand/limb" line in retention_analysis (clip 4's
  phantom-hand lesson).
- Independent /api/generate submissions per clip with ONLY the 3 fixed
  standing refs, never /api/sequence (compounding-degradation lesson).
- Variable clip duration per beat (this scene's rule, starting Scene 2).
"""
import json
import time
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing a simple worn cream cotton house dress with short sleeves"
MARCO_LOOK = "MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, sharp jawline, wearing a plain white ribbed crew-neck undershirt with short fitted sleeves and grey pajama pants"

def subject_defs():
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing in a modest bedroom at night.
<Subject 2> is {MARCO_LOOK}, standing in the same bedroom.
<Picture 3> is the bedroom set: plain cream walls, wall-mounted split-type AC unit, sheer white curtains, wooden dresser with mirror and warm bedside lamp, bed with floral-pattern sheets. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing and expression as specified above, only expression changes per shot.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing and expression as specified above, only expression changes per shot.
<Picture 3> is used only for the room's walls, furniture and lighting layout — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Teresa and Marco. No third person, hand, arm, or limb of any kind anywhere in frame."""

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by Subject 1 (S1) and Subject 2 (S2). Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT replace "mo" with "ko" or "ko" with "mo." Do NOT alter verb aspect. Do NOT paraphrase, normalize, or rewrite the dialogue."""


def clip_prompt(summary, shots, soundscape):
    detailed = "\n\n".join(shots)
    return f"""{subject_defs()}

summary:
[reference generation] {summary}

{RETENTION}

detailed_description:
{AUDIO_RULES}

{detailed}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


AMBIENCE = "Quiet bedroom at night, a faint electric fan hum."

clips_data = [
    dict(
        frames=124,  # ~5.2s, quick exchange
        summary="Teresa demands to know why, after everything, he's choosing this.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both fully visible. Teresa stands firm, arms tense at her sides. TERESA (S1), raw and direct, speaks the VERY FIRST LINE: <d>[Tagalog] Bakit, Marco? Kailangan kong malaman.</d> Marco looks away toward the window before answering. MARCO (S2), quiet, almost reluctant, replies: <d>[Tagalog] Sigurado ka bang gusto mong malaman?</d>',
        ],
        soundscape=f"{AMBIENCE} Only TERESA and MARCO speak.",
    ),
    dict(
        frames=141,  # ~5.9s
        summary="Marco starts to explain himself, calm and matter-of-fact.",
        shots=[
            '[Shot 1] Close-up favoring Marco, camera just past Teresa\'s shoulder. He exhales slowly, like he\'s rehearsed the words. MARCO (S2), calm, unflinching, speaks the VERY FIRST LINE: <d>[Tagalog] Kasi sa kanya, hindi ako kailangan magpaliwanag kung bakit ako gumagastos.</d> Teresa\'s jaw tightens just off-frame at the edge of shot, visible slightly.',
        ],
        soundscape=f"{AMBIENCE} Only MARCO speaks in this clip.",
    ),
    dict(
        frames=175,  # ~7.3s, 2-shot cut
        summary="Marco reveals the real reason is money and comfort; Teresa realizes she's being compared.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both fully visible. Marco stands with his arms loosely crossed, at ease. MARCO (S2), plain, without shame, speaks the VERY FIRST LINE: <d>[Tagalog] Binibigyan niya ako ng buhay na gusto ko. Hindi tulad ng buhay na kaya mong ibigay.</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Teresa\'s face, camera just past Marco\'s shoulder. Her expression shifts from disbelief to something colder. TERESA (S1), flat, stunned, replies: <d>[Tagalog] Pera pala talaga ang dahilan.</d>',
        ],
        soundscape=f"{AMBIENCE} Only MARCO and TERESA speak.",
    ),
    dict(
        frames=158,  # ~6.6s
        summary="Teresa's hurt turns to anger over years of sacrifice; Marco stays unbothered.",
        shots=[
            '[Shot 1] Tight intimate two-shot, both faces close together in frame, camera at eye level between them. Teresa\'s voice rises, hurt turning sharp. TERESA (S1), bitter, speaks the VERY FIRST LINE: <d>[Tagalog] Pinagtiisan kong mabuhay ng simple, ganito na lang pala ang halaga ko sa\'yo?</d> Marco shrugs slightly, meeting her eyes without flinching. MARCO (S2), even, replies: <d>[Tagalog] Hindi kasalanan na gusto kong maging komportable.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TERESA and MARCO speak.",
    ),
    dict(
        frames=158,  # ~6.6s
        summary="Teresa asks what happens to them now; Marco's tone turns cold and final.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both fully visible. Teresa\'s voice drops, almost pleading despite herself. TERESA (S1), quiet, speaks the VERY FIRST LINE: <d>[Tagalog] So ano na ngayon? Ano nangyari sa amin?</d> Marco\'s expression hardens, all warmth gone. MARCO (S2), cold, replies: <d>[Tagalog] Wala nang \'amin,\' Teresa.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TERESA and MARCO speak.",
    ),
    dict(
        frames=175,  # ~7.3s, cliffhanger with cut
        summary="Marco delivers the ultimatum; Teresa is left frozen as the scene cuts hard.",
        shots=[
            '[Shot 1] Wide two-shot, fixed camera, mirroring the scene\'s opening framing. Marco takes one step back, already turning slightly away, done with the conversation. MARCO (S2), cold and decided, delivered without hesitation, speaks the VERY FIRST LINE: <d>[Tagalog] Simpakan mo na ang mga gamit mo. Desidido na ako.</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Teresa\'s face, camera just past Marco\'s shoulder. She says nothing, frozen, eyes wide with disbelief. Hard cut to black at the end of the shot.',
        ],
        soundscape=f"{AMBIENCE} Only MARCO speaks in this clip.",
    ),
]

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "marco-ref.jpeg", "bedroom-ref.jpeg"]
BASE_SEED = 100511


def submit(prompt, frames, seed):
    payload = {
        "prompt": prompt,
        "mode": "refs",
        "engine": "h3",
        "params": dict(PARAMS_BASE, frames=frames, seed=seed),
        "refs": REFS,
    }
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    results = []
    for i, c in enumerate(clips_data):
        seed = BASE_SEED + i
        prompt = clip_prompt(c["summary"], c["shots"], c["soundscape"])
        r = submit(prompt, c["frames"], seed)
        print(f"clip {i+1} (seed {seed}, frames {c['frames']}): {r}")
        results.append(r)
        time.sleep(0.5)
    print(json.dumps(results, indent=2))
