import json
import urllib.request

LOCATION = ("inside a modest bedroom at night, warm lamp light, a small dresser "
            "and unmade bed visible")

HEAD_TMPL = """integrated_multimodal_description: [Shot {n}] Photorealistic contemporary Filipino drama {location}. Natural restrained acting, realistic emotional tension, believable Filipino behavior.

There are exactly two visible adult characters.

<Subject 1> is TERESA, using the identity from <Picture 1>: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing a simple worn cotton house dress.

<Subject 2> is MARCO, using the identity from <Picture 2>: a 25-year-old handsome Filipino man, short dark hair, sharp jawline, wearing a plain white undershirt and pajama pants.

<Picture 3> shows the empty bedroom set only — no characters in it — use it only for the room's walls, furniture, and lighting.

They are husband and wife, continuing the same argument, standing in the same room.

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
    (
        "WIDE ESTABLISHING TWO-SHOT. Fixed camera at a slight side angle, far enough back to show most of the room — the bed, dresser, and window all visible. Teresa stands near the bed holding a lit phone screen toward Marco, who has just stopped near the doorway, arms crossed.",
        "a woman with a low, trembling but controlled voice, speaks the VERY FIRST LINE immediately at the start of the clip",
        "Sino si Selina?",
        "a man with a calm, slightly irritated voice, not stepping closer",
        "Kailangan pa ba nating pag-usapan 'to ngayon?",
    ),
    (
        "MEDIUM TWO-SHOT, noticeably closer than a wide shot but both characters still fully in frame. Fixed camera, slight side angle. Teresa lowers the phone slightly, her hand trembling, still staring at him.",
        "voice sharper now, demanding",
        "Ilang buwan na ba kayo?",
        "flat, almost bored",
        "Anim na buwan.",
    ),
    (
        "CLOSE-UP FAVORING TERESA. Camera positioned just past Marco's shoulder so her face and upper body fill most of the frame, his shoulder and arm softly out of focus in the near foreground. Fixed camera, no movement. Teresa's breath catches; she takes one step back as if struck.",
        "voice breaking",
        "Anim na buwan mo akong niloloko?",
        "unbothered, matter-of-fact",
        "Hindi kita niloloko. Alam mo na, ayaw mo lang tanggapin.",
    ),
    (
        "CLOSE-UP FAVORING MARCO. Camera positioned just past Teresa's shoulder so his face and upper body fill most of the frame, her shoulder and hair softly out of focus in the near foreground. Fixed camera, no movement. Teresa's jaw tightens, disbelief turning to anger.",
        "sharp, incredulous",
        "So ako ang mali dito?",
        "shrugging slightly, genuinely believing he is reasonable",
        "Hindi ko kasalanan na mas komportable ako sa kanya.",
    ),
    (
        "REVERSE CLOSE-UP FAVORING TERESA, camera on the opposite side from the previous shot, past Marco's shoulder toward her face. Fixed camera, no movement. Teresa steps half a step closer, voice rising with a pleading edge underneath.",
        "firm, pleading edge underneath",
        "Tapusin mo na 'to, Marco.",
        "cold, final",
        "Hindi ko kailangan tapusin ang nagpapasaya sa akin.",
    ),
    (
        "TIGHT INTIMATE TWO-SHOT, both faces close together in frame, camera at eye level directly between them at a slight angle, noticeably tighter framing than any previous shot. Fixed camera, no movement. Teresa's eyes well up but she holds herself together, voice dropping to almost a whisper.",
        "quiet, wounded, voice almost breaking",
        "Kahit konting hiya, wala ka na?",
        "flat, looking her in the eye without flinching",
        "Hindi ako humihingi ng tawad.",
    ),
    (
        "CAMERA PULLS BACK to a wide two-shot again, mirroring the opening shot of the scene, giving the final beat room to breathe. Fixed camera, no movement, held on the final beat. Marco holds her gaze, unflinching, delivering the final line without hesitation.",
        "cold and final, delivered without hesitation",
        None,
        "cold and final, delivered without hesitation",
        "At hindi ko tinatapos 'to.",
    ),
]

items = []
for i, (camera_and_blocking, t_delivery, t_line, m_delivery, m_line) in enumerate(clips, start=1):
    body = HEAD_TMPL.format(n=i, location=LOCATION) + "\n" + camera_and_blocking + "\n"
    if i == 1:
        body += (
            f"\nTERESA (S1), {t_delivery}: <d>[Tagalog] {t_line}</d>\n"
            f"\nMARCO (S2), {m_delivery}: <d>[Tagalog] {m_line}</d>\n"
        )
    elif t_line is None:
        body += (
            f"\nMARCO (S2), {m_delivery}, speaks the VERY FIRST LINE immediately at the start of the clip: <d>[Tagalog] {m_line}</d>\n"
            "\nTeresa says nothing, her face frozen in stunned silence as the clip cuts abruptly.\n"
        )
    else:
        body += (
            f"\nTERESA (S1), {t_delivery}, speaks the VERY FIRST LINE immediately at the start of the clip: <d>[Tagalog] {t_line}</d>\n"
            f"\nMARCO (S2), {m_delivery}: <d>[Tagalog] {m_line}</d>\n"
        )
    # camera direction line pulled from the first sentence of camera_and_blocking (in caps)
    camera_line = camera_and_blocking.split(". ", 1)[0] + ". Single shot, no cuts."
    body += TAIL_TMPL.format(camera=camera_line)
    items.append({"prompt": body, "frames": 192})

payload = {
    "items": items,
    "params": {
        "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
        "seed": 100401, "ssd_streaming": True,
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
