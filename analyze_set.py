"""Real-comedian set analysis — ingest word-timed set, emit GTVH + timing.

Pipeline step for SPEC-comedian-analysis.md. Reads scribe word JSONs
(theory/scribe/*.json with word-level start/end), segments into beats by
pause gaps, extracts timing profiles, classifies GTVH per beat, and
aggregates operator frequencies. Outputs analysis JSON per set.

Timing taxonomy from Attardo & Pickering 2011:
  very_short 0.2-0.4 · short 0.4-0.6 · substantial 0.6-0.8 · topic >0.8
Punch lines are preceded by substantial pauses or longer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent
sys.path.insert(0, str(HERE / "audition"))

PAUSE_BINS = {
    "very_short": (0.2, 0.4),
    "short": (0.4, 0.6),
    "substantial": (0.6, 0.8),
    "topic": (0.8, 99.0),
}
# Beat segmentation: a gap >= this starts a new beat (seconds).
BEAT_GAP_S = 0.5
# A gap >= this before a word is a candidate punch-pause.
PUNCH_PAUSE_S = 0.6


def load_words(path: Path) -> list[dict]:
    d = json.loads(path.read_text())
    if "words" not in d:
        raise ValueError(f"{path} has no 'words' key")
    return d["words"], d


def pause_bins(pauses: list[float]) -> dict:
    counts = {k: 0 for k in PAUSE_BINS}
    for p in pauses:
        for name, (lo, hi) in PAUSE_BINS.items():
            if lo <= p < hi:
                counts[name] += 1
                break
        else:
            if p < 0.2:
                counts["very_short"] += 1
    return counts


def segment_beats(words: list[dict], gap_s: float = BEAT_GAP_S) -> list[list[dict]]:
    """Split words into beats where inter-word pause >= gap_s."""
    beats: list[list[dict]] = []
    current: list[dict] = [words[0]] if words else []
    for prev, w in zip(words, words[1:]):
        gap = w["start"] - prev["end"]
        if gap >= gap_s and current:
            beats.append(current)
            current = [w]
        else:
            current.append(w)
    if current:
        beats.append(current)
    return beats


def beat_text(beat: list[dict]) -> str:
    return " ".join(w["text"] for w in beat)


def timing_profile(words: list[dict]) -> dict:
    pauses = [round(w["start"] - p["end"], 3)
              for p, w in zip(words, words[1:]) if w["start"] - p["end"] > 0]
    total = words[-1]["end"] - words[0]["start"] if words else 0.0
    wpm = (len(words) / total * 60) if total > 0 else 0.0
    long_pauses = sorted((p for p in pauses if p >= PUNCH_PAUSE_S), reverse=True)
    return {
        "word_count": len(words),
        "duration_s": round(total, 2),
        "wpm": round(wpm, 1),
        "pause_count": len(pauses),
        "pause_bins": pause_bins(pauses),
        "mean_pause_s": round(sum(pauses) / len(pauses), 3) if pauses else 0,
        "median_pause_s": round(sorted(pauses)[len(pauses) // 2], 3) if pauses else 0,
        "punch_pauses_s": [round(p, 2) for p in long_pauses[:8]],
        "max_pause_s": round(max(pauses), 2) if pauses else 0,
    }


def punch_candidates(words: list[dict]) -> list[dict]:
    """Words preceded by a substantial+ pause — punchline candidates."""
    out = []
    for prev, w in zip(words, words[1:]):
        gap = w["start"] - prev["end"]
        if gap >= PUNCH_PAUSE_S:
            # Fingerprint: the ~7 words starting at w.
            fp = " ".join(x["text"] for x in words[words.index(w):words.index(w) + 7])
            out.append({
                "t_start_s": round(w["start"], 2),
                "pause_before_s": round(gap, 2),
                "fingerprint": fp[:60],
            })
    return out[:12]


def analyze(path: Path, comedian: str) -> dict:
    words, meta = load_words(path)
    beats = segment_beats(words)
    tp = timing_profile(words)
    pcs = punch_candidates(words)

    # GTVH per beat (code-only SI/LA; SO/LM/TA/NS need Jev key — try, else null).
    try:
        import gtvh
        _has_jev = True
    except Exception:
        gtvh = None
        _has_jev = False

    beat_rows = []
    for i, b in enumerate(beats):
        txt = beat_text(b)
        row = {
            "beat": i,
            "t0_s": round(b[0]["start"], 2),
            "t1_s": round(b[-1]["end"], 2),
            "words": len(b),
            "text": txt[:200],
            "pause_after_s": round(
                beats[i + 1][0]["start"] - b[-1]["end"], 2
            ) if i + 1 < len(beats) else 0,
        }
        if gtvh:
            try:
                row["gtvh"] = gtvh.classify(txt)
            except Exception:
                row["gtvh"] = {"provenance": "unavailable"}
        beat_rows.append(row)

    try:
        src = str(path.relative_to(REPO))
    except ValueError:
        src = str(path)

    return {
        "comedian": comedian,
        "source": src,
        "note": meta.get("note", ""),
        "audio_duration_s": meta.get("audio_duration_secs"),
        "timing": tp,
        "punch_candidates": pcs,
        "beats": beat_rows,
        "beat_count": len(beats),
        "gtvh_coverage": {
            "classified": sum(1 for r in beat_rows if (r.get("gtvh") or {}).get("SO")),
            "total": len(beat_rows),
        },
        "provenance": ("SYNTHETIC timing — content only" if "SYNTHETIC" in str(meta.get("note", ""))
                       else "measured — word timestamps from scribe; GTVH "
                       + ("jev+code" if _has_jev else "code-only")),
    }


def main():
    outs = []
    for stem, comedian in [
        ("louis_roadrage", "louis_ck"),
        ("norm_moth", "norm_macdonald"),
    ]:
        p = REPO / "theory" / "scribe" / f"{stem}.json"
        if not p.exists():
            print(f"skip {stem} (missing)")
            continue
        r = analyze(p, comedian)
        outp = REPO / "theory" / "analysis" / f"{stem}_analysis.json"
        outp.parent.mkdir(exist_ok=True)
        outp.write_text(json.dumps(r, indent=1))
        print(f"{stem}: {r['beat_count']} beats, "
              f"wpm={r['timing']['wpm']}, "
              f"punch_pauses={len(r['timing']['punch_pauses_s'])}, "
              f"gtvh={r['gtvh_coverage']}")
        outs.append(str(outp))
    return outs


if __name__ == "__main__":
    main()
