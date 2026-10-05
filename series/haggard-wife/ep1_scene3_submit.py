"""Episode 1, Scene 3: 'Not Who You Think'. Teresa leaves Marco with nothing
but her composure, arrives at what looks like a modest gate, and is met with
unexpected deference. Ends on a one-sided phone call: we only hear her side,
avoiding an invisible third speaker (established lesson from the POV skill —
no off-screen/unseen voice ever gets a <d> line). She stays in her plain
house dress throughout this scene on purpose — the wealth reveal lands
through how she's TREATED, not a wardrobe change yet.

New refs introduced for this scene:
- inputs/gate-ref.jpeg (location, standalone <Picture>, no characters)
- inputs/staff-ref.jpeg (Staff character, new <Subject>)
Teresa's ref (inputs/teresa-ref.jpeg) carries over.
"""
import json
import time
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, still wearing the same simple worn cream cotton house dress with short sleeves she left in, carrying nothing"
STAFF_LOOK = "a composed household staff member, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue."""


def clip_gate(summary, shots, soundscape):
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, standing just outside a gate at dusk.
<Subject 2> is TATAY LINO, {STAFF_LOOK}, standing just inside the gate.
<Picture 3> is the gate set: plain grey concrete perimeter wall, simple steel gate, a single warm porch light, dusk sky. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] {summary}

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the gate/wall/lighting layout — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Teresa and Tatay Lino. No third person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
{AUDIO_RULES}

{chr(10).join(shots)}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


def clip_solo_teresa(summary, shots, soundscape, location_note):
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK.replace('still wearing', 'now indoors, wearing')}, alone in a quiet, well-kept but understated room.
<Picture 2> is the room: {location_note} Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] {summary}

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly one person is visible in every shot of this clip: Teresa alone. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
{AUDIO_RULES}
Teresa is on a phone call. The caller's voice is NOT rendered as audible dialogue — we only see Teresa's side: her listening, her expression shifting, and her own spoken lines. Do not write any dialogue for the caller.

{chr(10).join(shots)}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


AMBIENCE_OUT = "Quiet residential street at dusk, distant crickets starting, a soft breeze."
AMBIENCE_IN = "Quiet, well-kept interior room, a soft ambient hum, distant faint clink of dishware somewhere in the house."

REFS_GATE = ["teresa-ref.jpeg", "staff-ref.jpeg", "gate-ref.jpeg"]
REFS_SOLO = ["teresa-ref.jpeg", "sala-ref.jpeg"]  # sala-ref generated separately below

clips_data = [
    dict(
        frames=158,  # ~6.6s
        refs=REFS_GATE,
        prompt=clip_gate(
            "Teresa arrives on foot at a plain, modest-looking gate; the staff member waiting there greets her with immediate, genuine deference.",
            [
                '[Shot 1] Medium two-shot at the gate, fixed camera, Teresa on the street side, Tatay Lino just inside having opened the gate for her. He bows his head slightly, voice warm and relieved. TATAY LINO (S2), gentle, deeply respectful, speaks the VERY FIRST LINE: <d>[Tagalog] Salamat sa Diyos, nakauwi na po kayo.</d> Teresa gives a small, tired, grateful nod, stepping through the gate. TERESA (S1), quiet, replies: <d>[Tagalog] Salamat, Tatay Lino.</d>',
            ],
            f"{AMBIENCE_OUT} Only TATAY LINO and TERESA speak.",
        ),
    ),
    dict(
        frames=141,  # ~5.9s
        refs=REFS_GATE,
        prompt=clip_gate(
            "Tatay Lino reveals that people inside have been waiting for her, deepening the mystery of why a modest place shows her this much respect.",
            [
                '[Shot 1] Medium two-shot, now just inside the gate, small covered walkway visible behind them. Tatay Lino gestures gently toward the house, tone careful and formal. TATAY LINO (S2), speaks the VERY FIRST LINE: <d>[Tagalog] Hinihintay na po kayo sa loob.</d> Teresa pauses mid-step, a flicker of quiet resolve crossing her tired face, but she says nothing, simply walking forward.',
            ],
            f"{AMBIENCE_OUT} Only TATAY LINO speaks in this clip.",
        ),
    ),
    dict(
        frames=192,  # ~8.0s, cliffhanger with cut, solo Teresa
        refs=REFS_SOLO,
        prompt=clip_solo_teresa(
            "Alone in a quiet room, Teresa takes a phone call; whoever it is addresses her with real weight, and she responds with a composed, quietly commanding line.",
            [
                '[Shot 1] Medium shot, fixed camera, Teresa standing alone by a window, phone held to her ear, listening, her tired expression slowly shifting into something more composed and controlled.',
                "[Shot 2] At 00:04.000, cut to a close-up on Teresa's face, phone still at her ear. She closes her eyes briefly, then opens them, calm and resolute. TERESA (S1), quiet but carrying unmistakable authority, speaks the VERY FIRST LINE: <d>[Tagalog] Hayaan mo silang maging masaya. Sa ngayon.</d> She lowers the phone slowly, her expression unreadable. Hard cut to black.",
            ],
            "Quiet room tone, a faint clock ticking somewhere, a soft breath as she lowers the phone. Only TERESA speaks.",
            "plain cream walls, simple wooden furniture, a large window with soft warm light, tasteful but modest decor.",
        ),
    ),
]

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}
BASE_SEED = 100601


def submit(prompt, frames, seed, refs):
    payload = {
        "prompt": prompt,
        "mode": "refs",
        "engine": "h3",
        "params": dict(PARAMS_BASE, frames=frames, seed=seed),
        "refs": refs,
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
        r = submit(c["prompt"], c["frames"], seed, c["refs"])
        print(f"clip {i+1} (seed {seed}, frames {c['frames']}): {r}")
        time.sleep(0.5)
