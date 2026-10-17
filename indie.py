#!/usr/bin/env python3
"""INDIE — small-comic lane on the unified schema (tier:"indie").

TIER LINE (owner 2026-10-17): king = established pros with national
credits (TV/film, distributed specials, touring, list presence) — canon
track. indie = literally unknown: own-channel clips, open-mic/club
regulars, regional circuits, debut specials. Mis-tiered KT guests
(Rawlings, Owen, Harland, Yakov, Trussell, Wheeler Walker) flipped to
king on sight; Dry Bar debut comics stay indie until canon evidence.

UNKNOWN-FOUNTAINS (verified, registry IDs): kill-tony bucket minutes,
dry-bar debut specials, just-for-laughs New Faces, xiaoguo, basketmouth.
PENDING owner paste: dont-tell-comedy, frog-and-bucket (Beat the Frog),
angel-comedy (New Act Showcase) — see channels.json _pending_owner_paste.

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
# PRESS COMPILERS (2026-10-17 batch): editors vetted standup-first, zero
# quota, near-zero junk. Deadline-2026 is the gold standard (explicitly
# stand-ups-first, no groups, no SNL-boost, no repeats). Vulture mixes
# sketch/improv/clowns — only confirmed standups admitted (see note).
# Edinburgh Best Newcomer = Fringe-hour standups by construction (duos
# skipped: Ada & Bron). Tier call: club-circuit/debut-hour/first-tour =
# indie even with late-night spots; sustained national presence = king.
PRESS_2026: dict[str, dict] = {
 "vittorio-angelone": {"sources": ["deadline-2026"], "note": "Belfast→London, JFL New Face 2025, 40k tickets Who Do You Think You Are tour"},
 "mary-beth-barone": {"sources": ["deadline-2026"], "note": "Netflix hour Galaxy Brain taping Mar, Pillow Talk club tour"},
 "ryan-davis": {"sources": ["deadline-2026"], "note": "Under-Rated special via Ali Siddiq channel 2.3M views, 30-city club tour"},
 "bo-johnson": {"sources": ["deadline-2026"], "note": "Debut hour Two Sailboats self-released, 333 headlining shows/2yr, DTC sets"},
 "orion-levine": {"sources": ["deadline-2026"], "note": "JFL New Face 2022, DTC set 197k, Read the Room live show"},
 "ismael-loutfi": {"sources": ["deadline-2026"], "note": "CC half hour Sound It Out, 2x DTC sets, JFL New Face 2016"},
 "laura-peek": {"sources": ["deadline-2026"], "note": "JFL New Face 2022, paid regular Comedy Store, 2x DTC Secret Sets"},
 "mike-rice": {"sources": ["deadline-2026"], "note": "Self-released An Irish Disgrace + Nasty Character, Edinburgh sellouts, first world tour 2026"},
 "red-richardson": {"sources": ["deadline-2026"], "note": "Bugatti tour (Store sellouts), DTC set 371k, Gervais orbit"},
 "erica-rhodes": {"sources": ["deadline-2026"], "note": "Call Me Crazy tour -> third special taping; AGT/Colbert spots, still club-breakout: indie"},
 "rachel-scanlon": {"sources": ["deadline-2026"], "note": "Debut hour Gay Fantasy, DTC set, Two Dykes and a Mic theater tour"},
 "brittany-schmitt": {"sources": ["deadline-2026"], "note": "800 Pound Gorilla From Ho to Housewife + Horny, DTC/CC sets, Von/Redd opener"},
 "usama-siddiquee": {"sources": ["deadline-2026"], "note": "First headlining tour wrapped, DTC half hour, Colbert debut 2024"},
 "jenny-tian": {"sources": ["deadline-2026"], "note": "Sydney circuit -> NYC, 2 self-released hours (900k/266k), Edinburgh + West End sellouts"},
 "tanael-joachim": {"name": "TJ", "sources": ["deadline-2026"], "note": "Cellar/Gotham regular, Alien of Ordinary Ability 167k, Carlin-taught English"},
 "aaron-weber": {"sources": ["deadline-2026"], "note": "Nashville/Opry youngest debut, JFL New Face 2021, 800PG Signature Dish 548k"},
 "brent-weinbach": {"sources": ["deadline-2026"], "note": "Alt veteran (Andy Kaufman Award), Popular Culture 2025; no breakout: indie until canon evidence"},
 "ayoade-bamgboye": {"sources": ["edinburgh-2025-newcomer-winner"], "note": "DLT Best Newcomer 2025, Swings and Roundabouts"},
 "elouise-eftos": {"sources": ["edinburgh-2025-newcomer"], "note": "Best Newcomer nominee 2025, Australia's First Attractive Comedian"},
 "kate-owens": {"sources": ["edinburgh-2025-newcomer"], "note": "Best Newcomer nominee 2025, Cooking with Kathryn"},
 "molly-mcguinness": {"sources": ["edinburgh-2025-newcomer"], "note": "Best Newcomer nominee 2025, Slob"},
 "roger-osullivan": {"sources": ["edinburgh-2025-newcomer"], "note": "Best Newcomer nominee 2025, Fekken"},
 "toussaint-douglass": {"sources": ["edinburgh-2025-newcomer"], "note": "Best Newcomer nominee 2025, Accessible Pigeon Material"},
 "marty-gleeson": {"sources": ["edinburgh-2026-newcomer-winner"], "note": "Best Newcomer 2026, Dog Ear"},
 "ania-magliano": {"sources": ["vulture-2026"], "note": "Standup, SNL UK Weekend Update + Taskmaster; confirmed standup, rest of list skipped (mixed disciplines)"},
 "ron-taylor": {"sources": ["vulture-2026"], "note": "Standup, Funny AF winner, decade of rooms before the break"},
 "sureni-weerasekera": {"sources": ["vulture-2026"], "note": "Standup, Netflix Introducing, Brooklyn + college circuit"},
 "liz-glazer": {"sources": ["gold-2026"], "note": "Smart personal standup, Sex-Education-adjacent rule-breaking (GOLD list)"},
 "amber-singletary": {"sources": ["gold-2026"], "note": "Writers-room + growing standup footprint (GOLD list)"},
 "johana-coca": {"sources": ["gold-2026"], "note": "Family/culture personal stories (GOLD list)"},
 "charlene-kaye": {"sources": ["gold-2026"], "note": "Tiger Daughter solo show -> special (GOLD list)"},
 "krishna-istha": {"sources": ["gold-2026"], "note": "Standup + Sex Education writing, genre-breaking (GOLD list)"},
 "mx-dahlia-belle": {"sources": ["gold-2026"], "note": "Gender Agenda + festival sets (GOLD list)"},
 "ella-yurman": {"sources": ["gold-2026"], "note": "All-trans standup show founder + political satire (GOLD list)"},
}
CURATED.update(PRESS_2026)


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
        if g.get("tier") == "king":
            print(f"  keep king: {cid} (press list never demotes)")
            continue
        if meta.get("name"):
            g["name"] = meta["name"]
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
    # funnygraph-local material: harvest_captions scribe + plain transcripts
    fg_scribe = HERE / "scribe"
    for pat in (f"{cid}*.json", f"{cid.replace('-', '_')}*.json"):
        for p in fg_scribe.glob(pat):
            try:
                d = json.loads(p.read_text())
                ws = d.get("words", [])
                if isinstance(ws, list) and ws and isinstance(ws[0], dict):
                    texts.append(" ".join(w.get("text", "") for w in ws))
                elif isinstance(ws, list) and ws and isinstance(ws[0], str):
                    texts.append(" ".join(ws))
            except (OSError, json.JSONDecodeError):
                continue
    fg_tr = HERE / "transcripts" / cid
    if fg_tr.exists():
        for p in sorted(fg_tr.glob("*.txt")):
            try:
                texts.append(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
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


def ops_from_kt() -> None:
    """KT minute judge analyses -> indie operator_priors (measured, not authored).

    characters2 KT minutes carry per-set Jev theory judgments (mechanisms[]
    with p + verdict, primary operator). No text, but structured theory
    evidence per performer — aggregated here into operator priors:
      score(op) = mean over the comic's minutes of p * w,
      w = 1.0 (verdict yes) / 0.5 (uncertain) / 0.0 (no).
    Written to identity.operator_priors with status measured-kt-jezv
    (judge-measured, not transcript-measured — weaker than M4, stronger
    than authored; the status says so). Theories outside our 15 ops kept
    verbatim with the same status (extended evidence, not invented).
    Indies only; kings keep authored/M4 priors.
    """
    ktd = Path("/root/characters2/theory/killtony-minutes")
    if not ktd.exists():
        print("no KT minutes dir")
        return
    from collections import defaultdict
    per: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list))
    n_files = 0
    for p in ktd.glob("*.json"):
        stem = p.stem
        stem = re.sub(r"\.(granular|gemini|performance|stage_timeline).*$", "", stem)
        stem = re.sub(r"_(raw|short|clip)$", "", stem)
        m = re.match(r"^([a-z_]+?)(?:_\d+)?(?:-\d+)?$", stem)
        if not m:
            continue
        slug = m.group(1).replace("_", "-")
        try:
            d = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        docs = d if isinstance(d, list) else [d]
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            mechs = doc.get("mechanisms") or []
            if not isinstance(mechs, list):
                continue
            n_files += 1
            for mc in mechs:
                if not isinstance(mc, dict):
                    continue
                th = mc.get("theory")
                pv = mc.get("p")
                if not th or not isinstance(pv, (int, float)):
                    continue
                w = {"yes": 1.0, "uncertain": 0.5}.get(
                    (mc.get("verdict") or ""), 0.0)
                per[slug][th].append(pv * w)
    print(f"{n_files} KT analyses")
    n = 0
    for slug, ops in sorted(per.items()):
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            continue
        g = json.loads(gpath.read_text())
        if g.get("tier") != "indie":
            continue
        priors = {th: round(sum(v) / len(v), 3)
                  for th, v in ops.items() if v}
        priors = {k: v for k, v in priors.items() if v > 0}
        if not priors:
            continue
        ident = g.setdefault("identity", {})
        ident["operator_priors"] = priors
        ident["operator_priors_status"] = (
            "measured-kt-jezv: judge-aggregated over "
            f"{sum(len(v) for v in ops.values())} mechanism reads "
            f"({len(ops)} ops); judge-measured, not transcript-measured")
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        n += 1
        top = sorted(priors.items(), key=lambda kv: -kv[1])[:3]
        print(f"  {slug}: " + ", ".join(f"{k}={v}" for k, v in top))
    print(f"operator priors set for {n} indies")


def match_greats(top_k: int = 3) -> None:
    import sys as _sys
    _sys.path.insert(0, str(HERE))
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize
    import numpy as _np
    kings = _kings()
    kids, kdocs = [], []
    for cid, j in kings:
        ident = j.get("identity", {})
        t = (ident.get("deal", "") + " " + ident.get("premise", "") + " " +
             ident.get("misinterpretation_rule", "") + " " +
             " ".join(ident.get("threads", [])) + " " +
             " ".join((ident.get("modulator_range") or [])))
        if len(t.split()) >= 5:
            kids.append(cid)
            kdocs.append(t)
    indies = _indies()
    idocs = []
    for cid, g, _ in indies:
        idocs.append(g.get("name", "") + " " +
                     (g.get("discovery") or {}).get("discovery_note", "") + " " +
                     (g.get("identity") or {}).get("deal", ""))
    vec = TfidfVectorizer(max_features=3000, stop_words="english",
                          ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(kdocs + idocs)
    Z = normalize(X.toarray())
    K, I = Z[:len(kids)], Z[len(kids):]
    sims = I @ K.T
    n = 0
    for i, (cid, g, gpath) in enumerate(indies):
        order = sorted(range(len(kids)), key=lambda k: -sims[i, k])[:top_k]
        g["nearest_greats"] = [
            {"comedian_id": kids[k], "sim": round(float(sims[i, k]), 3)}
            for k in order if sims[i, k] > 0.02]
        # style tags: inherit top match's type + theories, flagged inferred.
        # Similarity is resemblance, not measurement — tags carry the sim
        # so readers (and the recommender) can discount weak matches.
        g.pop("style_tags", None)
        if g["nearest_greats"]:
            top = g["nearest_greats"][0]
            kj = dict(kings)[top["comedian_id"]]
            kh = kj.get("humor_type") or {}
            g["style_tags"] = {
                "humor_type": kh.get("primary") if isinstance(kh, dict) else None,
                "theories": ((kj.get("identity") or {}).get("preferred_theories") or [])[:3],
                "via": top["comedian_id"], "sim": top["sim"],
                "method": "inferred-from-nearest-king (resemblance, not measurement)",
            }
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        if g["nearest_greats"]:
            n += 1
    print(f"matched {n}/{len(indies)} indies to kings (latent space)")


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


def compare(cid: str) -> None:
    """Side-by-side: indie vs nearest kings. Units labeled, never blended.

    theory_score (0-1 NoSlop-gate rate) and paper (~0.02 calibrated
    laughter-fitted) and house (0-100) are DIFFERENT rulers — shown
    together for judgment, never averaged. The comparison a booker makes:
    who does this unknown resemble, how strong is the resemblance, and
    does the resemblance have measured jokes behind it.
    """
    sys.path.insert(0, str(HERE))
    gpath = COMEDIANS / cid / "comedian-graph.json"
    if not gpath.exists():
        print(f"unknown: {cid}")
        return
    g = json.loads(gpath.read_text())
    ts = g.get("theory_score") or {}
    st = g.get("style_tags") or {}
    yc = g.get("youtube_channel") or {}
    print(f"=== {g.get('name', cid)} [{g.get('tier')}] "
          f"region={g.get('region', '?')}")
    print(f"  headline={_headline(cid)} coverage=DISCOVERY "
          f"provisional={_prov(cid)}")
    print(f"  theory_score={ts.get('theory_score', '—')} (0-1 gate rate, "
          f"n={ts.get('n_chunks', '—')})" if ts else "  theory_score: unscored (no material)")
    print(f"  style: {st.get('humor_type', '?')} via {st.get('via', '?')} "
          f"sim={st.get('sim', '?')} [{st.get('method', '—')}]" if st else "  style: unmatched")
    print(f"  channel: {yc.get('title', '—')} subs={yc.get('subs', '?')} "
          f"status={yc.get('status', 'unlinked')}")
    print(f"  sources: {','.join((g.get('discovery') or {}).get('discovered_from', []))}")
    try:
        measured = {c["comedian_id"]: c for c in json.loads(
            (HERE / "rankings" / "theory_content.json").read_text())["comics"]}
        ratings = {c["comedian_id"]: c for c in json.loads(
            (HERE / "rankings" / "ratings.json").read_text())["rows"]}
    except (OSError, json.JSONDecodeError, KeyError):
        measured, ratings = {}, {}
    for ng in (g.get("nearest_greats") or [])[:3]:
        k = ng["comedian_id"]
        r = ratings.get(k, {})
        m = measured.get(k, {})
        print(f"  ~= {k} sim={ng['sim']}: house={r.get('headline', '?')} "
              f"paper={m.get('mean_paper', 'unmeasured')} "
              f"n_bits={m.get('n_bits', '—')} "
              f"type={(measured.get(k, {}) or {}).get('humor_type', '?')}")


def _headline(cid: str):
    try:
        rows = json.loads((HERE / "rankings" / "ratings.json").read_text())["rows"]
        return next(r["headline"] for r in rows if r["comedian_id"] == cid)
    except (OSError, json.JSONDecodeError, StopIteration, KeyError):
        return None


def _prov(cid: str):
    try:
        rows = json.loads((HERE / "rankings" / "ratings.json").read_text())["rows"]
        return next(r["provisional"] for r in rows if r["comedian_id"] == cid)
    except (OSError, json.JSONDecodeError, StopIteration, KeyError):
        return None


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
    ap.add_argument("--compare", default="")
    ap.add_argument("--ops", action="store_true")
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
    if args.compare:
        compare(args.compare)
    if args.ops:
        ops_from_kt()
    if not any(vars(args).values()):
        ap.print_help()


if __name__ == "__main__":
    main()
