#!/usr/bin/env python3
"""NETFLIX REPORTS — official What We Watched hours/views per comedy special.

Downloads Netflix's 7 engagement reports (H1 2023 – H1 2026, ~18k titles each,
99% of viewing), filters to comedy specials matching our comedians, sums
hours + views across halves.

This is platform-reported special viewership — the answer to "who actually
watches specials" that YouTube clips (distribution-weighted) can't give.
Chappelle's gated specials show up here. Normand's YouTube advantage doesn't.

Report URLs from girl.surgery/netflix_engagement/reproduce.py (public).

Usage: python3 netflix_reports.py
Output: rankings/netflix_specials.json (per-special hours/views by half)
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
OUT = HERE / "rankings"
DL = HERE / "data" / "netflix_reports"
DL.mkdir(parents=True, exist_ok=True)

REPORTS = {
    "2023H1": "https://assets.ctfassets.net/4cd45et68cgf/1HyknFM84ISQpeua6TjM7A/97a0a393098937a8f29c9d29c48dbfa8/What_We_Watched_A_Netflix_Engagement_Report_2023Jan-Jun.xlsx",
    "2023H2": "https://assets.ctfassets.net/4cd45et68cgf/inuAnzotdsAEgbInGLzH5/1be323ba419b2af3a96bffa29acc31a3/What_We_Watched_A_Netflix_Engagement_Report_2023Jul-Dec.xlsx",
    "2024H1": "https://assets.ctfassets.net/4cd45et68cgf/2PoZlfdc46dH2gQvI8eUzI/9db5840720c47acfcf7b89ffe2402860/What_We_Watched_A_Netflix_Engagement_Report_2024Jan-Jun.xlsx",
    "2024H2": "https://assets.ctfassets.net/4cd45et68cgf/6XSmoEjBjVMPRtYybT9d1E/8c0b0b2645b8712d5597b0bdbe0d64e2/What_We_Watched_A_Netflix_Engagement_Report_2024Jul-Dec.xlsx",
    "2025H1": "https://assets.ctfassets.net/4cd45et68cgf/mplcXj5ulHDfbCPCr0f0I/5dbb6ec09f03df89706476e380e9b8bd/What_We_Watched_A_Netflix_Engagement_Report_2025Jan-Jun.xlsx",
    "2025H2": "https://assets.ctfassets.net/4cd45et68cgf/2vdDPGLKA0XX2cjF2APJFn/7f1c367b39ed73a6a588751d3c5d0252/What_We_Watched_A_Netflix_Engagement_Report_2025Jul-Dec__6_.xlsx",
    "2026H1": "https://assets.ctfassets.net/4cd45et68cgf/40WGcHJa9vRua31kU6Gbz5/43b15c7fbd6924392fc80e885839e39f/Netflix-s_What_We_Watched_Report_2026Jan-Jun__1_.xlsx",
}


def comic_names() -> dict:
    """comedian_id → [name words for matching]."""
    out = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            name = json.loads(g.read_text()).get("name", "")
        except (OSError, json.JSONDecodeError):
            continue
        words = [w for w in re.sub(r"[^a-z0-9]+", " ", name.lower()).split()
                 if len(w) > 2]
        if words:
            out[d.name] = (name, words)
    return out


def download():
    import urllib.request
    paths = {}
    for half, url in REPORTS.items():
        p = DL / f"{half}.xlsx"
        if p.exists() and p.stat().st_size > 100000:
            print(f"  {half}: cached ({p.stat().st_size // 1000000}MB)")
        else:
            print(f"  {half}: downloading...", flush=True)
            req = urllib.request.Request(
                url, headers={"User-Agent": "funnygraph/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(p, "wb") as f:
                f.write(r.read())
            print(f"    {p.stat().st_size // 1000000}MB")
        paths[half] = p
    return paths


def harvest(paths: dict, comics: dict) -> list[dict]:
    import openpyxl
    found: dict = {}
    for half, p in paths.items():
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        ws = wb.active
        started = False
        n = 0
        for row in ws.iter_rows(values_only=True):
            if not started:
                if len(row) > 1 and row[1] == "Title":
                    started = True
                continue
            if not row or len(row) < 5 or not row[1]:
                continue
            title = str(row[1])
            hours = row[4] or 0
            # views column varies by report; runtime col too — grab generously
            views = 0
            for v in row[5:9]:
                if isinstance(v, (int, float)) and v > 1000:
                    # views are much larger than runtime-minutes; take the big one
                    views = max(views, int(v))
                    break
            tl = re.sub(r"[^a-z0-9]+", " ", title.lower())
            tl_words = set(tl.split())
            for cid, (name, words) in comics.items():
                # whole-word matching ("amer" must not match "american")
                hit = sum(1 for w in words if w in tl_words)
                # need ALL name words as whole words
                if hit < len(words):
                    continue
                key = (cid, title)
                f = found.setdefault(key, {
                    "comedian_id": cid, "comedian": name,
                    "title": title, "halves": {},
                })
                try:
                    f["halves"][half] = {"hours": int(hours or 0),
                                         "views": int(views or 0)}
                except (TypeError, ValueError):
                    pass
                break
            n += 1
        print(f"  {half}: scanned {n} rows, {len(found)} comedy matches so far")
        wb.close()
    out = []
    for f in found.values():
        f["total_hours"] = sum(h["hours"] for h in f["halves"].values())
        f["total_views"] = sum(h["views"] for h in f["halves"].values())
        out.append(f)
    out.sort(key=lambda x: -x["total_hours"])
    return out


def main() -> None:
    comics = comic_names()
    print(f"{len(comics)} comedians")
    paths = download()
    specials = harvest(paths, comics)
    (OUT / "netflix_specials.json").write_text(json.dumps(specials, indent=1))
    print(f"\n=== NETFLIX SPECIAL VIEWERSHIP (top 25 by hours) ===")
    for s in specials[:25]:
        print(f"  {s['total_hours']:>12,}h  {s['title'][:50]:50} {s['comedian'][:20]}")
    # per-comedian rollup into graphs
    roll: dict = {}
    for s in specials:
        r = roll.setdefault(s["comedian_id"],
                            {"hours": 0, "views": 0, "specials": 0})
        r["hours"] += s["total_hours"]
        r["views"] += s["total_views"]
        r["specials"] += 1
    for cid, r in roll.items():
        g = COMEDIANS / cid / "comedian-graph.json"
        if g.exists():
            j = json.loads(g.read_text())
            j["netflix_viewership"] = {**r, "source": "What We Watched 2023H1-2026H1"}
            g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
    print(f"\n{specials} specials, {len(roll)} comedians with Netflix hours")


if __name__ == "__main__":
    main()
