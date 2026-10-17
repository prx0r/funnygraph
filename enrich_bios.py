#!/usr/bin/env python3
"""ENRICH BIOS — Wikidata DOB/birthplace/citizenship for every comedian.

Free, CC0, no key. wbsearchentities (name → QID) + wbgetentities (claims).
Writes bio{} into each comedian-graph.json. Slow but thorough (~2s/comic).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
CACHE = HERE / "wikidata_cache.json"

UA = {"User-Agent": "funnygraph/1.0 (comedy research database; contact: research@pogtown.com)"}


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


def search(name: str) -> str | None:
    url = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="
           + urllib.parse.quote(name) + "&language=en&format=json&limit=5")
    d = _get(url)
    for it in d.get("search", []):
        desc = (it.get("description") or "").lower()
        label = (it.get("label") or "").lower()
        # must look like a person, preferably comedian/comic/actor
        if any(w in desc for w in ("comedian", "comic", "stand-up", "actor",
                                   "actress", "humorist", "entertainer")):
            return it["id"]
    # fallback: first human-looking hit
    for it in d.get("search", []):
        if "born" in (it.get("description") or "").lower():
            return it["id"]
    return None


def claims(qid: str) -> dict:
    url = (f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}"
           f"&format=json&props=claims|labels&languages=en")
    d = _get(url)
    ent = (d.get("entities") or {}).get(qid, {})
    return ent.get("claims", {})


def _time_val(cl: dict, prop: str) -> str | None:
    for c in cl.get(prop, []):
        try:
            v = c["mainsnak"]["datavalue"]["value"]["time"]
            # +1987-12-11T00:00:00Z → 1987-12-11
            return v.lstrip("+").split("T")[0]
        except (KeyError, TypeError):
            continue
    return None


def _item_label(qid: str) -> str:
    url = (f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}"
           f"&format=json&props=labels&languages=en")
    try:
        d = _get(url)
        return ((d.get("entities") or {}).get(qid, {}).get("labels", {})
                .get("en", {}).get("value", qid))
    except Exception:
        return qid


def _item_val(cl: dict, prop: str) -> tuple[str | None, str | None]:
    for c in cl.get(prop, []):
        try:
            qid = c["mainsnak"]["datavalue"]["value"]["id"]
            return qid, _item_label(qid)
        except (KeyError, TypeError):
            continue
    return None, None


def enrich(cid: str, name: str) -> dict | None:
    qid = search(name)
    if not qid:
        return None
    cl = claims(qid)
    dob = _time_val(cl, "P569")
    dod = _time_val(cl, "P570")
    _, pob = _item_val(cl, "P19")
    _, citz = _item_val(cl, "P27")
    occs = []
    for c in cl.get("P106", [])[:4]:
        try:
            oq = c["mainsnak"]["datavalue"]["value"]["id"]
            occs.append(_item_label(oq))
        except (KeyError, TypeError):
            continue
    return {"wikidata_id": qid, "dob": dob, "dod": dod,
            "birthplace": pob, "citizenship": citz,
            "occupations": occs, "source": "wikidata (CC0)"}


def main() -> None:
    only = sys.argv[1:] or None
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    n_hit = n_miss = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        cid = d.name
        if only and cid not in only:
            continue
        j = json.loads(g.read_text())
        if j.get("bio", {}).get("wikidata_id") and "--refresh" not in sys.argv:
            continue
        name = j.get("name", cid)
        if cid in cache:
            bio = cache[cid]
        else:
            print(f"  {cid} ({name})...", flush=True)
            try:
                bio = enrich(cid, name)
            except Exception as e:
                print(f"    fail: {e}")
                bio = None
            cache[cid] = bio
            CACHE.write_text(json.dumps(cache, indent=1))
            time.sleep(0.6)
        if bio:
            j["bio"] = bio
            g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
            n_hit += 1
            print(f"    {bio.get('dob')} · {bio.get('birthplace')} · {bio.get('wikidata_id')}")
        else:
            n_miss += 1
            print("    no match")
    print(f"\n=== bios: {n_hit} hit, {n_miss} miss ===")


if __name__ == "__main__":
    main()
