# STRUCTURES — reusable episode frameworks (funnygraph)

> Don't write scripts. Write STRUCTURES that generate scripts from graphs.
> Each structure is a function: graph → episode blueprint.
> Port to any comedian by swapping the input graph.

## THE CORE INSIGHT

Every "Why is X Funny?" episode follows the same essay arc:
1. **The transgressive clip** (grab by the throat)
2. **The question** (make them pause)
3. **The signature bits** (Trojan horse: "you might think of bits like this...")
4. **The machine** (beat-by-beat deconstruction with overlays)
5. **The philosophy** (why the machine works — BV, timing, status)
6. **The comparison** (who tries this and fails)
7. **The chronology** (how the machine evolved)
8. **The close** (thesis restated + next episode hook)

The STRUCTURE is fixed. The CONTENT is a function of the comedian.

---

## STRUCTURE 1: THE COLD OPEN

**Template:**
```
[CLIP: <comedian> at their most transgressive]
  Selection: highest-BV bit, longest pause, or darkest known_bit
  Duration: 15–30 seconds. Raw. No music.

[BEAT OF SILENCE — 2 seconds]

[TEXT ON SCREEN: "Why is that funny?"]

[JAZZ KICKS IN — hook begins]

NARRATOR:
> "You just heard <specific description of what happened>.
> And <you laughed / you felt something / something happened>
> that isn't supposed to happen.
>
> And the thing is — that's not even their best bit."
```

**Data-driven selection:**
| Input field | What to pick | Source |
|---|---|---|
| `known_bits` | Bit with longest pause or darkest theme | `known_bits[].title` + `timing_measured` |
| `theory_links.benign_violation` | Highest BV score | `theory_links` |
| `modes.repertoire` | Dominant mode's most extreme example | `modes.signature` |
| `specials_dark` | Darkest special's most famous bit | `rankings/specials_dark.json` |

**Voice options:** warm-confessional (Louis), deadpan (Norm), manic (Robin),
prophetic (Carlin), rage (Burr). The narrator's tone MATCHES the
comedian's delivery archetype — mirror the engine.

---

## STRUCTURE 2: THE QUESTION (essay pivot)

**Template:**
```
NARRATOR:
> "When you think of <comedian>, you might think of bits like this..."

[CLIP MONTAGE — 3 signature bits, 15s each, NO commentary]

> "Or maybe you think of <second theme>. Or <third theme>.
> There's a catalogue of <comedian> bits that exist in a very
> specific zone: <zone description>."

[BEAT — let it land]

> "But here's what's interesting. None of those bits are actually
> about the thing they're about. <Bit 1> isn't about <surface topic>.
> <Bit 2> isn't about <surface topic>. They're about something else
> entirely. And if you can find the thing they're all about — you'll
> find the thing that makes <comedian> the comedian they are. And
> it's not what you think."

[GRAPHIC: the deal — identity.deal one-liner]

> "This is a video about the machine that runs underneath <comedian> —
> and why the machine works. And along the way, it's going to turn
> out to be a video about why comedy works."
```

**Data-driven selection:**
| Field | What it provides |
|---|---|
| `identity.deal` | The one-sentence machine description |
| `known_bits[]` | 3 bits for the montage (pick by variety of theme) |
| `humor_type.primary` | The "zone" (dark-confessional, observational, rant...) |
| `identity.misinterpretation_rule` | The "thing they're all about" (revealed later) |

---

## STRUCTURE 3: THE MACHINE (beat-by-beat deconstruction)

**This is the core essay — the clip IS the text, annotations ARE the close reading.**

**Template:**
```
[FULL CLIP: <best measured set window>, with overlays]

BEAT-BY-BEAT WALKTHROUGH (from timing_measured + analysis):

For each beat:
  BEAT N [timestamp] "<first 8 words>"
    → [LABEL] <what's happening: PREMISE / ESCALATION / VIOLATION /
       CONFESSION / GATE / RESET / META-CONFESSION>
    → [OPERATOR: <name>] (if operator fires)
    → ⏸ PAUSE <N>s (if > 0.8s)
      INTERLUDE: "<what this pause is doing — 2-3 sentences>"

At the longest pause:
    ╔═════════════════════════════════════════╗
    ║ <THEME>: <the thing this silence proves> ║
    ║ <3-4 lines of analysis>                  ║
    ╚═════════════════════════════════════════╝

After clip ends:
NARRATOR:
> "That's the <bit name>. <duration>. <N> punch pauses.
> One <N>-second silence. And a machine that runs on <mechanism>.
>
> But this bit isn't special. It's the same machine that runs
> every <comedian> set. The machine has a name. And if you can
> see the machine, you'll see it everywhere.
>
> The machine is called <THESIS MECHANISM>."
```

**Beat classification (automatic from data):**
| Beat type | Trigger | Overlay label |
|---|---|---|
| Premise | First sentence of new topic, no joke framing | [PREMISE] |
| Escalation | Violation increases (darker/more specific) | [ESCALATION] |
| Violation | The unsayable arrives | [VIOLATION] |
| Confession | Comedian names their own mechanism | [CONFESSION] |
| Gate | Acknowledges room's discomfort | [GATE] |
| Reset | Back to normalcy after violation | [RESET] |
| Meta | Names the engine while running it | [META-CONFESSION] |

**Pause classification:**
| Pause length | Type | Interlude style |
|---|---|---|
| 0.6–1.0s | micro-punch | One line: "Just long enough for the implication to land." |
| 1.0–2.0s | standard punch | 2 sentences: what the room is absorbing |
| 2.0–4.0s | topic-pause | 3 sentences: the mechanism at work |
| 4.0s+ | confession-hold | FULL BOX: the room's decision process |

**The interlude formula (for any pause):**
```
"What happened in the <N> seconds before it: <what the room just heard>.
 The pause is <mechanism name>: <what the silence does>.
 <Why this specific length matters: not too short, not too long.>"
```

---

## STRUCTURE 4: THE PHILOSOPHY (why the machine works)

**Template:**
```
NARRATOR:
> "Every comedian who <does the thing> is doing one of three things.
> They're either doing it for <shock value / spectacle / provocation>.
> Or they're doing it as <genuine confession / craft / performance>.
> Or they're doing it as a third thing, which doesn't have a good
> name yet.

> <Comedian> is doing the third thing. And the third thing works
> because of three conditions that have to be true at the same time."

[ANIMATED TRIANGLE: Benign Violation]
  VIOLATION (top)
  BENIGN (bottom-left) ————— SIMULTANEOUS (bottom-right)

> "Condition one: <the violation>. <What's actually unsayable>.
> Condition two: <the benign frame>. <How the room stays safe>.
> Condition three: <the timing>. <What the pause does>.

> And here's the thing nobody talks about: the room is not passive.
> The audience is the fourth condition. <Split knowledge:
> the audience KNOWS it has the same thoughts.>
> The laugh is not <approval / shock / enjoyment>. The laugh is
> <recognition / relief / confession>. The laugh is the audience
> <confessing back / admitting complicity / recognizing itself>.

> This is what makes <comedian> different from <comparison type>.
> A <comparison type> <lowers someone else / goes for the gag /
> plays it straight>. <Comedian> <lowers themselves / tells the
> truth / holds the silence>. And the room trusts them because
> <reason>. And once the room trusts them, they can say anything."
```

**BV triangle data mapping:**
| Triangle vertex | Comedian-specific | Source |
|---|---|---|
| Violation | What's actually unsayable for THIS comic | `known_bits`, taboo, dark board |
| Benign | How the room stays safe | `engine.archetype_delivery`, `modes.signature` |
| Simultaneous | What the pause does | `timing_measured.punch_pauses_s` |

---

## STRUCTURE 5: THE COMPARISON (who tries and fails)

**Template:**
```
> "So why doesn't everyone do this? Because the <N> conditions are
> nearly impossible to hold simultaneously."

[COMPARISON GRID]
| Comedian | Violation | Benign frame | Simultaneous? | Result |
|---|---|---|---|---|
| <subject> | extreme | <frame> | ✅ (<pause>) | works |
| <comparison A> | moderate | none | ❌ | <fails differently> |
| <comparison B> | extreme | weak | ❌ | <fails differently> |
| <comparison C> | extreme | wrong container | ❌ | <fails differently> |

> "Take any one away and the machine breaks. That's why it's hard
> to copy. And that's why the next time you hear a comedian say
> <the thing> and the room <laughs instead of gasping> — you'll
> know exactly what's happening. The machine is running."
```

**Comparison selector (automatic):**
| Who to compare | Why | Source |
|---|---|---|
| Nearest neighbor who does it differently | Same zone, different engine | `neighbors.json` |
| Nearest neighbor who does it worse | Same zone, missing condition | `neighbors.json` + craft score |
| Famous comedian who fails at it | High-fame, low craft in this zone | `by_type` board + house rank |
| Historical precursor | Who did this first | influence graph / generation boards |

---

## STRUCTURE 6: THE CHRONOLOGY (how the machine evolved)

**Template:**
```
[TIMELINE GRAPHIC with clips]

| Year | Special | What changed | Key data |
|---|---|---|---|
| <earliest> | <special> | <engine state> | IMDb <rating> |
| <peak> | <special> | <what perfected> | IMDb <rating> |
| <current> | <special> | <where the machine is now> | — |

> "The machine <evolved / was rebuilt / was deconstructed> over
> <N> specials. <One sentence about the arc.>"
```

**Timeline data mapping:**
| Field | What it provides |
|---|---|
| `specials_rated[]` | Years + ratings + titles |
| `recognition.trajectory_2004_2017` | Rise/fall/stable |
| `generation.id` | Which era they belong to |
| `sets[]` timing status | Which sets are measured (for pause-length-over-time graphic) |

---

## STRUCTURE 7: THE CLOSE (thesis + next episode)

**Template:**
```
NARRATOR:
> "<Comedian> is not a <surface description>.
> They're a <deeper description> — and then they <what they do with it>.

> The <longest pause description> isn't a <surface thing>.
> It's <what it actually is>. And <what it actually is> is the <thing>.
> And <the thing> is the only place where you can <what comedy does>.

> They don't get away with it because they're <obvious reason>.
> They get away with it because they built a machine that <what the
> machine does>. And the machine runs on <mechanism>.

> If you want to see the machine running in a different comedian —
> one who <does the same thing differently> — the next episode is
> about <next comedian>. And the machine there is <different mechanism>."

[GRAPHIC: the pause bars — <N>s and <N>s]
[GRAPHIC: house board position — #<N>, sweep [<N>,<N>]]
[END CARD: Subscribe. Next: Why is <next comedian> Funny?]
```

**Next-episode selector:**
| Priority | Who | Why |
|---|---|---|
| 1 | Nearest neighbor with measured timing | Same mechanism, different engine |
| 2 | Nearest neighbor with different type | Same quality, different zone |
| 3 | Most-underrated (highest gap) | "The machine works but nobody knows" |
| 4 | Most-overrated (lowest gap) | "The machine is broken — why?" |

---

## STRUCTURE 8: VISUAL OVERLAY GRAMMAR

The overlay system is a **grammar**, not a template. Every clip gets
annotated with the same vocabulary:

```
OVERLAY ELEMENTS:
  [PREMISE]           — first sentence of new topic
  [ESCALATION]        — violation increases
  [VIOLATION]         — the unsayable arrives
  [CONFESSION]        — names own mechanism
  [GATE]              — acknowledges room's discomfort
  [RESET]             — back to normalcy
  [META-CONFESSION]   — names the engine while running it
  [OPERATOR: X]       — named comedy operator fires
  [STATUS: self ↓, room ↑]  — status inversion
  [BV: V=X, B=Y]     — benign-violation score
  ⏸ PAUSE [N]s       — silence timer (fires at >0.8s)
  BEAT N             — sentence counter

INTERLUDE TYPES:
  1. ONE-LINE    — micro-pause (0.6–1.0s): "Just long enough for..."
  2. TWO-SENTENCE — standard punch (1.0–2.0s): what the room absorbs
  3. THREE-SENTENCE — topic-pause (2.0–4.0s): the mechanism at work
  4. FULL BOX    — confession-hold (4.0s+): the room's decision process
  5. OPERATOR    — when an operator fires: name it, explain it, cite it
  6. COMPARISON  — when another comedian appears: what they're doing differently
  7. DATA        — when a number appears: what it means, why it matters

MUSIC RULES:
  - Silence during measured pauses (no exceptions)
  - Quiet jazz under analysis (warm, not busy)
  - Upbeat jazz for hooks and transitions
  - Single piano note after longest hold (the room exhaling)
  - No music under confession-holds (4.0s+)
```

---

## STRUCTURE 9: INTERLUDE GENERATOR

**The interlude is the analysis. It replaces narrator-over-clip.**

**Formula for any beat/moment:**
```
1. WHAT HAPPENED: <one sentence: what the room just heard>
2. WHAT IT DOES: <one sentence: the mechanism at work>
3. WHY THIS LENGTH: <one sentence: why this specific pause/moment>
4. THE CONNECTION: <one sentence: how this connects to the thesis>
```

**Example (Louis, beat 1, 2.26s pause):**
```
WHAT HAPPENED: Louis just said he's afraid of losing his memory.
WHAT IT DOES: The pause lets the premise settle — the room must
  fully accept the fear before the violation can fire.
WHY THIS LENGTH: 2.26 seconds is Attardo's premise-clarity window:
  long enough for comprehension, short enough to maintain momentum.
THE CONNECTION: This is the same premise-clarity mechanism that
  gates every violation in every Louis set.
```

**Example (Norm, beat 1, 3.5s pause):**
```
WHAT HAPPENED: Norm delivered a setup and then just... stopped.
WHAT IT DOES: The silence IS the joke. The room realizes nothing
  is coming. The nothing is the punchline.
WHY THIS LENGTH: 3.5 seconds is long enough for the room to
  give up on the punchline. The giving-up is the laugh.
THE CONNECTION: This is anti-timing: instead of holding for the
  punchline, you hold past it. The mechanism is the ABSENCE of
  the thing the room expects.
```

---

## STRUCTURE 10: EPISODE ASSEMBLY (the pipeline)

```
INPUT: comedian_id
  ↓
STEP 1: Load graph → extract thesis, engine, timing, bits, comparisons
  ↓
STEP 2: Select cold open (highest-BV bit / longest pause / darkest theme)
  ↓
STEP 3: Select 3 signature bits (variety of theme + mode)
  ↓
STEP 4: Classify beats (premise/escalation/violation/confession/gate/reset)
  ↓
STEP 5: Generate interludes (formula per pause length + operator fires)
  ↓
STEP 6: Select comparisons (nearest neighbor + famous failure + precursor)
  ↓
STEP 7: Build timeline (specials_rated + recognition + sets)
  ↓
STEP 8: Generate close (thesis restated + next-episode selector)
  ↓
STEP 9: Assemble overlay grammar (all beats labeled, all pauses timed)
  ↓
OUTPUT: episode blueprint (JSON) → script → production notes
```

**The blueprint JSON structure:**
```json
{
  "comedian": "louis-ck",
  "thesis": "The confession machine",
  "cold_open": {"bit": "van sequence", "pause": 8.16, "hook": "Why is that funny?"},
  "montage": ["van", "everything-is-amazing", "airplane"],
  "machine": {"set": "road_rage", "window": "120-240s", "beats": [...]},
  "philosophy": {"violation": "...", "benign": "...", "simultaneous": "..."},
  "comparison": {"subject": "louis-ck", "fails": ["insult", "cringe", "therapy"]},
  "timeline": [{"year": 2007, "special": "Shameless", "change": "..."}],
  "close": {"thesis": "...", "next": "norm-macdonald", "next_mechanism": "boredom"}
}
```

---

## WHY THIS WORKS

1. **Scalable:** 178 kings × 1 structure = 178 episodes. No per-comedian
   scriptwriting. The structure generates the script from the graph.
2. **Consistent:** Every episode has the same arc. The audience learns
   the structure and starts seeing it in comedy they watch.
3. **Deep:** The interlude generator forces analysis at every pause,
   every operator fire, every comparison. No hand-waving.
4. **Portable:** Port to any comedian by swapping the graph. The
   structure doesn't change. The content is a function of the data.
5. **The Trojan horse works:** The audience comes for the comedian,
   stays for the theory, leaves understanding comedy. The structure
   GUARANTEES the theory gets delivered because it's built into the
   interlude grammar.

---

## STRUCTURE 11: THE SELF-ANALYSIS (interview mining)

**Where comedians explain their own engine:**

The best comedy analysis isn't from us — it's from the comic
explaining why they work. We mine interviews for self-analysis.

**Sources (YouTube search, one-time per comic, then cache):**
- WTF with Marc Maron (the canonical comedy-interview show)
- Conan O'Brien Needs A Friend
- Joe Rogan Experience
- Letterman/Colbert/Noah (the "how do you write" segments)
- Fresh Air (Terry Gross — deep, slow, self-aware)
- Festival Q&As (Edinburgh, Just For Laughs)

**Extraction targets (what to pull from each interview):**

| What they say | What it maps to | Graph field |
|---|---|---|
| "I always start with..." | Writing process / premise source | `identity.threads` |
| "The audience doesn't know..." | Split knowledge / audience model | `operator_priors.split_knowledge` |
| "I had to learn to..." | Delivery evolution | `timing_profile.doctrine` |
| "My worst set was..." | Failure mode / what breaks the engine | `blind_spots` |
| "I think I'm funny because..." | Self-model / origin story | `identity.deal` |
| "What I'm really talking about is..." | The hidden subject | `identity.problem_space` |
| "The pause is..." | Timing self-awareness | `timing_measured` |
| "I can't do what ___ does" | Self-positioning vs neighbors | `neighbors.json` |

**The format:**
```
[CLIP: <comedian> on <show>, explaining their own process]
  Overlay: their words annotated with our operator names.
  "When Louis says 'I say terrible things because it's true' —
   that's expose_self_blindness firing in real time. He's naming
   the engine while it's running."

NARRATOR:
> "And here's the thing — <comedian> already knows how their
> machine works. They've explained it. <N> times, actually.
> Let's collect what they said and map it to the data."
```

**Why this matters:**
1. **Self-analysis is gold** — the comic's own words are the most
   authoritative source on their engine
2. **It validates our data** — if our graph says `split_knowledge: 0.85`
   and they say "I always make the audience feel like they're in on it"
   — that's independent confirmation
3. **It humanizes the analysis** — hearing them explain it is more
   engaging than reading a graph overlay
4. **It fills gaps** — blind spots, writing process, failure modes —
   things our data can't measure but interviews can

**Mining pipeline:**
```
1. Search: "<comedian> interview how do you write" (YouTube)
2. Pull: 10-20 min clips (fair use: commentary/criticism)
3. Transcribe: captions → text
4. Extract: sentences matching the extraction targets above
5. Map: each quote → graph field it confirms/challenges
6. Overlay: the interview clip with our operator annotations
```

---

## STRUCTURE 12: THE FEELING MAP (how does it make you feel + where does it take you)

**The question nobody asks in comedy analysis: what is the emotional
journey of a set? Not "is it funny" but "where does it take you?"**

**Template:**
```
NARRATOR:
> "Let's map the feeling of a <comedian> set. Not the jokes —
> the emotional geography. Where does he take you? And where
> do you end up?"

[EMOTIONAL JOURNEY GRAPH — a line chart of the audience's
 emotional state over the course of a set]

  START: curiosity / comfort
  → escalation: anxiety / recognition
  → violation: shock / guilt / relief
  → confession: intimacy / complicity
  → reset: safety / laughter
  → repeat, deeper each time
  → END: <where the set leaves you>

[OVERLAY on each section: the rasa being evoked]
  hasya → karuna → hasya → bhayanaka → shanta
```

**The rasa map for any comedian:**
| Set section | Primary rasa | Secondary rasa | Operator firing |
|---|---|---|---|
| Opening | hasya (mirth) | shanta (peace) | split_knowledge |
| Mid-set | hasya → karuna (grief) | raudra (anger) | character_violation |
| Darkest point | karuna → bhayanaka (fear) | bibhatsa (disgust) | benign_violation |
| Resolution | shanta (peace) | hasya (mirth) | expose_self_blindness |
| Closer | veera (heroism) | adbhuta (wonder) | status_reversal |

**The "where does it take you" answer per comedian type:**

| Type | Starting point | Journey | Ending point |
|---|---|---|---|
| Dark-confessional | Comfort | Shock → recognition → complicity | "I'm not alone" |
| Observational | Normalcy | "Wait, I do that too" → recognition | Self-awareness |
| Rant | Frustration | Escalation → catharsis → relief | "Someone finally said it" |
| Absurdist | Boredom | Confusion → surrender → delight | "The world is stranger than I thought" |
| One-liner | Attention | Surprise → admiration → greed ("another one") | Addiction to the rhythm |
| Storytelling | Curiosity | Immersion → surprise → warmth | "I know that person" |
| Character | Recognition | Laughter → discomfort → empathy | "That's me in a costume" |
| Meta | Cynicism | Deconstruction → recognition → freedom | "Comedy is a construct and that's okay" |

**The feeling map IS the rasa cycle.** It's not decoration — it's the
structural analysis of why a set WORKS as an emotional experience, not
just a collection of jokes.

---

## STRUCTURE 13: THE PERSONALIZATION ENGINE

**Each comedian gets a graph-driven visual identity that matches their
engine. The identity isn't decoration — it's a data visualization.**

### The personalization layers:

**Layer 1: COLOUR** (from `production/PALETTE.md`)
- Primary colour = engine mood (orange = warm confession, blue = cold stillness)
- The colour tells you what kind of comedy before a word is spoken

**Layer 2: RHYTHM** (from `timing_measured.pause_bins`)
- The episode's editing rhythm MATCHES the comedian's timing signature
- Fast-talkers (Louis 171 WPM): rapid cuts, tight frames
- Slow-deliberate (Norm): long holds, static frames
- Chaotic (Casey): jump cuts, visual noise
- Measured (Burr): medium cuts, steady pulse

**Layer 3: MUSIC** (from `generation.id` + `region`)
- Seventies US: funk/jazz underlays
- Aughts US: indie rock / acoustic
- Nineties UK: Britpop / trip-hop
- Tens: electronic / lo-fi
- Louisiana (Normand): jazz / swamp blues
- NYC: subway ambience / downtown jazz

**Layer 4: TYPOGRAPHY** (from `humor_type.primary`)
- Dark-confessional: serif, intimate, slow reveal
- Rant: bold sans-serif, all-caps moments, fast
- Absurdist: mismatched fonts, rotating text, chaos
- One-liner: monospace, staccato, typewriter
- Storytelling: handwritten, flowing, warm
- Meta: clean, editorial, magazine-style

**Layer 5: FACE TREATMENT** (from `modes.signature`)
- Dark-confessional: close-up, eyes visible, low light
- Rant: medium shot, hands visible, high contrast
- Absurdist: wide shot, full body, motion blur
- One-liner: tight crop, mouth focus
- Storytelling: medium-close, warm light, slight grain
- Meta: clean, studio, editorial lighting

### Example: Mark Normand personalization
```
COLOUR: Green (#1A6B3C dark) + White
RHYTHM: Medium-fast (his delivery is quick but controlled)
MUSIC: Louisiana jazz + NYC downtown (his two homes)
TYPOGRAPHY: Handwritten serif — storytelling with precision
FACE: Medium-close, warm light, slight grain (NYC comedy club)
EMOTIONAL START: Comfort (observational = "wait, I do that too")
EMOTIONAL END: Self-awareness
RASA CYCLE: hasya → hasya (observational doesn't cycle much —
  it's steady-state mirth, which is why it feels like hanging
  out with a funny friend)
OPERATOR EMPHASIS: split_knowledge (observational = recognition)
PAUSE SIGNATURE: Short holds, rapid recovery (NYC timing)
```

### Example: Louis C.K. personalization
```
COLOUR: Orange (#E8740C) + White
RHYTHM: Slow-build with long holds (8.16s confession holds)
MUSIC: Quiet jazz → silence → single piano note after hold
TYPOGRAPHY: Serif, intimate, slow reveal (confessional)
FACE: Close-up, eyes visible, low light (confession booth)
EMOTIONAL START: Curiosity → SHOCK → complicity → "I'm not alone"
EMOTIONAL END: The room agrees with him (the laugh IS the confession)
RASA CYCLE: hasya → karuna → hasya → bhayanaka → shanta
OPERATOR EMPHASIS: split_knowledge + expose_self_blindness
PAUSE SIGNATURE: Long holds at dark turns (the confession mechanism)
```

### The personalization JSON:
```json
{
  "comedian": "louis-ck",
  "colour": {"primary": "#E8740C", "accent": "#FFFFFF"},
  "rhythm": {"wpm": 171, "pause_profile": "long-holds", "cut_style": "slow-build"},
  "music": {"era": "aughts", "genre": "quiet-jazz", "region": "us"},
  "typography": {"style": "serif", "mood": "intimate", "reveal": "slow"},
  "face": {"shot": "close-up", "lighting": "low", "treatment": "confession-booth"},
  "emotion": {"start": "curiosity", "journey": ["shock","complicity","recognition"], "end": "I'm-not-alone"},
  "rasa_cycle": ["hasya","karuna","hasya","bhayanaka","shanta"],
  "operator_emphasis": ["split_knowledge","expose_self_blindness"],
  "pause_signature": {"type": "long-holds", "max_hold": 8.16, "at": "dark-turns"}
}
```

### The personalization JSON for any comedian:
```json
{
  "comedian": "<cid>",
  "colour": "<from PALETTE.md>",
  "rhythm": {"wpm": "<from timing_measured>", "pause_profile": "<from pause_bins>", "cut_style": "<derived>"},
  "music": {"era": "<from generation.id>", "genre": "<derived>", "region": "<from region>"},
  "typography": "<from humor_type.primary>",
  "face": "<from modes.signature>",
  "emotion": "<from STRUCTURE 12 feeling map>",
  "rasa_cycle": "<from STRUCTURE 12 rasa map>",
  "operator_emphasis": "<from operator_priors top 2>",
  "pause_signature": "<from timing_measured>"
}
```

**This JSON IS the production brief.** A motion designer reads it and
knows everything: colour, rhythm, music, typography, face treatment,
emotional arc, rasa cycle, operator emphasis, pause signature. No
meeting needed. No mood board needed. The graph generates it.

---

## STRUCTURE 14: THE BOOKEND (open with the clip, close with the same clip)

**The most powerful structural device in the series. The clip is the
same. The audience is different.**

### How it works

```
COLD OPEN (0:00–0:35):
  Play the transgressive clip RAW. No overlays. No music. No context.
  The audience laughs (or cringes) WITHOUT understanding the mechanism.
  They feel something but they can't name it.

  [TEXT ON SCREEN: "Why is that funny?"]

THE EPISODE (0:35–55:00):
  Deconstruct the machine. Teach the audience every mechanism:
  timing, operators, BV, status, the room's role, the pause.
  By the end, they KNOW the machine.

CLOSE (55:00–60:00):
  Play the SAME CLIP again. Raw. No overlays. No music.
  But now the audience hears it differently. They hear the pauses.
  They feel the violation. They see the benign frame. They
  understand why they laughed.

  [After the clip: 3 seconds of silence]

  [TEXT ON SCREEN: "Now you know why."]
```

### Why this works psychologically

1. **The first viewing is naive.** The audience experiences the joke
   the way a normal audience does — raw, unanalyzed. They laugh at
   the surface (the shock, the absurdity, the delivery).

2. **The episode is the analysis.** Every mechanism is named, every
   pause is timed, every operator is labeled. The audience builds
   a mental model of the machine.

3. **The second viewing is informed.** The SAME clip now sounds
   different. The 8.16s hold is no longer "a pause" — it's the
   confession mechanism. The "bored" line is no longer "funny" —
   it's the deflationary turn. The audience HEARS the machine.

4. **The transformation IS the thesis.** The episode doesn't TELL
   you comedy is a machine — it SHOWS you by changing how you hear
   a clip in 55 minutes. The proof is in your own ears.

### The clip transformation map

| Element | First viewing | Second viewing |
|---|---|---|
| The 8.16s hold | "That's a long pause" | "That's the room metabolizing the confession" |
| "I don't really like doing that" | "That's funny" | "That's the deflationary turn — the boredom is the payload" |
| The laugh after the hold | Relief | Recognition + relief + complicity |
| "Saying something terrible because it makes me laugh" | "That's a meta-joke" | "That's expose_self_blindness — he's naming the engine while it runs" |
| The room's energy | "They're laughing" | "They're confessing back" |

### The exact timing

```
COLD OPEN CLIP:
  Duration: 15–30 seconds (the transgressive moment + the hold)
  Treatment: raw, no overlays, no music, no title
  Selection: the bit with the LONGEST pause (the money moment)

CLOSE CLIP:
  Duration: THE SAME 15–30 seconds (identical)
  Treatment: raw, no overlays, no music, no title
  BUT: the audience has changed. They've heard 55 minutes of analysis.

POST-CLIP:
  3 seconds of silence.
  [TEXT: "Now you know why."]
  [END CARD]
```

### What to put in the middle (the transformation arc)

The episode must teach EXACTLY the mechanisms that the bookend clip
contains. If the clip has:
- A long pause → teach timing (Act 2)
- A violation → teach BV (Act 3)
- A status inversion → teach status dynamics (Act 3)
- A meta-confession → teach expose_self_blindness (Act 2)
- A comparison moment → teach the comparison grid (Act 4)

The clip's CONTENT DETERMINES which structures fire. The bookend
isn't decorative — it's the curriculum.

### Variations

**The Echo (soft bookend):**
- Open with the clip
- Close with a DIFFERENT clip from the same special
- The second clip demonstrates the SAME mechanism
- "The machine works everywhere. Here's another room."

**The Reversal (hard bookend):**
- Open with the clip
- Close with the clip played BACKWARDS (or slowed down)
- The pauses become the punchlines. The machine is audible.
- Only works for timing-focused episodes (Louis, Norm)

**The Comparison Bookend:**
- Open with the clip (Louis)
- Close with a DIFFERENT comedian attempting the same structure
- "Same machine. Different engine. You can hear the difference now."
- Works for cross-cultural episodes (UK vs US)

### The emotional arc of the bookend

```
VIEWING 1 (cold open):
  Emotion: shock / laughter / "what is happening"
  Rasa: hasya (mirth) + bhayanaka (fear)
  Understanding: surface only

VIEWING 2 (close):
  Emotion: recognition / "I hear it now" / mastery
  Rasa: shanta (peace) + hasya (mirth)
  Understanding: full mechanism visible
```

The audience's emotional journey MIRRORS the learning journey:
from confusion to clarity, from surface to depth, from naive to
informed. The clip didn't change. THEY changed. And that's the
thesis of the entire series: comedy is a machine, and once you
see the machine, you can't unsee it.

---

## STRUCTURE 15: THE LENS (cross-domain definition)

> Added 2026-10-18 from FORMULA.md decode. Before analyzing comedy,
> teach the LENS via film, music, or novels. The gold videos spend
> 3–5 minutes here. We were skipping it.

**Why it works:** the viewer learns a PORTABLE FRAME in a domain they
already understand (film plots, musical technique), then applies it to
comedy. The return to comedy feels like discovery, not lecture. This
is also empirically grounded — the DPV framework (LITERATURE.md §2)
shows humor appreciation runs on prediction-error resolution, and
teaching the prediction pattern in a simpler domain first makes the
comedy application land faster.

**Template:**
```
1. Name the device (unreliable narrator / rhythm / trojan horse).
2. Fully retell ONE non-comedy example (2–3 min).
   - Film: Shutter Island, Fight Club, American Psycho
   - Music: Danny Kaye, radio DJ technique, jazz structure
   - Novel: first-person unreliable narrators
3. Extract the PRINCIPLE from that example in plain language.
4. Bridge back: "So how does this work in stand-up?"
5. [Optional] Self-aware channel voice: "Isn't this video about X?!"
```

**Gold examples:**
- Acaster video: Shutter Island fully retold → Venn diagram → "we can apply the same logic"
- Carlin video: Danny Kaye + xylophone + DJ → "that's the Danny K part of my jeans"
- Locke video: McIntyre "follows a great recipe" vs Lock "combining weird flavors"

**Data hooks:** the lens often maps to a single operator or theory.
- Unreliable narrator → split_knowledge + expose_self_blindness + A7 awareness axis
- Rhythm/music → timing doctrine + syllable melody + DPV temporal scaffolding
- Trojan horse → BV simultaneous condition (genre does accessibility, ideas stay strange)

**Duration:** 3–5 min (5–8% of a 60-min episode). Never skip. Never
let it exceed 6 min or the comedy audience drifts.

---

## STRUCTURE 16: THE CHARACTER (persona before the machine)

> Added 2026-10-18 from FORMULA.md decode. We had persona graphs in
> data but no VIDEO ACT for meeting the persona. The gold videos all
> spend 4–8 minutes here before touching any bit analysis.

**Why it works:** the audience needs to know WHO is speaking before
the mechanism analysis makes sense. The persona is the delivery system
for the engine. characters2's VALIDATION.md grounds this empirically
(stage persona ≠ person is the literature-validated center of humor
persona research). The video act makes that gap VISIBLE.

**Template (4 sub-beats):**
```
a. VIDEO-GAME ANALOGY (1–2 min)
   "Think of it like a character creation suite."
   Quick contrasts: Burr heightens anger / Moran puts logic into
   whimsy / Ali Wong adds fury. The viewer learns to READ personas.

b. OWN-WORDS CLIP (1–2 min)
   The subject describes their own persona in an interview.
   Stuart Goldsmith on Acaster. Acaster on himself. Lock on Lock.

c. REAL-PERSON REVEAL (1 min)
   The shock of seeing them WITHOUT the persona.
   "When you see Acaster without the persona it's a bit of a shock."

d. HISTORY (1–2 min)
   How the persona was built. Failed attempts. Years of tinkering.
   Acaster imitating Ross Noble. Lock's Jack D + Mighty Boa blend.
```

**Data hooks:**
- identity.archetype + delivery_archetype
- identity.modulator_range (the oscillation the video describes)
- identity.contradictions (the gap the video makes visible)
- A7 awareness axis (characters2 AXES.md: plays unaware, privately hyper-aware)

**Gold examples:**
- Acaster: "unjustifiably confident idiot" → Screech/Zac Morris analogy → Ross Noble years
- Locke: "Jack D combined with the Mighty Boa" → protected vs unprotected self
- Carlin: hippie tenor → Patrick's advice → vitriolic philosopher

---

## STRUCTURE 17: THE DISCOVERY (accidental genesis)

> Added 2026-10-18 from FORMULA.md decode. The gold videos spend 4–6
> minutes on HOW THE COMEDIAN FOUND THEIR OWN MACHINE. Our chronology
> act was about specials over time; this is about the moment the engine
> was discovered. Different thing.

**Why it works:** the discovery story is the comedian explaining their
own mechanism without knowing they're explaining it. It's Structure 11
(self-analysis) filtered through narrative. It also earns the thesis:
if the comedian discovered it accidentally, the analysis feels like
archaeology, not projection.

**Template:**
```
1. CREATIVE LOW POINT — they hated their old process.
   "The show I'd done before, I'd hated the writing process."
2. STOPPED DOING X — abandoned the craft habit.
   "I wasn't even writing stuff down anymore."
3. ACCIDENTAL DISCOVERY — a dumb choice that turned out to be the engine.
   "I'm gonna tell them I'm an undercover cop. It was literally that!"
4. BLEED-THROUGH — real life started leaking into the fake premise.
   "My girlfriend had genuinely broke up with me… I could do it
    through that and just say it's my wife leaving me."
5. FRIEND'S DIAGNOSIS — someone names it for them.
   Nish Kumar: "you kind of owe it to the audience to tell them."
6. META-REVEAL — the joke IS the thesis.
   "I'm an undercover cop pretending to be a stand-up comedian.
    The only thing lamer than that would be a stand-up comedian
    pretending to be an undercover cop."
```

**Data hooks:**
- provenance.persona + provenance.next (how the graph was authored mirrors how the persona was authored)
- generation.breakthrough (the era when the engine clicked)
- essay_seeds with "accidental" framing

**Gold examples:**
- Acaster: full 5-beat discovery (above)
- Locke: "it was an accident… I was going through all this stuff of not knowing who I was"
- Carlin: "one night by accident it will happen the correct way and then you save it" (tape every show)

---

## STRUCTURE 18: THE FAIRNESS (critique bracket)

> Added 2026-10-18 from FORMULA.md decode. All four gold videos include
> a section that criticizes or contextualizes the subject BEFORE the
> legacy close. We had no dedicated fairness beat. This buys trust.

**Why it works:** honest critique makes the praise credible. The gold
videos don't just admire — they note where it fails, where it's dated,
where imitation is dangerous. This is Structure 12 (feeling map) with
teeth: the narrator's own honest reaction, not just the audience's.

**Template (pick 2–3):**
```
- WHERE IT FAILS: "others like the hair poem feel dated and
  desperate to impress"
- STYLE AGEING: "standup has outgrown this style of delivery.
  Comedy has become conversation"
- SELF-INDULGENCE: "there is also by his own admission Indulgence"
- IMITATION RISK: "the biggest risk is new Comics will try to
  imitate his delivery without the perspective to back it up"
- HONEST UNCERTAINTY: "I've struggled with this as a research
  assignment… Sean is so hard to make sense of"
- FORMAT CONSTRAINT: "I feel like the show restricts him a bit
  too much"
- COMMERCIAL DILUTION: "more and more popular he got the less and
  less of his people he was getting at his shows"
```

**Placement:** after the case study / second specimen, before the
human universal + close. The audience has seen the machine work; now
they see its limits. Then the universal pivot lands harder because
it survived the critique.

**Gold examples:**
- Carlin: 80s indulgence + "he wasn't always the funniest" + danger of imitation
- Locke: "I prefer sha lock on panel shows as opposed to his standup" + the disappointing looped tour show
- Acaster: "other specials that are obviously about something… come off a little forced"
- (Nerdwriter Louis: lighter — "in my opinion" appears once, committing rather than hedging)

---

## STRUCTURE 8 ADDENDUM: THE MUSIC OVERLAY

> Added 2026-10-18. The Carlin gold essay runs entirely on RHYTHM
> analysis: syllable counts, speed, pitch, word-count subversion.
> Our overlay grammar (original Structure 8) was semantic operators
> only. This addendum adds the temporal/music layer.

**New overlay components (fire alongside existing operator labels):**

| Overlay | Trigger | Source data |
|---|---|---|
| **[SYLLABLES: N]** | Line complete | word-timed transcript, syllable count |
| **[MELODY: AAB]** | 3-line pattern detected | syllable-count rhythm |
| **[SUBVERT: N→M]** | Melody broken (count changes) | syllable delta |
| **[SPEED: X.X syl/s]** | Speech-rate shift > 20% from baseline | word timestamps |
| **[PAUSE: N.NNs]** | Silence > 0.6s (existing, enhanced) | timing_measured |
| **[PITCH: high→low]** | Register shift at punchline | prosody (when available) |
| **[WORDCOUNT: N in Ns]** | Dense passage | count + duration |
| **[RHYTHM: steady/loose]** | Inter-onset consistency | TAMS-style measure |
| **[STAY IN BIT]** | Energy maintained through applause | modulator persistence |

**The Carlin-style analysis pattern (for rhythm-focused episodes):**
```
BEAT: "filthy foul vile vulgar coarse unseemly improper"
  → [SYLLABLES: 2-2-1-1-2-2-2] [MELODY: pairs]
  → 1977 version: same-length pause between each → predictable
  → 1978 version: chopped pace, L-sound launch → flow
  → [SUBVERT: uniform→varied] [SPEED: 3.8→4.6 syl/s]
  INTERLUDE: "The 1978 version is nearly a second faster.
   He bounces from the consonant T's of Street Talk into the
   rounded ooh of locker room language. The rhythm IS the joke."
```

**Literature backing (LITERATURE.md):**
- Attardo & Pickering 2011: timing = pause distribution + speech rate
- TAMS (PNAS 2026): "imaginary metronome" — steady inter-onset intervals
- DPV (arxiv 2026): strategic temporal-semantic coupling distinguishes expertise
- Seinfeld (via characters2): "you count syllables… it's more like songwriting"

**When to fire THE MUSIC vs semantic overlays:**
- Rhythm-focused episode (Carlin, Norm's never-stop): MUSIC overlays dominant
- Confession-focused episode (Louis): PAUSE + BV overlays dominant
- Persona-focused episode (Locke, Acaster): STATUS + CHARACTER overlays dominant
- Default: both layers, MUSIC quieter in the mix

