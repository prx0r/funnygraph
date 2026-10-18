# LITERATURE — timing, music, and comedy research

> Research backing the FORMULA.md tone rules and THE MUSIC overlay.
> Searched 2026-10-18. Key finding: timing is not a delivery detail —
> it is a cognitive mechanism. The music framing in GOLD-CARLIN is
> empirically defensible, not just aesthetic.

---

## THE FIVE PAPERS THAT MATTER

### 1. Attardo & Pickering 2011 — "Timing in the performance of jokes"
*Humor: International Journal of Humor Research, 24(2), 227–247*

The foundational empirical paper. Defines timing as two measurable things:
- **Pause distribution** (especially before the punchline)
- **Speech rate** (syllables per second)

Key findings:
- Punchlines preceded by substantial pauses (0.6–0.8s+)
- Speech rates in English: 3.47–5.7 syllables/sec depending on condition
- Norrick's prediction: punchlines delivered FASTER than setup ("more rapid fluid delivery")
- Punch lines may be delivered with altered rhythm and set apart by pauses
- Conclusion: "the theory of timing in joke performance is in serious need of further research" — we are filling that gap

**Maps to:** our pause taxonomy (very_short/short/substantial/topic), punchline_hold_ms, the Carlin syllable analysis

---

### 2. DPV framework — "Timing is Everything: Temporal Scaffolding of Semantic Surprise in Humor"
*arxiv 2605.00143. 828 Chinese stand-up performances, 86 hours, 2017–2025*

The largest-scale timing study. Proposes the DPV (differential prediction-violation) framework:

- **Setup** establishes temporal AND semantic expectations: regular ~0.6s pauses, small semantic distances between consecutive sentences
- **Punchline** violates BOTH simultaneously: extended pause (~1.5s) + semantically distant content
- **Strategic coupling distinguishes EXPERTISE**: high-performing comedians show stronger temporal-semantic coupling than low performers. This is not content complexity — it's the coordination of WHEN and WHAT.

Three findings:
1. Pause variability (temporal unpredictability) predicts appreciation
2. Slower speech rate → higher appreciation (more processing time for prediction elaboration)
3. Few well-placed surprising moments > constant moderate incongruity (the brain prioritizes resolving large discrete violations)

**Maps to:** the Louis 8.16s confession (extreme temporal violation at the semantic peak), BV simultaneous condition (temporal coupling IS the simultaneity), our "timing GATES cognitive access" claim in theory_links.dpv

---

### 3. TAMS — "Timing structures in live comedy: A matched-sequence approach"
*PNAS Nexus 5(1), pgaf394, 2026-01-05*

Applies MUSIC PERFORMANCE ANALYSIS methods to stand-up. The method is literally borrowed from genetics (sequence matching) and music performance (expressive timing).

Key concepts:
- **Content pillars**: recurring sequence units that appear frequently in a show — the "themes" identified by repetition, not by content analysis
- **Timing beams**: consistent temporal scaffolding around content pillars — like a musical structure
- **Imaginary metronome**: when inter-onset or inter-end intervals are held steady across performances, the comedian is performing "as if to an imaginary metronome where the start or end of a segment needs to occur at a particular time in the overall melody of the joke"
- **Audience impacts microtiming**: same joke, 20 performances — audience interaction tightens punchline timing (pauses and speech segments become more parallel)
- **Show evolution**: TAMS visualizations reveal how content accumulates over performance iterations — the show "stabilizes" over a tour

**Maps to:** the Carlin "jazz feeling" analysis (rhythm held steady across performances), our "stay in the bit" delivery continuity rule, the panel-show safety-net mechanism (audience/other comics as timing co-regulators)

---

### 4. TIC-TALK — multimodal timing database
*CHum 2026. 5,400+ temporally aligned segments, 90 specials, 2015–2024*

The multimodal resource. Captures language + gesture + audience response jointly:
- Comedic timing = short-lag coordination across verbal, acoustic, and visual cues
- Gestures, pauses, and interaction with laughter are "essential components of meaning and rhythm"
- Each modality retains native temporal resolution; signals merged by hierarchical temporal containment
- 384-dim sentence-BERT embeddings per segment

**Maps to:** our multimodal roadmap (RESEARCH-multimodal-comedy.md), the Carlin physical-performance-alignment chapter (body in rhythm with voice), the need for a MUSIC overlay that tracks pitch/speed/gesture alongside semantics

---

### 5. McGraw & Warren — Benign Violation Theory
*Psychological Science 21(8), 1141–1149, 2010; Warren et al. 2021 integrative review*

The theory our whole graph is built on. Core claim: humor occurs when a violation is appraised as BOTH wrong AND okay, SIMULTANEOUSLY.

Three conditions that make a violation benign:
- (a) alternative norm suggesting acceptability (resolution)
- (b) weak commitment to the violated norm
- (c) psychological distance from the violation

**The timing link (from McGraw & Warren 2014, SAGE):**
> "both the appraisal that there is a violation and the appraisal that everything is benign need to occur simultaneously. This explains why timing, brevity, and surprise are so important in comedy."

Timing is not decorative — it is the MECHANISM that makes simultaneous appraisal possible. Too short: violation wins (uncomfortable). Too long: benign wins (boring). The hold duration is the Goldilocks zone.

**Maps to:** the Louis 8.16s hold (the simultaneous condition operationalized), our BV triangle overlay, the "laugh is relief — the room survived the violation" reading

---

## SUPPORTING FINDINGS

### Schempp 2024 — "Comic Timing in Contemporary Slapstick Films"
*Projections: The Journal for Movies and Mind, 18(2)*

Defines comic timing as **perceived durational incongruity** — two types:
1. Standard: setup durationally LONGER than payoff
2. Non-standard: extended duration as self-referential humor (metajoke about timing itself)

The extended-duration gag "represents a metajoke about the nature of comic timing." Establishes expected rhythm through decades of repetition, then subverts it.

**Maps to:** Lock's defiance of prescriptive rhythm (GOLD-LOCKE-FULL Ch13), Carlin's shell-shock-vs-battle-fatigue comparison (word count doubles = duration manipulation), Acaster's big-bang-blackout-monologue openings

### Zhong 2026 — "Prosodic Markers in Mandarin Stand-Up Comedy"
*Speech Prosody 2026*

Production vs perception dissociation:
- **Production**: professional comedians significantly LENGTHEN pauses before punchlines vs baseline structural pauses. The pre-punchline pause is an "explicit pragmatic marker."
- **Perception**: no optimal pause duration found in audio-only listening. Humor perception is primarily content-driven for narrative jokes.
- **Implication**: timing strategies are shaped by structural/interactional demands of LIVE performance, not by fine-grained perceptual preferences.

**Maps to:** why the panel format changes Lock's timing (audience interaction reshapes the temporal structure), why measured timing must come from live/special recordings not lab playback

### Norrick 2001 (via Attardo & Pickering)
> "timing is a composite buildup of hesitations, false starts, repetitions and formulaicity in the build-up along with a more rapid, fluid delivery of the punch-line"

The punchline is FASTER, not slower. The setup is the slow part.

**Maps to:** Carlin's speed analysis ("spitting out a setup insanely quickly before digging into a punch line"), the DPV finding that slower overall rate + specific fast punchlines = expertise

### Seinfeld on syllables (via characters2 SKILL-seinfeld.md)
> "you count syllables… it's more like songwriting"

The comic-as-songwriter framing is not metaphor — it's craft instruction. Syllable counting is a real technique used by working comedians.

**Maps to:** GOLD-CARLIN's entire syllable-melody analysis (8-syllable line, subverted to 7, break to 2×2), our delivery-shape theory (hold-time → sentence rhythm)

---

## WHAT THIS CONFIRMS FROM THE GOLD TRANSCRIPTS

| Gold claim | Literature support |
|---|---|
| Carlin: "it really is a song… melody, subvert, climax" | TAMS (imaginary metronome), Seinfeld (syllable counting), DPV (temporal scaffolding) |
| Carlin: "25 words in 14 seconds" vs "nearly a second faster" | Attardo & Pickering (pause distribution + speech rate = timing) |
| Louis spec: 8.16s hold = Goldilocks zone | McGraw & Warren (simultaneous appraisal needs the hold), DPV (extended pause at semantic peak) |
| Locke: "sixth option" / garden path | DPV (prediction error resolution), incongruity theory |
| Acaster: unreliable narrator = dual-layer | BV (two simultaneous appraisals of the same event), split_knowledge |
| Lock: "panel format removes premise burden" | TAMS (audience impacts microtiming), Zhong (live interaction shapes timing) |
| Carlin: body-in-rhythm-with-voice | TIC-TALK (gesture-speech-audience coordination) |

---

## WHAT WE CAN CLAIM IN VIDEOS (grounded)

Safe to say in narration (with overlay citation):
- "Comedy timing is measurable: pause duration and speech rate. Attardo and Pickering established this in 2011."
- "The punchline works by violating two expectations at once — the timing AND the meaning. A 2026 study of 828 stand-up performances found that the best comedians couple these violations more tightly than anyone else."
- "Benign Violation Theory says humor requires two opposite appraisals to happen simultaneously. Timing is the mechanism that makes simultaneity possible."
- "Comedians count syllables. It's more like songwriting than writing. George Carlin was doing it before anyone was measuring it."

NOT safe without more data:
- Specific optimal pause durations (Zhong found no perceptual optimum — live performance is different)
- Cross-cultural universality of timing (DPV notes pause-duration-content relationships may vary by culture)
- Causal claims about any single comedian's timing (we have n=1 measured sets for most)

---

## CITE LIST (for video credits / paper)

1. Attardo, S. & Pickering, L. (2011). Timing in the performance of jokes. *Humor* 24(2), 227–247.
2. [DPV authors] (2026). Timing is Everything: Temporal Scaffolding of Semantic Surprise in Humor. *arXiv:2605.00143*.
3. Pope, R. et al. (2026). Timing structures in live comedy: A matched-sequence approach. *PNAS Nexus* 5(1), pgaf394.
4. [TIC-TALK authors] (2026). TIC-TALK: Pipeline and Database for the Multimodal Study of Comedic Timing. *CHum 2026*.
5. McGraw, A.P. & Warren, C. (2010). Benign violations: Making immoral behavior funny. *Psychological Science* 21(8), 1141–1149.
6. McGraw, A.P. & Warren, C. (2014). Benign Violation Theory. In *Encyclopedia of Humor Studies*. SAGE.
7. Warren, C., Barsky, A., & McGraw, A.P. (2021). What Makes Things Funny? *Perspectives on Psychological Science* 16(1), 41–65.
8. Schempp, A. (2024). Comic Timing in Contemporary Slapstick Films. *Projections* 18(2).
9. Zhong et al. (2026). Prosodic Markers in Mandarin Stand-Up Comedy. *Speech Prosody 2026*.
10. Norrick, N.R. (2001). Invective in conversation. *Humor* 14(3).
11. Attardo, S. & Raskin, V. (1991). General Theory of Verbal Humor. *Humor* 4(3–4).
