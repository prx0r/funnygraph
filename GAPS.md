# GAPS — what's wrong with our methodology (honest audit, 2026-10-17)

> Every flaw we know about, stated plainly. A ranking that hides its gaps
> is a listicle. This file is the difference.

## Fitted result (fit_weights.py): the legs disagree

Hid RS2017, predicted it from CC2004+IMDb+awards over 16 comics on both lists:

| Weights (CC, IMDb, awards) | Kendall concordance |
|---|---|
| (1, 0, 0) — CC only | **0.692** |
| (3, 2, 1) — current | 0.658 |
| best found | 0.692 at (1, 0, 0) |

**Adding IMDb + awards made canon prediction WORSE.** They don't refine the
critics' signal — they measure something else (audience taste ≠ critic canon).
Averaging legs destroys both signals. The fix is not better weights; it's
**stop averaging, model the disagreement**: separate CANON and PEOPLE'S
CHOICE boards, with the gap as the product.

## Gap list

### 1. Critics leg is stale (CRITICAL)
CC2004 is 22 years old, RS2017 is 9. Anyone who broke through after 2017
(Gillis, KT wave, TikTok comics) has ZERO critics data. The leg structurally
favors the dead and the old. **Fix: our own 2026 critic survey + arena votes
as a new leg with a 2026 timestamp (TOP2026.md).**

### 2. IMDb leg biases (HIGH)
- Vote-count bias: recent Netflix specials have 10-100x the votes of 90s hours.
- Shrinkage (m=1000) helps but doesn't erase the structural advantage.
- Selection bias: only specials notable enough for IMDb pages exist.
- Rating drift: platform-wide inflation over time uncorrected.
- **Fix: time-decayed momentum (rating velocity), vote-count floors per era.**

### 3. Awards leg sparse + mainstream-biased (HIGH)
13/181 scored. Grammys favor recorded mainstream; Mark Twain is lifetime
achievement (old comics); alt/underground systematically excluded.
**Fix: more QIDs (bios running), plus comedy-specific awards (American Comedy
Awards, Edinburgh Comedy Award) as additional P166 filters.**

### 4. Missing-data asymmetry (HIGH)
44/181 have critics ranks, 85/181 have IMDb. ~100 comics ride near-zero legs
— their ranks are noise. **Fix: coverage-weighted confidence per position;
don't rank the unmeasured (or rank separately as "unranked — insufficient data").**

### 5. No pairwise data (MEDIUM)
Bradley-Terry leg reserved but empty. Our arena votes exist but small-n.
**Fix: TOP2026 arena battles feed this leg directly.**

### 6. Generation boundaries authored (MEDIUM)
Breakthrough decade is judgment, not measurement. Cusp comics could flip gens.
**Fix: derive from first-special year where transcripts give it; flag cusp cases.**

### 7. Weights asserted, now FITTED — and fitting says split the boards (MEDIUM)
See fitted result above. 3/2/1 was a guess; the data says critics and
audiences are different elections. **Fix: CANON board (critics+awards) and
PEOPLE'S CHOICE board (audience+momentum), published separately.**

### 8. No recency mechanism (HIGH for 2026 product)
A 2023 breakout competes against 40 years of canon with no momentum term.
**Fix: rating velocity + 2024-26 special boost + YouTube view counts in the
2026 board only (never in ALL-TIME).**

### 9. Single snapshot (MEDIUM)
Rankings-through-years needs more time points: 2004, 2017, now. **Fix: our
2026 vote becomes the third point; annual cadence after.**

### 10. No audience segmentation (LOW)
Critics vs audiences disagree systematically; we averaged. **Fix: model the
disagreement (already have disagreement.json — promote it to first-class).**

## What "definitive" can honestly mean

Not one number. Three boards + uncertainty:
- **ALL-TIME CANON** (critics + awards, era-normalized, slow-moving)
- **PEOPLE'S CHOICE** (audience WR + momentum, fast-moving)
- **TOP 2026** (fresh legs only: our vote + recent specials + views — see TOP2026.md)
- Every position with leg breakdown + disagreement + coverage confidence.
