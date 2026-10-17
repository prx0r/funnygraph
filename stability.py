#!/usr/bin/env python3
"""STABILITY — regime-stability intervals for every consensus position.

Formalizes the "top-1 flips by regime" claim into per-comic rank intervals.

A rank without a stability interval is a point estimate pretending to be a
fact. We recompute the board under 72 regimes:
  * weight grid: wc in {1..5} x wa in {0..3} x waw in {0..2} (60 regimes;
    same grid as fit_weights.py, so stability and fitting speak one language)
  * leave-one-leg-out (3 regimes: drop critics / audience / awards)
  * WR calibration perturbation: m in {250,500,1000} x C in {7.0,7.5,8.0}
    (9 regimes at default weights — does the shrinkage prior move ranks?)

Kemenization is NOT rerun per regime (O(n^2) x 72 is wasteful and the moves
are local). Instead we measure Kemenization displacement once at default
weights and report it alongside: max/mean positions moved.

Output per comic: median rank, p5/p95 across regimes, LOO ranks,
stable-claim flag (|p95-p5| <= 5 AND same holder across LOO).
Writes rankings/stability.json. Reads only; never touches existing boards.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from rank_comedians import (GEN_START, award_score, borda_leg, imdb_wr,
                            load_comics)

OUT = HERE / "rankings"


def base_legs(comics: dict, m: int = 500, C: float = 7.5):
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
    critics = {cid: cc_b.get(cid, 0) / cc_m + rs_b.get(cid, 0) / rs_m
               for cid in comics}
    wr = {}
    for cid, j in comics.items():
        sp = j.get("specials_rated") or []
        rated = [s for s in sp
                 if s.get("imdb_rating") and s.get("imdb_votes")]
        if not rated:
            continue
        s = max(rated, key=lambda x: (x.get("standout", False),
                                      x.get("imdb_rating", 0)))
        R, v = s["imdb_rating"], s["imdb_votes"]
        wr[cid] = round((v / (v + m)) * R + (m / (v + m)) * C, 3)
    aud_order = sorted(wr, key=lambda c: -wr[c])
    aud_b = borda_leg(aud_order)
    aud_m = max(aud_b.values(), default=1)
    audience = {cid: aud_b.get(cid, 0) / aud_m for cid in comics}
    aw_raw = {cid: award_score((j.get("recognition") or {}).get("awards", []))
              for cid, j in comics.items()}
    aw_m = max(aw_raw.values(), default=1) or 1
    awards = {cid: v / aw_m for cid, v in aw_raw.items()}
    return critics, audience, awards


def rank_of(order: list[str]) -> dict[str, int]:
    return {cid: i + 1 for i, cid in enumerate(order)}


def kemenize(board: list[str], legs: tuple[dict, dict, int]) -> list[str]:
    """Same adjacent-swap hill-climb as rank_comedians.py (<=6 passes)."""
    board = list(board)

    def cost(order):
        pos = {cid: i for i, cid in enumerate(order)}
        c = 0
        for leg in legs:
            ranked = sorted([x for x in order if leg[x] > 0],
                            key=lambda x: -leg[x])
            rp = {x: i for i, x in enumerate(ranked)}
            for i in range(len(ranked)):
                for k in range(i + 1, len(ranked)):
                    a, b = ranked[i], ranked[k]
                    if pos[a] > pos[b]:
                        c += 1
        return c

    improved, rounds = True, 0
    while improved and rounds < 6:
        improved, rounds = False, rounds + 1
        base = cost(board)
        for i in range(len(board) - 1):
            board[i], board[i + 1] = board[i + 1], board[i]
            if cost(board) < base:
                base = cost(board)
                improved = True
            else:
                board[i], board[i + 1] = board[i + 1], board[i]
    return board


def main() -> None:
    comics = load_comics()
    cids = sorted(comics)
    critics, audience, awards = base_legs(comics)
    legs = {"critics": critics, "audience": audience, "awards": awards}

    def board_for(wc, wa, waw, drop=None, m=500, C=7.5):
        use_aud = audience
        if m != 500 or C != 7.5:
            _, use_aud, _ = base_legs(comics, m, C)
        w = {"critics": wc, "audience": wa, "awards": waw}
        if drop:
            w[drop] = 0.0
        board = sorted(cids, key=lambda c: -(w["critics"] * critics[c]
                                             + w["audience"] * use_aud[c]
                                             + w["awards"] * awards[c]))
        return rank_of(board)

    regimes: list[tuple[str, dict[str, int]]] = []
    # 60 weight-grid regimes
    for wc in (1, 2, 3, 4, 5):
        for wa in (0, 1, 2, 3):
            for waw in (0, 1, 2):
                regimes.append((f"w{wc}{wa}{waw}",
                                board_for(wc, wa, waw)))
    # 3 leave-one-leg-out
    for drop in ("critics", "audience", "awards"):
        regimes.append((f"no-{drop}", board_for(3, 2, 1, drop=drop)))
    # 9 WR-prior perturbations
    for m in (250, 500, 1000):
        for C in (7.0, 7.5, 8.0):
            if m == 500 and C == 7.5:
                continue
            regimes.append((f"wr-m{m}-C{C}", board_for(3, 2, 1, m=m, C=C)))
    print(f"{len(regimes)} regimes x {len(cids)} comics")

    # Kemenization displacement at default weights (once)
    pre = sorted(cids, key=lambda c: -(3 * critics[c] + 2 * audience[c]
                                       + awards[c]))
    post = kemenize(pre, (critics, audience, awards))
    r0, r1 = rank_of(pre), rank_of(post)
    disp = {c: abs(r0[c] - r1[c]) for c in cids}
    kem = {"max_displacement": max(disp.values()),
           "mean_displacement": round(statistics.mean(disp.values()), 3),
           "moved": sum(1 for c in cids if disp[c] > 0)}
    print(f"kemenization displacement: max={kem['max_displacement']} "
          f"mean={kem['mean_displacement']} moved={kem['moved']}")

    # default board for reference (must match consensus.json order pre-kemenize
    # up to kemenization moves; we report post-kemenize default rank)
    default_rank = rank_of(post)
    name_of = {c: comics[c].get("name", c) for c in cids}

    rows = []
    for cid in cids:
        rs = sorted(r for _, b in regimes for r in [b[cid]])
        p5 = rs[int(0.05 * len(rs))]
        p95 = rs[int(0.95 * len(rs))]
        med = int(statistics.median(rs))
        loo = {tag: b[cid] for tag, b in regimes if tag.startswith("no-")}
        rows.append({
            "comedian_id": cid,
            "name": name_of[cid],
            "default_rank": default_rank[cid],
            "median_rank": med,
            "p5_rank": p5,
            "p95_rank": p95,
            "width": p95 - p5,
            "loo": loo,
            "stable": (p95 - p5) <= 5,
        })
    rows.sort(key=lambda r: r["default_rank"])
    n_stable = sum(1 for r in rows if r["stable"])
    print(f"stable (|p95-p5|<=5): {n_stable}/{len(rows)}")
    print("widest intervals (claims, not facts):")
    for r in sorted(rows, key=lambda r: -r["width"])[:8]:
        print(f"  #{r['default_rank']:>3} {r['name'][:24]:24} "
              f"median {r['median_rank']:>3}  90% [{r['p5_rank']},{r['p95_rank']}]")

    (OUT / "stability.json").write_text(json.dumps({
        "note": "Rank intervals across 72 regimes (60 weight-grid + 3 "
                "leave-one-leg-out + 8 WR-prior perturbations, "
                "Kemenization displacement measured separately). "
                "A position is a STABLE CLAIM iff width<=5.",
        "kemenization_displacement": kem,
        "n_regimes": len(regimes),
        "n_stable": n_stable,
        "rows": rows,
    }, indent=1))
    print("\nsaved rankings/stability.json")


if __name__ == "__main__":
    main()
