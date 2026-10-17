# LEGACY — what history says (0-100)

**One line:** critics' lists + industry awards, era-normalized. The canon's verdict.

## Formula
1. Borda points per critics' list (Comedy Central 2004, Rolling Stone 2017),
   each normalized to [0,1] by its own max, summed (max 2.0).
2. Awards: Mark Twain 3.0, Grammy 2.0, Kennedy 2.5, Emmy/Peabody 1.5, other 1.0.
3. Weighted sum (critics 3, awards 1) → percentile of board → 0-100.
4. Era-normalized variant: within-generation z-scores first (PAPER.md §4.3).

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
