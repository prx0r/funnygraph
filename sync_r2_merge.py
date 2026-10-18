#!/usr/bin/env python3
"""Pass 3: merge + specials.

1. For the 6 comedians with BOTH harvest files AND R2 clips, merge R2
   clip rows into the harvest file (keyed by videoId, don't clobber).
2. Create data/r2/specials/{slug}.json for all 292 comedians with
   specials — full special metadata + transcript pointer.
3. Build data/r2/site_manifest.json: comedian → {clips: [...], specials: [...]}
   each entry has videoId/url + transcript_url for site embedding.
"""
from __future__ import annotations
import json, re, subprocess, time
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

EP = "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com"
BUCKET = "comedy-specials"
LOCAL = Path("/root/funnygraph")
R2DIR = LOCAL / "data" / "r2"
YOUTUBE = LOCAL / "data" / "youtube"
SPECIALS_DIR = R2DIR / "specials"
BASE_URL = f"https://{EP.split('//')[1]}/{BUCKET}"

def s3cp_json(key, timeout=90):
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
    # --- 1. Merge R2 clips into overlapping harvest files ---
    print("=== 1. Merge R2 clips into harvest files ===")
    clip_rows_by_slug = defaultdict(list)
    for line in open(R2DIR / "live_index.jsonl"):
        r = json.loads(line)
        clip_rows_by_slug[r["comedian_slug"]].append(r)

    # For overlap slugs, fetch their R2 clip JSONs and merge
    overlap = ["ali-woods", "bill-hicks", "billy-connolly", "john-meagher",
               "stewart-lee", "tommy-tiernan"]
    # Actually merge for ALL slugs that have both a harvest file and R2 clips
    all_harvest = {f.stem for f in YOUTUBE.glob("*.json")
                   if json.loads(f.read_text()).get("source") != "r2:comedy-specials"}
    merge_slugs = sorted(all_harvest & set(clip_rows_by_slug.keys()))
    print(f"  merge slugs: {merge_slugs}")

    merged_rows = 0
    for slug in merge_slugs:
        yf = YOUTUBE / f"{slug}.json"
        data = json.loads(yf.read_text())
        rows = data.get("rows") or []
        existing_vids = {r.get("videoId") for r in rows}
        # fetch R2 clips for this slug
        r2_rows = clip_rows_by_slug[slug]
        fetched = {}
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(s3cp_json, r["r2_clip_key"]): r["r2_clip_key"] for r in r2_rows}
            for fut in as_completed(futs):
                doc = fut.result()
                if doc:
                    fetched[futs[fut]] = doc
        for key, doc in fetched.items():
            vid = doc.get("id") or ""
            if vid in existing_vids:
                # update existing row with r2 linkage
                for row in rows:
                    if row.get("videoId") == vid:
                        row["r2_clip_key"] = key
                        row["transcript_url"] = f"{BASE_URL}/{key}"
                        row["transcript_available"] = bool(doc.get("transcript"))
                        row["n_words"] = len(doc.get("words") or [])
                        words = doc.get("words") or []
                        row["words_timed"] = bool(words and isinstance(words[0], dict) and "start" in words[0])
                        row["transcript_method"] = doc.get("transcript_method")
                        row["transcript_preview"] = (doc.get("transcript") or "")[:200]
                        merged_rows += 1
                        break
            else:
                # append new R2 row
                words = doc.get("words") or []
                rows.append({
                    "videoId": vid,
                    "title": doc.get("title"),
                    "channel": doc.get("channel"),
                    "views": doc.get("views"),
                    "duration_s": doc.get("duration_s"),
                    "url": doc.get("url"),
                    "n_words": len(words),
                    "words_timed": bool(words and isinstance(words[0], dict) and "start" in words[0]),
                    "transcript_method": doc.get("transcript_method"),
                    "transcript_available": bool(doc.get("transcript")),
                    "transcript_preview": (doc.get("transcript") or "")[:200],
                    "r2_clip_key": key,
                    "transcript_url": f"{BASE_URL}/{key}",
                    "source_group": doc.get("source_group"),
                    "source": "r2",
                })
                merged_rows += 1
        rows.sort(key=lambda r: r.get("views") or 0, reverse=True)
        data["rows"] = rows
        data["clips"] = len(rows)
        data["r2_linked"] = True
        data["r2_merged_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        yf.write_text(json.dumps(data, indent=1) + "\n")
        print(f"  {slug}: now {len(rows)} rows ({merged_rows} r2-linked so far)")

    # --- 2. Specials metadata ---
    print("\n=== 2. Fetch specials metadata ===")
    sp = json.loads((R2DIR / "specials_index.json").read_text())
    sp_rows = sp["specials"]
    print(f"  fetching {len(sp_rows)} specials...")
    t0 = time.time()
    sp_docs = {}
    done = 0
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(s3cp_json, s["r2_special_key"]): s for s in sp_rows}
        for fut in as_completed(futs):
            s = futs[fut]
            doc = fut.result()
            if doc:
                sp_docs[s["r2_special_key"]] = (s, doc)
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(sp_rows)}  {time.time()-t0:.1f}s")
    print(f"  fetched {len(sp_docs)} ok, {time.time()-t0:.1f}s")

    # Write per-comedian specials files
    SPECIALS_DIR.mkdir(parents=True, exist_ok=True)
    sp_by_slug = defaultdict(list)
    for key, (s, doc) in sp_docs.items():
        slug = s["comedian_slug"]
        words = doc.get("words") or []
        has_timing = bool(words and isinstance(words[0], dict) and "start" in words[0])
        sp_by_slug[slug].append({
            "special_slug": s["special_slug"],
            "title": doc.get("title") or doc.get("special"),
            "comedian": doc.get("comedian"),
            "url": doc.get("url"),
            "source": doc.get("source"),
            "n_words": len(words) if words else len((doc.get("transcript") or "").split()),
            "words_timed": has_timing,
            "transcript_method": doc.get("transcript_method"),
            "transcript_preview": (doc.get("transcript") or "")[:300],
            "r2_special_key": key,
            "transcript_url": f"{BASE_URL}/{key}",
        })
    for slug, items in sorted(sp_by_slug.items()):
        items.sort(key=lambda x: x.get("n_words") or 0, reverse=True)
        (SPECIALS_DIR / f"{slug}.json").write_text(json.dumps({
            "comedian_slug": slug,
            "specials": items,
            "count": len(items),
        }, indent=1) + "\n")
    print(f"  wrote {len(sp_by_slug)} specials files → data/r2/specials/")

    # --- 3. Site manifest ---
    print("\n=== 3. Build site manifest ===")
    manifest = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "r2_bucket": f"r2://{BUCKET}",
        "base_url": BASE_URL,
        "note": "transcript_url points at the raw R2 JSON; site/worker should fetch with creds or presigned URL",
        "comedians": {},
    }
    # From youtube files (clips)
    for f in YOUTUBE.glob("*.json"):
        d = json.loads(f.read_text())
        slug = f.stem
        clips = []
        for r in d.get("rows") or []:
            if r.get("r2_clip_key"):
                clips.append({
                    "videoId": r.get("videoId"),
                    "title": r.get("title"),
                    "views": r.get("views"),
                    "duration_s": r.get("duration_s"),
                    "url": r.get("url"),
                    "n_words": r.get("n_words"),
                    "words_timed": r.get("words_timed"),
                    "transcript_url": r.get("transcript_url"),
                })
        specials = []
        sf = SPECIALS_DIR / f"{slug}.json"
        if sf.exists():
            sd = json.loads(sf.read_text())
            for s in sd.get("specials") or []:
                specials.append({
                    "special_slug": s.get("special_slug"),
                    "title": s.get("title"),
                    "n_words": s.get("n_words"),
                    "words_timed": s.get("words_timed"),
                    "transcript_url": s.get("transcript_url"),
                })
        if clips or specials:
            manifest["comedians"][slug] = {
                "name": d.get("name") or slug.replace("-", " ").title(),
                "n_clips": len(clips),
                "n_specials": len(specials),
                "clips": clips[:50],  # cap for manifest size
                "specials": specials,
            }
    # Add specials-only comedians not in youtube files
    for slug, items in sp_by_slug.items():
        if slug not in manifest["comedians"]:
            manifest["comedians"][slug] = {
                "name": items[0].get("comedian") or slug.replace("-", " ").title(),
                "n_clips": 0,
                "n_specials": len(items),
                "clips": [],
                "specials": [{
                    "special_slug": s.get("special_slug"),
                    "title": s.get("title"),
                    "n_words": s.get("n_words"),
                    "words_timed": s.get("words_timed"),
                    "transcript_url": s.get("transcript_url"),
                } for s in items],
            }
    manifest_path = R2DIR / "site_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    n_c = len(manifest["comedians"])
    n_clips = sum(c["n_clips"] for c in manifest["comedians"].values())
    n_sp = sum(c["n_specials"] for c in manifest["comedians"].values())
    print(f"  manifest: {n_c} comedians, {n_clips} clips, {n_sp} specials")
    print(f"  wrote {manifest_path} ({manifest_path.stat().st_size/1024:.0f}KB)")

    # --- Final ---
    print("\n=== DONE ===")
    print(f"  merged r2 rows into harvest: {merged_rows}")
    print(f"  specials files: {len(sp_by_slug)}")
    print(f"  manifest comedians: {n_c}")

if __name__ == "__main__":
    main()
