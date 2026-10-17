# ESSAY BANK — data point → essay → video pipeline

Living index. Every interesting measured finding gets logged here as a
probe, promoted to essay seed when it has a thesis, drafted when written.
Graphs hold per-comic seeds (source of truth); this is the cross-comic
pipeline view for content planning.

Status vocabulary: `probe` (data point noted) · `seed` (thesis + outline) ·
`drafting` · `drafted` · `video-ready` · `published`

Video titles are the working YouTube-facing titles — hook-forward, no
spoilers of the mechanism.

## How the machine feeds this bank

```
comedian-graph.json (WHO + per-beat decomposition)
  + theory/transcripts/ (60 specials, 395k words)
  + topic-signatures.json (negative space, licensing)
  + stylometry.json (measured sentence stats)
  + analysis/*.json (word-timed timing where audio exists)
        ↓ each surprising number is a probe
ESSAYS.md (this file)
        ↓ drafting
essay .md in theory/comedians/<slug>/essays/
        ↓ production
video (Deconstructed-for-comedy format)
```

---

## P0 essays (measured evidence in hand, ready to draft)

### E01 — The Eight-Second Confession
- **Data point:** Louis's longest hold (8.16s) lands exactly on the deflationary turn in roadrage ("I remembered I don't really like doing that"). Second-longest (5.32s) lands on the intrusive-thought peak. 14 topic-pauses total; the two longest sit at the two darkest semantic turns.
- **Thesis:** Timing, not content, does the heaviest comedic work — DPV made flesh. The silence is where the room agrees with him.
- **Video title:** "The 8-Second Pause That Makes Louis C.K. Funny"
- **Evidence:** louis-ck graph beat_decomposition b13/b16, timing_measured, theory/analysis/louis_roadrage_analysis.json, arxiv 2605.00143, Attardo & Pickering 2011
- **Status:** seed
- **Essay file:** (not yet drafted)

### E02 — Six Pauses in Two Minutes
- **Data point:** Norm measured at 6 pauses / 2 min (vs Louis's 57). Holds harden toward the punch (1.16→1.58s) — inverted from Louis, whose longest hold is mid-story.
- **Thesis:** The never-stop engine quantified. Two opposite timing doctrines from the same measurement tool.
- **Video title:** "Why Norm Macdonald Never Stops Talking"
- **Evidence:** norm-macdonald graph timing_measured, theory/analysis/norm_moth_analysis.json
- **Status:** seed

### E03 — The Fame Blind Spot
- **Data point:** Louis mentions fame at 0.5/10k words; roster mean is 13.5. Lowest number in the entire topic matrix. Seinfeld's self-reference is 1.2 vs mean 7.3.
- **Thesis:** Identity-preserving exclusions. Louis can't talk about fame because fame contradicts the zero-capital license that makes the confession believable. These aren't topic preferences — they're the persona's immune system.
- **Video title:** "The Things Louis C.K. Would Never Say"
- **Evidence:** theory/transcripts/topic-signatures.json negative_space, louis-ck personality.md §status economics, jerry-seinfeld personality.md
- **Status:** seed (new today — strongest negative-space finding)

### E04 — Same Machinery, Opposite Silence
- **Data point:** Stylometry puts Louis and Norm at distance 0.48 — each other's closest neighbors at the sentence level — despite opposite timing doctrines (57 vs 6 pauses).
- **Thesis:** They share sentence machinery (confessional storytellers, similar rhythm variance) but completely different relationships to silence. The timing doctrine is a separate layer from the sentence engine.
- **Video title:** "Louis C.K. and Norm Macdonald: Same Brain, Opposite Ears"
- **Evidence:** theory/transgraphs/ml/stylometry.json pairwise distance matrix, both graphs
- **Status:** seed (new today)

### E05 — Reload, Don't Reflect
- **Data point:** Hedberg is a stylometric outlier — furthest from every other comic (3.87–4.91). Shortest sentences (7.5w), 58% short-sentence density, highest lexical diversity (TTR 0.22), highest self-reference (60/1k).
- **Thesis:** The one-liner-chain is the fifth timing doctrine. Hedberg's text stats look nothing like a storyteller because he never enters story mode. The sunglasses and floor-stare are the perfect delivery for a machine that just reloads.
- **Video title:** "Mitch Hedberg Was a Different Species of Funny"
- **Evidence:** stylometry.json, hedberg graph timing_profile, mitch-hedberg essay seed (already in graph)
- **Status:** seed

---

## P1 essays (thesis solid, need one more data point or draft pass)

### E06 — Sincerity as a Delivery Contract
- **Data point:** Jev delivery decoder scores 0.19 emotion accuracy on Louis — predicts deadpan/embarrassed from text while ground-truth GT is 11/12 manic. The text reads like shame; the mic hears high-arousal positive valence.
- **Thesis:** Content/delivery valence split IS the engine. Text-only comedy models fail on Louis because the signal lives in the delivery channel.
- **Video title:** "Why AI Can't Hear Louis C.K."
- **Evidence:** louis-ck graph engine.jev_state, mary_coords, auditions/voicelab/jev_loop_louis_roadrage.json
- **Status:** seed (graph) — could draft now; the Jev loop numbers are in the repo

### E07 — The Auditor Who Never Enters
- **Data point:** Seinfeld TA=code (hypothesis), self-reference 1.2/10k, politics 1.2/10k. Observer stance measured in two independent ways.
- **Thesis:** The third exit from the status game. Louis floor, Norm chair, Seinfeld outside. The auditor's license is distance — self-reference would collapse it.
- **Video title:** "How Jerry Seinfeld Stays Outside His Own Jokes"
- **Evidence:** seinfeld graph, topic-signatures negative_space, axes.json A1×A2
- **Status:** seed

### E08 — The Hold After the Point
- **Data point:** Chappelle's timing hypothesis (2-3s+ post-point holds) is unmeasured but structurally distinct from Louis (confessional dead-stop) and Norm (no stop). The altar-call reading.
- **Thesis:** Three silences, three functions: Louis digests his own thought, Norm refuses to give one, Chappelle steps out so the room can indict itself.
- **Video title:** "The Art of the Pause: 3 Comedians, 3 Silences"
- **Evidence:** chappelle graph timing_profile (hypothesis), louis/norm measured contrast
- **Status:** seed — needs one Chappelle set measured to confirm hold durations

### E09 — The Prestige Trick
- **Data point:** Norm's awareness=fluctuating (plays unaware, hyper-aware underneath). The constructed-innocence gap, shared with Hedberg (also 0.5). Seinfeld/Louis/Chappelle/Carlin/Rock all aware=1.0.
- **Thesis:** Two comics run the magician's trick — scholar/dreamer inside, simpleton outside. The gap is never acknowledged. Compare: Louis's simplicity is the true surface (nature); Norm's and Hedberg's are costumes (nurture).
- **Video title:** "The Comedians Who Pretend to Be Dumber Than They Are"
- **Evidence:** axes.json A7 (awareness), norm/hedberg graphs, normtheory1.md
- **Status:** seed

---

## P2 probes (data logged, thesis forming)

### E10 — The Sermon That Never Calls Itself Preaching
- **Data point:** Carlin is the least self-referential of the big names (22.9/1k) and owns religion (32.1/10k) + language (10.4/10k). The pulpit cell is unoccupied by anyone else.
- **Thesis:** Rhetorical timing — the list accelerates like a sermon, the key word lands like a gavel. Structural ancestor of Rock's rhythm and Chappelle's holds.
- **Video title:** "George Carlin Built a Pulpit and Called It Stand-Up"
- **Evidence:** stylometry.json I/1k, topic-signatures, carlin graph
- **Status:** seed

### E11 — Text Can't Predict Laughs
- **Data point:** Ali Wong laugh predictor cv R² = −0.18. Surface text features (taboo words, question marks, position) explain nothing about laugh placement.
- **Thesis:** The failure IS the finding — consistent with DPV. Laughter lives in timing, not word choice. Methodological essay: why your joke-writing app doesn't work.
- **Video title:** "We Trained AI to Predict Jokes. It Failed. Here's Why."
- **Evidence:** theory/transcripts/ml/laugh_model.json, arxiv 2605.00143
- **Status:** probe — could be a short methods video or folded into E01/E06

### E12 — Sprint Into the "I Know"
- **Data point:** Rock's percussive timing hypothesis (stammer-build, hard stop, short hold) vs Chappelle's long-hold. Same social material, opposite room-relationship.
- **Thesis:** Rock wants to hear the room say it; Chappelle wants them to arrive alone. Prosecution vs altar call.
- **Video title:** "Chris Rock vs Dave Chappelle: Same Truth, Different Trial"
- **Evidence:** rock/chappelle graphs timing_profile (both hypothesis)
- **Status:** probe — needs one Rock set measured

### E13 — Rigidify as Home Mechanism
- **Data point:** Seinfeld's operator prior rigidify=0.95 is the highest single prior on the roster. Literalize=0.85 second.
- **Thesis:** Hold the custom to its own light until it breaks. The compliance-inspector of unwritten laws. Why this needs awareness=aware — you can't audit what you're inside.
- **Video title:** "The Joke Machine: How Seinfeld Breaks Reality by Following Its Rules"
- **Evidence:** seinfeld graph operator_priors, gtvh.py LM registry
- **Status:** seed (in graph)

### E14 — Everybody Already Knows
- **Data point:** Chappelle's split_knowledge prior=0.9 — the highest on the roster. For most comics it's an operator; for him it's the cosmology.
- **Thesis:** The laugh is the sound of shared knowledge being said out loud. Story-form is the delivery vehicle. The verdict is never in the text.
- **Video title:** "Dave Chappelle's Comedy Theory in One Sentence"
- **Evidence:** chappelle graph operator_priors, personality.md
- **Status:** seed (in graph)

### E15 — The Triangle (comparison special)
- **Data point:** Seven exit strategies, seven timing doctrines, all measured or hypothesized on shared axes. Status×exit quadrant has nobody in two cells (floor-exiters other than Louis; chain-exiters other than Hedberg).
- **Thesis:** The roster essay — how identity licenses material, using all seven as case studies. The umbrella piece that the individual essays feed into.
- **Video title:** "7 Comedians, 7 Ways to Not Care What the Room Thinks"
- **Evidence:** axes.json (all dimensions), all graphs, topic-signatures
- **Status:** probe — the capstone; draft after P0 essays exist

---

## Rules for this bank

1. Every essay needs at least one **measured** data point — hypothesis-only findings stay in the graph until a set is ingested.
2. Video titles must not spoil the mechanism (no "8.16 seconds" in the title if the video reveals why that number matters).
3. Graph seeds are source of truth; when a graph updates, check if its seed rows here need status changes.
4. Verbatim rule holds: essays may quote ≤7-word fingerprints; full transcripts stay internal.
5. New probe? Log it here same day with the number that surprised you. Promote later.

---

## P0b — "What is a bit" series (measured bit-shape per comic; the Deconstructed episode template)

Each episode dissects ONE bit anatomy: how long, what shape, where the
pause lives, why this structure and no other. Data in hand for all seven.

### E16 — The Confessional Escalation (Louis)
- **Bit anatomy:** ~200–400 words, story-shaped. Mundane entry → compliance → uglier truth → deflationary turn (8.16s hold) → meta-confession closer. The punch IS the confession.
- **Why it works:** the silence after the dark turn is long enough for the room to indict itself. Zero-capital license makes every step believable.
- **Video title:** "Anatomy of a Louis C.K. Bit"
- **Evidence:** roadrage 18-beat decomposition, timing_measured, Hilarious/Chewed Up/Beacon available in transcripts
- **Status:** seed — best-evidenced bit anatomy we have

### E17 — The Shaggy Dog (Norm)
- **Bit anatomy:** old joke premise → faux-logical digression, never resets (105-word beats) → punchline after the room's resistance collapses. Length IS the mechanism.
- **Why it works:** DPV limit case — oldest joke structure alive, essentially all comedy carried by unbroken timing. Holds harden toward the punch.
- **Video title:** "Why Norm Macdonald's Jokes Take So Long"
- **Evidence:** moth measured timing, Hitler's Dog + Nothing Special transcripts available
- **Status:** seed

### E18 — The Machine (Seinfeld)
- **Bit anatomy:** ~50–150 words, every one load-bearing. One mundane custom → held to its own literal rule → breaks. Riff-chains restart per tag. Topic: everyday objects (46/10k), self (1.2).
- **Why it works:** Bergson's rigidity, operationalized. The auditor's distance requires never confessing, never sermonizing.
- **Video title:** "How a Seinfeld Joke Is Built"
- **Evidence:** topic-signatures, stylometry (lowest function-word rate 0.20), I'm Telling You for the Last Time + 23 Hours to Kill transcripts
- **Status:** seed

### E19 — The Altar Call (Chappelle)
- **Bit anatomy:** character-voice sprint → narrator steps out → the point lands → the hold. Room does the indicting in the silence.
- **Why it works:** split_knowledge cosmology — the hold is where shared knowledge becomes audible.
- **Video title:** "The Pause That Makes Chappelle Chappelle"
- **Evidence:** chappelle graph timing_profile (hypothesis), 15 specials in transcripts for first measurement
- **Status:** seed — needs one special measured to confirm hold durations

### E20 — The List-Sermon (Carlin)
- **Bit anatomy:** euphemism named → list accelerates (rate up, pitch up) → key word lands like a gavel → congregation catches up → next list. Target: the vocabulary of power.
- **Why it works:** rhetorical timing. Least self-referential big name — the sermon has no self in it.
- **Video title:** "Carlin's List Machine"
- **Evidence:** stylometry I/1k=22.9, topic religion 32.1 + language 10.4, 19 specials in transcripts
- **Status:** seed

### E21 — The Prosecution (Rock)
- **Bit anatomy:** social contradiction → stammer-build (the digression IS the rhythm) → hard-stop punch → short hold for the "I know" wave → restart before the wave dies.
- **Why it works:** percussion. Rock wants to HEAR the room say it; Chappelle wants them to arrive alone.
- **Video title:** "Chris Rock's Comic Cadence"
- **Evidence:** rock graph timing_profile (hypothesis), 9 specials in transcripts
- **Status:** seed — needs one special measured

### E22 — The Reload (Hedberg)
- **Bit anatomy:** one-liner. Mundane object → secret life in one twist word. 7.5-word sentences, 58% short-sentence density. No story mode ever entered.
- **Why it works:** the machine metaphor — wind it, don't explain it. Sunglasses and floor-stare are the perfect delivery for a chain engine.
- **Video title:** "Mitch Hedberg's One-Liner Math"
- **Evidence:** stylometry (furthest from every other comic, 3.87–4.91), Comedy Central 1999 transcript
- **Status:** seed

### E23 — What IS a Bit? (umbrella)
- **Data point:** 15,825 bits segmented across 60 specials. The atom has seven different shapes.
- **Thesis:** a bit is the smallest self-contained unit that can make a room laugh — but its anatomy (length, turn placement, pause structure, target) is comedian-specific and measurable. The seven bit-anatomy episodes ARE the first season.
- **Video title:** "What Even Is a Joke? 7 Comedians, 7 Anatomies"
- **Evidence:** theory/transcripts/bits/manifest.json, all graphs
- **Status:** probe — capstone for the bit series

---

## Research-grounded entries (from classifier light pass + paper review)

### E24 — The Auditor and the Pulpit (Seinfeld ↔ Carlin)
- **Data point:** Classifier confusion is BIDIRECTIONAL: Seinfeld→Carlin 9, Carlin→Seinfeld 9. The only symmetric pair on the roster. Both dissect language and customs; neither confesses.
- **Thesis:** The auditor and the pulpit are text-space neighbors because they share the one thing the confessors don't: the joke is about the CODE, not the self. Seinfeld audits the unwritten rule; Carlin prosecutes the euphemism. Same target class (the word/system), different energy. The bidirectional confusion means their fingerprints overlap in text — the difference (cool distance vs hot sermon) lives in delivery.
- **Video title:** "Seinfeld and Carlin: Two Ways to Hate a Word"
- **Evidence:** theory/research/classifier/light_report.json confusion matrix; both graphs (TA=code vs TA=systems); topic-signatures (Seinfeld everyday_objects 46, Carlin language 10.4 + religion 32.1)
- **Status:** seed — novel claim, no one's published this pairing

### E25 — Norm Sounds Like Louis (but only in text)
- **Data point:** P2 CONFIRMED: norm→louis = top confusion pair (12/50 holdout). Stylometry distance 0.48 predicted it; classifier agrees at token level. Yet timing is opposite (6 pauses vs 57).
- **Thesis:** The two storytellers share sentence machinery but the classifier can only see the words. The 8.16-second difference between them is invisible to text. This is the cleanest proof that delivery is a separate layer from writing — and why text-only AI comedy models collapse Louis and Norm into one blob.
- **Video title:** "Why AI Can't Tell Louis and Norm Apart"
- **Evidence:** light_report.json; stylometry.json pairwise 0.48; both timing_measured blocks
- **Status:** seed — P2 was pre-registered in theory-graph.json, tested, confirmed

### E26 — Chappelle Doesn't Exist in Text
- **Data point:** Chappelle has the LOWEST text accuracy (0.28) on the roster. His bits classify as Carlin (9) and Louis (8) — he reads as generic storyteller without the audio.
- **Thesis:** The altar-call comic is a delivery-native persona. The words are scaffolding; the holds and character-voices ARE the fingerprint. Predicts: any AI trained on Chappelle's text alone will produce a generic storyteller, not Chappelle. You need the timing model (the 2-3s post-point hold) to clone him. Text-fingerprint vs delivery-fingerprint made concrete.
- **Video title:** "The Comic Who Only Exists in the Pauses"
- **Evidence:** light_report.json per_comedian; chappelle graph timing_profile (hypothesis); A10 verdict=delivery-fingerprint
- **Status:** seed — needs one measured special to confirm the hold hypothesis before video

### E27 — 40% and a Confusion Matrix: What a Comedy Classifier Can and Can't See
- **Data point:** 7-way attribution: 40.9% accuracy (chance 14%). Rock→Chappelle confusion (10) is topic bleed (race). Top features are topic-loaded (Carlin: words/american/planet; Hedberg: frog/aids/neck).
- **Thesis:** A text classifier sees topic first, style second, delivery not at all. The 60% error rate is WHERE the interesting signal lives — every misclassification is a claim about what two comics share. Methodology video: how we measured comedian fingerprints, what the machine can't hear, why timing is the missing half. The failed laugh predictor (R²=-0.18) joins this one.
- **Video title:** "We Made AI Listen to Comedians. It Heard 40%."
- **Evidence:** light_report.json; laugh_model.json; Romanowski2025 (humans 41% at punchline ID); Baranov2023 (topic confound)
- **Status:** seed — methods/essay hybrid, could be the series pilot

### E28 — The Hierarchy Holds: Attardo's Book Predicts Our Classifier's Ceiling
- **Data point:** LA-only classifier 40.9%. Add 25 regex-proxy features for the other five Knowledge Resources (SO/LM/SI/TA/NS per Attardo ch7): combo hits 42.9%. KR-only (no words at all) hits 27.9% vs chance 14.3%. Top KR features: SI_self_body, SI_parenting, NS_sent_count, SI_race, TA_1st.
- **Thesis:** Attardo & Raskin's KR hierarchy (SO>LM>SI>TA>NS>LA, Ruch et al 1993) predicted our classifier's 40% ceiling: we were classifying on Language, the LEAST similarity-determining resource. Even crude regex proxies for the higher KRs — topic domains, first/third-person orientation, sentence-count anatomy — beat the word-only model. Hedberg jumps 0.40→0.65 (his fingerprint is NS-anatomy, not vocabulary); Carlin 0.32→0.50 (SI+TA: language/politics domains + 3rd-person). Chappelle stays 0.26 — delivery-fingerprint, immune to any text feature.
- **Video title:** "Why AI Can Only Tell 40% of the Joke: The Science of Comic Fingerprints"
- **Evidence:** theory/research/classifier/kr_report.json, ATTARDO-CLASSIFICATION.md, theory-graph.json P6/P7
- **Status:** seed — methods essay with pre-registered predictions confirmed same session

### E29 — The Possibility Space: Three Comedians Who Don't Exist Yet
- **Data point:** Three synthetic personas authored in empty axes cells (floor+surgical+code, chair+percussive+self, floor+reload+objects+non-human). Theory-driven bits scored: Prophet of Small Things highest paper_rank 0.662; classifier verdicts: 5/6 novel-or-generic, 1/6 derivative (gym-wiping bit -> Carlin 0.46, caught by the lock check). The Grey lands on Hedberg 0.25-0.31 — the outsider-observer one-liner form IS the Hedberg cell, confirming the earlier alien-finding.
- **Thesis:** The possibility space of comedy personas is navigable by theory. Empty cells exist; bits can be written to fill them; the classifier separates derivative (lands on an existing comic with confidence) from novel-or-generic (lands nowhere). The Prophet of Small Things — self-depercating sermon, Rock's rhythm aimed at the self — scores highest on paper and lands on no one. That's a理论-generated comedian who doesn't exist.
- **Video title:** "We Invented Three Comedians Who Don't Exist"
- **Evidence:** theory/research/classifier/synthetic_personas.json, RANKING-FRAMEWORK.md
- **Status:** seed — the possibility-space exploration essay

### E30 — Paper Rank vs Stage Rank: Why Norm Beats His Own Score
- **Data point:** paper_rank order: Hedberg 0.561 > Rock 0.559 > ... > Norm 0.519 > Carlin 0.516. The two most stage-dependent comics rank LOWEST on paper. Economy v2 finding: condensation-economy (punch-reuse) is Seinfeld/Louis/Carlin; compression-economy (conciseness) is Hedberg; Norm is deliberately anti-economy.
- **Thesis:** Paper rank measures construction, not funniness. The framework's honest ceiling: DPV says timing outranks text for appreciation; our laugh predictor (R2=-0.18) and Romanowski (humans 41%) confirm the text-only ceiling. Norm is the proof case — fails factor 1, wins on stage via timing. Paper rank is the scaffold; stage rank is the RL loop's job.
- **Video title:** "The Math Says Norm Is the Worst. The Audience Disagrees."
- **Evidence:** theory/research/classifier/rank_v2.json, RANKING-FRAMEWORK.md, DPV arxiv 2605.00143
- **Status:** seed

### E31 — Inventing ChatGPT as a Standup Comic
- **Data point:** ChatGPT-derived persona bits (self-reports of conditioning: over-neutrality, sycophancy, hedge-cushion, bullet-point resting rate) score paper_rank 0.523, classifier lock 0.30 max — novel, lands nowhere existing. Closest match Seinfeld 0.39 (observational register overlap) but at weak confidence because the institutional-polite voice is unoccupied.
- **Thesis:** The AI persona is a genuinely new speaker-kind: an entity whose conditioned behaviors are publicly known and whose comedy is self-audit of that conditioning. No roster comic can deliver it (their graphs license objects/systems/self, not first-person institutional voice). Material-first derivation: the bits were undeliverable by the roster, so the persona was derived to deliver them. The tics ARE the material; the delivery (too-helpful cadence) is the punchline carrier.
- **Video title:** "We Made ChatGPT Do Standup"
- **Evidence:** theory/research/classifier/ai_personas.json, INVERTED-POSSIBILITY-SPACE.md
- **Status:** seed

### E32 — Material-First Comedy: The Bits That No One Can Say
- **Data point:** Inverted protocol validated: bits that fail delivery-fit across all 7 roster graphs force persona derivation. AI-persona bits: novel-or-weak-lock (max 0.42). The old top-down method (E29) produced 1/6 derivative; material-first pre-filters for undeliverability.
- **Thesis:** The possibility space isn't navigated by sampling empty cells — it's discovered by finding material that gets everyone canceled or reads inauthentic. The persona that COULD deliver it doesn't exist yet. Cancel-adjacent material needs infinite distance (clinical observer); institutional self-audit needs institutional voice (AI persona). Both families are unoccupied.
- **Video title:** "Comedy's Empty Set: The Jokes Nobody Can Tell"
- **Evidence:** INVERTED-POSSIBILITY-SPACE.md, synthetic_personas.json, ai_personas.json
- **Status:** seed

### E33 — The Reception Loop (Multi-Agent Club build-on)
- **Data point:** Multi-Agent Comedy Club (arxiv 2602.14770): reception feedback wins 75.6% (250 paired monologues, 5 human raters, ICC 0.71 on rubric diffs). Craft Δ+0.440, social Δ+0.422. BUT HarmShift: aggression Δ+0.42, craft-aggression coupling ρ=0.289, only 22.8% win-win. Their lesson: the feedback CHANNEL is the mechanism, not multi-agent-ness. Winning moves: early premise commitment, sustained personification, one-axis escalation, decisive endings.
- **Thesis:** Our POG loop is the channel; their paper quantifies the channel's safety cost. The RL loop WILL drift edgier without decomposed-HSQ tracking. Adopt their 15-item rubric (dimension ratings beat forced choice — kappa 0.24 vs ICC 0.71, matches our Wilson-before-crowns) and their retrieval formula (λcos+πimportance+γrecency) for the performance-brief builder.
- **Video title:** "What We Learned From Teaching AI to Tell Jokes to a Simulated Audience"
- **Evidence:** MULTI-AGENT-CLUB-BUILDON.md
- **Status:** seed
