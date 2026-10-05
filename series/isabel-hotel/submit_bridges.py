"""Two pure bridge clips for the Isabel hotel episode — arrival beats so the
manager and the executive don't materialise fully-formed in position.

Both use the ONLY walking staging that has ever worked reliably in this
project: camera already inside the destination space, facing the direction
the subject comes from, subject walking TOWARD camera. Sideways and
away-from-camera motion is what produced the exiting-instead-of-entering
failures on the Episode 1 gate and porch clips.

Both solo (zero duplication risk), both silent, both ~4.5s.

Placement in the final assembly:
    1, 2, [manager bridge], 3, 4, 5, 6, [executive bridge], 7, 8, 9, 10
"""
import json
import time
import urllib.request

API = "http://127.0.0.1:7833/api/generate"

MANAGER = ("the HOTEL MANAGER, using <Picture 1> for his identity: a Filipino man with slicked-back BLACK hair, "
           "clean-shaven, wearing a CHARCOAL GREY two-piece suit with a gold hotel lapel pin and a grey tie. "
           "He has NO waistcoat and NO grey in his hair.")

EXECUTIVE = ("the SENIOR EXECUTIVE, using <Picture 1> for his identity: an older, distinguished Filipino man in his "
             "50s with clearly GREY-STREAKED hair, wearing a dark NAVY THREE-PIECE suit with a visible waistcoat and "
             "navy tie.")

LOBBY = ("<Picture 2> is the hotel lobby: polished marble floors, a long reception desk with brass accents and a "
         "marble counter, warm ambient lighting, a tall floral arrangement, high ceilings, elegant seating visible in "
         "the background. Composition/location anchor only — no characters appear in this picture.")

SILENT = """CRITICAL AUDIO RULE: There is NO dialogue anywhere in this clip. Nobody speaks a single word — this entire clip is silent visual direction only, carried purely by movement and expression. Do not write any <d> lines.
CRITICAL VISUAL RULE: Do NOT render any on-screen subtitles, captions, text overlays, or burned-in text of any kind anywhere in the frame."""

ONE_MAN = ("Exactly one person is visible in every frame of this clip, and no one else. Do not duplicate, clone, or "
           "generate a second version of him. No second person, hand, arm, or limb of any kind anywhere in frame. "
           "Background hotel guests may appear only as distant, blurred, out-of-focus figures far behind him, never "
           "near him and never interacting. No visual artifacts, streaks, lines, or chromatic fringing anywhere in "
           "frame — clean photographic image quality throughout. His suit keeps its own exact colour for the entire "
           "clip and never changes shade.")

AMBIENCE = ("Quiet upscale hotel lobby ambience, firm footsteps approaching on marble, distant murmured conversation, "
            "a faint lobby piano far in the background.")


def build(subject, summary, retention_extra, shot, soundscape):
    return f"""subject_definitions:
<Subject 1> is {subject}
{LOBBY}

summary:
[reference generation] {summary}

retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone and body from <Picture 1>. Clothing as specified above. {retention_extra}
<Picture 2> is used only for the lobby layout and lighting — do not add any character from this picture. {ONE_MAN}

detailed_description:
{SILENT}

{shot}

overall_soundscape:
{soundscape}

non_diegetic_music:
N/A"""


MANAGER_BRIDGE = build(
    MANAGER,
    "The hotel manager emerges from the back office behind the reception counter and takes his place at the desk, "
    "irritated at being called over — his arrival beat before he confronts Isabel.",
    "His hair is black and slicked back with NO grey, and his charcoal suit has NO waistcoat.",
    "[Shot 1] From the very first frame, the camera is already inside the hotel lobby on the guest side of the "
    "reception desk, facing the desk and the back wall behind it, where an open back-office doorway stands — no other "
    "location appears at any point in this clip. Medium shot, fixed camera. The reception counter is empty, with "
    "nobody behind it. The manager steps forward through the already-open back-office doorway — the door is already "
    "open and nobody opens or touches it — and moves TOWARD the camera to take his place behind the reception "
    "counter, growing larger in frame and never moving away from camera. He tugs his suit jacket straight as he "
    "comes, his expression that of a man irritated at being bothered by something beneath him. He does not speak.",
    AMBIENCE,
)

EXECUTIVE_BRIDGE = build(
    EXECUTIVE,
    "The senior executive strides in from the hotel's main entrance, grim and purposeful, already knowing something "
    "is wrong — his arrival beat before he reaches Isabel.",
    "His hair is clearly grey-streaked and he wears a navy THREE-PIECE suit with a visible waistcoat.",
    "[Shot 1] From the very first frame, the camera is already inside the hotel lobby, facing toward the hotel's main "
    "entrance — no other location appears at any point in this clip. Wide-to-medium shot, fixed camera. The executive "
    "is already mid-stride, walking directly TOWARD the camera, deeper into frame and never away from it, crossing "
    "the marble floor at a fast, purposeful pace. His expression is grim and set — he already knows something is "
    "wrong. He does not speak. He grows larger in frame as he approaches.",
    AMBIENCE,
)


PARAMS_BASE = {
    "width": 576, "height": 1024, "steps": 20, "reuse": 2, "layers": 50,
    "ssd_streaming": True,
}


def submit(prompt, frames, seed, refs):
    payload = {
        "prompt": prompt, "mode": "refs", "engine": "h3",
        "params": dict(PARAMS_BASE, frames=frames, seed=seed),
        "refs": refs,
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    r1 = submit(MANAGER_BRIDGE, 107, 510111, ["hotel-manager-ref.jpeg", "hotel-lobby-ref.jpeg"])
    print("manager bridge (seed 510111):", r1)
    time.sleep(0.4)
    r2 = submit(EXECUTIVE_BRIDGE, 107, 510112, ["hotel-executive-ref.jpeg", "hotel-lobby-ref.jpeg"])
    print("executive bridge (seed 510112):", r2)
