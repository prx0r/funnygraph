#!/usr/bin/env python3
"""HUMOR TYPES + SPECIALS BOARD — classify every comedian, rank every special.

Humor-type taxonomy (from our operator/theory registry):
  dark-confessional, absurdist, observational, roast, storytelling,
  one-liner, meta, character, rant, crowd-improv, musical, surreal,
  clean-everyman, provocateur

Classification signals (in order):
  1. archetype → type map (authored, strongest)
  2. operator_priors + preferred_theories (authored)
  3. transcript stats: profanity rate, question rate, exclamation rate (measured)

Specials board: every specials_rated[] across all comics → IMDb WR →
best specials of all time + darkest + by-type rankings.

Usage: python3 classify_humor.py
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
TR = HERE / "transcripts"
OUT = HERE / "rankings"

ARCHETYPE_TO_TYPE = {
    "sincere_storyteller": "dark-confessional",
    "suspension_deadpan": "absurdist",
    "observational_auditor": "observational",
    "rhythm_prosecutor": "observational",
    "prophet_curmudgeon": "rant",
    "philosophical_raconteur": "storytelling",
    "whimsical_float": "absurdist",
    "confessional_firestorm": "dark-confessional",
    "deadpan_absurdist": "absurdist",
    "architect_one_liner": "one-liner",
    "surgical_one_liner": "one-liner",
    "anxious_surrealist": "surreal",
    "deadpan-report": "absurdist",
    "sleepy-report": "surreal",
    "meta-architect": "meta",
    "meta_pop_prophet": "meta",
    "long_con_architect": "meta",
    "character_vault": "character",
    "manic_character_vault": "character",
    "surreal_historian": "character",
    "immigrant_observer": "observational",
    "swamp_philosopher": "surreal",
    "cosmic_gremlin": "surreal",
    "lovable_idiot_warlord": "storytelling",
    "rage_apologist": "rant",
    "degenerate_philosopher": "rant",
    "truth_bully": "rant",
    "lawyer_demolition": "rant",
    "controlled_confessor": "roast",
    "grin_assassin": "roast",
    "status_assassin": "roast",
    "toddler_provocateur": "provocateur",
    "provocateur_smug": "provocateur",
    "confessional_assassin": "dark-confessional",
    "therapy_neurotic": "dark-confessional",
    "melancholy_craftsman": "storytelling",
    "old_radio_neurotic": "storytelling",
    "wholesome_confused": "clean-everyman",
    "anxious_everyman": "clean-everyman",
    "clean_machine": "clean-everyman",
    "man_child_epic": "storytelling",
    "zero_status_engine": "one-liner",
    "page_to_stage": "crowd-improv",
    "clip_machine": "crowd-improv",
    "firestarter": "crowd-improv",
    "chaos_regular": "crowd-improv",
    "chaos-machine": "crowd-improv",
    "absurdist_firecracker": "absurdist",
    "drunken_curmudgeon": "rant",
    "curmudgeon": "rant",
    "bridge_translator": "observational",
    "millennial_anthropologist": "observational",
    "domestic_surrealist": "surreal",
    "ethnographer-deadpan": "observational",
    "storytelling_confessor": "storytelling",
    "honest_autopsy": "dark-confessional",
    "nerd_professor": "observational",
    "tender-report": "storytelling",
    "designer": "one-liner",
    "sleepy_surrealist": "surreal",
    "argument_brawler": "rant",
    "exasperated_traditionalist": "rant",
    "meta_architect": "meta",
    "deadpan_dark": "dark-confessional",
    "exasperated-traditionalist": "rant",
    "barstool-prophet": "rant",
    "jazz-confessional": "dark-confessional",
    "anarchist": "provocateur",
    "courtroom": "rant",
}

THEORY_TO_TYPE = {
    "benign_violation": "dark-confessional",
    "literalise": "absurdist",
    "rigidity": "meta",
    "status_reversal": "roast",
    "incongruity": "observational",
    "bisociation": "surreal",
    "escalation": "storytelling",
    "bogus_logic": "absurdist",
    "repetition_variation": "one-liner",
    "garden_path": "observational",
    "two_stories": "storytelling",
    "split_knowledge": "dark-confessional",
    "persona_gap": "character",
    "character_violation": "provocateur",
}


def transcript_signals(cid: str) -> dict:
    d = TR / cid
    if not d.exists():
        return {}
    text = ""
    for p in sorted(d.glob("*.txt")):
        try:
            text += p.read_text(encoding="utf-8", errors="replace") + "\n"
        except OSError:
            continue
    words = re.findall(r"[a-z']+", text.lower())
    if len(words) < 500:
        return {}
    n = len(words)
    profane = sum(1 for w in words if w in
                  {"fuck", "fucking", "shit", "bitch", "ass", "damn",
                   "cunt", "dick", "piss"}) / n
    return {
        "profanity_rate": round(profane, 4),
        "dark": profane > 0.008,
        "clean": profane < 0.002,
        "words": n,
    }


def classify(j: dict, sig: dict) -> dict:
    ident = j.get("identity", {})
    arch = ident.get("archetype", "")
    theories = ident.get("preferred_theories", [])
    votes: Counter = Counter()
    if arch in ARCHETYPE_TO_TYPE:
        votes[ARCHETYPE_TO_TYPE[arch]] += 3
    for t in theories:
        if t in THEORY_TO_TYPE:
            votes[THEORY_TO_TYPE[t]] += 1
    # measured overrides
    if sig.get("dark"):
        votes["dark-confessional"] += 1
    if sig.get("clean"):
        votes["clean-everyman"] += 1
    # transcript fallback for auto-drafts: profanity decides dark/clean,
    # question-rate hints crowd-improv, exclamation hints rant
    if not votes and sig.get("words"):
        if sig.get("dark"):
            votes["dark-confessional"] += 2
        elif sig.get("clean"):
            votes["clean-everyman"] += 2
        else:
            votes["observational"] += 1
    if not votes:
        return {"primary": "unclassified", "scores": {}, "method": "none"}
    total = sum(votes.values())
    ranked = votes.most_common(3)
    return {
        "primary": ranked[0][0],
        "secondary": ranked[1][0] if len(ranked) > 1 else None,
        "scores": {k: round(v / total, 2) for k, v in ranked},
        "method": "archetype+theories" + ("+transcript" if sig else ""),
    }


def imdb_wr(rating: float, votes: int, m: int = 1000, C: float = 7.0) -> float:
    return round((votes / (votes + m)) * rating + (m / (votes + m)) * C, 3)


def main() -> None:
    type_counts: Counter = Counter()
    specials = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        if d.name in EXCLUDED:
            continue
        j = json.loads(g.read_text())
        sig = transcript_signals(d.name)
        ht = classify(j, sig)
        j["humor_type"] = ht
        type_counts[ht["primary"]] += 1
        # specials for the board
        for s in j.get("specials_rated") or []:
            if not s.get("imdb_rating") or not s.get("imdb_votes"):
                continue
            specials.append({
                "special": s.get("title"), "year": s.get("year"),
                "comedian": j.get("name", d.name),
                "comedian_id": d.name,
                "imdb_id": s.get("imdb_id"),
                "rating": s.get("imdb_rating"), "votes": s.get("imdb_votes"),
                "wr": imdb_wr(s["imdb_rating"], s["imdb_votes"]),
                "standout": bool(s.get("standout")),
                "humor_type": ht["primary"],
                "generation": (j.get("generation") or {}).get("id"),
            })
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")

    print("=== HUMOR TYPE CENSUS ===")
    for t, n in type_counts.most_common():
        print(f"  {t:20} {n}")

    # best specials of all time
    specials.sort(key=lambda s: -s["wr"])
    (OUT / "specials.json").write_text(
        json.dumps(specials[:100], indent=1))
    print(f"\n=== BEST SPECIALS (top 15 by WR) ===")
    for i, s in enumerate(specials[:15], 1):
        print(f"{i:>2} {s['rating']:.1f}({s['votes']:,}) {s['special'][:45]:45} "
              f"{s['comedian'][:20]} [{s['humor_type']}]")

    # darkest specials: high rating + dark-confessional/provocateur/rant types
    dark_types = {"dark-confessional", "provocateur", "rant"}
    dark = [s for s in specials if s["humor_type"] in dark_types]
    dark.sort(key=lambda s: -s["wr"])
    (OUT / "specials_dark.json").write_text(json.dumps(dark[:50], indent=1))
    print(f"\n=== DARKEST (top 10) ===")
    for i, s in enumerate(dark[:10], 1):
        print(f"{i:>2} {s['rating']:.1f} {s['special'][:45]:45} {s['comedian'][:20]}")

    # by humor type
    by_type: dict = {}
    for s in specials:
        by_type.setdefault(s["humor_type"], []).append(s)
    for t in by_type:
        by_type[t].sort(key=lambda s: -s["wr"])
        by_type[t] = by_type[t][:20]
    (OUT / "specials_by_type.json").write_text(json.dumps(by_type, indent=1))
    print(f"\nsaved rankings/specials.json ({len(specials)}), "
          f"specials_dark.json ({len(dark)}), specials_by_type.json")


if __name__ == "__main__":
    main()
