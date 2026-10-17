# OVERRATED — the verdict in plain English

**One line:** massively overrated / overrated / accurately rated /
underrated / massively underrated. Bounded, median-centered, no math required.

## Bands (from v0.1 distribution, n=64, median +0.08)

| Band | Range | Share | Examples |
|---|---|---|---|
| massively overrated | ≥ +0.50 | ~8% | Fluffy +0.83, Sebastian +0.73 |
| overrated | +0.20 to +0.50 | ~25% | Gervais +0.67, Noah +0.60 |
| accurately rated | ±0.20 | ~55% | Burr/Chappelle ±0.07 |
| underrated | −0.20 to −0.50 | ~10% | Izzard −0.38, Vir Das −0.36 |
| massively underrated | < −0.50 | ~5% | Hicks −0.71, Stewart Lee −0.64 |

Numeric `gap_value` kept alongside for transparency; the band is the display.

**Formula:** `gap_value = Popularity pct − Audience pct`, then banded above.

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
