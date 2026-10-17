# ENDPOINTS — canonical rankings as products, worked backwards to pipelines

> Define the crown first. Derive the criteria. Build only the pipelines each
> crown needs. Status per endpoint: LIVE / NEEDS / BLOCKED.

## 1. Greatest Comedian of All Time ✅ LIVE (proprietary)
- **Criteria:** HOUSE election — first-party signals only (P1 measured
  joke quality + P2 theory depth, mean of available legs; P4 arena
  reserved). External judgments (critics/IMDb/awards) display as labeled
  reference panels, never inputs.
- **Pipelines:** house_rank.py (weight-sweep intervals per position).
  Reference elections: rank_comedians.py + split_boards.py (kept, labeled).
- **Current:** Norm/Louis/Carlin (house) vs Carlin/Pryor/Rock (consensus ref).
  The gap between ours and theirs is itself product.
- **Needs:** P1 coverage 18→50+ (annotation), P4 arena votes (TOP2026).

## 2. Greatest Special of All Time ✅ LIVE
- **Criteria:** IMDb WR (Top-250 shrinkage) + Netflix hours as corroboration
  + critic-list citations as third leg.
- **Pipelines:** enrich_ratings.py + netflix_reports.py + critic_lists.py.
  Built.
- **Current:** Inside 8.6 (60k) vs Dress to Kill 8.6 (7.8k) vs Chewed Up 8.5.
  Critic citations: Chappelle (4 lists), Rock/Carlin/Murphy/Izzard (3 each).
- **Needs:** annual refresh as new lists publish.

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
- **Current:** Fluffy +0.83 / Hicks −0.70.

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

## 9. Best by Country ✅ LIVE (5 countries populated)
- **Criteria:** kings by house + local rising indies (by_country.json).
- **Current:** US (Louis #1), UK (Stewart Lee #1, Acaster/Carr/Lock/Izzard chase),
  Canada (Norm, thin), Australia (Gadsby, thin), NZ (6 rising, no kings yet).
- **Blocked on:** non-US awards legs (partially live: British/Chortle/Edinburgh
  now score), non-English IMDb coverage.

## 10. Comedian of the Week / Rising Star / New Comic 🔶 PARTIAL (boards live, velocity pending)
- **Criteria:** weekly velocity + bracket (pulse.py built + upgraded).
- **Pipelines:** discover.py --scan (registry uploads → indie drafts, KT
  fountain live: 6 verified drafts 2026-10-17) → --fetch-sets (BLOCKED:
  InnerTube denied + yt-dlp missing; needs owner cookies) → indie.py
  --score/--match-greats → rate.py --check (auto-rates) → pulse.py
  --report → rankings/spotlight.json (comedian_of_week, bracket_champs,
  rising_star, new_comic_of_week, trending_clips).
- **Live now:** spotlight.json (absolute mode: Hart 525M, Burnham 340M;
  NEW: Basketmouth 12.5M indie), indie --spotlight queue (Kam Patterson
  0.71 scored; 119 awaiting material — the sets bottleneck, quantified).
- **Blocked on:** Monday snapshot cadence (velocity needs 2+ snaps),
  cookie export for caption pulls (6 drafted indies have zero sets).

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
