# SERIES — YouTube video series bible (funnygraph-powered)

> Every episode is built from comedian graphs + theory data. The graph IS
> the episode spine: thesis, mechanism, evidence, numbers, comparisons.
> Clips are embedded from YouTube (fair-use commentary/criticism).
> Docstring: this file is the master spec — producers read it first.

## Series 1: WHY IS X FUNNY? (the flagship)

**Format:** 8–12 min per episode. One comedian. Theory-first, numbers-backed.
**Template:** `episodes/why-shane-gillis-funny.md` (proven).
**Data source:** `comedians/<id>/comedian-graph.json` + `rankings/` + `theory_content.json`.

### Episode structure (Gillis template, refined for each comic)
```
COLD OPEN (0:00–0:45)
  Hook: the most surprising fact from the data. 26.5M Netflix hours.
  Frame: "shouldn't work — why does he?"

ACT 1: THE ENGINE (0:45–3:00)
  Thesis = identity.misinterpretation_rule (THE lens)
  Mechanism, beat by beat (3–4 steps):
    1. The setup (delivery_style)
    2. The gap (where the joke lives — misinterpretation)
    3. The landing (timing_profile.doctrine)
  Theory links = operator_priors + preferred_theories
  [GRAPHIC: engine diagram]

ACT 2: THE NUMBERS (3:00–5:00)
  House rank + sweep interval (proprietary, honest)
  Popularity vs quality gap (metrics.gap_value)
  Nearest neighbors (latent space — "the machine found his scene")
  [GRAPHIC: radar chart of 5 lenses]

ACT 3: THE BITS (5:00–8:00)
  2–3 known_bits with why_it_works
  Each bit: theory_links explained → live clip embed
  [CLIP: the bit plays, voice-over explains mechanism]

CLOSER (8:00–9:00)
  Verdict: where he sits on the boards, what the future holds
  The thesis restated in one sentence
```

### Episode priority (deepest data first)
| # | Comic | Why first | Data depth |
|---|---|---|---|
| 1 | Gillis | proven template | FULL |
| 2 | Theo Von | house #5, biggest establishment gap (consensus #201) | FULL |
| 3 | Carlin | control group — every board agrees | FULL |
| 4 | Norm | house #5, measured timing, moth joke | FULL |
| 5 | Louis | house #2, measured timing, confession booth | FULL |
| 6 | Stewart Lee | meta-architect, house #6 | FULL |
| 7 | Hicks | most underrated (−0.70) | FULL |
| 8 | Chappelle | story god, era #1 | FULL |
| 9 | Rock | observational king, 3233 bits | FULL |
| 10 | Burr | rage auditor, aughts king | FULL |
| 11 | Seinfeld | observational origin, house #11 | FULL |
| 12 | Casey Rocket | absurdist-firecracker, KT data | PARTIAL |
| 13 | Kam Patterson | measured KT priors, rising | PARTIAL |
| 14 | Hedberg | one-liner physics, 202 bits | FULL |
| 15 | Stewart Lee | meta-comedy deep-dive | FULL |

### Data mapping per episode field
| Video element | Graph field |
|---|---|
| Thesis | identity.misinterpretation_rule |
| Engine diagram | identity.operator_priors + preferred_theories |
| Timing analysis | timing_profile.doctrine_hypothesis + timing_measured |
| Bits breakdown | known_bits[].title + why_it_works + theory_links |
| Numbers segment | metrics{legacy,audience,popularity,theory,gap_value} + house rank |
| "Who's like him" | neighbors.json (latent space) |
| Type classification | humor_type.primary + secondary + scores |
| Mode/repertoire | modes.signature + repertoire |
| Specials | specials_rated[] + specials.json + specials_dark.json |
| Historical context | generation.id + recognition{cc2004,rs2017,paste_2017,c4_2007} |
| Theory links | theory_links[] + PAPER_ARXIV §2.6 |

---

## Series 2: THEORY OF COMEDY (the lecture series)

**Format:** 12–18 min per episode. One theory/concept per episode.
**Host model:** talking-head + animated diagrams + comedy clips as evidence.
**Data source:** `PAPER_ARXIV.md` §2.6 + `rankings/theory_content.json` + graphs.

### Episode map
| # | Topic | Core theory | Comedy examples (from our data) |
|---|---|---|---|
| 1 | Why Anything Is Funny | The three theories (superiority/incongruity/relief) + BV | Hobbes "sudden glory" → roast type board; Kant "strained expectation" → absurdist board; McGraw & Warren BV → dark-confessional |
| 2 | Bergson: The Mechanical in the Living | Le Rire, rigidity as comedy | rigidify operator (Carlin euphemism execution); Gillis "idiot-warlord" as mechanical commitment; Casey Rocket's freezes |
| 3 | Freud: Joke-Work | Condensation, displacement, tendentious vs innocent | Seinfeld "noticing" (displacement); Hicks tendentious; Silverman provocateur |
| 4 | Incongruity & Resolution | Beattie → Kant → Ritchie IR/SD | double_interpret operator; Wright impossible objects; Emo Philips |
| 5 | The 15 Comedy Operators | Our operator taxonomy + fitted weights | mistake_identity +.0065 (highest lift); juxtapose +.0047; split_knowledge (commonest, below average) |
| 6 | Benign Violation | McGraw & Warren, 3 conditions | taboo field analysis; dark board; Carlin 7 words; Gervais awards-show |
| 7 | GTVH: The 6 Layers | Raskin/Attardo knowledge resources | Script Opposition + Logical Mechanism + Situation + Target + Narrative + Language, mapped to graph fields |
| 8 | Timing: The Physics of Laughs | Pause ladders, hold patterns, DPV | Norm's moth (measured: 6 pauses in 2 min, none <1.16s); Louis confession holds; Burr self-check pauses |
| 9 | Status: The Invisible Game | Status dynamics in every joke | status_invert operator (391 bits, +.0038 lift); Pryor→Chappelle lineage; Stewart Lee deconstruction |
| 10 | The Line: Taboo & Violation | BV applied to taboo sets | dark board (50 specials); Hicks advertising-as-war; Chappelle close-but-not; norm's "too soon" |
| 11 | Types: The 13 Schools | Our humor_type taxonomy | by_type boards: observational (Rock), rant (Carlin), absurdist (Wright), meta (Burnham), character (Robin) |
| 12 | The Future: AI & Comedy | Our synthetic roster + agent harness | Chorus Machine, Heckler Protocol, Archivist; NoSlop gates; the anti-slop problem |

### Episode structure
```
OPEN (0:00–1:00)
  The question: "What makes anything funny?"
  Clip montage of the concept across 3–4 comics

THEORY (1:00–5:00)
  Animated diagram of the theory
  Primary source: Bergson text / Freud quote / BV paper
  [ANIM: mechanical-living diagram, script opposition, etc.]

THE EVIDENCE (5:00–12:00)
  3–5 comedy clips as proof
  Each: setup → mechanism named → punchline lands
  Data overlay: operator frequency, lift weight, bit count
  [GRAPHIC: "this operator fires in N% of measured bits"]

THE DEEP CUT (12:00–15:00)
  One unexpected application
  e.g. "Bergson predicted Gillis 124 years early"
  Cross-cultural angle from COUNTRY_THEORY.md

CLOSER (15:00–18:00)
  What this theory can't explain (honest limits)
  Next episode teaser
```

---

## Series 3: COMEDY ACROSS BORDERS (cross-cultural + music)

**Format:** 10–15 min per episode. Comparison-driven.
**Data source:** `COUNTRY_THEORY.md` + `by_continent.json` + `by_country.json`
+ neighbors.json + PAPER_ARXIV §2.6.

### Episode map
| # | Title | Angle | Data |
|---|---|---|---|
| 1 | UK vs US: Why They Laugh Differently | Tsukkomi vs solo; class vs race; panel-show culture | COUNTRY_THEORY variables 1–4; by_country boards (UK #1 Stewart Lee vs US #1 Carlin); C4-2007 poll vs CC-2004 |
| 2 | Black Comedy: Pryor → Rock → Chappelle → Hart | The lineage + what changed | influence graph (Pryor→Murphy x10); humor_type dark-confessional board; generation boards; gap analysis (Hart overrated +0.525 vs Pryor underrated) |
| 3 | Jazz Riffing → Comedy Riffing | Predictive processing: expectation violation as the common engine | Jazz riff = pattern establishment + violation + return; comedy riff = setup + punchline + tag. Casey Rocket as pure violation (no return). Theo as violation-with-resolution. Mechanism weights: mistake_identity +.0065 (pattern-break) vs split_knowledge (pattern-maintain) |
| 4 | Casey Rocket vs Theo Von: Two Engines | The deepest contrast in our data | Casey: absurdist, torrential + freezes, neighbor Montgomery 0.63. Theo: surreal, slow drawl + precision, neighbor Lock 0.44. Same "weird" — completely different mechanisms. KT data for Casey. |
| 5 | Nigeria vs US: Comedy Without the Algorithm | Basketmouth, Alibaba; distribution as comedy variable | COUNTRY_THEORY variable 6 (distribution); Nigeria scene (7 comics); Basketmouth 12.5M views; beef culture as status game |
| 6 | China: Comedy Under Constraint | Xiaoguo; censorship as form | COUNTRY_THEORY variable 3 (state pre-approval); China 8 comics; wordplay-over-provocation; tsukkomi variable |
| 7 | Australia/NZ: The Antipodean Voice | Gadsby, Jefferies, Kiwi scene | by_country boards; AUS/NZ 11 comics; Melbourne Barry as regional award |
| 8 | India: 960M Reasons | Zakir Khan, Biswa; scale as variable | India 7 comics; Zakir 8.5M subs; YouTube-native distribution |

### Music analogy framework (episodes 3–4)
```
JAZZ RIFF                          COMEDY RIFF
─────────────────────────────────────────────────
Pattern establishment              Setup
Harmonic expectation              Audience model (what's normal)
Chord substitution                 Punchline (violation)
Return to tonic                    Tag / callback
Improvisation over changes         Riffing over a topic

CASEY ROCKET = free jazz           Pattern → violate → freeze → next
  No return to tonic. Pure violation.
  Predictive processing: max prediction error, no resolution.

THEO VON = cool jazz               Pattern → violate → resolve → wisdom
  Return to tonic (the wise observation).
  Predictive processing: moderate error, resolution rewards.

THE MECHANISM MAP:
  mistake_identity (+.0065) = pattern BREAK (jazz substitution)
  split_knowledge (−.0014)  = pattern MAINTAIN (return to tonic)
  The highest-lift operator is the one that BREAKS expectations.
  That's why Casey Rocket works: he's pure mistake_identity.
```

---

## Series 4: THE LINE (taboo & violation)

**Format:** 8–12 min per episode. One taboo theme per episode.
**Data source:** `rankings/specials_dark.json` + graph taboo fields +
BV theory + by_type dark-confessional/roast/provocateur boards.

### Episode map
| # | Title | The line | Examples |
|---|---|---|---|
| 1 | The Seven Words | Language taboo | Carlin → FCC v. Pacifica; what's still unsayable |
| 2 | Punching Up vs Down | Status + target | BV condition: benign requires "alternative norm"; roast board; Silverman provocateur |
| 3 | Race: The American Fault Line | Pryor → Rock → Chappelle → Hart lineage | Dark-confessional board; the "close but not" technique; Chappelle's close-but-not as BV at max |
| 4 | Death, Grief, and the 24-Hour Rule | Tragedy timing | BV psychological distance condition; Tig Notaro's elephant; Norm's moth |
| 5 | Sex: From Lenny to Louis | Sexual taboo decay | Lenny Bruce → Carlin → Louis; what's still transgressive |
| 6 | Religion: The Last Taboo | Blasphemy across cultures | COUNTRY_THEORY variable 2; Hicks' atheist bits; Stewart Lee's Catholic material |
| 7 | The Holocaust Joke Problem | BV at its limit | What makes some Holocaust jokes work (Hicks) and most not; psychological distance as the only lever |
| 8 | Self-Deprecation vs Self-Destruction | The target is yourself | Expose_self_blindness operator; Hedberg; Norm's "I'm a garbage person" |
| 9 | The Machine's Line | AI comedy and taboo | Synthetic roster (Heckler Protocol); what AI can/can't do with taboo; NoSlop gates |
| 10 | Where Is the Line in 2026? | Current state | Panel of comedians + our data; C4 vs CC-2004 shifts; what changed |

---

## Series 5: THE MACHINERY (meta — how we measure comedy)

**Format:** 6–10 min per episode. Behind-the-scenes of the measurement.
**Data source:** everything. The repo IS the content.

| # | Title | Content |
|---|---|---|
| 1 | How We Rank Comedians | House board methodology; P1/P2; why Norm isn't #1 |
| 2 | The 15 Comedy Operators | Taxonomy + fitted weights; mistake_identity leads |
| 3 | Why Ratings Lie | IMDb biases; audience ≠ critics; the gap as product |
| 4 | The AI Comedy Problem | NoSlop gates; agent harness; what "funny" means to a machine |
| 5 | Building the Comedy Graph | 1959 profiles; discovery pipeline; OTM; how we found them |
| 6 | The Line We Drew | Exclusion list; ethics; what we won't measure |

---

## Cross-series data assets

| Asset | Powers |
|---|---|
| `comedians/*/comedian-graph.json` | Series 1 (episodes), Series 2 (examples), Series 3 (comparisons), Series 4 (taboo fields) |
| `rankings/theory_content.json` | Series 2 (operator weights), Series 3 (jazz analogy), Series 5 (methodology) |
| `rankings/by_type.json` | Series 2 (types episode), Series 3 (comparison), Series 4 (dark/roast/provocateur) |
| `rankings/by_generation.json` | Series 1 (historical context), Series 3 (cross-generational), Series 4 (taboo decay) |
| `COUNTRY_THEORY.md` | Series 3 (all episodes) |
| `PAPER_ARXIV.md` §2.6 | Series 2 (theory grounding), Series 5 (methodology) |
| `rankings/specials_dark.json` | Series 4 (dark board, all episodes) |
| `rankings/neighbors.json` | Series 1 ("who's like him"), Series 3 (engine comparison) |
| `KT minutes + Jev analyses` | Series 1 (Casey/Kam episodes), Series 4 (norm's moth) |
| `metrics.json` (5 lenses) | Series 1 (numbers segment), Series 5 (rating system) |
| `rankings/bits.json` | Series 1 (bit breakdowns), Series 4 (taboo examples) |

## What we DON'T have (gaps for future episodes)

- **Timed word-level data** for most comics (only 4 measured sets — Louis, Norm, WT, Kam). Blocks timing-analysis episodes for 15/18 measured comics.
- **Audio** for laugh-density overlays (blocked on cookies for new pulls).
- **Comment sentiment** (weak lexicon — needs comedy-specific training).
- **Non-English transcripts** (Xiaoguo captions unavailable; whisper path blocked).
- **Arena votes** (no BT leg data yet — TOP2026 ballot gated on owner).

## Production notes

- **Clips:** embed from YouTube (official channels only, per no-search law).
  Commentary/criticism = fair use. Never rehost. Always link.
- **Voice-over:** graph text is hypothesis until measured — always frame
  as "our data suggests" not "this is the truth."
- **Graphics:** engine diagrams, radar charts, neighbor maps, type boards —
  all generated from JSON. No manual design needed for data overlays.
- **Cadence:** Series 1 weekly (15 episodes = 15 weeks). Series 2 biweekly
  (12 episodes = 24 weeks). Series 3 monthly (8 episodes = 8 months).
  Series 4 monthly (10 episodes = 10 months). Series 5 as-needed (6 episodes).

---

## Series 6: THE PHILOSOPHY OF LAUGHTER (the deep series)

**Format:** 15–20 min per episode. One philosophical question per episode.
**Tone:** visual-essay (Nerdwriter / Like Stories of Old style), not lecture.
**Data source:** `PAPER_ARXIV.md` §2.6 + graphs + COUNTRY_THEORY + new rasa mapping.

### Episode map

| # | Title | Question | Theory | Comedy data |
|---|---|---|---|---|
| 1 | Why Is Self-Realization Funny? | When the room laughs at recognition, what is it recognizing? | Morreall incongruity + our split_knowledge operator (3011 bits) | The "I'm not alone" signal; Norm's moth (recognition of absurdity); Louis confession machine |
| 2 | Laughter Is a Social Animal | Why do we laugh 30× more in groups? What is laughter FOR? | Provine 2000 (laughter as social grooming); evolutionary biology | status_reversal operator; crowd-improv type board; the alliance loop |
| 3 | Sudden Understanding | The "aha" moment as comedy mechanism | Ritchie surprise-disambiguation; Minsky frame-shift | double_interpret (588 bits); Emo Philips; Steven Wright; the garden path |
| 4 | Absurdity, Horror, Grief, Disbelief | The four registers of dark comedy | BV + dark board (50 specials); Kubler-Ross applied to jokes | dark-confessional type; Hicks; Tig Notaro's elephant; Norm's cancer bit |
| 5 | Animals Don't Laugh (Or Do They?) | Play-fighting, tickling, the evolutionary origin | Darwin 1872; Gervais & Wilson 2005; Vettiger et al. 2020 (rat tickling) | BV as evolutionary mechanism; "mock attack" = benign violation in nature |
| 6 | Laughter Across Cultures | Why the same joke dies in Lagos and kills in London | COUNTRY_THEORY (7 variables); tsukkomi; taboo sets; censorship | by_country boards; Nigeria beef culture; China wordplay; Japan manzai |
| 7 | The Sanskrit Theory of Comedy | Rasa theory, hasya, and why ancient India mapped laughter better than Aristotle | Bharata Natyashastra; Abhinavagupta; rasa-sutra | 9 rasas mapped to 13 humor types; hasya subtypes vs our type board |
| 8 | Tantra and the Sacred Laugh | The role of laughter in tantric practice; the "ugly truth" as liberation | Kashmir Shaivism; Chögyam Trungpa; the "crazy wisdom" tradition | Louis confession machine as tantric move; Stewart Lee deconstruction; the taboo as sacred boundary |
| 9 | Why Is Awkwardness Funny? | The comedy of social discomfort | Goffman face-work; BV via "loss of face" | Seinfeld observational; cringe comedy; the "room notices" mechanism |
| 10 | The Phenomenology of the Laugh | What happens in the 200ms between surprise and laughter? | McGraw & Warren BV neural pathway; fMRI comedy studies | Measured timing data (Louis 8.16s hold); DPV arXiv paper |
| 11 | Comedy and Madness | Are comedians funnier because of mental illness, or despite it? | Greengross & Miller 2012; affiliation vs self-defeating humor | Our M5 construct test (failed — priors don't predict); the honest answer |
| 12 | Can Machines Be Funny? | The computational humor problem and our synthetic roster | THInC (F1 0.85); NoSlop gates; the agent harness | Chorus Machine, Heckler Protocol, Archivist; the anti-slop problem |

### RASA THEORY DEEP-DIVE (Episode 7 outline)

The Natyashastra (c. 200 BCE – 200 CE) catalogs 9 rasas (emotional
flavors) that a performance should evoke. The 9th is **hasya** (laughter/
mirth), which Bharata subdivides into subtypes. This is the oldest
systematic taxonomy of humor — and it maps directly to our 13-type board.

```
NATYASHSTRA RASA          FUNNYGRAPH HUMOR TYPE          OPERATOR
─────────────────────────────────────────────────────────────────
hasya (mirth)             observational                   split_knowledge
  ├ aphasya (suppressed)  deadpan / one-liner             literalize
  ├ upahasya (coarse)     roast / provocateur             status_invert
  ├ahasya (pure joy)      clean-everyman                  benign_violation
  └ avahasya (ridicule)   roast / character               character_violation

karuna (compassion/grief) dark-confessional               expose_self_blindness
raudra (anger)            rant                             rigidify
bhayanaka (fear)          dark / taboo                     benign_violation
bibhatsa (disgust)        provocateur                      unmask
veera (heroism)           storytelling (hero journey)      status_reversal
adbhuta (wonder)          absurdist / surreal              juxtapose
shanta (peace)            meta / contemplative             (no operator — negative space)
```

**Key insight:** The Natyashastra treats hasya as ONE of NINE rasas —
not the goal of comedy but a flavor in a palette. Our type board treats
13 types as parallel flavors. The mapping suggests: the best comedy
doesn't maximize hasya — it CYCLES through rasas. Chappelle's
dark-confessional = hasya→karuna→hasya. Carlin's rant = raudra wrapped
in hasya. Norm's moth = hasya→bhayanaka→shanta.

**Abhinavagupta's gloss (10th c.):** Rasa is not "the emotion" but the
"aesthetic savor" — the audience's experience of the emotion. This maps
to our BV framework: the violation is the emotion; the benign is the
aesthetic distance; the rasa is what the audience actually tastes.

**Visual for the episode:** An animated rasa-chakra (wheel) with the
9 rasas at their cardinal points, and a real-time tracker showing which
rasa a comedian is evoking moment-by-moment. Overlay: Chappelle's
Killin' Them Softly cycling through hasya→karuna→hasya in a single bit.

### TANTRA AND THE SACRED LAUGH (Episode 8 outline)

The tantric tradition treats the "ugly truth" as the path to liberation
— not despite its ugliness but BECAUSE of it. Key threads:

- **Chögyam Trungpa, "crazy wisdom"**: the guru who acts mad to break
  the student's social conditioning. Louis's confession machine does
  the same thing: the "crazy" statement breaks the room's social
  conditioning about what's sayable.
- **Kashmir Shaivism, spanda**: the universe as vibration/pulse. The
  comedic timing pulse (setup→violation→silence→laugh) mirrors the
  spanda rhythm. Our measured timing data (pause bins) IS a spanda map.
- **The taboo as sacred boundary**: in tantra, transgression of social
  norms is a deliberate spiritual move (not nihilism — the violation
  must be WITHIN a sacred container). Louis's container = the comedy
  club = the ritual space. The room knows the rules of the ritual, so
  the transgression is safe. This is BV as ritual theory.
- **The "ugly truth" as liberation**: Carl Jung's shadow work — the
  things we refuse to acknowledge are the things that control us. Louis
  brings the shadow into the light and the room laughs because it
  recognizes its own shadow. This is the deepest reading of split_knowledge:
  the audience's unconscious material made conscious through comedy.

**Comparison for the episode:**
| Tradition | The sacred laugh | Container | Transgression |
|---|---|---|---|
| Tantra | Spanda (cosmic pulse) | Ritual initiation | Social norms |
| Trungpa | Crazy wisdom | Teacher-student | Ego/conditioning |
| Louis | Confession machine | Comedy club | Sayable/unsayable |
| Stewart Lee | Deconstruction | Edinburgh Fringe hour | Comedy itself |

---

## Series 7: TIMING LAB (the AI delivery experiment)

**Format:** 8–12 min per episode. Same text, different deliveries.
**Hook:** "What happens when you read Louis C.K.'s set in five different ways?"
**Data source:** `sets[].timing_measured` + characters2 voice engine
(fish TTS, clone `fb015415`) + `analysis/louis_roadrage_analysis.json`.

### The experiment
Take the Road Rage measured set (337 words, 57 pauses, 8 punch pauses).
Render it through our voice engine in **five delivery conditions**:

```
CONDITION 1: LOUIS (ground truth)
  Original audio. The measured delivery. 171.4 WPM, 57 pauses,
  max hold 8.16s. The benchmark.

CONDITION 2: NO PAUSES (machine read)
  TTS reads the text at constant speed, zero pauses. No timing.
  Prediction: the jokes die. The violation fires but the room has
  no time to metabolize it. This is the "AI comedy problem" made
  audible: the content is identical but the comedy is gone.

CONDITION 3: OVER-PAUSED (exaggerated timing)
  Same text, but all punch pauses doubled (8.16→16.32s, 5.32→10.64s).
  Prediction: the comedy collapses into awkwardness. The pauses
  become THE joke instead of serving the joke. Timing has a Goldilocks
  zone.

CONDITION 4: WRONG PAUSES (randomized)
  Same text, same total pause time, but pauses placed at random
  positions (not at punch points). Prediction: some jokes survive
  (content-driven), some die (timing-driven). This is the experiment
  that PROVES timing gates content (DPV paper claim).

CONDITION 5: DIFFERENT VOICE (norm-style delivery)
  Same text, but delivered with Norm's timing doctrine (deadpan,
  no acceleration, single long hold at the end). Prediction: the
  confession reads as deadpan comedy instead of manic confession.
  The engine changes; the content stays.

CONDITION 6 (bonus): THEO-STYLE
  Same text, delivered with Theo Von's swamp-philosopher timing
  (slow drawl, long pauses before images, sudden precision).
  Prediction: the dark content becomes surreal-wisdom instead of
  manic-confession.
```

### What this proves
1. **Timing gates content** (DPV claim, arXiv 2605.00143) — audible proof
2. **The engine is separable from the material** — same words, different
   comedy, depending on delivery
3. **The Goldilocks zone** — too little timing kills comedy, too much
   kills comedy, the measured Louis delivery IS the zone
4. **AI comedy problem** — Condition 2 (no pauses) IS what AI-generated
   comedy sounds like. The content is fine; the timing is dead.

### Production requirements
- Fish TTS (free tier) + Louis voice clone `fb015415`
- Scribe JSON for the Road Rage window (word timings from characters2)
- Five renders + original = 6 audio tracks
- Visual: waveform comparison (Louis vs each condition) + laugh-track
  overlay (our laugh_sim data where available)

### Episode structure
```
OPEN (0:00–1:00)
  "Same words. Same comedian. Five different deliveries.
   Only one is funny. Let's prove it."

THE SETUP (1:00–3:00)
  Show the measured data: 57 pauses, 8 punch pauses, 8.16s max hold.
  "This is the timing map of a 2-minute comedy window."

CONDITION 2: NO PAUSES (3:00–5:00)
  Play. Let the deadness land.
  INTERLUDE: "This is what AI comedy sounds like. The words are
  fine. The timing is dead. The room has no time to metabolize
  the violation. This is the DPV paper made audible."

CONDITION 3: OVER-PAUSED (5:00–6:30)
  Play. The awkwardness.
  INTERLUDE: "The pauses became the joke. Timing has a Goldilocks
  zone. Too little kills it. Too much kills it differently."

CONDITION 4: WRONG PAUSES (6:30–9:00)
  Play. Some jokes survive, some die.
  INTERLUDE: "The content-driven jokes survived. The timing-driven
  jokes died. This proves: timing and content are SEPARABLE comedy
  mechanisms. Louis is doing both."

CONDITION 5: NORM-STYLE (9:00–11:00)
  Play. Deadpan confession.
  INTERLUDE: "Same content, different engine. The confession reads
  as deadpan instead of manic. The TYPE of comedy changed. The
  words didn't."

CONDITION 1: LOUIS (11:00–13:00)
  Play the original. After the alternatives, the master delivery
  is audible in a way it never was before. The 8.16s hold lands
  differently now.

CLOSER (13:00–15:00)
  "Timing is not decoration. It is a comedy mechanism on par with
  the punchline. The content gives you the violation. The timing
  gives the room time to metabolize it. Remove either one and the
  comedy dies. This is why AI can't be funny yet — it has the
  content but not the clock."

[GRAPHIC: waveform comparison — 6 tracks stacked, pauses visible
as gaps, the Louis track highlighted]
```

---

## Cross-series data assets (updated)

| Asset | Powers |
|---|---|
| `sets[].timing_measured` | Series 7 (all conditions), Series 1 (timing overlays) |
| `characters2 voice engine (fish TTS)` | Series 7 (delivery renders) |
| `analysis/louis_roadrage_analysis.json` | Series 7 (beat map), Series 1 (Louis episode) |
| `COUNTRY_THEORY.md` | Series 3 + Series 6 ep.6 |
| `rankings/theory_content.json` mechanism_weights | Series 2 ep.5, Series 6 ep.7 (rasa mapping) |
| `rankings/specials_dark.json` | Series 4 + Series 6 ep.4 |
| `PAPER_ARXIV.md` §2.6 | Series 2 + Series 6 (all theory grounding) |
| NEW: rasa↔type mapping (this doc) | Series 6 ep.7 |

## RASA MAPPING REFERENCE (for graphics + Series 6)

```
The 9 Rasas (Natyashastra) → 13 Funnygraph Types → 15 Operators

RASA          TYPE              OPERATOR           BITS  LIFT
────────────────────────────────────────────────────────────
hasya         observational     split_knowledge    3011  -0.0014
karuna        dark-confessional expose_self_blind   —     —
raudra        rant              rigidify            182   -0.0013
bhayanaka     (taboo/dark)      benign_violation    —     —
veera         storytelling      status_reversal     —     —
bibhatsa      provocateur       unmask              —     —
adbhuta       absurdist/surreal juxtapose           157   +0.0047
shanta        meta              (negative space)    —     —

KEY INSIGHT: hasya is ONE of nine rasas, not THE goal.
The best comedy CYCLES through rasas:
  Chappelle: hasya → karuna → hasya (Killin' Them Softly)
  Carlin:    raudra wrapped in hasya (list sermon)
  Norm:      hasya → bhayanaka → shanta (the moth)
  Louis:     karuna disguised as hasya (Road Rage)
  Casey:     adbhuta × hasya (absurd-firecracker)
```

## Production priority (updated)

| Priority | Series | Why now |
|---|---|---|
| 1 | WHY IS X FUNNY? (ep 1–3) | Proven template, deepest data, fastest to produce |
| 2 | TIMING LAB (Louis experiment) | Uses existing voice engine + measured set; highest novelty |
| 3 | THEORY OF COMEDY (ep 1–5) | Grounds everything else; PAPER_ARXIV §2.6 is ready |
| 4 | THE PHILOSOPHY OF LAUGHTER (ep 1, 7) | Self-realization + rasa = most original content |
| 5 | COMEDY ACROSS BORDERS (ep 1, 3–4) | UK data just populated; Casey/Theo comparison is viral-ready |
| 6 | THE LINE (ep 1–2) | Taboo content needs careful framing; build audience first |
| 7 | THE MACHINERY (ep 1–2) | Meta content; good for channel credibility |

---

## REFERENCE CHANNEL: Comedy Without Errors (the gold standard)

**Channel:** @ComedyWithoutErrors · 31.3K subs · 19 videos
**Tagline:** "Inside techniques, gossip and analysis of comedy. For
comedy nerds only. Dissecting the frog, analysing its insides."

### Why this channel IS the model

| What they do | What we can do better (with data) |
|---|---|
| 60-77 min deep dives (Louis Part 1 = 1:17:46, 495K views) | Same length, but with measured timing overlays |
| Named chapter sections (14 chapters in Louis Part 1) | Auto-generated from beat classification |
| Personal essayist voice (vulnerable, "I became a fanatic") | Same tone (GOLD.md) + graph-backed claims |
| Interview clips as evidence (Louis explaining his process) | Structure 11: self-analysis mining |
| "Dissecting the frog" metaphor | We LITERALLY dissect: operators, pause bins, BV scores |
| Creator is a working comedian (filmed his own special) | Our narrator voice = fan-with-notebook (GOLD.md) |
| 19 videos in 3 years (quality > quantity) | Our structures make quality scalable |
| Patreon-supported | Direct monetization path |

### Their top performers (what the audience wants)

| Video | Views | Length | Format |
|---|---|---|---|
| Bo Burnham - Inside In Context | 473K | 1:07:40 | Single-comic deep dive |
| Stewart Lee: The Audience is the Problem | 533K | ~45min | Single-comic deep dive |
| How Dave Chappelle Delivers a Callback | 401K | ~20min | Technique breakdown |
| We Need to Talk About Louis Part 1 | 495K | 1:17:46 | Multi-part saga |
| James Acaster - Unreliable | 239K | ~60min | Single-comic deep dive |
| Billy Connolly - Winging It | 192K | ~30min | Single-comic deep dive |

**Pattern:** Single-comedic deep dives at 20-70 minutes are the sweet
spot. Technique breakdowns (callback, heckler, rhythm) are the second
format. Multi-part sagas build loyal audiences.

### What they have that we don't
1. **A working comedian's voice** — the creator performs, so the
   analysis has performer credibility. We have 29,617 measured bits
   and 18 comics with laughter-fitted scores. Different credibility.
2. **Interview access** — they've interviewed Guy Montgomery, Josh
   Harmon, Jerrod Carmichael. We have YouTube interview clips to mine.
3. **Narrative voice** — "I was in my first year of uni. I stumbled
   across a clip of Chewed Up." Personal story as frame. We can do
   this: the narrator IS a fan who built a database.

### What we have that they don't
1. **Measured timing data** — 8.16s holds, 57 pauses, beat maps.
   They describe timing qualitatively; we QUANTIFY it.
2. **1959 profiles** — we can compare Louis to 18 measured comics
   and 1941 provisional ones. They analyze one comic at a time.
3. **Fitted mechanism weights** — mistake_identity +0.0065 lift.
   They say "this works"; we say "this works in N% of measured bits
   with lift +X."
4. **The house board** — our proprietary ranking. They have opinions;
   we have a board with sweep intervals.
5. **The overlay system** — real-time beat labels, pause timers,
   operator fire indicators. They use chapter markers; we use
   data-driven annotations.

### The synthesis (our format = their voice + our data)

```
THEIR STRUCTURE (from Louis Part 1):
  Chapter 1: Personal relationship with the comic
  Chapter 2: The cancellation / context
  Chapter 3-12: Deep analysis with clips
  Chapter 13: The aftermath
  Chapter 14: Where we are now

OUR STRUCTURE (from BEAT_MAP.md):
  Cold open: transgressive clip + question
  Machine: beat-by-beat with overlays (20 min)
  Philosophy: BV + timing + status
  Comparison: who else does this
  Chronology: the evolution
  Close: bookend clip + "now you know why"

THE SYNTHESIS:
  Cold open: transgressive clip (THEIR hook style)
  Personal: "I became a fanatic" essay moment (THEIR voice)
  Machine: beat-by-beat with overlays (OUR data advantage)
  Philosophy: BV + timing + status (OUR theory)
  Interview: comic explains their own engine (THEIR evidence style)
  Comparison: who else + data (OUR neighbors + type boards)
  Chronology: timeline + clips (THEIR documentary style)
  Close: bookend + "now you know why" (OUR structural device)
```

### The narrator voice (from their transcripts + GOLD.md)

**Their voice (verbatim patterns):**
- "I try to make it seem like I'm just getting this out, but I know
  all the moves, I know every little piece of it."
- "When I was a teenager, Louis C.K. was the pinnacle of comedy."
- "This will sound insane, but when I started writing jokes, I would
  hear them in his voice."
- "He wasn't just a comedian, but a hero and a role model."

**Our narrator voice should be:**
- A fan who built a database. Not a professor. Not a critic.
- "I counted 4,478 bits of Carlin. Here's what I found."
- "The machine has a name. And if you can see the machine, you'll
  see it everywhere."
- "Louis C.K. is not a comedian who says terrible things. He's a
  comedian who makes terrible things TRUE."

**The key rule (from GOLD.md):** Never explain over clips. Play the
clip, pause, analyze, resume. The clip IS the text. The analysis IS
the close reading. The narrator doesn't talk about the joke — they
read it aloud, like a poem.
