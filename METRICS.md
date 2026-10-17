# METRICS — funnygraph proprietary scores

> Rotten Tomatoes has Tomatometer vs Audience Score. We have five lenses,
> and the gaps between them are the product. Views ≠ funny — but views
> MINUS funny = overrated, and funny MINUS views = underrated.

## The suite (all 0-100)

| Metric | Question | Inputs |
|---|---|---|
| **CANON** | What does history say? | critics ranks + awards, era-normalized |
| **CROWD** | What do audiences say? | IMDb standout WR, Top-250 shrinkage |
| **PULL** | Who reaches eyeballs? | YouTube totals + Netflix hours (distribution-weighted, labeled) |
| **HEAT** | Who's hot NOW? | view velocity + recent-special momentum (pulse) |
| **CRAFT** | How deep is the engine? | theory depth: known_bits + measured timing + operator diversity |

## The differentials (the product)

| Differential | Formula | Meaning |
|---|---|---|
| **GAP** | PULL pct − CROWD pct | +overrated / −underrated |
| **CANON LAG** | CROWD pct − CANON pct | +ahead of canon (breakout not yet canonized) / −canonized above audience love |
| **HEAT CHECK** | HEAT pct − CROWD pct | +moment outrunning body of work / −body of work outrunning moment |

Live examples (v0.1, n=31 with both signals):
- Hart GAP +0.37 (most overrated by the metric — biggest reach, #30 quality)
- Hicks GAP −0.86, Stewart Lee −0.78 (most underrated — beloved, unwatched)
- Burr −0.07, Chappelle −0.05 (balanced — as big as they are good)

## Rules

1. Never blend lenses into one number without showing components.
2. PULL is labeled distribution-weighted everywhere it appears.
3. HEAT needs 2+ pulse snapshots (velocity); until then it's views+recency.
4. CRAFT is theory-authored until timing measurement scales — flagged as such.
5. All scores recomputed weekly (pulse) and yearly (canon); histories kept
   for trajectory charts.
