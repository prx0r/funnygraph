#!/usr/bin/env python3
"""RATE — the canonical rating pipeline. Every profile rated, by default.

One command rates every comedian and rebuilds every board. New graphs are
picked up automatically: zero-leg newcomers get an HONEST provisional
rating (neighbor-inferred, flagged, never blended silently) instead of a
meaningless bottom rank.

  python3 rate.py              # full rebuild: boards + ratings + validation
  python3 rate.py --fast       # boards + ratings only (skip validation)
  python3 rate.py --check      # rebuild only if graphs changed (cron-safe)
  python3 rate.py --watch 300  # daemon: --check every N seconds

DESIGN (why this file exists):
  Before: 9 scripts, run by hand, in an order kept in a human's head.
  After: one entry point, fixed stage order, change detection, run log.
  rate.py never fetches (no keys, no quota, no network): enrich_*.py and
  harvest scripts collect; rate.py is pure from graphs. A newcomer with no
  legs still gets rated — provisionally, with the method stated.

CANONICAL RATING (per profile, embedded as graph["rating"] + ratings.json):
  headline 0-100  = HOUSE percentile (our proprietary election) when the
                    profile scores on >=1 proprietary leg, else provisional
                    inference (method stated, never silent).
  coverage        = FULL (P1+P2) / PARTIAL (one leg) / UNRANKED (none).
  provisional     = null | neighbor-latent | type-prior | global-prior.
  boards.house    = our rank+pct+interval. boards.consensus/canon/peoples/
                    era = EXTERNAL reference elections, displayed verbatim
                    and labeled — never inputs to the headline.

PROVISIONAL LADDER (cold start, first rung that applies):
  1. neighbor-latent: sim-weighted mean of top-5 neighbors' consensus
     percentiles (neighbors.json latent space; newcomer included on rebuild).
  2. type-prior: median consensus percentile of the newcomer's humor_type.
  3. global-prior: global median. Always flagged provisional + THIN/UNRANKED.

CANONICAL WORKFLOW (the loop this file orchestrates the tail of):
  FIND      discover.py --scan (registry uploads, incremental) +
            press compilers (indie.py CURATED: deadline/vulture/edinburgh/
            gold/timeout lists) + venue rosters (--rosters). Roast-titled
            videos never yield names; full names only; showname junk
            blocklisted; every batch tier-audited (national credits = king).
  LINK      discover.py --link-channels (evidence handles/descriptions) +
            --guess-handles (verified forHandle) + --link-websites
            (Wikidata P856, then verified URL guesses). Our pages drive
            traffic outward; their uploads feed our pulse inward.
  VERIFY    discover.py --audit-channels (active/stale/dormant/variety;
            fountain/collision links unlinked).
  SETS      harvest_captions.py per evidence video (BLOCKED pending owner
            cookies) or harvester --only for linked channels (stats now,
            captions later). indie.py --score gates material on arrival.
  RATE      this file: boards + ratings.json + per-graph rating{}.
  PULSE     pulse.py --snapshot (weekly) + --report -> spotlight.json
            (comedian_of_week, bracket_champs, rising_star,
            new_comic_of_week). Monday cadence; velocity needs 2+ snaps.
  PROMOTE   human flips indie->king on canon evidence (specials, lists,
            sustained touring). Nothing auto-promotes; everything auto-rates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
RANK = HERE / "rankings"
STATE = HERE / ".rate_state.json"
RUNLOG = RANK / "runs.jsonl"
VERSION = "rate/v1"

sys.path.insert(0, str(HERE))
from rank_comedians import load_comics

try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

CORE_STAGES = [
    ("recommend.py", [], True),        # latent space (provisional needs this)
    ("rank_comedians.py", [], True),   # consensus/era/disagreement
    ("mallows_phi.py", [], False),     # precision weights (split needs this)
    ("split_boards.py", [], True),     # canon + peoples
    ("metrics.py", [], True),          # 5-lens panel -> graphs + metrics.json
    ("theory_content.py", [], False),  # needs characters2; warn-skip if absent
    ("house_rank.py", [], True),       # PROPRIETARY board (needs theory+metrics)
    ("regions.py", ["--countries"], True),  # per-country boards (needs house+ratings)
]
VALID_STAGES = [
    ("kendall_w.py", ["--boots", "200"], False),
    ("stability.py", [], False),
    ("bt_leg.py", [], False),
    ("fit_weights.py", [], False),
]


# volatile keys the pipeline itself rewrites (must not trigger rebuilds)
VOLATILE = ("rating", "metrics")


def manifest_hash() -> str:
    h = hashlib.sha256()
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            j = json.loads(g.read_text())
            for k in VOLATILE:
                j.pop(k, None)
            blob = json.dumps(j, sort_keys=True).encode()
        except (OSError, json.JSONDecodeError):
            st = g.stat()
            blob = f"{st.st_size}:{st.st_mtime_ns}".encode()
        h.update(d.name.encode() + b":" + hashlib.sha256(blob).digest())
    h.update(VERSION.encode())
    return h.hexdigest()


def run_stage(script: str, args: list[str], required: bool) -> bool:
    t0 = time.time()
    r = subprocess.run([sys.executable, str(HERE / script), *args],
                       capture_output=True, text=True, timeout=1200)
    dt = round(time.time() - t0, 1)
    ok = r.returncode == 0
    tag = "OK " if ok else ("FAIL" if required else "SKIP")
    last = (r.stdout.strip().splitlines() or [""])[-1][:100]
    err = (r.stderr.strip().splitlines() or [""])[-1][:160] if not ok else ""
    print(f"[{tag}] {script} ({dt}s) {last} {err}")
    return ok


def pct_of(rank: int | None, n: int) -> float | None:
    if not rank:
        return None
    return round(100 * (1 - (rank - 1) / max(1, n)), 1)


def load_board(path: str) -> dict:
    try:
        rows = json.loads((RANK / path).read_text())
        rows = rows.get("rows", rows) if isinstance(rows, dict) else rows
        return {c["comedian_id"]: c for c in rows}
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return {}


def build_ratings() -> tuple[int, int]:
    """Embed rating{} per graph + write ratings.json site table."""
    from kendall_w import compute_legs

    comics = load_comics()  # kings, exclusion-guarded
    # all profiles (any tier) for rating embed
    profiles: dict[str, dict] = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            profiles[d.name] = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue

    legs = compute_legs(comics)  # external legs (coverage context only)
    consensus = load_board("consensus.json")
    canon = load_board("canon.json")
    peoples = load_board("peoples.json")
    era = load_board("era_adjusted.json")
    house = load_board("house.json")  # PROPRIETARY board -> headline
    stability = load_board("stability.json")
    try:
        neighbors = json.loads((RANK / "neighbors.json").read_text())
    except (OSError, json.JSONDecodeError):
        neighbors = {}
    n_cons = len(consensus) or 1

    # type medians (provisional ladder rung 2) — from house pcts
    n_house = len(house) or 1
    type_pcts: dict[str, list[float]] = {}
    for cid, h in house.items():
        ht = (comics[cid].get("humor_type") or {}) if cid in comics else {}
        t = ht.get("primary") if isinstance(ht, dict) else None
        if t and h.get("house_pct") is not None:
            type_pcts.setdefault(t, []).append(h["house_pct"])
    type_med = {t: statistics.median(v) for t, v in type_pcts.items()}
    glob_med = statistics.median(
        [h["house_pct"] for h in house.values()
         if h.get("house_pct") is not None] or [50.0])

    def provisional(cid: str) -> tuple[float, str]:
        nbs = neighbors.get(cid) or []
        scored = [(n["sim"], (house.get(n["comedian_id"]) or {}).get("house_pct"))
                  for n in nbs[:5]]
        scored = [(s, p) for s, p in scored if p is not None]
        if scored:
            w = sum(s for s, _ in scored) or 1
            return (round(sum(s * p for s, p in scored) / w, 1),
                    "neighbor-latent")
        ht = (profiles[cid].get("humor_type") or {})
        t = ht.get("primary") if isinstance(ht, dict) else None
        if t and t in type_med:
            return (round(type_med[t], 1), "type-prior")
        return (round(glob_med, 1), "global-prior")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows, n_prov = [], 0
    for cid, j in sorted(profiles.items()):
        is_king = cid in comics
        n_legs = sum(1 for leg in legs.values()
                     if is_king and leg.get(cid, 0) > 0)
        coverage = ({3: "FULL", 2: "PARTIAL", 1: "THIN"}.get(n_legs,
                                                             "UNRANKED")
                    if is_king else "DISCOVERY")
        prov = None
        h = house.get(cid, {})
        if is_king and h.get("rank"):
            headline = h.get("house_pct")
            coverage = h.get("coverage", "PARTIAL")
            boards = {
                "house": {"rank": h.get("rank"), "pct": headline,
                          "sweep": [h.get("sweep_lo"), h.get("sweep_hi")]},
                "consensus": {"rank": (consensus.get(cid) or {}).get("rank"),
                              "ref": True},
                "canon": {"rank": (canon.get(cid) or {}).get("rank"),
                          "ref": True},
                "peoples": {"rank": (peoples.get(cid) or {}).get("rank"),
                            "wr": (peoples.get(cid) or {}).get("wr"),
                            "ref": True},
                "era": {"rank": (era.get(cid) or {}).get("rank"),
                        "ref": True},
            }
            interval = {"lo": h.get("sweep_lo"), "hi": h.get("sweep_hi")}
        elif is_king:
            # UNRANKED on our legs: no house rank, no interval. Reference
            # elections display verbatim (labeled); headline is provisional.
            headline, prov = provisional(cid)
            n_prov += 1
            coverage = "UNRANKED"
            boards = {
                "house": {"rank": None},
                "consensus": {"rank": (consensus.get(cid) or {}).get("rank"),
                              "ref": True},
                "canon": {"rank": (canon.get(cid) or {}).get("rank"),
                          "ref": True},
                "peoples": {"rank": (peoples.get(cid) or {}).get("rank"),
                            "wr": (peoples.get(cid) or {}).get("wr"),
                            "ref": True},
                "era": {"rank": (era.get(cid) or {}).get("rank"),
                        "ref": True},
            }
            interval = None
        else:
            # indies: discovery track — theory depth when present, else type/global
            th = ((j.get("metrics") or {}).get("theory"))
            if th is not None:
                headline, prov = float(th), "theory-depth"
            else:
                headline, prov = provisional(cid)
            n_prov += 1
            boards = {b: {"rank": None} for b in
                      ("consensus", "canon", "peoples", "era")}
            interval = None
        rating = {
            "headline": headline,
            "coverage": coverage,
            "provisional": prov,
            "boards": boards,
            "interval": interval,
            "updated": now,
            "pipeline": VERSION,
        }
        j["rating"] = rating
        (COMEDIANS / cid / "comedian-graph.json").write_text(
            json.dumps(j, indent=2) + "\n", encoding="utf-8")
        m = (j.get("metrics") or {})
        h = house.get(cid, {})
        rows.append({"comedian_id": cid, "name": j.get("name", cid),
                     "tier": j.get("tier", "king"),
                     "generation": ((j.get("generation") or {}).get("id")),
                     **{k: v for k, v in rating.items() if k != "boards"},
                     "boards": rating["boards"],
                     # FUNNIER = the house percentile: our proprietary rating.
                     # It replaces the theory lens at presentation (theory
                     # depth still feeds P2 and stays in graph metrics).
                     "lenses": {"legacy": m.get("legacy"),
                                "audience": m.get("audience"),
                                "popularity": m.get("popularity"),
                                "funnier": h.get("house_pct"),
                                "heat": m.get("heat"),
                                "gap_value": m.get("gap_value"),
                                "overrated": m.get("overrated"),
                                "canon_lag": m.get("canon_lag")}})
    rows.sort(key=lambda r: (-(r["headline"] or -1), r["name"]))
    (RANK / "ratings.json").write_text(json.dumps({
        "note": "Canonical site table: one row per profile. headline = HOUSE "
                "percentile (proprietary: measured jokes + theory depth) when "
                "scored, else flagged provisional inference (method stated). "
                "boards.house is ours; consensus/canon/peoples/era carry "
                "ref:true — external reference elections, displayed verbatim, "
                "never inputs. Coverage: FULL/PARTIAL (proprietary legs) / "
                "UNRANKED / DISCOVERY (indies).",
        "updated": now, "pipeline": VERSION, "n": len(rows),
        "n_provisional": n_prov,
        "rows": rows,
    }, indent=1))
    print(f"[OK ] ratings: {len(rows)} profiles, {n_prov} provisional -> "
          f"rankings/ratings.json")
    return len(rows), n_prov


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fast", action="store_true",
                    help="boards + ratings only, skip validation")
    ap.add_argument("--check", action="store_true",
                    help="rebuild only if graphs changed since last run")
    ap.add_argument("--watch", type=int, default=0, metavar="SEC",
                    help="daemon: --check every SEC seconds")
    args = ap.parse_args()

    def once() -> bool:
        h = manifest_hash()
        if args.check or args.watch:
            try:
                if json.loads(STATE.read_text()).get("hash") == h:
                    print(f"no changes ({h[:12]}), skipping")
                    return True
            except (OSError, json.JSONDecodeError):
                pass
        t0 = time.time()
        ok = True
        for script, sargs, req in CORE_STAGES:
            if not run_stage(script, sargs, req) and req:
                ok = False
                print(f"ABORT: required stage {script} failed")
                break
        if ok and not args.fast:
            for script, sargs, req in VALID_STAGES:
                run_stage(script, sargs, req)
        n, n_prov = (0, 0)
        if ok:
            try:
                n, n_prov = build_ratings()
            except Exception as e:  # ratings must never break the boards
                print(f"[FAIL] ratings embed: {type(e).__name__}: {e}")
                ok = False
        rec = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "pipeline": VERSION, "hash": h, "ok": ok,
               "profiles": n, "provisional": n_prov,
               "seconds": round(time.time() - t0, 1),
               "fast": args.fast}
        if ok:
            STATE.write_text(json.dumps({"hash": h, **rec}, indent=1))
        with RUNLOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"done ok={ok} profiles={n} provisional={n_prov} "
              f"({rec['seconds']}s) -> {RUNLOG.name}")
        return ok

    if args.watch:
        print(f"watching every {args.watch}s (Ctrl-C to stop)")
        while True:
            once()
            time.sleep(args.watch)
    else:
        sys.exit(0 if once() else 1)


if __name__ == "__main__":
    main()
