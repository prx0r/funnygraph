#!/usr/bin/env python3
"""Build/refresh profiles for all R2 comedians.

For each comedian in data/r2/site_manifest.json:
  - Create graph if missing (indie tier, UK region default)
  - Update existing stubs (fill discovery + r2 linkage)
  - Never clobber full-identity graphs (only add r2/youtube linkage)
  - Attach youtube clip stats + set_queue → R2 specials

Schema: pogtown.comedian.v1 (same as everywhere).
"""
from __future__ import annotations
import json, time
from pathlib import Path
from collections import defaultdict

LOCAL = Path("/root/funnygraph")
COMEDIANS = LOCAL / "comedians"
R2DIR = LOCAL / "data" / "r2"
TODAY = time.strftime("%Y-%m-%d")

def display(slug: str) -> str:
    return slug.replace("-", " ").title()

def blank_graph(cid: str, name: str) -> dict:
    return {
        "schema": "pogtown.comedian.v1",
        "comedian_id": cid,
        "name": name,
        "tier": "indie",
        "note": "Indie-tier graph: R2 transcript-linked profile.",
        "version": 1,
        "created": TODAY,
        "annotator": "sync_r2_profiles.py",
        "identity": {
            "deal": "", "premise": "", "archetype": "indie_draft",
            "awareness": "unknown", "awareness_note": "",
            "philosophy": {}, "dramatic_core": {},
            "misinterpretation_rule": "", "contradictions": [],
            "status_model": {}, "expression": {}, "modulator_range": [],
            "profile": {}, "operator_priors": {},
            "preferred_theories": [], "threads": [], "problem_space": [],
        },
        "discovery": {},
        "sets": [],
        "essay_seeds": [],
        "provenance": {
            "tier": "indie",
            "rules_held": ["stage persona only", "no verbatim lines"],
        },
    }

def main():
    manifest = json.loads((R2DIR / "site_manifest.json").read_text())
    specials_dir = R2DIR / "specials"

    created = 0
    stubs_updated = 0
    fulls_linked = 0
    skipped = 0

    for slug, entry in sorted(manifest["comedians"].items()):
        name = entry.get("name") or display(slug)
        n_clips = entry.get("n_clips", 0)
        n_specials = entry.get("n_specials", 0)
        clips = entry.get("clips", [])
        specials = entry.get("specials", [])

        gpath = COMEDIANS / slug / "comedian-graph.json"
        exists = gpath.exists()
        if exists:
            try:
                g = json.loads(gpath.read_text())
            except Exception:
                g = blank_graph(slug, name)
        else:
            g = blank_graph(slug, name)

        is_full = bool(g.get("identity", {}).get("deal"))
        is_king = g.get("tier") == "king"

        # Always update name if blank
        if not g.get("name"):
            g["name"] = name

        # Discovery provenance
        disc = g.setdefault("discovery", {})
        srcs = disc.setdefault("discovered_from", [])
        if "r2:comedy-specials" not in srcs:
            srcs.append("r2:comedy-specials")
        disc["r2_comedian"] = True
        if n_clips:
            disc["r2_clips"] = n_clips
        if n_specials:
            disc["r2_specials"] = n_specials

        # YouTube block (clip stats)
        if clips:
            with_views = [c for c in clips if c.get("views")]
            total_views = sum(c.get("views") or 0 for c in with_views)
            timed = sum(1 for c in clips if c.get("words_timed"))
            g["youtube"] = {
                "clips": n_clips,
                "total_views": total_views,
                "timed_clips": timed,
                "r2_linked": True,
                "top_clip": {k: clips[0].get(k) for k in
                             ("videoId", "title", "channel", "views",
                              "duration_s", "url", "r2_clip_key",
                              "transcript_url") if clips[0].get(k)} if clips else None,
            }

        # set_queue → R2 specials (for future measured sets)
        if specials:
            sp_titles = [s.get("title") or s.get("special_slug") for s in specials[:8]]
            timed_sp = sum(1 for s in specials if s.get("words_timed"))
            g["set_queue"] = {
                "note": f"{n_specials} full specials in R2 ({timed_sp} timed). "
                        f"Ready for analyze_set → known_bits + timing_measured.",
                "r2_specials": [s.get("r2_special_key") or s.get("special_slug")
                                for s in specials],
                "special_titles": sp_titles,
                "blocked_on": "ingest (r2 specials are transcript-linked)",
            }

        # Transcript availability summary (lightweight)
        total_tw = sum(c.get("n_words") or 0 for c in clips)
        total_sw = sum(s.get("n_words") or 0 for s in specials)
        if total_tw or total_sw:
            g["transcripts"] = {
                "clip_words": total_tw,
                "special_words": total_sw,
                "timed_clips": sum(1 for c in clips if c.get("words_timed")),
                "timed_specials": sum(1 for s in specials if s.get("words_timed")),
                "r2_source": "r2:comedy-specials",
                "synced": TODAY,
            }

        # Region default: UK (this harvest was UK-focused) unless already tagged
        if not g.get("region"):
            g["region"] = "uk"
        if not g.get("continent"):
            g["continent"] = "europe"

        # Tier: never demote a king; new graphs = indie
        if not exists:
            g["tier"] = "indie"
            created += 1
        elif is_full:
            fulls_linked += 1
        elif is_king:
            # king stub (promoted earlier) — keep tier, just link
            stubs_updated += 1
        else:
            stubs_updated += 1

        g["version"] = max(g.get("version", 1), 1)
        g["r2_profiled"] = TODAY

        COMEDIANS.mkdir(exist_ok=True)
        (COMEDIANS / slug).mkdir(exist_ok=True)
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")

    # Also attach specials linkage to full graphs that already existed
    # (already done above via set_queue/transcripts — fulls_linked counted)

    total_graphs = len(list(COMEDIANS.glob("*/comedian-graph.json")))
    print("=== R2 PROFILE BUILD ===")
    print(f"  manifests processed: {len(manifest['comedians'])}")
    print(f"  graphs created:      {created}")
    print(f"  stubs linked:        {stubs_updated}")
    print(f"  full graphs linked:  {fulls_linked}")
    print(f"  total graphs now:    {total_graphs}")

if __name__ == "__main__":
    main()
