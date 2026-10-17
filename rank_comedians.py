#!/usr/bin/env python3
"""RANK — consensus comedian ranking from critics + audience + awards.

Design in RANKINGS.md. Borda per leg → weighted sum → local Kemenization →
consensus + disagreement + by-generation boards.

Legs: critics (CC2004 + RS2017), audience (IMDb standout WR), awards.
Missing-data rule: comics postdating a list are MISSING (not low);
comics contemporary-but-unranked sit below ranked ones (Dwork rule).

Usage: python3 rank_comedians.py [--weights c,a,aw] [--out rankings/]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
OUT = HERE / "rankings"

# generation → first year (for postdate rule: comic can't be on older lists)
GEN_START = {"pioneers": 1950, "seventies": 1970, "eighties-boom": 1980,
             "nineties": 1990, "aughts": 2000, "tens": 2010, "twenties": 2020}
LIST_YEARS = {"cc2004": 2004, "rs2017": 2017}

AWARD_W = {"mark twain": 3.0, "grammy": 2.0, "emmy": 1.5, "peabody": 1.5,
           "kennedy": 2.5, "pulitzer": 2.0, "tony": 1.0, "oscar": 1.0,
           "golden globe": 1.0, "writers guild": 1.0, "critics": 1.0}


TIER_RANKED = ("king",)  # indies excluded from canon until promoted


def load_comics() -> dict:
    comics = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        j = json.loads(g.read_text())
        if j.get("tier", "king") not in TIER_RANKED:
            continue
        comics[d.name] = j
    return comics


def imdb_wr(specials: list, m: int = 1000, C: float = 7.0) -> float | None:
    """IMDb Top-250 formula on the standout (or best) special."""
    if not specials:
        return None
    rated = [s for s in specials if s.get("imdb_rating") and s.get("imdb_votes")]
    if not rated:
        return None
    s = max(rated, key=lambda x: (x.get("standout", False), x.get("imdb_rating", 0)))
    R, v = s["imdb_rating"], s["imdb_votes"]
    return round((v / (v + m)) * R + (m / (v + m)) * C, 3)


def award_score(awards: list) -> float:
    sc = 0.0
    for a in awards or []:
        name = (a.get("award") or "").lower()
        for k, w in AWARD_W.items():
            if k in name:
                sc += w
                break
    return round(sc, 2)


def borda_leg(order: list[str]) -> dict:
    """Rank position → Borda points (top = most)."""
    n = len(order)
    return {cid: n - i for i, cid in enumerate(order)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", default="3,2,1",
                    help="critics,audience,awards (default 3,2,1)")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    wc, wa, waw = (float(x) for x in args.weights.split(","))
    out = Path(args.out)
    out.mkdir(exist_ok=True)

    comics = load_comics()
    print(f"{len(comics)} comedians")

    # ── leg 1: critics (CC2004 + RS2017, Borda each, summed) ──
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
    # normalize each to 0..1 by its own max
    cc_m, rs_m = max(cc_b.values(), default=1), max(rs_b.values(), default=1)
    critics = {cid: round(cc_b.get(cid, 0) / cc_m + rs_b.get(cid, 0) / rs_m, 4)
               for cid in comics}
    print(f"critics leg: CC={len(cc_order)} RS={len(rs_order)}")

    # ── leg 2: audience (IMDb WR → ranking → Borda) ──
    wr = {}
    for cid, j in comics.items():
        w = imdb_wr(j.get("specials_rated") or [])
        if w:
            wr[cid] = w
    aud_order = sorted(wr, key=lambda c: -wr[c])
    aud_b = borda_leg(aud_order)
    aud_m = max(aud_b.values(), default=1)
    audience = {cid: round(aud_b.get(cid, 0) / aud_m, 4) for cid in comics}
    print(f"audience leg: {len(aud_order)} rated")

    # ── leg 3: awards ──
    aw_raw = {cid: award_score((j.get("recognition") or {}).get("awards", []))
              for cid, j in comics.items()}
    aw_m = max(aw_raw.values(), default=1) or 1
    awards = {cid: round(v / aw_m, 4) for cid, v in aw_raw.items()}
    print(f"awards leg: {sum(1 for v in aw_raw.values() if v)} awarded")

    # ── weighted consensus ──
    def total(cid):
        return wc * critics[cid] + wa * audience[cid] + waw * awards[cid]

    board = sorted(comics, key=lambda c: -total(c))

    # ── local Kemenization: hill-climb adjacent swaps vs legs ──
    def legs_of(cid):
        return (critics[cid], audience[cid], awards[cid])

    def kendall_cost(order):
        # pairwise disagreements with each leg's implied order
        cost = 0
        pos = {cid: i for i, cid in enumerate(order)}
        for leg in (critics, audience, awards):
            ranked = sorted([c for c in order if leg[c] > 0],
                            key=lambda c: -leg[c])
            rp = {c: i for i, c in enumerate(ranked)}
            for i in range(len(ranked)):
                for k in range(i + 1, len(ranked)):
                    a, b = ranked[i], ranked[k]
                    if pos[a] > pos[b]:
                        cost += 1
        return cost

    improved = True
    rounds = 0
    while improved and rounds < 6:
        improved = False
        rounds += 1
        base = kendall_cost(board)
        for i in range(len(board) - 1):
            board[i], board[i + 1] = board[i + 1], board[i]
            if kendall_cost(board) < base:
                base = kendall_cost(board)
                improved = True
            else:
                board[i], board[i + 1] = board[i + 1], board[i]

    # ── disagreement: variance across legs' implied ranks ──
    import statistics
    dis = {}
    for cid in comics:
        ranks = []
        for leg, ordered in ((critics, None), (audience, None), (awards, None)):
            pass
        # implied rank within each leg (1 = top), only where leg > 0
        vals = []
        for leg in (critics, audience, awards):
            if leg[cid] > 0:
                vals.append(leg[cid])
        dis[cid] = round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0

    consensus = []
    for i, cid in enumerate(board, 1):
        j = comics[cid]
        consensus.append({
            "rank": i,
            "comedian_id": cid,
            "name": j.get("name", cid),
            "score": round(total(cid), 4),
            "legs": {"critics": critics[cid], "audience": audience[cid],
                     "awards": awards[cid]},
            "disagreement": dis[cid],
            "generation": (j.get("generation") or {}).get("id"),
            "imdb_wr": wr.get(cid),
            "cc2004": (j.get("recognition") or {}).get("comedy_central_2004"),
            "rs2017": (j.get("recognition") or {}).get("rolling_stone_2017"),
        })
    (out / "consensus.json").write_text(json.dumps(consensus, indent=1))

    # by generation
    byg = {}
    for gen in GENS_ORDER:
        members = [c for c in consensus if c["generation"] == gen]
        for i, c in enumerate(members, 1):
            c = dict(c)
            c["gen_rank"] = i
            byg.setdefault(gen, []).append(c)
    (out / "by_generation.json").write_text(json.dumps(byg, indent=1))

    # ── era-normalized board: within-generation z-scores per leg ──
    # Rules: missing leg data = neutral (z=0), never negative. Generations
    # with <5 scored members fall back to global stats (tiny groups give
    # extreme z-scores from single outliers).
    import statistics
    zlegs = {}
    for leg_name, leg in (("critics", critics), ("audience", audience),
                          ("awards", awards)):
        zlegs[leg_name] = {}
        groups: dict[str, list[str]] = {}
        for cid, j in comics.items():
            gen = (j.get("generation") or {}).get("id", "unknown")
            groups.setdefault(gen, []).append(cid)
        # global fallback stats
        all_vals = [leg[c] for c in comics if leg[c] > 0]
        g_mu = statistics.mean(all_vals) if all_vals else 0.0
        g_sd = statistics.pstdev(all_vals) if len(all_vals) > 1 else 1.0
        for gen, members in groups.items():
            vals = [leg[c] for c in members if leg[c] > 0]
            if len(vals) >= 5:
                # median, not mean: three giants shouldn't crater a good comic
                mu = statistics.median(vals)
                sd = statistics.pstdev(vals) or 1.0
            else:
                mu, sd = g_mu, g_sd or 1.0
            for c in members:
                if leg[c] <= 0:
                    zlegs[leg_name][c] = 0.0  # missing = neutral
                else:
                    zlegs[leg_name][c] = round((leg[c] - mu) / sd, 3)

    def ztotal(cid):
        return wc * zlegs["critics"][cid] + wa * zlegs["audience"][cid] + \
            waw * zlegs["awards"][cid]

    zboard = sorted(comics, key=lambda c: -ztotal(c))
    era_adjusted = []
    for i, cid in enumerate(zboard, 1):
        j = comics[cid]
        era_adjusted.append({
            "rank": i,
            "comedian_id": cid,
            "name": j.get("name", cid),
            "zscore": round(ztotal(cid), 3),
            "zlegs": {k: zlegs[k][cid] for k in zlegs},
            "generation": (j.get("generation") or {}).get("id"),
            "raw_rank": next((c["rank"] for c in consensus
                              if c["comedian_id"] == cid), None),
        })
    (out / "era_adjusted.json").write_text(json.dumps(era_adjusted, indent=1))

    # era-benefit gap: climb = raw_rank - new_rank (positive = moved UP)
    # Gate to comics with ≥2 scored legs — sparse comics tie at zero and
    # their rank gaps are noise, not signal (stated limitation, §7).
    def n_legs(cid):
        return sum(1 for leg in (critics, audience, awards) if leg[cid] > 0)

    gap = sorted([c for c in era_adjusted if n_legs(c["comedian_id"]) >= 2],
                 key=lambda c: (c["raw_rank"] or 999) - c["rank"])
    (out / "era_gap.json").write_text(json.dumps({
        "note": "climb = raw_rank - era_rank. Positive climb = ranked BETTER era-adjusted "
                "(underrated by raw cross-era comparison). Negative = ranked WORSE "
                "era-adjusted (benefits from raw comparison, i.e. era advantage).",
        "biggest_climbers": [
            {**c, "climb": (c["raw_rank"] or 999) - c["rank"]} for c in gap[-15:][::-1]],
        "biggest_fallers": [
            {**c, "climb": (c["raw_rank"] or 999) - c["rank"]} for c in gap[:15]],
    }, indent=1))

    # disagreement board (most fought-over first)
    fight = sorted([c for c in consensus if c["disagreement"] > 0],
                   key=lambda c: -c["disagreement"])[:30]
    (out / "disagreement.json").write_text(json.dumps(fight, indent=1))

    print(f"\n=== TOP 20 ===")
    for c in consensus[:20]:
        print(f"{c['rank']:>3} {c['name'][:24]:24} {c['score']:.2f} "
              f"(c{c['legs']['critics']:.2f} a{c['legs']['audience']:.2f} w{c['legs']['awards']:.2f})")
    print(f"\nsaved {out}/consensus.json + by_generation.json + disagreement.json")


GENS_ORDER = ["pioneers", "seventies", "eighties-boom", "nineties", "aughts",
              "tens", "twenties"]

if __name__ == "__main__":
    main()
