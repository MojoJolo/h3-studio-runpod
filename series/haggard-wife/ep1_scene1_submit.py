import json
import urllib.request

LOCATION = ("inside a modest bedroom at night, warm lamp light, a small dresser "
            "and unmade bed visible")

COMMON_HEAD = f"""integrated_multimodal_description: [Shot {{n}}] Photorealistic contemporary Filipino drama {LOCATION}. Natural restrained acting, realistic emotional tension, believable Filipino behavior.

There are exactly two visible adult characters.

<Subject 1> is TERESA, using the identity from <Picture 1>: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing a simple worn cotton house dress.

<Subject 2> is MARCO, using the identity from <Picture 2>: a 25-year-old handsome Filipino man, short dark hair, sharp jawline, wearing a plain white undershirt and pajama pants.

They are husband and wife.

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

The camera holds a continuous static medium two-shot.
"""

COMMON_TAIL = """

Speaker lock: Only TERESA speaks S1. Only MARCO speaks S2. Never swap dialogue, voices, lip movements, or eyelines.

Camera: Single continuous medium two-shot from a slight side angle. No cuts.

overall_soundscape: Quiet bedroom at night, a faint electric fan hum, distant dog barking outside. No narrator or voice-over. Only TERESA and MARCO speak.

non_diegetic_music: N/A"""

clips = [
    # (blocking, teresa_delivery, teresa_line, marco_delivery, marco_line)
    (
        "Teresa stands near the bed holding a lit phone screen toward Marco, who has just stopped near the doorway, arms crossed.",
        "a woman with a low, trembling but controlled voice, speaks the VERY FIRST LINE immediately at the start of the clip",
        "Sino si Selina?",
        "a man with a calm, slightly irritated voice, not stepping closer",
        "Kailangan pa ba nating pag-usapan 'to ngayon?",
    ),
    (
        "Teresa lowers the phone slightly, her hand trembling, still staring at him.",
        "voice sharper now, demanding",
        "Ilang buwan na ba kayo?",
        "flat, almost bored",
        "Anim na buwan.",
    ),
    (
        "Teresa's breath catches; she takes one step back as if struck.",
        "voice breaking",
        "Anim na buwan mo akong niloloko?",
        "unbothered, matter-of-fact",
        "Hindi kita niloloko. Alam mo na, ayaw mo lang tanggapin.",
    ),
    (
        "Teresa's jaw tightens, disbelief turning to anger.",
        "sharp, incredulous",
        "So ako ang mali dito?",
        "shrugging slightly, genuinely believing he is reasonable",
        "Hindi ko kasalanan na mas komportable ako sa kanya.",
    ),
    (
        "Teresa steps closer, voice rising.",
        "firm, pleading edge underneath",
        "Tapusin mo na 'to, Marco.",
        "cold, final",
        "Hindi ko kailangan tapusin ang nagpapasaya sa akin.",
    ),
    (
        "Teresa's eyes well up but she holds herself together, voice dropping to almost a whisper.",
        "quiet, wounded",
        "Kahit konting hiya, wala ka na?",
        "flat, looking her in the eye without flinching",
        "Hindi ako humihingi ng tawad.",
    ),
    (
        "Marco holds her gaze, unflinching. Teresa says nothing, her face frozen in stunned silence as the clip cuts abruptly.",
        "cold and final, delivered without hesitation",
        None,
        "cold and final, delivered without hesitation",
        "At hindi ko tinatapos 'to.",
    ),
]

items = []
for i, (blocking, t_delivery, t_line, m_delivery, m_line) in enumerate(clips, start=1):
    body = COMMON_HEAD.format(n=i) + "\n" + blocking + "\n"
    if i == 1:
        body += (
            f"\nTERESA (S1), {t_delivery}: <d>[Tagalog] {t_line}</d>\n"
            f"\nMARCO (S2), {m_delivery}: <d>[Tagalog] {m_line}</d>\n"
        )
    elif i == len(clips):
        body += (
            f"\nMARCO (S2), {m_delivery}, speaks the VERY FIRST LINE immediately at the start of the clip: <d>[Tagalog] {m_line}</d>\n"
        )
    else:
        body += (
            f"\nTERESA (S1), {t_delivery}, speaks the VERY FIRST LINE immediately at the start of the clip: <d>[Tagalog] {t_line}</d>\n"
            f"\nMARCO (S2), {m_delivery}: <d>[Tagalog] {m_line}</d>\n"
        )
    body += COMMON_TAIL
    items.append({"prompt": body, "frames": 192})

payload = {
    "items": items,
    "params": {
        "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
        "seed": 100101, "ssd_streaming": True,
    },
    "refs": ["teresa-ref.jpeg", "marco-ref.jpeg"],
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
