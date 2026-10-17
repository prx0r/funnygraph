# LEGACY — what history says (0-100)

**One line:** percentile rank on the consensus board (the establishment
election: critics + audience + awards). What history says, all legs in.

## Formula (code truth, metrics.py)
1. Take the comedian's rank on rankings/consensus.json (weighted 3/2/1
   Borda + local Kemenization — a REFERENCE election, not ours).
2. Percentile: `100·(1 − (rank−1)/n)`.
3. `legacy_era`: same percentile on the era-adjusted board.

## Inputs
- `recognition.comedy_central_2004`, `recognition.rolling_stone_2017`
- `recognition.awards[]` (Wikidata P166, CC0)
- `generation.id` (breakthrough decade)

## Justification
Critics' lists are the only cross-comedian expert judgments with published
methodology and dates. Awards are sparse but high-authority peer/industry
signals. Combined with Borda (transparent, auditable) + local Kemenization
(Dwork et al. 2001). Era-normalization removes recency/canonization bias
(ported from music artist-era alignment research, Billboard 2026).

## Limitations
- Newest list is 2017: post-2017 breakouts score ~0 here by construction.
- Awards miss entire scenes (alt, non-US, non-English).
- Panel opacity: listicle methodology trusted, not audited.
- See GAPS.md §1, §3.

## References
Dwork et al. 2001 · Kemeny 1959 · Billboard artist-era alignment 2026 · PAPER.md §4.
