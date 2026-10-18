#!/usr/bin/env python3
"""Fix discovered specials: strict same-comedian matching + link into graphs.

The loose title match produced cross-comedian false positives.
This pass:
  1. Re-match specials to R2 specials ONLY within same comedian, strict overlap
  2. Write clean per-comedian discovered files
  3. Link videoIds into comedian graphs (youtube_specials block)
  4. Build clean site_special_links.json for embedding
"""
from __future__ import annotations
import json, re, time
from pathlib import Path
from collections import defaultdict

LOCAL = Path("/root/funnygraph")
OUT = LOCAL / "data" / "youtube_discovered"
R2DIR = LOCAL / "data" / "r2"
COMEDIANS = LOCAL / "comedians"

def title_words(t):
    return set(re.findall(r'[a-z]{4,}', (t or "").lower()))

def match_special(vid_title, sp_title, vid_slug=None, sp_slug=None):
    """Strict match: same comedian + significant word overlap."""
    if not vid_title or not sp_title:
        return False
    a, b = title_words(vid_title), title_words(sp_title)
    if not a or not b:
        return False
    overlap = a & b
    # require ≥2 overlapping content words OR one very distinctive word ≥7 chars
    if len(overlap) >= 2:
        return True
    if any(len(w) >= 7 and w in overlap for w in overlap):
        return True
    return False

def main():
    spec = json.loads((OUT / "discovered_specials.json").read_text())
    clips = json.loads((OUT / "discovered_clips.json").read_text())

    # Load R2 specials by comedian
    r2_sp = defaultdict(list)  # slug -> [special dict]
    for f in (R2DIR / "specials").glob("*.json"):
        d = json.loads(f.read_text())
        for s in d.get("specials", []):
            r2_sp[d["comedian_slug"]].append(s)

    # Re-match strictly
    clean_matches = []
    unmatched = []
    for s in spec["specials"]:
        slug = s["comedian_slug"]
        matched = None
        for sp in r2_sp.get(slug, []):
            if match_special(s["title"], sp.get("title"), slug, sp.get("special_slug")):
                matched = sp
                break
        if matched:
            clean_matches.append({**s, "r2_special_key": matched.get("r2_special_key"),
                                   "r2_special_slug": matched.get("special_slug"),
                                   "n_words": matched.get("n_words"),
                                   "words_timed": matched.get("words_timed")})
        else:
            unmatched.append(s)

    print(f"strict matches: {len(clean_matches)} (was 505 loose)")
    print(f"unmatched: {len(unmatched)}")

    # Save clean matches
    (OUT / "special_transcript_links.json").write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "YouTube full specials whose videoIds are now linked to R2 transcripts",
        "n": len(clean_matches),
        "links": clean_matches,
    }, indent=1))

    # Per-comedian clean links
    links_by_slug = defaultdict(list)
    for m in clean_matches:
        links_by_slug[m["comedian_slug"]].append(m)

    # Link into graphs: youtube_specials block
    linked_graphs = 0
    for slug, items in sorted(links_by_slug.items()):
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            continue
        g = json.loads(gpath.read_text())
        ys = g.setdefault("youtube_specials", [])
        existing_vids = {x.get("videoId") for x in ys}
        new = 0
        for it in items:
            if it["videoId"] in existing_vids:
                continue
            ys.append({
                "videoId": it["videoId"],
                "title": it["title"],
                "duration_s": it["duration_s"],
                "views": it.get("views"),
                "url": it.get("url") or f"https://www.youtube.com/watch?v={it['videoId']}",
                "r2_special_key": it.get("r2_special_key"),
                "r2_special_slug": it.get("r2_special_slug"),
                "transcript_linked": True,
            })
            new += 1
        if new:
            g["youtube_specials_count"] = len(ys)
            gpath.write_text(json.dumps(g, indent=1) + "\n")
            linked_graphs += 1

    # Also link unmatched specials (video-only, no transcript yet) as embeds
    unmatched_by_slug = defaultdict(list)
    for s in unmatched:
        unmatched_by_slug[s["comedian_slug"]].append(s)
    for slug, items in sorted(unmatched_by_slug.items()):
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            continue
        g = json.loads(gpath.read_text())
        ys = g.setdefault("youtube_specials", [])
        existing = {x.get("videoId") for x in ys}
        new = 0
        for it in items:
            if it["videoId"] in existing:
                continue
            ys.append({
                "videoId": it["videoId"],
                "title": it["title"],
                "duration_s": it["duration_s"],
                "views": it.get("views"),
                "url": it.get("url") or f"https://www.youtube.com/watch?v={it['videoId']}",
                "transcript_linked": False,
            })
            new += 1
        if new:
            g["youtube_specials_count"] = len(ys)
            gpath.write_text(json.dumps(g, indent=1) + "\n")

    # Clean discovered_clips: add url field
    for c in clips.get("clips", []):
        if not c.get("url"):
            c["url"] = f"https://www.youtube.com/watch?v={c['videoId']}"
    (OUT / "discovered_clips.json").write_text(json.dumps(clips, indent=1))

    # Stats
    with_transcript = sum(1 for c in COMEDIANS.glob("*/comedian-graph.json")
                          if json.loads(c.read_text()).get("youtube_specials_count"))
    total_linked = sum(
        len(json.loads(c.read_text()).get("youtube_specials") or [])
        for c in COMEDIANS.glob("*/comedian-graph.json")
    )
    print(f"\n=== LINKED ===")
    print(f"  strict transcript links: {len(clean_matches)}")
    print(f"  graphs with youtube_specials: {with_transcript}")
    print(f"  total specials linked in graphs: {total_linked}")
    print(f"  clean links file: data/youtube_discovered/special_transcript_links.json")

if __name__ == "__main__":
    main()
