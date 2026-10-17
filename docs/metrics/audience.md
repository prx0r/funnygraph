# AUDIENCE — what viewers rate (0-100)

**One line:** standout-special IMDb, Top-250 shrinkage. The people's verdict per special.

## Formula (display score — v0.2 correction)
1. Per comedian, take the standout (or best-rated) special's RAW IMDb rating.
2. Map 5.0→0, 9.0→100: `(r−5)·25`, clipped.
3. NO shrinkage in display (v0.1 wrongly claimed WR here): shrinkage exists
   to ORDER fairly (ranking leg: WR m=500, C=7.50 calibrated); the display
   shows what viewers said, vote-base credibility on the coverage badge.

## Inputs
- `specials_rated[]` (IMDb title.ratings + title.basics, free public datasets)
- Match: whole-word title overlap ≥2 words or comedian name in title.

## Justification
The IMDb Top-250 formula is the industry standard for combining rating with
vote-base credibility. Per-special (not career-average) because specials vary
wildly within a career. Academic precedent: LIWC-22 + IMDb study (PMC 2024)
uses IMDb as the dependent variable for special quality with vote-count
standardization.

## Limitations
- Vote-count recency bias; selection bias (only notable specials get pages).
- Platform rating drift uncorrected. Understates non-English specials.
- See GAPS.md §2.

## References
IMDb Top-250 methodology · LIWC/IMDb study (PMC 2024) · GAPS.md §2.
