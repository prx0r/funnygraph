#!/usr/bin/env python3
"""ENRICH RATINGS — IMDb public datasets → special ratings/votes/year.

Free, no key: datasets.imdbws.com/title.{basics,ratings}.tsv.gz
Matches our transcript titles to IMDb entries, writes specials[] with
rating/votes/year into each graph. standout = highest-rated special.

Usage:
  python3 enrich_ratings.py           # match all comedians
  python3 enrich_ratings.py --rebuild # rebuild specials[] from scratch
"""
from __future__ import annotations

import gzip
import json
import re
import sys
from pathlib import Path
try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
TR = HERE / "transcripts"
IMDB_BASICS = Path("/tmp/title.basics.tsv.gz")
IMDB_RATINGS = Path("/tmp/title.ratings.tsv.gz")


def load_ratings() -> dict:
    r = {}
    with gzip.open(IMDB_RATINGS, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 3:
                r[parts[0]] = (float(parts[1]), int(parts[2]))
    print(f"ratings: {len(r)} entries")
    return r


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[''`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def load_comedy_index(ratings: dict, min_votes: int = 25) -> list[dict]:
    """IMDb basics filtered to comedy specials-ish entries with ratings."""
    idx = []
    with gzip.open(IMDB_BASICS, "rt", encoding="utf-8") as f:
        header = next(f).rstrip("\n").split("\t")
        ti = {h: i for i, h in enumerate(header)}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < len(header):
                continue
            ttype = p[ti["titleType"]]
            if ttype not in ("movie", "tvSpecial", "video", "tvMovie"):
                continue
            genres = p[ti["genres"]] or ""
            if "Comedy" not in genres:
                continue
            tconst = p[ti["tconst"]]
            if tconst not in ratings:
                continue
            rating, votes = ratings[tconst]
            if votes < min_votes:
                continue
            try:
                year = int(p[ti["startYear"]]) if p[ti["startYear"]] not in ("\\N", "") else 0
            except ValueError:
                year = 0
            idx.append({
                "tconst": tconst,
                "primary": p[ti["primaryTitle"]] or "",
                "original": p[ti["originalTitle"]] or "",
                "year": year, "rating": rating, "votes": votes,
                "n_primary": norm(p[ti["primaryTitle"]] or ""),
                "n_original": norm(p[ti["originalTitle"]] or ""),
            })
    print(f"comedy index: {len(idx)} entries")
    return idx


def parse_special_title(stem: str, comedian_name: str) -> tuple[str, int]:
    """'nate-bargatze-the-tennessee-kid-transcript' → ('the tennessee kid', 0)."""
    s = stem.lower().replace("-transcript", "").replace("_transcript", "")
    cn = norm(comedian_name)
    s = s.replace("-", " ")
    # strip comedian name prefix
    for variant in (cn, cn.replace(" ", "")):
        if s.startswith(variant):
            s = s[len(variant):].strip()
            break
    # year at end?
    year = 0
    m = re.search(r"\b(19|20)\d{2}\b", s)
    if m:
        year = int(m.group(0))
    title = re.sub(r"\b(19|20)\d{2}\b", "", s).strip(" -")
    title = re.sub(r"\b(full|transcript)\b", "", title).strip(" -")
    return title, year


def match_special(title: str, year: int, comic_norm: str,
                  idx: list[dict]) -> dict | None:
    nt = norm(title)
    if len(nt) < 4:
        return None
    # strip generic suffixes that cause false hits
    nt = re.sub(r"\b(full transcript|transcript|full|special|live|uncut)\b", "", nt).strip()
    if len(nt) < 4:
        return None
    # short titles MUST contain the comedian's name (kills "Up", "Live", "Raw" false hits)
    comic_words = [w for w in comic_norm.split() if len(w) > 3]
    needs_name = len(nt) < 15
    cands = []
    nt_words = [w for w in nt.split() if len(w) > 3]
    for e in idx:
        hit = nt in e["n_primary"] or nt in e["n_original"] or \
            e["n_primary"] in nt or e["n_original"] in nt
        if not hit:
            continue
        # year must agree if we have one
        if year and e["year"] and abs(e["year"] - year) > 1:
            continue
        # comedian name should appear in the IMDb title (most specials are "Name: Special")
        cn_hit = any(w in e["n_primary"] for w in comic_words)
        if needs_name and not cn_hit:
            continue
        # matched IMDb title must share ≥2 distinctive words with parsed title,
        # OR contain the comedian name (kills 'Up', 'Live', single-word collisions).
        # BLACKLISTED ids never match (franchise collisions).
        if e["tconst"] in ("tt1049413",):
            continue
        imdb_words = set((e["n_primary"] + " " + e["n_original"]).split())
        overlap = sum(1 for w in nt_words if w in imdb_words)
        if overlap < 2 and not cn_hit:
            continue
        # comedian name in title required, always (specials are 'Name: Special')
        if not cn_hit:
            continue
        score = e["votes"] + (100000 if cn_hit else 0)
        cands.append((score, e))
    if not cands:
        return None
    cands.sort(key=lambda x: -x[0])
    return cands[0][1]


def main() -> None:
    rebuild = "--rebuild" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    ratings = load_ratings()
    idx = load_comedy_index(ratings)
    n_match = n_total = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        if d.name in EXCLUDED:
            continue
        cid = d.name
        if only and cid not in only:
            continue
        j = json.loads(g.read_text())
        name = j.get("name", cid)
        cn = norm(name)
        specials = [] if rebuild else j.get("specials_rated") or []
        seen = {s.get("imdb_id") for s in specials}
        tdir = TR / cid
        files = sorted(tdir.glob("*.txt")) if tdir.exists() else []
        # also characters2 transcripts
        c2 = Path(f"/root/characters2/theory/transcripts/{cid}")
        if c2.exists():
            files += sorted(c2.glob("*.txt"))
        for tp in files:
            title, year = parse_special_title(tp.stem, name)
            m = match_special(title, year, cn, idx)
            n_total += 1
            if m and m["tconst"] not in seen:
                specials.append({
                    "title": m["primary"], "year": m["year"],
                    "imdb_id": m["tconst"],
                    "imdb_rating": m["rating"], "imdb_votes": m["votes"],
                    "transcript": tp.name,
                })
                seen.add(m["tconst"])
                n_match += 1
        if specials:
            specials.sort(key=lambda s: -(s.get("imdb_rating", 0) or 0))
            # standout = top-rated with real vote base
            for s in specials:
                s.pop("standout", None)
            top = max((s for s in specials if s.get("imdb_votes", 0) >= 500),
                      key=lambda s: s.get("imdb_rating", 0), default=None)
            if top:
                top["standout"] = True
            j["specials_rated"] = specials
            g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
    print(f"\n=== matched {n_match}/{n_total} transcript files to IMDb ===")


if __name__ == "__main__":
    main()
