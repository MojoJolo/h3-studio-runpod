import json
import urllib.request

LOCATION = ("inside a modest bedroom at night, warm lamp light, a small dresser "
            "and unmade bed visible, thin curtains over the window")

HEAD_TMPL = """integrated_multimodal_description: [Shot {n}] Photorealistic contemporary Filipino drama {location}. Natural restrained acting, realistic emotional tension, believable Filipino behavior.

There are exactly two visible adult characters.

<Subject 1> is TERESA, using the identity from <Picture 1>: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing a simple worn cotton house dress.

<Subject 2> is MARCO, using the identity from <Picture 2>: a 25-year-old handsome Filipino man, short dark hair, sharp jawline, wearing a plain white undershirt and pajama pants.

They are husband and wife, continuing the same argument from before, standing in the same spots in the room.

Both speak natural conversational Taglish.

CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Preserve all Tagalog pronouns and verb forms exactly.
Do NOT replace "mo" with "ko" or "ko" with "mo."
Do NOT alter verb aspect.
Do NOT paraphrase, normalize, or rewrite the dialogue.

IMPORTANT EYELINE LOCK:
Teresa and Marco face each other at a natural three-quarter angle. They speak directly to each other's faces. Neither character looks toward or acknowledges the camera.
"""

TAIL_TMPL = """

Speaker lock: Only TERESA speaks S1. Only MARCO speaks S2. Never swap dialogue, voices, lip movements, or eyelines.

Camera: {camera}

overall_soundscape: Quiet bedroom at night, a faint electric fan hum, distant dog barking outside. No narrator or voice-over. Only TERESA and MARCO speak.

non_diegetic_music: N/A"""

clips = [
    # (camera, blocking, first_speaker_block, second_speaker_block)
    (
        "Close two-shot favoring Marco, camera positioned just past Teresa's shoulder so he fills most of the frame, her shoulder and hair softly out of focus in the near foreground. Fixed camera, no movement.",
        "Marco's arms stay crossed, his expression flat and unbothered.",
        ("TERESA (S1)", "sharp, incredulous, speaks the VERY FIRST LINE immediately at the start of the clip", "So ako ang mali dito?"),
        ("MARCO (S2)", "shrugging slightly, genuinely believing he is being reasonable", "Hindi ko kasalanan na mas komportable ako sa kanya."),
    ),
    (
        "Reverse close two-shot favoring Teresa, camera positioned just past Marco's shoulder so her face fills most of the frame, his shoulder softly out of focus in the near foreground. Fixed camera, no movement.",
        "Teresa steps half a step closer, her voice rising with a pleading edge underneath.",
        ("TERESA (S1)", "firm, pleading edge underneath, speaks the VERY FIRST LINE immediately at the start of the clip", "Tapusin mo na 'to, Marco."),
        ("MARCO (S2)", "cold, final, not moving", "Hindi ko kailangan tapusin ang nagpapasaya sa akin."),
    ),
    (
        "Tight intimate two-shot, both faces close together in frame, camera at eye level directly between them at a slight angle. Fixed camera, no movement.",
        "Teresa's eyes well up but she holds herself together, her voice dropping to almost a whisper.",
        ("TERESA (S1)", "quiet, wounded, voice almost breaking, speaks the VERY FIRST LINE immediately at the start of the clip", "Kahit konting hiya, wala ka na?"),
        ("MARCO (S2)", "flat, looking her in the eye without flinching", "Hindi ako humihingi ng tawad."),
    ),
    (
        "Camera pulls back slightly to a medium two-shot, giving the moment room to breathe, both characters fully visible, fixed frame, no movement, held on the final beat.",
        "Marco holds her gaze, unflinching, delivering the final line without hesitation.",
        ("MARCO (S2)", "cold and final, delivered without hesitation, speaks the VERY FIRST LINE immediately at the start of the clip", "At hindi ko tinatapos 'to."),
        None,
    ),
]

items = []
for i, (camera, blocking, first, second) in enumerate(clips, start=4):
    body = HEAD_TMPL.format(n=i, location=LOCATION) + "\n" + blocking + "\n"
    label, delivery, line = first
    body += f"\n{label}, {delivery}: <d>[Tagalog] {line}</d>\n"
    if second:
        label2, delivery2, line2 = second
        body += f"\n{label2}, {delivery2}: <d>[Tagalog] {line2}</d>\n"
    else:
        body += "\nTeresa says nothing, her face frozen in stunned silence as the clip cuts abruptly.\n"
    body += TAIL_TMPL.format(camera=camera)
    items.append({"prompt": body, "frames": 192})

payload = {
    "items": items,
    "params": {
        "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
        "seed": 100201, "ssd_streaming": True,
    },
    "refs": ["teresa-ref.jpeg", "marco-ref.jpeg", "bedroom-ref.jpeg"],
    "engine": "h3",
}

req = urllib.request.Request(
    "http://127.0.0.1:7833/api/sequence",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req) as resp:
    print(resp.status, resp.read().decode())
