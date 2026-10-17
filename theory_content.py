#!/usr/bin/env python3
"""THEORY CONTENT — joke-quality evidence from characters2 bit annotations.

The Theory lens (metrics.py craft score) measures documentation depth, not
joke quality. This file builds the content half from characters2's theory
work — read-only, no copies, no duplication:

  characters2/theory/transcripts/bits_theory.json  29,617 bits x 18 comics
    per-bit: economy, incongruity, surprise, absurd, violation, benign,
    benign_violation, paper (calibrated), thesis, KR, comic, special
  characters2/theory/transcripts/bits_annotated/  ops per bit (bit-ops-v1)
  characters2/theory/transcripts/ml/operator_frequency.json  per-10k rates
  characters2/theory/transcripts/ml/laugh_density.json  per-special means

Computes (all joins on identical slugs):
  1. per-comic joke-quality aggregates: n_bits, mean/p90 paper score,
     mean bv/economy/incongruity/violation, operator entropy + top op,
     laugh-density aggregates. -> "who has the best jokes" (measured 18).
  2. per-TYPE boards: measured comics grouped by funnygraph humor_type,
     ranked by mean paper (n>=200 bits gate). -> best jokes per comedy type.
  3. fitted mechanism weights: mean paper per operator (with-op vs
     without-op lift). THInC-analog for stand-up: which mechanisms predict
     bit quality. (M5-redo input.)
  4. M5-redo: funnygraph AUTHORED operator_priors vs characters2 MEASURED
     normalized_priors, Pearson per comic over common ops. Validates (or
     kills) our authoring with independent measurement.

Usage: python3 theory_content.py [--c2 PATH]
Output: rankings/theory_content.json. Reads only, both repos.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from rank_comedians import load_comics

OUT = HERE / "rankings"
C2DEFAULT = Path("/root/characters2/theory")


def pearson(xs: list[float], ys: list[float]) -> float | None:
    try:
        return round(statistics.correlation(xs, ys), 3)
    except statistics.StatisticsError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--c2", default=str(C2DEFAULT))
    args = ap.parse_args()
    c2 = Path(args.c2)
    assert (c2 / "transcripts" / "bits_theory.json").exists(), \
        f"characters2 theory not found at {c2}"

    bt = json.loads((c2 / "transcripts" / "bits_theory.json").read_text())
    print(f"{len(bt)} theory bits")

    # ops per bit_id from bits_annotated
    ops_of: dict[str, list[str]] = {}
    for p in (c2 / "transcripts" / "bits_annotated").rglob("*.bits.json"):
        try:
            d = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for b in d.get("bits") or []:
            if b.get("bit_id"):
                ops_of[b["bit_id"]] = b.get("ops") or []
    print(f"{len(ops_of)} bits with ops")

    opfreq = json.loads((c2 / "transcripts" / "ml" / "operator_frequency.json")
                        .read_text())
    laughden = json.loads((c2 / "transcripts" / "ml" / "laugh_density.json")
                          .read_text())

    # ── 1. per-comic aggregates ──
    per: dict[str, dict] = defaultdict(lambda: {
        "papers": [], "bv": [], "eco": [], "inc": [], "vio": [],
        "op_counts": defaultdict(int), "n_ops_bits": 0})
    op_papers: dict[str, list[float]] = defaultdict(list)
    all_papers: list[float] = []
    for bid, t in bt.items():
        c = t.get("comic")
        if not c:
            continue
        p = t.get("paper")
        if not isinstance(p, (int, float)):
            continue
        r = per[c]
        r["papers"].append(p)
        all_papers.append(p)
        for k, kk in (("bv", "benign_violation"), ("eco", "economy"),
                      ("inc", "incongruity"), ("vio", "violation")):
            v = t.get(kk)
            if isinstance(v, (int, float)):
                r[k].append(v)
        for op in ops_of.get(bid, []):
            r["op_counts"][op] += 1
            op_papers[op].append(p)
        if ops_of.get(bid):
            r["n_ops_bits"] += 1

    comics = load_comics()
    name_of = {c: j.get("name", c) for c, j in comics.items()}
    type_of = {c: (j.get("humor_type") or j.get("identity") or {})
               for c, j in comics.items()}

    def htype(cid: str) -> str | None:
        j = comics.get(cid) or {}
        ht = j.get("humor_type")
        if isinstance(ht, dict) and ht.get("primary"):
            return ht["primary"]
        if isinstance(ht, str) and ht:
            return ht
        for k in ("humorType", "type"):
            v = j.get(k)
            if isinstance(v, str) and v:
                return v
            if isinstance(v, dict) and v.get("id"):
                return v["id"]
        ident = j.get("identity") or {}
        v = ident.get("humor_type")
        if isinstance(v, str) and v:
            return v
        if isinstance(v, dict) and v.get("primary"):
            return v["primary"]
        return None

    rows = []
    for c, r in sorted(per.items()):
        ps = sorted(r["papers"])
        n = len(ps)
        mean_p = statistics.mean(ps)
        p90 = ps[int(0.9 * n)]
        # operator entropy (breadth) + signature (top op)
        tot = sum(r["op_counts"].values()) or 1
        ent = -sum((v / tot) * math.log(v / tot)
                   for v in r["op_counts"].values() if v > 0)
        top = max(r["op_counts"].items(),
                  key=lambda kv: kv[1])[0] if r["op_counts"] else None
        # laugh density aggregates
        lds = laughden.get(c) or []
        means = [s.get("mean_laugh_pred") for s in lds
                 if isinstance(s.get("mean_laugh_pred"), (int, float))]
        hot = [s.get("hot_unit_frac") for s in lds
               if isinstance(s.get("hot_unit_frac"), (int, float))]
        # measured priors (characters2) for M5-redo
        meas = (opfreq.get(c) or {}).get("normalized_priors") or {}
        rows.append({
            "comedian_id": c,
            "name": name_of.get(c, c),
            "humor_type": htype(c),
            "in_funnygraph": c in comics,
            "n_bits": n,
            "mean_paper": round(mean_p, 4),
            "p90_paper": round(p90, 4),
            "mean_bv": round(statistics.mean(r["bv"]), 4) if r["bv"] else None,
            "mean_economy": round(statistics.mean(r["eco"]), 4) if r["eco"] else None,
            "mean_incongruity": round(statistics.mean(r["inc"]), 4) if r["inc"] else None,
            "mean_violation": round(statistics.mean(r["vio"]), 4) if r["vio"] else None,
            "op_entropy": round(ent, 3),
            "top_op": top,
            "ops_coverage": round(r["n_ops_bits"] / n, 3) if n else 0,
            "mean_laugh_pred": round(statistics.mean(means), 4) if means else None,
            "mean_hot_frac": round(statistics.mean(hot), 4) if hot else None,
            "_meas_priors": meas,
        })
    rows.sort(key=lambda r: -r["mean_paper"])
    print("\nbest jokes (mean paper, measured comics):")
    for r in rows[:8]:
        print(f"  {r['name'][:22]:22} paper {r['mean_paper']:.4f} "
              f"p90 {r['p90_paper']:.4f} n={r['n_bits']} [{r['humor_type']}]")

    # ── 2. per-type boards ──
    by_type: dict[str, list] = defaultdict(list)
    for r in rows:
        if r["in_funnygraph"] and r["humor_type"] and r["n_bits"] >= 200:
            by_type[r["humor_type"]].append(r)
    type_boards = {}
    for t, rs in sorted(by_type.items()):
        rs = sorted(rs, key=lambda r: -r["mean_paper"])
        slim = []
        for i, r in enumerate(rs, 1):
            slim.append({"rank": i, "comedian_id": r["comedian_id"],
                         "name": r["name"], "mean_paper": r["mean_paper"],
                         "p90_paper": r["p90_paper"], "n_bits": r["n_bits"],
                         "top_op": r["top_op"]})
        type_boards[t] = {"n_measured": len(rs), "thin": len(rs) < 2,
                          "rows": slim}
    print(f"\n{len(type_boards)} types with measured comics: "
          + ", ".join(f"{t}({v['n_measured']})" for t, v in type_boards.items()))

    # ── 3. fitted mechanism weights ──
    base = statistics.mean(all_papers)
    mech = []
    for op, ps in sorted(op_papers.items()):
        if len(ps) < 50:
            continue
        m = statistics.mean(ps)
        mech.append({"op": op, "n_bits": len(ps),
                     "mean_paper": round(m, 4),
                     "lift_vs_global": round(m - base, 4)})
    mech.sort(key=lambda m: -m["mean_paper"])
    print("\nmechanism weights (mean paper | op present):")
    for m_ in mech[:8]:
        print(f"  {m_['op']:22} n={m_['n_bits']:>5} paper {m_['mean_paper']:.4f} "
              f"lift {m_['lift_vs_global']:+.4f}")

    # ── 4. M5-redo: authored vs measured priors ──
    m5 = []
    for r in rows:
        if not r["in_funnygraph"]:
            continue
        auth = ((comics[r["comedian_id"]].get("identity") or {})
                .get("operator_priors") or {})
        auth = {k: v for k, v in auth.items()
                if isinstance(v, (int, float))}
        meas = r["_meas_priors"]
        common = [k for k in auth if k in meas]
        if len(common) < 3:
            continue
        rho = pearson([auth[k] for k in common], [meas[k] for k in common])
        m5.append({"comedian_id": r["comedian_id"], "name": r["name"],
                   "n_common_ops": len(common), "pearson": rho})
    valid = [m_["pearson"] for m_ in m5 if m_["pearson"] is not None]
    m5mean = round(statistics.mean(valid), 3) if valid else None
    print(f"\nM5-redo: authored vs measured priors, {len(m5)} comics, "
          f"mean Pearson = {m5mean} (old M5 text-proxy: r=-0.05)")
    for m_ in sorted(
            m5, key=lambda m: -(m["pearson"]
                                if m["pearson"] is not None else -9))[:5]:
        print(f"  {m_['name'][:22]:22} r={m_['pearson']} (n={m_['n_common_ops']})")

    for r in rows:
        r.pop("_meas_priors", None)
    (OUT / "theory_content.json").write_text(json.dumps({
        "note": "Joke-quality evidence from characters2 bit annotations "
                "(read live; nothing copied). mean_paper = calibrated paper "
                "score (laughter-fitted rubric). Type boards gated n>=200 "
                "bits. Mechanism weights = mean paper | op present.",
        "source": {"repo": str(c2), "n_bits": len(bt),
                   "n_ops_bits": len(ops_of)},
        "global_mean_paper": round(base, 4),
        "comics": rows,
        "by_type": type_boards,
        "mechanism_weights": mech,
        "m5_redo": {"mean_pearson": m5mean, "per_comic": m5,
                    "note": "authored operator_priors vs measured "
                            "normalized_priors (characters2 ml). Old M5 "
                            "used text proxies (r=-0.05); this is the "
                            "direct test."},
    }, indent=1))
    print("\nsaved rankings/theory_content.json")


if __name__ == "__main__":
    main()
