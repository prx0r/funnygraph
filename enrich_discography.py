#!/usr/bin/env python3
"""DISCOGRAPHY — comedy album metadata via MusicBrainz (no key, polite).

Albums date careers: a 1992 debut hour on wax pins breakthrough decade
better than any bio; tracklists enumerate hours; labels trace scenes
(Dry Bar, 800 Pound Gorilla, Comedy Central Records, Sub Pop).
Metadata only (titles/years/labels) — no audio, no transcripts.

Two-phase (disambiguation is the whole ballgame):
  --resolve  name -> MB artist candidates; KEEP only comedy-tagged
             (standup comedy/comedy/spokenword); writes musicbrainz_id +
             candidates to graph (status needs-review on ambiguity).
  --pull     verified MBIDs (status ok) -> release-groups (albums) ->
             graph.discography[] {title, year, label, type}.

Rate limit: 1 req/sec STRICT (503s otherwise). Free, no key, CC0-ish
(MetaBrainz open data).
Usage: python3 enrich_discography.py --resolve [--only slug] | --pull
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
UA = {"User-Agent": "funnygraph/1.0 (comedy research database)"}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def norm(s: str) -> str:
    return re.sub(r"[^a-z]+", "", s.lower())


def resolve() -> None:
    try:
        from exclude import EXCLUDED
    except ImportError:
        EXCLUDED = set()
    n_ok = n_rev = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        j = json.loads(g.read_text())
        mb = j.get("musicbrainz") or {}
        if mb.get("status") == "ok":
            continue
        name = j.get("name", d.name)
        r = None
        for _try in range(3):
            try:
                r = _get("https://musicbrainz.org/ws/2/artist/?query=artist:"
                         + urllib.parse.quote(name) + "&fmt=json&limit=10")
                break
            except Exception as e:
                print(f"  {d.name} retry {_try} {type(e).__name__}")
                time.sleep(5 + 5 * _try)
        if r is None:
            time.sleep(2.0)
            continue
        cands = []
        for a in r.get("artists", []):
            tags = {t.get("name", "").lower()
                    for t in (a.get("tags") or [])}
            an = a.get("name", "")
            if norm(an) != norm(name):
                continue
            funny = bool(tags & {"standup comedy", "stand-up comedy", "comedy",
                                 "spokenword", "spoken word"})
            cands.append({"id": a.get("id"), "name": an,
                          "tags": sorted(tags)[:6], "funny": funny,
                          "score": a.get("score")})
        funny = [c for c in cands if c["funny"]]
        if len(funny) == 1:
            j["musicbrainz"] = {"id": funny[0]["id"], "status": "ok",
                                "tags": funny[0]["tags"],
                                "source": "musicbrainz (name+comedy-tag)"}
            n_ok += 1
            print(f"  OK {d.name} -> {funny[0]['id'][:8]}")
        elif funny:
            j["musicbrainz"] = {"status": "needs-review",
                                "candidates": funny[:4],
                                "source": "musicbrainz (ambiguous)"}
            n_rev += 1
            print(f"  REVIEW {d.name}: {len(funny)} comedy candidates")
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        time.sleep(1.2)
    print(f"resolved ok={n_ok} review={n_rev}")


def pull() -> None:
    n = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        mb = j.get("musicbrainz") or {}
        if mb.get("status") != "ok" or not mb.get("id"):
            continue
        if j.get("discography"):
            continue
        try:
            r = _get(f"https://musicbrainz.org/ws/2/release-group/?artist={mb['id']}"
                     "&type=album&fmt=json&limit=100")
        except Exception as e:
            print(f"  {d.name} pull fail {type(e).__name__}")
            time.sleep(1.2)
            continue
        discs = []
        for rg in r.get("release-groups", []):
            discs.append({"title": rg.get("title"),
                          "year": (rg.get("first-release-date") or "")[:4] or None,
                          "label": None, "mbid": rg.get("id")})
        discs.sort(key=lambda x: (x["year"] or "9999"))
        j["discography"] = discs
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        n += 1
        if discs:
            print(f"  {d.name}: {len(discs)} releases ({discs[0]['year']}–{discs[-1]['year']})")
        time.sleep(1.2)
    print(f"discographies pulled: {n}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--pull", action="store_true")
    args = ap.parse_args()
    if args.resolve:
        resolve()
    if args.pull:
        pull()
    if not (args.resolve or args.pull):
        ap.print_help()


if __name__ == "__main__":
    main()
