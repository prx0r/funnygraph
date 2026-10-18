# BEAT MAP — 60-minute episode timing formula

> The exact second-by-second structure. A video editor can follow this
> without a meeting. The comedian's graph fills the content; this file
> defines the rhythm, clip placement, and interlude cadence.
>
> Target: 60 minutes. Format: long-form YouTube documentary.
> Companion to STRUCTURES.md (frameworks) + PALETTE.md (visual identity).

---

## THE 60-MINUTE ARC

```
ACT 0 — COLD OPEN           0:00 – 3:00    (3 min)
ACT 1 — THE QUESTION        3:00 – 8:00    (5 min)
ACT 2 — THE MACHINE         8:00 – 28:00   (20 min)  ← the core
ACT 3 — THE PHILOSOPHY      28:00 – 40:00  (12 min)
ACT 4 — THE COMPARISON      40:00 – 48:00  (8 min)
ACT 5 — THE CHRONOLOGY      48:00 – 55:00  (7 min)
ACT 6 — THE CLOSE           55:00 – 60:00  (5 min)
```

**Why these proportions:** Act 2 (the machine) is 33% of the runtime
because the clip-with-annotations IS the product. Acts 3–5 (philosophy,
comparison, chronology) total 43% — enough to deliver theory without
losing the audience. The close is 8% — short enough to land, long enough
to breathe.

---

## ACT 0: COLD OPEN (0:00–3:00)

```
0:00:00 – 0:00:05   BLACK SCREEN. One line of text:
                     "Why is that funny?"
                     No music. No sound. Let the question hang.

0:00:05 – 0:00:35   CLIP: The most transgressive bit. Raw. No overlays.
                     Selection: longest known_bit pause OR darkest theme.
                     Duration: 15–30 seconds. Let it play uninterrupted.
                     THIS IS THE BOOKEND CLIP (Structure 14). The same
                     clip plays again at 55:00 — but the audience has
                     changed. Save it. Don't re-edit it. Identical.

0:00:35 – 0:00:37   SILENCE. 2 seconds. Black screen.

0:00:37 – 0:00:50   JAZZ KICKS IN. Narrator voice enters.
                     "You just heard [specific description].
                      And [something happened] that isn't supposed
                      to happen. And the thing is — that's not even
                      their best bit."

0:00:50 – 0:01:30   TITLE SEQUENCE (if series has one) or DIRECT
                     into Act 1. The question from 0:00:00 echoes.

0:01:30 – 0:03:00   [OPTIONAL: second clip — the polar opposite bit.
                     Shows range. 15 seconds. Then:]
                     "That's the same person. Same machine.
                      Different gear. This video is about the machine."
```

**Clip insertion rule (cold open):**
| What to pick | Data source | Duration |
|---|---|---|
| Primary: longest-pause bit | `known_bits` with max `timing_measured` | 15–30s |
| Optional: polar-opposite bit | Same comic, different `modes.repertoire` | 15s |

**Music:** silence → jazz at 0:00:37. The silence IS the hook.

---

## ACT 1: THE QUESTION (3:00–8:00)

```
3:00 – 4:30   "When you think of [comedian], you might think of bits
               like this..."
               [CLIP MONTAGE: 3 signature bits, 15s each, NO commentary]
               Bit selection: variety of theme + mode.
               Bit 1: their most famous bit (recognition)
               Bit 2: their darkest bit (violation)
               Bit 3: their most technically impressive bit (craft)

4:30 – 5:30   "There's a catalogue of [comedian] bits that exist in a
               very specific zone: [zone description]."
               [GRAPHIC: humor_type.primary + modes.repertoire bar]

5:30 – 6:30   "But here's what's interesting. None of those bits are
               actually about the thing they're about. [Bit 1] isn't
               about [surface]. [Bit 2] isn't about [surface].
               They're about something else entirely."

6:30 – 7:00   [BEAT — 3 seconds of silence. Let the question land.]

7:00 – 8:00   "If you can find the thing they're all about — you'll
               find the thing that makes [comedian] the comedian they
               are. And it's not what you think."
               [GRAPHIC: identity.deal one-liner]
               "This is a video about the machine that runs underneath
               [comedian] — and why it works. And along the way, it's
               going to turn out to be a video about why comedy works."
```

**Montage clip rules:**
| Slot | Selection rule | Duration | Music |
|---|---|---|---|
| Bit 1 (famous) | Highest `specials_rated` rating's most-cited bit | 15s | None |
| Bit 2 (darkest) | `specials_dark` + highest `benign_violation` | 15s | None |
| Bit 3 (craft) | Longest measured `pause_count` set | 15s | None |

**Music:** quiet jazz under narration. Silence under clips. The clips
are the evidence; don't talk over evidence.

---

## ACT 2: THE MACHINE (8:00–28:00) — THE CORE

**This is 20 minutes of beat-by-beat deconstruction. The structure:**

```
8:00 – 8:30    "Let's start with [the best set]."
               [GRAPHIC: set title + timing stats]
               "337 words. 57 pauses. One 8.16-second silence.
                This is the timing map of a 2-minute comedy window."
               [GRAPHIC: pause bins as histogram]

8:30 – 28:00   [FULL SET PLAY, WITH OVERLAYS]
               The clip plays. Overlays fire in real time.
               The narrator pauses the clip at key moments for interludes.
```

### THE BEAT-BY-BEAT TIMING FORMULA

The clip plays continuously. Overlays annotate. The narrator INTERJECTS
at specific beats. Here's the cadence:

```
FOR EACH BEAT in the set:
  1. Clip plays (2–10 seconds of raw material)
  2. Overlay fires: [BEAT N] + [LABEL] + [OPERATOR] (if applicable)
  3. If pause > 0.8s: ⏸ PAUSE [N]s overlay appears
  4. If pause > 2.0s: NARRATOR interjects (interlude)
  5. Clip resumes

INTERLUDE CADENCE:
  - Every 4–6 beats, the narrator takes a breath (no interlude)
  - Interludes are RAREST at the start (let the set breathe)
  - Interludes are MOST FREQUENT at the darkest turns (the room
    needs guidance when the content is hardest)
  - After the longest pause: FULL BOX interlude (the money moment)

TARGET INTERLUDE FREQUENCY:
  20-minute Act 2 → ~25 interludes total
  Average: 1 interlude per 48 seconds of clip
  Peak density: 1 interlude per 15 seconds (at the darkest turn)
  Trough density: 1 interlude per 90 seconds (at the resets)
```

### THE INTERLUDE TYPE DISTRIBUTION

```
For a 20-minute Act 2 with ~25 interludes:

  ONE-LINE (micro-pause, 0.6–1.0s):     ~5 interludes  (20%)
    "Just long enough for the implication to land."

  TWO-SENTENCE (standard, 1.0–2.0s):    ~7 interludes  (28%)
    What happened + what it does.

  THREE-SENTENCE (topic-pause, 2.0–4.0s): ~6 interludes (24%)
    What happened + mechanism + why this length.

  FULL BOX (confession-hold, 4.0s+):     ~3 interludes  (12%)
    The room's decision process. The money moments.

  OPERATOR (operator fires):              ~3 interludes  (12%)
    Name it, explain it, cite it.

  COMPARISON (another comedian appears):  ~1 interlude   (4%)
    What they're doing differently.
```

### THE PAUSE INTERLUDE TEMPLATE (exact wording)

**ONE-LINE (0.6–1.0s pause):**
```
"⏸ [N] seconds. Just long enough for the implication to land."
```

**TWO-SENTENCE (1.0–2.0s pause):**
```
"⏸ [N] seconds. [What the room just heard]. The pause lets
the implication settle before he escalates past it."
```

**THREE-SENTENCE (2.0–4.0s pause):**
```
"⏸ [N] seconds. [What the room just heard]. This is [mechanism
name]: [what the silence does]. [Why this specific length matters]."
```

**FULL BOX (4.0s+ pause):**
```
╔═══════════════════════════════════════════════════════╗
║ [THEME NAME]: [what this silence proves]              ║
║                                                        ║
║ [What the room just heard — one sentence].             ║
║ [What the silence is doing — one sentence].            ║
║ [What the room decides in the silence — one sentence]. ║
║ [Why the laugh that follows is about X, not Y].        ║
╚═══════════════════════════════════════════════════════╝
```

**OPERATOR interlude:**
```
"[OPERATOR: <name>] fires here. [What the operator is — one sentence].
 [How it applies to this specific moment — one sentence].
 [The data: <operator> fires in N% of measured bits, lift +X]."
```

### THE ACT 2 CLOSING BEAT

```
27:00 – 28:00   After the longest pause and its FULL BOX interlude,
                the clip plays to its natural end.
                Then:

                "That's [bit name]. [Duration]. [N] punch pauses.
                 One [N]-second silence. And a machine that runs on
                 [mechanism].

                 But this bit isn't special. It's the same machine
                 that runs every [comedian] set. The machine has a
                 name. And if you can see the machine, you'll see
                 it everywhere.

                 The machine is called [THESIS MECHANISM]."
```

---

## ACT 3: THE PHILOSOPHY (28:00–40:00)

```
28:00 – 30:00   "Every comedian who [does the thing] is doing one of
                 three things. [Comparison type A]. Or [type B].
                 Or a third thing, which doesn't have a good name yet.

                 [Comedian] is doing the third thing."

30:00 – 33:00   [ANIMATED TRIANGLE: Benign Violation]
                 Condition 1: Violation (top) — what's unsayable
                 Condition 2: Benign (bottom-left) — how room stays safe
                 Condition 3: Simultaneous (bottom-right) — the timing

                 For each condition: 1 minute.
                 Violation: show the darkest clip fragment (5s)
                 Benign: show the warmest delivery fragment (5s)
                 Simultaneous: show the longest pause (raw, no music)

33:00 – 36:00   "And here's the thing nobody talks about: the room
                 is not passive. The audience is the fourth condition."

                 [GRAPHIC: the alliance loop]
                 Comedian says thing → Room flinches → Comedian names
                 the flinch → Room laughs → Comedian escalates → Repeat

                 "The laugh is not [approval/shock]. The laugh is
                 [recognition/relief]. The laugh is the audience
                 [confessing back]."

36:00 – 39:00   [EMOTIONAL JOURNEY MAP — from STRUCTURE 12]
                 Line chart of audience emotional state over the set.
                 Rasa cycle overlaid: hasya → karuna → hasya → ...

                 "Let's map the feeling. Not the jokes — the emotional
                  geography. Where does [comedian] take you? And where
                  do you end up?"

39:00 – 40:00   "This is what makes [comedian] different from
                 [comparison type]. [Comparison type] [lowers someone
                 else]. [Comedian] [lowers themselves]. And the room
                 trusts them because [reason]. And once the room trusts
                 them, they can say anything."
```

**Philosophy act rhythm:**
| Section | Duration | Visual | Music |
|---|---|---|---|
| Three things | 2 min | Talking head | Quiet jazz |
| BV triangle | 3 min | Animated triangle + clips | None under clips |
| Alliance loop | 3 min | Animated diagram | Quiet jazz |
| Emotional map | 3 min | Line chart + rasa wheel | Quiet jazz |
| Trust machine | 1 min | Comparison grid | Quiet jazz → transition |

---

## ACT 4: THE COMPARISON (40:00–48:00)

```
40:00 – 42:00   "So why doesn't everyone do this? Because the [N]
                 conditions are nearly impossible to hold simultaneously."

42:00 – 46:00   [COMPARISON GRID — 4 rows, 1 minute each]

                 Row 1: [Comedian] — works. Show 15s clip.
                 Row 2: [Comparison A] — fails differently. Show 15s.
                 Row 3: [Comparison B] — fails differently. Show 15s.
                 Row 4: [Comparison C] — fails differently. Show 15s.

                 For each: "Take any one condition away and the
                 machine breaks. [Specific condition missing].
                 The result is [specific failure mode]."

46:00 – 48:00   "Take any one away and the machine breaks. That's why
                 it's hard to copy. And that's why the next time you
                 hear a comedian say [the thing] and the room
                 [laughs instead of gasping] — you'll know exactly
                 what's happening. The machine is running.

                 But machines evolve. Let's watch this one evolve."
```

**Comparison grid data mapping:**
| Row | Selection | Data source | Clip duration |
|---|---|---|---|
| Subject | The comedian being analyzed | Full graph | 15s (best bit) |
| Comparison A | Nearest neighbor, different engine | `neighbors.json[0]` | 15s (their best bit) |
| Comparison B | Famous comedian, fails at this zone | `by_type` board, lower craft | 15s (their attempt) |
| Comparison C | Historical precursor | influence graph / generation | 15s (archival) |

---

## ACT 5: THE CHRONOLOGY (48:00–55:00)

```
48:00 – 50:00   [TIMELINE GRAPHIC — full career]
                 Each special: year, title, rating, what changed.
                 Clips: 5s per special (the signature moment).

50:00 – 53:00   NARRATOR walks the arc:
                 "In [year], [comedian] was [state]. By [year],
                  the machine had [evolved/rebuilt/deconstructed].
                  The key shift was [what changed]."

53:00 – 54:00   [GRAPHIC: pause-length-over-time (if measured)]
                 "Did the pauses get longer as they got more confident?
                  Did the violations get darker? The data says [answer].
                  [If not measured:] We haven't measured all the timing
                  yet — but the roadmap is to find out."

54:00 – 55:00   "The machine [is still running / was rebuilt / was
                  deconstructed]. And the room [still trusts them /
                  is learning to trust them again / trusted them
                  differently]."
```

**Chronology data mapping:**
| Element | Source | Duration per item |
|---|---|---|
| Timeline bars | `specials_rated[]` (year + rating) | Continuous |
| Signature clips | Best bit per special | 5s each |
| Pause data | `sets[].timing_measured` | Graphic only |
| Recognition | `recognition{cc2004,rs2017,paste_2017,c4_2007}` | Text card |

---

## ACT 6: THE CLOSE (55:00–60:00)

```
55:00 – 56:30   "[Comedian] is not a [surface description].
                 They're a [deeper description] — and then they
                 [what they do with it]."

56:30 – 57:30   "The [longest pause description] isn't a [surface].
                 It's [what it actually is]. And [what it actually
                 is] is the [thing]. And [the thing] is the only
                 place where you can [what comedy does]."

57:30 – 58:30   "[Comedian] doesn't get away with it because they're
                 [obvious reason]. They get away with it because they
                 built a machine that [what the machine does]. And the
                 machine runs on [mechanism]."

58:30 – 59:00   [GRAPHIC: the pause bars — the two longest silences
                 drawn as giant vertical lines through the transcript.
                 The text flows around them like water around stones.]

                 "If you want to see the machine running in a different
                  comedian — one who [does the same thing differently] —
                  the next episode is about [next comedian]. And the
                  machine there is [different mechanism]."

59:00 – 59:30   [GRAPHIC: house board position — #N, sweep [lo,hi]]

59:30 – 59:50   THE BOOKEND: Play the SAME clip from 0:00:05.
                 Raw. No overlays. No music. Identical.
                 The audience hears it differently now. They hear
                 the pauses. They feel the violation. They see the
                 benign frame. They understand why they laughed.

59:50 – 59:53   [3 SECONDS OF SILENCE]

59:53 – 59:55   [TEXT ON SCREEN: "Now you know why."]

59:55 – 60:00   [END CARD: Subscribe. Next: Why is [next] Funny?]
```

---

## MASTER RHYTHM TABLE

| Act | Duration | Clips | Interludes | Graphics | Music |
|---|---|---|---|---|---|
| 0: Cold open | 3 min | 2 (15–30s) | 0 | 1 (title) | Silence → jazz |
| 1: Question | 5 min | 3 (15s) | 0 | 2 (type + deal) | Quiet jazz |
| 2: Machine | 20 min | 1 (full set) | ~25 | ~30 overlays | Silence under clip |
| 3: Philosophy | 12 min | 3 (5s) | 3 | 4 (triangle, loop, map, grid) | Quiet jazz |
| 4: Comparison | 8 min | 4 (15s) | 0 | 1 (grid) | Quiet jazz |
| 5: Chronology | 7 min | ~7 (5s) | 0 | 2 (timeline, pause chart) | Quiet jazz |
| 6: Close | 5 min | 1 (bookend) | 0 | 3 (pause bars, board, text) | Jazz → silence |
| **TOTAL** | **60 min** | **~19 clips** | **~28** | **~40** | — |

**THE BOOKEND RULE:** The cold open clip (0:00:05) and the close clip
(59:30) are IDENTICAL — same edit, same duration, same raw treatment.
The only thing that changed is the audience. They watched 55 minutes
of analysis. Now they hear the machine. This is the proof that the
episode worked.

---

## CLIP SELECTION CHEAT SHEET

| Need | Pick from | Duration | Rule |
|---|---|---|---|
| Cold open hook | `known_bits` longest pause | 15–30s | Raw, no overlay, no music |
| Montage bit (famous) | `specials_rated` top bit | 15s | Recognition |
| Montage bit (dark) | `specials_dark` + BV | 15s | Violation |
| Montage bit (craft) | Measured set, longest pauses | 15s | Technique |
| Machine core | Best measured set window | Full window | With overlays |
| Philosophy evidence | Specific beat from the set | 5s | Isolated moment |
| Comparison subject | Same set, different beat | 15s | The engine at work |
| Comparison A | Neighbor's best bit | 15s | Different engine |
| Comparison B | Famous failure | 15s | Missing condition |
| Comparison C | Archival precursor | 15s | Historical |
| Chronology clips | Best bit per special | 5s each | Evolution |
| Close echo | The longest pause moment | 5s | Callback to cold open |

---

## MUSIC CUE SHEET

| Timestamp | Music | Duration | Purpose |
|---|---|---|---|
| 0:00:00–0:00:37 | Silence | 37s | The question hangs |
| 0:00:37–0:08:00 | Upbeat jazz | 7m23s | Hook + question |
| 0:08:00–28:00 | None (under clip) | 20m | The clip is the evidence |
| 28:00–40:00 | Quiet jazz | 12m | Philosophy |
| 40:00–48:00 | Quiet jazz | 8m | Comparison |
| 48:00–55:00 | Quiet jazz → building | 7m | Chronology |
| 55:00–59:30 | Quiet jazz → single piano | 4.5m | Close |
| 59:30–59:50 | None (raw clip) | 20s | The bookend — identical to cold open |
| 59:50–60:00 | Silence | 10s | Now you know why |

**Rules:**
- NO music under any measured pause > 2.0s (full stop)
- Single piano note after the longest hold (the room exhaling)
- Jazz mirrors the comedian's delivery archetype (warm for confession,
  cold for deadpan, chaotic for absurdist)
- Transition from Act 2 to 3: 3 seconds of silence before the
  philosophy begins — the room resets

---

## THE FORMULA (summary)

```
60 MINUTES = 
  3 min  cold open (the transgressive clip + the question)
+ 5 min  montage (3 signature bits + the pivot)
+ 20 min machine (full set + ~28 interludes + overlays)
+ 12 min philosophy (BV triangle + alliance loop + emotional map)
+ 8 min  comparison (4 comedians, 15s each)
+ 7 min  chronology (timeline + evolution)
+ 5 min  close (thesis + next episode)

CLIPS: ~18 total (1 full set + 17 fragments)
INTERLUDES: ~28 (weighted toward the darkest moments)
GRAPHICS: ~40 (overlays, diagrams, charts, cards)
MUSIC: jazz (quiet) + silence (sacred) + piano (one note)
```

The comedian's graph fills the content. This file defines the rhythm.
Swap the comedian, the rhythm holds, the content changes.

---

# BEAT MAP v2 — gold-formula revision (2026-10-18)

> The original 60-min arc (above) is preserved. This section overlays
> the decoded 11-beat gold formula from FORMULA.md, inserting four new
> acts and adding THE MUSIC overlay to the grammar. Use this for the
> Louis spec v3 and all future episodes that want to FEEL like the gold
> transcripts (Carlin / Acaster / Locke).

## THE REVISED ARC

```
ACT 0    ENGINE NAMED + POETIC INTRO    0:00  – 1:30   (1.5 min)
ACT 1    SPECIFIC THESIS                1:30  – 3:00   (1.5 min)
ACT 1.5  THE LENS (cross-domain)        3:00  – 7:30   (4.5 min)  ← NEW
ACT 1.75 THE CHARACTER (persona)        7:30  – 12:00  (4.5 min)  ← NEW
ACT 2    THE MACHINE (case study)       12:00 – 28:00  (16 min)
ACT 2.5  SECOND SPECIMEN                28:00 – 33:00  (5 min)    ← enhanced
ACT 3    THE PHILOSOPHY (universal)     33:00 – 40:00  (7 min)
ACT 3.5  THE DISCOVERY (genesis)        40:00 – 45:00  (5 min)    ← NEW
ACT 4    THE FAIRNESS (critique)        45:00 – 49:00  (4 min)    ← NEW
ACT 5    THE CHRONOLOGY                 49:00 – 54:00  (5 min)
ACT 6    SUBJECT NAMES ENGINE + CLOSE   54:00 – 60:00  (6 min)
```

**What changed vs v1:**
- Cold open compressed (3 min → 1.5 min): engine + poem + thesis in one breath
- LENS inserted (4.5 min): teach the device via film/music before comedy
- CHARACTER inserted (4.5 min): meet the persona before the machine
- Machine shortened (20 → 16 min): the persona act does setup work the machine was doing
- DISCOVERY inserted (5 min): accidental genesis before fairness
- FAIRNESS inserted (4 min): critique bracket before chronology
- CLOSE enhanced: subject-names-engine beat before the bookend

## THE MUSIC OVERLAY (new grammar layer)

Fires alongside existing operator labels. Primary source: word-timed
transcripts + timing_measured. See STRUCTURES.md Structure 8 addendum.

```
┌─────────────────────────────────────────────────────────┐
│  ON SCREEN (during machine act):                        │
│                                                         │
│  "filthy foul vile vulgar coarse unseemly improper"     │
│  [SYLLABLES: 2-2-1-1-2-2-2] [MELODY: pairs]            │
│  [SPEED: 4.6 syl/s]  [PAUSE: 0.7s]                      │
│  [OPERATOR: rigidify]  [BV: v=0.6 b=0.7]                │
│                                                         │
│  INTERLUDE after subversion:                            │
│  "1978 is nearly a second faster. He bounces from       │
│   the consonant T's into the rounded ooh. The rhythm    │
│   IS the joke."                                         │
└─────────────────────────────────────────────────────────┘
```

| Overlay | Trigger | Fires in |
|---|---|---|
| [SYLLABLES: N-N-N] | line complete | machine, specimen |
| [MELODY: pattern] | 3+ line rhythm | machine |
| [SUBVERT: N→M] | melody broken | machine |
| [SPEED: X.X syl/s] | rate shift > 20% | machine, specimen |
| [WORDCOUNT: N in Ns] | dense passage | machine |
| [STAY IN BIT] | applause, no break | machine |
| [PITCH: high→low] | register shift | machine (when prosody available) |

**Overlay priority by episode type:**
- Rhythm episode (Carlin, Norm): MUSIC dominant, semantic quieter
- Confession episode (Louis): PAUSE + BV dominant, MUSIC quieter
- Persona episode (Locke, Acaster): STATUS + CHARACTER dominant

## ACT 1.5: THE LENS (3:00–7:30)

```
3:00 – 3:15   "The device has a name. Before we get to comedy,
               let me show you where else it lives."
3:15 – 5:30   NON-COMEDY EXAMPLE, fully retold.
               Film: Shutter Island (Acaster video)
               Music: Danny Kaye / radio DJ (Carlin video)
               Analogy: recipe vs weird flavors (Locke video)
5:30 – 6:15   PRINCIPLE extracted in plain language.
               "The narrator's version of events is wrong. We
                spend the whole film in their wrong version."
6:15 – 7:00   BRIDGE BACK.
               "So how does this work in stand-up?"
               [Optional self-aware voice: "Isn't this video
                about James Acaster you giant plum?!"]
7:00 – 7:30   THESIS RE-ANCHORED to the comedian.
               "James Acaster does this. Here's how."
```

**Music:** quiet jazz under lens, silence under any embedded clip.

## ACT 1.75: THE CHARACTER (7:30–12:00)

```
7:30 – 9:00   VIDEO-GAME ANALOGY.
               "Think of it like a character creation suite."
               Quick contrasts: Burr / Moran / Wong (10s each).
9:00 – 10:30  OWN-WORDS CLIP.
               Subject describes their persona. Stuart Goldsmith
               on Acaster. Acaster on Acaster.
10:30 – 11:00 REAL-PERSON REVEAL.
               "When you see them without the persona it's a
                bit of a shock."
11:00 – 12:00 PERSONA HISTORY.
               Failed attempts. Years of tinkering.
               "I thought I was a great fun cool lad… they
                could tell it wasn't real."
```

**Overlays:** [ARCHETYPE: x] [MODULATORS: list] [AWARENESS: aware/semi/constructed]
**Music:** quiet jazz, no silence needed (no punchlines here).

## ACT 2.5: SECOND SPECIMEN (28:00–33:00)

Enhanced from v1 comparison. Rule: same device, DIFFERENT comedian,
done DIFFERENTLY.

```
28:00 – 28:30  "The device isn't unique to [subject]. Another
                comedian uses the same mechanism — but
                differently."
28:30 – 31:00  CASE STUDY of the second comedian.
                Lee's failed callback → 20 min of revelation.
                Same unreliable narrator, different delivery.
31:00 – 32:00  VENN DIAGRAM: overlap + difference.
                "Acaster's story falls apart to reveal himself.
                 Lee's joke falls apart to reveal himself.
                 Same device. Different failure mode."
32:00 – 33:00  "Now you can hear the device everywhere."
```

## ACT 3.5: THE DISCOVERY (40:00–45:00)

```
40:00 – 41:00  CREATIVE LOW POINT.
                "The show I'd done before, I'd hated the process."
41:00 – 41:45  STOPPED DOING X.
                "I wasn't even writing stuff down anymore."
41:45 – 42:45  ACCIDENTAL DISCOVERY.
                "I'm gonna tell them I'm an undercover cop."
42:45 – 43:45  BLEED-THROUGH.
                "My girlfriend had genuinely broke up with me."
43:45 – 44:30  FRIEND'S DIAGNOSIS.
                Nish Kumar: "you owe it to the audience."
44:30 – 45:00  META-REVEAL.
                "I'm an undercover cop pretending to be a
                 stand-up comedian."
```

**Music:** quiet jazz. This is narrative, not analysis.

## ACT 4: THE FAIRNESS (45:00–49:00)

```
45:00 – 46:30  WHERE IT FAILS.
                "Others feel dated." "Standup has outgrown this."
                "By his own admission, Indulgence."
46:30 – 47:30  IMITATION RISK.
                "The biggest risk is new Comics will try to
                 imitate this without the perspective."
47:30 – 48:30  HONEST UNCERTAINTY.
                "I've struggled with this as a research
                 assignment… they're so hard to make sense of."
48:30 – 49:00  SURVIVES THE CRITIQUE.
                "And yet. The machine still works."
```

**Music:** dry. Almost no jazz. The critique should feel unvarnished.

## ACT 6: SUBJECT NAMES ENGINE + CLOSE (54:00–60:00)

```
54:00 – 56:00  SUBJECT'S OWN THEORY.
                Carlin: jester → philosopher → poet triptych.
                Acaster: "I can do that forever."
                Locke: Robin Williams spark-of-madness quote.
                Play their own words explaining their engine.
56:00 – 57:30  HUMAN UNIVERSAL (if not fully landed in Act 3).
                "We are all unreliable narrators."
57:30 – 59:30  BOOKEND CLIP (identical to cold open, raw).
59:30 – 59:50  SILENCE. [TEXT: "Now you know why."]
59:50 – 60:00  END CARD. Next episode hook.
```

## REVISED MASTER TABLE

| Act | Duration | Clips | Interludes | Music |
|---|---|---|---|---|
| 0: Engine+Intro | 1.5 min | 0–1 | 0 | Silence → jazz |
| 1: Thesis | 1.5 min | 3 (10s) | 0 | Quiet jazz |
| 1.5: Lens | 4.5 min | 1–2 (non-comedy) | 0 | Quiet jazz + clip |
| 1.75: Character | 4.5 min | 3–4 (interview) | 0 | Quiet jazz |
| 2: Machine | 16 min | 1 full set | ~20 | Silence under clip |
| 2.5: Specimen | 5 min | 2–3 (15s) | ~3 | Quiet jazz |
| 3: Philosophy | 7 min | 1–2 (5s) | 2 | Quiet jazz |
| 3.5: Discovery | 5 min | 3–4 (interview) | 0 | Quiet jazz |
| 4: Fairness | 4 min | 1–2 (5s) | 0 | Dry / none |
| 5: Chronology | 5 min | ~5 (5s) | 0 | Quiet jazz |
| 6: Close | 6 min | 1 (bookend) + 1–2 (subject) | 0 | Jazz → piano → silence |
| **TOTAL** | **60 min** | **~25 clips** | **~25** | — |

THE BOOKEND RULE STILL HOLDS: cold open clip and close clip identical.

