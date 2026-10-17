# ARENA — blind pairwise battles for TOP 2026 (design v1)

> The leg nobody else has: blind A/B clip votes → Bradley-Terry scores.
> Infrastructure exists (characters repo: audition stage, battle mode, Elo/Wilson).
> This doc wires it to TOP 2026.

## Battle format
- 60-90s clips, audio-first (no thumbnails/names visible during vote).
- Random pairings ACROSS generations + scenes (Pryor vs Gillis is a feature).
- Voter picks winner or Pass. No comments during vote (post-vote discussion ok).
- n≥30 votes before a pairing counts (Wilson interval).

## Anti-brigading
- Rate-limited votes per voter per day.
- No campaign links (no "vote for X" — battles are random, can't target).
- Outlier detection: voters with >85% one-sided picks flagged.
- Verified voters only for TOP 2026 (arena regulars + critic survey panel).

## Scoring
- Bradley-Terry global scores via Zermelo iteration (Newman 2023).
- Output feeds rank_comedians.py leg 4 (weight TBD by coverage).
- Weekly leaderboard published with n per pairing (transparency).

## Pairing strategy (to bootstrap)
- Phase 1: kings vs kings (calibrate the scale — Pryor vs Carlin anchors top).
- Phase 2: kings vs indies (the discovery engine — "unknown beats legend" moments).
- Phase 3: indies vs indies (spotlight queue ordered by BT score).

## Integration
- Battle votes → `rankings/arena.json` {a, b, a_wins, b_wins, n}.
- rank_comedians.py reads arena.json as 4th leg when present.
- Characters repo runs the app; funnygraph consumes the votes. Boundary kept.
