#!/usr/bin/env python3
"""RECOGNITION — rankings through the years + awards into every graph.

Sources (all free):
  CC100  Comedy Central 100 Greatest Stand-ups (2004) — /tmp/cc100.json
  RS50   Rolling Stone 50 Best (2017) — /tmp/rs50.json
  AWARDS Wikidata P166 (award received) — Grammy Best Comedy Album,
         Mark Twain Prize, Emmys, etc. — live SPARQL-ish via wbgetentities
  IMDb   specials_rated (already in graphs) = current audience verdict

The trajectory (CC2004 → RS2017 → IMDb now) IS rankings through the years.
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
CACHE = HERE / "wikidata_cache.json"

UA = {"User-Agent": "funnygraph/1.0 (comedy research database; contact: research@pogtown.com)"}


def norm(s: str) -> str:
    s = s.lower().replace("’", "").replace("'", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load_ranks() -> dict:
    out = {}
    cc = {int(k): v for k, v in json.loads(Path("/tmp/cc100.json").read_text()).items()}
    cc[1] = "Richard Pryor"
    cc[4] = "Woody Allen"
    rs = {int(k): v for k, v in json.loads(Path("/tmp/rs50.json").read_text()).items()}
    return {"cc2004": cc, "rs2017": rs}


def match_rank(name: str, rankmap: dict) -> int | None:
    nn = norm(name)
    # exact-ish: all words of rank name appear
    for rank, rname in rankmap.items():
        rn = norm(rname)
        if nn == rn or nn.replace(" ", "") == rn.replace(" ", ""):
            return rank
        # last-name + first-name containment both ways
        nw, rw = set(nn.split()), set(rn.split())
        if nw and rw and (nw <= rw or rw <= nw):
            return rank
    return None


def _get(url: str) -> dict:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    return {}


def awards_for(qid: str) -> list[dict]:
    """P166 award received + year (P585 point in time) where present."""
    url = (f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}"
           f"&format=json&props=claims&languages=en")
    try:
        d = _get(url)
    except Exception:
        return []
    ent = (d.get("entities") or {}).get(qid, {})
    out = []
    for c in ent.get("claims", {}).get("P166", []):
        try:
            aq = c["mainsnak"]["datavalue"]["value"]["id"]
            # label
            lurl = (f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={aq}"
                    f"&format=json&props=labels&languages=en")
            ld = _get(lurl)
            label = ((ld.get("entities") or {}).get(aq, {}).get("labels", {})
                     .get("en", {}).get("value", aq))
            # year
            year = None
            for q in (c.get("qualifiers", {}).get("P585", [])):
                try:
                    t = q["datavalue"]["value"]["time"]
                    year = int(t.lstrip("+")[:4])
                    break
                except (KeyError, TypeError, ValueError):
                    continue
            out.append({"award": label, "year": year})
            time.sleep(0.3)
        except (KeyError, TypeError):
            continue
    # keep the ones that matter, cap at 12
    keep = [a for a in out if any(
        w in a["award"].lower() for w in
        ("grammy", "mark twain", "emmy", "peabody", "kennedy",
         "pulitzer", "tony", "oscar", "golden globe", "eddie",
         "writers guild", "producers guild", "critics"))] or out[:12]
    return keep[:12]


def main() -> None:
    ranks = load_ranks()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    n_rank = n_aw = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        j = json.loads(g.read_text())
        name = j.get("name", d.name)
        rec = j.get("recognition") or {}
        cc = match_rank(name, ranks["cc2004"])
        rs = match_rank(name, ranks["rs2017"])
        if cc:
            rec["comedy_central_2004"] = cc
        if rs:
            rec["rolling_stone_2017"] = rs
        if cc or rs:
            n_rank += 1
        # trajectory: rise/fall/stable between 2004→2017 (lower rank = better)
        if cc and rs:
            rec["trajectory_2004_2017"] = (
                "rise" if rs < cc else "fall" if rs > cc else "stable")
        # awards via cached QID
        bio = j.get("bio") or {}
        qid = bio.get("wikidata_id") or (cache.get(d.name) or {}).get("wikidata_id")
        if qid and "awards" not in rec:
            print(f"  {d.name} awards...", flush=True)
            try:
                aw = awards_for(qid)
                if aw:
                    rec["awards"] = aw
                    n_aw += 1
                    print(f"    {len(aw)} awards")
                else:
                    rec["awards"] = []
                time.sleep(0.5)
            except Exception as e:
                print(f"    fail: {e}")
        if rec:
            j["recognition"] = rec
            g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
    print(f"\n=== rankings: {n_rank} comics ranked, awards: {n_aw} ===")


if __name__ == "__main__":
    main()
