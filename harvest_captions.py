#!/usr/bin/env python3
"""HARVEST — YouTube captions → scribe word JSON → analyze_set → graph fields.

The easiest transcript path: yt-dlp pulls auto/manual captions (word-timed
when available), we convert to the scribe format analyze_set.py expects,
run the analyzer, and emit timing_measured + punch_candidates ready to drop
into a comedian-graph.json.

Usage:
  python3 harvest_captions.py "https://www.youtube.com/watch?v=..." \
      --comedian theo-von --title "Theo Von clip"
  python3 harvest_captions.py --search "kill tony william montgomery" --limit 3
  python3 harvest_captions.py --from-transcript path/to.txt --comedian robin-williams

Output:
  scribe/<comedian>-<slug>.json     word-timed (scribe format)
  analysis/<comedian>-<slug>.json   timing + punches + beats
  (prints a graph-patch snippet ready to paste into comedian-graph.json)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).parent
SCRIBE = HERE / "scribe"
ANALYSIS = HERE / "analysis"
SCRIBE.mkdir(exist_ok=True)
ANALYSIS.mkdir(exist_ok=True)

# reuse the analyzer from characters2 if present
ANALYZER_CANDIDATES = [
    HERE / "analyze_set.py",
    Path("/root/characters2/theory/analyze_set.py"),
]


def _load_analyzer():
    import importlib.util
    for p in ANALYZER_CANDIDATES:
        if p.exists():
            spec = importlib.util.spec_from_file_location("analyze_set", p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["analyze_set"] = mod
            spec.loader.exec_module(mod)
            return mod
    return None


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


# ── VTT → words ─────────────────────────────────────────────────────────────

_TS = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")
_TAG = re.compile(r"<[^>]+>")
_WORDISH = re.compile(r"[A-Za-z0-9']+")


def _hms(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def vtt_to_words(vtt_text: str) -> list[dict]:
    """Parse WebVTT into scribe-style word list.

    Handles:
      - line-level cues (start/end for the whole line → split words evenly)
      - word-level <00:00:01.000><c> chunks (YouTube auto-subs) → exact timings
    """
    words: list[dict] = []
    lines = vtt_text.splitlines()
    i = 0
    while i < len(lines):
        m = _TS.search(lines[i])
        if not m:
            i += 1
            continue
        t0 = _hms(m.group(1), m.group(2), m.group(3), m.group(4))
        t1 = _hms(m.group(5), m.group(6), m.group(7), m.group(8))
        # collect cue text until blank line
        cue: list[str] = []
        i += 1
        while i < len(lines) and lines[i].strip() and "-->" not in lines[i]:
            cue.append(lines[i])
            i += 1
        raw = " ".join(cue)
        # word-level timestamps: <HH:MM:SS.mmm>word pairs
        ts_words = re.findall(
            r"<(\d{2}:\d{2}:\d{2})[.,](\d{3})>([^<]+)", raw)
        if ts_words:
            # strip tags, rebuild with per-word timing
            clean = _TAG.sub("", raw)
            # pair each timestamp with the following word chunk
            parts = re.split(r"<\d{2}:\d{2}:\d{2}[.,]\d{3}>", raw)
            # parts[0] is before first tag (usually empty); ts_words aligns with parts[1:]
            for j, (hhmmss, ms, chunk) in enumerate(ts_words):
                h, mnt, s = hhmmss.split(":")
                wstart = _hms(h, mnt, s, ms)
                # next timestamp or cue end
                if j + 1 < len(ts_words):
                    nh, nm, ns, nms = (ts_words[j + 1][0], ts_words[j + 1][1], None, None)
                    h2, m2, s2 = nh.split(":")
                    wend = _hms(h2, m2, s2, nms or "000")
                else:
                    wend = t1
                for wt in _WORDISH.findall(chunk):
                    words.append({
                        "text": wt, "start": round(wstart, 3),
                        "end": round(wend, 3), "type": "word",
                        "speaker_id": "speaker_0",
                    })
        else:
            # line-level: split words evenly across [t0, t1]
            toks = _WORDISH.findall(_TAG.sub("", raw))
            if not toks:
                continue
            dur = max(0.05, t1 - t0)
            per = dur / len(toks)
            for k, wt in enumerate(toks):
                ws = t0 + k * per
                words.append({
                    "text": wt, "start": round(ws, 3),
                    "end": round(ws + per, 3), "type": "word",
                    "speaker_id": "speaker_0",
                })
    # ensure sorted, non-overlapping-ish
    words.sort(key=lambda w: w["start"])
    return words


def words_to_scribe(words: list[dict], note: str = "") -> dict:
    text = " ".join(w["text"] for w in words)
    dur = words[-1]["end"] if words else 0.0
    return {
        "language_code": "eng",
        "text": text,
        "words": words,
        "audio_duration_secs": round(dur, 2),
        "note": note,
    }


# ── harvest via InnerTube (works when yt-dlp is IP-blocked) ─────────────────

ANDROID_KEY = "AIzaSyA8eiZmM1FaDVjRy-df2OKiwaqSkS6Eo4"
PLAYER_URL = f"https://www.youtube.com/youtubei/v1/player?key={ANDROID_KEY}"


def innertube_captions(video_id: str, timeout: int = 20) -> tuple[str, str]:
    """InnerTube player API → (vtt_or_xml, title). No cookies needed."""
    import urllib.request

    def _post(payload: dict) -> dict:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            PLAYER_URL, data=data,
            headers={"Content-Type": "application/json",
                     "User-Agent": "com.google.android.youtube/20.10.38 "
                                   "(Linux; U; Android 13) gzip"},
            method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())

    clients = [
        {"clientName": "ANDROID", "clientVersion": "20.10.38",
         "androidSdkVersion": 34, "hl": "en", "gl": "US"},
        {"clientName": "IOS", "clientVersion": "20.10.3",
         "deviceModel": "iPhone16,2", "hl": "en", "gl": "US"},
        {"clientName": "WEB", "clientVersion": "2.20250101.00",
         "hl": "en", "gl": "US"},
    ]
    title = "unknown"
    for client in clients:
        try:
            player = _post({"videoId": video_id, "context": {"client": client}})
        except Exception:
            continue
        title = player.get("videoDetails", {}).get("title") or title
        tracks = (player.get("captions", {})
                  .get("playerCaptionsTracklistRenderer", {})
                  .get("captionTracks", []))
        if not tracks:
            continue

        def _rank(t):
            lang = t.get("languageCode") or ""
            kind = t.get("kind") or ""
            if lang == "en" and kind != "asr":
                return 0
            if lang.startswith("en"):
                return 1
            return 2
        for track in sorted(tracks, key=_rank):
            url = track.get("baseUrl")
            if not url:
                continue
            # timedtext often returns XML even with fmt=json3 — parse both
            for sep in ("&fmt=json3", "&fmt=srv3", ""):
                try:
                    req = urllib.request.Request(
                        url + sep, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=timeout) as resp:
                        body = resp.read().decode("utf-8", errors="replace")
                    words = []
                    if body.lstrip().startswith("{"):
                        words = json3_to_words(body)
                    elif "<timedtext" in body or "<p " in body:
                        words = srv3_to_words(body)
                    elif "<v " in body or "-->" in body:
                        words = vtt_to_words(body)
                    if len(words) >= 20:
                        sc = words_to_scribe(
                            words, note=f"innertube {video_id}")
                        return json.dumps(sc), title
                except Exception:
                    continue
    raise RuntimeError(f"innertube captions failed for {video_id}")


def srv3_to_words(body: str) -> list[dict]:
    """Parse timedtext format 3 XML: <p t=MS d=MS>text</p> → words."""
    matches = re.findall(
        r'<p[^>]*\bt="([^"]*)"[^>]*\bd="([^"]*)"[^>]*>(.*?)</p>',
        body, re.DOTALL)
    words: list[dict] = []
    for t_s, d_s, txt in matches:
        t0 = int(t_s) / 1000.0
        dur = int(d_s) / 1000.0
        clean = _TAG.sub("", txt)
        toks = _WORDISH.findall(clean)
        if not toks or dur <= 0:
            continue
        per = dur / len(toks)
        for k, wt in enumerate(toks):
            ws = t0 + k * per
            words.append({
                "text": wt, "start": round(ws, 3),
                "end": round(ws + per, 3), "type": "word",
                "speaker_id": "speaker_0",
            })
    words.sort(key=lambda w: w["start"])
    return words


def json3_to_words(body: str) -> list[dict]:
    """Parse YouTube timedtext json3 into word list."""
    try:
        d = json.loads(body)
    except json.JSONDecodeError:
        return []
    words: list[dict] = []
    for ev in d.get("events") or []:
        segs = ev.get("segs") or []
        t0 = (ev.get("tStartMs") or 0) / 1000.0
        dur = (ev.get("dDurationMs") or 0) / 1000.0
        # if segments have their own offsets, use them; else split evenly
        if segs and any("tOffsetMs" in s for s in segs):
            for s in segs:
                txt = (s.get("utf8") or "").strip()
                if not txt or txt == "\n":
                    continue
                st = t0 + (s.get("tOffsetMs") or 0) / 1000.0
                # end = next seg start or event end
                en = t0 + dur
                for wt in _WORDISH.findall(txt):
                    words.append({
                        "text": wt, "start": round(st, 3),
                        "end": round(en, 3), "type": "word",
                        "speaker_id": "speaker_0",
                    })
        else:
            text = "".join(s.get("utf8") or "" for s in segs)
            toks = _WORDISH.findall(text)
            if not toks or dur <= 0:
                continue
            per = dur / len(toks)
            for k, wt in enumerate(toks):
                ws = t0 + k * per
                words.append({
                    "text": wt, "start": round(ws, 3),
                    "end": round(ws + per, 3), "type": "word",
                    "speaker_id": "speaker_0",
                })
    words.sort(key=lambda w: w["start"])
    return words


def _ytid(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else url

def ytdlp_captions(url: str, langs: list[str] | None = None) -> tuple[str, str]:
    """Fetch best available captions. Returns (vtt_text, video_title)."""
    langs = langs or ["en", "en-US", "en-orig"]
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--skip-download", "--no-simulate",
        "--write-auto-subs", "--write-subs",
        "--sub-langs", ",".join(langs),
        "--sub-format", "vtt",
        "-o", "/tmp/yt_harvest_%(id)s",
        "--print-json", "--no-warnings",
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    # find the JSON (last stdout line that parses)
    info = None
    for line in reversed(r.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                info = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if not info:
        # fallback: try to read any /tmp/yt_harvest_*.vtt
        vtts = list(Path("/tmp").glob("yt_harvest_*.vtt"))
        if not vtts:
            raise RuntimeError(f"no captions / no info: {r.stderr[-300:]}")
        return vtts[0].read_text(encoding="utf-8", errors="replace"), "unknown"
    vid = info.get("id", "")
    title = info.get("title", "unknown")
    # prefer downloaded vtt
    for pat in (f"/tmp/yt_harvest_{vid}*.vtt", f"/tmp/yt_harvest_*.vtt"):
        vtts = list(Path("/tmp").glob(pat.replace("/tmp/", "")))
        if not vtts:
            vtts = list(Path("/tmp").glob(f"yt_harvest_*{vid}*.vtt"))
        if vtts:
            return vtts[0].read_text(encoding="utf-8", errors="replace"), title
    # last resort: requested_subtitles URLs
    subs = info.get("requested_subtitles") or info.get("subtitles") or {}
    for lang in langs:
        if lang in subs and subs[lang]:
            sub_url = (subs[lang] if isinstance(subs[lang], dict) else {}).get("url")
            if sub_url:
                import urllib.request
                with urllib.request.urlopen(sub_url, timeout=30) as resp:
                    return resp.read().decode("utf-8", errors="replace"), title
    raise RuntimeError("captions not found after yt-dlp")


# ── from plain .txt transcript ──────────────────────────────────────────────

def txt_to_scribe(txt_path: Path, note: str = "") -> dict:
    """Plain transcript → approximate word timings (even spacing).

    WARNING: timing is SYNTHETIC (even WPM). Good for content/topics,
    NOT for measured timing claims. Mark provenance accordingly.
    """
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    # strip common transcript headers / speaker labels
    raw = re.sub(r"^\s*\[.*?\]\s*$", "", raw, flags=re.M)
    raw = re.sub(r"^[A-Z][A-Z .'-]{2,}:\s*", "", raw, flags=re.M)
    toks = _WORDISH.findall(raw)
    if not toks:
        raise ValueError(f"no words in {txt_path}")
    # assume 150 wpm default (stand-up varies 120-200)
    wpm = 150.0
    per = 60.0 / wpm
    words = []
    t = 0.0
    for wt in toks:
        words.append({
            "text": wt, "start": round(t, 3), "end": round(t + per * 0.9, 3),
            "type": "word", "speaker_id": "speaker_0",
        })
        t += per
    return words_to_scribe(
        words, note=f"SYNTHETIC timing from {txt_path.name} @ {wpm}wpm — "
                    f"NOT measured; content-only")


# ── analyze + graph patch ───────────────────────────────────────────────────

def run_analysis(scribe_path: Path, comedian: str) -> dict | None:
    mod = _load_analyzer()
    if not mod:
        return None
    try:
        result = mod.analyze(scribe_path, comedian)
        out = ANALYSIS / f"{comedian}-{scribe_path.stem}.json"
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
        return result
    except Exception as e:  # noqa: BLE001
        print(f"  analysis failed: {e}")
        return None


def graph_patch(result: dict, comedian: str, title: str,
                scribe_rel: str, synthetic: bool = False) -> dict:
    """Build the sets[] fragment ready to merge into comedian-graph.json."""
    tp = result.get("timing") or result.get("timing_profile") or {}
    pcs = result.get("punch_candidates") or result.get("punches") or []
    return {
        "set_id": f"{comedian}_{slugify(title)[:40]}",
        "title": title,
        "status": "synthetic-timing" if synthetic else "harvested",
        "transcript": {
            "path": scribe_rel,
            "format": "scribe word-timed",
            "words": tp.get("word_count", 0),
            "duration_s": tp.get("duration_s", 0),
        },
        "timing_measured": {
            **{k: tp.get(k) for k in
               ("wpm", "pause_count", "pause_bins", "mean_pause_s",
                "median_pause_s", "max_pause_s", "punch_pauses_s")},
            "thesis": (
                "SYNTHETIC timing — even WPM, content-only"
                if synthetic else
                f"wpm={tp.get('wpm')} · max_hold={tp.get('max_pause_s')}s · "
                f"topic_pauses={ (tp.get('pause_bins') or {}).get('topic', 0) }"),
        },
        "punch_candidates": pcs[:12],
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", help="YouTube URL")
    ap.add_argument("--comedian", required=True, help="comedian_id (e.g. theo-von)")
    ap.add_argument("--title", default="", help="set title (default: video title)")
    ap.add_argument("--from-transcript", help="plain .txt transcript path")
    ap.add_argument("--wpm", type=float, default=150,
                    help="assumed WPM for .txt synthetic timing")
    args = ap.parse_args()

    slug = slugify(args.title or "set")
    scribe_path = SCRIBE / f"{args.comedian}-{slug}.json"

    if args.from_transcript:
        tp = Path(args.from_transcript)
        print(f"[txt] {tp} → scribe (SYNTHETIC timing @ {args.wpm}wpm)")
        # patch wpm by rewriting after (txt_to_scribe hardcodes 150)
        sc = txt_to_scribe(tp, note=f"SYNTHETIC @ {args.wpm}wpm — content-only")
        scribe_path.write_text(json.dumps(sc, indent=1), encoding="utf-8")
        synthetic = True
        title = args.title or tp.stem
    elif args.url:
        vid = _ytid(args.url)
        print(f"[innertube] fetching captions for {vid}")
        sc = None
        title = args.title
        synthetic = False
        try:
            body, vtitle = innertube_captions(vid)
            if body.lstrip().startswith("{"):
                sc = json.loads(body)
                words = sc["words"]
            else:
                words = vtt_to_words(body)
                sc = words_to_scribe(words, note=f"innertube {vid}")
            if len(words) < 20:
                raise RuntimeError(f"only {len(words)} words")
            scribe_path.write_text(json.dumps(sc, indent=1), encoding="utf-8")
            title = args.title or vtitle
            print(f"  {len(words)} words · {sc['audio_duration_secs']}s")
        except Exception as e:
            print(f"  innertube failed ({e}); trying yt-dlp")
            try:
                vtt, vtitle = ytdlp_captions(args.url)
                words = vtt_to_words(vtt)
                if len(words) < 20:
                    raise RuntimeError(f"only {len(words)} words from yt-dlp")
                sc = words_to_scribe(words, note=f"yt-dlp captions of {vtitle}")
                scribe_path.write_text(json.dumps(sc, indent=1), encoding="utf-8")
                title = args.title or vtitle
                print(f"  {len(words)} words · {sc['audio_duration_secs']}s")
            except Exception as e2:
                raise SystemExit(
                    f"no captions from any source for {vid}: {e2}\n"
                    f"Options: (1) provide cookies to yt-dlp, "
                    f"(2) use --from-transcript with a .txt, "
                    f"(3) drop a pre-made scribe JSON into scribe/")
    else:
        ap.error("need a URL or --from-transcript")

    print(f"[scribe] {scribe_path}")
    result = run_analysis(scribe_path, args.comedian)
    if result:
        patch = graph_patch(result, args.comedian, title,
                            str(scribe_path.relative_to(HERE)),
                            synthetic=synthetic)
        patch_path = ANALYSIS / f"{args.comedian}-{slug}-graph-patch.json"
        patch_path.write_text(json.dumps(patch, indent=1), encoding="utf-8")
        print(f"[analysis] {ANALYSIS / (args.comedian + '-' + scribe_path.stem + '.json')}")
        print(f"[patch]    {patch_path}")
        print("\n=== GRAPH PATCH (paste into sets[]) ===")
        print(json.dumps(patch, indent=1)[:1500])
    else:
        print("[analysis] analyzer unavailable — scribe saved, run analyze_set.py manually")


if __name__ == "__main__":
    main()
