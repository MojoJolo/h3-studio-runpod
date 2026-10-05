"""Standalone episode: Isabel / hotel lobby. 10 clips, ~65s.

A plainly-dressed woman is publicly humiliated by hotel staff who judge her
by appearance. One phone call later, the manager is fired in front of
everyone and she turns to the receptionist who started it.

All production lessons from the Haggard Wife series are applied here:
- Six-section MiniMax H3 Full-Reference Mode prompt format
- Uncontracted Tagalog ("sa iyo", never "sa'yo") for TTS pronunciation
- Explicit anti-caption visual rule on every clip
- Explicit anti-duplication language in retention_analysis
- Opening shot staged already-in-position (no walking in)
- Max 2 visible characters per clip; at most 2 character refs + 1 location
- Manager and executive given explicitly contrasting features so the dim
  lobby doesn't blur them together
"""
import json
import time
import urllib.request

API = "http://127.0.0.1:7833/api/generate"

ISABEL = ("ISABEL, using <Picture 1> for her identity: a plain, completely unremarkable Filipina woman in her "
          "early 40s, no makeup, dark hair simply tied back, wearing a simple beige short-sleeve blouse and dark "
          "slacks, holding a modest handbag. She looks ordinary, not poor.")

RECEPTIONIST = ("the HOTEL RECEPTIONIST, using <Picture 2> for her identity: a Filipina woman in her mid-20s, "
                "sleek dark hair pulled back into a tight bun, polished makeup, wearing a crisp dark navy hotel "
                "uniform blazer with a small gold name tag.")

MANAGER_P2 = ("the HOTEL MANAGER, using <Picture 2> for his identity: a Filipino man with slicked-back BLACK hair, "
              "clean-shaven, wearing a CHARCOAL GREY two-piece suit with a gold hotel lapel pin and a grey tie. "
              "He has NO waistcoat and NO grey in his hair.")

MANAGER_P1 = MANAGER_P2.replace("<Picture 2>", "<Picture 1>")

EXECUTIVE_P2 = ("the SENIOR EXECUTIVE, using <Picture 2> for his identity: an older, distinguished Filipino man in "
                "his 50s with clearly GREY-STREAKED hair, wearing a dark NAVY THREE-PIECE suit with a visible "
                "waistcoat and navy tie. He is visibly older and more senior than the hotel manager.")

LOBBY_P3 = ("<Picture 3> is the hotel lobby: polished marble floors, a long reception desk with brass accents and a "
            "marble counter, warm ambient lighting, a tall floral arrangement, high ceilings, elegant seating visible "
            "in the background. Composition/location anchor only — no characters appear in this picture.")

LOBBY_P2 = LOBBY_P3.replace("<Picture 3>", "<Picture 2>")

AUDIO = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame."""

AUDIO_SILENT = """CRITICAL AUDIO RULE: There is NO dialogue anywhere in this clip. Nobody speaks a single word — this entire clip is silent visual direction only, carried purely by expression. Do not write any <d> lines.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame."""

AMBIENCE = "Quiet upscale hotel lobby ambience, soft footsteps on marble, distant murmured conversation, a faint lobby piano far in the background."


def build(subjects, summary, retention, audio, shots, soundscape):
    return f"""subject_definitions:
{subjects}

summary:
[reference generation] {summary}

retention_analysis:
{retention}

detailed_description:
{audio}

{shots}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


NO_ARTIFACTS = ("No visual artifacts, streaks, lines, or chromatic fringing anywhere in frame — clean photographic "
                "image quality throughout. Each character's garment keeps its own exact colour for the entire clip "
                "and never drifts toward another character's colour.")

TWO_PEOPLE = ("Exactly two people are visible in every shot of this clip, and no one else. Do not duplicate, clone, "
              "or generate a second version of either subject. No third person, no extra hand, arm, or limb of any "
              "kind anywhere in frame. Background hotel guests may appear only as distant, blurred, out-of-focus "
              f"figures far behind them, never near the two subjects and never interacting. {NO_ARTIFACTS}")

ONE_PERSON = ("Exactly one person is visible in every frame of this clip: Isabel alone, and no one else. Do not "
              "duplicate or clone her. No second person, hand, arm, or limb of any kind anywhere in frame. "
              "Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind her. "
              f"{NO_ARTIFACTS}")


clips = []

# ---- 1. Hook ----
clips.append(dict(
    n=1, frames=192, seed=510101,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "Already mid-confrontation at the reception desk, the receptionist publicly tells Isabel she does not belong "
        "in this hotel, loud enough that other guests turn to look. Isabel stays quietly polite.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, both women are ALREADY standing in position at the reception desk, "
        "facing each other, the confrontation already in progress — nobody walks into frame. Medium two-shot, fixed "
        "camera, the marble desk and warm lobby clearly visible around them. The receptionist looks Isabel slowly up "
        "and down, not hiding her contempt, and raises her voice slightly so it carries across the lobby. "
        "RECEPTIONIST (S2), openly disdainful, speaks the VERY FIRST LINE: "
        "<d>[Tagalog] Ma'am, sabi ko na po sa inyo — hindi po ito lugar para sa katulad niyo.</d> "
        "Isabel does not flinch or raise her voice. ISABEL (S1), quiet, still polite, replies: "
        "<d>[Tagalog] May reservation po ako.</d>",
        f"{AMBIENCE} Only the RECEPTIONIST and ISABEL speak.",
    ),
))

# ---- 2. Receptionist doubles down ----
clips.append(dict(
    n=2, frames=192, seed=510102,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "The receptionist refuses to even check properly, insisting there is no record and the hotel is full. Isabel "
        "asks her calmly to check again and is shut down.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, same positions at the reception desk. The receptionist barely "
        "glances at her computer screen before answering. RECEPTIONIST (S2), dismissive, speaks the VERY FIRST LINE: "
        "<d>[Tagalog] Wala po kaming record. Puno na rin po kami.</d> "
        "Isabel remains calm, her hands still folded on her handbag. ISABEL (S1), patient, asks: "
        "<d>[Tagalog] Pwede mo bang i-check ulit?</d> "
        "The receptionist does not touch the keyboard at all. RECEPTIONIST (S2), clipped and final, replies: "
        "<d>[Tagalog] Ma'am, alam ko po ang trabaho ko.</d>",
        f"{AMBIENCE} Only the RECEPTIONIST and ISABEL speak.",
    ),
))

# ---- 3. Manager arrives, contemptuous ----
clips.append(dict(
    n=3, frames=175, seed=510103,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The hotel manager steps in and, instead of helping, insults Isabel's clothes and threatens to call security. "
        "He uses 'Ma'am' but addresses her with informal, disrespectful pronouns.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above. "
        f"His hair is black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, the manager already standing beside the reception desk facing Isabel, "
        "both fully in frame, the lobby visible around them. He looks her over with open disdain, one hand gesturing "
        "toward the entrance. MANAGER (S2), contemptuous, speaks the VERY FIRST LINE: "
        "<d>[Tagalog] May problema ba? Ma'am, tingnan mo nga ang suot mo. Umalis ka na bago ko tawagin ang security.</d> "
        "Isabel says nothing. She holds his gaze for a moment, absolutely still. He turns his back on her "
        "dismissively and walks off toward the far side of the lobby, leaving her standing alone.",
        f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    ),
))

# ---- 4. Angst beat (silent, solo) ----
clips.append(dict(
    n=4, frames=107, seed=510104,
    refs=["isabel-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n{LOBBY_P2}",
        "Alone for a moment, the humiliation finally lands on Isabel. Her composure cracks briefly — and then it is "
        "gone, and she takes out her phone.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Picture 2> is used only for the lobby layout and lighting — do not add any character from this picture. {ONE_PERSON}",
        AUDIO_SILENT,
        "[Shot 1] From the very first frame, the camera is already on Isabel standing alone to one side of the lobby, "
        "medium close shot. Nobody else is near her. She grips the strap of her handbag tightly. For one moment her "
        "composed expression cracks — a flicker of real, private hurt crosses her face, her eyes glassy. Then she "
        "swallows it, her jaw sets, and the hurt vanishes completely. She reaches into her bag and takes out her phone.",
        "Quiet upscale hotel lobby ambience, a faint lobby piano far in the background, the soft click of a handbag clasp.",
    ),
))

# ---- 5. The call (solo) ----
clips.append(dict(
    n=5, frames=124, seed=510105,
    refs=["isabel-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n{LOBBY_P2}",
        "Isabel makes one short phone call. No explanation, no threat — just an instruction.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Picture 2> is used only for the lobby layout and lighting — do not add any character from this picture. {ONE_PERSON}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already on Isabel alone, medium close shot, phone already "
        "raised to her ear, her expression now completely calm and unreadable. ISABEL (S1), quiet and commanding, "
        "speaks the VERY FIRST LINE: <d>[Tagalog] Nasa lobby ako. Punta ka dito.</d> "
        "She lowers the phone without waiting for a reply.",
        "Quiet upscale hotel lobby ambience, a faint lobby piano far in the background. Only ISABEL speaks.",
    ),
))

# ---- 6. Manager mocks the call ----
clips.append(dict(
    n=6, frames=141, seed=510106,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The manager sees her on the phone and mocks her for it — seconds before that call destroys his career.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above. "
        f"His hair is black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, both already in position, the manager a few steps from Isabel with "
        "his arms loosely folded, smirking at the phone in her hand. MANAGER (S2), openly mocking, speaks the VERY "
        "FIRST LINE: <d>[Tagalog] Sino ba naman ang tatawagan mo? Walang makakatulong sa iyo dito.</d> "
        "Isabel does not answer him and does not look away. She simply waits.",
        f"{AMBIENCE} Only the MANAGER speaks in this clip.",
    ),
))

# ---- 7. The turn ----
clips.append(dict(
    n=7, frames=175, seed=510107,
    refs=["isabel-ref.jpeg", "hotel-executive-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {EXECUTIVE_P2}\n{LOBBY_P3}",
        "A senior hotel executive stands before Isabel and greets her with deep deference, apologising for not "
        "knowing she had arrived.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above. "
        f"His hair is clearly grey-streaked and he wears a navy THREE-PIECE suit with a visible waistcoat.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, the executive already standing in front of Isabel, slightly bowed "
        "toward her, both fully in frame. His whole posture is deferential — the opposite of how the staff have "
        "treated her. EXECUTIVE (S2), urgent and respectful, speaks the VERY FIRST LINE: "
        "<d>[Tagalog] Ma'am Isabel! Pasensya na po, hindi namin alam na nandito na kayo.</d> "
        "Isabel says nothing. She simply looks past him, toward where the manager is standing off-camera.",
        f"{AMBIENCE} Only the EXECUTIVE speaks in this clip.",
    ),
))

# ---- 8. The payback ----
clips.append(dict(
    n=8, frames=175, seed=510108,
    refs=["hotel-executive-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {EXECUTIVE_P2.replace('<Picture 2>', '<Picture 1>')}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The executive turns on the manager and fires him on the spot, in the middle of the lobby. The manager tries "
        "to protest that he did not know who she was.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. He is the OLDER man with "
        f"GREY-STREAKED hair in the NAVY THREE-PIECE suit with a visible waistcoat.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. He is the YOUNGER man with "
        f"slicked-back BLACK hair in the CHARCOAL two-piece suit with NO waistcoat. The two men must look clearly "
        f"different from each other and must never be confused or swapped.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, the two men facing each other in the lobby. The manager's smug "
        "expression is completely gone — he has gone pale and rigid. The executive does not raise his voice at all. "
        "EXECUTIVE (S1), ice cold, speaks the VERY FIRST LINE: <d>[Tagalog] Kolektahin mo na ang gamit mo.</d> "
        "The manager takes a half step forward, panicking, hands lifting. MANAGER (S2), stammering, replies: "
        "<d>[Tagalog] Sir, hindi ko po alam—</d> "
        "The executive cuts him off without blinking. EXECUTIVE (S1), flat and final: "
        "<d>[Tagalog] Hindi mo nga alam. Iyon ang problema.</d>",
        f"{AMBIENCE} Only the EXECUTIVE and the MANAGER speak.",
    ),
))

# ---- 9. Vicious ----
clips.append(dict(
    n=9, frames=141, seed=510109,
    refs=["isabel-ref.jpeg", "hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {MANAGER_P2}\n{LOBBY_P3}",
        "The manager grovels toward Isabel. She finally turns and looks at him, and tells him this is not over.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above. "
        f"His hair is black and slicked back with NO grey, and his charcoal suit has NO waistcoat.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera, the manager turned toward Isabel, his hands half-raised in a "
        "pleading gesture, desperate. Isabel turns her head and looks directly at him for the first time, completely "
        "calm. ISABEL (S1), quiet and merciless, speaks the VERY FIRST LINE: "
        "<d>[Tagalog] Hindi lang trabaho mo ang mawawala sa iyo.</d> "
        "The manager's face collapses. He says nothing.",
        f"{AMBIENCE} Only ISABEL speaks in this clip.",
    ),
))

# ---- 10. Cliffhanger ----
clips.append(dict(
    n=10, frames=124, seed=510110,
    refs=["isabel-ref.jpeg", "receptionist-ref.jpeg", "hotel-lobby-ref.jpeg"],
    prompt=build(
        f"<Subject 1> is {ISABEL}\n<Subject 2> is {RECEPTIONIST}\n{LOBBY_P3}",
        "Isabel turns to the receptionist who started all of this and who thought she had been forgotten. Two words, "
        "then a hard cut.",
        f"<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.\n"
        f"<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.\n"
        f"<Picture 3> is used only for the lobby layout and lighting — do not add any character from this picture. {TWO_PEOPLE}",
        AUDIO,
        "[Shot 1] From the very first frame, the camera is already inside the hotel lobby — no other location appears at any point in this clip. Medium two-shot, fixed camera. The receptionist is frozen behind the desk, having watched "
        "everything, clearly hoping she has gone unnoticed. Isabel turns her head slowly and looks straight at her. "
        "ISABEL (S1), quiet, almost gentle, speaks the VERY FIRST LINE: <d>[Tagalog] Ikaw naman.</d> "
        "The receptionist's face drains of colour. Hold on her stricken expression. Hard cut to black.",
        f"{AMBIENCE} Only ISABEL speaks in this clip.",
    ),
))


PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}


def submit(clip):
    payload = {
        "prompt": clip["prompt"],
        "mode": "refs",
        "engine": "h3",
        "params": dict(PARAMS_BASE, frames=clip["frames"], seed=clip["seed"]),
        "refs": clip["refs"],
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    for c in clips:
        r = submit(c)
        print(f"clip {c['n']:>2} (seed {c['seed']}, frames {c['frames']}): {r}")
        time.sleep(0.4)
