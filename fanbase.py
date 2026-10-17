#!/usr/bin/env python3
"""FANBASE — F1 fingerprints, F2 overlap graph, F6 learned lexicon.

Reads rankings/pulse/comments-*.json (with author hashes).
Outputs fanbase/{cid}.json, fanbase/overlap.json, fanbase/lexicon.json.

Usage: python3 fanbase.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
PULSE = HERE / "rankings" / "pulse"
OUT = HERE / "fanbase"
OUT.mkdir(exist_ok=True)

STOP = set("""the a an and or of to in on for with is are was were be been have has had
do does did i you he she it we they not no yes so if as at by from but that this
what which who when where why how all any just like know right yeah oh really going
get got one two would could should im ive dont doesnt wasnt didnt its thats theres
hes shes youre were gonna wanna gotta this that with from they them then than
there here when what much more most very can will just about into over after
before there here they them his her our your its my me him us we our video man
lol lmao haha hahaha bro dude man guy really very so just like know think got
get one get got going go see saw look watch watched show special stand comedy
comedian funny hilarious laugh laughing joke jokes bit set minute minutes part""".split())

EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")

LAUGH_MARKERS = {"😂", "🤣", "💀", "lol", "lmao", "hahaha", "dead", "killed me",
                 "crying", "wheezing", "rewatch", "rewatching"}


def load_comments() -> list[dict]:
    out = []
    for p in sorted(PULSE.glob("comments-*.json")):
        try:
            for m in json.loads(p.read_text()):
                for c in m.get("comments", []):
                    out.append({**c, "videoId": m.get("videoId"),
                                "comedian": m.get("comedian"),
                                "comedian_id": m.get("comedian_id",
                                                     (m.get("comedian") or "").lower().replace(" ", "-")),
                                "title": m.get("title", "")})
        except (OSError, json.JSONDecodeError):
            continue
    return out


def fingerprint(comments: list[dict]) -> dict:
    words: Counter = Counter()
    emojis: Counter = Counter()
    for c in comments:
        toks = re.findall(r"[a-z']+", (c.get("text") or "").lower())
        words.update(t for t in toks if t not in STOP and len(t) > 2)
        emojis.update(EMOJI_RE.findall(c.get("text") or ""))
    n = len(comments)
    laughs = sum(1 for c in comments
                 if any(m in (c.get("text") or "").lower() for m in LAUGH_MARKERS))
    return {
        "n_comments": n,
        "distinctive_words": [w for w, _ in words.most_common(15)],
        "top_emoji": [e for e, _ in emojis.most_common(8)],
        "laugh_rate": round(laughs / max(1, n), 3),
        "timestamp_rate": round(sum(1 for c in comments if c.get("has_timestamp")) / max(1, n), 3),
        "goat_rate": round(sum(1 for c in comments if c.get("goat_call")) / max(1, n), 3),
        "avg_sentiment": round(sum(c.get("sentiment", 0) for c in comments) / max(1, n), 3),
        "avg_length": round(sum(len((c.get("text") or "").split()) for c in comments) / max(1, n), 1),
    }


def main() -> None:
    comments = load_comments()
    print(f"{len(comments)} comments loaded")
    if not comments:
        print("run pulse.py --mine-comments first")
        return

    # ── F1: per-comedian fingerprints ──
    by_comic: dict = defaultdict(list)
    for c in comments:
        by_comic[c.get("comedian_id") or c.get("comedian")].append(c)
    for cid, cs in sorted(by_comic.items()):
        fp = fingerprint(cs)
        fp["comedian"] = cs[0].get("comedian")
        fp["comedian_id"] = cid
        (OUT / f"{cid}.json").write_text(json.dumps(fp, indent=1))
    print(f"F1: {len(by_comic)} fanbase fingerprints")

    # ── F2: overlap graph (shared commenters) ──
    # Exclude videos attributed to 2+ comedians (collabs share an audience
    # by construction — that's not fanbase overlap, that's one room).
    from collections import defaultdict as _dd
    _by_vid: dict = _dd(set)
    for c in comments:
        _by_vid[c.get("videoId")].add(c.get("comedian_id") or c.get("comedian"))
    _multi = {v for v, cs in _by_vid.items() if len(cs) > 1}
    authors: dict = defaultdict(set)
    for c in comments:
        a = c.get("author")
        if a and c.get("videoId") not in _multi:
            authors[c.get("comedian_id") or c.get("comedian")].add(a)

    cids = sorted(authors)
    overlap = []
    for i in range(len(cids)):
        for k in range(i + 1, len(cids)):
            a, b = authors[cids[i]], authors[cids[k]]
            if not a or not b:
                continue
            inter = len(a & b)
            if inter == 0:
                continue
            union = len(a | b)
            overlap.append({
                "a": cids[i], "b": cids[k],
                "shared": inter,
                "jaccard": round(inter / union, 4),
            })
    overlap.sort(key=lambda o: -o["shared"])
    (OUT / "overlap.json").write_text(json.dumps(overlap[:100], indent=1))
    print(f"F2: {len(overlap)} comedian pairs share commenters")
    for o in overlap[:10]:
        print(f"   {o['a'][:20]:20} × {o['b'][:20]:20} shared={o['shared']} j={o['jaccard']}")

    # ── F6: learned lexicon seed (words overrepresented in GOAT/timestamp comments) ──
    pos_words: Counter = Counter()
    all_words: Counter = Counter()
    for c in comments:
        toks = [t for t in re.findall(r"[a-z']+", (c.get("text") or "").lower())
                if t not in STOP and len(t) > 2]
        all_words.update(toks)
        if c.get("goat_call") or c.get("has_timestamp"):
            pos_words.update(toks)
    lex = []
    n_pos = sum(pos_words.values()) or 1
    n_all = sum(all_words.values()) or 1
    for w, cnt in pos_words.most_common(200):
        if cnt < 2:
            continue
        lift = (cnt / n_pos) / ((all_words[w] + 0.5) / (n_all + 0.5 * len(all_words)))
        if lift > 1.5:
            lex.append({"word": w, "lift": round(lift, 2), "count": cnt})
    lex.sort(key=lambda x: -x["lift"])
    (OUT / "lexicon.json").write_text(json.dumps(lex[:60], indent=1))
    print(f"F6: {len(lex)} learned positive markers")
    print("   top:", ", ".join(x["word"] for x in lex[:12]))


if __name__ == "__main__":
    main()
