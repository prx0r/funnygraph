# RANKINGS — definitive comedian rankings: theory, prior art, our design

> Can we have THE definitive comedian ranking? Short answer: no (Arrow proved
> it). Long answer: we can build the best-measured consensus with honest
> uncertainty — and that's a better product than any listicle.

## Has anyone tried?

| Attempt | Method | Problem |
|---|---|---|
| Comedy Central 100 (2004) | panel vote, one snapshot | frozen in 2004; Louis CK #97 (now consensus top-5) |
| Rolling Stone 50 (2017) | critics vote, one snapshot | Norm/Attell/Giraldo absent; recency bias admitted in the piece |
| Paste 50 (2017) | critics + notable works | same-era snapshot, different taste |
| Ranker.com | endless crowd votes | popularity contest, brigading, no methodology |
| IMDb per-special ratings | audience cardinal scores | special-level not comedian-level; vote-count bias toward recent |
| Our arena (characters repo) | blind pairwise votes + Elo/Wilson | small-n, single-audience, needs n≥30 per pairing |

Nobody has done **principled aggregation across critics + audience + awards
+ pairwise votes** for comedians. That's the gap.

## Why "definitive" is impossible (the theory)

**Arrow's impossibility theorem (1951):** no rank aggregation rule satisfies
all fairness criteria at once. Any "definitive" ranking makes a tradeoff —
the honest move is to name the tradeoff.

**Kemeny (1959)** is the gold standard: the ranking minimizing total
Kendall-tau distance to all input rankings = the geometric median = MLE under
the Mallows noise model. Problem: NP-hard (Bartholdi 1989), still open/hard
even for 3 voters. At 181 comedians, exact Kemeny is hopeless — but **local
Kemenization** (Dwork et al. 2001): start from Borda, hill-climb single swaps.
Cheap, auditable, near-optimal.

**Bradley-Terry (1952)** converts pairwise comparisons to skill scores via
Zermelo's iteration (Newman 2023 gives a fast async variant). Perfect for our
arena votes later — and listicles *imply* pairwise outcomes (if A ranks above
B on a list, that's an A-beats-B observation).

**IMDb Top 250 formula** (the industry standard for combining rating + votes):
`WR = (v/(v+m))·R + (m/(v+m))·C` — shrinks low-vote specials toward the mean.
We use this for the audience leg.

## Our design: consensus + uncertainty, not a crown

Four voter legs, each a partial ranking over the 181:

1. **Critics leg** — CC2004 + RS2017 (+ Paste when scraped). Unranked comics
   sit below ranked ones per list (Dwork partial-list rule), EXCEPT comics
   who postdate the list (Gillis can't be on a 2004 list) — those are
   *missing*, not *low*. This distinction is the whole ballgame.
2. **Audience leg** — IMDb standout-special WR per comedian (Top-250 formula,
   m=1000 votes). Cardinal → ranking.
3. **Awards leg** — prestige-weighted: Mark Twain Prize > Grammy Best Comedy
   Album > Emmy. Binary-ish signals, high authority, low coverage.
4. **Arena leg** (later) — our own blind pairwise votes → Bradley-Terry scores.

Aggregation: Borda per leg → normalize → weighted sum (critics 3, audience 2,
awards 1 — weights published, tunable) → local Kemenization hill-climb →
**consensus ranking + per-position disagreement** (how much the legs fought).

Era adjustment: separate within-generation ranks (pioneers don't compete with
twenties) + a cross-era board with the temporal caveat stated, not hidden.

## What we publish

- `rankings/consensus.json` — the board, with per-comic leg breakdown
- `rankings/disagreement.json` — where the legs fight (most interesting content:
  "critics say X, audiences say Y")
- `rankings/by_generation.json` — seven era boards
- The trajectory (CC2004 → RS2017 → IMDb now) as the "rankings through
  the years" view — rise/fall/stable per comic.

## Anti-goals

- No single number without uncertainty. No crown without the fight shown.
- No recency blindness: a 2024 breakout doesn't outrank Pryor on one special.
- No listicle cosplay: every weight, voter, and missing-data rule is in the repo.
