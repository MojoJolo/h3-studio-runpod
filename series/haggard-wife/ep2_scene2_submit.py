"""Episode 2, Scene 2: 'Quiet Moves'. Teresa and Tatay Lino in her private
office. This is where she visibly transforms from haggard to composed
(per the bible's own schedule - Ep2 Scene2 is where this begins), where
the audience finally learns WHY she lived haggard by choice, and where the
investigation into Selina's money is set in motion and pays off.

3 clips, lean per the no-drag rule: the 'give an order' and 'investigate
Selina' beats are merged into one clip since splitting them added nothing.
"""
import json
import time
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman with fine delicate features and high cheekbones, now composed and elegant — hair loose and smooth instead of a tired ponytail, calm controlled posture, no longer haggard or tired-looking, wearing a tailored dark charcoal silk blouse"
STAFF_LOOK = "TATAY LINO, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"

def subject_defs():
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, seated at a large executive desk in her private office.
<Subject 2> is {STAFF_LOOK}, standing respectfully near the desk.
<Picture 3> is the office: large dark wood executive desk, tall bookshelf filled with books, deep green leather chair, warm brass desk lamp, heavy curtains, old-money decor. Composition/location anchor only — no characters appear in this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing and composed demeanor as specified above, consistent throughout.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Teresa and Tatay Lino, and no one else."""

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame. This is a clean photographic/cinematic image with no text elements at all — no matter what is spoken."""


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


AMBIENCE = "A quiet private office at night, a faint clock ticking, warm lamp light."

clips_data = [
    dict(
        frames=158,  # ~6.6s
        summary="Teresa, composed and commanding, gives Tatay Lino a direct instruction to investigate Selina's finances, and he obeys instantly and completely.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, Teresa seated at the desk, Tatay Lino standing attentively. Teresa does not look up from the papers in front of her as she speaks, calm and precise. TERESA (S1), composed, quietly commanding, speaks the VERY FIRST LINE: <d>[Tagalog] Alamin mo kung saan talaga nanggagaling ang pera ni Selina. Gusto kong malaman lahat.</d> Tatay Lino gives a small, immediate bow of the head. TATAY LINO (S2), respectful, without hesitation, replies: <d>[Tagalog] Opo, Ma\'am. Gagawin ko na po agad.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TERESA and TATAY LINO speak.",
    ),
    dict(
        frames=175,  # ~7.3s
        summary="Tatay Lino gently offers her a way back to her family fully; Teresa reveals she chose the haggard life herself, refusing to let money define her marriage.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera at a moderate distance, both Teresa and Tatay Lino fully visible from the waist up, the office clearly visible around them — the bookshelf, desk lamp, and curtains all in frame. Tatay Lino stands respectfully beside the desk, hands clasped in front of him, not touching her, his tone softening, fatherly but proper. TATAY LINO (S2), gentle, speaks the VERY FIRST LINE: <d>[Tagalog] Kung gusto niyo pong bumalik nang buo, laging bukas ang pinto rito.</d> Teresa looks down at her hands for a moment, something old and tired crossing her composed face before she steadies it. TERESA (S1), quiet, resolute, replies: <d>[Tagalog] Pinili ko ang buhay na iyon, Tatay Lino. Ayokong mahalin ako ni Marco dahil lang sa pera. Gusto kong totoo.</d>',
        ],
        soundscape=f"{AMBIENCE} Only TATAY LINO and TERESA speak.",
    ),
    dict(
        frames=175,  # ~7.3s, cliffhanger with cut
        summary="Tatay Lino returns with the finding: Selina has been profiting from corrupt flood control project deals — a standalone discovery about her, with no connection whatsoever to Teresa's family or any company of theirs. Teresa's reaction is cold and calculating.",
        shots=[
            '[Shot 1] Medium two-shot, fixed camera, Tatay Lino now standing closer to the desk, a folder in hand, clearly troubled by what he found. TATAY LINO (S2), careful, grave, speaks the VERY FIRST LINE: <d>[Taglish] Ma\'am, si Selina po pala, sangkot sa corrupt na flood control projects. Milyun-milyon na ang nakuha niya.</d>',
            '[Shot 2] At 00:04.000, cut to a close-up on Teresa\'s face, camera just past Tatay Lino\'s shoulder. She goes very still, a slow, cold understanding dawning in her eyes — not shock, calculation. TERESA (S1), quiet, almost to herself, replies: <d>[Tagalog] Kaya pala.</d> Hard cut to black.',
        ],
        soundscape=f"{AMBIENCE} A folder set softly on the desk. Only TATAY LINO and TERESA speak.",
    ),
]

PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "staff-ref.jpeg", "office-ref.jpeg"]
BASE_SEED = 200101


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
