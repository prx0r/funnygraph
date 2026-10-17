# SITE METRICS — the Rotten Tomatoes model for comedy, global by design

> RT shows Tomatometer + Audience Score side by side, same methodology for
> every film in every country. Our panels do the same for every comedian in
> every region. A score means the same thing in Lagos as in Louisville —
> and when it can't (coverage gaps), the badge says so.

## The panel (per comedian page)

```
HOUSE 100 · FULL · ours (measured jokes + theory depth), sweep [1,3]
LEGACY 87  |  AUDIENCE 76  |  POPULARITY 92  |  HEAT —  |  FUNNIER 100
Overrated (+0.21) · LEGACY LAG -0.08
Generation: tens · Region: US · Scene: podcast
Standout special: Beautiful Dogs (2023, IMDb 8.1)
Reference: consensus #25 · canon #38 · people's #18 · era #39 (ref)
Closest match: Theo Von 0.43 · For fans of: Carlin, Burr
```

HOUSE is the headline (proprietary election — the only number that is
ours). The five lenses and external boards display alongside, labeled:
lenses measure reception + documentation; consensus/canon/people's/era
are reference elections (ref:true), never inputs to HOUSE. Zero-leg
profiles show a flagged provisional headline and no house rank.

## Cross-country comparability rules

1. **Same formula everywhere.** LEGACY/AUDIENCE/POPULARITY/THEORY compute identically
   regardless of region. No regional curves, no hidden adjustments.
2. **Coverage badges, not silent gaps.** HOUSE coverage counts
   proprietary legs only: FULL (measured jokes + theory depth) /
   PARTIAL (one leg) / UNRANKED (none — provisional headline, no rank).
   Each lens carries its own n (specials rated, clips tracked, awards
   counted). Reference boards show external ranks verbatim, labeled ref.
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
   YouTube is our SOLE measurement source (velocity, comments, embeds,
   captions) — no other platform offers legal time-series APIs (TikTok
   Research is gated academic; IG Graph covers own accounts only).
   TikTok/IG handles live on profiles as `socials{}`: discovery evidence
   + display ("elsewhere" rails), NEVER metrics. A million TikTok
   followers moves no number; it only says where to look.
6. **Era-normalization is global.** Generations are worldwide cohorts (a tens
   comic in Lagos competes with tens in Louisville). Regional scenes may lag
   global eras — noted, not corrected (correcting would erase real differences).

## Metric definitions (frozen v2 — v1 kept in git history)

- HOUSE 0-100: percentile on the proprietary board (P1 measured joke
  quality + P2 theory depth, mean of available legs; P4 arena reserved).
  Sweep interval published. The headline; the only number that is ours.
- LEGACY 0-100: percentile rank on the consensus board (external critics +
  audience + awards). Reference: what history says.
- AUDIENCE 0-100: standout IMDb mapped (5.0→0, 9.0→100), raw display.
  Reference: what viewers rate.
- POPULARITY 0-100: blended YouTube + Netflix-hours percentile.
  Reference: reach, never quality, never an input.
- HEAT 0-100: UNIMPLEMENTED (null until pulse cadence). No proxy shipped.
- FUNNIER 0-100: the house percentile — our proprietary rating (P1 measured
  joke quality + P2 theory depth). Replaces THEORY at presentation; theory
  depth still feeds P2 and stays in graph metrics + theory_content.json.
- GAP: POPULARITY pct − AUDIENCE pct. LEGACY LAG: AUDIENCE pct − LEGACY pct.

## What "definitive" means here

Not one number — one proprietary headline plus five auditable lenses,
differentials, coverage badges, and labeled reference elections,
computed identically from Lagos to Louisville. The methodology is public;
anyone reruns our code and gets our board. That is the RT-model promise:
same ruler, every movie, every country — and our ruler measures only
what we measured.
