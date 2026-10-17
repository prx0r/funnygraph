# Consensus Ranking of Stand-Up Comedians Across Eras
## A principled aggregation of critics, audiences, and awards with honest uncertainty

**funnygraph working paper v0.1 — DRAFT, not submitted**

---

## Abstract

We construct the first principled consensus ranking of stand-up comedians
(n=179) from four independent voter legs: published critics' lists (Comedy
Central 2004, Rolling Stone 2017), audience ratings (IMDb standout-special
weighted ratings, Top-250 formula), industry awards (Wikidata: Mark Twain
Prize, Grammys, Emmys), and a transparent aggregation rule (Borda per leg →
weighted sum → local Kemenization). The central methodological contribution
is **era-normalized comparison**: comedians are scored against their own
generation's baseline (z-scores within breakthrough cohort) before cross-era
comparison, eliminating the structural advantages of recency (more specials,
more votes, living memory) and canonization (older lists can't rank the
unborn). We publish the board, per-position disagreement across legs, and
seven within-generation boards. All inputs, weights, missing-data rules, and
code are public. No prior academic work attempts comedian ranking; existing
literature covers humor detection (SCRIPTS, StandUp4AI, Open Mic) and
performer psychology (Greengross et al. 2012), never cross-performer ranking.

---

## 1. Introduction

"Who's the greatest stand-up of all time?" is among the most argued questions
in popular culture — and the least measured. Existing answers are single
snapshots: a panel vote frozen in 2004 (Comedy Central 100), a critics' vote
frozen in 2017 (Rolling Stone 50), an endless popularity contest (Ranker), or
per-special audience scores (IMDb) that never aggregate to the comedian level.
Each is defensible alone; none combines evidence; none states uncertainty.

We argue the right product is not a crown but a **consensus with disagreement
shown**: a board where every position carries its leg breakdown, every weight
is published, and the places where critics and audiences fight are the most
prominent feature, not a footnote.

## 2. Related work

**Computational humor** works on detection, never ranking: SCRIPTS (LREC 2022,
90 scripts / 68 comics, laugh-marker classification), StandUp4AI (EMNLP 2025,
3617 videos, laughter labels), Open Mic funniness scores, LLM humor-detection
metrics (CMCL 2025). None ranks performers against each other.

**Performer psychology** (Greengross, Martin & Miller 2012) finds professional
success predicted positively by affiliative humor and negatively by
self-defeating humor (n=31 comics) — a result our operator-prior features can
test at scale (§6).

**Cross-era comparison** is developed furthest in music: artist–era alignment
frameworks score artists against era baselines on profile-shape similarity and
contrast ratio (Billboard Hot 100, six decades); rank-turbulence divergence
quantifies chart reshuffling across time. We port the era-baseline idea to
comedy (§4.3).

**Rank aggregation theory**: Kemeny (1959) optimal consensus is the MLE under
the Mallows noise model but NP-hard (Bartholdi et al. 1989); Dwork et al.
(2001) give the practical recipe — Borda start, local Kemenization hill-climb
— plus the partial-list rule (unranked items sit below ranked ones) that we
extend with the postdate distinction (§4.2). Bradley-Terry (1952) with
Zermelo iteration (Newman 2023) handles our future pairwise arena votes.
Arrow (1951) proves no perfect rule exists; we publish our tradeoff.

## 3. Data

| Source | n | Type | Years | License/cost |
|---|---|---|---|---|
| Comedy Central 100 | 100 ranked | critics panel | 2004 | public list |
| Rolling Stone 50 | 50 ranked | critics vote | 2017 | public list |
| IMDb title.ratings + title.basics | 83,292 comedy entries w/ votes | audience cardinal | to 2026 | free public datasets |
| Wikidata (P569/P19/P166) | 181 bios, awards w/ years | structured facts | — | CC0, free API |
| funnygraph transcripts | 383 specials, ~21M words | text | 1970s–2026 | mixed (fair-use research) |

Coverage: 181 comedians, 225 IMDb-matched specials, 91+ bios, 44 listicle-ranked.

## 4. Method

### 4.1 Voter legs

- **Critics leg.** Borda points per list (top = most), each list normalized to
  [0,1] by its own max, summed. Two lists → max 2.0.
- **Audience leg.** Per comedian, take the standout (or best) special; apply
  the IMDb Top-250 shrinkage `WR = (v/(v+m))·R + (m/(v+m))·C` with m=1000,
  C=7.0; rank comedians by WR; Borda, normalized to [0,1].
- **Awards leg.** Prestige weights: Mark Twain 3.0, Grammy 2.0, Kennedy 2.5,
  Emmy/Peabody 1.5, others 1.0. Summed per comedian, normalized to [0,1].

### 4.2 Missing-data rules (the core contribution)

A list is a partial ranking. Dwork's rule places unranked items below ranked
ones — but only when the item *could* have been ranked. We distinguish:

- **Postdate (missing):** comedian's generation starts after the list year
  (e.g. Gillis vs a 2004 list). Excluded from that leg's denominator —
  neither helped nor hurt.
- **Contemporary-but-unranked (low):** active before the list year, absent.
  Scores 0 on that list (Dwork rule). This is a real signal: the panel
  considered the era and passed.

Generation = breakthrough decade (first national hour/TV), not birth year —
Seinfeld (b.1954, breakthrough 1989) and Rock (b.1965, breakthrough 1990)
share a generation by construction.

### 4.3 Era normalization

Raw cross-era comparison is rigged: newer comics have more specials, more
IMDb votes, and living memory; older comics have canonization and
survivorship. Following the music-era-alignment approach, we compute
**within-generation z-scores** per leg before cross-era comparison:

`z(leg, comic) = (leg(comic) − mean(leg | generation)) / sd(leg | generation)`

The published board uses raw weighted sums (interpretable); the
era-adjusted board uses z-scores (fair). Both ship; the gap between them is
itself a finding (who benefits from their era?).

### 4.4 Aggregation

Weighted sum (critics 3, audience 2, awards 1 — published, tunable), then
local Kemenization: hill-climb adjacent swaps against total Kendall distance
to the three legs' implied orders (≤6 passes). Output: consensus order +
per-comic leg breakdown + disagreement (s.d. across legs' normalized scores).

## 5. Results (v0.1)

Top 5: Carlin, Pryor, Rock, Seinfeld, R. Williams. Full board +
seven generation boards + top-30 disagreement board in `rankings/`.
Notable disagreements (critics vs audience legs) flagged per comic.

## 6. Validation roadmap

- **Greengross test:** do our operator_priors predict IMDb WR the way HSQ
  styles predict success? (affiliative+ / self-defeating− at n=181 vs n=31)
- **Listicle prediction:** hide RS2017, predict it from CC2004 + IMDb —
  measures how much canonization is predictable vs genuinely new judgment.
- **Inter-leg agreement:** Kendall-tau between legs; awards leg is sparse —
  report coverage-weighted confidence per position.
- **Sensitivity:** weight sweeps (2,2,2 / 4,1,1 / critics-only) — positions
  stable across sweeps are claims; unstable ones are questions.

## 7. Limitations

Single-author theory seeds (hypothesis until measured); IMDb vote brigading
and recency bias partially but not fully corrected; awards leg sparse for
alt/underground comics (systematically undervalues them — stated, not
hidden); no non-English comedy coverage yet; pairwise arena votes not yet
integrated (Bradley-Terry leg reserved).

## References

Arrow 1951 · Attardo & Pickering 2011 · Attardo & Raskin (GTVH) ·
Bartholdi, Tovey & Trick 1989 · Bradley & Terry 1952 · Dwork et al. 2001 ·
Greengross, Martin & Miller 2012 · Kemeny 1959 · McGraw & Warren 2010 ·
Mittal et al. 2021 (Open Mic) · Newman 2023 (Bradley-Terry) ·
StandUp4AI (EMNLP 2025) · Turano & Strapparava 2022 (SCRIPTS) ·
Jentzsch & Kersting 2023/CMCL 2025 (LLM humor metric) ·
Billboard artist-era alignment 2026 · rank-turbulence divergence 2026.
