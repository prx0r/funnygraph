# Five Lenses: Auditable Multi-Signal Metrics for Stand-Up Comedy

## funnygraph working paper v0.1 — DRAFT, not submitted

---

## Abstract

We define five comedian-level metrics — Legacy, Audience, Popularity, Heat,
Theory — each with published formula, inputs, and limitations, plus two
differentials (Verdict Gap, Canon Lag) computed as percentile differences
between lenses. Applied to 291 comedians across 21 regions, the metrics
reproduce known truths (Hicks beloved-but-unwatched, Hart watched-but-middling)
and surface new ones (Norm Macdonald's invisibility explained by a 9-video
official channel). The central claim: popularity and quality are different
elections, and their gap is more informative than either alone. All code,
data, and weights are public; every score carries a coverage badge. Related
work covers clip-level humour scoring (arXiv 2110.12765, humour quotient 0-4)
and special-level linguistic prediction of IMDb ratings (PMC 2024) — neither
attempts named, career-level, multi-lens metrics.

---

## 1. Introduction

Rotten Tomatoes endures because of a design decision, not data: two scores,
side by side, same methodology for every film. Tomatometer (critics) vs
Audience Score (viewers), and the gap between them is itself content
("critics hated it, audiences loved it" is a headline genre).

Comedy has no equivalent. IMDb rates specials but never aggregates to
comedians. Listicles crown without methodology. Ranker counts votes without
auditing them. We build the RT-model for stand-up: five named lenses, one
methodology doc per lens (docs/metrics/), identical computation from Lagos
to Louisville, coverage badges where data runs thin.

## 2. The five lenses

**Legacy (0-100): what history says.** Critics' Borda + prestige-weighted
awards, percentile of consensus board. Slow-moving, canon-shaped, structurally
blind to post-2017 breakouts (newest input list is 2017 — stated, not hidden).

**Audience (0-100): what viewers rate.** Standout-special IMDb mapped 5.0→0,
9.0→100, with Top-250 shrinkage (m=1000, C=7.0) for vote-base credibility.
Per-special because careers vary; shrinkage because vote counts vary 1000x.

**Popularity (0-100): who reaches eyeballs.** Blended YouTube + Netflix-hours
percentile. Explicitly distribution-weighted: YouTube-native comics
structurally win, gated comics structurally lose, removal strategies equal
invisibility. Labeled reach, never quality — and never an input to quality.

**Heat (0-100): who's hot now.** v1: views + recency proxy. v2 (on second
pulse snapshot): views/day velocity bracketed by channel size, so a Kill Tony
clip gaining 50k/wk outranks a Netflix clip gaining 200k/wk at 1% of the subs.

**Theory (0-100): how deep the engine runs.** known_bits + essays + measured
timing + doctrine, over 8. The only lens scoring the work, not its reception.
Authored until measured (flagged); operational (predicts script-readiness).

## 3. Differentials

**Verdict Gap = Popularity pct − Audience pct.** Positive: watched more than
loved (Fluffy +0.83). Negative: loved more than watched (Hicks −0.75).
Near zero: reach matches regard (Burr, Chappelle ±0.07).

**Canon Lag = Audience pct − Legacy pct.** Positive: ahead of canon (breakouts
not yet canonized). Negative: canonized above current audience love.

## 4. Cross-country comparability

Same formula everywhere; no regional curves. Coverage badges
(FULL/PARTIAL/THIN/UNRANKED) instead of silent gaps. Known skews published:
IMDb understates non-English (shrinkage penalizes low votes); awards miss
entire scenes (roadmap: Humour Awards, Edinburgh, Melbourne Barry as equal
legs); YouTube is reach-not-quality. Netflix hours are region-blind by
construction (20M hours in Brazil = 20M in the US) and partially offset
IMDb's anglo-skew. Generations are worldwide cohorts. See SITE_METRICS.md.

## 5. Validation

- **Face validity:** gap extremes match critical consensus (Hicks/Lee
  underrated, Hart overrated are uncontroversial characterizations with
  numbers attached for the first time).
- **Construct test (roadmap):** Greengross et al. 2012 found affiliative humor
  predicts success — do our operator_priors predict Audience? (ML_PIPELINES.md #5)
- **Stability:** weight sweeps + coverage-gated claims (PAPER.md §6).
- **Falsifier:** if gap rankings invert under equal-coverage subsamples, the
  metric measures coverage, not verdict — test quarterly as coverage grows.

## 6. Limitations

Single-author theory seeds; IMDb anglo-skew; awards Western-skew; YouTube
top-40 coverage; Heat v1 is proxy; Theory rewards documentation effort;
non-English comedy thin throughout. All in GAPS.md. The paper's claim is
methodological (auditable lenses + honest gaps), not empirical (these exact
numbers are v0.1 and will move with coverage).

## References

arXiv 2110.12765 (humour quotient) · Dwork et al. 2001 · IMDb Top-250 ·
LIWC/IMDb (PMC 2024) · Greengross, Martin & Miller 2012 · Kemeny 1959 ·
Serrano et al. rank-turbulence 2026 · funnygraph GAPS.md, PAPER.md, SITE_METRICS.md.
