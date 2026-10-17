#!/usr/bin/env python3
"""SPLIT BOARDS — obey the fitted result (GAPS.md #7).

fit_weights.py proved averaging critics + audience destroys signal
(CC-only 0.692 > weighted 0.658): they are different elections.
This file publishes them as different elections:

  CANON board (rankings/canon.json): critics + awards only — the
    establishment election. Weights are MALLOWS-IMPLIED precisions
    (rankings/mallows.json), renormalized over the two legs:
    no asserted weights anywhere in this file.
  PEOPLE'S board (rankings/peoples.json): audience WR only, ranked by
    standout-special weighted rating. Momentum (standout-special recency
    percentile) is a SHOWN column, never blended: blending without
    velocity data would repeat the asserted-weights sin (GAPS.md).

The weighted consensus remains the legacy view; these two are primary.
Kings only, exclusion-guarded (via load_comics). Reads only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kendall_w import compute_legs
from rank_comedians import imdb_wr, load_comics

OUT = HERE / "rankings"


def main() -> None:
    comics = load_comics()
    legs = compute_legs(comics)

    # ── CANON: critics + awards, Mallows-implied weights ──
    mal = json.loads((OUT / "mallows.json").read_text())["legs"]
    wsum = mal["critics"]["precision_neglogphi"] + \
        mal["awards"]["precision_neglogphi"]
    wc = mal["critics"]["precision_neglogphi"] / wsum
    wa = mal["awards"]["precision_neglogphi"] / wsum
    print(f"canon weights from mallows.json: critics={wc:.3f} awards={wa:.3f}")
    canon = sorted(comics,
                   key=lambda c: -(wc * legs["critics"][c]
                                    + wa * legs["awards"][c]))
    canon_rows = []
    for i, cid in enumerate(canon, 1):
        j = comics[cid]
        canon_rows.append({
            "rank": i,
            "comedian_id": cid,
            "name": j.get("name", cid),
            "score": round(wc * legs["critics"][cid]
                           + wa * legs["awards"][cid], 4),
            "critics": legs["critics"][cid],
            "awards": legs["awards"][cid],
            "generation": (j.get("generation") or {}).get("id"),
        })
    (OUT / "canon.json").write_text(json.dumps({
        "note": "ALL-TIME CANON: establishment election (critics + awards). "
                f"Weights fitted, not asserted (Mallows precision: {wc:.3f}/{wa:.3f}).",
        "weights": {"critics": round(wc, 4), "awards": round(wa, 4)},
        "rows": canon_rows,
    }, indent=1))

    # ── PEOPLE'S: audience WR only + momentum column ──
    rated = []
    for cid, j in comics.items():
        sp = j.get("specials_rated") or []
        ok = [s for s in sp if s.get("imdb_rating") and s.get("imdb_votes")]
        if not ok:
            continue
        w = imdb_wr(sp)
        best = max(ok, key=lambda x: (x.get("standout", False),
                                      x.get("imdb_rating", 0)))
        rated.append((cid, w, best))
    rated.sort(key=lambda r: -r[1])
    years = sorted({r[2].get("year") or 0 for r in rated if r[2].get("year")})
    ymin, ymax = (min(years), max(years)) if years else (0, 0)
    peoples = []
    for i, (cid, w, best) in enumerate(rated, 1):
        y = best.get("year") or ymin
        momentum = round((y - ymin) / max(1, ymax - ymin), 3)
        # approval rate: % of rated specials >= 7.5 (binary approval lens,
        # RT-Tomatometer-flavored; SHOWN not blended — means are gameable,
        # approval is robust. METHODOLOGY steal-list item, now live.)
        sp = comics[cid].get("specials_rated") or []
        ok = [s for s in sp if isinstance(s.get("imdb_rating"), (int, float))]
        appr = round(sum(1 for s in ok if s["imdb_rating"] >= 7.5)
                     / max(1, len(ok)), 3) if ok else None
        peoples.append({
            "rank": i,
            "comedian_id": cid,
            "name": comics[cid].get("name", cid),
            "wr": w,
            "standout": best.get("special") or best.get("title"),
            "standout_year": y,
            "standout_votes": best.get("imdb_votes"),
            "momentum_recency": momentum,
            "n_specials_rated": len(ok),
            "approval_rate": appr,
            "generation": (comics[cid].get("generation") or {}).get("id"),
        })
    (OUT / "peoples.json").write_text(json.dumps({
        "note": "PEOPLE'S CHOICE: audience election, ranked by standout-special "
                "IMDb WR (m=500, C=7.5). momentum_recency is SHOWN, not blended "
                "(no asserted weights).",
        "rows": peoples,
    }, indent=1))

    print("\nCANON top 10:")
    for r in canon_rows[:10]:
        print(f"  {r['rank']:>2} {r['name'][:24]:24} {r['score']:.3f}")
    print("\nPEOPLE'S top 10:")
    for r in peoples[:10]:
        print(f"  {r['rank']:>2} {r['name'][:24]:24} WR {r['wr']} "
              f"({r['standout_year']})")
    print("\nsaved rankings/canon.json + rankings/peoples.json")


if __name__ == "__main__":
    main()
