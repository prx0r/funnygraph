#!/usr/bin/env python3
"""NETFLIX VIEWS — real special viewership from Tudum weeklies (free, no key).

Netflix publishes weekly Top 10 with millions-of-views per title (static HTML
in article pages). This harvests comedy-special entries across recent weeklies:
special title + views + week → per-comedian viewership.

This is the specials-viewership answer: platform-reported watches, not
distribution-weighted YouTube clips. Normand doesn't win here by being
YouTube-native; Chappelle's gated specials show up here.

Usage:
  python3 netflix_views.py --weeks 12     # last 12 weekly articles
  python3 netflix_views.py --all          # full sitemap sweep (slow)
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "rankings"
UA = {"User-Agent": "funnygraph/1.0 (comedy research database; contact: research@pogtown.com)"}


def _get(url: str) -> str:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    return ""


def weekly_urls(n: int = 12) -> list[str]:
    """Generate recent Monday weekly top-10 article URLs (known pattern).

    Asks for 3x and lets 404s fall out (Tudum sometimes skips weeks).
    """
    import datetime
    out = []
    d = datetime.date.today()
    d -= datetime.timedelta(days=d.weekday())
    for _ in range(n * 3):
        slug = f"top-10-{d.strftime('%B').lower()}-{d.day}-{d.year}"
        out.append(f"https://www.netflix.com/tudum/articles/{slug}")
        d -= datetime.timedelta(days=7)
    return out[:n * 3]


def parse_weekly(html: str) -> list[dict]:
    """Extract (title, views_millions) for comedy-special-looking entries."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    out = []
    # pattern: "Title ... with X.X million views" / "premiered at No. N, with X.X million views"
    for m in re.finditer(
            r"([A-Z][A-Za-z0-9'&.,:!\-– ]{4,80}?)\s+"
            r"(?:premiered at No\. \d+|held|landed|debuted|took|claimed|locked in)[^.]{0,120}?"
            r"with ([\d.]+) million views", text):
        title = m.group(1).strip(" .,-–:")
        views = float(m.group(2))
        # comedy-special heuristic
        if re.search(r"\b(special|comedy|comedian|stand-?up|roast|tour|live)\b", title, re.I) or \
           re.search(r"\b(special|comedy|comedian|stand.?up|roast)\b",
                     text[max(0, m.start() - 300):m.start() + 200], re.I):
            out.append({"title": title, "views_m": views})
    return out


def match_comedian(title: str) -> str | None:
    """Match a Tudum title to a funnygraph comedian_id."""
    import unicodedata
    t = unicodedata.normalize("NFKD", title.lower())
    t = re.sub(r"[^a-z0-9]+", " ", t)
    best, best_score = None, 0
    for d in sorted((HERE / "comedians").iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            name = json.loads(g.read_text()).get("name", "")
        except (OSError, json.JSONDecodeError):
            continue
        nw = [w for w in re.sub(r"[^a-z0-9]+", " ", name.lower()).split()
              if len(w) > 2]
        if not nw:
            continue
        hit = sum(1 for w in nw if w in t)
        score = hit / len(nw)
        if hit >= 1 and score > best_score and (hit >= 2 or len(nw) == 1):
            best, best_score = d.name, score
    return best


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weeks", type=int, default=12)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    urls = weekly_urls(200 if args.all else args.weeks)
    print(f"{len(urls)} candidate articles")
    entries = []
    ok = need = args.weeks
    for u in urls:
        if ok <= 0:
            break
        week = re.search(r"(top-10-[a-z]+-\d+-?\d*)", u)
        wk = week.group(1) if week else u[-20:]
        try:
            html = _get(u)
        except Exception:
            continue
        found = parse_weekly(html)
        if not found:
            continue
        ok -= 1
        for e in found:
            cid = match_comedian(e["title"])
            entries.append({**e, "week": wk, "url": u, "comedian_id": cid})
        time.sleep(0.5)
    print(f"{len(entries)} comedy entries")
    (OUT / "netflix_views.json").write_text(json.dumps(entries, indent=1))

    # per-comedian rollup
    roll: dict = {}
    for e in entries:
        if not e["comedian_id"]:
            continue
        r = roll.setdefault(e["comedian_id"],
                            {"weeks": 0, "total_views_m": 0.0, "entries": []})
        r["weeks"] += 1
        r["total_views_m"] = round(r["total_views_m"] + e["views_m"], 1)
        r["entries"].append({"title": e["title"][:60], "week": e["week"],
                             "views_m": e["views_m"]})
    roll_list = sorted(roll.items(), key=lambda x: -x[1]["total_views_m"])
    (OUT / "netflix_comedians.json").write_text(
        json.dumps([{"comedian_id": k, **v} for k, v in roll_list], indent=1))
    print("=== NETFLIX VIEWERSHIP (Tudum weeklies) ===")
    for cid, r in roll_list[:15]:
        print(f"  {r['total_views_m']:>6.1f}M over {r['weeks']}wk  {cid}")
    unmatched = sum(1 for e in entries if not e["comedian_id"])
    print(f"unmatched entries: {unmatched}")


if __name__ == "__main__":
    main()
