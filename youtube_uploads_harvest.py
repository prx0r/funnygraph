#!/usr/bin/env python3
"""Economic YouTube harvest via uploads playlists (NO search).

Quota math:
  channels.list   = 1 unit / 50 IDs       (3 calls for 106 channels)
  playlistItems   = 1 unit / 50 items     (~2 units per channel page)
  search.list     = 100 units  ← NEVER USE

For each registered channel:
  1. Get uploads playlistId (batched)
  2. Enumerate uploads (first ~200 per channel)
  3. Classify: >20min = special candidate, 1-5min = clip candidate
  4. Match specials by title to existing R2 specials (link videoId)
  5. Save new clips to data/youtube_discovered/

Env: YOUTUBE_API_KEY
"""
from __future__ import annotations
import json, os, re, time, urllib.request, urllib.parse
from pathlib import Path
from collections import defaultdict

LOCAL = Path("/root/funnygraph")
CHANNELS_F = LOCAL / "data" / "channels.json"
R2DIR = LOCAL / "data" / "r2"
OUT = LOCAL / "data" / "youtube_discovered"
OUT.mkdir(exist_ok=True)

KEY = os.environ.get("YOUTUBE_API_KEY", "")
API = "https://www.googleapis.com/youtube/v3"

def yt_get(endpoint, **params):
    params["key"] = KEY
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(params)}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "funnygraph/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
                # respect quota errors
                if "error" in data:
                    err = data["error"]
                    print(f"    API error {err.get('code')}: {err.get('message','')[:80]}")
                    if err.get("reason") in ("quotaExceeded", "dailyLimitExceeded"):
                        raise SystemExit("QUOTA EXCEEDED — stopping")
                    time.sleep(2)
                    continue
                return data
        except SystemExit:
            raise
        except Exception as e:
            if attempt == 2:
                print(f"    fail: {e}")
                return None
            time.sleep(1 + attempt)
    return None

def parse_duration(d):
    """ISO 8601 duration → seconds."""
    if not d:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d)
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s

def main():
    if not KEY:
        print("ERROR: set YOUTUBE_API_KEY")
        return
    channels = json.loads(CHANNELS_F.read_text())
    # flatten: slug -> channel_id (take first if list)
    ch_map = {}
    for slug, v in channels.items():
        if slug.startswith("_"):
            continue
        if isinstance(v, list) and v:
            ch_map[slug] = v[0]
        elif isinstance(v, str) and v.startswith("UC"):
            ch_map[slug] = v
    print(f"channels to harvest: {len(ch_map)}")

    # Load R2 specials index for title matching
    sp_idx = json.loads((R2DIR / "specials_index.json").read_text())
    # Build title → r2 key map (need titles from the specials files)
    # We have special_slug but not always title; use slug words for matching
    sp_by_slug = {}
    for f in (R2DIR / "specials").glob("*.json"):
        d = json.loads(f.read_text())
        for s in d.get("specials", []):
            sp_by_slug[s.get("special_slug")] = s

    # Step 1: batch channel→uploads playlist (50 per call)
    ids = list(ch_map.values())
    slugs_by_cid = defaultdict(list)
    for slug, cid in ch_map.items():
        slugs_by_cid[cid].append(slug)

    cid_to_uploads = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        data = yt_get("channels", part="contentDetails,snippet", id=",".join(batch))
        if not data:
            continue
        for item in data.get("items", []):
            cid = item["id"]
            uploads = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            title = item.get("snippet", {}).get("title", "")
            if uploads:
                cid_to_uploads[cid] = (uploads, title)
        print(f"  channels batch {i//50+1}: got {len(cid_to_uploads)} uploads playlists")
        time.sleep(0.3)

    # Step 2: enumerate uploads per channel
    discovered_specials = []
    discovered_clips = []
    seen_video_ids = set()

    # Existing videoIds from R2 index (to dedup)
    for line in open(R2DIR / "live_index.jsonl"):
        r = json.loads(line)
        # file_stem is slugified; we'll dedup by r2 key later

    for slug, cid in sorted(ch_map.items()):
        if cid not in cid_to_uploads:
            continue
        uploads_pl, ch_title = cid_to_uploads[cid]
        videos = []
        page_token = None
        for page in range(4):  # up to 200 videos per channel
            params = dict(part="contentDetails,snippet", playlistId=uploads_pl, maxResults=50)
            if page_token:
                params["pageToken"] = page_token
            data = yt_get("playlistItems", **params)
            if not data:
                break
            for item in data.get("items", []):
                vid = item.get("contentDetails", {}).get("videoId") or \
                      item.get("snippet", {}).get("resourceId", {}).get("videoId")
                title = item.get("snippet", {}).get("title", "")
                if vid and vid not in seen_video_ids:
                    videos.append({"videoId": vid, "title": title})
                    seen_video_ids.add(vid)
            page_token = data.get("nextPageToken")
            if not page_token:
                break
            time.sleep(0.2)
        if not videos:
            continue

        # Step 3: batch videos.list to get durations (50 per call, 1 unit)
        video_ids = [v["videoId"] for v in videos]
        vmeta = {}
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            data = yt_get("videos", part="contentDetails,snippet,statistics", id=",".join(batch))
            if not data:
                continue
            for item in data.get("items", []):
                dur = parse_duration(item.get("contentDetails", {}).get("duration"))
                sn = item.get("snippet", {})
                st = item.get("statistics", {})
                vmeta[item["id"]] = {
                    "videoId": item["id"],
                    "title": sn.get("title", ""),
                    "channel": sn.get("channelTitle", ch_title),
                    "publishedAt": sn.get("publishedAt", ""),
                    "duration_s": dur,
                    "views": int(st.get("viewCount", 0)),
                    "likes": int(st.get("likeCount", 0)),
                }
            time.sleep(0.2)

        # Classify
        for v in videos:
            m = vmeta.get(v["videoId"])
            if not m:
                continue
            dur = m["duration_s"]
            title_lower = m["title"].lower()
            # Special: >20 min and looks like a special (stand up, special, live, full)
            if dur >= 1200:
                # Match to R2 specials by title similarity
                matched_sp = None
                for sp_slug, sp in sp_by_slug.items():
                    if sp.get("comedian_slug") == slug or True:  # match across all
                        sp_title = (sp.get("title") or "").lower()
                        # fuzzy: check if significant words overlap
                        if sp_title and any(w in title_lower for w in sp_title.split() if len(w) > 4):
                            matched_sp = sp_slug
                            break
                discovered_specials.append({
                    **m,
                    "comedian_slug": slug,
                    "matched_r2_special": matched_sp,
                })
            elif 30 <= dur <= 600:
                discovered_clips.append({
                    **m,
                    "comedian_slug": slug,
                })

    # Save
    (OUT / "discovered_specials.json").write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n": len(discovered_specials),
        "specials": discovered_specials,
    }, indent=1))
    (OUT / "discovered_clips.json").write_text(json.dumps({
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n": len(discovered_clips),
        "clips": discovered_clips[:2000],  # cap
    }, indent=1))

    # Per-comedian files
    by_slug = defaultdict(list)
    for v in discovered_specials + discovered_clips:
        by_slug[v["comedian_slug"]].append(v)
    for slug, vids in by_slug.items():
        (OUT / f"{slug}.json").write_text(json.dumps({
            "comedian_id": slug,
            "specials": [v for v in vids if v["duration_s"] >= 1200],
            "clips": [v for v in vids if v["duration_s"] < 1200],
        }, indent=1))

    matched = sum(1 for s in discovered_specials if s.get("matched_r2_special"))
    print(f"\n=== HARVEST DONE ===")
    print(f"  channels enumerated: {len(cid_to_uploads)}")
    print(f"  unique videos seen:  {len(seen_video_ids)}")
    print(f"  specials discovered: {len(discovered_specials)} ({matched} matched to R2 transcripts)")
    print(f"  clips discovered:    {len(discovered_clips)}")
    print(f"  per-comedian files:  {len(by_slug)} → data/youtube_discovered/")

if __name__ == "__main__":
    main()
