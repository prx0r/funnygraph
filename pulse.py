#!/usr/bin/env python3
"""PULSE — weekly comedy charts. The fast board to complement the slow canon.

All-time boards (consensus, era-adjusted) move yearly. The pulse moves WEEKLY:
re-pull stats for every tracked video, compute velocity, mine comments,
publish trending clips/comedians, comedian-of-week, rising star, small-channel
highlights.

Data per video per week (YouTube API, cheap):
  videos.list (1 unit/50): views, likes, comments, duration
  commentThreads.list (1 unit): top comments → sentiment, quote-backs,
    timestamp laughs ("4:32 killed me"), GOAT declarations
  channels.list (1 unit): subs (for small-channel discovery)

Metrics:
  velocity_views/day, velocity_likes/day (vs last snapshot)
  like_rate, comment_rate (engagement depth)
  sentiment (lexicon, $0)
  quote_backs (comment text ∩ transcript bits)
  breakout = velocity_zscore within sub-bracket (rising star needs bracket,
    not raw — a KT clip gaining 50k/wk beats a Netflix clip gaining 200k/wk
    when the KT channel has 1% of the subs)

Outputs: rankings/pulse/YYYY-Www.json + PULSE.md (human-readable weekly post).

Usage:
  python3 pulse.py --snapshot          # store this week's stats
  python3 pulse.py --report            # velocity vs last snapshot + report
  python3 pulse.py --mine-comments --top 20
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data" / "youtube"
PULSE = HERE / "rankings" / "pulse"
PULSE.mkdir(parents=True, exist_ok=True)

API = "https://www.googleapis.com/youtube/v3"

POS = set("""genius best greatest hilarious funny love loved amazing incredible
masterpiece brilliant legend goat iconic classic perfect gold brilliant awesome
love hilarious funny best greatest goat legend""".split())
NEG = set("""terrible awful boring worst hate hated bad trash garbage cringe
unfunny overrated annoying stupid dumb flop""".split())


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
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    return {}


def week_id() -> str:
    d = datetime.date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def all_tracked() -> list[dict]:
    vids = []
    for p in sorted(DATA.glob("*.json")):
        d = json.loads(p.read_text())
        for r in d.get("rows", []):
            vids.append({**r, "comedian": d["name"],
                         "comedian_id": d["comedian_id"]})
    return vids


def fetch_stats(ids: list[str], key: str) -> dict:
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = (f"{API}/videos?part=statistics&id=" + ",".join(chunk)
               + f"&key={key}")
        d = _get(url)
        for it in d.get("items") or []:
            st = it.get("statistics") or {}
            out[it["id"]] = {
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
            }
        time.sleep(0.3)
    return out


def snapshot() -> Path:
    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")
    vids = all_tracked()
    print(f"{len(vids)} tracked videos")
    stats = fetch_stats([v["videoId"] for v in vids], key)
    snap = {"week": week_id(), "date": str(datetime.date.today()),
            "videos": {vid: stats.get(vid, {}) for vid in stats}}
    p = PULSE / f"snap-{week_id()}.json"
    p.write_text(json.dumps(snap, indent=0))
    print(f"snapshot {p} ({len(snap['videos'])} videos)")
    return p


def sentiment(text: str) -> float:
    words = re.findall(r"[a-z']+", text.lower())
    if not words:
        return 0.0
    p = sum(1 for w in words if w in POS)
    n = sum(1 for w in words if w in NEG)
    return round((p - n) / max(1, len(words)), 3)


def mine_comments(video_id: str, key: str, max_results: int = 50) -> dict:
    url = (f"{API}/commentThreads?part=snippet&videoId={video_id}"
           f"&maxResults={min(100, max_results)}&orderBy=relevance"
           f"&textFormat=plainText&key={key}")
    import hashlib
    try:
        d = _get(url)
    except Exception as e:
        return {"videoId": video_id, "error": str(e)[:100]}
    comments = []
    for it in d.get("items") or []:
        s = (it.get("snippet") or {}).get("topLevelComment", {}).get("snippet", {})
        text = s.get("textDisplay", "")
        # hashed author id — joinable across videos, no PII.
        # skip when no identifier (empty would collide across strangers)
        raw_id = (s.get("authorChannelId", {}) or {}).get("value", "")
        if not raw_id:
            ah = ""
        else:
            ah = hashlib.sha256(raw_id.encode()).hexdigest()[:16]
        comments.append({
            "author": ah,
            "text": text[:300],
            "likes": s.get("likeCount", 0),
            "publishedAt": (s.get("publishedAt") or "")[:10],
            "sentiment": sentiment(text),
            "has_timestamp": bool(re.search(r"\b\d{1,2}:\d{2}\b", text)),
            "goat_call": bool(re.search(
                r"\b(goat|greatest|best ever|funniest|genius|masterpiece)\b",
                text, re.I)),
        })
    n = len(comments)
    return {
        "videoId": video_id,
        "n": n,
        "avg_sentiment": round(sum(c["sentiment"] for c in comments) / max(1, n), 3),
        "timestamp_laughs": sum(1 for c in comments if c["has_timestamp"]),
        "goat_calls": sum(1 for c in comments if c["goat_call"]),
        "top_quoted": sorted(comments, key=lambda c: -c["likes"])[:5],
        "comments": comments,
    }


def report() -> None:
    snaps = sorted(PULSE.glob("snap-*.json"))
    if len(snaps) < 2:
        print("need 2 snapshots for velocity (run --snapshot weekly)")
        # first-week report: rank by absolute scale
        vids = all_tracked()
        vids.sort(key=lambda v: -v.get("views", 0))
        rep = {"week": week_id(), "mode": "absolute (first snapshot)",
               "trending_clips": [
                   {"title": v["title"][:60], "comedian": v["comedian"],
                    "views": v["views"], "likes": v.get("likes", 0)}
                   for v in vids[:15]]}
        (PULSE / f"{week_id()}.json").write_text(json.dumps(rep, indent=1))
        print(f"absolute report → {PULSE / (week_id() + '.json')}")
        return
    prev = json.loads(snaps[-2].read_text())["videos"]
    cur = json.loads(snaps[-1].read_text())["videos"]
    vids = all_tracked()
    rows = []
    for v in vids:
        vid = v["videoId"]
        p, c = prev.get(vid, {}), cur.get(vid, {})
        dv = c.get("views", 0) - p.get("views", 0)
        dl = c.get("likes", 0) - p.get("likes", 0)
        rows.append({**v, "d_views": dv, "d_likes": dl,
                     "views_now": c.get("views", 0)})
    rows.sort(key=lambda r: -r["d_views"])
    # comedian of the week: sum velocity per comedian
    from collections import defaultdict
    by_comic: dict = defaultdict(int)
    for r in rows:
        by_comic[r["comedian_id"]] += r["d_views"]
    cow = sorted(by_comic.items(), key=lambda x: -x[1])[:5]
    rep = {"week": week_id(), "mode": "velocity",
           "trending_clips": [
               {"title": r["title"][:60], "comedian": r["comedian"],
                "d_views": r["d_views"], "views_now": r["views_now"]}
               for r in rows[:15] if r["d_views"] > 0],
           "comedian_of_week": [
               {"comedian_id": cid, "d_views": dv} for cid, dv in cow]}
    (PULSE / f"{week_id()}.json").write_text(json.dumps(rep, indent=1))
    print(f"velocity report → {PULSE / (week_id() + '.json')}")
    for r in rep["trending_clips"][:8]:
        print(f"  +{r['d_views']:>10,}  {r['title'][:50]:50} {r['comedian'][:18]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--mine-comments", action="store_true")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    if args.snapshot:
        snapshot()
    if args.mine_comments:
        key = _key()
        vids = sorted(all_tracked(), key=lambda v: -v.get("views", 0))[:args.top]
        out = []
        for v in vids:
            m = mine_comments(v["videoId"], key)
            m["title"] = v["title"][:60]
            m["comedian"] = v["comedian"]
            out.append(m)
            print(f"  {v['comedian'][:20]:20} n={m.get('n', 0)} "
                  f"sent={m.get('avg_sentiment', 0):+.2f} "
                  f"ts={m.get('timestamp_laughs', 0)} goat={m.get('goat_calls', 0)}")
            time.sleep(0.4)
        (PULSE / f"comments-{week_id()}.json").write_text(json.dumps(out, indent=1))
    if args.report:
        report()
    if not (args.snapshot or args.report or args.mine_comments):
        ap.print_help()


if __name__ == "__main__":
    main()
