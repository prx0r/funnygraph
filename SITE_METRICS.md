# SITE METRICS — the Rotten Tomatoes model for comedy, global by design

> RT shows Tomatometer + Audience Score side by side, same methodology for
> every film in every country. Our panels do the same for every comedian in
> every region. A score means the same thing in Lagos as in Louisville —
> and when it can't (coverage gaps), the badge says so.

## The panel (per comedian page)

```
LEGACY 87  |  AUDIENCE 76  |  POPULARITY 92  |  HEAT 64  |  THEORY 71
Overrated (+0.21) · LEGACY LAG -0.08 · coverage: FULL
Generation: tens · Region: US · Scene: podcast
Standout special: Beautiful Dogs (2023, IMDb 8.1)
Closest match: Theo Von 0.43 · For fans of: Carlin, Burr
```

## Cross-country comparability rules

1. **Same formula everywhere.** LEGACY/AUDIENCE/POPULARITY/THEORY compute identically
   regardless of region. No regional curves, no hidden adjustments.
2. **Coverage badges, not silent gaps.** Each score carries n (specials rated,
   clips tracked, awards counted). FULL (3+ legs) / PARTIAL (2) / THIN (1) /
   UNRANKED (0 — shown, never ranked).
3. **IMDb is global-ish but US-skewed.** Non-English specials get fewer votes;
   the Top-250 shrinkage (m=1000) already penalizes them. Documented limitation:
   AUDIENCE understates non-English comics. Netflix hours (platform-reported,
   region-blind) partially offsets — a special watched 20M hours in Brazil
   counts the same as 20M in the US.
4. **Awards are Western-skewed.** Grammys/Mark Twain/Emmys miss entire scenes
   (Nigeria's Humour Awards, Edinburgh Comedy Award, Melbourne Barry). Roadmap:
   add regional awards as equal-weight legs (P166 already supports any award).
5. **YouTube is distribution-skewed.** Labeled POPULARITY (reach), never quality.
   Removal-strategy and platform-native confounds documented per comic where known.
6. **Era-normalization is global.** Generations are worldwide cohorts (a tens
   comic in Lagos competes with tens in Louisville). Regional scenes may lag
   global eras — noted, not corrected (correcting would erase real differences).

## Metric definitions (frozen v1)

- LEGACY 0-100: critics Borda + awards, percentile of consensus board.
- AUDIENCE 0-100: standout IMDb mapped (5.0→0, 9.0→100).
- POPULARITY 0-100: blended YouTube + Netflix-hours percentile.
- HEAT 0-100: velocity percentile (needs 2+ pulse snapshots; else views+recency).
- THEORY 0-100: theory depth (bits + essays + measured timing + doctrine) / 8.
- GAP: POPULARITY pct − AUDIENCE pct. LEGACY LAG: AUDIENCE pct − LEGACY pct.

## What "definitive" means here

Not one number — five auditable scores + differentials + coverage badges,
computed identically from Lagos to Louisville. The methodology is public;
anyone reruns our code and gets our board. That is the RT-model promise:
same ruler, every movie, every country.
