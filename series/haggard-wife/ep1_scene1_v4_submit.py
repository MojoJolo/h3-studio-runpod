import json
import urllib.request

SUBJECT_DEFS = """subject_definitions:
<Subject 1> is TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes. In this scene she wears a simple worn cotton house dress, standing in a modest bedroom at night.
<Subject 2> is MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, sharp jawline. In this scene he wears a plain white undershirt and pajama pants, standing in the same bedroom.
<Picture 3> is the bedroom set: plain cream walls, wall-mounted split-type AC unit, sheer white curtains, wooden dresser with mirror and warm bedside lamp, bed with floral-pattern sheets. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Only her clothing and expression change per shot.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Only his clothing and expression change per shot.
<Picture 3> is used only for the room's walls, furniture and lighting layout — do not add any character or person from this picture; only Subject 1 and Subject 2 are ever visible."""

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by Subject 1 (S1) and Subject 2 (S2). Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT replace "mo" with "ko" or "ko" with "mo." Do NOT alter verb aspect. Do NOT paraphrase, normalize, or rewrite the dialogue."""


def clip_prompt(n, summary, shots, soundscape):
    detailed = "\n\n".join(shots)
    return f"""{SUBJECT_DEFS}

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


clips_data = [
    dict(
        summary="Teresa confronts Marco with proof of the affair the moment he walks in; he doesn't deny it.",
        shots=[
            '[Shot 1] Wide establishing two-shot, fixed camera at a slight side angle, most of the bedroom visible — bed, dresser, window. Marco has just stepped inside the doorway on the right. Teresa stands near the bed on the left, holding a lit phone screen toward him. TERESA (S1), a woman with a low, trembling but controlled voice, speaks the VERY FIRST LINE: <d>[Tagalog] Sino si Selina?</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Marco, camera just past Teresa\'s shoulder so his face fills most of the frame. He does not step closer, arms crossed. MARCO (S2), a man with a calm, slightly irritated voice, replies: <d>[Tagalog] Kailangan pa ba nating pag-usapan \'to ngayon?</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum, distant dog barking outside. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Teresa presses for how long the affair has been going on; Marco answers flatly.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both characters visible, same positions as before. Teresa lowers the phone slightly, hand trembling. TERESA (S1), voice sharper, demanding, speaks the VERY FIRST LINE: <d>[Tagalog] Ilang buwan na ba kayo?</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Marco\'s face, camera just past Teresa\'s shoulder. MARCO (S2), flat, almost bored, replies: <d>[Tagalog] Anim na buwan.</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Teresa reacts in disbelief to the length of the deception; Marco is unbothered and dismissive.",
        shots=[
            '[Shot 1] Close-up favoring Teresa, camera just past Marco\'s shoulder so her face fills most of the frame. Her breath catches, she takes one step back as if struck. TERESA (S1), voice breaking, speaks the VERY FIRST LINE: <d>[Tagalog] Anim na buwan mo akong niloloko?</d>',
            '[Shot 2] At 00:04.000, cut to a medium two-shot, fixed camera, both visible. MARCO (S2), unbothered, matter-of-fact, replies: <d>[Tagalog] Hindi kita niloloko. Alam mo na, ayaw mo lang tanggapin.</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Teresa's hurt turns to anger; Marco shamelessly justifies himself as the reasonable one.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera. Teresa\'s jaw tightens, disbelief turning to anger. TERESA (S1), sharp, incredulous, speaks the VERY FIRST LINE: <d>[Tagalog] So ako ang mali dito?</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Marco, camera just past Teresa\'s shoulder. He shrugs slightly, genuinely believing he is reasonable. MARCO (S2) replies: <d>[Tagalog] Hindi ko kasalanan na mas komportable ako sa kanya.</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Teresa pleads for him to end the affair; Marco coldly refuses.",
        shots=[
            '[Shot 1] Close-up favoring Teresa, camera just past Marco\'s shoulder. She steps half a step closer, voice rising with a pleading edge underneath. TERESA (S1), firm, pleading, speaks the VERY FIRST LINE: <d>[Tagalog] Tapusin mo na \'to, Marco.</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Marco, camera just past Teresa\'s shoulder. Cold, final, not moving. MARCO (S2) replies: <d>[Tagalog] Hindi ko kailangan tapusin ang nagpapasaya sa akin.</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Teresa, wounded and quiet, asks if he has any shame left; Marco flatly says he isn't sorry.",
        shots=[
            '[Shot 1] Tight intimate two-shot, both faces close together in frame, camera at eye level between them at a slight angle. Teresa\'s eyes well up but she holds herself together. TERESA (S1), quiet, wounded, voice almost breaking, speaks the VERY FIRST LINE: <d>[Tagalog] Kahit konting hiya, wala ka na?</d>',
            '[Shot 2] At 00:04.000, holding the same tight intimate two-shot, no cut in camera position, only his expression changes. MARCO (S2), flat, looking her in the eye without flinching, replies: <d>[Tagalog] Hindi ako humihingi ng tawad.</d>',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum. Only TERESA and MARCO speak.",
    ),
    dict(
        summary="Marco delivers the final cold line; Teresa is left in stunned silence as the scene cuts to black.",
        shots=[
            '[Shot 1] Camera pulls back to a wide two-shot, mirroring the opening shot of the scene, giving the moment room to breathe. Marco holds Teresa\'s gaze, unflinching. MARCO (S2), cold and final, delivered without hesitation, speaks the VERY FIRST LINE: <d>[Tagalog] At hindi ko tinatapos \'to.</d>',
            '[Shot 2] At 00:05.000, cut to a close-up on Teresa\'s face, camera just past Marco\'s shoulder. She says nothing, her face frozen in stunned silence. Hard cut to black at the end of the shot.',
        ],
        soundscape="Quiet bedroom at night, a faint electric fan hum, then dead silence before the cut. Only MARCO speaks in this clip.",
    ),
]

def build_items():
    items = []
    for i, c in enumerate(clips_data, start=1):
        prompt = clip_prompt(i, c["summary"], c["shots"], c["soundscape"])
        items.append({"prompt": prompt, "frames": 192})
    return items


PARAMS = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "seed": 100501, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "marco-ref.jpeg", "bedroom-ref.jpeg"]


if __name__ == "__main__":
    payload = {"items": build_items(), "params": PARAMS, "refs": REFS, "engine": "h3"}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/sequence",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
