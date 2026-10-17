# GAPS — what's wrong with our methodology (honest audit, 2026-10-17)

> Every flaw we know about, stated plainly. A ranking that hides its gaps
> is a listicle. This file is the difference.
>
> Status 2026-10-17 PM (v0.2): items marked ✅ CLOSED were fixed today
> (kendall_w.py, stability.py, mallows_phi.py, bt_leg.py, split_boards.py —
> see PAPER_ARXIV.md). The rest stand.

## Fitted result (fit_weights.py): the legs disagree — WITH A CAVEAT (runs A+B)

Hide RS2017, predict it from CC2004+IMDb+awards.

Run A (day-zero, n=16):

| Weights (CC, IMDb, awards) | Kendall concordance |
|---|---|
| (1, 0, 0) — CC only | **0.692** |
| (3, 2, 1) — asserted | 0.658 |
| best found | 0.692 at (1, 0, 0) |

Run B (2026-10-17, n=29 — more graphs carry both ranks now; 2 members
gained critic-matched specials; several gained awards):

| Weights (CC, IMDb, awards) | Kendall concordance |
|---|---|
| (1, 0, 0) — CC only | 0.635 |
| (3, 2, 1) — asserted | 0.677 |
| best found | **0.709 at (1, 2, 1)** |

**The grid search flipped direction between runs.** n≈16–29 grid fits are
FRAGILE — a few members' features move the estimate ±0.05. Do not steer
product by either run alone. The split boards stand on the STABLE evidence
instead: pairwise taus (n=178–232, τ ca≈.18–.20 with tight CIs) and
Mallows precision ordering — critics and audiences measure different
things whether or not any given grid run favors blending. The v0.2 papers
cited Run A as proof; corrected in §§ below to weak-signal status.

**Run A read:** adding IMDb + awards made canon prediction worse — they
measure something else (audience taste ≠ critic canon). **Run B read:**
with fuller audience features, blending helps. Both reads are consistent
with the stable finding (taus): the legs measure different things; whether
a tiny grid run rewards blending depends on feature coverage that week.
Product stance unchanged: **stop averaging, model the disagreement** —
separate CANON and PEOPLE'S CHOICE boards, with the gap as the product.
The gap is now justified by taus, not by either grid run.

## Gap list

### 1. Critics leg is stale (CRITICAL)
CC2004 is 22 years old, RS2017 is 9. Anyone who broke through after 2017
(Gillis, KT wave, TikTok comics) has ZERO critics data. The leg structurally
favors the dead and the old. **Fix: our own 2026 critic survey + arena votes
as a new leg with a 2026 timestamp (TOP2026.md).**

### 2. IMDb leg biases (HIGH)
- Vote-count bias: recent Netflix specials have 10-100x the votes of 90s hours.
- Shrinkage (m=500, C=7.50 calibrated) helps but doesn't erase the structural advantage.
- Selection bias: only specials notable enough for IMDb pages exist.
- Rating drift: platform-wide inflation over time uncorrected.
- **Fix: time-decayed momentum (rating velocity), vote-count floors per era.**

### 3. Awards leg sparse + mainstream-biased (HIGH) — 🔶 PARTIAL (v0.2+)
Filter + weights now accept regional legs (11 labels landed: British
Comedy/Chortle/Edinburgh; Matafeo Edinburgh + Vir Das Emmy curated from
source). Wikidata P166 is the binding constraint for NG/AU scenes —
bios/QIDs missing, not just filtered. Weights asserted (too sparse to
fit — stated in code).
13/181 scored. Grammys favor recorded mainstream; Mark Twain is lifetime
achievement (old comics); alt/underground systematically excluded.
**Fix: more QIDs (bios running), plus comedy-specific awards (American Comedy
Awards, Edinburgh Comedy Award) as additional P166 filters.**

### 4. Missing-data asymmetry (HIGH)
44/181 have critics ranks, 85/181 have IMDb. ~100 comics ride near-zero legs
— their ranks are noise. **Fix: coverage-weighted confidence per position;
don't rank the unmeasured (or rank separately as "unranked — insufficient data").**

### 5. No pairwise data (MEDIUM) — ✅ PARTIALLY CLOSED (v0.2)
Bradley-Terry leg reserved but empty. Our arena votes exist but small-n.
Rank-breaking BT on list-implied pairs built (bt_leg.py, 701 pairs,
τ=+0.876 vs Borda critics — Borda validated). True arena votes still
pending (TOP2026).
**Fix: TOP2026 arena battles feed this leg directly.**

### 6. Generation boundaries authored (MEDIUM)
Breakthrough decade is judgment, not measurement. Cusp comics could flip gens.
**Fix: derive from first-special year where transcripts give it; flag cusp cases.**

### 7. Weights asserted, now FITTED — and fitting says split the boards (MEDIUM) — ✅ CLOSED (v0.2)
See fitted result above. 3/2/1 was a guess; the data says critics and
audiences are different elections. Mallows φ per leg (mallows_phi.py)
implies precision weights (critics .498 / audience .214 / awards .288).
**Fix: CANON board (critics+awards) and PEOPLE'S CHOICE board
(audience+momentum), published separately (split_boards.py).** Done —
canon.json + peoples.json are primary; weighted consensus is legacy view.

### 8. No recency mechanism (HIGH for 2026 product)
A 2023 breakout competes against 40 years of canon with no momentum term.
**Fix: rating velocity + 2024-26 special boost + YouTube view counts in the
2026 board only (never in ALL-TIME).**

### 9. Single snapshot (MEDIUM)
Rankings-through-years needs more time points: 2004, 2017, now. **Fix: our
2026 vote becomes the third point; annual cadence after.**

### 10. No audience segmentation (LOW) — ✅ CLOSED (v0.2)
Critics vs audiences disagree systematically; we averaged. Pairwise
τ(critics,audience)=+0.177 with bootstrap CI; Kendall's W=0.438, p=0.22
(independence not rejected on full-coverage n=11). Disagreement is now
first-class (agreement.json); averaging is legacy view.
**Fix: model the disagreement (already have disagreement.json — promote it to first-class).** Done.

## What "definitive" can honestly mean

Not one number. Three boards + uncertainty:
- **ALL-TIME CANON** (critics + awards, era-normalized, slow-moving)
- **PEOPLE'S CHOICE** (audience WR + momentum, fast-moving)
- **TOP 2026** (fresh legs only: our vote + recent specials + views — see TOP2026.md)
- Every position with leg breakdown + disagreement + coverage confidence.
