"""Eli: medicine run through an infected city. Reference mode, in-clip cuts, Turbo 6.
Pictures: 1 Eli, 2 infected look (template for every infected, each a different person), 3 empty street (location)."""
import json, sys, time, urllib.request

SUBJECTS = """subject_definitions:
<Subject 1> is ELI, using <Picture 1> for his identity: Filipino-Spanish man around 35, lean and tired, short messy dark hair, stubble, olive-green worn field jacket over a grey hoodie, dark jeans, black backpack, short metal baton, a thin plain silver bracelet on his right wrist.
<Subject 2> is the INFECTED, using <Picture 2> ONLY as the style template: greyish pale skin with dark veins, bloodshot clouded eyes, torn dirty everyday clothes, hunched twitching movement. Every infected is a DIFFERENT person (different age, gender, build, hair and clothes: office worker, delivery rider, older woman in a cardigan, teenager in a hoodie, security guard). Never copy the same face onto several infected.
<Picture 3> is the location: an empty downtown street at dusk. Location/composition anchor only, no characters come from this picture."""

RETENTION = """retention_analysis:
<Subject 1> fully_preserved: face, hair, skin tone, body and outfit from <Picture 1>, including the backpack and the silver bracelet.
<Subject 2>: style only from <Picture 2>; each infected individual looks different.
<Picture 3> is used only for the environment, layout and lighting; do not add any person from it."""

RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue written inside <d>...</d> may be spoken aloud. Everything else is SILENT visual direction. Otherwise only breathing, grunts, infected snarls and screeches, never words.
CRITICAL VISUAL RULE: No other survivors, no crowd of normal people. No on-screen text, subtitles, captions, logos, watermarks or readable signs.
LOCATION LOCK (same street in every shot of every clip): one straight downtown road running away from camera, the same as <Picture 3>. Fixed layout: a dark alley entrance on the LEFT side; storefronts with half-open metal shutters on both sides; a silver sedan abandoned at an angle across the left lane; a white van stopped in the middle distance; a red hatchback parked at the RIGHT curb (the car Eli gets slammed into); flickering streetlights; an orange-purple dusk sky between the buildings; trash and glass bottles on the asphalt. Every camera angle shows THIS same street: only the camera moves. Do not add, remove or relocate cars, the alley, shutters or lights between shots. Same dusk light throughout, slowly darkening. Changes persist: a dent in the red hatchback stays dented in later shots.
STYLE: Photorealistic live-action survival horror film, handheld documentary energy, shallow depth of field, desaturated teal-orange grade, natural dusk light, grounded and tense, no gore, no cartoon effects. Hard cuts, no dissolves."""

def clip(summary, shots, sound, music):
    return f"""{SUBJECTS}

summary:
[reference generation] {summary}

{RETENTION}

detailed_description:
{RULES}

{shots}

overall_soundscape:
{sound}

non_diegetic_music:
{music}"""

C1 = clip(
 "Eli packs insulin and his daughter's crayon drawing, walks the empty street, hears a rolling bottle, and gets tackled into a parked car by an infected man.",
 """[Shot 1] Extreme close-up: Eli's hands, crouched beside the red hatchback, slide a small white insulin box and a folded child's crayon drawing (a stick-figure man holding a little girl's hand, a yellow sun, NO words) into the front pocket of his backpack and zip it shut.
[Shot 2] At 00:01.600, cut to a wide shot from behind: Eli walks quickly down the middle of the empty road toward camera-far, backpack on, baton in hand, the abandoned silver sedan on the left, the red hatchback at the right curb.
[Shot 3] At 00:03.200, cut to a medium shot facing Eli: he stops dead, listening. Cut to an insert at 00:04.200: a glass bottle rolls slowly out of the dark alley on the left and clinks to a stop. Total silence.
[Shot 4] At 00:05.800, cut to a wide handheld shot: an infected man in a torn office shirt bursts from behind the red hatchback and tackles Eli into its side, BANG, the door dents, the frame shakes.""",
 "Distant wind between buildings, Eli's quick footsteps and breath, a zipper, a glass bottle rolling and clinking, dead silence, then a violent snarl and a heavy BANG of a body hitting a car door.",
 "A low, uneasy drone that drops out completely during the silence; a sharp sting on the tackle.")

C2 = clip(
 "Eli fights off the first infected, then more emerge from between the cars and slowly surround him; there is nowhere to run.",
 """[Shot 1] Close two-shot against the dented red hatchback: the infected man snaps at Eli's face; Eli jams his forearm into the infected's jaw, blocking the bite, then plants a boot and kicks him away.
[Shot 2] At 00:02.200, cut to over Eli's shoulder: behind him, a second infected (a delivery rider in a torn jacket) rises between the cars. Then a third, an older woman in a cardigan.
[Shot 3] At 00:04.000, cut to a slow wide pan: three more infected step out from between the abandoned cars and from the alley on the left, twitching, closing in from every side.
[Shot 4] At 00:05.800, cut to a high overhead angle: Eli at the center of a tightening ring of six infected on the asphalt. Cut to a close-up at 00:06.800: Eli looks left, then right, breathing hard. Nowhere to run.""",
 "Snarls and wet breathing, a boot impact, shuffling and dragging footsteps from every direction, low guttural clicks, Eli's ragged breath, the faint buzz of a flickering streetlight.",
 "A slow, tightening string drone with a heartbeat-like low pulse.")

C3 = clip(
 "Eli fights back with his baton but is overwhelmed and dragged to the ground; with hands grabbing him from everywhere, he pulls a small silver bracelet from his jacket.",
 """[Shot 1] Medium shot: the first infected charges; Eli swings the metal baton, CRACK, across its head and it drops onto the asphalt.
[Shot 2] At 00:01.600, cut to a side angle: the delivery-rider infected leaps onto Eli's back; Eli drives himself backward and slams it against the red hatchback's door.
[Shot 3] At 00:03.300, cut to a wide shot: the rest rush him all at once and drag him down to the street.
[Shot 4] At 00:04.800, cut to a chaotic low close-up on the ground: grey hands grabbing at his jacket, hood and arms from every side; Eli, pinned, desperately forces one hand inside his jacket.
[Shot 5] At 00:06.400, cut to an extreme close-up: his hand pulls out a small plain silver metal bracelet, its surface catching the dying dusk light.""",
 "A sharp CRACK of the baton, a body hitting asphalt, a car door slam, a wave of overlapping snarls, fabric tearing, Eli's strained grunts, then a faint metallic chime as the bracelet comes out.",
 "Percussive, frantic strings rising to a peak, cutting to a single held high note on the bracelet.")

C4 = clip(
 "The bracelet expands into heavy rings; Eli punches the ground and a shockwave throws every infected away; car alarms wail and distant screams answer from all directions; Eli looks at his daughter's drawing and runs.",
 """[Shot 1] Close-up: Eli clenches his fist; the small silver bracelet unfolds and expands into several heavy segmented metal rings locking around his forearm with a mechanical clank, glowing faintly white-blue at the seams.
[Shot 2] At 00:01.500, cut to a wide overhead shot: Eli punches the asphalt, BOOM, a ring-shaped shockwave blasts outward and throws every infected away from him across the street; the abandoned cars rock and their windows rattle.
[Shot 3] At 00:03.000, cut to a low angle: car alarms start screaming up and down the street, headlights flashing; Eli slowly gets to his feet, the rings around his arm. He freezes as dozens of distant inhuman SCREAMS answer from every direction.
[Shot 4] At 00:05.000, cut to a close-up: Eli pulls the crayon drawing a little way out of his backpack pocket, looks at it, and whispers: <d>[English] I'm coming home, Mia.</d>
[Shot 5] At 00:06.800, cut to a wide shot from behind: Eli sprints down the middle of the darkening street toward the far end. At 00:07.600 the frame cuts to pure black and holds black to the end.""",
 "A mechanical clank and hum as the rings form, a huge concussive BOOM, bodies skidding, then a chorus of car alarms wailing, then dozens of distant screams echoing between buildings, Eli's whisper, running footsteps, then sudden silence on black.",
 "Silence on the ring transformation, a deep sub-bass hit on the shockwave, an ominous rising choir-like drone under the distant screams, a single emotional piano note under the whisper, then nothing on black.")

if __name__ == "__main__":
    refs = ["eli-ref.jpeg", "infected-ref.jpeg", "street-ref.jpeg"]
    ids = []
    for i, (c, seed) in enumerate(((C1, 670001), (C2, 670002), (C3, 670003), (C4, 670004)), 1):
        open(f"clip{i}.prompt.txt", "w").write(c)
        if "--submit" in sys.argv:
            body = {"prompt": c, "mode": "refs", "engine": "runpod", "refs": refs,
                    "params": {"width": 576, "height": 1024, "frames": 192, "steps": 6, "reuse": 2,
                               "layers": 50, "seed": seed, "turbo": True}}
            r = json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:7833/api/generate",
                           data=json.dumps(body).encode(), method="POST")).read())
            print(f"clip{i}", r); ids.append(r["id"]); time.sleep(1.1)
    if ids:
        open("job_ids.json", "w").write(json.dumps(ids))
    print("prompts written", [len(c) for c in (C1, C2, C3, C4)])
