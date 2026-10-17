#!/usr/bin/env python3
"""RECOMMEND — 'if you love X you'll like Y' from graph latent space.

TF-IDF + SVD over deals + misinterpretation rules + threads + topics +
humor_type + generation + scene → every comic a vector → cosine neighbors.

No API, no keys, runs offline. Feeds: discovery ("more like this"),
small-channel matching (match indie comics to legends), episode pairing
("the modern ___ is ___").

Usage:
  python3 recommend.py                         # full neighbor map
  python3 recommend.py --for louis-ck          # neighbors of one comic
  python3 recommend.py --for louis-ck --small  # small-channel lookalikes
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
OUT = HERE / "rankings"


def doc_of(j: dict) -> str:
    ident = j.get("identity", {})
    parts = [
        ident.get("deal", ""),
        ident.get("premise", ""),
        ident.get("misinterpretation_rule", ""),
        ident.get("archetype", ""),
        " ".join(ident.get("threads", [])),
        " ".join(ident.get("problem_space", [])),
        " ".join(ident.get("preferred_theories", [])),
        " ".join(b.get("title", "") + " " + b.get("why_it_works", "")
                 for b in j.get("known_bits", [])),
        (j.get("humor_type") or {}).get("primary", ""),
        (j.get("generation") or {}).get("id", ""),
    ]
    return " ".join(p for p in parts if p)


def build():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize

    ids, docs = [], []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        t = doc_of(j)
        if len(t.split()) < 10:
            continue
        ids.append(d.name)
        docs.append(t)
    vec = TfidfVectorizer(max_features=4000, stop_words="english",
                          ngram_range=(1, 2), min_df=2)
    X = vec.fit_transform(docs)
    k = min(60, X.shape[1] - 1, X.shape[0] - 1)
    svd = TruncatedSVD(n_components=max(8, k), random_state=7)
    Z = normalize(svd.fit_transform(X))
    return ids, Z


def neighbors(ids, Z, target: str, n: int = 8, same_gen_only=False,
              gens: dict | None = None):
    import numpy as np
    if target not in ids:
        return []
    i = ids.index(target)
    sims = (Z @ Z[i])
    order = sorted(range(len(ids)),
                   key=lambda k: -sims[k] if k != i else 2)
    out = []
    for k in order:
        if k == i:
            continue
        if same_gen_only and gens and gens.get(ids[k]) != gens.get(target):
            continue
        out.append({"comedian_id": ids[k], "sim": round(float(sims[k]), 3)})
        if len(out) >= n:
            break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--for", dest="target", default="")
    ap.add_argument("--n", type=int, default=8)
    args = ap.parse_args()

    ids, Z = build()
    print(f"latent space: {len(ids)} comics")
    gens = {}
    for cid in ids:
        try:
            j = json.loads((COMEDIANS / cid / "comedian-graph.json").read_text())
            gens[cid] = (j.get("generation") or {}).get("id")
        except (OSError, json.JSONDecodeError):
            pass

    if args.target:
        nb = neighbors(ids, Z, args.target, n=args.n)
        j = json.loads((COMEDIANS / args.target / "comedian-graph.json").read_text())
        print(f"\n=== if you love {j.get('name', args.target)} ===")
        for r in nb:
            try:
                nm = json.loads(
                    (COMEDIANS / r["comedian_id"] / "comedian-graph.json").read_text()
                ).get("name", r["comedian_id"])
            except (OSError, json.JSONDecodeError):
                nm = r["comedian_id"]
            print(f"  {r['sim']:.2f}  {nm} [{gens.get(r['comedian_id'])}]")
        return

    full = {}
    for cid in ids:
        full[cid] = neighbors(ids, Z, cid, n=8)
    (OUT / "neighbors.json").write_text(json.dumps(full, indent=0))
    print(f"saved rankings/neighbors.json ({len(full)} comics)")


if __name__ == "__main__":
    main()
