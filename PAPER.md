# Consensus Ranking of Stand-Up Comedians Across Eras
## A principled aggregation of critics, audiences, and awards with honest uncertainty

**funnygraph working paper v0.2 — DRAFT, not submitted.**
Synced to code 2026-10-17 (rank_comedians.py, metrics.py, kendall_w.py,
stability.py, mallows_phi.py, bt_leg.py, split_boards.py). Supersedes v0.1
where they differ; drifts are listed in §8, not hidden.

---

## Abstract

We construct a principled consensus ranking of stand-up comedians (n=178
kings) from three voter legs: published critics' lists (Comedy Central 2004,
Rolling Stone 2017), audience ratings (IMDb standout-special weighted
ratings, Top-250 shrinkage calibrated to the specials corpus: m=500,
C=7.50), and industry awards (Wikidata, prestige-weighted). Aggregation is
Borda per leg → weighted sum → local Kemenization. Our contributions: (1) a
postdate-aware missing-data rule extending Dwork's partial-list treatment;
(2) era-normalized comparison via within-generation median z-scores
(missing = neutral, minimum group 5); (3) fitted rather than asserted
weights — Mallows dispersion per leg implies precision weights, and a
hide-one-list experiment shows critics-only predicts the held-out list
(0.692) better than any blend (≤0.658), so we publish CANON and PEOPLE'S
CHOICE as separate elections; (4) rank-breaking Bradley-Terry on
list-implied pairs validates Borda as the aggregation (τ = 0.876);
(5) every position carries a 72-regime stability interval — only 15/178
positions are stable claims. All inputs, weights, code, and disagreements
are public. No prior academic work attempts comedian ranking.

---

## 1. Introduction

"Who's the greatest stand-up of all time?" is among the most argued
questions in popular culture — and the least measured. Existing answers are
single snapshots (Comedy Central 100, frozen 2004; Rolling Stone 50, frozen
2017), endless popularity contests (Ranker), or per-special audience scores
(IMDb) that never aggregate to the comedian level. Each is defensible alone;
none combines evidence; none states uncertainty.

We argue the right product is not a crown but a **consensus with
disagreement shown**: a board where every position carries its leg
breakdown and stability interval, every weight is fitted or published, and
the places where critics and audiences fight are the most prominent
feature, not a footnote. Arrow (1951) proves no perfect aggregation rule
exists; we publish our tradeoff.

## 2. Related work

**Computational humor** works on detection, never ranking: SCRIPTS (LREC
2022: 90 scripts / 68 comics, laugh-marker classification), StandUp4AI
(EMNLP 2025: 3617 videos, laughter labels), Open Mic funniness scores, LLM
humor-detection metrics (CMCL 2025). None ranks performers against each
other — that gap is this paper.

**Performer psychology** (Greengross, Martin & Miller 2012) finds
professional success predicted positively by affiliative humor and
negatively by self-defeating humor (n=31 comics). Our operator-prior
features test this at scale; the test currently FAILS (r=−0.05, §6) —
published, not buried. Full theory grounding — the classical triad
(SEP/IEP), Bergson, Freud's joke-work, SSTH/GTVH linguistics, benign
violation, and ten verified arXiv precedents, with a theory→construct→
proxy map for every graph field — lives in PAPER_ARXIV.md §2.6.

**Cross-era comparison** is developed furthest in sports: Berry, Reese &
Larkey (1999) bridge eras statistically; music chart work ports the
era-baseline idea (rank-turbulence divergence, Dodds et al. 2020). We port
within-cohort normalization to comedy (§4.6).

**Rank aggregation theory**: Kemeny optimal consensus is the MLE under the
Mallows (1957) noise model but NP-hard (Bartholdi, Tovey & Trick 1989).
Dwork et al. (2001) give the practical recipe — Borda start (a
5-approximation to the Kemeny optimum), local Kemenization hill-climb —
plus the partial-list rule (unranked items sit below ranked ones) that we
extend with the postdate distinction (§4.2). Bradley-Terry (1952) with MM
estimation (Hunter 2004; originating with Zermelo 1929) handles pairwise
data; rank-breaking (Khetan & Oh 2016) lets lists imply pairs.

## 3. Data

| Source | n | Type | Years | License/cost |
|---|---|---|---|---|
| Comedy Central 100 | 100 ranked (29 among kings) | critics panel | 2004 | public list |
| Rolling Stone 50 | 50 ranked (28 among kings) | critics vote | 2017 | public list |
| IMDb title.ratings + title.basics | 83,292 comedy entries w/ votes | audience cardinal | to 2026 | free public datasets |
| Wikidata (P569/P19/P166) | 170 bios, awards w/ years | structured facts | — | CC0, free API |
| funnygraph transcripts | 404 files, ~19MB | text | 1970s–2026 | mixed (fair-use research) |
| YouTube Data API (registry channels only) | 57 pulls, ~556 clips | views/likes/comments | to 2026 | quota-limited |
| Netflix official reports | 7 reports, 83–347 specials w/ hours | viewership | 2023–2026 | public PDFs/xlsx |

Coverage (2026-10-17): 178 kings scored; critics leg 41, audience leg 76,
prestige-matched awards 25 (44 graphs carry an awards field; 25 match the
prestige table). Full three-leg coverage: 11 comics.

## 4. Method

### 4.1 Voter legs

- **Critics leg.** Borda points per list (top = most), each list normalized
  to [0,1] by its own max, summed (max 2.0). Borda is a 5-approximation to
  the Kemeny optimum (Dwork et al. 2001) at O(n log n) — the formal reason
  we use it rather than exact Kemeny, which is NP-hard at n=178.
- **Audience leg.** Per comedian, the standout (or best) special; IMDb
  Top-250 shrinkage `WR = (v/(v+m))·R + (m/(v+m))·C` with **m=500, C=7.50**,
  calibrated to the specials corpus (corpus mean 7.50, median votes 3,747;
  keeps 75/99 specials eligible — classify_humor.py:186). Rank by WR; Borda;
  normalize to [0,1].
- **Awards leg.** Prestige weights from code (rank_comedians.py AWARD_W):
  Mark Twain 3.0, Kennedy 2.5, Grammy 2.0, Pulitzer 2.0, Emmy/Peabody 1.5,
  Tony/Oscar/Golden Globe/Writers Guild/critics-circle 1.0; substring match,
  first hit wins. Summed per comedian, normalized to [0,1].

### 4.2 Missing-data rules (core contribution — stated precisely)

A list is a partial ranking. Dwork's rule places unranked items below
ranked ones — but only when the item *could* have been ranked:

- **Postdate (missing):** generation starts after the list year (Gillis vs
  2004). Excluded from that list's Borda (never enters the order).
- **Contemporary-but-unranked (low):** active before the list year, absent.
  Scores 0 (Dwork rule) — the panel considered the era and passed.

Precision note (v0.2 honesty): in a Borda-sum aggregation both cases score
0 on that list — the distinction is NOT operational in the critics score
itself. It is operational in (a) era z-scores (missing legs get z=0
neutral, §4.6), (b) disagreement gating (legs scoring 0 are excluded from
the s.d.), and (c) coverage badges. Generation = breakthrough decade, not
birth year — Seinfeld (b.1954) and Rock (b.1965) share a generation by
construction. Cusp cases are flagged, not smoothed.

### 4.3 Aggregation

Weighted sum (default critics 3, audience 2, awards 1 — published,
tunable), then local Kemenization: adjacent-swap hill-climb against total
Kendall distance to the three legs' implied orders (≤6 passes).
Measured displacement at default weights: max 19 positions, mean 0.76, 56
of 178 moved — Kemenization is refinement, not revolution. Precision note:
the Kemenization cost treats legs equally (unweighted) while the consensus
uses (3,2,1); weighting the cost by leg precision is v0.3 work.

### 4.4 Bradley-Terry validation of Borda (new in v0.2)

Rank-breaking (Khetan & Oh 2016): CC2004 yields 406 pairs, RS2017 378
pairs (among kings), 701 unique; MM estimation (Hunter 2004) to 1e-12.
Result: **BT order vs Borda critics leg τ = +0.876 (n=41)** — Borda is an
excellent cheap stand-in for the pairwise MLE on the same data. BT vs full
consensus τ = +0.690. Caveat: unregularized BT concentrates mass on
undefeated players (Pryor 0.993); the ORDER is the finding, strengths are
uncalibrated (weak-prior regularization is v0.3 work).

### 4.5 Weight fitting: Mallows φ and the split boards (new in v0.2)

Fitting the Mallows dispersion per leg against consensus (RIM exact
moment-match, Fligner & Verducci 1986): critics φ=0.721, audience φ=0.869,
awards φ=0.828. Precision-implied weights: **critics 0.498, audience
0.214, awards 0.288** — the asserted (3,2,1) over-weighted audience and
under-weighted awards. Caveat: fitting against consensus is circular
(legs agree with consensus partly by construction), so absolute φ values
are lower bounds on noise; the PRECISION ORDERING is the finding.

The hide-one-list experiment (fit_weights.py, n=16 comics on both lists):
CC-only predicts RS2017 at **0.692**, best blend 0.692 at (1,0,0), current
(3,2,1) at 0.658. **Blending critics with audience destroys canon
signal.** Obeyed in v0.2: CANON board (critics+awards, Mallows weights
0.634/0.366 — no asserted weights) and PEOPLE'S board (audience WR only;
recency shown, never blended) are now primary; the weighted consensus is
the legacy view. Canon #1 Carlin; People's #1 Burnham (Inside, WR 8.591).

### 4.6 Era normalization

Within-generation z-scores per leg before cross-era comparison:
median (not mean — giants must not crater good comics), missing legs z=0
neutral (never rewarded, never punished), generations with <5 scored
members fall back to global mean/sd. Raw and era-adjusted boards both
ship; the gap is itself a finding (era_gap.json, gated to ≥2 scored legs).
Era-adjusted top: Chappelle 13.02, Carlin 11.38, Hicks 10.98.

### 4.7 Disagreement machinery (new in v0.2)

- Per-position s.d. across scoring legs (disagreement.json; top: Lenny
  Bruce 0.83 — canonized, unwatched).
- Inter-leg concordance (kendall_w.py, rankings/agreement.json):
  τ(critics,audience)=+0.177 [95% CI +0.032,+0.303];
  τ(critics,awards)=+0.425 [+0.267,+0.565];
  τ(audience,awards)=+0.290 [+0.151,+0.419].
  Kendall's W over 11 full-coverage comics = 0.438 (χ² p=0.22 —
  **cannot reject independence**). The legs do not significantly agree;
  that is WHY they ship separately. Awards is the most central leg
  (mean τ 0.357).
- Regime-stability intervals (stability.py, 71 regimes: 60 weight-grid +
  3 leave-one-leg-out + 8 WR-prior perturbations): **15/178 positions
  stable** (|p95−p5| ≤ 5). Carlin #1 [1,2] is a claim; Vir Das #22
  [14,175] is a question. Every position ships its interval.

## 5. Results (v0.2, 2026-10-17)

Consensus top 5: Carlin 8.49, Pryor 7.71, Rock 7.16, Chappelle 6.51,
Seinfeld 6.51 (reference election). Canon top 3: Carlin, Robin Williams,
Pryor. People's top 3: Burnham, Izzard, Louis C.K. House top 3
(proprietary, first-party only): Norm 0.922, Louis 0.911, Carlin 0.812.
Full boards + seven generation boards +
decade/type/mode/continent/specials/bits/neighbors in `rankings/`.

## 6. Validation

- **Listicle prediction** (done): §4.5. n=16 is small — CI via bootstrap
  is v0.3 work; the point estimate's DIRECTION (blending hurts) replicated
  across the full pairwise-tau analysis (§4.7).
- **Greengross construct test** (done, FAILED): authored rigidify priors
  vs measured transcript density r=−0.05 (ml_analysis.py M5). Theory
  recalibration required, stated.
- **Ratings regression** (done): R²=0.09 — ratings barely predictable from
  text features; profanity effect ≈ 0; double-interpretation positive,
  vocab-diversity negative (M2). Profanity peaked in the 70s, declining
  (M6).
- **Face validity**: gap extremes match critical consensus (Hicks/Lee
  underrated, Iglesias overrated — now with numbers: Hicks −0.70, Iglesias
  +0.83 (Hart +0.525 the famous case),
  median +0.087, n=64).
- **Falsifiers**: gap rankings must survive equal-coverage subsamples
  (quarterly test); BT order must track Borda under new lists.

## 7. Limitations

Single-author theory seeds; critics leg frozen (newest input 2017 —
post-2017 breakouts structurally scoreless there); IMDb brigading/recency/
anglo-skew partially corrected; awards Western-skew (regional awards
roadmap); arena votes unintegrated; non-English comedy thin; stability
intervals are regime-based, not sampling-based. Full list: GAPS.md.

## 8. v0.1 → v0.2 drift log (what changed and why)

m=1000/C=7.0 → m=500/C=7.5 (corpus calibration); mean → median z-scores;
n=179/181 → 178 kings; awards 13 → 25 prestige-matched; postdate rule
wording made operationally precise; consensus demoted to legacy view
behind CANON/PEOPLE'S; all §6 roadmap items except bootstrap-on-n=16 and
coverage-weighted confidence now built.

## References

- Arrow, K.J. (1951). *Social Choice and Individual Values.* Wiley.
- Bartholdi, J., Tovey, C.A. & Trick, M.A. (1989). Voting schemes for
  which it can be difficult to tell who won the election. *Social Choice
  and Welfare*, 6(2).
- Berry, S.M., Reese, C.S. & Larkey, P.D. (1999). Bridging different eras
  in sports. *J. American Statistical Association*, 94(447).
- Bradley, R.A. & Terry, M.E. (1952). Rank analysis of incomplete block
  designs I. *Biometrika*, 39(3/4).
- Dodds, P.S. et al. (2020). Allotaxonometry and rank-turbulence
  divergence. *EPJ Data Science*, 9:36.
- Dwork, C., Kumar, R., Naor, M. & Sivakumar, D. (2001). Rank aggregation
  methods for the Web. *Proc. WWW10.*
- Fligner, M.A. & Verducci, J.A. (1986). Distance based ranking models.
  *J. Royal Statistical Society B*, 48(3).
- Hunter, D.R. (2004). MM algorithms for generalized Bradley-Terry
  models. *Annals of Applied Statistics*, 2(1).
- Kemeny, J.G. (1959). Mathematics without numbers. *Daedalus*, 88(4).
- Kendall, M.G. (1938). A new measure of rank correlation. *Biometrika*,
  30(1/2).
- Kendall, M.G. & Babington Smith, B. (1939). The problem of m rankings.
  *Annals of Mathematical Statistics*, 10(3).
- Khetan, A. & Oh, S. (2016). Data-driven rank breaking for efficient
  rank aggregation. *J. Machine Learning Research*, 17(1).
- Mallows, C.L. (1957). Non-null ranking models. I. *Biometrika*, 44(1/2).
- McGraw, A.P. & Warren, C. (2010). Benign violations. *Psychological
  Science*, 21(8).
- Newman, M.E.J. (2023). Efficient computation of rankings from pairwise
  comparisons. *arXiv* — VERIFY exact title/venue before submission.
- Plackett, R.L. (1975). The analysis of permutations. *JRSS-C*, 24(2).
- Raskin, V. (1985). *Semantic Mechanisms of Humor.* Reidel; Attardo, S.
  & Raskin, V. (1991). Script theory revis(it)ed. *HUMOR*, 4(3-4).
- Wilson, E.B. (1927). Probable inference, the law of succession, and
  statistical inference. *J. American Statistical Association*, 22(158).
- Zermelo, E. (1929). Die Berechnung der Turnier-Ergebnisse als ein
  Maximumproblem der Wahrscheinlichkeitsrechnung. *Math. Zeitschrift*, 29.
- Greengross, Martin & Miller (2012); SCRIPTS/LREC 2022; StandUp4AI/EMNLP
  2025; Open Mic (Mittal et al. 2021); CMCL 2025 LLM humor metric — VERIFY
  full citations before submission (see PAPER_ARXIV.md checklist).
- Industry systems: IMDb Top-250 formula (help.imdb.com); Rotten
  Tomatoes Tomatometer/Audience methodology; Metacritic (undisclosed
  weights — negative example); Letterboxd Top 250.
