"""Scene 3 bridging clip, v2: relocated from a generic hallway to the front
PORCH of Teresa's house, door already open, with the opulent interior
(chandelier, marble, staircase) clearly visible through the doorway behind
the maid — a much stronger, more concrete wealth-reveal beat than the
earlier version, per user direction. Same dialogue as before. Maid bows.
"""
import json
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman, haggard but naturally beautiful, dark hair in a low ponytail with loose strands, tired eyes, wearing the same simple worn cream cotton house dress with short sleeves"
MAID_LOOK = "a household maid, using <Picture 2> for her identity: a Filipina woman in her mid-30s, neat black hair in a low bun, warm and welcoming expression, wearing a simple pale blue collared house-uniform blouse"

PROMPT = f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, already standing still on the porch, facing the open front door and the house. She does not walk or turn during this clip — she is stationary, front of her body fully facing the doorway the entire time.
<Subject 2> is {MAID_LOOK}, standing just inside the open doorway, facing outward toward Teresa. She does not walk or turn away during this clip either.
<Picture 3> is the porch and open front door: understated tiled porch, plain exterior, the door standing wide open behind the maid revealing an opulent interior beyond — a grand foyer with a crystal chandelier, marble flooring, and an elegant curved staircase, warm gold lighting. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Facing the house, Teresa is greeted right at the open front door by a maid who welcomes her with a bow — beyond the threshold, the interior briefly visible is unmistakably opulent, a striking contrast to the modest gate and street outside.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the porch/doorway/interior-glimpse layout and lighting — do not add any character or person from this picture. EXACTLY TWO PEOPLE total appear anywhere in this clip, in every single frame: Teresa and the maid, and no one else. Do not duplicate or clone either subject. No third person, no extra hand, arm, or limb of any kind anywhere in frame. Neither character walks anywhere in this clip — both remain in place the entire time, Teresa's front always facing the house/doorway, never her back.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip, in clear, natural, well-articulated Filipino-accented speech. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written, clearly and naturally. Do NOT paraphrase, normalize, or rewrite the dialogue. The word "Ready" is the English loanword commonly used in casual Filipino speech, said naturally with a Filipino accent, not over-enunciated.

[Shot 1] From the very first frame, the camera is already on the porch, positioned to the side of the open doorway: Teresa is already standing on the porch tiles, seen from behind/three-quarter, her front facing the open door, and the maid is already standing in the doorway facing her, the opulent foyer glimpse — crystal chandelier, marble floor, curved staircase — clearly visible behind the maid with warm light spilling onto the porch tiles. There is no other location, room, or setting shown at any point in this clip — only this porch and doorway, from frame one to the last frame. Neither character moves their feet. The maid gives a small, respectful bow of the head as she welcomes her. MAID (S2), warm and welcoming, speaks the VERY FIRST LINE: <d>[Taglish] Ready na po ang kwarto niyo, Ma'am.</d> Teresa gives a small, tired nod, still adjusting to the reception. TERESA (S1), quiet, replies: <d>[Tagalog] Salamat.</d> The maid straightens, still standing in place in the doorway.

overall_soundscape:
Quiet dusk ambience outside, a faint warm hum from the chandelier's light fixtures inside, distant crickets. Only MAID and TERESA speak.

non_diegetic_music:
N/A"""

PARAMS = {
    "width": 576, "height": 1024, "frames": 141, "steps": 20, "reuse": 2,
    "layers": 50, "seed": 100680, "ssd_streaming": True,
}
REFS = ["teresa-ref.jpeg", "maid-ref.jpeg", "porch-ref.jpeg"]

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
