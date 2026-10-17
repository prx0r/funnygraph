#!/usr/bin/env python3
"""AGREEMENT — inter-leg concordance for the consensus ranking.

Formalizes PAPER.md section 6 ("inter-leg agreement") which was roadmap-only.

Computes:
  1. Pairwise Kendall tau-b between the three legs (critics, audience, awards)
     over all kings, with bootstrap 95% CIs (resample comics, 1000 reps).
  2. Kendall's W (coefficient of concordance, Kendall & Babington Smith 1939)
     on the full-coverage subset (comics scoring on all three legs),
     with chi-square significance: X^2 = m(n-1)W, df = n-1.
  3. Per-leg centrality: mean tau of each leg against the other two
     (which leg is the "median voter").
  4. Coverage table: how many comics each leg scores (the missing-data audit).

Leg scores are recomputed here with the exact recipe of rank_comedians.py
(Borda per list normalized by own max; WR m=500 C=7.5; prestige awards),
so this file can never drift from the ranker. Import, don't copy.

Usage: python3 kendall_w.py [--boots N]
Output: rankings/agreement.json + printed summary.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from rank_comedians import (AWARD_W, GEN_START, LIST_YEARS, award_score,
                            borda_leg, imdb_wr, load_comics)

OUT = HERE / "rankings"


def compute_legs(comics: dict) -> dict[str, dict[str, float]]:
    """Exact leg recipe from rank_comedians.py. Returns {leg: {cid: score}}."""
    cc_order, rs_order = [], []
    for cid, j in comics.items():
        rec = j.get("recognition") or {}
        gen = (j.get("generation") or {}).get("id", "")
        gs = GEN_START.get(gen, 2000)
        if rec.get("comedy_central_2004") and gs <= 2004:
            cc_order.append((rec["comedy_central_2004"], cid))
        if rec.get("rolling_stone_2017") and gs <= 2017:
            rs_order.append((rec["rolling_stone_2017"], cid))
    cc_order.sort()
    rs_order.sort()
    cc_b = borda_leg([c for _, c in cc_order])
    rs_b = borda_leg([c for _, c in rs_order])
    cc_m = max(cc_b.values(), default=1)
    rs_m = max(rs_b.values(), default=1)
    critics = {cid: round(cc_b.get(cid, 0) / cc_m + rs_b.get(cid, 0) / rs_m, 4)
               for cid in comics}

    wr = {}
    for cid, j in comics.items():
        w = imdb_wr(j.get("specials_rated") or [])
        if w:
            wr[cid] = w
    aud_order = sorted(wr, key=lambda c: -wr[c])
    aud_b = borda_leg(aud_order)
    aud_m = max(aud_b.values(), default=1)
    audience = {cid: round(aud_b.get(cid, 0) / aud_m, 4) for cid in comics}

    aw_raw = {cid: award_score((j.get("recognition") or {}).get("awards", []))
              for cid, j in comics.items()}
    aw_m = max(aw_raw.values(), default=1) or 1
    awards = {cid: round(v / aw_m, 4) for cid, v in aw_raw.items()}
    return {"critics": critics, "audience": audience, "awards": awards}


def kendall_taub(xs: list[float], ys: list[float]) -> float:
    """Kendall tau-b (ties in either ranking handled). Pure stdlib."""
    n = len(xs)
    conc = disc = t_x = t_y = 0
    for i in range(n):
        for k in range(i + 1, n):
            dx = (xs[i] > xs[k]) - (xs[i] < xs[k])
            dy = (ys[i] > ys[k]) - (ys[i] < ys[k])
            if dx != 0 and dy != 0:
                if dx == dy:
                    conc += 1
                else:
                    disc += 1
            elif dx != 0:
                t_y += 1
            elif dy != 0:
                t_x += 1
    denom = math.sqrt((conc + disc + t_x) * (conc + disc + t_y))
    return (conc - disc) / denom if denom else 0.0


def kendalls_w(rank_matrix: list[list[float]]) -> tuple[float, float, int]:
    """Kendall's W with tie correction.

    rank_matrix: m judges x n items (average ranks, ties = midranks).
    Returns (W, chi2 p-value approx via chi-square CDF, n).
    p-value uses the Wilson-Hilferty-free path: scipy if present, else
    a normal approximation note (returns -1.0 when scipy missing).
    """
    m = len(rank_matrix)
    n = len(rank_matrix[0])
    # column sums of ranks
    col = [sum(rank_matrix[j][i] for j in range(m)) for i in range(n)]
    mean_r = sum(col) / n
    S = sum((c - mean_r) ** 2 for c in col)
    # tie correction per judge: T = sum(t^3 - t) over tie groups
    T = 0.0
    for row in rank_matrix:
        counts: dict[float, int] = {}
        for v in row:
            counts[v] = counts.get(v, 0) + 1
        for t in counts.values():
            if t > 1:
                T += t ** 3 - t
    denom = m * m * (n ** 3 - n) - m * T
    W = 12 * S / denom if denom else 0.0
    chi2 = m * (n - 1) * W
    try:
        from scipy.stats import chi2 as _chi2

        p = float(1 - _chi2.cdf(chi2, n - 1))
    except ImportError:
        p = -1.0
    return W, p, n


def to_midrank(scores: dict[str, float], cids: list[str]) -> list[float]:
    """Scores -> average ranks (1 = top). Ties share midranks."""
    order = sorted(cids, key=lambda c: -scores[c])
    ranks: dict[str, float] = {}
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        mid = (i + 1 + j + 1) / 2
        for k in range(i, j + 1):
            ranks[order[k]] = mid
        i = j + 1
    return [ranks[c] for c in cids]


def bootstrap_tau(x: list[float], y: list[float], boots: int,
                  seed: int = 7) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(x)
    vals = []
    for _ in range(boots):
        idx = [rng.randrange(n) for _ in range(n)]
        vals.append(kendall_taub([x[i] for i in idx], [y[i] for i in idx]))
    vals.sort()
    lo = vals[int(0.025 * boots)]
    hi = vals[int(0.975 * boots)]
    return round(lo, 3), round(hi, 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--boots", type=int, default=1000)
    args = ap.parse_args()

    comics = load_comics()
    legs = compute_legs(comics)
    cids = sorted(comics)
    names = ["critics", "audience", "awards"]
    vec = {nm: [legs[nm][c] for c in cids] for nm in names}

    # 1. pairwise tau-b + bootstrap CIs
    pairs = {}
    for i in range(3):
        for k in range(i + 1, 3):
            a, b = names[i], names[k]
            tau = kendall_taub(vec[a], vec[b])
            lo, hi = bootstrap_tau(vec[a], vec[b], args.boots)
            pairs[f"{a}_vs_{b}"] = {
                "tau_b": round(tau, 3), "ci95": [lo, hi], "n": len(cids)}
            print(f"tau({a},{b}) = {tau:+.3f}  95% CI [{lo:+.3f},{hi:+.3f}]")

    # 2. Kendall's W on full-coverage subset (all three legs > 0)
    full = [c for c in cids
            if all(legs[nm][c] > 0 for nm in names)]
    W, p, n = (0.0, -1.0, 0)
    if len(full) >= 3:
        mat = [to_midrank(legs[nm], full) for nm in names]
        W, p, n = kendalls_w(mat)
    print(f"\nKendall's W (n={n} full-coverage comics, m=3 legs): {W:.3f}"
          + (f"  chi2 p={p:.2e}" if p >= 0 else "  (scipy missing, no p)"))

    # W on the critics+audience pair over comics scoring on both
    # (awards sparsity would otherwise dominate the story)
    ca = [c for c in cids if legs["critics"][c] > 0 and legs["audience"][c] > 0]
    W2, p2, n2 = 0.0, -1.0, 0
    if len(ca) >= 3:
        mat2 = [to_midrank(legs["critics"], ca), to_midrank(legs["audience"], ca)]
        W2, p2, n2 = kendalls_w(mat2)
    print(f"Kendall's W critics+audience (n={n2}): {W2:.3f}"
          + (f"  chi2 p={p2:.2e}" if p2 >= 0 else ""))

    # 3. per-leg centrality (mean tau vs the other two)
    centrality = {}
    for nm in names:
        others = [pairs[k]["tau_b"] for k in pairs if nm in k]
        centrality[nm] = round(statistics.mean(others), 3)
    print(f"\nleg centrality (mean tau vs others): {centrality}")

    # 4. coverage audit
    coverage = {nm: sum(1 for c in cids if legs[nm][c] > 0) for nm in names}
    coverage["all_three"] = len(full)
    coverage["n_kings"] = len(cids)
    print(f"coverage: {coverage}")

    (OUT / "agreement.json").write_text(json.dumps({
        "note": "Inter-leg concordance. tau-b handles ties (awards zeros). "
                "W needs complete rankings: full-coverage subset only. "
                "CIs by resampling comics (1000 reps).",
        "pairwise_tau_b": pairs,
        "kendalls_W_all3": {"W": round(W, 4), "chi2_p": p, "n": n},
        "kendalls_W_critics_audience": {"W": round(W2, 4), "chi2_p": p2,
                                        "n": n2},
        "leg_centrality": centrality,
        "coverage": coverage,
    }, indent=1))
    print("\nsaved rankings/agreement.json")


if __name__ == "__main__":
    main()
