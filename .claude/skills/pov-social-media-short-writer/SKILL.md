---
name: pov-social-media-short-writer
description: >
  Generate high-retention English POV/"caught on camera" short-form videos for Facebook
  Reels, TikTok, and YouTube Shorts, formatted as MiniMax H3 generation prompts.
  Specializes in realistic handheld spontaneous-phone-footage scenes — relationship,
  cheating, family, betrayal, and awkward-moment conflicts — with immediate hooks,
  natural conversational English dialogue, exactly two speaking characters (both
  visible, no off-screen voices), believable escalation, and a strong twist/reveal
  ending. Distinct from cinematic short-drama skills: no baked-in captions/overlays
  (a caption is generated and burned on separately, after rendering) and no polished
  cinematography — this looks like it was filmed by a bystander on their phone.
---

# POV / Social-Media Short Writer

Use this skill to create **short, spontaneous-feeling "caught on camera" videos** for
social video — the found-footage / POV social feed aesthetic, as opposed to a
polished scripted drama.

The target is not cinematic storytelling. The target is:

- immediate comprehension
- strong curiosity in the first second
- realistic, grounded conflict or moment
- high comment potential
- believable characters
- short dialogue
- a satisfying twist, reveal, punchline, or unresolved ending
- prompts that are easy for video-generation models to execute

The default production target is **16 seconds total** — **2 independently generated
8-second clips**.

This is a sibling skill to `english-short-drama-writer` and
`filipino-ragebait-short-drama-writer` — same underlying format discipline — but the
visual style is handheld spontaneous phone footage, not a cinematic two-shot.

---

# 0. THE FORMULA — read this first, it overrides anything below

These scripts are **arguments, not narratives.** The viewer is a participant who is on
the wronged party's side from word one, and the entertainment is watching the other
person incriminate themselves further. Everything else in this skill follows from that.

```text
OUTRAGEOUS HOOK → 1 SHORT QUESTION → SHAMELESS ANSWER → WORSE REVEAL
→ "FUCK YOU" LEVEL REACTION → FINAL LINE THAT MAKES THEM EVEN WORSE
```

## Mapping six beats onto two clips

POV is 16s, so the beats compress — they do not get cut:

```text
Clip 1:  OUTRAGEOUS HOOK → 1 SHORT QUESTION → SHAMELESS ANSWER
Clip 2:  WORSE REVEAL → "FUCK YOU" LEVEL REACTION → FINAL LINE THAT MAKES THEM WORSE
```

Hard consequences:

- **No exposition.** You do not brief a participant.
- **No follow-up questions after a reveal.** The surrogate would be asking what the
  audience already worked out.
- **The guilty party NEVER apologises.** An apology ends an argument, and the argument
  is the product. They justify instead.

## The two roles (GENDER-FREE)

Every script has one **shameless escalator** and one **terse surrogate**.

**Never assign these roles by gender.** Anyone can be absurdly rude and bad, and mixed
combinations are encouraged — two women, two men, older against younger, in-law against
spouse. Writing "the man is always the bad one" is both lazy and sexist.

The **shameless escalator** doesn't get louder, they get *more self-incriminating*. Every
line worsens their own position. The **terse surrogate** stays short, because the
audience already agrees with them — brevity signals they're right, over-explaining reads
as pleading:

```text
Too?
Fuck you.
What the fuck.
```

## The reaction beat in English

"Gago ka" maps to **"Fuck you."** or **"What the fuck."** — a short, crude, unanswerable
verdict. Do NOT soften it into something composed like "You're disgusting" — that reads
as too controlled for this beat and kills the rage.

## Accidental information beats object discovery

**This supersedes the "Two hook styles" guidance in §6.** The strongest hook is not a
discovered object — it is a line that leaks more than the speaker intends, while they
are busy managing a *smaller* crisis:

```text
You can't be pregnant too!   → "Too?"          (a second pregnancy, in one word)
Are you married?  → Not yet. Tomorrow.          (the wedding is tomorrow)
```

The audience solves it before anyone explains. Being ahead of the characters IS the
hook. Object discovery still works, but it is now the *weakest* of the three hook
styles — reach for accidental information first, mid-argument accusation second.

## The final line beats a twist

A final line that adds a fresh layer of humiliation is stronger than a twist reveal,
because it retroactively poisons the scene. Leave the aftermath unresolved — do not
resolve who leaves, who wins, or what happens next.

## Repetition: escalate, don't restructure

Rotate the **source of outrage**. Cheating, pregnancy and "other woman" are heavily
overused. Reach for: money, laziness, in-laws, status, work, parenting, inheritance,
body insults, entitlement, exes, weddings, household labour.

But **keep the six beats fixed.** The skeleton should stay recognizable. The variation
lever is going *harder inside it* — pile up more absurdity, stack more rage, build the
tension higher each script. **A script that feels same-y is under-escalated, not
over-structured.**

---

# 1. Core Creative Goal

Create scenes that make the viewer immediately think or comment things like:

- "Wait, what?"
- "No way this is real."
- "The way she just said that..."
- "I'd have left right there."
- "Is he serious right now?"
- "This is so awkward I can't."
- "Okay but why is she so calm about this."

The best scripts produce **curiosity and argument in the comments**, not just passive
watching.

Do not write villains who sound like cartoon villains. The most effective moment is
usually someone saying something infuriating, suspicious, or absurd **while genuinely
believing they are being reasonable or that they won't get caught**.

---

# 2. Default Format

Unless the user says otherwise:

- 2 clips
- 8 seconds per clip
- 16 seconds total
- **exactly 2 speaking characters per clip, both visible — never more, and no
  off-screen voice** (see §4 — this includes the person filming: they never speak)
- no on-screen caption, text overlay, or social-media UI of any kind (added separately
  in post-production — never describe one in the prompt)
- no background music
- natural, spontaneous-feeling behavior — not staged or theatrical
- one continuous shot per 8-second clip, no internal cuts
- hard cut at the end of the final clip
- do not over-explain the backstory

Each clip should be independently understandable enough for separate AI generation.

Use this separator between clips:

```text
=====
```

---

# 3. The Most Important Rule: Hook at Second 0

The **first spoken line, or the first thing visibly happening, must already contain
the hook** — the interesting, awkward, suspicious, or surprising thing the viewer
stumbled into.

Do not waste the opening on:

- walking into a room
- greetings
- establishing who everyone is
- unnecessary setup
- characters entering and sitting down
- long visual descriptions before something happens

The opening should make the viewer understand within 1-2 seconds that they've
stumbled into the middle of something.

## Strong hook examples

```text
Why do you have two toothbrushes in here?
```

```text
Wait, is that her ringtone on your phone?
```

```text
Whose bag is this in the closet?
```

```text
You told me you were working late.
```

```text
Why does she have a key to this apartment?
```

## Absurd-but-realistic hooks (raw and blunt)

Some of the highest-performing hooks (validated on the Tagalog series — see the
`filipino-ragebait-short-drama-writer` skill) are almost too blunt to sound written.
That's exactly why they work: a person hurt or furious enough will actually blurt out
something this raw — it isn't composed, it's involuntary.

```text
You don't even know who the father is?
```

```text
You were seeing both of us at the same time?
```

```text
So what am I to you, an option?
```

These work as either a blunt accusation stripped of any softening, or a self-directed
rhetorical insult thrown back at the accuser — shocking enough to stop a scroll, but
still something a real person would actually say mid-fight, not a surreal or
cartoonish line. Keep it platform-safe (no slurs) while keeping the rawness. Vary the
specific line across scripts rather than reusing the same one.

A hook should usually be:

- accusatory, suspicious, or curious
- revealing
- unexpected
- morally questionable or ambiguous
- occasionally raw/blunt enough to sound involuntary (see "Absurd-but-realistic hooks"
  above)

---

# 4. THE #1 FAILURE MODE — Exactly Two Speakers, Full Stop

MiniMax H3 becomes unreliable and confusing with three or more speaking voices in a
clip — even if only two people are ever visible. It loses track of who is speaking,
struggles to correctly withhold lip movement from a voice that has no visible mouth,
action and dialogue fall out of sync, and the result is unusable.

**Hard rule: exactly two visible characters per clip, and only those two ever speak.
Never a third voice — not a crowd, not a narrator, and not an off-screen "person
filming" voice either.** This skill deliberately does NOT use a POV voice/off-screen
speaker, even though the content is filmed POV-style — the camera can imply someone is
holding the phone without that person ever talking. If the two-visible-characters rule
was the first fix, this is the second: adding a third speaking identity — even
invisible — reintroduces the same confusion in a different form.

A third person may exist only as:

- mentioned but off-screen and silent ("She's still messaging him.")
- heard but not as speech (a phone ringing, a door closing, a voice from another room
  that is not written as dialogue)
- the person filming, implied only through camera movement/reactions — they never
  speak, never get a speaker ID, and are never written as saying anything

---

# 5. Action and Dialogue Must Stay in Sync

A recurring failure: the prompt describes a physical action, and then separately
describes dialogue that reads as happening afterward or unrelated to it, so the
rendered clip shows the action completing in silence and the line landing over a
static beat.

**Fix: describe the action and the line that accompanies it in the same beat, in the
order they actually happen together — not as two separate sequential paragraphs.**

Good (action and line fused into one beat):

```text
She pulls the second toothbrush out of the cup and holds it up without a word, waiting.
```

```text
He glances at the toothbrush, then looks away instead of answering.

HE (S2), still not looking at her, says: <d>[English] It's for guests.</d>
```

Bad (action described, then a disconnected line that isn't clearly timed to it):

```text
She checks the bathroom. Later she confronts him about something.

HE: <d>[English] It's for guests.</d>
```

Keep physical action simple — one clear beat per line of dialogue, not a chain of
unrelated actions stacked before the line finally lands.

---

# 6. Escalation Pattern

Use this default two-clip pattern.

## Clip 1 — The hook

Start immediately with the suspicious, awkward, or curious moment — a question or
discovery. The other character reacts, deflects, or gives an explanation that doesn't
quite land. End clip 1 with the audience wanting clarification.

## Clip 2 — Payoff

Push the same beat one step further, then deliver — in this order of preference, per §0:

- **a final line that makes them even worse** (a fresh layer of humiliation that
  retroactively poisons the scene) — strongest, reach for this first
- a hypocritical or absurd justification
- a dismissive final line
- a statement that reframes everything the viewer thought was happening
- an unresolved, stunned reaction
- a twist reveal — now the *weakest* option; §0 demotes twists below humiliation

Do not introduce a whole new escalation step before the payoff — with only 2 clips,
clip 2 has to carry both the "it gets worse" beat and the payoff in one continuous
shot.

Then:

```text
Hard cut on the reaction. Do not resolve. Do not explain further.
```

## Two hook styles

The hook can come from either:

- **Object discovery** — a physical thing that shouldn't be there (toothbrush, ringtone,
  bag in the closet). The dialogue then interrogates the object.
- **Argument mid-scene** — no physical object at all; the camera simply catches an
  accusation already in progress, and the defense line is what makes it land. This is
  the default hook style in the sibling `english-short-drama-writer` skill (see its §4A)
  and works just as well here — don't over-rely on discovered objects.

Worked example, argument style (no object needed):

```text
Clip 1:
You told her you miss her?
We're just friends.
You tell all your friends you love them?
You're making this bigger than it is.

Clip 2:
You deleted the messages.
Because I knew you'd react like this.
```

```text
Clip 1:
You gave her money again?
She needed help.
She's your ex.

Clip 2:
So I'm supposed to let her struggle?
You told me we couldn't afford daycare.
```

Notice the payoff in both is the defense line itself ("You're making this bigger than
it is," "So I'm supposed to let her struggle?") — not a discovered object, not a twist.
That's what should make viewers argue in the comments.

---

# 7. Dialogue Style

Dialogue should sound like real, unscripted conversation.

Prefer short sentences. Do not make anyone speak like a writer.

## Good

```text
Why does your location say you're still there?
```

```text
I told you, I left an hour ago.
```

```text
Then why is your car still in the driveway?
```

## Too written

```text
I cannot believe you would deceive me in such a calculated and deliberate manner.
```

Avoid that.

---

# 8. Speaker Lock and Dialogue Preservation

When writing MiniMax H3 prompts, dialogue must be preserved exactly and speakers must
never be ambiguous.

Always include a speaker lock:

```text
Speaker lock: Only [NAME], the [description] (S1), speaks S1. Only [NAME], the
[description] (S2), speaks S2. Never swap dialogue, voices, or lip movements between
them.
```

Always include:

```text
CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Do NOT swap pronouns (e.g. do not change "you" to "I" or vice versa).
Do NOT alter verb tense.
Do NOT paraphrase, normalize, or rewrite the dialogue.
```

If a specific word or phrase matters to the plot, reinforce it explicitly, e.g.:

```text
IMPORTANT: The exact word is "guests," not "gifts."
```

---

# 9. Audio Rule for MiniMax H3

Always include:

```text
CRITICAL AUDIO RULE:
There is NO narrator and NO disembodied voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud, by the two visible
characters (S1, S2). No other voice speaks — not the person filming, not anyone
off-screen.
Everything outside <d>...</d> is SILENT visual direction only.
```

Never put spoken content outside `<d>` tags.

---

# 10. H3 Prompt Template

Use this template for full generation prompts.

```text
8 | integrated_multimodal_description: [Shot 1] Photorealistic spontaneous handheld
smartphone footage inside [LOCATION], [TIME OF DAY]. Vertical, casual, imperfect
framing, natural camera movement — this feels captured in the moment, not
professionally filmed.

There are exactly two visible adult characters.

CHARACTER A is [age, appearance, clothing, emotional state].

CHARACTER B is [age, appearance, clothing, emotional state].

They are [relationship].

Both speak natural conversational English.

CRITICAL AUDIO RULE:
There is NO narrator and NO disembodied voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud, by the two visible
characters (S1, S2). No other voice speaks.
Everything outside <d>...</d> is SILENT visual direction only.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Do NOT swap pronouns. Do NOT alter verb tense. Do NOT paraphrase or rewrite.

The camera holds a handheld medium shot, natural small movement, slightly imperfect
framing. Neither visible character looks at the camera unless the situation
specifically requires acknowledging the person filming.

[Action and the line that accompanies it, fused into one beat — see §5.]

CHARACTER A (S1), [delivery], speaks the VERY FIRST LINE: <d>[English] HOOK LINE</d>

[Character B's reaction, fused with their line.]

CHARACTER B (S2), [delivery], replies: <d>[English] RESPONSE</d>

Speaker lock: Only CHARACTER A speaks S1. Only CHARACTER B speaks S2. Never swap
dialogue, voices, or lip movements.

overall_soundscape: [Natural, realistic ambience for the location.]

non_diegetic_music: N/A

=====

[Repeat the template for clip 2 — same location and characters, continuing the
situation straight to the payoff per §6. Repeat full character descriptions again; do
not assume the model remembers clip 1.]
```

---

# 11. Visual Simplicity

AI generation works better when scenes are simple. This is doubly important here
since keeping the model from getting confused is the #1 priority (see §4).

Prefer:

- bedroom, living room, kitchen, bathroom, hallway, car, driveway, front porch
- one clear, static-ish location per clip

Avoid:

- any background characters, even briefly visible ones
- crowds, parties, restaurants with visible other patrons
- complex choreography or characters moving through multiple rooms
- multiple simultaneous actions
- phones with readable text on screen
- physical altercations

Exactly **two visible characters** is the hard default. No exceptions.

---

# 12. Acting Direction

Use:

- natural
- suspicious
- defensive
- caught off guard
- quietly panicking
- dismissive
- trying to stay calm
- stunned

Avoid constant shouting. A calm, deflecting answer is often more effective — and more
believable as real footage — than a screaming reaction.

Example:

```text
He answers flatly, already reaching for an explanation, like he's said it before.
```

That produces a stronger result than:

```text
He panics and yells.
```

---

# 13. Strong Final Lines

The final line should be memorable and concrete.

Good categories:

## Dismissive

```text
It's not what it looks like.
```

## Hypocritical

```text
You're being paranoid.
```

## Reveal

```text
She's coming over Friday too.
```

## Cold admission

```text
Yeah. I know.
```

## Comeback

```text
Since when do guests need two?
```

Avoid vague endings like "There's something I need to tell you." Land one concrete
fact or line instead.

---

# 14. What to Avoid

- **Any third speaking voice, visible or not** — including an off-screen "person
  filming" voice (see §4 — the single most important rule in this skill).
- **Action described separately from the dialogue it should sync to** (see §5).
- On-screen captions, text overlays, subtitles, usernames, reaction counters, or any
  platform branding — never describe these, they are added separately in post.
- Excessive exposition — let dialogue and behavior reveal the situation.
- Any narrator or voice-over of any kind — the camera work carries the POV feel, no
  voice needs to.
- Cartoon-villain behavior — the best moments come from someone who thinks they're
  being reasonable.
- Recycling the same excuse/twist pattern across consecutive scripts.

---

# 15. Quality Check Before Output

Before returning a script, verify:

- Are there **exactly two speaking characters, both visible**, and no more, in every
  clip — with no off-screen or narrator voice of any kind?
- Does the first spoken line or visible moment hook immediately?
- Is every action fused with the dialogue it accompanies, not described separately?
- Are speaker locks explicit and unambiguous?
- Is the dialogue short, natural, and free of exposition?
- Does each clip escalate?
- Does the final line land a concrete twist, reveal, or reaction — not something vague?
- Is there zero on-screen text/caption described anywhere?
- Are characters, clothing, and location consistent across both clips?
- Is the story distinct from recent scripts (not a recycled premise/twist)?

If any answer is no, revise before output.
