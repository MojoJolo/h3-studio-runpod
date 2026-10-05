"""3rd attempt at Scene 3 clips 1-2. Root cause identified: staging a
"stepping through/opening the gate" transition gave the model an ambiguous
crossing direction (rendered as exiting, twice, despite explicit "entering"
language) AND an implied "gate operator" action that it duplicated into a
second Tatay Lino (twice, across two seeds/framings).

Fix: skip the gate-crossing moment entirely. Both clips are staged just
inside the property, gate already closed behind them, both facing TOWARD
the house (away from the gate) — no crossing action, no gate-operating
action, nothing for the model to get backward or duplicate.
"""
import json
import time
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, still wearing the same simple worn cream cotton house dress with short sleeves she left in, carrying nothing"
STAFF_LOOK = "a composed household staff member, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"

def subject_defs():
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing in the walkway just inside the property, facing toward the house.
<Subject 2> is TATAY LINO, {STAFF_LOOK}, standing beside her in the same walkway, also facing toward the house. There is no security guard, no watchman, no second household staff member, and no one else employed at this house anywhere in this clip. Tatay Lino is the sole staff member on the entire property.
<Picture 3> is the property walkway: a plain covered concrete walkway leading to the house's front door, warm porch light, the closed gate and perimeter wall visible only far behind them in the background, dusk sky. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the walkway/wall/lighting layout — do not add any character or person from this picture. EXACTLY TWO PEOPLE total appear anywhere in this clip, in every single frame: Teresa and Tatay Lino, and no one else. Do not duplicate, clone, or generate a second version of either subject. No third person, no security guard, no watchman, no bystander, no extra hand, arm, or limb of any kind anywhere in frame, at any timestamp. Neither character opens, closes, or touches the gate in this clip — the gate is already shut, far in the background, not part of the action."""

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue."""


def clip_prompt(summary, shots, soundscape):
    return f"""{subject_defs()}

summary:
[reference generation] {summary}

{RETENTION}

detailed_description:
{AUDIO_RULES}

{chr(10).join(shots)}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


AMBIENCE = "Quiet residential property at dusk, distant crickets starting, a soft breeze, far-off street sounds beyond the wall."

clips_data = [
    dict(
        frames=141,  # ~5.9s
        summary="Already inside the property, walking toward the house, Tatay Lino greets Teresa home with immediate, genuine deference.",
        shots=[
            '[Shot 1] Tight close two-shot, fixed camera positioned ahead of them near the house, both faces filling most of the frame as they walk slowly toward camera along the walkway. Tatay Lino glances at her, voice warm and relieved. TATAY LINO (S2), gentle, deeply respectful, speaks the VERY FIRST LINE: <d>[Tagalog] Salamat sa Diyos, nakauwi na po kayo.</d> Teresa gives a small, tired, grateful nod without breaking stride. TERESA (S1), quiet, replies: <d>[Tagalog] Salamat, Tatay Lino.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TATAY LINO and TERESA speak.",
    ),
    dict(
        frames=141,  # ~5.9s
        summary="Tatay Lino reveals that people inside have been waiting for her, deepening the mystery of why a modest place shows her this much respect.",
        shots=[
            '[Shot 1] Tight close two-shot, fixed camera positioned ahead of them near the house, both faces filling most of the frame as they continue walking slowly toward camera along the walkway, now closer to the front door. Tatay Lino gestures gently toward the house ahead, tone careful and formal. TATAY LINO (S2), speaks the VERY FIRST LINE: <d>[Tagalog] Hinihintay na po kayo sa loob.</d> Teresa pauses mid-step, a flicker of quiet resolve crossing her tired face, but she says nothing, simply continuing forward.',
        ],
        soundscape=f"{AMBIENCE} Only TATAY LINO speaks in this clip.",
    ),
]

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "staff-ref.jpeg", "gate-ref.jpeg"]
BASE_SEED = 100630


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
        print(f"clip {i+1} (seed {seed}, frames {c['frames']}): {r}")
        time.sleep(0.5)
