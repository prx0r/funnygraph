# VERDICT GAP — overrated / underrated (±1.0)

**One line:** Popularity percentile MINUS Audience percentile. The product.

## Formula
`gap = PULL_pct − CROWD_pct` (both 0-1 percentiles over comics with both signals).
`canon_lag = CROWD_pct − LEGACY_pct` (ahead of canon vs canonized above love).

## Live readings (v0.1)
- Overrated: Fluffy +0.83, Sebastian +0.73 (massive reach, modest ratings)
- Underrated: Hicks −0.75, Stewart Lee −0.70 (beloved, unwatched)
- Balanced: Burr/Chappelle ±0.07 (as big as they are good)

## Justification
RT's Tomatometer-vs-Audience split proves gaps are content: the disagreement
IS the story. Our gap is computed, not vibes — two audited percentiles,
one subtraction. Requires both signals (grows with coverage).

## Limitations
- Needs both legs; single-leg comics get no gap (shown as —).
- YouTube coverage is top-40 only (sample biased toward the popular).
- Small-n percentiles noisy; badge coverage alongside.

## References
METRICS.md · GAPS.md §10 · rankings/metrics.json.
