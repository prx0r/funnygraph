#!/usr/bin/env python3
"""INDIE — small-comic lane on the unified schema (tier:"indie").

Design decision (2026-10-17): ONE schema (pogtown.comedian.v1) + tier field,
not a separate graph type. Evidence: 123 auto-drafts already live fine in
king schema with nulls, and every indie-only field (discovery, theory_score,
nearest_greats, subs) is useful for kings too. Promotion = flip tier + fill
fields. Zero migration.

  comedians/{cid}/comedian-graph.json with tier indie has:
    discovery{}: discovered_from[], discovery_note, kt_appearances, subs
    theory_score{}: fame-independent joke quality (gates over material)
    nearest_greats[]: latent-space kings they resemble
  kings exclude indies from canon boards; spotlight + for-you include them.

Usage:
  python3 indie.py --seed-lists        # (re)seed discovery entries
  python3 indie.py --score             # theory-score indies with material
  python3 indie.py --match-greats      # nearest kings per indie
  python3 indie.py --for-you "louis-ck,norm-macdonald,mitch-hedberg"
  python3 indie.py --spotlight         # small comic of the week queue
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
KT = Path("/root/characters2/theory/killtony-minutes")
SCRIBE = Path("/root/characters2/theory/scribe")

# curated discovery: name → (sources, note)
CURATED: dict[str, dict] = {
    "andrew-orolfo": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "chris-higgins": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "curtis-cook": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "felicia-folkes": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "hannah-magy": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "jessie-lee": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "maddie-wiener": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "max-higgins": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "richard-perez": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "sam-rocha": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "victoria-vincent": {"sources": ["timeout-2026"], "note": "Time Out 12 to watch 2026"},
    "marcello-hernandez": {"sources": ["comedyville-2026", "snl"], "note": "SNL breakout, Netflix American Boy"},
    "stavros-halkias": {"sources": ["comedyville-2026", "podcast"], "note": "Cum Town → Live at the Lodge Room indie special"},
    "matt-rife": {"sources": ["comedyville-2026", "tiktok"], "note": "TikTok crowd-work → touring juggernaut"},
    "jay-jurden": {"sources": ["comedyville-2026"], "note": "Debut hour Yes Ma'am, punchline-packed"},
    "darrick-stroup": {"sources": ["comedyville-2026", "netflix"], "note": "Netflix Nostalgia, top-10 debut"},
    "rafi-bastos": {"sources": ["comedyville-2026"], "note": "Brazil pioneer, English breakout Unfamiliar Territory"},
    "sherise": {"sources": ["comedyville-2026"], "note": "NY scene → film/TV 2026"},
    "dulce-sloan": {"sources": ["comedyville-2026", "daily-show"], "note": "Daily Show correspondent, sharp fearless voice"},
    "hollie-harper": {"sources": ["comedyville-2026"], "note": "Rising 2026"},
    "leah-rudick": {"sources": ["gold-2026"], "note": "Character work translating online→sold-out IRL"},
    "laura-ramoso": {"sources": ["gold-2026"], "note": "Cross-border character comedy, Fey/Poehler opener"},
    "jiaoying-summers": {"sources": ["gold-2026"], "note": "Completed hour, self-built tour"},
    "chloe-petts": {"sources": ["gold-2026", "uk"], "note": "Soho Theatre runs, settling into voice"},
    "jenny-zigrino": {"sources": ["gold-2026"], "note": "Late-night sets, festival headliner, at full power"},
    "rahkie-mateen": {"sources": ["gold-2026"], "note": "Unapologetically Rocky — intimate, brave"},
    "dina-hashem": {"sources": ["gold-2026"], "note": "Deadpan restraint, Prime Dark Little Whispers"},
    "tacarra-williams": {"sources": ["gold-2026"], "note": "Warm observational, personal+topical"},
    "megan-gailey": {"sources": ["gold-2026"], "note": "Rock-solid honesty-and-timing standup"},
    "jeff-arcuri": {"sources": ["deadline-2025", "reddit"], "note": "r/JeffArcuri top-1% subreddit, front-page regular"},
}


def display(cid: str) -> str:
    return " ".join(w.capitalize() for w in cid.split("-"))


def _indies() -> list[tuple[str, dict, Path]]:
    out = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("tier") == "indie":
            out.append((d.name, j, g))
    return out


def _kings() -> list[tuple[str, dict]]:
    out = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("tier", "king") == "king":
            out.append((d.name, j))
    return out


def kt_names() -> dict:
    from collections import Counter
    c: Counter = Counter()
    if not KT.exists():
        return {}
    for p in KT.glob("*.json"):
        s = p.stem
        s = re.sub(r"\.(granular|gemini|performance|stage_timeline).*$", "", s)
        s = re.sub(r"_(raw|short|clip)$", "", s)
        s = re.sub(r"-\d+$", "", s)
        m = re.match(r"^([a-z_]+?)(?:_\d+)?$", s)
        if not m:
            continue
        name = m.group(1)
        if name.startswith("kt") or "passport" in name or "laughs" in name \
                or name in ("walking", "nashville", "casey_theo_transcript",
                            "casey_theo_full_transcript", "casey_theo_podcast_0_10min",
                            "casey_theo_podcast_full", "casey_theo_podcast"):
            continue
        if len(name) > 3:
            c[name] += 1
    return dict(c)


def _blank_indie(cid: str) -> dict:
    return {
        "schema": "pogtown.comedian.v1", "comedian_id": cid,
        "name": display(cid), "tier": "indie",
        "note": "Indie-tier graph: discovery + theory-scored from material.",
        "version": 1, "created": "2026-10-17", "annotator": "indie.py",
        "identity": {"deal": "", "premise": "", "archetype": "indie_draft",
                     "awareness": "unknown", "awareness_note": "",
                     "philosophy": {}, "dramatic_core": {},
                     "misinterpretation_rule": "", "contradictions": [],
                     "status_model": {}, "expression": {}, "modulator_range": [],
                     "profile": {}, "operator_priors": {},
                     "preferred_theories": [], "threads": [], "problem_space": []},
        "discovery": {}, "sets": [], "essay_seeds": [],
        "provenance": {"tier": "indie",
                       "rules_held": ["stage persona only", "no verbatim lines"]},
    }


def seed_lists() -> None:
    n = 0
    for cid, meta in CURATED.items():
        if cid in EXCLUDED:
            continue
        d = COMEDIANS / cid
        d.mkdir(exist_ok=True)
        gpath = d / "comedian-graph.json"
        g = json.loads(gpath.read_text()) if gpath.exists() else _blank_indie(cid)
        g["tier"] = "indie"
        g["discovery"] = {"discovered_from": meta["sources"],
                          "discovery_note": meta["note"]}
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        n += 1
    for raw, count in sorted(kt_names().items()):
        if count < 2:
            continue
        cid = raw.replace("_", "-")
        if (COMEDIANS / cid / "comedian-graph.json").exists():
            # king exists — annotate KT appearances, don't downgrade
            gpath = COMEDIANS / cid / "comedian-graph.json"
            g = json.loads(gpath.read_text())
            g.setdefault("discovery", {}).setdefault(
                "discovered_from", []).append("kill-tony-minutes") \
                if "kill-tony-minutes" not in g.setdefault(
                    "discovery", {}).setdefault("discovered_from", []) else None
            g["discovery"]["kt_appearances"] = count
            gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
            continue
        d = COMEDIANS / cid
        d.mkdir(exist_ok=True)
        gpath = d / "comedian-graph.json"
        g = json.loads(gpath.read_text()) if gpath.exists() else _blank_indie(cid)
        g["tier"] = "indie"
        disc = g.setdefault("discovery", {})
        src = disc.setdefault("discovered_from", [])
        if "kill-tony-minutes" not in src:
            src.append("kill-tony-minutes")
        disc["kt_appearances"] = count
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        n += 1
    print(f"seeded {n} indie entries")


def scribe_text_for(cid: str) -> str:
    texts = []
    for pat in (f"{cid}*.json", f"{cid.replace('-', '_')}*.json"):
        for p in SCRIBE.glob(pat):
            try:
                d = json.loads(p.read_text())
                ws = d.get("words", [])
                if isinstance(ws, list) and ws and isinstance(ws[0], dict):
                    texts.append(" ".join(w.get("text", "") for w in ws))
            except (OSError, json.JSONDecodeError):
                continue
    return " ".join(texts)


def theory_score(text: str) -> dict | None:
    if len(text.split()) < 60:
        return None
    sys.path.insert(0, "/root/noslop/miner/src")
    sys.path.insert(0, "/root/characters2/theory")
    try:
        from human_gate import is_coherent, human_distance
    except Exception:
        return None
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 6][:60]
    if not sents:
        return None
    coh = sum(1 for s in sents if is_coherent(s)[0])
    hum, ai_sum = 0, 0.0
    for s in sents:
        try:
            hd = human_distance(s)
            ai_sum += hd.get("ai_conf", 1.0)
            if hd.get("human_like"):
                hum += 1
        except Exception:
            continue
    n = len(sents)
    return {"n_chunks": n, "coherence_rate": round(coh / n, 3),
            "human_band_rate": round(hum / n, 3),
            "mean_ai_conf": round(ai_sum / n, 3),
            "theory_score": round(0.5 * (coh / n) + 0.5 * (hum / n), 3)}


def score_cmd() -> None:
    n = 0
    for cid, g, gpath in _indies():
        text = scribe_text_for(cid)
        if not text:
            continue
        sc = theory_score(text)
        if sc:
            g["material_words"] = len(text.split())
            g["theory_score"] = sc
            gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
            n += 1
            print(f"  {cid}: theory={sc['theory_score']} "
                  f"(coh {sc['coherence_rate']}, hum {sc['human_band_rate']})")
    print(f"scored {n} indies with material")


def match_greats(top_k: int = 3) -> None:
    kings = _kings()
    king_docs = {}
    for cid, j in kings:
        ident = j.get("identity", {})
        king_docs[cid] = (
            ident.get("deal", "") + " " + ident.get("premise", "") + " " +
            ident.get("misinterpretation_rule", "") + " " +
            " ".join(ident.get("threads", []))).lower()
    n = 0
    for cid, g, gpath in _indies():
        doc = (g.get("name", "") + " " +
               (g.get("discovery") or {}).get("discovery_note", "")).lower()
        words = set(re.findall(r"[a-z]{4,}", doc))
        scored = []
        for kcid, kd in king_docs.items():
            overlap = len(words & set(re.findall(r"[a-z]{4,}", kd)))
            if overlap:
                scored.append((overlap, kcid))
        scored.sort(reverse=True)
        if scored:
            g["nearest_greats"] = [
                {"comedian_id": kcid, "shared_terms": ov}
                for ov, kcid in scored[:top_k]]
            gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
            n += 1
    print(f"matched {n} indies to kings")


def for_you(favs: list[str], n: int = 10) -> None:
    sys.path.insert(0, str(HERE))
    from recommend import build, neighbors
    ids, Z = build()
    recs: dict = {}
    for f in favs:
        f = f.strip()
        if f not in ids:
            print(f"  unknown: {f}")
            continue
        for r in neighbors(ids, Z, f, n=12):
            recs.setdefault(r["comedian_id"], {"sim": 0, "via": []})
            recs[r["comedian_id"]]["sim"] = max(
                recs[r["comedian_id"]]["sim"], r["sim"])
            recs[r["comedian_id"]]["via"].append(f)
    print(f"\n=== FOR YOU (loves {', '.join(favs)}) — kings ===")
    for cid, r in sorted(recs.items(), key=lambda x: -x[1]["sim"])[:8]:
        print(f"  {r['sim']:.2f}  {cid}  (via {','.join(r['via'][:2])})")
    print("=== FOR YOU — lowkey indies ===")
    hits = []
    for cid, g, _ in _indies():
        ng = g.get("nearest_greats", [])
        hit = [x for x in ng if x["comedian_id"] in favs]
        if hit:
            ts = g.get("theory_score") or {}
            hits.append({"name": g.get("name"), "via": [x["comedian_id"] for x in hit],
                         "theory": ts.get("theory_score"),
                         "sources": ((g.get("discovery") or {}).get("discovered_from") or [])})
    hits.sort(key=lambda x: -(x["theory"] or 0))
    for h in hits[:10]:
        print(f"  {h['name']}  (like {','.join(h['via'][:2])})"
              f"  theory={h['theory']}  [{','.join(h['sources'][:2])}]")


def spotlight() -> None:
    cands = []
    for cid, g, _ in _indies():
        ts = g.get("theory_score") or {}
        if ts.get("theory_score"):
            cands.append((ts["theory_score"], g))
    cands.sort(reverse=True)
    print("=== SMALL COMIC SPOTLIGHT QUEUE (theory-scored) ===")
    for sc, g in cands[:10]:
        ng = ", ".join(x["comedian_id"] for x in g.get("nearest_greats", [])[:2])
        src = ",".join((g.get("discovery") or {}).get("discovered_from", [])[:2])
        print(f"  {sc:.2f}  {g.get('name')}  (like {ng})  [{src}]")
    # unscored discovery queue
    fresh = [(g.get("name"), g) for _, g, _ in _indies()
             if not (g.get("theory_score") or {}).get("theory_score")]
    if fresh:
        print(f"\n=== UNSCORED DISCOVERY ({len(fresh)} awaiting material) ===")
        for name, g in fresh[:10]:
            src = ",".join((g.get("discovery") or {}).get("discovered_from", [])[:2])
            print(f"  {name}  [{src}]")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-lists", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--match-greats", action="store_true")
    ap.add_argument("--for-you", default="")
    ap.add_argument("--spotlight", action="store_true")
    args = ap.parse_args()
    if args.seed_lists:
        seed_lists()
    if args.score:
        score_cmd()
    if args.match_greats:
        match_greats()
    if args.for_you:
        for_you(args.for_you.split(","))
    if args.spotlight:
        spotlight()
    if not any(vars(args).values()):
        ap.print_help()


if __name__ == "__main__":
    main()
