"""Corrected resubmission of Scene 2 clips 5 and 6 (jobs 630/631 cancelled):
- 'amin' (exclusive we/us) -> 'atin' (inclusive we/us) since both lines refer
  to Teresa and Marco together, not excluding the listener.
- 'Simpakan' (not a real Tagalog word, an error) -> 'Impake' (pack).
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
        frames=158,  # ~6.6s
        summary="Teresa asks what happens to them now; Marco's tone turns cold and final.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both fully visible. Teresa\'s voice drops, almost pleading despite herself. TERESA (S1), quiet, speaks the VERY FIRST LINE: <d>[Tagalog] So ano na ngayon? Ano nangyari sa atin?</d> Marco\'s expression hardens, all warmth gone. MARCO (S2), cold, replies: <d>[Tagalog] Wala nang atin, Teresa.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TERESA and MARCO speak.",
    ),
    dict(
        frames=175,  # ~7.3s, cliffhanger with cut
        summary="Marco delivers the ultimatum; Teresa is left frozen as the scene cuts hard.",
        shots=[
            '[Shot 1] Wide two-shot, fixed camera, mirroring the scene\'s opening framing. Marco takes one step back, already turning slightly away, done with the conversation. MARCO (S2), cold and decided, delivered without hesitation, speaks the VERY FIRST LINE: <d>[Tagalog] Kunin mo na ang mga gamit mo. Desidido na ako.</d>',
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
BASE_SEED = 100517


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
    for i, c in enumerate(clips_data):
        seed = BASE_SEED + i
        prompt = clip_prompt(c["summary"], c["shots"], c["soundscape"])
        r = submit(prompt, c["frames"], seed)
        print(f"clip {i+5} (seed {seed}, frames {c['frames']}): {r}")
        time.sleep(0.5)
