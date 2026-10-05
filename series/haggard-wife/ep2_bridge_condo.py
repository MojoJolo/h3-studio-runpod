"""Short bridging clip for Episode 2's interleaved cut: a wide, zoomed-out
establishing shot of Marco and Selina's condo interior, both small in frame,
sitting together laughing. Serves as the 'meanwhile, across town' visual
anchor between Teresa's office scene and the closer Marco/Selina dialogue
clips that follow. Silent, no dialogue, purely a spatial/tonal bridge.
"""
import json
import urllib.request

SELINA_LOOK = "SELINA, using <Picture 1> for her identity: a 42-year-old striking, confident Filipina woman, glossy dark wavy hair, bold red lipstick, wearing an elegant emerald green silk robe-style loungewear with gold jewelry"
MARCO_LOOK = "MARCO, using <Picture 2> for his identity: a 25-year-old handsome Filipino man, short dark hair, clean-shaven sharp jawline, wearing an open dark navy silk shirt (a cool, distinctly blue tone, never green or teal), a flashy gold watch on his wrist"

PROMPT = f"""subject_definitions:
<Subject 1> is {SELINA_LOOK}, seated on the curved sofa.
<Subject 2> is {MARCO_LOOK}, seated beside her on the same sofa.
<Picture 3> is the condo living room: floor-to-ceiling windows with a glittering city skyline view at night, curved white sofa, crystal pendant light, marble accent wall, expensive minimalist decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] A wide, zoomed-out establishing shot of the entire condo interior, Marco and Selina small in frame, sitting together laughing about something — a silent tonal bridge showing their carefree happiness.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing stays emerald green, never changes color.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing stays navy blue, never drifts toward green or teal.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every frame of this clip: Selina and Marco, and no one else. No visual artifacts, streaks, or lines of any kind should appear anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO dialogue anywhere in this clip. Neither character speaks — this entire clip is silent visual direction only. Do not write any <d> lines.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame.

[Shot 1] From the very first frame, a wide, zoomed-out shot capturing the entire condo living room — the full curved sofa, the towering windows, the glittering skyline beyond, the pendant light overhead. Marco and Selina are small within the wide frame, seated close together on the sofa, both laughing genuinely at something, relaxed and carefree, wine glasses on the table in front of them. The camera holds perfectly still, taking in the full scale and luxury of the space.

overall_soundscape:
Faint, distant laughter and the muffled hum of the city far below, a soft clink of glasses.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 107, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 200401, "ssd_streaming": True,
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
