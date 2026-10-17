#!/usr/bin/env python3
"""YOUTUBE HARVEST — every comedian's clips with views/likes/comments.

YouTube Data API v3 (key in .env, gitignored):
  search.list (100 units) → top clips per comedian
  videos.list (1 unit/50 ids) → views, likes, comments, duration, date

Quota math: 10k units/day default. 1 search (100) + 1 stats call (1) per
comedian ≈ 101 × 181 = 18k — over daily. So: --top N flag, resume cache,
and prefer channel-uploads (1 unit) where channel IDs are known.

Stores: data/youtube/{cid}.json per comedian (all clips + aggregates).
Publishes: rankings/clips.json (top clips), rankings/channels.json.

Usage:
  python3 youtube_harvest.py --top 60
  python3 youtube_harvest.py --only shane-gillis,theo-von
  python3 youtube_harvest.py --resume
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
DATA = HERE / "data" / "youtube"
DATA.mkdir(parents=True, exist_ok=True)

API = "https://www.googleapis.com/youtube/v3"


def _key() -> str:
    k = os.getenv("YOUTUBE_DATA_API_KEY", "").strip()
    if k:
        return k
    env = HERE / ".env"
    if env.exists():
        for ln in env.read_text().splitlines():
            if ln.startswith("YOUTUBE_DATA_API_KEY="):
                return ln.split("=", 1)[1].strip()
    return ""


def _get(url: str) -> dict:
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:
            body = ""
            try:
                body = e.read()[:300] if hasattr(e, "read") else ""
            except Exception:
                pass
            if attempt == 2:
                raise RuntimeError(f"yt api fail: {e} {body}")
            time.sleep(1 + attempt)
    return {}


def parse_dur(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)


def search_clips(name: str, key: str, max_results: int = 10) -> list[dict]:
    q = urllib.parse.quote(f"{name} standup comedy special clip")
    url = (f"{API}/search?part=snippet&q={q}&type=video&maxResults={max_results}"
           f"&order=viewCount&videoEmbeddable=true&key={key}")
    d = _get(url)
    out = []
    for it in d.get("items") or []:
        vid = (it.get("id") or {}).get("videoId")
        sn = it.get("snippet") or {}
        if vid:
            out.append({"videoId": vid, "title": sn.get("title", ""),
                        "channel": sn.get("channelTitle", ""),
                        "publishedAt": sn.get("publishedAt", "")[:10]})
    return out


def video_stats(ids: list[str], key: str) -> dict:
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = (f"{API}/videos?part=statistics,contentDetails,snippet&id="
               + ",".join(chunk) + f"&key={key}")
        d = _get(url)
        for it in d.get("items") or []:
            st = it.get("statistics") or {}
            cd = it.get("contentDetails") or {}
            sn = it.get("snippet") or {}
            out[it["id"]] = {
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
                "duration_s": parse_dur(cd.get("duration", "")),
                "title": sn.get("title", ""),
                "channel": sn.get("channelTitle", ""),
                "publishedAt": (sn.get("publishedAt") or "")[:10],
            }
        time.sleep(0.3)
    return out


def harvest(cid: str, name: str, key: str, n: int = 10) -> dict:
    clips = search_clips(name, key, max_results=n)
    stats = video_stats([c["videoId"] for c in clips], key) if clips else {}
    rows = []
    for c in clips:
        s = stats.get(c["videoId"], {})
        rows.append({
            "videoId": c["videoId"],
            "title": s.get("title") or c["title"],
            "channel": s.get("channel") or c["channel"],
            "publishedAt": s.get("publishedAt") or c["publishedAt"],
            **{k: s.get(k, 0) for k in ("views", "likes", "comments", "duration_s")},
        })
    rows.sort(key=lambda r: -r["views"])
    tot_v = sum(r["views"] for r in rows)
    tot_l = sum(r["likes"] for r in rows)
    agg = {
        "comedian_id": cid, "name": name,
        "clips": len(rows), "total_views": tot_v, "total_likes": tot_l,
        "avg_views": tot_v // max(1, len(rows)),
        "like_rate": round(tot_l / max(1, tot_v), 5),
        "top_clip": rows[0] if rows else None,
        "rows": rows,
    }
    (DATA / f"{cid}.json").write_text(json.dumps(agg, indent=1))
    return agg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=0, help="top N by current rank")
    ap.add_argument("--only", default="")
    ap.add_argument("--n", type=int, default=8, help="clips per comedian")
    args = ap.parse_args()
    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")

    comics = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if g.exists():
            j = json.loads(g.read_text())
            comics.append((d.name, j.get("name", d.name)))
    if args.only:
        want = set(args.only.split(","))
        comics = [(c, n) for c, n in comics if c in want]
    elif args.top:
        # rank order if available, else alpha
        try:
            board = json.loads((HERE / "rankings" / "consensus.json").read_text())
            order = [c["comedian_id"] for c in board]
            comics.sort(key=lambda x: order.index(x[0]) if x[0] in order else 999)
        except (OSError, json.JSONDecodeError):
            pass
        comics = comics[:args.top]

    print(f"{len(comics)} comedians × ~101 units ≈ {len(comics)*101} quota")
    done = 0
    for cid, name in comics:
        if (DATA / f"{cid}.json").exists():
            continue
        try:
            a = harvest(cid, name, key, n=args.n)
            done += 1
            print(f"  {cid}: {a['clips']} clips, "
                  f"{a['total_views']:,} views, top={a['top_clip']['views'] if a['top_clip'] else 0:,}")
        except Exception as e:
            print(f"  {cid} FAIL: {e}")
        time.sleep(0.5)
    print(f"\n=== {done} harvested, data/youtube/ ===")


if __name__ == "__main__":
    main()
