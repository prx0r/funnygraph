#!/usr/bin/env python3
"""YOUTUBE HARVEST v2 — NO SEARCH. Registry channels → uploads playlists.

Quota: channels.list (1) + playlistItems (1/50) + videos.list (1/50) +
channels subs (1/50). A 2000-video channel costs ~45 units TOTAL vs 100
for ONE search. Complete enumeration, zero guessing, zero quota burn.

Registry: data/channels.json (comedian_id → [channel IDs]). Curated only —
add confirmed IDs, never search.

Usage:
  python3 youtube_harvest2.py --only mark-normand
  python3 youtube_harvest2.py --top 60
  python3 youtube_harvest2.py --all
  python3 youtube_harvest2.py --add-channel shane-gillis UCxxxx  # register
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
try:
    from exclude import EXCLUDED, filter_ids
except ImportError:
    EXCLUDED = set()
    def filter_ids(x): return x

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
DATA = HERE / "data" / "youtube"
DATA.mkdir(parents=True, exist_ok=True)
REG = HERE / "data" / "channels.json"

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
                body = e.read()[:200] if hasattr(e, "read") else ""
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


def sub_bracket(subs: int) -> str:
    if subs < 10_000:
        return "micro (<10k)"
    if subs < 100_000:
        return "small (<100k)"
    if subs < 1_000_000:
        return "mid (<1M)"
    return "big (1M+)"


def uploads_playlist(channel_id: str, key: str) -> tuple[str, dict]:
    d = _get(f"{API}/channels?part=contentDetails,statistics,snippet&id="
             f"{channel_id}&key={key}")
    items = d.get("items") or []
    if not items:
        raise RuntimeError(f"no channel {channel_id}")
    it = items[0]
    st = it.get("statistics") or {}
    return (it["contentDetails"]["relatedPlaylists"]["uploads"],
            {"subs": int(st.get("subscriberCount", 0)),
             "channel_views": int(st.get("viewCount", 0)),
             "channel": (it.get("snippet") or {}).get("title", "")})


def playlist_videos(pl: str, key: str, cap: int = 200) -> list[dict]:
    """All video IDs in an uploads playlist (paginated, 1 unit/page)."""
    out, token = [], ""
    while len(out) < cap:
        url = (f"{API}/playlistItems?part=contentDetails&maxResults=50"
               f"&playlistId={pl}&key={key}" + (f"&pageToken={token}" if token else ""))
        d = _get(url)
        for it in d.get("items") or []:
            vid = (it.get("contentDetails") or {}).get("videoId")
            if vid:
                out.append({"videoId": vid})
        token = d.get("nextPageToken", "")
        if not token:
            break
        time.sleep(0.2)
    return out[:cap]


def video_stats(ids: list[str], key: str) -> dict:
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = (f"{API}/videos?part=statistics,contentDetails,snippet&id="
               + ",".join(chunk) + f"&key={key}")
        d = _get(url)
        for it in d.get("items") or []:
            st, cd, sn = it.get("statistics") or {}, it.get("contentDetails") or {}, it.get("snippet") or {}
            try:
                out[it["id"]] = {
                    "views": int(st.get("viewCount", 0)),
                    "likes": int(st.get("likeCount", 0)),
                    "comments": int(st.get("commentCount", 0)),
                    "duration_s": parse_dur(cd.get("duration", "")),
                    "title": sn.get("title", ""),
                    "publishedAt": (sn.get("publishedAt") or "")[:10],
                }
            except (TypeError, ValueError):
                continue
        time.sleep(0.3)
    return out


def is_standup(title: str) -> bool:
    t = title.lower()
    # keep standup-ish, drop obvious non-sets (podcast eps kept — they're discovery)
    return True  # keep everything from official channels; filter at analysis


def harvest(cid: str, name: str, key: str, channels: list[str],
            cap: int = 200) -> dict:
    rows = []
    chan_info: dict = {}
    for ch in channels:
        try:
            pl, info = uploads_playlist(ch, key)
            chan_info[ch] = info
            vids = playlist_videos(pl, key, cap=cap)
            stats = video_stats([v["videoId"] for v in vids], key)
            for v in vids:
                s = stats.get(v["videoId"])
                if not s:
                    continue
                rows.append({
                    "videoId": v["videoId"],
                    "title": s["title"],
                    "channel": info["channel"],
                    "channelId": ch,
                    "channel_subs": info["subs"],
                    "bracket": sub_bracket(info["subs"]),
                    "publishedAt": s["publishedAt"],
                    "views": s["views"], "likes": s["likes"],
                    "comments": s["comments"],
                    "duration_s": s["duration_s"],
                })
        except Exception as e:
            print(f"    channel {ch} fail: {e}")
    # keep standup-relevant: filter obvious junk, cap at top 100 by views
    rows = [r for r in rows if is_standup(r["title"])]
    rows.sort(key=lambda r: -r["views"])
    rows = rows[:100]
    tot_v = sum(r["views"] for r in rows)
    tot_l = sum(r["likes"] for r in rows)
    agg = {
        "comedian_id": cid, "name": name,
        "channels": chan_info,
        "clips": len(rows), "total_views": tot_v, "total_likes": tot_l,
        "avg_views": tot_v // max(1, len(rows)),
        "like_rate": round(tot_l / max(1, tot_v), 5),
        "top_clip": rows[0] if rows else None,
        "rows": rows,
        "method": "registry-uploads (no search)",
    }
    (DATA / f"{cid}.json").write_text(json.dumps(agg, indent=1))
    return agg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--top", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--cap", type=int, default=200)
    ap.add_argument("--add-channel", nargs=2, metavar=("COMEDIAN", "CHANNEL_ID"))
    args = ap.parse_args()

    reg = json.loads(REG.read_text())

    if args.add_channel:
        cid, chid = args.add_channel
        reg.setdefault(cid, [])
        if chid not in reg[cid]:
            reg[cid].append(chid)
            REG.write_text(json.dumps(reg, indent=1) + "\n")
            print(f"registered {chid} for {cid}")
        else:
            print("already registered")
        return

    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")

    targets = []
    _reg_skip = EXCLUDED
    if args.only:
        for cid in args.only.split(","):
            cid = cid.strip()
            if cid in reg:
                targets.append(cid)
            else:
                print(f"no channels registered for {cid} "
                      f"(use --add-channel {cid} UCxxxx)")
    elif args.all:
        targets = [c for c in reg if not c.startswith("_")
                   and not c.startswith("kill-tony")
                   and not c.startswith("netflix")
                   and not c.startswith("team-")
                   and not c.startswith("tonight")]
    elif args.top:
        try:
            board = json.loads((HERE / "rankings" / "consensus.json").read_text())
            order = [c["comedian_id"] for c in board]
        except (OSError, json.JSONDecodeError):
            order = []
        cids = [c for c in order if c in reg][:args.top]
        # plus registry carriers
        targets = cids
    else:
        ap.print_help()
        return

    targets = [t for t in targets if t not in EXCLUDED]
    print(f"{len(targets)} targets (uploads playlists, ~1 unit/50 vids)")
    for cid in targets:
        try:
            g = json.loads((COMEDIANS / cid / "comedian-graph.json").read_text())
            name = g.get("name", cid)
        except (OSError, json.JSONDecodeError):
            name = cid
        try:
            a = harvest(cid, name, key, reg[cid], cap=args.cap)
            print(f"  {cid}: {a['clips']} clips, {a['total_views']:,} views")
        except Exception as e:
            print(f"  {cid} FAIL: {e}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
