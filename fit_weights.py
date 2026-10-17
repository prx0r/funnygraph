#!/usr/bin/env python3
"""FIT WEIGHTS — hide RS2017, predict it from CC2004+IMDb+awards. Learn weights."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from rank_comedians import load_comics, imdb_wr, award_score

comics = load_comics()
both = [cid for cid, j in comics.items()
        if (j.get("recognition") or {}).get("comedy_central_2004")
        and (j.get("recognition") or {}).get("rolling_stone_2017")]
print(f"{len(both)} comedians on both lists (fitting set)")


def kendall(pred_order, true_order):
    pos = {c: i for i, c in enumerate(pred_order)}
    tp = {c: i for i, c in enumerate(true_order)}
    common = [c for c in pred_order if c in tp]
    conc = disc = 0
    for i in range(len(common)):
        for k in range(i + 1, len(common)):
            a, b = common[i], common[k]
            if (tp[a] - tp[b]) * (pos[a] - pos[b]) > 0:
                conc += 1
            else:
                disc += 1
    return conc / (conc + disc) if conc + disc else 0


true_rs = sorted(
    both, key=lambda c: comics[c]["recognition"]["rolling_stone_2017"])

# precompute features
feat = {}
for cid, j in comics.items():
    rec = j.get("recognition") or {}
    cc = rec.get("comedy_central_2004", 101)
    feat[cid] = {
        "cc": (101 - cc) / 100,
        "imdb": (imdb_wr(j.get("specials_rated") or []) or 7.0) / 10,
        "aw": min(award_score(rec.get("awards", [])) / 5, 1),
    }

best = None
for wc in [1, 2, 3, 4, 5]:
    for wa in [0, 1, 2, 3]:
        for waw in [0, 1, 2]:
            scores = {cid: wc * f["cc"] + wa * f["imdb"] + waw * f["aw"]
                      for cid, f in feat.items()}
            pred = sorted(comics, key=lambda c: -scores[c])
            tau = kendall(pred, true_rs)
            if best is None or tau > best[0]:
                best = (tau, wc, wa, waw)
print(f"BEST concordance {best[0]:.3f} at CC={best[1]} IMDb={best[2]} awards={best[3]}")
# current weights score
scores = {cid: 3 * f["cc"] + 2 * f["imdb"] + 1 * f["aw"]
          for cid, f in feat.items()}
pred = sorted(comics, key=lambda c: -scores[c])
print(f"CURRENT (3,2,1): {kendall(pred, true_rs):.3f}")
# baseline: CC2004 alone predicts RS2017?
scores0 = {cid: f["cc"] for cid, f in feat.items()}
pred0 = sorted(comics, key=lambda c: -scores0[c])
print(f"BASELINE (CC only): {kendall(pred0, true_rs):.3f}")
