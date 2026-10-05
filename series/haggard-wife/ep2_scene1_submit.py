"""Episode 2, Scene 1: 'Flaunting It'. Marco and Selina in their upgraded
condo — this scene's real job is giving Marco's choice of Selina genuine
emotional texture (per Ep1 audience feedback): she makes him feel chosen,
admired, unburdened, not just funded. Ends on Selina dismissing Teresa's
family as 'nobodies,' with a flicker of something unreadable in Marco's
reaction rather than easy agreement (foreshadowing the reckoning).

Only 2 established characters (Marco, Selina), both already have refs
from Episode 1 — no new character risk. Location: condo (new this episode).
"""
import json
import time
import urllib.request

SELINA_LOOK = "SELINA, using <Picture 1> for her identity: a 42-year-old striking, confident Filipina woman, glossy dark wavy hair, bold red lipstick, refined makeup, wearing an elegant emerald green silk robe-style loungewear with gold jewelry, poised and composed"
MARCO_LOOK = "MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, clean-shaven sharp jawline, wearing an open dark navy silk shirt, a flashy gold watch on his wrist, confident easy smile"

def subject_defs():
    return f"""subject_definitions:
<Subject 1> is {SELINA_LOOK}, in the condo living room.
<Subject 2> is {MARCO_LOOK}, in the same condo living room.
<Picture 3> is the condo living room: floor-to-ceiling windows with a glittering city skyline view at night, curved white sofa, crystal pendant light, marble accent wall, expensive minimalist decor. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Selina and Marco, and no one else."""

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


AMBIENCE = "A quiet, expensive-feeling condo interior at night, faint distant city hum through the glass."

clips_data = [
    dict(
        frames=158,  # ~6.6s
        summary="Marco admires an expensive new watch Selina just gave him; she makes him feel chosen and unburdened, not funded.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, both seated close together on the curved sofa, the city skyline glittering behind them. Marco turns his wrist, admiring a gold watch, genuinely delighted. MARCO (S2), warm, almost boyish, speaks the VERY FIRST LINE: <d>[Tagalog] Selina... hindi ko akalaing bibigyan mo pa ako nito.</d> Selina leans in, adjusting his collar with a soft, confident smile. SELINA (S1), warm and possessive, replies: <d>[Tagalog] Dahil karapat-dapat ka rito. Gusto kong pakiramdam mo, hari ka — hindi parang pasanin.</d>',
        ],
        soundscape=f"{AMBIENCE} Soft rustle of fabric as Selina leans in. Only SELINA and MARCO speak.",
    ),
    dict(
        frames=141,  # ~5.9s
        summary="Selina's phone lights up with gossip about Teresa's rough new circumstances; she and Marco mock it together.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, Selina glancing down at her phone screen (screen not visible to camera), a slow smirk spreading. SELINA (S1), amused, speaks the VERY FIRST LINE: <d>[Tagalog] Grabe, nakita raw si Teresa. Halos di na siya makilala.</d> Marco leans over to look, then sits back, laughing lightly, shaking his head. MARCO (S2), dismissive, replies: <d>[Tagalog] Sabi ko na sa\'yo, hindi siya katulad mo.</d>',
        ],
        soundscape=f"{AMBIENCE} A faint phone notification chime. Only SELINA and MARCO speak.",
    ),
    dict(
        frames=158,  # ~6.6s, cliffhanger
        summary="Selina dismisses Teresa's family as nobodies; Marco's reaction is not quite as certain as before.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera. Selina sips from a wine glass, utterly unbothered, waving a dismissive hand. SELINA (S1), cold and offhand, speaks the VERY FIRST LINE: <d>[Tagalog] Wala naman talagang mawawala sa kanila. Mga walang kwentang pamilya lang naman sila.</d> Marco\'s easy smile falters for just a moment — he looks down at his glass instead of laughing along this time, something unreadable crossing his face. Hard cut before he says anything.',
        ],
        soundscape=f"{AMBIENCE} Ice shifts softly in Selina's glass. Only SELINA speaks in this clip.",
    ),
]

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}
REFS = ["selina-ref.jpeg", "marco-ref.jpeg", "condo-ref.jpeg"]
BASE_SEED = 200001


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
