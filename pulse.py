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

Outputs: rankings/pulse/YYYY-Www.json + rankings/spotlight.json (site board:
comedian_of_week, bracket_champs, rising_star, new_comic_of_week,
trending_clips).

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
import sys
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


def snap_id() -> str:
    import datetime as _dt
    now = _dt.datetime.now()
    # isocalendar week to match week_id() (%W disagreed: W41 vs W42 bug 2026-10-17)
    return now.strftime("%Y-W%V-%m%d-%H%M")


def all_tracked() -> list[dict]:
    vids = []
    for p in sorted(DATA.glob("*.json")):
        d = json.loads(p.read_text())
        for r in d.get("rows", []):
            vids.append({**r, "comedian": d["name"],
                         "comedian_id": d["comedian_id"]})
    return _reattr(vids)


def _reattr(vids: list[dict]) -> list[dict]:
    """KT-channel videos belong to the mined minute-performer, not the file
    owner. A past harvest filed Angie Stroud's minute under jim-jefferies
    and it crowned him rising star on her views (2026-10-17). Fix: mine
    the title (same rules as discovery); override when the slug exists.
    """
    try:
        sys.path.insert(0, str(HERE))
        from discover import names_from_title, ROAST_RE
    except Exception:
        return vids
    fixed = 0
    for v in vids:
        title = v.get("title", "")
        ch = v.get("channelId") or ""
        chname = v.get("channel", "") or ""
        is_kt = (ch == "UCwzCMiicL-hBUzyjWiJaseg"
                 or "kill tony" in chname.lower()
                 or bool(re.search(r"(^|\s)KT\s*#\d+|kill.?tony\s*#\d+",
                                   title, re.I)))
        if not is_kt:
            continue
        if ROAST_RE.search(title):
            continue
        full, _ = names_from_title(title)
        for name in full:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            if (HERE / "comedians" / slug / "comedian-graph.json").exists():
                if slug != v["comedian_id"]:
                    v["comedian_id"] = slug
                    v["comedian"] = name
                    fixed += 1
                break
    if fixed:
        print(f"reattributed {fixed} KT minutes to performers")
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
    # channel subs time-series (the rising-star instrument): subs velocity
    # is THE breakout signal for unknowns. channels.list, 1 unit / 50.
    ch_ids = sorted({v.get("channelId") for v in vids if v.get("channelId")})
    chans = {}
    for i in range(0, len(ch_ids), 50):
        try:
            d = _get(f"{API}/channels?part=statistics,snippet&id="
                     + ",".join(ch_ids[i:i + 50]) + f"&key={key}")
        except Exception as e:
            print(f"  channel batch fail: {type(e).__name__}")
            break
        for it in d.get("items") or []:
            st = it.get("statistics") or {}
            chans[it["id"]] = {
                "subs": int(st.get("subscriberCount", 0) or 0),
                "channel_views": int(st.get("viewCount", 0) or 0),
                "title": ((it.get("snippet") or {}).get("title") or "")[:60],
            }
        time.sleep(0.3)
    print(f"{len(chans)} channels with subs")
    snap = {"week": week_id(), "taken": snap_id(), "date": str(datetime.date.today()),
            "videos": {vid: stats.get(vid, {}) for vid in stats},
            "channels": chans}
    p = PULSE / f"snap-{snap_id()}.json"
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


def _profile(cid: str) -> dict:
    """tier + created + discovery for a comedian_id (new-comic join)."""
    try:
        j = json.loads((HERE / "comedians" / cid /
                        "comedian-graph.json").read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return {"tier": j.get("tier", "king"), "created": j.get("created", ""),
            "region": j.get("region", ""), "name": j.get("name", cid),
            "discovery": j.get("discovery") or {}}


def _is_new(cid: str, week: str) -> bool:
    """New comic = indie tier (discovery track), full stop.

    Graph `created` dates mean file-authored date (nearly all read
    2026-10-16/17 from the founding wave) — NOT career start. An earlier
    version used them and labeled Kevin Hart a new comic. Kings are
    established by tier definition; only indies are new.
    """
    return _profile(cid).get("tier") == "indie"


def report() -> None:
    snaps = sorted(PULSE.glob("snap-*.json"),
                   key=lambda p: p.stat().st_mtime)  # mtime, not filename
    if len(snaps) < 2:
        print("need 2 snapshots for velocity (run --snapshot weekly)")
        # first-week report: rank by absolute scale
        vids = all_tracked()
        vids.sort(key=lambda v: -v.get("views", 0))
        from collections import defaultdict as _dd
        by_comic: dict = _dd(int)
        for v in vids:
            by_comic[v["comedian_id"]] += v.get("views", 0)
        cow = sorted(by_comic.items(), key=lambda x: -x[1])[:5]
        newcomers = [(cid, vv) for cid, vv in by_comic.items()
                     if _is_new(cid, week_id())]
        newcomers.sort(key=lambda x: -x[1])
        rep = {"week": week_id(), "mode": "absolute (first snapshot)",
               "trending_clips": [
                   {"title": v["title"][:60], "comedian": v["comedian"],
                    "views": v["views"], "likes": v.get("likes", 0)}
                   for v in vids[:15]],
               "comedian_of_week": [
                   {"comedian_id": cid, "views": vv} for cid, vv in cow],
               "bracket_champs": {},
               "rising_star": None,
               "new_comic_of_week": (
                   {"comedian_id": newcomers[0][0],
                    "views": newcomers[0][1], "basis": "absolute-scale"}
                   if newcomers else None)}
        (PULSE / f"{week_id()}.json").write_text(json.dumps(rep, indent=1))
        (HERE / "rankings" / "spotlight.json").write_text(
            json.dumps(rep, indent=1))
        print(f"absolute report → {PULSE / (week_id() + '.json')} + spotlight.json")
        return
    prev = json.loads(snaps[-2].read_text())["videos"]
    cur = json.loads(snaps[-1].read_text())["videos"]
    prev_ch = json.loads(snaps[-2].read_text()).get("channels", {})
    cur_ch = json.loads(snaps[-1].read_text()).get("channels", {})
    vids = all_tracked()
    rows, newly = [], []
    for v in vids:
        vid = v["videoId"]
        p, c = prev.get(vid, {}), cur.get(vid, {})
        if vid not in prev:
            # first-seen video: lifetime views are NOT weekly velocity.
            # Listed separately, never in velocity boards.
            newly.append({**v, "views_now": c.get("views", 0)})
            continue
        dv = c.get("views", 0) - p.get("views", 0)
        dl = c.get("likes", 0) - p.get("likes", 0)
        rows.append({**v, "d_views": dv, "d_likes": dl,
                     "views_now": c.get("views", 0)})
    rows.sort(key=lambda r: -r["d_views"])
    newly.sort(key=lambda r: -r.get("views_now", 0))
    # comedian of the week: sum velocity per comedian (raw scale board)
    from collections import defaultdict
    import statistics as _st
    by_comic: dict = defaultdict(int)
    for r in rows:
        by_comic[r["comedian_id"]] += r["d_views"]
    cow = sorted(by_comic.items(), key=lambda x: -x[1])[:5]
    # bracketed velocity: z-score of d_views within channel-size bracket.
    # A KT clip gaining 50k/wk beats Netflix gaining 200k/wk at 1% subs.
    by_bracket: dict = defaultdict(list)
    for r in rows:
        by_bracket[r.get("bracket", "unbracketed")].append(r)
    bracket_champs = {}
    zrows = []
    for br, rs in by_bracket.items():
        dvs = [r["d_views"] for r in rs]
        mu = _st.mean(dvs) if dvs else 0
        sd = _st.pstdev(dvs) if len(dvs) > 1 else 0
        for r in rs:
            z = round((r["d_views"] - mu) / sd, 2) if sd > 0 else 0.0
            zrows.append({**r, "vel_z": z})
        # gate: no champ on a flat (zero-velocity) window — snapshots too
        # close together produce all-zero deltas, and crowning noise as
        # signal is exactly what this file exists to prevent.
        if len(rs) >= 3 and sd > 0 and max(dvs) > 0:
            top = max(rs, key=lambda r: (r["d_views"] - mu))
            bracket_champs[br] = {
                "comedian_id": top["comedian_id"],
                "title": top["title"][:60], "d_views": top["d_views"],
                "z": round((top["d_views"] - mu) / sd, 2)}
    # rising star: top bracket-z among discovery/indie or small brackets,
    # gated on positive velocity (same flat-window rule).
    small_br = [z for z in zrows
                if z["d_views"] > 0 and
                (z.get("bracket", "").startswith(("micro", "small"))
                 or _profile(z["comedian_id"]).get("tier") == "indie")]
    rising = max(small_br, key=lambda z: z["vel_z"]) if small_br else None
    # minimum absolute pulse: z-scores on tiny brackets explode from noise
    # (Steven Wright +36 views, z 12.13, crowned 2026-10-17). A rising star
    # moves rooms, not rounding errors.
    if rising and rising["d_views"] < 500:
        rising = None
    # new comic of the week: velocity among new profiles (indie or <=60d),
    # fallback to best DISCOVERY headline when no velocity yet
    newcomers = [(cid, dv) for cid, dv in by_comic.items()
                 if _is_new(cid, week_id())]
    newcomers.sort(key=lambda x: -x[1])
    new_cow = None
    if newcomers and newcomers[0][1] > 0:
        new_cow = {"comedian_id": newcomers[0][0],
                   "d_views": newcomers[0][1], "basis": "velocity"}
    else:
        try:
            ratings = json.loads(
                (HERE / "rankings" / "ratings.json").read_text())["rows"]
            # skip synthetic/test profiles: new-comic means human unknowns.
            # (headline 0.0 is a valid score — falsy but not missing.)
            disc = [r for r in ratings
                    if r.get("tier") == "indie"
                    and r.get("headline") is not None
                    and _profile(r["comedian_id"]).get("region") != "synthetic"
                    and not r["comedian_id"].startswith("test-")]
            disc.sort(key=lambda r: -r["headline"])
            if disc:
                new_cow = {"comedian_id": disc[0]["comedian_id"],
                           "headline": disc[0]["headline"],
                           "basis": "top-discovery-headline"}
        except (OSError, json.JSONDecodeError, KeyError):
            pass
    # subs velocity: per-channel subscriber gains between snapshots.
    # Channel->comic from tracked rows; channels serving 3+ comics are
    # compilers (fountains) and excluded — rising means personal growth.
    ch_comics: dict = {}
    for r in vids:
        ch_comics.setdefault(r.get("channelId", ""), set()).add(
            r.get("comedian_id"))
    subs_rows = []
    for cid, c in cur_ch.items():
        p = prev_ch.get(cid, {})
        if not p or not c.get("subs"):
            continue
        ds = c["subs"] - p.get("subs", 0)
        owners = {o for o in ch_comics.get(cid, set()) if o}
        if len(owners) > 3:
            continue
        subs_rows.append({
            "channel": c.get("title", cid[:8]),
            "comedian_id": sorted(owners)[0] if owners else None,
            "subs_then": p.get("subs", 0), "subs_now": c["subs"],
            "d_subs": ds,
            "d_pct": round(100 * ds / max(1, p.get("subs", 0)), 2)})
    subs_rows.sort(key=lambda r: -r["d_subs"])
    rep = {"week": week_id(), "mode": "velocity",
           "trending_clips": [
               {"title": r["title"][:60], "comedian": r["comedian"],
                "d_views": r["d_views"], "views_now": r["views_now"]}
               for r in rows[:15] if r["d_views"] > 0],
           "newly_tracked": [
               {"title": r["title"][:60], "comedian": r["comedian"],
                "views_now": r["views_now"]}
               for r in newly[:10]],
           "subs_growth": [r for r in subs_rows[:12] if r["d_subs"] > 0],
           "comedian_of_week": [
               {"comedian_id": cid, "d_views": dv} for cid, dv in cow],
           "bracket_champs": bracket_champs,
           "rising_star": ({"comedian_id": rising["comedian_id"],
                            "title": rising["title"][:60],
                            "d_views": rising["d_views"],
                            "z": rising["vel_z"],
                            "bracket": rising.get("bracket")}
                           if rising else None),
           "new_comic_of_week": new_cow}
    (PULSE / f"{week_id()}.json").write_text(json.dumps(rep, indent=1))
    (HERE / "rankings" / "spotlight.json").write_text(json.dumps(rep, indent=1))
    print(f"velocity report → {PULSE / (week_id() + '.json')} + spotlight.json")
    for r in rep["trending_clips"][:8]:
        print(f"  +{r['d_views']:>10,}  {r['title'][:50]:50} {r['comedian'][:18]}")
    if rep["rising_star"]:
        print(f"  RISING: {rep['rising_star']}")
    if rep["new_comic_of_week"]:
        print(f"  NEW: {rep['new_comic_of_week']}")
    for r in rep.get("subs_growth", [])[:6]:
        print(f"  SUBS +{r['d_subs']:>8,} ({r['d_pct']:>6.2f}%)  "
              f"{r['channel'][:34]:34} {str(r['comedian_id'])[:18]}")


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
