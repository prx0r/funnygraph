#!/usr/bin/env python3
"""BT LEG — list-implied Bradley-Terry strengths for the critics leg.

RANKINGS.md reserves a Bradley-Terry leg for future arena votes. This builds
the version that needs no new data: published lists already imply pairwise
outcomes (A ranked above B on CC2004 == A-beats-B observation). Rank-breaking
(Khetan & Oh 2016): each list of length k yields k(k-1)/2 pairs.

Pairs: CC2004 (100 ranked -> 4950 pairs) + RS2017 (50 -> 1225 pairs), one
vote each; pairs appearing in both lists count twice (agreed evidence);
conflicting orders across lists both enter (BT prices disagreement).
Postdate rule inherited from the ranker: a comic only appears in lists
predating... precisely: only in lists whose year >= generation start
(same GEN_START gate as rank_comedians.py).

Estimation: MM algorithm (Hunter 2004): pi_i <- W_i / sum_{j} N_ij/(pi_i+pi_j).
Convergence 1e-12. Comics in no pairs are absent (BT undefined) — stated.

Validation use: Kendall tau between BT order and the Borda critics leg.
High tau justifies Borda as the cheap (5-approx, Dwork et al. 2001) stand-in;
divergence would indict it.
Writes rankings/bt.json. Reads only.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kendall_w import compute_legs, kendall_taub
from rank_comedians import GEN_START, load_comics

OUT = HERE / "rankings"


def implied_pairs(comics: dict) -> dict[tuple[str, str], list[int]]:
    """(winner, loser) -> [wins]. One entry per list occurrence."""
    pairs: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0])
    lists = 0
    for key, year in (("comedy_central_2004", 2004),
                      ("rolling_stone_2017", 2017)):
        order = []
        for cid, j in comics.items():
            rec = j.get("recognition") or {}
            gen = (j.get("generation") or {}).get("id", "")
            if rec.get(key) and GEN_START.get(gen, 2000) <= year:
                order.append((rec[key], cid))
        order.sort()
        ranked = [c for _, c in order]
        for i in range(len(ranked)):
            for k in range(i + 1, len(ranked)):
                pairs[(ranked[i], ranked[k])][0] += 1
        lists += 1
        print(f"{key}: {len(ranked)} ranked -> "
              f"{len(ranked) * (len(ranked) - 1) // 2} pairs")
    return pairs


def bradley_terry(pairs: dict, tol: float = 1e-12,
                  max_it: int = 10000) -> dict[str, float]:
    """MM (Hunter 2004). Returns normalized strengths summing to 1."""
    players = set()
    for (a, b) in pairs:
        players.add(a)
        players.add(b)
    players = sorted(players)
    wins: dict[str, float] = {p: 0.0 for p in players}
    nmat: dict[tuple[str, str], float] = defaultdict(float)
    for (a, b), (w,) in pairs.items():
        wins[a] += w
        nmat[(a, b)] += w
        nmat[(b, a)] += w
    pi = {p: 1.0 / len(players) for p in players}
    for _ in range(max_it):
        new = {}
        for p in players:
            denom = 0.0
            for q in players:
                if q == p or nmat[(p, q)] == 0:
                    continue
                denom += nmat[(p, q)] / (pi[p] + pi[q])
            new[p] = wins[p] / denom if denom else 0.0
        s = sum(new.values()) or 1.0
        new = {p: v / s for p, v in new.items()}
        if max(abs(new[p] - pi[p]) for p in players) < tol:
            pi = new
            break
        pi = new
    return pi


def main() -> None:
    comics = load_comics()
    pairs = implied_pairs(comics)
    print(f"{len(pairs)} unique pairs")
    pi = bradley_terry(pairs)
    bt_order = sorted(pi, key=lambda c: -pi[c])

    # validate against the Borda critics leg
    legs = compute_legs(comics)
    crit = legs["critics"]
    sub = [c for c in bt_order if crit[c] > 0]
    tau = kendall_taub([pi[c] for c in sub], [crit[c] for c in sub])
    # also vs raw consensus for context
    consensus = [c["comedian_id"] for c in
                 json.loads((OUT / "consensus.json").read_text())]
    cpos = {c: i for i, c in enumerate(consensus)}
    tau_cons = kendall_taub([pi[c] for c in sub],
                            [-cpos[c] for c in sub])
    print(f"\nBT order vs Borda critics leg: tau-b = {tau:+.3f} (n={len(sub)})")
    print(f"BT order vs consensus:          tau-b = {tau_cons:+.3f}")

    rows = [{"rank": i + 1, "comedian_id": c,
             "name": comics[c].get("name", c),
             "bt_strength": round(pi[c], 6)} for i, c in enumerate(bt_order)]
    (OUT / "bt.json").write_text(json.dumps({
        "note": "Bradley-Terry strengths from list-implied pairs "
                "(rank-breaking; Khetan & Oh 2016), MM estimation "
                "(Hunter 2004). Comics in no pairs absent (BT undefined).",
        "n_pairs": len(pairs),
        "tau_vs_borda_critics": round(tau, 4),
        "tau_vs_consensus": round(tau_cons, 4),
        "rows": rows,
    }, indent=1))
    print("\nsaved rankings/bt.json")


if __name__ == "__main__":
    main()
