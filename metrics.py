#!/usr/bin/env python3
"""METRICS — compute CANON/CROWD/PULL/HEAT/CRAFT + differentials into graphs.

Reads: rankings/consensus.json, era_adjusted.json, data/youtube/*.json,
       netflix hours in graphs, specials_rated, theory depth.
Writes: metrics{} per graph + rankings/metrics.json (all boards).

Usage: python3 metrics.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
RANK = HERE / "rankings"


def pct(rank: int | None, n: int) -> float | None:
    if not rank:
        return None
    return round(1 - (rank - 1) / max(1, n), 4)


def load_board(path: str) -> dict:
    try:
        return {c["comedian_id"]: c["rank"]
                for c in json.loads((RANK / path).read_text())}
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> None:
    consensus = load_board("consensus.json")
    era = {c["comedian_id"]: c["rank"] for c in
           json.loads((RANK / "era_adjusted.json").read_text())} \
        if (RANK / "era_adjusted.json").exists() else {}
    n = len(consensus) or 1

    # youtube pull
    yt = {}
    for p in Path(HERE / "data" / "youtube").glob("*.json"):
        try:
            d = json.loads(p.read_text())
            yt[d["comedian_id"]] = d["total_views"]
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    yt_rank = {c: i + 1 for i, c in
               enumerate(sorted(yt, key=lambda c: -yt[c]))}

    # netflix hours pull
    nflx = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        h = (j.get("netflix_viewership") or {}).get("hours", 0)
        if h:
            nflx[d.name] = h

    out = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        j = json.loads(g.read_text())
        cid = d.name

        canon = pct(consensus.get(cid), n)
        cands = ([pct(era.get(cid), n)] if era.get(cid) else [])
        canon_z = pct(era.get(cid), n)
        # crowd from standout WR
        sp = j.get("specials_rated") or []
        rated = [s for s in sp if s.get("imdb_rating")]
        crowd = None
        if rated:
            best = max(rated, key=lambda s: s["imdb_rating"])
            # scale 5.0-9.0 → 0-100
            crowd = round(max(0, min(100, (best["imdb_rating"] - 5.0) * 25)), 1)
        # pull: youtube percentile blended with netflix hours percentile
        pull = None
        if cid in yt_rank or cid in nflx:
            parts = []
            if cid in yt_rank:
                parts.append(1 - (yt_rank[cid] - 1) / max(1, len(yt_rank)))
            if cid in nflx:
                nr = sorted(nflx, key=lambda c: -nflx[c]).index(cid) + 1
                parts.append(1 - (nr - 1) / len(nflx))
            pull = round(sum(parts) / len(parts) * 100, 1)
        # craft: theory depth signals
        depth = 0
        depth += min(3, len(j.get("known_bits", [])))
        depth += min(2, len(j.get("essay_seeds", [])) // 2)
        depth += 2 if any((s.get("timing_measured") or {})
                          for s in j.get("sets", [])) else 0
        depth += 1 if (j.get("timing_profile") or {}).get("doctrine_hypothesis") else 0
        craft = round(depth / 8 * 100, 1)

        m = {"canon": round(canon * 100, 1) if canon is not None else None,
             "canon_era": round(canon_z * 100, 1) if canon_z is not None else None,
             "crowd": crowd, "pull": pull, "craft": craft,
             "heat": None}  # heat needs pulse velocity (2+ snapshots)
        # differentials (percentile gaps)
        def _pct100(v):
            return v / 100 if v is not None else None
        cp, cr, pu = _pct100(m["canon"]), _pct100(crowd), _pct100(pull)
        m["gap"] = round(pu - cr, 3) if pu is not None and cr is not None else None
        m["canon_lag"] = round(cr - cp, 3) if cr is not None and cp is not None else None
        j["metrics"] = m
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        out.append({"comedian_id": cid, "name": j.get("name", cid),
                    "generation": (j.get("generation") or {}).get("id"),
                    **m})
    (RANK / "metrics.json").write_text(json.dumps(out, indent=1))

    def top(key, k=10, rev=True):
        rows = [c for c in out if c.get(key) is not None]
        rows.sort(key=lambda c: -c[key] if rev else c[key])
        return rows[:k]

    print("=== CANON (top 8) ===")
    for c in top("canon", 8):
        print(f"  {c['canon']:>5}  {c['name'][:26]}")
    print("=== CROWD (top 8) ===")
    for c in top("crowd", 8):
        print(f"  {c['crowd']:>5}  {c['name'][:26]}")
    print("=== OVERRATED (gap, top 8) ===")
    for c in top("gap", 8):
        print(f"  {c['gap']:+.2f}  {c['name'][:26]}")
    print("=== UNDERRATED (gap, bottom 8) ===")
    for c in top("gap", 8, rev=False):
        print(f"  {c['gap']:+.2f}  {c['name'][:26]}")
    print(f"\nsaved rankings/metrics.json ({len(out)} comics)")


if __name__ == "__main__":
    main()
