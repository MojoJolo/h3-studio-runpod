"""Episode 2, Scene 3: 'The Trap Is Set'. Teresa arranges a meeting with
Selina without revealing her identity, then the cliffhanger is the silent
visual reveal itself - Selina opening the boardroom door and seeing Teresa
already there. No dialogue in clip 2 at all; the actual confrontation
conversation is saved for Episode 3's opening, per user direction.

2 clips, deliberately short and cold - the tonal contrast scene.
"""
import json
import time
import urllib.request

TERESA_LOOK = "TERESA, using <Picture 1> for her identity: a 25-year-old Filipina woman with fine delicate features and high cheekbones, composed and elegant, hair loose and smooth, calm controlled posture, wearing a tailored dark charcoal silk blouse"
STAFF_LOOK = "TATAY LINO, using <Picture 2> for his identity: a Filipino man in his mid-50s, neatly combed grey-streaked hair, clean-shaven, wearing a simple white long-sleeve barong-style shirt, calm and deeply respectful demeanor"
SELINA_LOOK = "SELINA, a 42-year-old striking, confident Filipina woman, glossy dark wavy hair, bold red lipstick, refined makeup, wearing an elegant tailored business dress, poised and composed"

AUDIO_RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue inside <d>...</d> may be spoken aloud, by the visible subject(s) named for this clip. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak every <d> line EXACTLY as written. Preserve all Tagalog pronouns and verb forms exactly. Do NOT paraphrase, normalize, or rewrite the dialogue.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame."""


def clip1_prompt():
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, seated at a large executive desk in her private office.
<Subject 2> is {STAFF_LOOK}, standing respectfully near the desk.
<Picture 3> is the office: large dark wood executive desk, tall bookshelf filled with books, deep green leather chair, warm brass desk lamp, heavy curtains, old-money decor. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Teresa instructs Tatay Lino to arrange a private meeting with Selina, without revealing her own identity beforehand.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Subject 2> fully_preserved: face, hair, skin tone and body from <Picture 2>. Clothing as specified above.
<Picture 3> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly two people are visible in every shot of this clip: Teresa and Tatay Lino, and no one else.

detailed_description:
{AUDIO_RULES}

[Shot 1] Medium two-shot, fixed camera, the office clearly visible around them. Teresa closes a folder on her desk with quiet finality. TERESA (S1), cold, decisive, speaks the VERY FIRST LINE: <d>[Taglish] Mag-schedule ka ng meeting. Gusto kong personal siyang harapin — pero huwag mo munang sasabihin kung sino ako.</d> Tatay Lino gives a small, respectful nod. TATAY LINO (S2), replies: <d>[Tagalog] Opo, Ma'am.</d>

overall_soundscape:
A quiet private office at night, a faint clock ticking, warm lamp light. Only TERESA and TATAY LINO speak.

non_diegetic_music:
N/A"""


def clip2_prompt():
    """Solo Teresa, already seated, waiting — pure suspense-building shot,
    no second character, no dialogue."""
    return f"""subject_definitions:
<Subject 1> is {TERESA_LOOK}, already seated at the head of a long boardroom table, alone.
<Picture 2> is the boardroom: long polished dark wood table, tall leather executive chairs, floor-to-ceiling windows with a city skyline at night, a single row of downlights over the table. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Teresa sits alone at the head of the boardroom table, composed and still, waiting for Selina to arrive without knowing who she's about to meet.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> is used only for the room's layout and lighting — do not add any character or person from this picture. Exactly one person is visible in every frame of this clip: Teresa alone. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO dialogue anywhere in this clip. Teresa does not speak. This entire clip is silent visual direction only, carried purely by stillness and atmosphere. Do not write any <d> lines.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame.

[Shot 1] From the very first frame, the camera is already inside the boardroom, positioned facing Teresa at the head of the table, the city skyline glittering through the windows behind her. She sits perfectly still, hands folded on the table, composed and patient, occasionally glancing toward the far end of the room where the door is closed. Nothing else happens — she simply waits, radiating quiet control.

overall_soundscape:
Dead silence in the boardroom, only the faint hum of the city through the windows.

non_diegetic_music:
N/A"""


def clip3_prompt():
    """Different angle near the entrance — Selina enters, camera positioned
    inside the room looking back toward the door so her walking motion
    reads unambiguously as entering (toward camera/into the room)."""
    return f"""subject_definitions:
<Subject 1> is {SELINA_LOOK}, using <Picture 1> for her identity, just stepping through the boardroom doorway.
<Picture 2> is the boardroom entrance end: dark wood double doors with brushed-metal handles, the same long polished dark wood table and tall leather chairs visible in the foreground, dark wood-paneled wall. Composition/location anchor only — no characters appear in this picture.
<Picture 3> is the boardroom window end: floor-to-ceiling windows with a city skyline at night, same table and chairs, a single row of downlights overhead — the far end of the same room, for overall style/lighting consistency. Composition/location anchor only — no characters appear in this picture.

summary:
[reference generation] Selina enters the boardroom expecting an anonymous business meeting; a different camera angle near the entrance captures her stepping in and freezing in shock as she sees who is waiting for her — a silent, purely visual reveal with no dialogue.

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above.
<Picture 2> and <Picture 3> are used only for the room's layout and lighting (two views of the same boardroom, entrance end and window end) — do not add any character or person from either picture. Exactly one person is visible in every frame of this clip: Selina alone, entering. No second person, hand, arm, or limb of any kind anywhere in frame.

detailed_description:
CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY Selina speaks, and only the single line written below in <d>...</d>. Everything else is silent visual direction.
CRITICAL DIALOGUE PRESERVATION: Speak the <d> line EXACTLY as written. Do NOT paraphrase or rewrite it.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame.

[Shot 1] From the very first frame, the camera is positioned INSIDE the boardroom near the far end, facing back toward the entrance door, so Selina walks TOWARD the camera as she enters — deeper into the room, never away from it. She steps through the doorway, confident and composed, expecting a routine meeting, walking forward normally.

[Shot 2] At 00:04.000, cut to a tight close-up push-in on Selina's face, filling most of the frame. Her confident expression collapses dramatically and unmistakably into genuine shock — her eyes go wide, her mouth falls open, her steps stop dead, her whole posture stiffens as the color seems to drain from her face. SELINA (S1), breathless, stunned, barely able to get the word out, says: <d>[English] Teresa?</d> Hard cut to black immediately after she speaks.

overall_soundscape:
Dead silence in the boardroom, only the faint hum of the city through the windows and the soft sound of her footsteps stopping abruptly.

non_diegetic_music:
N/A"""


PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}


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
    r2 = submit(clip2_prompt(), 124, 200221, ["teresa-ref.jpeg", "boardroom-ref.jpeg"])
    print("clip2 (Teresa waiting):", r2)
    time.sleep(0.5)
    r3 = submit(clip3_prompt(), 158, 200222, ["selina-ref.jpeg", "boardroom-ref.jpeg"])
    print("clip3 (Selina enters, shock):", r3)
