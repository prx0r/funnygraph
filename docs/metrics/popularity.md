# POPULARITY — who reaches eyeballs (0-100)

**One line:** YouTube totals + Netflix hours, blended percentile. Reach, NOT quality.

## Formula
1. YouTube: total views across tracked official clips → percentile.
2. Netflix: total What-We-Watched hours across specials → percentile.
3. Mean of available percentiles → 0-100.

## Inputs
- `youtube.total_views` (Data API, official channels only — registry, no search)
- `netflix_viewership.hours` (7 official reports 2023H1-2026H1)

## Justification
Reach is worth measuring separately from quality — conflating them is the
original sin of every GOAT list (see fit_weights.py: averaging legs destroys
signal, GAPS.md). YouTube measures clip-distribution success; Netflix hours
measure special watches (platform-reported, region-blind).

## Limitations (stated on every display)
- Distribution-weighted: YouTube-native comics structurally win; gated comics lose.
- Removal strategy = invisibility, not unpopularity.
- Accumulation bias (2008 vs 2024 clips) — HEAT velocity partially corrects.
- NEVER an input to quality judgments.

## References
GAPS.md §8 · TOP2026.md (popularity vs quality split).
