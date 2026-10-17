# Five Lenses: Auditable Multi-Signal Metrics for Stand-Up Comedy

## funnygraph working paper v0.2 — DRAFT, not submitted

Synced to code 2026-10-17 (metrics.py). Corrects two v0.1 false claims:
crowd score uses the RAW standout rating (not WR shrinkage); HEAT is
unimplemented (None) pending pulse cadence — the v1 proxy was spec, not code.

---

## Abstract

We define five comedian-level metrics — Legacy, Audience, Popularity, Heat,
Theory — each with published formula, exact code reference, inputs, and
limitations, plus two differentials (Verdict Gap, Canon Lag) computed as
percentile differences between lenses. Applied to 293 comedians across 21
regions, the metrics reproduce known truths with numbers attached for the
first time (Hicks −0.70 underrated, Iglesias +0.83 overrated, median +0.087,
n=64) and surface new ones (Norm Macdonald's invisibility explained by a
9-video official channel). The central claim: popularity and quality are
different elections — inter-leg τ(critics,audience) = +0.177 — and their
gap is more informative than either alone. All code, data, and weights are
public; every score carries a coverage badge. Related work covers
clip-level humour scoring and special-level linguistic prediction of IMDb
ratings — neither attempts named, career-level, multi-lens metrics.

---

## 1. Introduction

Rotten Tomatoes endures because of a design decision, not data: two scores,
side by side, same methodology for every film. Tomatometer (critics) vs
Audience Score (viewers), and the gap between them is itself content.

Comedy has no equivalent. IMDb rates specials but never aggregates to
comedians. Listicles crown without methodology. Ranker counts votes without
auditing them. We build the RT-model for stand-up: five named lenses, one
methodology doc per lens (docs/metrics/), identical computation from Lagos
to Louisville, coverage badges where data runs thin. FORMULA, not vibes:
every lens below names its exact computation in metrics.py.

## 2. The five lenses (with exact formulas)

**Legacy (0–100): what history says.** Percentile rank on the consensus
board (metrics.py `pct()`): `100·(1 − (rank−1)/n)`. Slow-moving,
canon-shaped, structurally blind to post-2017 breakouts (newest critics
input 2017 — stated, not hidden). `legacy_era` = same percentile on the
era-adjusted board.

**Audience (0–100): what viewers rate.** RAW standout-special IMDb rating
mapped 5.0→0, 9.0→100 (`(r−5)·25`, clipped). Precision note: this is NOT
the WR-shrunk audience leg used for ranking — deliberately. Shrinkage
exists to order low-vote items fairly; a 0–100 display score should show
what viewers said, with vote-base credibility carried separately by the
coverage badge. Conflating the two was a v0.1 documentation error;
the code always showed raw. Whether display should ALSO shrink is open
(v0.3: show both, let the gap speak).

**Popularity (0–100): who reaches eyeballs.** Mean of per-source reach
percentiles among tracked comics: YouTube total-views rank percentile
(57 channels) + Netflix-hours rank percentile (graphs'
`netflix_viewership.hours`). Explicitly distribution-weighted:
YouTube-native comics structurally win, gated comics structurally lose,
removal strategies equal invisibility. Labeled reach, never quality —
and never an input to quality (POPULARITY does not enter any ranking).

**Heat (0–100): who's hot now.** UNIMPLEMENTED (code: None). Spec'd in
docs/metrics/heat.md: v1 views+recency proxy → v2 views/day velocity
bracketed by channel size once 2+ pulse snapshots exist. We ship the
column with nulls rather than a proxy we can't defend — a metric that
only moves weekly must not be faked from a snapshot. Blocker: Monday
pulse cadence.

**Theory (0–100): how deep the engine runs.** `100·depth/8` where depth =
min(3, known_bits) + min(2, essay_seeds/2) + 2 if any timing_measured set +
1 if doctrine_hypothesis. The only lens scoring the work, not its
reception. Authored until measured (flagged); rewards documentation
effort — stated as a limitation, not a secret (a well-documented
mediocrity outscores an undocumented genius; coverage badges mitigate).

## 3. Differentials

**Verdict Gap = Popularity pct − Audience pct** (percentile units, −1..1).
Positive: watched more than loved. Negative: loved more than watched.
Bands from the v0.2 distribution (n=64, median +0.087): ≥+0.50 massively
overrated; +0.20 overrated; ±0.20 accurately rated (~60%); −0.20
underrated; <−0.50 massively underrated. Current: Iglesias +0.83 (most
overrated; Hart +0.525 the famous case), Hicks −0.70, Stewart Lee −0.612 (most underrated), Burr
+0.114, Chappelle +0.102 (balanced).

**Canon Lag = Audience pct − Legacy pct.** Positive: ahead of canon
(breakouts not yet canonized). Negative: canonized above current audience
love (Hart −0.43).

## 4. Cross-country comparability

Same formula everywhere; no regional curves. Coverage badges
(FULL/PARTIAL/THIN/UNRANKED) instead of silent gaps. Known skews
published: IMDb understates non-English (Top-250 shrinkage penalizes low
votes); awards miss entire scenes (roadmap: Humour Awards, Edinburgh
Comedy Award, Melbourne Barry as equal legs); YouTube is reach-not-quality.
Netflix hours are region-blind by construction and partially offset IMDb's
anglo-skew. Generations are worldwide cohorts. See SITE_METRICS.md.

## 5. Validation

- **Face validity:** gap extremes match critical consensus — now with
  numbers attached for the first time.
- **Discriminant validity (new v0.2):** τ(critics,audience) = +0.177
  (agreement.json) — the lenses measure different things, which is the
  license for the gap product. A gap between identical lenses would be
  noise; ours is signal.
- **Construct test (FAILED, published):** Greengross et al. (2012) predict
  affiliative styles succeed — our operator_priors do not predict Audience
  (r=−0.05, M5). The theory lens measures documentation depth, not joke
  quality; we do not claim otherwise.
- **Stability:** only 15/178 consensus positions stable across 71 regimes —
  gap verdicts inherit this; banded verdicts (±0.20 accurate band) are
  robust by construction, exact gap_values are not claims.
- **Falsifier:** if gap rankings invert under equal-coverage subsamples,
  the metric measures coverage, not verdict — test quarterly as coverage
  grows.

## 6. Limitations

Single-author theory seeds; IMDb anglo-skew; awards Western-skew; YouTube
top-40 coverage; Heat unimplemented; Theory rewards documentation effort;
crowd-display-vs-WR-rank duality unresolved; non-English comedy thin
throughout. All in GAPS.md. The paper's claim is methodological (auditable
lenses + honest gaps), not empirical (these exact numbers are v0.2 and will
move with coverage).

## References

- Dwork, C., Kumar, R., Naor, M. & Sivakumar, D. (2001). Rank aggregation
  methods for the Web. *Proc. WWW10.*
- Greengross, Martin & Miller (2012) — VERIFY full citation.
- IMDb Top-250 formula (help.imdb.com); Rotten Tomatoes methodology.
- James, W. & Stein, C. (1961). Estimation with quadratic loss. *Proc.
  Fourth Berkeley Symp.* (shrinkage precedent for WR).
- Kemeny, J.G. (1959). Mathematics without numbers. *Daedalus*, 88(4).
- funnygraph GAPS.md, PAPER.md (v0.2), SITE_METRICS.md, agreement.json.
