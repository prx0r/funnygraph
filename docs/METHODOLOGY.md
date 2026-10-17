# METHODOLOGY — how the best is calculated: IMDb, RT, Metacritic, Letterboxd, ours

> Every major ranking system, side by side with ours. Steal what works,
> document what differs, state what we can't replicate.

## IMDb Top 250 (films)
- **Formula:** `WR = (v÷(v+m))×R + (m÷(v+m))×C` — true Bayesian estimate
  (credibility theory: m imaginary votes at the mean).
- **Parameters:** m=25,000 minimum, C≈7.0 global mean, **regular voters only**
  (criteria undisclosed).
- **What we steal:** the formula shape. Shrinkage toward the mean for low-n
  is the correct answer to vote-count bias.
- **What we can't replicate:** regular-voter weighting (no voter data),
  m=25,000 scale (specials max ~350k votes; films do millions).
- **Our calibration:** m=500, C=7.50 (corpus mean of 99 rated specials;
  median votes 3,747; keeps 75/99 eligible). Documented in code.

## Rotten Tomatoes
- **Tomatometer:** % of approved critics rating fresh (binary, min review counts).
- **Audience Score:** % of users rating 3.5+/5.
- **What we steal:** the two-score display + the gap as content. Binary
  approval is robust where means are gameable.
- **What differs:** we use cardinal IMDb ratings (richer) instead of binary
  fresh/rotten; our "critics" are two listicles, not hundreds of reviews.
- **Roadmap:** approval-rate variant per comic (% specials ≥7.5) as a second
  audience lens — cheap to add, harder to game than means.

## Metacritic
- **Method:** weighted average of critic scores, weights undisclosed.
- **Lesson (negative):** undisclosed weights = unauditable. We publish ours.
  Metascore's opacity is what not to do.

## Letterboxd Top 250
- **Method:** plain weighted average, community-voted, no public formula.
- **Lesson:** community trust substitutes for methodology — works at their
  scale, wouldn't survive our auditability promise.

## Ours (funnygraph)
| Decision | Choice | Why |
|---|---|---|
| Audience formula | IMDb WR shape, m=500, C=7.5 | calibrated to specials corpus (not films) |
| Critics aggregation | Borda + local Kemenization | transparent, auditable (vs Metacritic opacity) |
| Display model | RT two-score + gap | gaps are content, proven |
| Missing data | postdate=missing, contemporary-absent=low | Dwork partial-list rule + temporal fix |
| Era handling | within-generation z-scores | ported from music era-alignment |
| Weights | 3/2/1 published, tunable | fitted result (0.658 < 0.692) disclosed; split boards preferred |
| Uncertainty | disagreement per position, coverage badges | no crown without the fight shown |

## What's missing vs the industry
1. Regular-voter equivalent (bot/brigade resistance) — no voter data, stated.
2. Review-count minimums for board eligibility (IMDb: 25k; ours: none yet —
   recommend specials≥500 votes + comics with 2+ legs for ranked boards).
3. Demographic breakdowns (IMDb has them; we can't).
4. Time-decay (all systems underweight it; our HEAT is the start).
