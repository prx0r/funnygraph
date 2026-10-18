#!/usr/bin/env python3
"""Build the funnier substrate: one clean clips corpus.

Merges:
  1. R2-linked clips from data/youtube/*.json (2,373, with transcripts)
  2. Discovered clips from uploads harvest (4,806, video-only)
  3. Special transcript links (79, video+transcript full specials)

Dedups by videoId. Output: data/clips_substrate.jsonl — one clip per
line, funnier-compatible fields + transcript_url + duration + topics
hint from title.

Funnier clip schema reference (site/clips.json):
  id, comic, fg, title, channel, kind, media, checked, venue,
  style[], topics[], format, carrier, setting, region, tags{}

Our substrate adds (not in funnier's committed schema, but needed
for karaoke + comparison):
  duration_s, views, transcript_url, words_timed, source
"""
from __future__ import annotations
import json, re, time
from pathlib import Path
from collections import defaultdict

LOCAL = Path("/root/funnygraph")
OUT = LOCAL / "data"
YT = OUT / "youtube"
DISC = OUT / "youtube_discovered"
R2DIR = OUT / "r2"

def band(dur):
    if dur is None: return None
    if dur <= 75: return "short"
    if dur <= 180: return "mid"
    if dur <= 420: return "long"
    return "xl"

def format_of(dur, title=""):
    # funnier's detect-format: vertical if shorts-like
    if dur and dur <= 60 and ("#shorts" in title.lower() or "shorts" in title.lower()):
        return "vertical"
    return "horizontal"

def title_topics(title, topics_tree=None):
    """Very rough topic hint from title keywords. Funnier does proper tagging."""
    if not topics_tree:
        return []
    t = (title or "").lower()
    hits = []
    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "kw":
                    continue
                walk(v, path + [k])
        elif isinstance(node, list):
            pass
    # simple: just return empty — funnier has its own tagger
    return []

def main():
    clips = {}  # videoId -> clip dict

    # 1. R2-linked clips from data/youtube
    n_r2 = 0
    for f in YT.glob("*.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        slug = d.get("comedian_id") or f.stem
        name = d.get("name") or slug.replace("-", " ").title()
        for row in d.get("rows") or []:
            vid = row.get("videoId")
            if not vid or vid in clips:
                continue
            clips[vid] = {
                "id": vid,
                "comic": name,
                "fg": slug,
                "title": row.get("title"),
                "channel": row.get("channel"),
                "kind": "human",
                "media": "youtube",
                "duration_s": row.get("duration_s"),
                "band": band(row.get("duration_s")),
                "format": format_of(row.get("duration_s"), row.get("title")),
                "views": row.get("views"),
                "url": row.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "transcript_url": row.get("transcript_url"),
                "words_timed": row.get("words_timed"),
                "transcript_method": row.get("transcript_method"),
                "n_words": row.get("n_words"),
                "source": "r2-linked",
                "setting": "stand-up",
                "carrier": "official",
                "region": "uk",
            }
            n_r2 += 1

    # 2. Discovered clips (uploads harvest)
    n_disc = 0
    disc_f = DISC / "discovered_clips.json"
    if disc_f.exists():
        disc = json.loads(disc_f.read_text())
        for row in disc.get("clips", []):
            vid = row.get("videoId")
            if not vid or vid in clips:
                continue
            clips[vid] = {
                "id": vid,
                "comic": row.get("comedian_slug", "").replace("-", " ").title(),
                "fg": row.get("comedian_slug"),
                "title": row.get("title"),
                "channel": row.get("channel"),
                "kind": "human",
                "media": "youtube",
                "duration_s": row.get("duration_s"),
                "band": band(row.get("duration_s")),
                "format": format_of(row.get("duration_s"), row.get("title")),
                "views": row.get("views"),
                "url": row.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "transcript_url": None,
                "words_timed": False,
                "source": "uploads-harvest",
                "setting": "stand-up",
                "carrier": "official",
                "region": None,
            }
            n_disc += 1

    # 3. Special transcript links (full specials with video+transcript)
    n_sp = 0
    sp_f = DISC / "special_transcript_links.json"
    if sp_f.exists():
        spl = json.loads(sp_f.read_text())
        for row in spl.get("links", []):
            vid = row.get("videoId")
            if not vid:
                continue
            if vid in clips:
                # upgrade existing with transcript
                clips[vid]["transcript_url"] = row.get("r2_special_key") and \
                    f"https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com/comedy-specials/{row['r2_special_key']}"
                clips[vid]["words_timed"] = row.get("words_timed")
                clips[vid]["n_words"] = row.get("n_words")
                clips[vid]["setting"] = "special"
                clips[vid]["is_special"] = True
            else:
                clips[vid] = {
                    "id": vid,
                    "comic": row.get("comedian_slug", "").replace("-", " ").title(),
                    "fg": row.get("comedian_slug"),
                    "title": row.get("title"),
                    "channel": row.get("channel"),
                    "kind": "human",
                    "media": "youtube",
                    "duration_s": row.get("duration_s"),
                    "band": band(row.get("duration_s")),
                    "format": format_of(row.get("duration_s"), row.get("title")),
                    "views": row.get("views"),
                    "url": row.get("url") or f"https://www.youtube.com/watch?v={vid}",
                    "transcript_url": row.get("r2_special_key") and \
                        f"https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com/comedy-specials/{row['r2_special_key']}",
                    "words_timed": row.get("words_timed"),
                    "n_words": row.get("n_words"),
                    "source": "special-link",
                    "setting": "special",
                    "carrier": "official",
                    "region": None,
                    "is_special": True,
                }
            n_sp += 1

    # Finalize: add checked date, sort by views
    now = time.strftime("%Y-%m-%d")
    rows = list(clips.values())
    for r in rows:
        r["checked"] = now
    rows.sort(key=lambda r: r.get("views") or 0, reverse=True)

    # Write JSONL (funnier-friendly streaming format)
    out_f = OUT / "clips_substrate.jsonl"
    with open(out_f, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    # Also write a compact index for quick queries
    idx = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_clips": len(rows),
        "n_with_transcript": sum(1 for r in rows if r.get("transcript_url")),
        "n_timed": sum(1 for r in rows if r.get("words_timed")),
        "n_specials": sum(1 for r in rows if r.get("is_special")),
        "sources": {
            "r2-linked": n_r2,
            "uploads-harvest": n_disc,
            "special-link": n_sp,
        },
        "by_comedian": {},
        "by_band": {},
    }
    for r in rows:
        fg = r.get("fg") or "?"
        idx["by_comedian"][fg] = idx["by_comedian"].get(fg, 0) + 1
        b = r.get("band") or "?"
        idx["by_band"][b] = idx["by_band"].get(b, 0) + 1
    (OUT / "clips_substrate_index.json").write_text(json.dumps(idx, indent=1))

    print(f"=== SUBSTRATE BUILT ===")
    print(f"  total clips:     {len(rows)}")
    print(f"  with transcript: {idx['n_with_transcript']}")
    print(f"  timed (karaoke): {idx['n_timed']}")
    print(f"  full specials:   {idx['n_specials']}")
    print(f"  comedians:       {len(idx['by_comedian'])}")
    print(f"  by band:         {idx['by_band']}")
    print(f"  wrote: data/clips_substrate.jsonl ({out_f.stat().st_size/1024/1024:.1f}MB)")
    print(f"  wrote: data/clips_substrate_index.json")

if __name__ == "__main__":
    main()
