#!/usr/bin/env python3
"""Build wave 3 + auto-generate long-tail graphs from transcript data."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from seed_wave2 import make_graph  # noqa: E402
from seed_wave3 import WAVE3  # noqa: E402

OUT = HERE / "comedians"
TR = HERE / "transcripts"


def build_wave3() -> int:
    n = 0
    for cid, seed in WAVE3.items():
        d = OUT / cid
        d.mkdir(exist_ok=True)
        (d / "comedian-graph.json").write_text(
            json.dumps(make_graph(cid, seed), indent=2) + "\n", encoding="utf-8")
        n += 1
    print(f"wave3: {n} graphs")
    return n


STOP = set("""the a an and or of to in on for with is are was were be been have has had
do does did i you he she it we they not no yes so if as at by from but that this
what which who when where why how all any just like know right yeah oh really going
get got one two would could should im ive dont doesnt wasnt didnt its thats theres
hes shes youre were gonna wanna gotta lemme gimme yall cause coz cos""".split())


def transcript_text(cid: str) -> str:
    d = TR / cid
    if not d.exists():
        return ""
    parts = []
    for p in sorted(d.glob("*.txt")):
        try:
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(parts)


def auto_seed(cid: str, display: str, text: str) -> dict:
    """Transcript-grounded minimal seed for the long tail."""
    words = re.findall(r"[a-z']{3,}", text.lower())
    n = len(words)
    c = Counter(w for w in words if w not in STOP and len(w) > 3)
    top = [w for w, _ in c.most_common(12)]
    # style signals
    profane = sum(1 for w in words if w in
                  {"fuck", "fucking", "shit", "bitch", "ass", "damn", "hell"}) / max(1, n)
    questions = text.count("?") / max(1, len(text.split(". ")))
    energy = "high" if profane > 0.008 else "medium" if profane > 0.003 else "low-key"
    return {
        "name": display,
        "deal": f"Stand-up voice with {n:,} words of specials in the corpus. Top distinctive vocabulary: {', '.join(top[:5])}.",
        "premise": f"Auto-drafted from {n:,} transcript words — needs human review for the engine thesis.",
        "archetype": "auto_draft", "awareness": "unknown",
        "awareness_note": "auto-draft — needs human review",
        "philosophy": {"ontology": f"Top topics suggest: {', '.join(top[:4])}.",
            "epistemology": "auto-draft", "axiology": "auto-draft",
            "causality": "auto-draft", "agency": "auto-draft"},
        "dramatic_core": {"want": "auto-draft", "fear": "auto-draft",
            "need": "auto-draft", "self_model": "auto-draft",
            "blind_spots": ["auto-draft — needs human review"]},
        "misinterpretation_rule": "auto-draft — derive from distinctive vocabulary and topics",
        "contradictions": [],
        "status_model": {"desired_status": "auto-draft", "felt_status": "auto-draft"},
        "expression": {"default_register": "auto-draft",
            "emotional_restraint": energy,
            "tells": [f"top words: {', '.join(top[:5])}"]},
        "modulator_range": [],
        "profile": {"energy": 0.5, "pace": "auto-draft", "gesture_frequency": 0.5,
                    "punchline_hold_ms": 800},
        "operator_priors": {"rigidify": 0.5, "literalize": 0.5,
            "double_interpret": 0.5, "status_invert": 0.5,
            "character_violation": 0.5,
            "status": "auto-draft from transcript stats"},
        "preferred_theories": [],
        "threads": top[:6],
        "problem_space": top[6:10],
        "timing_doctrine": "auto-draft — needs word-timed analysis",
        "style_thesis": f"Auto-draft from {n:,} words. Distinctive vocabulary centers on {', '.join(top[:5])}. Human review needed for the engine thesis.",
        "known_bits": [],
    }


# display-name cleanup for auto drafts
SKIP = {"comedy-central-presents", "bill-burr-presents", "amy-schumer-presents",
        "pete-davidson-presents", "the-standups", "latin-history-for-morons",
        "chris-rock-total-blackout", "ricky-gervais-live-2", "russell-howard-live",
        "gabriel-fluffy-iglesias", "david-chappelle",
        "jeff-foxworthy-larry-the-cable-guy"}


def build_longtail() -> int:
    n = 0
    for tdir in sorted(TR.iterdir()):
        if not tdir.is_dir():
            continue
        cid = tdir.name
        if (OUT / cid / "comedian-graph.json").exists():
            continue
        if cid in SKIP:
            continue
        text = transcript_text(cid)
        words = re.findall(r"[a-z']{3,}", text.lower())
        if len(words) < 500:
            continue
        display = " ".join(w.capitalize() for w in cid.split("-"))
        seed = auto_seed(cid, display, text)
        d = OUT / cid
        d.mkdir(exist_ok=True)
        g = make_graph(cid, seed)
        g["note"] = ("AUTO-DRAFT from transcript stats — needs human review for "
                     "identity/style thesis. Threads and vocabulary are measured.")
        (d / "comedian-graph.json").write_text(
            json.dumps(g, indent=2) + "\n", encoding="utf-8")
        n += 1
    print(f"longtail: {n} auto-draft graphs")
    return n


def main() -> None:
    a = build_wave3()
    b = build_longtail()
    total = len([p for p in OUT.iterdir()
                 if (p / "comedian-graph.json").exists()])
    print(f"total graphs: {total} (wave3={a}, longtail={b})")


if __name__ == "__main__":
    main()
