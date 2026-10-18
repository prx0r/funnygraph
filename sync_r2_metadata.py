#!/usr/bin/env python3
"""Pass 2: fetch all R2 clip JSONs → rebuild data/youtube/*.json with
real metadata (videoId, title, views, transcript, words_timed).

Cleaner than patching pass-1: fetches everything, groups by comedian,
writes one file per comedian with full rows.
"""
from __future__ import annotations
import json, re, subprocess, time
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

EP = "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com"
BUCKET = "comedy-specials"
YOUTUBE = Path("/root/funnygraph/data/youtube")
R2DIR = Path("/root/funnygraph/data/r2")
BASE_URL = f"https://{EP.split('//')[1]}/{BUCKET}"

def s3cp_json(key, timeout=60):
    try:
        out = subprocess.run(
            ["aws", "s3", "cp", f"s3://{BUCKET}/{key}", "-", "--endpoint-url", EP],
            capture_output=True, text=True, timeout=timeout)
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except Exception:
        return None

def main():
    rows = [json.loads(l) for l in open(R2DIR / "live_index.jsonl")]
    print(f"fetching {len(rows)} clip JSONs...")
    t0 = time.time()
    docs = {}  # r2_key -> doc
    done = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(s3cp_json, r["r2_clip_key"]): r["r2_clip_key"] for r in rows}
        for fut in as_completed(futs):
            key = futs[fut]
            doc = fut.result()
            if doc:
                docs[key] = doc
            else:
                failed += 1
            done += 1
            if done % 400 == 0:
                el = time.time() - t0
                print(f"  {done}/{len(rows)}  {done/el:.1f}/s  fail={failed}")
    print(f"fetched {len(docs)} ok, {failed} failed, {time.time()-t0:.1f}s")

    # Group by comedian
    by_slug = defaultdict(list)
    for key, doc in docs.items():
        slug = key.split("/")[1]
        by_slug[slug].append((key, doc))

    # Write one youtube file per comedian
    # ONLY touch files that are r2-sourced (created by pass 1) or don't exist.
    # Never overwrite youtube_harvest files (different clip set).
    synced = 0
    skipped_harvest = 0
    total_rows = 0
    total_words = 0
    timed_count = 0
    for slug, items in sorted(by_slug.items()):
        yf = YOUTUBE / f"{slug}.json"
        if yf.exists():
            try:
                existing = json.loads(yf.read_text())
                if existing.get("source") != "r2:comedy-specials" and not existing.get("r2_linked"):
                    skipped_harvest += 1
                    continue  # harvest file — don't clobber
            except Exception:
                pass
        yt_rows = []
        total_views = 0
        for key, doc in items:
            vid = doc.get("id") or ""
            words = doc.get("words") or []
            has_timing = bool(words and isinstance(words[0], dict) and "start" in words[0])
            transcript = doc.get("transcript") or ""
            n_words = len(words) if words else len(transcript.split())
            views = doc.get("views") or 0
            total_views += views
            if has_timing:
                timed_count += 1
            total_words += n_words
            yt_rows.append({
                "videoId": vid,
                "title": doc.get("title"),
                "channel": doc.get("channel"),
                "views": views,
                "likes": doc.get("likes"),
                "duration_s": doc.get("duration_s"),
                "url": doc.get("url"),
                "n_words": n_words,
                "words_timed": has_timing,
                "transcript_method": doc.get("transcript_method"),
                "transcript_available": bool(transcript),
                "transcript_preview": transcript[:200] if transcript else None,
                "r2_clip_key": key,
                "transcript_url": f"{BASE_URL}/{key}",
                "source_group": doc.get("source_group"),
            })
        # sort by views desc
        yt_rows.sort(key=lambda r: r.get("views") or 0, reverse=True)
        top = yt_rows[0] if yt_rows else None
        doc_out = {
            "comedian_id": slug,
            "name": (items[0][1].get("comedian") if items else slug.replace("-", " ").title()),
            "clips": len(yt_rows),
            "total_views": total_views,
            "r2_linked": True,
            "r2_metadata_synced": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "r2:comedy-specials",
            "top_clip": {k: top[k] for k in ("videoId","title","channel","views","duration_s","url","r2_clip_key","transcript_url") if top and k in top} if top else None,
            "rows": yt_rows,
        }
        (YOUTUBE / f"{slug}.json").write_text(json.dumps(doc_out, indent=1) + "\n")
        synced += 1
        total_rows += len(yt_rows)

    print("=== SYNCED ===")
    print(f"  comedian files written: {synced}")
    print(f"  harvest files skipped (preserved): {skipped_harvest}")
    print(f"  clip rows: {total_rows}")
    print(f"  transcript words: {total_words}")
    print(f"  clips with timed words: {timed_count}")
    print(f"  clips with transcript text: {sum(1 for d in docs.values() if d.get('transcript'))}")

if __name__ == "__main__":
    main()
