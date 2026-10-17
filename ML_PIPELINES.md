# ML Pipelines — funnygraph

> What we can compute, ordered by what runs now vs what needs more data.
> Data inventory (2026-10-17): 181 graphs · 78 known_bits · 225 specials_rated ·
> 91 bios · 167 generations · 84 recognition · 451 sets · 21M transcript words.

## Runs now

### 1. The comedy latent space
TF-IDF + SVD on deals + misinterpretation rules + threads → every comic a vector.
Outputs: nearest neighbors ("the modern Pryor is ___"), generation clusters,
scene separation. Answers "who's the X of Y?" with math. Feeds the recommender free.

### 2. What predicts a breakout special?
Regression: operator_priors + generation + vote base + transcript features
(profanity rate, question rate, vocab diversity) → IMDb rating.
Output: feature importances — timing, topic, or generation? Cross-validated.

### 3. Rise/fall modeling
CC2004 → RS2017 → IMDb now. Who rose (Louis 97→4), who fell, who's stable?
Classify trajectory from graph features.
Output: the canonization curve — what gets a comic INTO the canon 13 years later?

### 4. Voice fingerprints
Stylometry per comic: distinctive n-grams, profanity rate, sentence length,
question rate, "I" rate, list usage.
Output: measurable "this sounds like X" score for new material — feeds the
agent harness as a judge.

### 5. Theory validation (the honesty loop)
Do authored `operator_priors` correlate with measured transcript features?
(High-rigidify comics actually use more literal constructions?)
Output: proves or kills our own theory.

### 6. Generation gap analysis
Do generations measurably differ? Profanity by decade, topic drift
(airplanes → phones → AI), special length, rating distributions.
Output: "comedy got ___er over 50 years" with numbers.

## Needs more data

### 7. Timing → rating
Pause structure vs IMDb. Only 4 measured sets now; harvest 20+ word-timed
sets first (whisper on clips). Highest-value pipeline — DPV claim at scale.

### 8. Influence graph
Who cites whom (thread overlap + explicit mentions: "like Pryor said…") →
directed influence network. Needs mention-mining pass over transcripts.

### 9. Breakout prediction
Early signals before the big special (podcast frequency, KT appearances,
opener slots). Needs external timeline data. Hardest, most valuable.

### 10. Special recommender
"If you like Tennessee Kid, try ___" from latent space + ratings.
Trivial once #1 exists — free win.

## Recommended order
**1 + 4 + 2** now (one script): latent space, fingerprints, ratings regression.
Then **5** as the honesty check. Then **7** once word-timed sets scale.

## Rankings (separate problem — see RANKINGS.md)
Definitive comedian rankings from critics data: theory, prior art, and our
rank-aggregation design. Not an ML pipeline — a measurement problem.
