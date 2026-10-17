#!/usr/bin/env python3
"""HOUSE RANK — our proprietary election. First-party signals only.

Doctrine (owner call 2026-10-17): external judgments — critics lists,
IMDb ratings, awards prestige, Netflix hours, YouTube counts — are
DISPLAY-ONLY reference panels. They never enter our number. The house
board is computed exclusively from signals we measured or authored:

  P1 quality: mean calibrated paper score per comic (theory_content.json,
              29,617 characters2-annotated bits, laughter-fitted rubric).
              First-party measurement. 18 comics today; grows with annotation.
  P2 depth:   craft score 0-100 (metrics.py, known_bits + essays + timing).
              First-party authored — flagged, capped, never silent.
  P4 arena:   RESERVED. Our blind pairwise votes when TOP2026 runs.
              First-party by construction. Empty until then.

Reach/pull excluded by doctrine (popularity is not quality — our own
METRICS.md rule). Awards excluded as external judgments (factual record
kept on profiles, prestige never scored).

Aggregation: average of AVAILABLE normalized legs (missing legs excluded
from the denominator = neutral, never punished, never rewarded). No
asserted weights: default is the plain mean, and every position ships a
weight-sweep interval (P1:P2 in {0:1, 1:3, 1:1, 3:1, 1:0}) so readers see
exactly how much the blend matters. Fitting (Mallows pattern) scheduled
once P1 covers 50+ comics.

Coverage (proprietary legs): 2 = FULL, 1 = PARTIAL, 0 = UNRANKED.
Unmeasured comics are NOT ranked on noise: zero-leg profiles get no house
rank (null), only the provisional ladder in rate.py.

Usage: python3 house_rank.py
Reads: rankings/theory_content.json, rankings/metrics.json (+graphs for names).
Writes: rankings/house.json. Reads only.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from rank_comedians import load_comics

OUT = HERE / "rankings"
SWEEPS = [(0.0, 1.0), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (1.0, 0.0)]


def main() -> None:
    comics = load_comics()  # kings, exclusion-guarded
    tc = json.loads((OUT / "theory_content.json").read_text())
    measured = {c["comedian_id"]: c for c in tc["comics"]
                if c.get("in_funnygraph")}
    metrics = {c["comedian_id"]: c
               for c in json.loads((OUT / "metrics.json").read_text())}

    # normalize P1 (paper) and P2 (craft) to 0..1 by own max
    p1max = max([c["mean_paper"] for c in measured.values()] or [1.0])
    p2max = 100.0
    legs: dict[str, dict[str, float]] = {}
    for cid in comics:
        entry: dict[str, float] = {}
        if cid in measured:
            entry["P1"] = measured[cid]["mean_paper"] / p1max
        th = (metrics.get(cid) or {}).get("theory")
        if isinstance(th, (int, float)) and th > 0:
            entry["P2"] = th / p2max
        legs[cid] = entry

    def score(cid: str, w1: float, w2: float) -> float | None:
        e = legs[cid]
        num = (w1 * e["P1"] if "P1" in e else 0.0) + \
              (w2 * e["P2"] if "P2" in e else 0.0)
        den = (w1 if "P1" in e else 0.0) + (w2 if "P2" in e else 0.0)
        return round(num / den, 4) if den > 0 else None

    # default board: plain mean (0.5/0.5 over available)
    scored = [(cid, score(cid, 0.5, 0.5)) for cid in comics]
    scored = [(c, s) for c, s in scored if s is not None]
    scored.sort(key=lambda kv: -kv[1])
    rank_of = {cid: i + 1 for i, (cid, _) in enumerate(scored)}
    n = len(scored)

    # weight-sweep intervals per comic
    rows = []
    for cid, default in scored:
        variants = []
        for w1, w2 in SWEEPS:
            s = score(cid, w1, w2)
            if s is None:
                continue
            # rank under this sweep: order all comics by sweep score
            order = sorted(
                (c for c in comics if score(c, w1, w2) is not None),
                key=lambda c: -score(c, w1, w2))
            variants.append(order.index(cid) + 1)
        lo, hi = min(variants), max(variants)
        cov = "FULL" if len(legs[cid]) == 2 else "PARTIAL"
        j = comics[cid]
        rows.append({
            "rank": rank_of[cid],
            "comedian_id": cid,
            "name": j.get("name", cid),
            "house": default,
            "house_pct": round(100 * (1 - (rank_of[cid] - 1) / max(1, n)), 1),
            "legs": {k: round(v, 4) for k, v in legs[cid].items()},
            "coverage": cov,
            "sweep_lo": lo,
            "sweep_hi": hi,
            "sweep_width": hi - lo,
            "generation": ((j.get("generation") or {}).get("id")),
        })
    n_full = sum(1 for r in rows if r["coverage"] == "FULL")
    print(f"house board: {len(rows)} ranked ({n_full} FULL, "
          f"{len(rows) - n_full} PARTIAL) + P4 arena reserved")
    print("\nHOUSE top 12 (proprietary: measured jokes + theory depth):")
    for r in rows[:12]:
        p1 = r["legs"].get("P1", "-")
        p2 = r["legs"].get("P2", "-")
        print(f"  {r['rank']:>2} {r['name'][:22]:22} {r['house']:.3f} "
              f"[P1 {p1} P2 {p2}] {r['coverage']} sweep[{r['sweep_lo']},{r['sweep_hi']}]")

    (OUT / "house.json").write_text(json.dumps({
        "note": "PROPRIETARY election: first-party signals only (P1 measured "
                "joke quality + P2 authored theory depth; P4 arena reserved). "
                "External judgments (critics/IMDb/awards/Netflix/YouTube) are "
                "reference panels, never inputs. Default = mean of available "
                "legs; sweep interval shows blend sensitivity. Zero-leg "
                "profiles unranked (null), never tied at zero.",
        "legs": ["P1 measured joke quality (theory_content mean_paper)",
                 "P2 theory depth (craft/100, authored-flagged)",
                 "P4 arena votes (reserved, empty)"],
        "sweeps": ["0:1", "1:3", "1:1", "3:1", "1:0"],
        "n_full": n_full,
        "rows": rows,
    }, indent=1))
    print("\nsaved rankings/house.json")


if __name__ == "__main__":
    main()
