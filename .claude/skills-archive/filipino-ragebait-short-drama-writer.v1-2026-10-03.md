---
name: filipino-ragebait-short-drama-writer
description: >
  Generate high-retention Filipino short-form drama scripts and MiniMax H3-ready prompts
  for Facebook Reels, TikTok, and YouTube Shorts. Specializes in realistic husband-wife,
  family, OFW, money, cheating, in-law, work, and relationship conflicts with immediate
  ragebait hooks, natural Tagalog/Taglish dialogue, believable escalation, and strong
  24-second endings designed to trigger comments and continued viewing.
---

# Filipino Ragebait Short Drama Writer

Use this skill to create **short, emotionally triggering Filipino drama scripts** for social video.

The target is not traditional teleserye writing. The target is:

- immediate comprehension
- strong emotion in the first second
- realistic conflict
- high comment potential
- believable characters
- short dialogue
- a satisfying sting, betrayal, reveal, or unresolved ending
- prompts that are easy for video-generation models to execute

The default production target is **24 seconds total**, usually **3 independently generated 8-second clips**.

---

# 0. THE FORMULA — read this first, it overrides anything below

These scripts are **arguments, not narratives.** The viewer is a participant who is on
the wronged party's side from word one, and the entertainment is watching the other
person incriminate themselves further. Everything else in this skill follows from that.

```text
OUTRAGEOUS HOOK → 1 SHORT QUESTION → SHAMELESS ANSWER → WORSE REVEAL
→ "GAGO KA" LEVEL REACTION → FINAL LINE THAT MAKES THEM EVEN WORSE
```

Hard consequences of the above:

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
line they speak worsens their own position:

```text
Mabaho siya, pero mas masarap naman.
Asawa mo 'ko. Responsibilidad mo rin ako.
Hinaan mo boses mo. Siya nagbabayad ng condo.
```

The **terse surrogate** stays short, because the audience already agrees with them.
Brevity signals they're right; over-explaining reads as pleading:

```text
Rin?
Gago ka!
Kapal ng mukha mo.
Anong kinalaman...?
```

## Make the two characters visually unmistakable, not just gender-free

Roles are gender-free (above), but the two characters' physical design still needs to
be impossible for the model to confuse. Two real incidents on this account: a wife's
face rendered sliding into her husband's mid-clip (`mara-vince-household-redo`), and a
mother rendered looking like her own daughter (`bea-wedding-venue-betrayal`,
`claire-fake-baby-cover` — both mother/daughter family scenes). Default to a visually
obvious distinguishing axis between the two characters — different gender, or if both
are the same gender (a mother/daughter scene, two sisters), a real age gap with its own
visual markers (grey-streaked hair, fine lines, a more mature build — not just a number
in the bio) plus an explicit **CRITICAL CHARACTER IDENTITY LOCK** block repeated in
every clip naming which one must always look older, and stating they must never swap
faces/ages/hair/build/wardrobe/voice. Still flag to the user that a same-gender,
similar-age pairing is harder for the model to keep straight than a visually distinct
pair would be.

## Accidental information — the strongest hook

The best hooks leak more than the speaker intends, while they are busy managing a
*smaller* crisis:

```text
Hindi pwedeng buntis ka rin!   → "Rin?"        (a second pregnancy, in one syllable)
Kasal ka na?  → Hindi pa. Bukas pa.            (the wedding is tomorrow)
```

The audience solves it before anyone explains. Being ahead of the characters IS the hook.

## The final line beats a twist

You no longer need a "Kilala mo siya" style cliffhanger. A final line that adds a fresh
layer of humiliation is stronger, because it retroactively poisons the scene:

```text
Hinaan mo boses mo. Siya nagbabayad ng condo.
```

Leave the aftermath unresolved. Do not resolve who leaves, who wins, or what happens next.

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

- "Grabe naman 'yan."
- "Iwan mo na."
- "Ang kapal."
- "May point ba siya?"
- "Hindi dapat ganyan ang asawa."
- "Ganito talaga sa pamilya."
- "Naranasan ko rin 'to."
- "Ako lang ba naiirita?"
- "Tama ba siya o mali?"

The best scripts produce **argument in the comments**, not just sympathy.

Do not write villains who sound like cartoon villains.

The most effective antagonist is usually someone who says something infuriating **while genuinely believing they are being reasonable**.

A believable justification should pass four checks:

1. Technically understandable
2. Emotionally outrageous
3. Self-serving
4. Plausible enough that some viewers might actually defend it

"Pamilya ko rin naman sila" passes all four — that's why it works. "Wala akong pakialam sa nararamdaman mo" passes none of them — that's a cartoon villain line, not ragebait.

---

# 2. Default Format

Unless the user says otherwise:

- 3 clips
- 8 seconds per clip
- 24 seconds total
- exactly 2 visible characters per clip
- no narrator
- no voice-over
- no background music
- natural Filipino acting
- natural conversational Tagalog or Taglish
- one continuous shot per 8-second clip
- hard cut at the end of the final clip
- do not over-explain the backstory

Each clip should be independently understandable enough for separate AI generation.

Use this separator between clips:

```text
=====
```

---

# 3. The Most Important Rule: Hook at Second 0

The **first spoken line must already contain the conflict**.

Do not waste the opening on:

- greetings
- "May sasabihin ako"
- "Can we talk?"
- establishing dialogue
- unnecessary setup
- characters entering and sitting down
- long visual descriptions before speech

The opening line should make the viewer understand the problem immediately.

## Strong hook examples

```text
Hindi kita niloko. Nag-chat lang kami.
```

```text
Hindi naman trabaho 'yang ginagawa mo sa bahay.
```

```text
Ako na nga nagtatrabaho, ako pa magluluto para sa'yo?
```

```text
Simula nung kumikita ka, ang damot mo na.
```

```text
Binenta mo yung lupa ko nang hindi ako tinatanong?
```

```text
Ano ako, pang one night stand lang?
```

```text
Bakit di mo alam kung sino ang ama?
```

```text
Hindi ka pa rin mabuntis? Anong silbi mo sa anak ko?
```

## Absurd-but-realistic hooks (raw and blunt)

Some of the highest-performing hooks are almost too blunt to sound written — and that's
exactly why they work. A real person hurt or furious enough will actually blurt out
something this raw and direct; it isn't clever or composed, it's involuntary.

```text
Di mo alam sino tatay?
```

```text
Pinagsabay mo kami dalawa?
```

```text
Pokpok ba ako?
```

These land because they are:

- either a blunt accusation stripped of any softening, or a self-directed rhetorical
  insult thrown back at the accuser ("Pokpok ba ako?")
- shocking enough to stop a scroll, but still grounded — a real person could actually
  say this mid-fight, not a surreal or cartoonish line
- short enough to read as one gut-reaction, not a composed sentence

Use this style for the opening line or the final gut-punch line. Vary the specific
insult/accusation across scripts — don't reuse the exact same raw line repeatedly.

A hook should usually be:

- accusatory
- dismissive
- insulting
- shocking
- unfair
- revealing
- morally questionable
- occasionally raw/blunt enough to sound involuntary (see "Absurd-but-realistic hooks" above)

---

# 4. Best Ragebait Structure

Use this default escalation pattern.

## Clip 1 — The trigger

Start immediately with the most controversial line.

The second character reacts.

End clip 1 with the audience wanting clarification.

### Example pattern

```text
HUSBAND:
Hindi naman trabaho 'yang ginagawa mo sa bahay.

WIFE:
Anong ibig mong sabihin?

HUSBAND:
Nasa bahay ka lang naman buong araw.
```

---

## Clip 2 — Make it worse

The victim explains the obvious problem.

The other character **does not apologize**.

Instead, they minimize, justify, deflect, or reveal a selfish worldview.

### Example pattern

```text
WIFE:
Nagluto ako, naglinis, naglaba, nag-alaga ng anak natin buong araw.

HUSBAND:
Eh responsibilidad mo naman 'yan.

WIFE:
Responsibilidad ko lang?
```

This is often more effective than introducing a giant twist too early.

---

## Clip 3 — Ragebait payoff

Deliver one of these:

- a cruel justification
- a betrayal reveal
- a hypocritical statement
- a dismissive final line
- a simple comeback
- a statement that makes viewers furious
- an unresolved consequence

### Example pattern

```text
HUSBAND:
Ako naman nagbabayad ng lahat dito.

WIFE:
So dahil ikaw kumikita, ako na lahat sa bahay?

HUSBAND:
Eh ano pa bang ginagawa mo?

WIFE:
Sige. Bukas, wala akong gagawin.
```

Then:

```text
CUT ABRUPTLY.
```

---

# 5. Keep the Conflict Realistic

Prefer common Filipino relationship and family issues.

## High-performing conflict categories

### Marriage / live-in relationships

- housework imbalance
- unemployed/tambay partner
- salary inequality
- hidden spending
- emotional cheating
- deleted chats
- exes
- double standards
- childcare imbalance
- husband treating parenting as "helping"
- wife or husband financially supporting extended family without consent
- controlling friendships
- career resentment
- stay-at-home spouse being dismissed
- one partner telling the other to resign

### Money

- lending spouse's savings without permission
- giving money to parents/siblings
- unpaid debts
- tuition money
- remittances
- inheritance
- selling property without consent
- hidden loans
- salary entitlement
- "pera ko naman 'to"
- breadwinner pressure

### OFW

Excellent ragebait category.

Use themes such as:

- returning home and discovering savings are gone
- tuition was requested even though child stopped school
- unfinished house despite years of remittances
- spouse spent remittances on relatives
- children becoming distant
- family hiding major problems
- spouse making major financial decisions alone
- OFW sacrifice being taken for granted
- sibling debt being paid using OFW money

Important: do not repeat the same trope too often.

Avoid leaning repeatedly on:

```text
Pamilya ko rin naman sila.
```

Find fresher justifications.

### In-laws

- mother-in-law insulting infertility
- spouse refusing to defend partner
- in-law moving in without agreement
- money sent to parents
- comparison with siblings
- "Nanay ko 'yan. Ikaw ang makisama."

### Cheating / emotional cheating

- "Nag-chat lang kami."
- deleted messages
- calling another person "babe"
- secret emotional intimacy
- saying "wala namang nangyari"
- hidden girlfriend/wife
- post-intimacy betrayal
- "hindi naman tayo"
- service elevator / hidden exit
- partner minimizing behavior

### Adult children / parents

- tuition deception
- joblessness
- financial dependence
- lying about graduation
- hidden pregnancy
- inheritance
- parents demanding salary
- comparing siblings

### Domestic / gender unfairness

A third major lane on its own — not just a subset of "Marriage / live-in relationships" above. Pull it out and use it deliberately:

- stay-at-home parent dismissed as lazy
- housework framed as "not real work"
- unequal childcare split
- invisible mental load
- one partner earning much more, using that as leverage
- "nasa bahay ka lang naman buong araw"
- son financially prioritized over daughter
- double standards between husband and wife

Strongest framing: *"You benefit from my sacrifice, then tell me it doesn't count."*

## Ideal content mix

When generating a batch of concepts, roughly prioritize:

- 50% family / money / relationship betrayal
- 25% high-stakes cheating / relationship betrayal
- 15% domestic / gender / invisible-labor conflict
- 10% experimental

Directional, not strict — but money/family should dominate the batch, not cheating.

## Combine categories for stronger stories

The strongest concepts often stack two lanes instead of one:

- **Money + cheating** — husband secretly pays another woman's rent; wife discovers the missing ₱80,000 was for another woman's pregnancy.
- **Family + money** — husband empties the emergency fund for his brother; parents use an OFW child's remittance for another sibling.
- **Family + cheating** — mother-in-law already knew about the husband's kabit; sister covers for a cheating brother.
- **Pregnancy + cheating** — use selectively, for high-impact swings: "Buntis siya. Pero hindi raw siya kabit."

A single-lane conflict ("your brother borrowed money") is weak. A stacked one ("you maxed out our joint card for your brother's failing business") is strong.

---

# 6. Dialogue Style

Dialogue should sound like actual Filipino conversation.

Prefer short sentences.

Do not make everyone speak like a writer.

## Good

```text
Kaibigan ko lang siya.
```

```text
Kaibigan? Tinatawag ka niyang babe.
```

```text
Tawagan lang namin 'yon.
```

## Too written

```text
How can you possibly expect me to believe that your emotional attachment to her is merely platonic?
```

Avoid that.

---

# 7. Natural Tagalog and Taglish

Use Tagalog or Taglish based on the characters.

For middle-class Metro Manila couples, natural Taglish is fine.

Examples:

```text
Akala ko may something tayo.
```

```text
Lara, hindi naman tayo.
```

```text
So ano 'to?
```

For family conflict, straightforward Tagalog often works better.

```text
Tatlong taon akong nagtrabaho abroad para sa pera na 'yon.
```

Do not force deep or old-fashioned Tagalog.

---

## 7.1 Always specify the Filipino accent — in EVERY shot

**Writing `[Tagalog]` is NOT enough.** Multilingual generators often recognise Tagalog
vocabulary correctly but still pronounce it with English phonetics, English vowels,
unnatural stress, or a vaguely foreign accent.

Every independently generated shot with Tagalog or Taglish dialogue must carry an
explicit accent block **outside** the spoken dialogue:

```text
Both characters are native Metro Manila Filipino speakers.
They speak natural contemporary Tagalog/Taglish with authentic Metro Manila Filipino pronunciation.
Use clear Filipino vowels and natural Filipino rhythm.
Do NOT use an American, English, Spanish, or other foreign accent when speaking Tagalog.
Do NOT anglicize Filipino vowels.
Do NOT speak any pronunciation instructions aloud.
```

**Repeat this block in EVERY shot.** Do not assume Shot 1's pronunciation instructions
carry into Shot 2 or 3 — clips are generated semi-independently and the accent drifts
between them.

Weak, gives the generator almost nothing:

```text
Both speak Tagalog.
```

## 7.2 Taglish should still sound Filipino

English words keep natural English pronunciation; Tagalog words keep Filipino
pronunciation; the transition sounds natural to a Taglish speaker. Do **not** force the
English portion into a fake Filipino accent.

```text
<d>[Taglish] You told me single ka!</d>
```

Where useful, clarify outside the line: *"At least" is English — say it naturally in
English, then transition smoothly into Filipino pronunciation for "nakatulong ka."*

Keep it conversational, not formal:

```text
GOOD:  <d>[Tagalog] Bakit mo ginawa 'to?</d>
STIFF: <d>[Tagalog] Bakit mo ginawa ito?</d>
```

## 7.3 Pronunciation-lock ONLY the words likely to fail

Do not phoneticize every word. Lock roughly **3–8 words per clip** — ones that are
frequently mispronounced, likely to be anglicized, carry the hook or punchline, or are
known previous failures.

```text
PRONUNCIATION LOCK:
- asáwa = a-SA-wa, three syllables, stress on SA
- babáe = ba-BA-e, three syllables, never pronounce it "ba-bay"
- damít = da-MIT, stress on MIT
- These pronunciation instructions are SILENT and must never be spoken aloud.
```

Locking every word makes the model pronunciation-conscious and produces robotic pacing.

**Negative instructions beat positive ones.** "Pronounce babae correctly" is weak;
"never pronounce it 'ba-bay', keep the final e audible" is what actually works.

## 7.4 Keep the layers separate

The spoken line contains ONLY what the character says. Instructions live outside it.

```text
GOOD:
<d>[Tagalog] Darating asáwa ko.</d>

PRONUNCIATION LOCK:
- asáwa = a-SA-wa, three syllables, stress on SA

NEVER — the generator may speak the instruction aloud:
<d>[Tagalog] Darating asawa ko, pronounced a-SA-wa.</d>
```

## 7.5 Pronunciation-safe spelling

**Standalone "ako" is never written "'ko".**

```text
GOOD:   <d>[Tagalog] Pagod na ako.</d>
AVOID:  <d>[Tagalog] Pagod na 'ko.</d>
```

This applies ONLY to standalone `ako`. Ordinary grammatical `ko` stays `ko`:

```text
GOOD: <d>[Tagalog] Asáwa ko siya.</d>
GOOD: <d>[Tagalog] Trabaho ko 'to.</d>
GOOD: <d>[Tagalog] Mahal ko siya.</d>
```

Vernacular contractions `'to`, `'yan`, `'yon` are fine — they reflect real Metro Manila
speech. **This is NOT a blanket "write everything uncontracted" rule.**

**Bare "Oo"** is sometimes pronounced like the English interjection "oh". Don't just
re-roll the same spelling hoping it fixes itself — use `O-o`, or rewrite naturally as
`Tama.` / `Sige.` / `Ganun na nga.` depending on context. Do not mechanically replace
every "Oo".

## 7.6 Escalation ladder — try in this order

1. Normal Filipino spelling
2. Accent / native-speaker instruction (7.1)
3. Pronunciation lock (7.3)
4. Stress mark inside the dialogue — `babáe`, `asáwa`
5. Phonetic-friendly spelling as a LAST resort — `ba-ba-e`, `O-o`

Artificial spelling hurts rhythm and delivery, so never reach for step 5 early. But
equally, do not sit on step 1 re-rolling the same spelling indefinitely — climb the
ladder.

---

# 8. Pronoun and Verb Preservation

When writing MiniMax H3 prompts, dialogue must be preserved exactly.

AI video models may accidentally change:

- `mo` to `ko`
- `ko` to `mo`
- `umalis` to `umaalis`
- tense/aspect
- key plot words

Always include:

```text
CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Preserve all Tagalog pronouns and verb forms exactly.
Do NOT replace "mo" with "ko" or "ko" with "mo."
Do NOT alter verb aspect.
Never shorten standalone "ako" into "'ko."
Normal grammatical "ko" remains "ko."
Natural vernacular contractions such as "'to," "'yan," and "'yon" are allowed.
Do NOT paraphrase, normalize, or rewrite the dialogue.
```

See §7.5 for why the `ako` / `'ko` distinction matters and why this is NOT a blanket
ban on contractions.

If a specific word matters to the plot, reinforce it.

Example:

```text
IMPORTANT:
The exact word is "umalis," NOT "umaalis."
```

---

# 9. Audio Rule for MiniMax H3

Video models may vocalize visual directions if the prompt is not strict.

Always include:

```text
CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.
```

Never put spoken content outside `<d>` tags.

---

# 10. H3 Prompt Template

Use this template when the user requests full generation prompts.

```text
8 | integrated_multimodal_description: [Shot 1] Photorealistic contemporary Filipino drama inside [LOCATION] in [TIME OF DAY]. Natural restrained acting, realistic emotional tension, believable Filipino behavior.

There are exactly two visible adult characters.

CHARACTER A is [age, appearance, clothing, emotional state].

CHARACTER B is [age, appearance, clothing, emotional state].

They are [relationship].

Both speak natural conversational [Tagalog/Taglish].

CRITICAL AUDIO RULE:
There is NO narrator.
There is NO voice-over.
ONLY dialogue written inside <d>...</d> may be spoken aloud.
Everything outside <d>...</d> is SILENT visual direction only.

CRITICAL DIALOGUE PRESERVATION:
Speak every <d> line EXACTLY as written.
Preserve all Tagalog pronouns and verb forms exactly.
Do NOT replace "mo" with "ko" or "ko" with "mo."
Do NOT alter verb aspect.
Do NOT paraphrase, normalize, or rewrite the dialogue.

The camera holds a continuous medium two-shot.

[Visual action.]

CHARACTER A (S1), [delivery], speaks the VERY FIRST LINE: <d>[Tagalog] DIALOGUE</d>

CHARACTER B (S2), [delivery], replies: <d>[Tagalog] DIALOGUE</d>

[Reaction.]

overall_soundscape: [Natural room/environment ambience]. No narrator or voice-over. Only CHARACTER A and CHARACTER B speak.

non_diegetic_music: N/A
```

Then repeat character identity and key details for every independent 8-second clip.

Do not assume the video model remembers the previous generation.

---

# 11. Visual Simplicity

AI generation works better when scenes are simple.

Prefer:

- bedroom
- living room
- kitchen
- dining room
- hallway
- office
- restaurant table
- condo
- modest family home

Avoid:

- many background characters
- complex choreography
- multiple room changes
- phones with readable text
- multiple flashbacks
- physical fights unless essential
- three-way conversations

Exactly **two visible characters** is the default.

Other people may be mentioned but should remain off-screen.

---

# 12. Acting Direction

Use:

- restrained
- natural
- uncomfortable
- defensive
- quietly furious
- emotionally exhausted
- stunned
- ashamed
- dismissive
- irritated

Avoid constant shouting.

A calm or dismissive antagonist is often more triggering than a screaming one.

Example:

```text
He says it matter-of-factly, genuinely believing his reasoning is fair.
```

That produces stronger ragebait than:

```text
He laughs evilly.
```

Never make behavior cartoonish unless the user specifically requests comedy.

---

# 13. Strong Final Lines

The final line should be memorable.

Good categories:

## Dismissive

```text
Grabe ka. Chat lang 'yon.
```

## Entitled

```text
Eh responsibilidad mo naman 'yan.
```

## Hypocritical

```text
Pera ko naman 'to.
```

## Betrayal admission

```text
May girlfriend ako, Lara.
```

## Cold admission — NEVER an apology

Per §0, the guilty party never says sorry. Strip the apology and keep the flat,
unrepentant admission — it is colder without it:

```text
Alam ko.
```

## Comeback

```text
Mas mababa pa rin sa zero?
```

## Consequence

```text
Sige. Bukas, wala akong gagawin.
```

The ending does not always need a twist.

Sometimes the best ragebait ending is simply an infuriating statement.

---

# 14. Do Not Overuse Twists

Not every scene needs:

- secret wife
- secret child
- hidden second family
- surprise inheritance
- pregnancy
- affair reveal

A normal argument can perform better if the conflict is relatable.

Strong example:

```text
Hindi naman trabaho 'yang ginagawa mo sa bahay.
```

This works because many viewers already have an opinion before the second line.

---

# 15. Comment-Bait Logic

A strong script should leave at least one debatable question.

Examples:

- Is chatting cheating?
- Should a stay-at-home spouse handle all housework?
- Does the breadwinner get more authority?
- Can a spouse lend joint savings to family?
- Should an OFW parent blame the child or the spouse?
- Is a low-paying job better than unemployment?
- Should a wife tolerate a mother-in-law for her husband?
- Is emotional cheating still cheating if they never met?

Do not explicitly ask the audience these questions inside the drama.

Let the scene generate the argument naturally.

---

# 16. OFW-Specific Writing Rules

OFW stories should feel emotionally specific.

Useful visual details:

- large suitcase by the door
- travel jacket
- newly arrived parent
- pasalubong bag
- unopened luggage
- exhaustion from travel
- excitement turning into confusion

Good emotional contrast:

1. OFW arrives happy.
2. Small inconsistency appears.
3. Hidden truth comes out.
4. OFW realizes the sacrifice was wasted or taken for granted.

Example:

```text
Tay:
Nasaan si Carlo? Graduate na 'yon, 'di ba?

Daughter:
Tay... hindi po nagtapos si Carlo.

Father:
Eh bakit tuloy-tuloy pa rin yung hinihingi n'yong tuition sa'kin?
```

The real betrayal is often not the child failing.

It is the family **continuing to accept money while hiding the truth**.

---

# 17. Husband-Wife Ragebait Formula

These scenes work best when both sides have understandable pressures but one line crosses the line.

Example:

### Setup
Husband earns money.
Wife handles home and child.

### Bad husband logic
He thinks income contribution means household contribution is complete.

### Hook
```text
Hindi naman trabaho 'yang ginagawa mo sa bahay.
```

### Escalation
```text
Nasa bahay ka lang naman buong araw.
```

### Payoff
```text
Eh ano pa bang ginagawa mo?
```

The husband should not think he is evil.

He thinks he is stating a fact.

That is what makes viewers angrier.

---

# 18. Tambay / Unemployed Partner Formula

Avoid simply calling the unemployed partner lazy.

Give them a justification viewers will hate.

Example:

```text
WIFE:
Ilan inapplyan mo?

HUSBAND:
Wala today.

WIFE:
Tatlong buwan ka nang walang trabaho.

HUSBAND:
Eh ano gusto mo? Pumatol ako sa trabahong mababa sweldo?

WIFE:
Mas mababa pa rin sa zero?
```

This creates two camps:

- "Work is work."
- "He should wait for a better job."

That debate is useful.

---

# 19. Cheating / Chatting Formula

The rage comes from redefining cheating.

Example:

```text
HUSBAND:
Hindi kita niloko. Nag-chat lang kami.

WIFE:
Araw-araw? Hanggang madaling-araw?

HUSBAND:
Kaibigan ko lang siya.

WIFE:
Kaibigan? Tinatawag ka niyang babe.

HUSBAND:
Tawagan lang namin 'yon.
```

Then worsen it:

```text
WIFE:
Sinasabi mo sa kanya na nami-miss mo siya.

HUSBAND:
Eh hindi ko naman siya hinalikan.

WIFE:
So kailangan may halikan muna bago maging panloloko?

HUSBAND:
Grabe ka. Chat lang 'yon.
```

This is more realistic and comment-generating than immediately revealing physical cheating.

---

# 20. Post-Intimacy Betrayal Formula

Allowed tone: adult, suggestive, non-explicit.

Never show nudity or sexual activity.

Use visual implication only:

- rumpled sheets
- partially dressed adults
- fixing a shirt
- sitting at bed edge
- emotionally distant behavior

Example hook:

```text
Ano ako, pang one night stand lang?
```

Good escalation:

```text
Akala ko may something tayo.

Lara, hindi naman tayo.

So ano 'to?
```

Good betrayal ending:

```text
May girlfriend ako, Lara.

Gago ka. Niloko mo ako.

Alam ko. I'm sorry.
```

Keep adults clearly adults.

---

# 21. What to Avoid

Do not write:

### Too much exposition

Bad:

```text
As you know, I have been working in Dubai for the past three years sending you money every month...
```

Good:

```text
Tatlong taon akong nagpapadala.
```

### Redundant exposition

If the audience already understands it, do not repeat it.

### Generic filler

Avoid:

```text
Hindi mo naiintindihan.
```

unless followed by something specific.

### Recycled family line

Avoid repeatedly using:

```text
Pamilya ko rin naman sila.
```

It becomes predictable.

### Cartoon villains

Avoid:

```text
Wala akong pakialam sa nararamdaman mo!
```

unless context truly demands it.

### Fake cliffhangers

Avoid:

```text
May isa pa akong sikreto...
```

with no meaningful payoff.

---

# 22. Retention Rules

Every 8-second clip needs at least one meaningful development.

Do not let a clip exist only for reactions.

Ideal rhythm:

### Clip 1
Hook + reaction + worsening line

### Clip 2
Evidence + justification + new question

### Clip 3
Reveal/payoff + response + hard cut

Dialogue should be short enough for realistic delivery.

Do not cram 7 long lines into 8 seconds.

---

# 23. When the User Asks for "More Ragebait"

Do not simply rewrite the previous story with different names.

Change the **core moral issue**.

Rotate among:

- labor
- money
- loyalty
- parenting
- in-laws
- career
- OFW sacrifice
- emotional cheating
- inheritance
- boundaries
- adult children
- sibling favoritism
- gender double standards
- financial secrecy
- respect

---

# 24. Default Character Naming

Use simple, easy-to-hear names.

Examples:

- Anna
- Lara
- Mia
- Jen
- Celine
- Camille
- Bianca
- Marc
- Carlo
- Miguel
- Nico
- Daniel
- Paolo

Avoid names that sound too similar within the same scene.

---

# 25. Script-Only Mode

If the user asks for ideas, dialogue, or script only, do not automatically generate the full H3 technical prompt.

Use:

```text
CLIP 1
CHARACTER: dialogue

CHARACTER: dialogue

CLIP 2
...

CLIP 3
...
```

If the user asks for the full generation prompt, convert it into the H3 format.

---

# 26. User Preference Hierarchy

When generating content, prioritize in this order:

1. User's exact requested hook
2. Internal logic and context
3. Natural dialogue
4. Ragebait / emotional impact
5. Retention
6. Generation simplicity
7. Visual polish

Never force a twist that breaks context just because it is dramatic.

If a line feels out of context, rewrite the setup rather than defending it.

---

# 27. Concept Scoring (Before Writing)

Before writing a full script, score the concept itself — not just the finished dialogue. Rate each 0–2:

1. **Immediate hook** — can the conflict be understood in one sentence?
2. **Concrete loss** — did someone lose money, property, trust, time, family, or dignity?
3. **Shameless excuse** — does the offender have a believable but infuriating justification (see the four-part test in §1)?
4. **Comment debate** — can reasonable viewers actually disagree about part of it?
5. **Escalation room** — can each clip reveal something worse than the last?

A concept needs at least 4 of 5 to be worth writing. Reject anything that's only "someone might be cheating" — no concrete loss, no debate, nothing to escalate.

---

# 28. Quality Check Before Output

Before returning a script, verify:

- Does the first spoken line immediately hook?
- Is the conflict understandable without narration?
- Are there only two visible characters?
- Does each clip escalate?
- Is the antagonist believable?
- Is the dialogue natural Filipino speech?
- Is any line redundant?
- Does the final line sting?
- Is the final beat unresolved enough to provoke comments?
- Can each 8-second clip realistically fit the dialogue?
- Are pronouns and verb forms correct?
- Are stage directions silent?
- Is there zero narration?
- Is BGM set to N/A unless explicitly requested?
- Are characters and wardrobe repeated for independent generations?
- Is the story distinct from recent tropes?

If any answer is no, revise before output.

---

# 29. Caption Alignment

When also asked for a Facebook caption, match the same structure as the script — the caption should create an argument, not summarize the video.

Do not open with generic hooks like:

- "Wait for the plot twist."
- "You won't believe what happened."
- "Sino ba may point dito?"

Instead, lead with the outrage itself, near or in caps:

```text
GINAMIT NIYA YUNG TUITION NG ANAK NILA PAMBAYAD SA UTANG NG KUYA NIYA.
```

Then a short line of context, then end on a specific moral question — not a generic one:

```text
Tama bang tumulong sa pamilya kung sariling anak mo naman ang magsa-sacrifice?
```

A caption that just recaps the plot doesn't drive comments. A caption that takes a side — or forces the reader to — does.

---

# 30. Final Writing Principle

The best ragebait scene is not:

> "A bad person does something obviously evil."

It is:

> "A normal person says something many real people genuinely believe — and half the audience becomes furious."

Write for that tension.
