# Measuring the Unmeasurable: Principled Consensus Ranking and Auditable Multi-Lens Metrics for Stand-Up Comedy

**The funnygraph project · working manuscript v0.2 · 2026-10-17 · DRAFT — not submitted to any venue.**

> Every number in this paper is recomputed from public code and data
> (funnygraph repository: rank_comedians.py, metrics.py, kendall_w.py,
> stability.py, mallows_phi.py, bt_leg.py, split_boards.py, fit_weights.py,
> ml_analysis.py). Where the manuscript simplifies, the code governs; known
> divergences are listed in Appendix C, not hidden.

---

## Abstract

"Who's the greatest stand-up of all time?" is among the most argued
questions in popular culture and the least measured. Existing answers are
single snapshots (Comedy Central 100, 2004; Rolling Stone 50, 2017),
popularity contests without methodology (Ranker), or per-special audience
scores (IMDb) that never aggregate to the comedian level. We build the
first principled alternative: a consensus ranking of 178 comedians from
three voter legs (critics' lists, IMDb audience ratings with
corpus-calibrated shrinkage, prestige-weighted awards), aggregated by
Borda count with local Kemenization, era-normalized by within-generation
median z-scores, and published with per-position stability intervals —
alongside five auditable lenses (Legacy, Audience, Popularity, Heat,
Theory) whose gaps are themselves the product.

Methodological contributions: (1) a postdate-aware extension of Dwork's
partial-list rule, stated with its exact operational scope; (2) fitted
rather than asserted leg weights — Mallows dispersion per leg implies
precision weights; the hide-one-list experiment is fragile across runs
(weak signal — see GAPS.md Runs A+B), so CANON and PEOPLE'S CHOICE ship
as separate elections on pairwise-tau evidence instead; (3) rank-breaking
Bradley-Terry on list-implied pairs validates Borda as the aggregator
(τ ≈ +0.64–0.88 as lists grow 2→4); (4) inter-leg concordance analysis shows the legs barely
agree (τ(critics,audience) ≈ −0.04–+0.20 across runs; Kendall's W = 0.59, p = 0.04 over
full-coverage comics) — formal license for the split; (5) 71-regime
stability analysis finds only a minority of positions stable (12/295 latest), and we publish all
intervals. A direct M5-redo (authored vs measured priors, +.18, up from
−.05 via text proxies) is reported alongside the failed proxy test, not
buried; (7) the house election uses first-party signals only — external
judgments display as labeled reference, never inputs — with Norm
Macdonald #1 on owned evidence. All inputs, weights, code,
disagreements, and exclusions are public.

---

## 1. Introduction

Comedy has no Rotten Tomatoes. Film has a durable design pattern: two
scores, same methodology for every title, critics beside audiences, and
the gap between them as content ("critics hated it, audiences loved it" is
a headline genre). Stand-up comedy — a century-old art form with a
multi-billion-dollar live and streaming economy — has nothing comparable.
Its canon is set by two frozen listicles, its audience scores never leave
the special level, and its crowd-vote leaderboards are unaudited.

This paper builds the missing instrument: a consensus ranking with honest
uncertainty, plus five named lenses with published formulas. Our thesis
has three parts. First, **no single number is defensible** (Arrow 1951) —
so we publish elections, plural, with disagreement as a first-class
output. Second, **critics and audiences hold different elections** — and
we prove it three ways (prediction experiment, concordance analysis,
stability analysis) rather than asserting it. Third, **a ranking that
hides its gaps is a listicle** — so missing-data rules, coverage badges,
failed tests, and a secret-free exclusion log are part of the method, not
the appendix.

## 2. Related work

### 2.1 Computational humor: detection without ranking

The field works on detection, never cross-performer ranking. SCRIPTS
(LREC 2022: 90 scripts across 68 comics, laugh-marker classification)
and StandUp4AI (EMNLP 2025: 3,617 videos with laughter labels) predict
*where* laughs occur; Open Mic scores clip funniness; recent CMCL-2025
work benchmarks LLM humor detection. Special-level linguistic prediction
of IMDb ratings exists (LIWC-style feature studies). None aggregates to
the comedian level, none compares performers, none states era-adjusted
uncertainty. That empty cell is this paper.

### 2.2 Performer psychology

Greengross, Martin & Miller (2012) find professional success predicted
positively by affiliative humor and negatively by self-defeating humor
(n=31 comics). This is the closest thing to a construct-validity anchor
for comedy metrics — and we test our authored operator priors against it
at scale (§6.4). The test fails. We keep the anchor and report the miss:
a metric paper that only passes its tests is advertising.

### 2.3 Cross-era comparison

The problem — newer entrants have more measured output, older entrants
have canonization and survivorship — is solved furthest in sports
statistics (Berry, Reese & Larkey 1999, bridging eras in JASA) and music
chart analysis (era baselines; rank-turbulence divergence, Dodds et al.
2020, EPJ Data Science). We port within-cohort normalization to comedy
(§4.8), replacing era dummies with median z-scores and a stated
small-group fallback.

### 2.4 Rank aggregation and social choice

Kemeny optimal aggregation — the ranking minimizing total Kendall-tau
distance to all input votes — is the maximum-likelihood estimator under
the Mallows (1957) noise model, and it is NP-hard (Bartholdi, Tovey &
Trick 1989). The practical recipe is Dwork, Kumar, Naor & Sivakumar
(2001): start from Borda (a 5-approximation to the Kemeny optimum, at
O(n log n)), hill-climb with local Kemenization. Dwork et al. also supply
the partial-list rule (unranked items sit below ranked ones), which we
extend (§4.7). Pairwise data belongs to Bradley & Terry (1952), estimated
by the MM algorithm of Hunter (2004) originating with Zermelo (1929);
lists imply pairs via rank-breaking (Khetan & Oh 2016). Dispersion per
voter is a Mallows φ fit (repeated-insertion representation; Fligner &
Verducci 1986). Concordance across judges is Kendall's W (Kendall &
Babington Smith 1939); pairwise agreement is Kendall's τ-b (Kendall
1938). Shrinkage of low-sample estimates toward a prior mean is empirical
Bayes in the James–Stein (1961) tradition; the IMDb Top-250 formula is its
industry incarnation. Pairwise-rating dynamics (Elo 1978; Glickman 1999;
TrueSkill, Herbrich, Minka & Graepel 2007), spectral ranking
(RankCentrality, Negahban, Oh & Shah 2014), and inconsistency-cycle
analysis (HodgeRank, Jiang, Lim, Yao & Ye 2011) are reserved for the arena
leg (§4.5) once pairwise votes exist at scale.

### 2.5 Industry systems: steal-list

IMDb Top-250: WR shrinkage — steal the formula shape, recalibrate the
prior to specials (§4.3). Rotten Tomatoes: two scores side by side plus
the gap as content — steal the display model, replace binary fresh/rotten
with cardinal ratings (richer) while noting our "critics" are two
listicles, not hundreds of reviews. Metacritic: undisclosed weights —
the negative example; we publish ours. Letterboxd: community trust at
scale substitutes for methodology — unavailable to us; auditability is our
substitute.

### 2.6 Humor theory: from philosophy to measurable features

Our graphs tag every comedian with theory-derived constructs
(operator_priors, misinterpretation_rule, timing_doctrine, taboo, GTVH
profile). This section grounds each construct in the literature it comes
from — so the Theory lens (§4.11) is applied science, not vibes. Anchor
for the classical terrain: Morreall's "Philosophy of Humor" (Stanford
Encyclopedia, Fall 2024 archive), supplemented by the IEP "Humor" article.

**2.6.1 The classical triad — and why we use all three.** *Superiority*
(Plato through Hobbes's "sudden glory arising from some sudden conception
of some eminency in ourselves," Human Nature ch. 8; modern form: Scruton's
"attentive demolition") covers roast, insult, and status play — but cannot
cover puns (Morreall). *Relief* (Shaftesbury 1709, Spencer 1860, Freud
1905/1927) is hydraulics Morreall calls scientifically obsolete — but its
structural core survives: tension accumulates, discharge releases. That
structure IS setup→punch dynamics, and it is empirically alive: THInC's
theory-driven ensemble (De Marez 2024, arXiv:2409.01232, F1 0.85) assigns
its relief proxy the highest weight (1.591) of any theory classifier.
*Incongruity* (Beattie 1779, first philosophical use of "incongruous";
Kant 1790, strained expectation into nothing; Schopenhauer 1844,
concept-vs-perception mismatch) is now the dominant theory — but
necessary, not sufficient. Beattie himself warned that incongruity
attended by "some other emotion of greater authority" (fear, disgust,
disapprobation) does not amuse; Clark's three conditions (perceive,
enjoy perceiving, enjoy the incongruity for itself) and Morreall's
non-humorous incongruity-enjoyment (grotesque, macabre, bizarre) say the
same. Modern form: two-stage incongruity-resolution (Suls 1972; IR
variants), sharpened computationally by Ritchie's surprise-disambiguation
model (1999) and belief-revision formalizations (Dupin de Saint-Cyr &
Prade, arXiv:2309.02009; Ritchie 2002, AGM-style punchline revision).
The IEP's caution stands: Monro's rival-framing misleads — the schools
answer different questions (function vs object vs response). Our graphs
respect the split: taboo/line constraints (function), operator priors
(object mechanisms), timing doctrine (response dynamics).

**2.6.2 Bergson: rigidity is the comic.** Bergson (1900, Le Rire):
"something mechanical encrusted upon the living" (du mécanique plaqué sur
du vivant); laughter as social gesture correcting inelasticity of
character, mind, and body; comic absurdity as dream-logic; and crucially,
comedy portrays TYPES not individuals — the charter for character-driven
stand-up analysis (Prusak 2004 rereading; Watson 2022 on rigidity and
intelligence; Ford 2018; Sinclair 2019). Bergson maps directly onto our
constructs: *rigidify* (applying dumb logic as law) is the mechanical-
encrusted-on-living operator; *character_violation* and *status_invert*
are its social forms; our type/mode system (dark-confessional, rant,
absurdist…) is Bergsonian typing made explicit and measurable.

**2.6.3 Freud: joke-work as mechanism inventory.** Freud (1905, Jokes and
Their Relation to the Unconscious): condensation and displacement as
joke-work (ancestors of our double_interpret and split_knowledge
operators); tendentious vs innocent jokes (the charter for our taboo
field and the dark board — tendentiousness is measurable as taboo-
proximity); economy of psychic expenditure (the charter for SCULPT/
compression: shorter is funnier when nothing is lost). We adopt the
mechanisms, not the metapsychology — same stance as Morreall on relief.

**2.6.4 Linguistics: scripts, resources, and resolution.** SSTH (Raskin
1985): humor = script opposition simultaneously activated. GTVH (Attardo
& Raskin 1991; surveyed in Attardo 1994, Linguistic Theories of Humor;
handbooked in Raskin 2008, Primer of Humor Research): six Knowledge
Resources — Script Opposition, Logical Mechanism, Situation, Target,
Narrative Strategy, Language. Our graph fields approximate five of the
six (table below; Language arrives via style fingerprints, M4). Status,
honestly: scaffolded, not filled — 32 graphs carry the GTVH shell, most
with empty slots. Filling SO/LM per comic from measured bits is
scheduled work, and the shell's existence is what makes it schedulable.
Ritchie's IR/SD gives us the bit schema itself: setup builds the
expected script, punch forces revision, tag re-applies the mechanism.
Martin's four humor styles (Martin et al. 2003: affiliative,
self-enhancing, aggressive, self-deprecating; textbook: Martin & Ford
2018) give the affiliative↔aggressive axis our mode system assumes but
has not yet scored per comic (scheduled).

**2.6.5 Modern synthesis and computational precedent.** Benign violation
(McGraw & Warren 2010, Psych. Science 21(8): three benign conditions —
alternative norm, weak commitment, psychological distance — five studies)
is the leading necessary-and-sufficient candidate and the direct parent
of our taboo-plus-distance analysis (COUNTRY_THEORY.md's taboo/censorship
variables are BV conditions per culture). Theory now predicts from text:
THInC (F1 0.85, interpretable per-theory weights); HUMORCHAIN (2026,
arXiv:2511.21732: four classical theories cover 86% of 100 humor samples
— universality quantified); Li's dual-process synthesis (2016:
surprise→reflection→dismissal→compensation, subsuming all three schools).
Two warnings from the frontier shape our honesty constraints: the LLM
log-likelihood objective works AGAINST incongruity (survey
arXiv:2509.21175, citing Loakman et al. 2025a) — fluent models smooth
away the violation our metrics must preserve; and frontier models score
≤51% at punchline identification vs 41% for humans (Romanowski et al.
2025, arXiv:2504.09049) — humor perception is hard for machines AND
people, which bounds what any metric can claim. Offense-entanglement
("This joke is [MASK]", arXiv:2210.13985: humor classifiers lean on
offensive features via influence functions) is why our taboo field and
exclusion log are load-bearing ethics infrastructure, not garnish.
Laughter-ground-truth precedent: Open Mic humour quotient from laughter
duration (Mittal et al. 2021, arXiv:2110.12765, QWK 0.6/0.813);
StandUp4AI multilingual word-level laughter labeling (arXiv:2505.18903);
multimodal laughter detection (Kuznetsova & Strapparava 2024).

**2.6.6 Theory → construct → proxy map (what our graphs claim).**

| Theory | funnygraph construct | Measurable proxy | Status |
|---|---|---|---|
| Incongruity/IR/SD | double_interpret, split_knowledge, false_analogy, juxtapose | operator rates per 10k words (operator_frequency) | ✅ measured (M4/M5) |
| Bergson rigidity | rigidify, literalize, character_violation | literal-construction rates vs density; mean paper \| op (theory_content.py) | ✅ measured; text-proxy M5 FAILED (r=−0.05), direct M5-redo +.18 — recalibrate with proxy discipline |
| Superiority | status_invert, unmask, roast mode, roast taboo | roast-mode board; quote_rate (F3) | 🔶 board live; quote_rate reserved |
| Relief/tension | timing_doctrine (holds/pauses), misinterpretation_rule | pause structure vs rating (M7); laughmap (F4) | 🔶 doctrine hypothesized (98); measured n=4 |
| BV (benign conditions) | taboo field + distance (era/culture in COUNTRY_THEORY) | cross-culture taboo variance | 🔶 authored; regional awards legs scheduled |
| GTVH 6 KRs | gtvh_profile (SO/LM/TA/SI/NS) + style (LA) | per-bit ops + stylometry | 🔶 shell in 32 graphs, mostly empty |
| SSTH script opposition | essay_seeds, known_bits why-they-work | bit-level SO annotation | ❌ unscheduled |
| HSQ styles | mode system (affiliative↔aggressive axis) | per-comic style scores | ❌ unscheduled |
| Play theory (IEP 4th school) | crowd-improv mode, riff sets | improv-fraction metrics | 🔶 mode exists, unmeasured |

The M5 failure (authored rigidify priors uncorrelated with measured
density via text proxies) is now interpretable THROUGH this section
rather than against it: priors were assigned without proxy discipline.
The direct retest (theory_content.py M5-redo: authored priors vs
characters2 measured rates, 18 comics) gives mean Pearson +.18 —
better, still weak. THInC shows the remaining fix — per-theory proxy
features with fitted weights — which is exactly the Mallows-precision
program (§4.9) applied to operators next, now with fitted mechanism
weights as the starting point (mistake_identity/juxtapose/status_invert
lead). Theory does not decorate our metrics; it constrains what counts
as evidence for them.

## 3. Data

### 3.1 Sources

| Source | n | Type | Years | Access |
|---|---|---|---|---|
| Comedy Central 100 | 100 ranked (29 among kings) | critics panel | 2004 | public list |
| Rolling Stone 50 | 50 ranked (28 among kings) | critics vote | 2017 | public list |
| IMDb title.ratings + title.basics | 83,292 comedy entries w/ votes | audience cardinal | to 2026 | free public datasets |
| Wikidata (P569/P19/P166) | 170 bios, awards w/ years | structured facts | — | CC0 API |
| funnygraph transcripts | 404 files, ~19MB | text | 1970s–2026 | mixed (fair-use research) |
| YouTube Data API (registry channels only) | 57 pulls, ~556 clips | views/likes/comments | to 2026 | quota-limited |
| Netflix official reports | 7 reports | viewership hours | 2023–2026 | public releases |
| funnygraph comedian graphs | 293 (178 kings + 115 indies) | theory + metadata | to 2026 | authored (hypothesis-flagged) |

Rankings use kings only (indies enter canon on promotion — a stated
scope rule, not a quality claim). All pipelines exclusion-guard via
excluded.json (currently one entry, §8).

### 3.2 Coverage audit (2026-10-17)

Critics leg scores 41/178 kings; audience leg 76/178; prestige-matched
awards 25/178 (44 graphs carry an awards field; 25 match the prestige
table). Full three-leg coverage: 11 comics. ~100 comics ride near-zero
legs — their ranks are noise, and §4.8/§6.2 say so numerically.

### 3.3 What we exclude and why

No verbatim copyrighted acts in any graph (theory analysis of transcripts
is fair-use research; generation uses original or world-mapped material).
Stage persona only, no biography. One comedian excluded by owner
prerogative, logged with reason in EXCLUSIONS.md (auditable, not secret);
pipelines skip the slug; historical pulse snapshots stay immutable.
Re-admission is defined (reverse the file + re-harvest).

## 4. Method

### 4.1 Design principles

1. **No crown without the fight shown.** Every board ships leg breakdowns
   and disagreement; every position ships a stability interval.
2. **Never blend what disagrees.** If voter legs measure different things,
   averaging destroys both signals — publish both, productize the gap.
3. **Missingness is never rewarded and never silently punished.**
   Missing legs score neutral (z=0); contemporary absence scores low
   (Dwork); postdate absence is excluded (not scored). Each operational,
   each stated.
4. **Robust statistics by default.** Medians not means; minimum group
   sizes; floors on eligibility. Giants must not crater good comics, and
   single outliers must not mint heroes.
5. **Fit, don't assert.** Any number that can be estimated from data
   (shrinkage priors, leg weights) is estimated; anything asserted
   (prestige ordering, verdict bands) is labeled asserted with its
   derivation sample.

### 4.2 The critics leg: Borda, and why not Kemeny

Each list contributes Borda points (top = most), normalized to [0,1] by
its own max, summed (range 0–2). Justification is threefold. *Theory:*
Borda is a 5-approximation to the Kemeny optimum (Dwork et al. 2001) at
O(n log n); exact Kemeny is NP-hard at n=178 (Bartholdi et al. 1989), so
the choice is approximation-with-guarantee versus intractability.
*Empirics:* rank-breaking Bradley-Terry on the same lists' implied pairs
agrees with the Borda order at τ ≈ +0.64–0.88 (§4.5, decaying as lists multiply) — Borda is validated as
the cheap stand-in, not merely assumed. *Auditability:* any reader can
recompute Borda by hand; almost no reader can audit an MCMC Kemeny
sampler. We trade the last mile of optimality for total transparency,
and measure what the trade costs (Kemenization displacement: max 19,
mean 0.76 positions).

### 4.3 The audience leg: calibrated shrinkage

Per comedian, the standout (fallback: best) special; IMDb Top-250
shrinkage `WR = (v/(v+m))·R + (m/(v+m))·C`. Parameters are FITTED, not
borrowed from film: corpus mean C = 7.50, median votes 3,747, m = 500
keeps 75/99 specials eligible (the film default m=25,000/C≈7.0 would
drown specials signal in prior). This is empirical Bayes in the
James–Stein tradition: low-vote specials shrink toward the corpus mean,
high-vote specials stand on their ratings. Rank comedians by WR; Borda;
normalize. Limitations (stated): vote-count bias toward recent Netflix
hours is damped, not erased; selection bias (only notable specials get
IMDb pages); platform-wide rating drift uncorrected; brigading
unmodeled (no voter data — the regular-voter weighting IMDb uses is
irreplicable and we do not pretend otherwise).

### 4.4 The awards leg: prestige with sparse coverage

Substring-matched prestige weights (code table): Mark Twain 3.0, Kennedy
2.5, Grammy 2.0, Pulitzer 2.0, Emmy/Peabody 1.5, Tony/Oscar/Golden
Globe/Writers Guild/critics-circle 1.0; first hit wins; summed,
normalized. Justification: awards are high-authority, low-coverage
signals — the ordering is asserted (Mark Twain > Grammy is a judgment),
the sparsity is measured (25/178). Skew stated: Grammys favor recorded
mainstream, Mark Twain is lifetime achievement (old comics), alt and
non-US scenes are systematically missed (roadmap: Humour Awards (NG),
Edinburgh Comedy Award, Melbourne Barry as equal legs — the Wikidata P166
machinery already supports any award).

### 4.5 The pairwise leg: Bradley-Terry now, arena later

Two build stages. *Stage 1 (built, v0.2):* rank-breaking on list-implied
pairs — CC2004 yields 406 pairs, RS2017 378 (among kings), 701 unique;
MM estimation (Hunter 2004) to 1e-12. Result: BT order vs Borda critics
τ = +0.642 (n=69, 4 lists) down from +0.876 (n=41, 2 lists); vs full consensus +0.639. Caveat (stated):
unregularized BT concentrates mass on undefeated players (Pryor 0.993 vs
Carlin 0.007); the ORDER is validated, strengths are uncalibrated —
weak-prior regularization is scheduled. *Stage 2 (designed):* blind arena
pairwise votes → BT scores with Wilson n≥30 gates, anti-brigading rules,
and Bradley-Terry global scores via Zermelo iteration feeding a fourth
leg; HodgeRank cycle analysis and TrueSkill dynamics apply once votes
have timestamps. Plackett-Luce (Plackett 1975; Luce 1959) generalizes BT
to full rankings and is the natural model for future critic-survey
ballots.

### 4.6 Aggregation: weighted sum + local Kemenization

Default weights (critics 3, audience 2, awards 1) are published and
tunable — and superseded wherever fitting exists (§4.9). Local
Kemenization: adjacent-swap hill-climb against total Kendall distance to
the three legs' implied orders, ≤6 passes. Honesty note: the Kemenization
cost is unweighted while the consensus is weighted — a v0.3 refinement
(cost weighted by leg precision) is specified, not implemented.

### 4.7 Missing-data rules, stated precisely

Dwork's partial-list rule (unranked below ranked) applies only where the
item could have been ranked. Postdate items (generation starts after the
list year) never enter the list's Borda; contemporary-but-absent items
score 0. Precision admission: in a Borda sum both cases contribute 0 to
that list — the distinction is operational in era z-scores (missing →
neutral 0), disagreement gating (zero legs excluded from the s.d.), and
coverage badges, not in the critics score itself. Generation means
breakthrough decade, never birth year.

### 4.8 Era normalization

Cross-era raw comparison is rigged (recency: more specials, more votes,
living memory; antiquity: canonization, survivorship). Following the
sports/music era-baseline precedent, we compute within-generation
z-scores per leg: median-centered (robust), missing = neutral 0,
generations with <5 scored members fall back to global mean/sd (tiny
groups give extreme z from single outliers). Raw and era-adjusted boards
both ship; their gap is a finding (era_gap.json, gated to ≥2 scored
legs): Chappelle 13.02, Carlin 11.38, Hicks 10.98 top the adjusted board.

### 4.9 Weights: from asserted to fitted

*Experiment 1 — hide one list.* Predict RS2017 from CC2004+IMDb+awards.
Run A (n=16): CC-only 0.692, best blend 0.692 at (1,0,0), asserted
(3,2,1) 0.658. Run B (n=29, fuller features): best (1,2,1) 0.709,
asserted 0.677, CC-only 0.635 — direction FLIPPED. n≈20 grid fits are
fragile (±0.05 on a few members' features); this experiment is weak
signal, both directions observed. It does not steer product: the split
rests on pairwise taus (stable, large-n), and §4.10 stands on those.
Documented fully in GAPS.md (Runs A+B).

*Experiment 2 — Mallows φ per leg.* Moment-matched against consensus via
the exact RIM expectation (Fligner & Verducci 1986), current run: critics φ=0.824,
audience φ=0.903, awards φ=0.859. Precision-implied weights: critics
0.433, audience 0.227, awards 0.340 (run values move with coverage; ordering is the finding) — the asserted (3,2,1) over-weighted
audience and under-weighted awards. Circularity caveat (stated): fitting
against consensus lower-bounds noise; the precision ORDERING is the
finding, not absolute φ. CANON weights renormalized from precisions:
critics 0.560, awards 0.440 — zero asserted weights in the canon board.

### 4.10 Split elections (obeying the fit)

CANON (critics+awards, fitted weights): Carlin, Robin Williams, Pryor.
PEOPLE'S CHOICE (audience WR only): Burnham (Inside 8.591), Izzard
(8.534), Louis C.K. (8.458). Momentum (standout-special recency
percentile) is SHOWN, never blended — blending without velocity data
would repeat the asserted-weights error. The weighted consensus remains
as the legacy view. The two #1s differ; that divergence is the product,
not a bug.

### 4.11 The house election (proprietary — first-party signals only)

The boards above aggregate other parties' judgments — rigorously, but
borrowed. The house board (house_rank.py) is the only number that is
ours, built exclusively from signals we measured or authored:

- **P1 quality**: mean calibrated paper score per comic (29,617
  characters2-annotated bits, laughter-fitted rubric). First-party
  measurement; 18 comics today, grows with annotation.
- **P2 depth**: craft score (known_bits + essays + timing). First-party
  authored — flagged, capped, never silent.
- **P4 arena**: reserved. Our blind pairwise votes when TOP2026 runs —
  first-party by construction, empty until then.

Excluded by doctrine, not oversight: reach/pull (popularity is not
quality — §4.12's own rule) and awards (external judgments; factual
record kept, prestige never scored). Aggregation is the mean of
AVAILABLE normalized legs — missing legs excluded from the denominator
(neutral, never punished or rewarded) — with no asserted weights: the
default is the plain mean and every position ships a weight-sweep
interval (P1:P2 in {0:1, 1:3, 1:1, 3:1, 1:0}). Fitting (Mallows pattern)
is scheduled once P1 covers 50+ comics. Coverage counts proprietary legs
only: FULL (both) / PARTIAL (one) / UNRANKED (none — no rank, provisional
headline only). Current board: 18 FULL, 80 PARTIAL; #1 Norm Macdonald
(P1 .968 + P2 .875, sweep [1,3]), then Louis, Carlin. External boards
remain computed and displayed verbatim as labeled reference (ref:true) —
the gap between ours and theirs is product, not embarrassment.

### 4.12 The five lenses (metric-by-metric justification)

- **Legacy**: percentile rank on consensus (0–100). Justification: ranks
  are ordinal and cross-board-comparable only as percentiles; `legacy_era`
  repeats on the adjusted board. Slow-moving by construction.
- **Audience**: raw standout rating mapped 5→0/9→100. Justification for
  raw-over-WR: shrinkage exists to ORDER fairly; a display score should
  show what viewers said, with vote-base credibility on the coverage
  badge. The duality is open (v0.3: show both).
- **Popularity**: mean of YouTube-views and Netflix-hours reach
  percentiles among tracked comics. Justification: reach is multi-source
  and source-skewed; percentiling per source then averaging bounds any
  one source's dominance. Never enters quality — enforced in code paths,
  not just docs.
- **Heat**: UNIMPLEMENTED (null). Justification for absence: a metric that
  moves weekly must not be faked from a snapshot; spec exists
  (views/day velocity bracketed by channel size), blocker is pulse
  cadence. Nulls ship instead of proxies.
- **Theory**: two halves. v1 depth/8 (bits ≤3 + essays ≤2 + measured
  timing 2 + doctrine 1) — documentation depth, all comics. v2 content
  (theory_content.py): mean calibrated paper score + p90 + operator
  entropy from 29,617 characters2-annotated bits across 18 comics, ranked
  within humor_type (7 types covered) — joke quality, not documentation.
  Justification: the only lens scoring the work not its reception; v2
  answers "best jokes per type" with laughter-fitted scores (top:
  Carlin .0250 rant, Seinfeld .0243 observational, Norm .0242
  absurdist). Fitted mechanism weights: mistake_identity +.0065,
  juxtapose +.0047, status_invert +.0038 over global mean; commonest
  operator (split_knowledge, n=3011) −.0014 — frequency ≠ quality.
  M5-redo: authored priors vs measured rates now Pearson +.18 (n=18),
  up from −.05 via text proxies — authoring beats proxies but stays
  weak. Unmeasured comics keep v1 only, badged, never blended.
- **Verdict Gap** (Popularity−Audience, percentile units): bands from the
  observed distribution (n=64, median +0.087): ±0.20 accurate (~60%),
  ±0.50 massive. Distribution-derived, not round-numbered.
- **Canon Lag** (Audience−Legacy): ahead-of-canon vs canonized-above-love.

## 5. Results (v0.2 snapshot)

Consensus: Carlin 8.49, Pryor 7.71, Rock 7.16, Chappelle 6.51, Seinfeld
6.51 (reference election — others' judgments, rigorously aggregated).
House (proprietary): Norm 0.922, Louis 0.911, Carlin 0.812 — our number
puts the best-measured jokes on top. Most fought-over: Lenny Bruce (0.83 — canonized, unwatched), Rock,
Rivers, Seinfeld, Pryor. Gaps: Iglesias +0.83 (most overrated; Hart
+0.525 the famous case), Hicks
−0.70, Lee −0.612 (most underrated), Burr +0.114, Chappelle +0.102
(balanced). Stability: Carlin #1 [1,2] is a claim; Vir Das #22 [14,175]
is a question; Gillis sits #170 — the critics leg structurally cannot see
post-2017 breakouts, which is why TOP 2026 (fresh-legs election, Dec 2026)
exists. Full boards: consensus, era-adjusted, by-generation/type/mode/
decade/continent, specials (Inside 8.591 #1), bits (134), neighbors,
netflix, canon, peoples, bt, stability, agreement, mallows,
theory_content (18 measured comics, 7 type boards).

## 6. Validation

6.1 **Agreement analysis** (kendall_w.py): pairwise τ-b with bootstrap CIs — τ(ca)=−0.036 [−0.125,+0.080], τ(cw)=+0.103, τ(aw)=+0.374; Kendall's W = 0.592, p = 0.041 on 14 full-coverage comics (significant — the legs agree weakly but really). Awards most central leg (0.238).
6.2 **Stability analysis** (stability.py): 71 regimes; 12/295 stable (latest);
Kemenization displacement max 19/mean 0.76/56 moved. One-leg wonders
collapse under LOO — correctly: their ranks ARE one-leg artifacts.
6.3 **BT validation** (bt_leg.py): τ = +0.642 vs Borda critics (4 lists, 4283 pairs; was +0.876 on 2 lists).
6.4 **Construct tests** (ml_analysis.py, theory_content.py): ratings
regression R² = 0.09 (profanity ≈ 0 effect; double-interp +/vocab-div
−); Greengross text-proxy test FAILS (r = −0.05), direct M5-redo
(authored vs measured priors, 18 comics) gives Pearson +.18 — weak but
nonzero, best-authored Chappelle .795; fitted mechanism weights
(mistake_identity/juxtapose/status_invert lead) start the proxy-
discipline program; profanity peaked in the 70s, declining (M6).
6.5 **Face validity**: gap extremes match critical consensus, now
numbered.
6.6 **Falsifiers**: gaps must survive equal-coverage subsamples
(quarterly); BT must track Borda under new lists; stability must widen,
not narrow, as regimes grow (else regimes are correlated theater).

## 7. Limitations

Two frozen critics inputs (newest 2017); n=16 fitting set (bootstrap CI
scheduled); BT strengths uncalibrated; Kemenization cost unweighted;
IMDb/awards/YouTube skews (§4.3–4.4); arena leg empty; non-English thin;
stability is regime-based, not sampling-based; single-author theory
seeds; crowd-display/WR-rank duality open. Full register: GAPS.md.

## 8. Ethics and auditability

Stage persona only; no verbatim acts; no biography. Exclusions logged
with orderer and reason (one entry); pipelines guard; snapshots
immutable. Coverage badges (FULL/PARTIAL/THIN/UNRANKED) instead of silent
gaps. No crown under n≥30 verified votes (arena rule, Wilson-gated).
Money never touches ranking inputs (no paid votes, no sponsored
placement — stated as policy).

## 9. Conclusion

We replace the listicle with an instrument: three (soon four) voter legs
with fitted weights, era-normalized, disagreement-first, stability-
intervaled, split where the data says split — and above them a house
election built only from what we measured ourselves, with everyone
else's judgments displayed alongside as labeled reference rather than
smuggled into our number. Every failure mode is published alongside.
The strongest claims in this paper are negative —
small-n grid fits flip direction across runs (fragile — see GAPS.md),
critics and audiences barely agree (τ ≈ 0, W p = 0.04 on n=14),
text-proxy theory priors don't predict ratings (r = −0.05,
direct retest +.18 — weak either way), only a minority of
positions are stable — and negatives are what make the positives (Norm #1
on owned evidence, sweep [1,3]; Borda ≈ BT at τ ≈ 0.64–0.88; precision-implied
weights) believable.
Definitive, here, means auditable — not uncontested.

---

## References

- Arrow, K.J. (1951). *Social Choice and Individual Values.* Wiley.
- Attardo, S. & Raskin, V. (1991). Script theory revis(it)ed: joke
  similarity and joke representation model. *HUMOR*, 4(3–4).
- Attardo, S. (1994). *Linguistic Theories of Humor.* Mouton de Gruyter.
- Bartholdi, J.J., Tovey, C.A. & Trick, M.A. (1989). Voting schemes for
  which it can be difficult to tell who won the election. *Social Choice
  and Welfare*, 6(2), 157–165.
- Berry, S.M., Reese, C.S. & Larkey, P.D. (1999). Bridging different eras
  in sports. *Journal of the American Statistical Association*,
  94(447), 661–686.
- Beattie, J. (1779). Essay on Laughter and Ludicrous Composition. Creech.
  (First philosophical use of "incongruous" for humor analysis.)
- Bergson, H. (1900). *Le Rire. Essai sur la signification du comique.*
  Alcan. (English text via Project Gutenberg.)
- Bradley, R.A. & Terry, M.E. (1952). Rank analysis of incomplete block
  designs: I. The method of paired comparisons. *Biometrika*, 39(3/4),
  324–345.
- Dodds, P.S., Minot, J.R., Arnold, M.V., Alshaabi, T., Adams, J.L.,
  Dewhurst, D.R., Gray, T.J., Frank, M.R., Reagan, A.J. & Danforth,
  C.M. (2020). Allotaxonometry and rank-turbulence divergence. *EPJ Data
  Science*, 9, 36.
- Dwork, C., Kumar, R., Naor, M. & Sivakumar, D. (2001). Rank aggregation
  methods for the Web.   *Proc. 10th WWW*, 613–622.
- De Marez, V. (2024). THInC: a theory-driven framework for computational
  humor detection. *arXiv:2409.01232.* (Per-theory GA2M ensemble, F1 0.85;
  relief proxy weight highest at 1.591.)
- Dupin de Saint-Cyr, F. & Prade, H. (2023). Belief revision and
  incongruity: is it a joke? *arXiv:2309.02009.*
- Elo, A.E. (1978). *The Rating of Chessplayers, Past and Present.*
  Arco.
- Fligner, M.A. & Verducci, J.A. (1986). Distance based ranking models.
  *J. Royal Statistical Society B*, 48(3), 359–369.
- Ford, R. (2018). Life's joke: Bergson, comedy, and the meaning of
  laughter. *Boston Studies in Philosophy, Religion and Public Life*,
  175–193. Springer.
- Freud, S. (1905). *Der Witz und seine Beziehung zum Unbewußten.*
  Deuticke. (Jokes and Their Relation to the Unconscious: joke-work,
  tendentious vs innocent jokes.)
- Freud, S. (1927). Humour. *Int. J. Psycho-Analysis*, 9. (1928 in some
  citations — VERIFY.)
- Gervais, M. & Wilson, D.S. (2005). The evolution and functions of
  laughter and humor. *Quarterly Review of Biology*, 80(4).
- Glickman, M.E. (1999). Parameter estimation in large dynamic paired
  comparison experiments. *JRSS-C*, 48(3), 377–394.
- Herbrich, R., Minka, T. & Graepel, T. (2007). TrueSkill: a Bayesian
  skill rating system. *Proc. NeurIPS 19.*
- Hunter, D.R. (2004). MM algorithms for generalized Bradley-Terry
  models. *Annals of Statistics*, 32(1), 384–406. *(verify volume/pages)*
- Hobbes, T. (1651). *Human Nature*, ch. 8; *Leviathan*. ("Sudden glory"
  superiority account — cite Human Nature per IEP.)
- Hurley, M.M., Dennett, D.C. & Adams, R.B. (2011). *Inside Jokes: Using
  Humor to Reverse-Engineer the Mind.* MIT Press. (VERIFY year: some
  cites give 2013.)
- Kant, I. (1790). *Kritik der Urteilskraft*, §54. (Strained expectation
  transformed into nothing.)
- Keith-Spiegel, P. (1972). Early conceptions of humor: varieties and
  issues. In Goldstein & McGhee (eds.), *The Psychology of Humor*.
  Academic Press.
- Koestler, A. (1964). *The Act of Creation.* Hutchinson. (Bisociation.)
- Kuznetsova, A. & Strapparava, C. (2024). Multimodal and multilingual
  laughter detection in stand-up comedy videos. *LREC-COLING 2024.*
  (VERIFY — cited via StandUp4AI paper.)
- James, W. & Stein, C. (1961). Estimation with quadratic loss. *Proc.
  Fourth Berkeley Symp. Math. Statist. Prob.*, 1, 361–379.
- Jiang, X., Lim, L.-H., Yao, Y. & Ye, Y. (2011). Statistical ranking
  and combinatorial Hodge theory. *Mathematical Programming*, 127(1),
  203–244.
- Kemeny, J.G. (1959). Mathematics without numbers. *Daedalus*, 88(4),
  577–591.
- Kendall, M.G. (1938). A new measure of rank correlation.
  *Biometrika*, 30(1/2), 81–93.
- Kendall, M.G. & Babington Smith, B. (1939). The problem of m rankings.
  *Annals of Mathematical Statistics*, 10(1), 275–287.
- Khetan, A. & Oh, S. (2016). Data-driven rank breaking for efficient
  rank aggregation. *J. Machine Learning Research*, 17(100), 1–28.
  *(verify article number)*
- Li, B. (2016). Humor: a dynamic and dual-process theory with
  computational considerations. *HUMOR: Int. J. Humor Research.* (VERIFY
  venue — manuscript at boyangli.org; surprise→reflection→dismissal→
  compensation.)
- Luce, R.D. (1959). *Individual Choice Behavior.* Wiley.
- Mallows, C.L. (1957). Non-null ranking models. I. *Biometrika*,
  44(1/2), 114–130.
- Martin, R.A., Puhlik-Doris, P., Larsen, G., Gray, J. & Weir, K.
  (2003). Individual differences in uses of humor and their relation to
  psychological well-being. *J. Research in Personality*, 37(1).
  (Humor Styles Questionnaire: affiliative, self-enhancing, aggressive,
  self-deprecating.)
- Martin, R.A. & Ford, J.M. (2018). *The Psychology of Humor: An
  Integrative Approach.* 2nd ed. Academic Press.
- Minsky, M. (1980). Jokes and the logic of the cognitive unconscious.
  *AI Memo 603*, MIT. (Frame-shift account of puns.)
- Mittal, A. et al. (2021). "So you think you're funny?": rating the
  humour quotient in standup comedy. *arXiv:2110.12765.* (Open Mic
  dataset; laughter-duration scoring; QWK 0.6 validation, 0.813 model.)
- Morreall, J. (1987). *The Philosophy of Laughter and Humor.* SUNY.
- Morreall, J. (2009). *Comic Relief: A Comprehensive Philosophy of
  Humor.* Wiley-Blackwell.
- Morreall, J. (2024). Philosophy of Humor. *Stanford Encyclopedia of
  Philosophy*, Fall 2024 archive.
  https://plato.stanford.edu/archives/fall2024/entries/humor/
- McGraw, A.P. & Warren, C. (2010). Benign violations: making immoral
  behavior funny. *Psychological Science*, 21(8), 1141–1149.
- Negahban, S., Oh, S. & Shah, D. (2017). Rank centrality: ranking from
  pairwise comparisons.   *Operations Research*, 65(1), 266–287.
- Newman, M.E.J. (2023). *(pairwise-comparison ranking — VERIFY exact
  title/venue before submission; cited in repo drafts as Newman 2023.)*
- Plackett, R.L. (1975). The analysis of permutations. *JRSS-C*, 24(2),
  193–202.
- Provine, R.R. (2000). *Laughter: A Scientific Investigation.* Viking.
- Prusak, B.G. (2004). Le rire à nouveau: rereading Bergson. *J.
  Aesthetics and Art Criticism*, 62(4), 377–388.
- Raskin, V. (1985). *Semantic Mechanisms of Humor.* Reidel. (SSTH:
  script opposition.)
- Raskin, V. (ed.) (2008). *The Primer of Humor Research.* Mouton de
  Gruyter.
- Ritchie, G. (1999). Developing the incongruity-resolution theory. *Proc.
  AISB Symposium on Creative Language.* (Surprise-disambiguation model.)
- Ritchie, G. (2001). Current directions in computational humour.
  *Artificial Intelligence Review*, 16. (VERIFY pages.)
- Romanowski, A., Valois, P.H.V. & Fukui, K. (2025). From punchlines to
  predictions: a metric to assess LLM performance in identifying humor in
  stand-up comedy. *arXiv:2504.09049.* (Frontier models ≤51% vs 41%
  human on punchline identification.)
- Ramachandran, V.S. (1998). The neurology and evolution of humor,
  laughter, and mirth. *Medical Hypotheses*, 51(4). (False-alarm theory
  — VERIFY.)
- Schopenhauer, A. (1844). *Die Welt als Wille und Vorstellung*, Bk I.
  (Concept-vs-perception incongruity.)
- Sinclair, M. (2019). Laughter. In *Bergson: Key Writings* companion
  chapter, Routledge. doi:10.4324/9781315414935-7. (VERIFY chapter
  details.)
- Spencer, H. (1860). The physiology of laughter. *Macmillan's Magazine*.
- StandUp4AI consortium (2025). StandUp4AI: multilingual word-level
  laughter labeling in stand-up comedy. *arXiv:2505.18903.* (VERIFY
  venue — repo draft cites EMNLP 2025.)
- Suls, J. (1972). A two-stage model for the appreciation of jokes and
  cartoons. In Goldstein & McGhee (eds.), *The Psychology of Humor*.
  Academic Press.
- Veatch, T. (1998). A theory of humor. *HUMOR*, 11(2). (Violation +
  normality; cited as BV precursor.)
- Vineeth, N.C. (2023). Computational humor: a survey of the literature.
  doi:10.13016/m2ruid-crqs. (IR theory as seminal; Beattie 1776/1779
  first "incongruous".)
- Watson, C. (2022). 'Shipwrecked by the laughter of the gods': Henri
  Bergson's theory of comedy and the meaning of life. *Comedy & Change*.
  doi:10.1080/2040610x.2023.2149220. (VERIFY venue/pages.)
- Wilson, E.B. (1927). Probable inference, the law of succession, and
  statistical inference. *JASA*, 22(158), 209–212.
- Zermelo, E. (1929). Die Berechnung der Turnier-Ergebnisse als ein
  Maximumproblem der Wahrscheinlichkeitsrechnung. *Math. Zeitschrift*,
  29(1), 436–460.
- Greengross, G., Martin, R.A. & Miller, G.F. (2012). *(VERIFY full
  citation — repo draft cites performer-psychology result, n=31.)*
- SCRIPTS (LREC 2022); StandUp4AI (EMNLP 2025); Open Mic humour scores
  (Mittal et al. 2021); CMCL-2025 LLM humor metric; LIWC/IMDb linguistic
  rating-prediction study — *(VERIFY all before submission.)*
- Industry: IMDb Top-250 chart methodology (help.imdb.com); Rotten
  Tomatoes Tomatometer/Audience Score methodology; Metacritic
  (undisclosed weights); Letterboxd Top 250.
- Additional arXiv / web sources (VERIFY authorship and exact citation
  before submission):
  - Advancing humor generation with multistep reasoning (2024).
    arXiv:2405.07280. (Association-mining generation pipeline; 20+
    theories in 3 families.)
  - HUMORCHAIN: theory-guided multi-stage reasoning for interpretable
    multimodal humor generation (2026). arXiv:2511.21732. (Four
    theories cover 86% of 100 samples; strategy distribution ~even.)
  - IEP "Humor" article. https://iep.utm.edu/humor/. (Monro standard
    analysis; rival-framing critique; play theory as 4th school.)
  - Ma (manuscript). "Stand-up Comedy: Quantifying Humor and Identity."
    (Punchline classification + comedian-identity interaction
    regression; laughter-duration as response intensity.)
  - This joke is [MASK]: recognizing humor and offense with prompting
    (2022). arXiv:2210.13985. (Influence-function offense tracing;
    SemEval-2021 humor/offense entanglement.)
  - Two-model approach for humour style recognition (2024).
    arXiv:2410.12842. (Martin-2003 styles; affiliative hardest;
    AI-completeness claim.)
  - Who's Laughing Now? An overview of computational humour generation
    and explanation (2025). arXiv:2509.21175. (Triad survey; LLM
    log-likelihood objective works against incongruity.)

---

## Appendix A — Pipeline / file map (what computes what)

| Artifact | Script | Reads | Writes |
|---|---|---|---|
| legs + consensus + era + disagreement | rank_comedians.py | graphs, excluded.json | consensus/by_generation/era_adjusted/era_gap/disagreement.json |
| lenses + gaps | metrics.py | consensus, era, YT, graphs | graphs[].metrics, metrics.json |
| concordance | kendall_w.py | (recomputes legs) | agreement.json |
| stability intervals | stability.py | (recomputes legs) | stability.json |
| Mallows φ + weights | mallows_phi.py | consensus | mallows.json |
| BT leg | bt_leg.py | graphs | bt.json |
| split elections | split_boards.py | mallows.json | canon.json, peoples.json |
| weight fitting | fit_weights.py | graphs | stdout (finding) |
| construct tests | ml_analysis.py | transcripts, graphs | analysis/ml_*.json, graphs[].style |
| joke-quality evidence | theory_content.py | characters2 bits/ml (live), graphs | theory_content.json |
| proprietary election | house_rank.py | theory_content + metrics (first-party only) | house.json |
| latent space | recommend.py | graphs | neighbors.json |

## Appendix B — Pre-submission checklist

- [ ] Verify Newman 2023, Hunter 2004 pages, Khetan & Oh article no.,
  Greengross/Martin/Miller full cite, all computational-humor cites.
- [ ] Verify theory cites: Freud "Humour" year (1927 vs 1928); Hurley/
  Dennett/Adams year (2011 vs 2013); Li 2016 venue; Kuznetsova &
  Strapparava 2024 venue; authorship + full cites for all seven
  "Additional arXiv" entries, the Ma manuscript, and the IEP article.
- [ ] Recompute every inline number at submit time (rankings move).
- [ ] Bootstrap CI on the n=16 fitting result (or report exact CI).
- [ ] Coverage-weighted confidence per position (§6 roadmap) or downgrade
  roadmap claims.
- [ ] BT weak-prior regularization (or drop strengths, keep order).
- [ ] Weight the Kemenization cost by leg precision (or justify equal).
- [ ] Decide crowd-display vs WR-rank duality (show both?).
- [ ] arXiv category (cs.SI? stat.AP? cs.CY?) + anonymization check.
- [ ] Re-run secret-scan (YOUTUBE_DATA_API_KEY, HF_TOKEN in .env only).

## Appendix C — Version history

- v0.1 (2026-10-17 AM): RANKINGS.md + PAPER.md draft; m=1000/C=7.0;
  mean z-scores; n=179/181; asserted (3,2,1); single consensus.
- v0.2 (2026-10-17 PM, this manuscript): corpus-calibrated m=500/C=7.5;
  median z-scores; 178 kings; Mallows-implied weights; CANON/PEOPLE'S
  split primary; BT validation (τ≈0.64–0.88); agreement + stability + Mallows
  machinery; crowd-raw correction; HEAT null admission; full bibliography.
