"""Ring Fight: 4-character superpowered action scene, reference mode, in-clip cuts.
Pictures: 1 Jace, 2 Maya, 3 Viktor, 4 Rei, 5 empty garage (location only)."""
import json, sys, time, urllib.request

SUBJECTS = """subject_definitions:
<Subject 1> is JACE, using <Picture 1> for his identity: East Asian man around 28, athletic martial artist, black undercut hair, dark charcoal tactical jacket with rolled sleeves, black cargo pants. Six thin glowing CYAN metal energy rings orbit his forearms; he controls them like whips and projectiles.
<Subject 2> is MAYA, using <Picture 2> for her identity: Black woman around 26, lean and fast, long box braids tied back high, fitted red-and-black combat suit, fingerless gloves; her palms flash ORANGE when she absorbs or redirects momentum.
<Subject 3> is VIKTOR, using <Picture 3> for his identity: enormous pale bald man around 40, seven feet tall, massively muscular, scar across one eyebrow, sleeveless torn grey shirt; superhuman strength, moves like a freight train.
<Subject 4> is REI, using <Picture 4> for her identity: slim agile woman around 24, short platinum silver bob, black hooded bodysuit; her fists glow VIOLET and release short-range kinetic shockwaves.
<Picture 5> is the location: a multi-level concrete parking structure at night in heavy rain, wet reflective floor, concrete pillars, flickering fluorescent tube lights, a black SUV, parked sedans, a sport motorcycle. Location/composition anchor only, no characters come from this picture."""

RETENTION = """retention_analysis:
<Subject 1> to <Subject 4> fully_preserved: face, hair, skin tone, body and outfit from <Picture 1> to <Picture 4> respectively, including Jace's cyan rings, Maya's orange palm glow and Rei's violet fist glow.
<Picture 5> is used only for the environment, layout and lighting; do not add any person from it.
NEVER swap faces, hair, bodies, outfits or power colors between characters. Jace's power is always cyan rings, Maya's always orange palm flashes, Rei's always violet shockwaves, Viktor has no glow."""

RULES = """CRITICAL AUDIO RULE: There is NO narrator and NO voice-over. ONLY dialogue written inside <d>...</d> may be spoken aloud. Everything else is SILENT visual direction. Apart from that, characters make only physical effort sounds (breaths, grunts), never words.
CRITICAL VISUAL RULE: Only the named characters for this clip are visible. No bystanders, no extra fighters, no crowd. No on-screen text, subtitles, captions, logos or watermarks.
LOCATION LOCK (same set in every shot of every clip): one continuous parking level, the same as <Picture 5>. Fixed layout: a row of square concrete pillars with yellow-and-black striped bases running away from camera; low ceiling with long fluorescent tube lights in parallel rows; wet grey concrete floor with yellow parking lines and puddles reflecting the lights; the black SUV parked nose-in on the left side; a row of parked sedans (white, silver, dark grey) along the right side; the sport motorcycle parked beside the second pillar; the open side of the structure on the right with rain blowing in. Every camera angle shows THIS same space from a different position: only the camera moves. Do not add, remove or relocate pillars, cars, the motorcycle or lights between shots, and do not change the lighting color or time of day. Damage is cumulative and stays: once the SUV windshield is shattered or a pillar is cracked, it stays shattered or cracked in every later shot.
STYLE: Photorealistic live-action superhero film, practical-effects feel, anamorphic lens, rain and wet reflections, high-contrast teal and amber grading, fast precise fight choreography, weighty impacts, debris and sparks, slight handheld energy. Hard cuts on impact, no dissolves."""

def clip(summary, visible, shots, sound, music):
    return f"""{SUBJECTS}

summary:
[reference generation] {summary}

{RETENTION}

detailed_description:
{RULES}
Visible in this clip: {visible}.

{shots}

overall_soundscape:
{sound}

non_diegetic_music:
{music}"""

C1 = clip(
 "Viktor smashes Jace through an SUV windshield; Jace answers with his rings and slams Viktor into a pillar; Rei drops in from above.",
 "Jace, Viktor and Rei (Rei only in the final shot). Maya is NOT in this clip",
 """[Shot 1] Low wide angle on the wet floor. Viktor already mid-swing: his fist hits Jace square in the chest and Jace flies backward through the windshield of the black SUV in an explosion of glass. Rain in the lights.
[Shot 2] At 00:01.800, cut to a fast tracking shot: Jace rolls across the SUV hood and lands in a crouch, glass sliding off him. Viktor charges at him from frame left, huge and fast.
[Shot 3] At 00:03.400, cut to a close-up on Jace's forearms: he flicks both wrists, WHIP, WHIP, and two glowing cyan rings shoot out, streaking light, and lock around Viktor's arms.
[Shot 4] At 00:04.800, cut to a wide side angle: Jace yanks both rings backward with his whole body and Viktor is pulled off his feet face-first into a concrete pillar; the pillar cracks, dust bursts. [00:06.800] A beat later Rei drops into frame from the level above, landing in a crouch between them, fists already glowing violet.""",
 "Rain hammering the garage, tires hiss outside, a massive punch impact, a windshield shattering, glass raining onto metal, a thrown body denting a hood, two sharp metallic WHIP sounds, a bone-shaking concrete crack, Rei's light landing.",
 "Driving cinematic action score: heavy taiko percussion and low pulsing synth bass, hitting accents on each impact.")

C2 = clip(
 "Rei's ground-punch shockwave scatters everyone; Maya redirects her momentum off a car and launches back; Maya and Rei fight midair and Maya redirects a blast that shoves three cars across the garage.",
 "Rei, Maya and Jace (Jace only in Shot 1, tumbling). Viktor is NOT in this clip",
 """[Shot 1] Overhead angle. Rei punches the wet concrete: a circular violet shockwave ripples out, BOOM, blasting rain into mist; Jace and Maya are thrown backward off their feet.
[Shot 2] At 00:01.600, cut to a side tracking shot: Maya is flung toward a moving sedan, slaps one hand onto its hood, her palm flashes orange; the car's suspension slams down to the ground as all her momentum drives into it, and she rebounds straight back toward Rei like a launched spring.
[Shot 3] At 00:03.600, cut to a slow-motion-then-real-time midair collision: Maya and Rei meet in the air, rapid exchange: punch, block, elbow, knee, water spraying off them.
[Shot 4] At 00:05.600, cut to a close two-shot: Rei fires a violet shockwave from her palm; Maya catches Rei's wrist, twists, palm flashing orange, and redirects the blast sideways, BOOM, three parked cars are shoved sliding across the garage floor in a spray of sparks.""",
 "A deep concussive BOOM with a ripple of air, rain turned to mist, a car suspension crunching, a spring-like whoosh, rapid sharp punch and block impacts, a second BOOM, three cars scraping across concrete with screeching metal.",
 "Same driving action score, building faster, percussion hits synced to the strikes.")

C3 = clip(
 "Viktor tears off the rings and hurls a motorcycle; Maya runs across it midair and kicks Viktor, who just smiles and grabs her ankle; Jace fires all six rings and Maya turns Viktor's own force against him, blasting him through two concrete walls.",
 "Viktor, Jace and Maya. Rei is NOT in this clip",
 """[Shot 1] Medium low angle on Viktor: he tears the two cyan rings off his arms, they spin away flickering. He grabs the sport motorcycle by the frame and hurls it at Jace.
[Shot 2] At 00:01.700, cut to a wide angle: Jace ducks under the spinning motorcycle; Maya leaps onto it midair, runs across the spinning bike in two steps, springs off it and drives a flying kick straight into Viktor's jaw. His head barely turns. Viktor slowly smiles.
[Shot 3] At 00:04.000, cut to a close-up: Viktor's huge hand clamps around Maya's ankle and lifts her. Before he can slam her, Jace thrusts both arms forward and all six cyan rings fire and lock around Viktor's chest.
[Shot 4] At 00:05.800, cut to a wide symmetrical shot: Jace pulls the rings; Maya grabs Viktor's wrist, palm flashing orange, absorbs his pulling force and releases it, BOOM, Viktor rockets backward through two concrete walls in a shower of rubble and dust.""",
 "Ring hum dying as they are torn off, the scrape and roar of a motorcycle being lifted and thrown, a whistle of spinning metal, a hard kick impact, a low amused breath from Viktor, the hum of six rings locking, a massive BOOM, two walls exploding into rubble.",
 "Action score drops to a tense pulse on Viktor's smile, then slams back in full on the final blast.")

C4 = clip(
 "Silence after the blast; the ceiling buckles; Rei appears behind Jace with a charged fist; Maya shouts a warning; Jace forms all six rings into one gauntlet and meets Rei's shockwave fist-to-fist; every light explodes.",
 "Jace, Maya and Rei. Viktor is NOT in this clip",
 """[Shot 1] Wide, still, dust drifting through the fluorescent light beams, rain dripping. Jace lowers his hands, breathing hard; Maya stands a few meters behind him, screen-right. Near silence.
[Shot 2] At 00:01.800, cut to a low angle up at the ceiling: CRACK, the concrete buckles. Pull focus down to Rei silently rising behind Jace, her fist glowing intensely violet with compressed energy.
[Shot 3] At 00:03.000, cut to a close-up on Maya's face seeing it. MAYA shouts: <d>[English] JACE!</d>
[Shot 4] At 00:04.000, cut to a dynamic orbiting close shot: Rei punches; Jace spins, and all six cyan rings snap together around his right forearm into one massive glowing gauntlet; fist meets violet shockwave head-on.
[Shot 5] At 00:06.000, cut to the widest shot: a blinding cyan-and-violet flash, BOOOOOM, every fluorescent light in the garage explodes in a chain of sparks. At 00:07.400 the frame cuts to pure black and holds black to the end.""",
 "Dripping water and settling dust, heavy breathing, a sharp CRACK of concrete, a rising energy whine, Maya's shout, the metallic clack of six rings fusing into a gauntlet, a colossal BOOOOOM, a cascade of exploding fluorescent tubes, then sudden silence on black.",
 "Score cuts to silence for the stillness, a single rising synth swell under the ceiling crack, a huge final hit on the impact, then nothing on black.")

if __name__ == "__main__":
    refs = ["jace-ref.jpeg", "maya-ref.jpeg", "viktor-ref.jpeg", "rei-ref.jpeg", "garage-ref.jpeg"]
    ids = []
    for i, (c, seed) in enumerate(((C1, 650001), (C2, 650002), (C3, 650003), (C4, 650004)), 1):
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
