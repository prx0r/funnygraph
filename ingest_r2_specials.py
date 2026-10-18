#!/usr/bin/env python3
"""Ingest R2 timed specials → comedian graphs (known_bits + timing + sets).

For each timed special in data/r2/specials/:
  1. Fetch the special JSON from R2 (words with start/end)
  2. Run analyze_set.analyze() → timing profile + punch candidates
  3. Extract top punch_candidates → known_bits (title from context)
  4. Update comedian graph: sets[], timing_profile, known_bits, specials_rated
  5. Save raw analysis → analysis/{slug}-{special}_analysis.json

Focus: comedians with timed specials (currently Stewart Lee, Sloss, Amstell).
Rerunnable: skips sets already ingested.
"""
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

HERE = Path("/root/funnygraph")
sys.path.insert(0, str(HERE))
from analyze_set import analyze  # noqa: E402

EP = "https://954612afb5a97bb15dddcdc70176813d.r2.cloudflarestorage.com"
BUCKET = "comedy-specials"
R2DIR = HERE / "data" / "r2"
COMEDIANS = HERE / "comedians"
ANALYSIS = HERE / "analysis"
ANALYSIS.mkdir(exist_ok=True)

def s3cp_json(key, timeout=120):
    out = subprocess.run(
        ["aws", "s3", "cp", f"s3://{BUCKET}/{key}", "-", "--endpoint-url", EP],
        capture_output=True, text=True, timeout=timeout)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None

def main():
    sp_files = sorted((R2DIR / "specials").glob("*.json"))
    # Collect timed specials
    targets = []
    for f in sp_files:
        d = json.loads(f.read_text())
        for s in d.get("specials", []):
            if s.get("words_timed") and (s.get("n_words") or 0) > 500:
                targets.append((d["comedian_slug"], s))
    print(f"timed specials to ingest: {len(targets)}")

    by_comedian = {}
    for slug, sp in targets:
        by_comedian.setdefault(slug, []).append(sp)

    for slug, specials in sorted(by_comedian.items()):
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            print(f"  SKIP {slug}: no graph")
            continue
        g = json.loads(gpath.read_text())
        sets = g.setdefault("sets", [])
        existing_set_ids = {s.get("id") for s in sets}
        kb = g.setdefault("known_bits", [])
        existing_kb_titles = {b.get("title") for b in kb}

        for sp in specials:
            sp_slug = sp["special_slug"]
            set_id = f"{slug}-{sp_slug}"
            if set_id in existing_set_ids:
                print(f"  skip {set_id} (already ingested)")
                continue
            key = sp.get("r2_special_key")
            if not key:
                print(f"  skip {sp_slug}: no r2 key")
                continue
            print(f"  fetching {slug}/{sp_slug}...", flush=True)
            doc = s3cp_json(key)
            if not doc or not doc.get("words"):
                print(f"    FAIL fetch or empty")
                continue
            words = [w for w in doc["words"] if w.get("type") == "word" and "start" in w]
            if len(words) < 100:
                print(f"    skip: only {len(words)} timed words")
                continue

            # Write temp scribe file for analyze()
            tmp = Path(f"/tmp/opencode/{set_id}.json")
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(json.dumps({
                "words": words,
                "text": doc.get("transcript", ""),
                "audio_duration_secs": words[-1]["end"] if words else 0,
                "note": f"r2:{key} method={doc.get('transcript_method')}",
            }))

            try:
                result = analyze(tmp, slug.replace("-", "_"))
            except Exception as e:
                print(f"    analyze FAIL: {e}")
                continue

            # Save analysis
            apath = ANALYSIS / f"{slug}-{sp_slug}_analysis.json"
            apath.write_text(json.dumps(result, indent=1))

            # Timing summary
            timing = result.get("timing", {})
            pcs = result.get("punch_candidates", [])
            top_pauses = sorted(
                [p["pause_before_s"] for p in pcs if p.get("pause_before_s")],
                reverse=True)[:8]

            # Add to sets
            sets.append({
                "id": set_id,
                "special": sp_slug,
                "title": sp.get("title"),
                "source": f"r2:{key}",
                "transcript_method": doc.get("transcript_method"),
                "words_timed": True,
                "n_words": len(words),
                "duration_s": round(words[-1]["end"], 1) if words else None,
                "timing_measured": {
                    "wpm": timing.get("wpm"),
                    "pause_count": timing.get("pause_count"),
                    "pause_bins": timing.get("pause_bins"),
                    "mean_pause_s": timing.get("mean_pause_s"),
                    "punch_pauses_s": top_pauses,
                    "max_pause_s": timing.get("max_pause_s"),
                },
                "punch_candidates": pcs[:20],
                "beat_count": result.get("beat_count"),
                "provenance": "measured — R2 timed captions",
                "ingested": time.strftime("%Y-%m-%d"),
            })

            # known_bits from top punch candidates (unique fingerprints)
            new_kb = 0
            for p in sorted(pcs, key=lambda x: x.get("pause_before_s") or 0, reverse=True)[:5]:
                fp = (p.get("fingerprint") or "")[:80]
                if not fp:
                    continue
                title = fp[:60].strip()
                if title in existing_kb_titles:
                    continue
                kb.append({
                    "title": f"{sp_slug}: {title}",
                    "why_it_works": f"Long pause ({p.get('pause_before_s')}s) before "
                                    f"this beat in {sp.get('title') or sp_slug}. "
                                    f"Measured punch candidate.",
                    "theory_links": ["timing", "pause_distribution"],
                    "set_id": set_id,
                    "t_start_s": p.get("t_start_s"),
                    "pause_before_s": p.get("pause_before_s"),
                })
                existing_kb_titles.add(title)
                new_kb += 1

            # Update timing_profile
            tp = g.get("timing_profile") or {}
            measured = tp.get("measured") or []
            measured.append({
                "set_id": set_id,
                "wpm": timing.get("wpm"),
                "mean_pause_s": timing.get("mean_pause_s"),
                "punch_pauses_s": top_pauses[:5],
                "max_pause_s": timing.get("max_pause_s"),
            })
            tp["measured"] = measured
            tp["status"] = f"measured on {len(measured)} set(s)"
            g["timing_profile"] = tp

            # specials_rated stub
            sr = g.setdefault("specials_rated", [])
            if not any(x.get("special") == sp_slug for x in sr):
                sr.append({
                    "special": sp_slug,
                    "title": sp.get("title"),
                    "source": f"r2:{key}",
                    "n_words": len(words),
                    "words_timed": True,
                    "analysis": str(apath.relative_to(HERE)),
                })

            print(f"    OK: {len(words)} words, {len(pcs)} punch candidates, "
                  f"{new_kb} new known_bits, max_pause={timing.get('max_pause_s')}s")

        g["version"] = max(g.get("version", 1), 2)
        g["last_ingest"] = time.strftime("%Y-%m-%d")
        gpath.write_text(json.dumps(g, indent=1) + "\n")
        print(f"  {slug}: {len(sets)} sets, {len(kb)} known_bits total")

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
