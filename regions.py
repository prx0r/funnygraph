#!/usr/bin/env python3
"""REGIONS — country tagging + global scene seeding (tier indie unless noted).

Region from bio citizenship first (Wikidata), curated overrides second.
Scenes seeded: india (YouTube-native giants), china (Xiaoguo roster via
their official EN-subtitled YouTube channel), uk-irl panel wave.

YouTube translated captions (?tlang=) make foreign sets analyzable with
the same pipeline — subtitles, not dubs, but the words are what we score.

Usage: python3 regions.py --tag-all      # region field on every graph
       python3 regions.py --seed-global  # india + china indie entries
       python3 regions.py --board        # per-region rankings + census
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"

CITZ_TO_REGION = {
    "united states": "us", "united kingdom": "uk", "ireland": "ireland",
    "canada": "canada", "australia": "australia", "india": "india",
    "south africa": "south-africa", "germany": "germany", "france": "france",
    "netherlands": "netherlands", "new zealand": "new-zealand",
    "nigeria": "nigeria", "brazil": "brazil", "china": "china",
    "malaysia": "malaysia", "singapore": "singapore", "israel": "israel",
}

# curated overrides (stage base, not passport): cid → region
OVERRIDES = {
    # uk/ireland panel + alt wave
    "jimmy-carr": "uk", "sean-lock": "uk", "james-acaster": "uk",
    "stewart-lee": "uk", "dylan-moran": "ireland", "eddie-izzard": "uk",
    "ricky-gervais": "uk", "michael-mcintyre": "uk", "kevin-bridges": "uk",
    "lee-mack": "uk", "jack-whitehall": "uk", "russell-howard": "uk",
    "russell-brand": "uk", "sarah-millican": "uk", "greg-davies": "uk",
    "phil-wang": "uk", "sara-pascoe": "uk", "chloe-petts": "uk",
    "billy-connolly": "uk", "dave-allen": "ireland",
    # canada
    "jim-carrey-era": "canada",
    # australia/nz
    "jim-jefferies": "australia", "hannah-gadsby": "australia",
    "celeste-barber-era": "australia", "urzila-carlson": "new-zealand",
    # south africa
    "trevor-noah": "south-africa",
    # india
    "vir-das": "india", "zakir-khan-era": "india", "kanan-gill-era": "india",
    # germany
    "enissa-amani": "germany",
    # malaysia/singapore
    "ronny-chieng": "malaysia", "kavin-jay": "malaysia",
}

# global scene seeds: new indie entries with discovery context
GLOBAL_SEEDS: dict[str, dict] = {
    # INDIA — YouTube-native giants
    "zakir-khan": {"name": "Zakir Khan", "region": "india",
                   "sources": ["youtube-native", "amazon-prime", "netflix"],
                   "note": "India's biggest stand-up: 960M+ YT views, 6 specials, MSG sellout. Storyteller of a generation."},
    "kanan-gill": {"name": "Kanan Gill", "region": "india",
                   "sources": ["youtube-native", "pretentious-movie-reviews"],
                   "note": "Pretentious Movie Reviews → Keep It Real (Prime) → Netflix Yours Sincerely. Ex-software engineer."},
    "biswa-kalyan-rath": {"name": "Biswa Kalyan Rath", "region": "india",
                          "sources": ["youtube-native", "iit"],
                          "note": "IIT → Oracle → Pretentious Movie Reviews → Biswa Mast Aadmi 8.3. 829k subs."},
    "kenny-sebastian": {"name": "Kenny Sebastian", "region": "india",
                        "sources": ["youtube-native", "musician"],
                        "note": "Music + standup, #KennySingForMe. Middle-class restaurant problems."},
    "rahul-subramanian": {"sources": ["youtube-native"], "region": "india",
                          "note": "Random Chikibum, slow unnatural delivery, middle-class observations."},
    "sorabh-pant": {"sources": ["east-india-comedy"], "region": "india",
                    "note": "East India Comedy founder, 250+ shows, Vir Das opener lineage."},
    # CHINA — Xiaoguo roster (EN-subtitled YT channel UCfEpdNBbHUMwqk_ffAdHNVg)
    "pang-bo": {"name": "Pang Bo", "region": "china",
                "sources": ["xiaoguo", "rock-and-roast-s1-champion"],
                "note": "Rock & Roast S1 champion. Programmer-turned-comic, tech-life material."},
    "yang-li": {"name": "Yang Li", "region": "china",
                "sources": ["xiaoguo", "viral-feminist"],
                "note": "'Average yet confident men' routine went viral (2.15M Weibo followers), ignited feminist debate."},
    "li-xueqin": {"name": "Li Xueqin", "region": "china",
                  "sources": ["xiaoguo", "s3-standout"],
                  "note": "Relatable loser persona, S3 standout. Writer-comic."},
    "zhou-qimo": {"name": "Zhou Qimo", "region": "china",
                  "sources": ["xiaoguo", "multi-season-winner"],
                  "note": "Multiple-season winner, craft-first technician."},
    "niao-niao": {"name": "Niao Niao", "region": "china",
                  "sources": ["xiaoguo"],
                  "note": "Social-phobia + body-shame material, young women's experiences. BDD set 22K views EN-subtitled."},
    "he-guangzhi": {"name": "He Guangzhi", "region": "china",
                    "sources": ["xiaoguo"], "note": "Xiaoguo sensation, interview series on EN channel."},
    "qiu-rui": {"name": "Qiu Rui", "region": "china",
                "sources": ["xiaoguo"], "note": "'Worst Boss in the World' set, EN-subtitled."},
}


def tag_all() -> None:
    n_auto = n_over = 0
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        if d.name in EXCLUDED:
            continue
        j = json.loads(g.read_text())
        region = None
        citz = ((j.get("bio") or {}).get("citizenship") or "").lower()
        for k, v in CITZ_TO_REGION.items():
            if k in citz:
                region = v
                break
        if d.name in OVERRIDES:
            region = OVERRIDES[d.name]
            n_over += 1
        elif region:
            n_auto += 1
        if region:
            j["region"] = region
            g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
    print(f"tagged: {n_auto} from bio, {n_over} overrides")


def seed_global() -> None:
    n = 0
    for cid, s in GLOBAL_SEEDS.items():
        d = COMEDIANS / cid
        d.mkdir(exist_ok=True)
        gpath = d / "comedian-graph.json"
        if gpath.exists():
            g = json.loads(gpath.read_text())
        else:
            g = {"schema": "pogtown.comedian.v1", "comedian_id": cid,
                 "name": s.get("name") or " ".join(w.capitalize() for w in cid.split("-")),
                 "tier": "indie", "version": 1, "created": "2026-10-17",
                 "annotator": "regions.py",
                 "identity": {"deal": "", "premise": "", "archetype": "indie_draft",
                              "awareness": "unknown", "awareness_note": "",
                              "philosophy": {}, "dramatic_core": {},
                              "misinterpretation_rule": "", "contradictions": [],
                              "status_model": {}, "expression": {}, "modulator_range": [],
                              "profile": {}, "operator_priors": {},
                              "preferred_theories": [], "threads": [], "problem_space": []},
                 "sets": [], "essay_seeds": [],
                 "provenance": {"tier": "indie"}}
        g["tier"] = "indie"
        g["region"] = s["region"]
        g["discovery"] = {"discovered_from": s["sources"], "discovery_note": s["note"]}
        gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
        n += 1
    # register Xiaoguo channel
    reg_path = HERE / "data" / "channels.json"
    reg = json.loads(reg_path.read_text())
    if "UCfEpdNBbHUMwqk_ffAdHNVg" not in reg.get("xiaoguo", []):
        reg["xiaoguo"] = ["UCfEpdNBbHUMwqk_ffAdHNVg"]
        reg_path.write_text(json.dumps(reg, indent=1) + "\n")
    print(f"seeded {n} global indies + xiaoguo channel")


def board() -> None:
    from collections import Counter
    c = Counter()
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        if d.name in EXCLUDED:
            continue
        try:
            r = json.loads(g.read_text()).get("region", "?")
        except json.JSONDecodeError:
            r = "?"
        c[r] += 1
    print("=== REGION CENSUS ===")
    for r, n in c.most_common():
        print(f"  {r:15} {n}")


def countries() -> None:
    """Top comedians per country (us/uk/ca/au/nz): kings by house + local indies.

    Country pages need both canon and discovery: established kings ranked
    by house percentile, plus the best local indies by headline (rising
    locals). Regions come from graphs (origin/scene tags); thin countries
    show thin boards with the badge, never padded.
    Output: rankings/by_country.json.
    """
    house = {r["comedian_id"]: r for r in
             json.loads((HERE / "rankings" / "house.json").read_text())["rows"]}
    ratings = {r["comedian_id"]: r for r in
               json.loads((HERE / "rankings" / "ratings.json").read_text())["rows"]}
    targets = {"us": "United States", "uk": "United Kingdom",
               "canada": "Canada", "australia": "Australia",
               "new-zealand": "New Zealand"}
    out = {}
    for code, label in targets.items():
        kings, indies = [], []
        for d in sorted(COMEDIANS.iterdir()):
            g = d / "comedian-graph.json"
            if not g.exists() or d.name in EXCLUDED:
                continue
            try:
                j = json.loads(g.read_text())
            except json.JSONDecodeError:
                continue
            r = j.get("region")
            r = r if isinstance(r, str) else (r or {}).get("id", "")
            if r != code:
                continue
            row = {"comedian_id": d.name, "name": j.get("name", d.name)}
            if j.get("tier", "king") == "king" and d.name in house:
                h = house[d.name]
                row.update({"house": h["house"], "house_pct": h["house_pct"],
                            "rank": h["rank"], "coverage": h["coverage"]})
                kings.append(row)
            elif j.get("tier") == "indie":
                rt = ratings.get(d.name, {})
                row.update({"headline": rt.get("headline"),
                            "provisional": rt.get("provisional")})
                indies.append(row)
        kings.sort(key=lambda r: -r["house"])
        indies.sort(key=lambda r: -(r["headline"] or -1))
        out[code] = {"label": label, "n_kings": len(kings),
                     "n_indies": len(indies),
                     "thin": len(kings) < 5,
                     "kings": kings[:15], "rising": indies[:10]}
    (HERE / "rankings" / "by_country.json").write_text(json.dumps(out, indent=1))
    for code, v in out.items():
        top = v["kings"][0]["name"] if v["kings"] else "—"
        print(f"  {code:12} {len(v['kings']):>3} kings, {len(v['rising']):>3} indies "
              f"{'(THIN)' if v['thin'] else ''} #1 {top}")
    print("saved rankings/by_country.json")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag-all", action="store_true")
    ap.add_argument("--seed-global", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--countries", action="store_true")
    args = ap.parse_args()
    if args.tag_all:
        tag_all()
    if args.seed_global:
        seed_global()
    if args.board:
        board()
    if args.countries:
        countries()
    if not any(vars(args).values()):
        ap.print_help()


if __name__ == "__main__":
    main()
