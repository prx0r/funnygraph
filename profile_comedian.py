#!/usr/bin/env python3
"""PROFILE — YouTube search → captions → scribe → analyze → distinctive terms.

The characters2 pattern, packaged for funnygraph:
  1. YouTube Data API search for a comedian's standup clips
  2. InnerTube captions → word-timed scribe JSON (works without cookies)
  3. analyze_set.py → timing_measured + punch_candidates
  4. distinctive-term lift vs the rest of the roster (stylometry)
  5. graph-patch JSON ready to merge into comedian-graph.json sets[]

Key: YOUTUBE_DATA_API_KEY in .env (gitignored) or vault. Never in tree.

Usage:
  python3 profile_comedian.py --comedian theo-von --search "theo von standup"
  python3 profile_comedian.py --comedian william-montgomery --from-scribe scribe/william-montgomery-kt.json
  python3 profile_comedian.py --comedian robin-williams --from-transcript /root/characters2/theory/transcripts/robin-williams/robin-williams-weapons-self-destruction.txt
  python3 profile_comedian.py --roster-all          # profile every graph without sets
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from harvest_captions import (  # noqa: E402
    SCRIBE, ANALYSIS, _ytid, innertube_captions, words_to_scribe,
    txt_to_scribe, vtt_to_words, run_analysis, graph_patch, slugify,
)

API = "https://www.googleapis.com/youtube/v3"
CARRIERS = {
    "kill-tony": "UCwzCMiicL-hBUzyjWiJaseg",
    "netflix-is-a-joke": "UCObk_g1hQBy0RKKriVX_zOQ",
    "team-coco": "UCi7GJNg51C3jgmYTUwqoUXA",
}

STOP = set("""the a an and or of to in on for with is are was were be been have has had
do does did i you he she it we they my your his her its our their not no yes
so if as at by from but that this these those what which who whom when where why
how all any both each few more most other some such only own same than too very
can will just don should now u r im ive dont doesnt didnt its its gonna gonna
like know right yeah oh um uh really going get got one two three like really
going get got just like know right yeah oh um uh really going get""".split())


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
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def search_clips(query: str, key: str, max_results: int = 8) -> list[dict]:
    q = urllib.parse.quote(query)
    url = (f"{API}/search?part=snippet&q={q}&type=video&maxResults={max_results}"
           f"&order=relevance&videoEmbeddable=true&videoDuration=medium&key={key}")
    d = _get(url)
    out = []
    for it in d.get("items") or []:
        sn = it.get("snippet") or {}
        vid = (it.get("id") or {}).get("videoId")
        if not vid:
            continue
        title = sn.get("title", "")
        # standup heuristic
        blob = (title + " " + sn.get("description", "")).lower()
        if not any(w in blob for w in
                   ("stand", "comedy", "special", "set", "kill tony",
                    "monologue", "live", "hour", "netflix")):
            continue
        out.append({
            "videoId": vid, "title": title,
            "channel": sn.get("channelTitle", ""),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
    return out


def distinctive_terms(words_a: list[str], words_b: list[str]) -> list[dict]:
    """Log-odds lift of unigrams in comedian A vs rest of roster B."""
    a, b = Counter(words_a), Counter(words_b)
    n_a, n_b = sum(a.values()), sum(b.values())
    if n_a < 50 or n_b < 100:
        return []
    out = []
    vocab = set(a) | set(b)
    for w in vocab:
        if w in STOP or len(w) < 3:
            continue
        pa = (a[w] + 0.5) / (n_a + 0.5 * len(vocab))
        pb = (b[w] + 0.5) / (n_b + 0.5 * len(vocab))
        lift = pa / pb
        # only distinctive-enough terms
        if lift > 1.8 and a[w] >= 2:
            out.append({"ngram": w, "lift": round(lift, 3), "count": a[w]})
    out.sort(key=lambda x: -x["lift"])
    return out[:25]


def load_all_roster_words(skip: str) -> list[str]:
    """Words from every other comedian's scribe/transcript (for contrast set)."""
    words: list[str] = []
    for p in SCRIBE.glob("*.json"):
        if p.stem.startswith(skip):
            continue
        try:
            d = json.loads(p.read_text())
            words.extend((w.get("text") or "").lower()
                         for w in d.get("words", []) if w.get("text"))
        except (OSError, json.JSONDecodeError):
            continue
    # also plain transcripts
    tr_root = Path("/root/characters2/theory/transcripts")
    for txt in tr_root.glob("*/*.txt"):
        if skip.replace("-", "") in txt.stem.replace("-", ""):
            continue
        try:
            raw = txt.read_text(encoding="utf-8", errors="replace")[:200000]
            words.extend(re.findall(r"[a-z']{3,}", raw.lower()))
        except OSError:
            continue
    return words


def profile(comedian: str, title: str, scribe_path: Path,
            synthetic: bool = False) -> dict:
    result = run_analysis(scribe_path, comedian)
    words = []
    try:
        d = json.loads(scribe_path.read_text())
        words = [(w.get("text") or "").lower() for w in d.get("words", [])]
    except (OSError, json.JSONDecodeError):
        pass
    contrast = load_all_roster_words(comedian)
    terms = distinctive_terms([w for w in words if w], contrast)

    patch = None
    if result:
        try:
            scribe_rel = str(scribe_path.relative_to(HERE))
        except ValueError:
            scribe_rel = str(scribe_path)
        patch = graph_patch(result, comedian, title, scribe_rel,
                            synthetic=synthetic)
    profile_out = {
        "comedian": comedian,
        "title": title,
        "scribe": str(scribe_path),
        "word_count": len(words),
        "distinctive_terms": terms,
        "timing": (result or {}).get("timing"),
        "punch_candidates": ((result or {}).get("punch_candidates") or [])[:8],
        "synthetic_timing": synthetic,
    }
    # save profile
    prof_path = ANALYSIS / f"{comedian}-profile.json"
    prof_path.write_text(json.dumps(profile_out, indent=1), encoding="utf-8")
    if patch:
        patch_path = ANALYSIS / f"{comedian}-graph-patch.json"
        patch_path.write_text(json.dumps(patch, indent=1), encoding="utf-8")
    print(f"[profile] {prof_path}")
    if terms:
        top = ", ".join(f"{t['ngram']}({t['lift']:.1f}x)" for t in terms[:8])
        print(f"[terms]   {top}")
    if patch:
        tp = patch.get("timing_measured", {})
        print(f"[timing]  wpm={tp.get('wpm')} max_hold={tp.get('max_pause_s')}s "
              f"punches={len(patch.get('punch_candidates', []))}")
    return profile_out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--comedian", required=True)
    ap.add_argument("--search", default="", help="YouTube search query")
    ap.add_argument("--from-scribe", help="existing scribe JSON path")
    ap.add_argument("--from-transcript", help="plain .txt path")
    ap.add_argument("--video", help="specific YouTube URL/videoId")
    ap.add_argument("--title", default="")
    ap.add_argument("--max-videos", type=int, default=3)
    args = ap.parse_args()

    key = _key()
    cid = args.comedian
    harvested = []

    if args.from_scribe:
        sp = Path(args.from_scribe)
        profile(cid, args.title or sp.stem, sp, synthetic=False)
        harvested.append(sp)
    elif args.from_transcript:
        sp = SCRIBE / f"{cid}-txt.json"
        sc = txt_to_scribe(Path(args.from_transcript))
        sp.write_text(json.dumps(sc, indent=1), encoding="utf-8")
        profile(cid, args.title or Path(args.from_transcript).stem, sp,
                synthetic=True)
        harvested.append(sp)
    elif args.video or args.search:
        targets = []
        if args.video:
            vid = _ytid(args.video)
            targets.append({"videoId": vid, "title": args.title or vid,
                            "url": f"https://www.youtube.com/watch?v={vid}"})
        elif key:
            q = args.search or f"{cid.replace('-', ' ')} standup"
            print(f"[search] {q}")
            targets = search_clips(q, key, max_results=args.max_videos)[:args.max_videos]
            for t in targets:
                print(f"  found: {t['title'][:70]} ({t['videoId']})")
        else:
            raise SystemExit("no YOUTUBE_DATA_API_KEY and no --video")

        for t in targets:
            vid = t["videoId"]
            slug = slugify(t["title"])[:40]
            sp = SCRIBE / f"{cid}-{slug}.json"
            print(f"[captions] {t['title'][:60]}")
            try:
                body, vtitle = innertube_captions(vid)
                sc = json.loads(body) if body.lstrip().startswith("{") else None
                if sc is None:
                    sc = words_to_scribe(vtt_to_words(body), note=f"innertube {vid}")
                if len(sc.get("words", [])) < 30:
                    print(f"  skip: only {len(sc.get('words', []))} words")
                    continue
                sp.write_text(json.dumps(sc, indent=1), encoding="utf-8")
                profile(cid, vtitle, sp, synthetic=False)
                harvested.append(sp)
            except Exception as e:
                print(f"  fail: {e}")
                # try more search hits
                continue
            if len(harvested) >= args.max_videos:
                break
    else:
        ap.error("need --from-scribe, --from-transcript, --video, or --search")

    print(f"\n=== {cid}: {len(harvested)} set(s) profiled ===")


if __name__ == "__main__":
    main()
