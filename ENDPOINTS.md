# ENDPOINTS — canonical rankings as products, worked backwards to pipelines

> Define the crown first. Derive the criteria. Build only the pipelines each
> crown needs. Status per endpoint: LIVE / NEEDS / BLOCKED.

## 1. Greatest Comedian of All Time ✅ LIVE
- **Criteria:** consensus across critics + audience + awards, era-normalized.
- **Pipelines:** rank_comedians.py (Borda → Kemenization → z-scores). All built.
- **Current:** Pryor/Carlin/Rock (raw) · Chappelle/Hicks/Carlin (era-adjusted).
- **Needs:** awards leg depth (bios running), arena pairwise (TOP2026).

## 2. Greatest Special of All Time ✅ LIVE
- **Criteria:** IMDb WR (Top-250 shrinkage) + Netflix hours as corroboration.
- **Pipelines:** enrich_ratings.py + netflix_reports.py. Built.
- **Current:** Inside 8.6 (60k) vs Dress to Kill 8.6 (7.8k) vs Chewed Up 8.5.
- **Needs:** critic special lists (Paste/RS special ranks) as third leg.

## 3. Best Special by Decade ✅ LIVE (just built)
- **Criteria:** top WR per decade from specials.json.
- **Current:** 70s Pryor Live in Concert · 80s Delirious · 90s Dress to Kill ·
  00s Chewed Up · 10s Sticks & Stones · 20s Inside.
- **Needs:** nothing (recompute on new specials).

## 4. Kings of Each Type ✅ LIVE
- **Criteria:** legacy-primary within humor type (rankings/by_type.json).
- **Current:** 13 types crowned (Rock/observational … Silverman/provocateur).

## 5. Most Overrated / Underrated ✅ LIVE
- **Criteria:** Verdict Gap bands (docs/metrics/overrated.md).
- **Current:** Fluffy +0.83 / Hicks −0.75.

## 6. Breakout of the Year 🔶 NEEDS 2026 legs
- **Criteria:** rating velocity + first-time-ranked + arena + critic survey.
- **Pipelines:** pulse velocity (needs snapshot cadence), BALLOT_2026, ARENA_BALLOT.
- **Blocked on:** ballot distribution (owner), arena votes (characters repo).

## 7. Funniest Bit Ever 🔶 NEEDS bit-level data
- **Criteria:** quote-back rate + timestamp-laugh density + arena bit battles.
- **Pipelines:** F3/F4 specced (fanbase.py partial: 68 lexicon markers, GOAT calls).
- **Blocked on:** comment breadth (240 clips × 100), transcript↔comment fuzzy match.

## 8. Best by Generation ✅ LIVE
- **Criteria:** within-generation rank (rankings/by_generation.json).
- **Current:** 7 era boards.

## 9. Best by Country / Continent ✅ LIVE (structure) / 🔶 data thin
- **Criteria:** region-filtered consensus + local awards legs.
- **Pipelines:** rankings/by_continent.json built; regional awards missing.
- **Blocked on:** non-US awards legs, non-English IMDb coverage.

## 10. Comedian of the Week / Rising Star 🔶 NEEDS pulse cadence
- **Criteria:** weekly velocity + bracket + sentiment (pulse.py built).
- **Blocked on:** Monday snapshot cadence (automatic), subs backfill (quota).

## Pipeline dependency map
```
IMDb match ──→ specials board ──→ decade boards, GOAT special, CROWD metric
Netflix hours ─→ viewership corroboration, PULL metric
Critics lists ─→ CANON leg, trajectories
Awards (bios) ─→ prestige leg, recognition
YouTube stats ─→ PULL, pulse velocity, HEAT
Comments ──→ quote-backs, laugh maps, GOAT-debate votes (F3/F4/F5)
Arena votes ─→ Bradley-Terry leg, Breakout, Bit battles
Theory graphs → CRAFT metric, episode scripts, agent judges
```
Build in dependency order. No pipeline without a consuming endpoint.
