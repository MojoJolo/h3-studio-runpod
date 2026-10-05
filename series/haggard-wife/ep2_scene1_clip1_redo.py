"""Redo of Episode 2 Scene 1 clip 1 (seed 200001): had a persistent diagonal
RGB-fringed rendering artifact across the lower-left of frame, and Marco's
shirt color drifted from scripted dark navy to match Selina's teal-green
dress by mid-clip. Rerolling seed + reinforcing color distinction.
"""
import json
import urllib.request

SELINA_LOOK = "SELINA, using <Picture 1> for her identity: a 42-year-old striking, confident Filipina woman, glossy dark wavy hair, bold red lipstick, refined makeup, wearing an elegant emerald GREEN silk robe-style loungewear with gold jewelry, poised and composed"
MARCO_LOOK = "MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, clean-shaven sharp jawline, wearing an open dark NAVY BLUE silk shirt (a cool, distinctly blue tone, clearly different from Selina's green — never green, never teal), a flashy gold watch on his wrist, confident easy smile"

PROMPT = f"""subject_definitions:
<Subject 1> is {SELINA_LOOK}, in the condo living room.
<Subject 2> is {MARCO_LOOK}, in the same condo living room.
<Picture 3> is the condo living room: floor-to-ceiling windows with a glittering city skyline view at night, curved white sofa, crystal pendant light, marble accent wall, expensive minimalist decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Marco admires an expensive new watch Selina just gave him; she makes him feel chosen and unburdened, not funded. The moment is interrupted by her phone buzzing, setting up the next beat.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing stays emerald green throughout, never changes color.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing stays navy blue throughout, never changes color, never drifts toward green or teal.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Selina and Marco, and no one else. No visual artifacts, streaks, or lines of any kind should appear anywhere in frame — clean photographic image quality throughout.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.

[Shot 1] Medium two-shot, fixed camera, both seated close together on the curved sofa, the city skyline glittering behind them. Marco turns his wrist, admiring a gold watch, genuinely delighted. MARCO (S2), warm, almost boyish, speaks the VERY FIRST LINE: <d>[Tagalog] Selina... hindi ko akalaing bibigyan mo pa ako nito.</d> Selina leans in, adjusting his collar with a soft, confident smile. SELINA (S1), warm and possessive, replies: <d>[Tagalog] Dahil karapat-dapat ka rito. Gusto kong pakiramdam mo, hari ka — hindi parang pasanin.</d> Right as she finishes speaking, her phone buzzes with a notification on the side table beside her. She glances toward it, still smiling, one hand already reaching for it.

overall_soundscape:
A quiet, expensive-feeling condo interior at night, faint distant city hum through the glass. Soft rustle of fabric as Selina leans in. Only SELINA and MARCO speak.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 158, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 200010, "ssd_streaming": True,
}
REFS = ["selina-ref.jpeg", "marco-ref.jpeg", "condo-ref.jpeg"]

if __name__ == "__main__":
    payload = {"prompt": PROMPT, "mode": "refs", "engine": "h3", "params": PARAMS, "refs": REFS}
    req = urllib.request.Request(
        "http://127.0.0.1:7833/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read().decode())
