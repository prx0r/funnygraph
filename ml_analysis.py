#!/usr/bin/env python3
"""ML ANALYSIS — ratings regression + generation gap + fingerprints + theory check.

Four pipelines, zero new collection (all data present):
  M2 ratings regression: operator_priors + generation + transcript features → IMDb.
     Answers what predicts a breakout + Greengross construct test for PAPER.md.
  M6 generation gap: profanity/topics/length/ratings by decade.
     "Comedy got ___er over 50 years" with numbers.
  M4 fingerprints at scale: stylometry per comic from all 404 transcripts.
     Feeds agent harness judge + for-you matching. Writes style{} per graph.
  M5 theory validation: authored operator_priors vs measured transcript features.
     Proves or kills our own theory (honesty loop).

Usage: python3 ml_analysis.py [--only m2|m6|m4|m5]
Output: analysis/ml_*.json + style{} fields + PAPER-ready findings printout.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
TR = HERE / "transcripts"
ANALYSIS = HERE / "analysis"
ANALYSIS.mkdir(exist_ok=True)

PROFANE = {"fuck", "fucking", "shit", "bitch", "ass", "damn", "cunt", "dick",
           "piss", "hell", "bastard", "whore", "slut", "tits", "cock"}
STOP = set("""the a an and or of to in on for with is are was were be been have has had
do does did i you he she it we they not no yes so if as at by from but that this
what which who when where why how all any just like know right yeah oh really going
get got one two would could should im ive dont doesnt wasnt didnt its thats theres
hes shes youre were gonna wanna gotta this that with from they them then than
there here when what much more most very can will just about into over after
before there here they them his her our your its my me him us we our video man
lol lmao haha hahaha bro dude man guy really very so just like know right yeah""".split())


def transcript_text(cid: str) -> str:
    parts = []
    # funnygraph transcripts
    d = TR / cid
    if d.exists():
        for p in sorted(d.glob("*.txt")):
            try:
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
    # characters2 transcripts
    d2 = Path(f"/root/characters2/theory/transcripts/{cid}")
    if d2.exists():
        for p in sorted(d2.glob("*.txt")):
            try:
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
    return "\n".join(parts)


def features_of(text: str) -> dict:
    words = re.findall(r"[a-z']+", text.lower())
    n = len(words) or 1
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.split()]
    ns = len(sents) or 1
    fw = sum(1 for w in words if w in PROFANE)
    q = text.count("?")
    i_rate = sum(1 for w in words if w == "i") / n
    vocab = len(set(words)) / n  # type-token
    avg_len = sum(len(s.split()) for s in sents) / ns
    return {"words": len(words), "profanity_rate": round(fw / n, 4),
            "question_rate": round(q / ns, 3), "i_rate": round(i_rate, 3),
            "vocab_div": round(vocab, 3), "avg_sent_len": round(avg_len, 1)}


def load_kings() -> list[tuple[str, dict]]:
    out = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("tier", "king") != "king":
            continue
        out.append((d.name, j))
    return out


def m4_fingerprints(kings) -> dict:
    """Stylometry per comic → style{} written to graphs."""
    print("=== M4 fingerprints ===")
    fps = {}
    for cid, j in kings:
        text = transcript_text(cid)
        if len(text.split()) < 500:
            continue
        f = features_of(text)
        # distinctive bigrams vs global
        fps[cid] = {"name": j.get("name", cid), **f}
    # distinctive n-grams need global contrast — compute top unigrams per comic
    for cid, fp in fps.items():
        text = transcript_text(cid)
        c = Counter(w for w in re.findall(r"[a-z']+", text.lower())
                    if w not in STOP and len(w) > 3)
        fp["top_words"] = [w for w, _ in c.most_common(12)]
    # write style{} back
    n = 0
    for cid, fp in fps.items():
        g = COMEDIANS / cid / "comedian-graph.json"
        j = json.loads(g.read_text())
        j["style"] = {k: v for k, v in fp.items() if k != "name"}
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        n += 1
    json.dump(fps, open(ANALYSIS / "ml_fingerprints.json", "w"), indent=1)
    print(f"  {n} comics fingerprinted, style{{}} written")
    return fps


def m6_generation_gap(kings, fps: dict) -> None:
    print("=== M6 generation gap ===")
    by_gen: dict = defaultdict(list)
    for cid, j in kings:
        gen = (j.get("generation") or {}).get("id", "?")
        if cid in fps:
            by_gen[gen].append((cid, fps[cid]))
    order = ["pioneers", "seventies", "eighties-boom", "nineties", "aughts",
             "tens", "twenties"]
    rows = []
    for gen in order:
        members = by_gen.get(gen, [])
        if not members:
            continue
        prof = sum(f["profanity_rate"] for _, f in members) / len(members)
        q = sum(f["question_rate"] for _, f in members) / len(members)
        sl = sum(f["avg_sent_len"] for _, f in members) / len(members)
        # ratings for gen
        ratings = []
        for cid, _ in members:
            j = dict(kings)[cid] if isinstance(dict(kings).get(cid), dict) else None
            for _, jj in kings:
                if _ == cid:
                    j = jj
                    break
        rows.append({"generation": gen, "n": len(members),
                     "profanity": round(prof, 4), "questions": round(q, 3),
                     "sent_len": round(sl, 1)})
    json.dump(rows, open(ANALYSIS / "ml_generation_gap.json", "w"), indent=1)
    print("  profanity by decade:")
    for r in rows:
        print(f"    {r['generation']:15} n={r['n']:>2} prof={r['profanity']:.4f} "
              f"q={r['questions']:.2f} sentlen={r['sent_len']:.1f}")


def m2_regression(kings, fps: dict) -> None:
    print("=== M2 breakout regression ===")
    try:
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import cross_val_score
        import numpy as np
    except ImportError:
        print("  sklearn missing")
        return
    X, y, names = [], [], []
    for cid, j in kings:
        sp = j.get("specials_rated") or []
        rated = [s for s in sp if s.get("imdb_rating") and s.get("imdb_votes", 0) >= 200]
        if not rated or cid not in fps:
            continue
        best = max(rated, key=lambda s: s["imdb_rating"])
        ops = ((j.get("identity") or {}).get("operator_priors") or {})
        f = fps[cid]
        gen = (j.get("generation") or {}).get("id", "?")
        gen_idx = {"pioneers": 0, "seventies": 1, "eighties-boom": 2,
                   "nineties": 3, "aughts": 4, "tens": 5, "twenties": 6}.get(gen, 3)
        X.append([ops.get("rigidify", 0.5), ops.get("literalize", 0.5),
                  ops.get("double_interpret", 0.5), ops.get("status_invert", 0.5),
                  ops.get("character_violation", 0.5), f["profanity_rate"] * 100,
                  f["question_rate"], f["vocab_div"], f["i_rate"] * 10,
                  gen_idx, np.log10(best["imdb_votes"])])
        y.append(best["imdb_rating"])
        names.append(cid)
    if len(X) < 15:
        print(f"  only {len(X)} samples — need more rated+transcript overlap")
        return
    X = np.array(X)
    y = np.array(y)
    feats = ["rigidify", "literalize", "double_interp", "status_invert",
             "char_violation", "profanityx100", "questions", "vocab_div",
             "i_ratex10", "generation", "log_votes"]
    model = Ridge(alpha=1.0)
    try:
        r2 = cross_val_score(model, X, y, cv=min(5, len(X) // 3),
                             scoring="r2")
        print(f"  n={len(X)} CV R²={r2.mean():.3f} (±{r2.std():.3f})")
    except Exception as e:
        print(f"  cv fail: {e}")
        return
    model.fit(X, y)
    imp = sorted(zip(feats, model.coef_), key=lambda x: -abs(x[1]))
    print("  feature importances (coef):")
    for f, c in imp:
        print(f"    {f:15} {c:+.3f}")
    json.dump({"n": len(X), "cv_r2": round(float(r2.mean()), 3),
               "importances": {f: round(float(c), 3) for f, c in imp}},
              open(ANALYSIS / "ml_regression.json", "w"), indent=1)


def m5_theory_check(kings, fps: dict) -> None:
    print("=== M5 theory validation ===")
    # authored rigidify vs measured literal-construction proxy:
    # literal proxy = frequency of definitional phrasing ("is a", "means", "called")
    rows = []
    for cid, j in kings:
        if cid not in fps:
            continue
        ops = ((j.get("identity") or {}).get("operator_priors") or {})
        if "rigidify" not in ops:
            continue
        text = transcript_text(cid).lower()
        defin = len(re.findall(r"\b(is a|means|called|defined as|literally)\b", text))
        words = len(text.split()) or 1
        rows.append((ops["rigidify"], defin / words * 1000, cid))
    if len(rows) < 10:
        print(f"  only {len(rows)} with rigidify priors + transcripts")
        return
    try:
        import numpy as np
        r = np.corrcoef([x[0] for x in rows], [x[1] for x in rows])[0, 1]
        print(f"  authored rigidify vs measured definitional-density: r={r:+.3f} (n={len(rows)})")
        print("  " + ("THEORY HOLDS (positive)" if r > 0.2 else
                       "THEORY WEAK/DEAD (near zero or negative)"))
    except ImportError:
        print("  numpy missing")
        return
    json.dump([{"cid": c, "authored_rigidify": a, "measured_per_1k": round(m, 2)}
               for a, m, c in rows],
              open(ANALYSIS / "ml_theory_check.json", "w"), indent=1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else {"m2", "m6", "m4", "m5"}
    kings = load_kings()
    print(f"{len(kings)} kings")
    fps = {}
    if "m4" in only:
        fps = m4_fingerprints(kings)
    else:
        # load cached fingerprints if present
        try:
            fps = {k: v for k, v in
                   json.loads(open(ANALYSIS / "ml_fingerprints.json").read()).items()}
        except (OSError, json.JSONDecodeError):
            pass
    if "m6" in only:
        m6_generation_gap(kings, fps)
    if "m2" in only:
        m2_regression(kings, fps)
    if "m5" in only:
        m5_theory_check(kings, fps)


if __name__ == "__main__":
    main()
