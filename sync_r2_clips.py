#!/usr/bin/env python3
"""Sync R2 comedy-specials → local linkage layer.

Enums live R2 bucket (not the stale index), builds a fresh
videoId → {r2_clip_key, comedian_slug, transcript meta} map,
then:
  1. Writes data/r2/live_index.jsonl (fresh, complete)
  2. Enriches data/youtube/*.json rows with r2_clip_key + transcript_url
  3. Creates data/youtube/*.json for R2-only comedians (clip rows)
  4. Writes data/r2/specials_index.json (specials → r2 keys)

R2 layout:
  comedians/<slug>/clips/<slug>-<videoid>.json
  comedians/<slug>/specials/<special-slug>.json

Clip JSON: {id, url, title, comedian, channel, views, duration_s,
            words[], transcript, transcript_method}
Index row: {comedian_slug, clip_id, url, r2_clip_key, n_words, ...}
"""
from __future__ import annotations
import json, os, re, sys, time
from pathlib import Path
from collections import defaultdict

# S3 via aws cli (boto3 available too but cli is already credentialed)
import subprocess

EP = "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com"
BUCKET = "comedy-specials"
LOCAL = Path("/root/funnygraph")
R2DIR = LOCAL / "data" / "r2"
YOUTUBE = LOCAL / "data" / "youtube"
BASE_URL = f"https://{EP.split('//')[1]}/{BUCKET}"  # for public-ish reads; site should use presigned or worker

def s3ls(prefix):
    """List keys under prefix. Returns [(key, size)]."""
    out = subprocess.run(
        ["aws", "s3", "ls", f"s3://{BUCKET}/{prefix}",
         "--endpoint-url", EP, "--recursive"],
        capture_output=True, text=True, timeout=300)
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4:
            rows.append((parts[3], int(parts[2])))
    return rows

def s3cp_json(key):
    out = subprocess.run(
        ["aws", "s3", "cp", f"s3://{BUCKET}/{key}", "-",
         "--endpoint-url", EP],
        capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None

def slugify_videoid(vid):
    return re.sub(r'[^a-z0-9]+', '-', vid.lower()).strip('-')

def main():
    print("=== 1. Enumerate live R2 ===")
    t0 = time.time()
    clip_keys = [k for k, s in s3ls("comedians/") if "/clips/" in k and k.endswith(".json")]
    special_keys = [k for k, s in s3ls("comedians/") if "/specials/" in k and k.endswith(".json")]
    print(f"  clips: {len(clip_keys)}  specials: {len(special_keys)}  ({time.time()-t0:.1f}s)")

    # Group by comedian slug
    clips_by_slug = defaultdict(list)
    for k in clip_keys:
        # comedians/<slug>/clips/<file>.json
        slug = k.split("/")[1]
        clips_by_slug[slug].append(k)
    specials_by_slug = defaultdict(list)
    for k in special_keys:
        slug = k.split("/")[1]
        specials_by_slug[slug].append(k)
    print(f"  comedians with clips: {len(clips_by_slug)}")
    print(f"  comedians with specials: {len(specials_by_slug)}")

    # === 2. Build fresh index by fetching each clip's metadata ===
    # To avoid 2300 S3 GETs, first check if we can get metadata from the
    # key filename alone: <slug>-<videoid>.json → comedian + videoId.
    # We still need views/title etc from the JSON, but for LINKAGE we only
    # need videoId → r2_key mapping which the filename gives us.
    print("=== 2. Build linkage index from filenames ===")
    index_rows = []
    for slug, keys in sorted(clips_by_slug.items()):
        for k in keys:
            fname = k.split("/")[-1][:-5]  # strip .json
            # strip slug prefix: slug + "-" + videoid
            if fname.startswith(slug + "-"):
                vid_raw = fname[len(slug)+1:]
            else:
                vid_raw = fname
            # videoId: YouTube IDs are 11 chars [A-Za-z0-9_-]
            # our slugified version is lowercase-hyphenated; recover best guess
            # We store both the raw filename stem and the r2 key.
            index_rows.append({
                "comedian_slug": slug,
                "r2_clip_key": k,
                "file_stem": vid_raw,
            })
    print(f"  index rows: {len(index_rows)}")

    # Write fresh filename-based index (no per-clip GET needed for linkage)
    R2DIR.mkdir(parents=True, exist_ok=True)
    with open(R2DIR / "live_index.jsonl", "w") as f:
        for r in index_rows:
            f.write(json.dumps(r) + "\n")
    print(f"  wrote {R2DIR/'live_index.jsonl'}")

    # Specials index
    specials_rows = []
    for slug, keys in sorted(specials_by_slug.items()):
        for k in keys:
            fname = k.split("/")[-1][:-5]
            specials_rows.append({
                "comedian_slug": slug,
                "special_slug": fname,
                "r2_special_key": k,
            })
    with open(R2DIR / "specials_index.json", "w") as f:
        json.dump({"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "count": len(specials_rows),
                   "specials": specials_rows}, f, indent=2)
    print(f"  wrote {R2DIR/'specials_index.json'} ({len(specials_rows)} specials)")

    # === 3. Enrich data/youtube/*.json + create missing ===
    print("=== 3. Link data/youtube files to R2 ===")
    # Build videoId_key → row map. We need actual videoIds; filename stem is
    # slugified. For enrichment of EXISTING youtube files we match by
    # videoId against the slugified stem.
    vid_to_r2 = defaultdict(list)
    for r in index_rows:
        vid_to_r2[r["file_stem"]].append(r)

    existing = sorted(YOUTUBE.glob("*.json"))
    enriched = 0
    rows_linked = 0
    for yf in existing:
        slug = yf.stem
        try:
            data = json.loads(yf.read_text())
        except Exception:
            continue
        rows = data.get("rows") or []
        if not rows:
            continue
        changed = False
        for row in rows:
            vid = row.get("videoId") or ""
            stem = slugify_videoid(vid)
            matches = vid_to_r2.get(stem, [])
            # also try raw videoId as stored in R2 filenames
            if not matches:
                matches = vid_to_r2.get(vid, [])
            if matches:
                m = matches[0]
                row["r2_clip_key"] = m["r2_clip_key"]
                row["transcript_available"] = True
                # public URL for the transcript JSON (site/worker can fetch)
                row["transcript_url"] = f"{BASE_URL}/{m['r2_clip_key']}"
                changed = True
                rows_linked += 1
        if changed:
            data["r2_linked"] = True
            data["r2_linked_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            yf.write_text(json.dumps(data, indent=1) + "\n")
            enriched += 1
    print(f"  enriched {enriched} existing youtube files, {rows_linked} rows linked")

    # Create youtube files for R2-only comedians
    r2_slugs = set(clips_by_slug.keys())
    local_slugs = {f.stem for f in existing}
    r2_only = sorted(r2_slugs - local_slugs)
    created = 0
    total_rows = 0
    for slug in r2_only:
        rows = []
        for r in clips_by_slug[slug]:
            fname = r.split("/")[-1][:-5]
            stem = fname[len(slug)+1:] if fname.startswith(slug+"-") else fname
            rows.append({
                "videoId": stem,  # slugified; site resolves via r2_clip_key
                "r2_clip_key": r,
                "transcript_available": True,
                "transcript_url": f"{BASE_URL}/{r}",
                "title": None,  # needs per-clip GET to fill; linkage works without
                "channel": None,
                "views": None,
                "duration_s": None,
                "source_group": "r2-sync",
            })
        if not rows:
            continue
        total_rows += len(rows)
        # count words from summary if available
        doc = {
            "comedian_id": slug,
            "name": slug.replace("-", " ").title(),
            "clips": len(rows),
            "r2_linked": True,
            "r2_linked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": "r2:comedy-specials",
            "rows": rows,
        }
        (YOUTUBE / f"{slug}.json").write_text(json.dumps(doc, indent=1) + "\n")
        created += 1
    print(f"  created {created} new youtube files ({total_rows} rows)")

    # === 4. Summary ===
    final_yt = list(YOUTUBE.glob("*.json"))
    linked_files = sum(1 for f in final_yt if json.loads(f.read_text()).get("r2_linked"))
    print("=== DONE ===")
    print(f"  R2 clips indexed: {len(index_rows)}")
    print(f"  R2 specials indexed: {len(specials_rows)}")
    print(f"  data/youtube files: {len(final_yt)} ({linked_files} r2_linked)")
    print(f"  comedians with clips in R2: {len(clips_by_slug)}")
    print(f"  comedians with specials in R2: {len(specials_by_slug)}")

if __name__ == "__main__":
    main()
