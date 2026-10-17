#!/usr/bin/env python3
"""MALLOWS PHI — per-leg noise fit: how noisy is each voter?

Treats the consensus board as the central ranking sigma_0 and fits, per leg,
the Mallows dispersion parameter phi in (0,1] by moment-matching:
observed Kendall distance d_leg == E[d](phi) under the Mallows model.

E[d](phi) is exact via the repeated-insertion (RIM) representation
(Fligner & Verducci 1986): inserting item j (2..n) incurs
E[V_j] = sum_{k=0}^{j-1} k phi^k / sum_{k=0}^{j-1} phi^k,
and E[d] = sum_j E[V_j]. Inverted by bisection.

phi -> 0: leg is a near-noiseless copy of consensus (high precision).
phi -> 1: leg is uniform noise (no information about consensus).

Implied weights w_leg proportional to precision (-ln phi), normalized.
These REPLACE asserted weights with fitted ones wherever a single number
is needed (canon board). Legs at phi = 1 get epsilon floor, stated.

Only comics scoring > 0 on the leg enter its n (missing != disagreement).
Writes rankings/mallows.json. Reads only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kendall_w import compute_legs
from rank_comedians import load_comics

OUT = HERE / "rankings"


def expected_distance(phi: float, n: int) -> float:
    """Exact E[Kendall d] under Mallows(n, phi) via RIM. phi in (0,1]."""
    if phi >= 1.0:
        # uniform: E[d] = n(n-1)/4
        return n * (n - 1) / 4
    total = 0.0
    for j in range(2, n + 1):
        num = sum(k * (phi ** k) for k in range(j))
        den = sum(phi ** k for k in range(j))
        total += num / den if den else 0.0
    return total


def fit_phi(d_obs: float, n: int) -> float:
    """Bisect phi in [1e-9, 1] with E[d](phi) == d_obs."""
    d_max = expected_distance(1.0, n)
    if d_obs >= d_max:
        return 1.0
    if d_obs <= 0:
        return 1e-9
    lo, hi = 1e-9, 1.0  # E[d] decreasing in... note: E[d] INCREASES in phi
    # E[d](lo->0) = 0, E[d](hi=1) = max. bisect:
    for _ in range(200):
        mid = (lo + hi) / 2
        if expected_distance(mid, n) < d_obs:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def kendall_dist(order_a: list[str], order_b: list[str]) -> int:
    """Discordant pairs between two total orders over the same items."""
    pos = {c: i for i, c in enumerate(order_b)}
    d = 0
    for i in range(len(order_a)):
        for k in range(i + 1, len(order_a)):
            if pos[order_a[i]] > pos[order_a[k]]:
                d += 1
    return d


def main() -> None:
    comics = load_comics()
    legs = compute_legs(comics)
    consensus = [c["comedian_id"]
                 for c in json.loads((OUT / "consensus.json").read_text())]
    cpos = {c: i for i, c in enumerate(consensus)}

    rows = {}
    for nm, leg in legs.items():
        sub = [c for c in consensus if leg[c] > 0]
        n = len(sub)
        leg_order = sorted(sub, key=lambda c: -leg[c])
        d = kendall_dist(leg_order, sub)
        dmax = n * (n - 1) // 2
        phi = fit_phi(float(d), n)
        import math

        precision = -math.log(phi) if phi < 1 else 0.0
        rows[nm] = {
            "n_scored": n,
            "kendall_d": d,
            "d_max": dmax,
            "d_norm": round(d / dmax, 4) if dmax else 0.0,
            "phi": round(phi, 4),
            "precision_neglogphi": round(precision, 4),
        }
        print(f"{nm:9} n={n:>3} d={d:>5}/{dmax:<5} "
              f"d_norm={d/dmax if dmax else 0:.3f} phi={phi:.4f}")

    tot = sum(r["precision_neglogphi"] for r in rows.values()) or 1.0
    for nm in rows:
        rows[nm]["implied_weight"] = round(
            rows[nm]["precision_neglogphi"] / tot, 3)
    print("\nimplied weights (precision-normalized): "
          + str({k: v["implied_weight"] for k, v in rows.items()}))

    (OUT / "mallows.json").write_text(json.dumps({
        "note": "Mallows phi per leg vs consensus central ranking, RIM exact "
                "moment-match (Fligner & Verducci 1986). phi->0 noiseless, "
                "phi->1 uniform. Implied weights = precision-normalized; "
                "they replace asserted 3/2/1 wherever one number is needed.",
        "legs": rows,
    }, indent=1))
    print("\nsaved rankings/mallows.json")


if __name__ == "__main__":
    main()
