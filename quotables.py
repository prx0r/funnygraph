#!/usr/bin/env python3
"""QUOTABLES — F3 quote-backs: what fans repeat is what they remember.

A bit nobody quotes is a bit nobody remembers. This mines pulse comment
dumps for repeated phrases per comedian: candidate quote-backs of actual
material (quoted text scored highest), with multi-author gates so one
spammer can't mint a quotable. Also aggregates timestamp-laughs and
GOAT-calls per comic (F4/F5 inputs).

Inputs: rankings/pulse/comments-*.json (pulse.py --mine-comments).
Output: fanbase/quotables.json {comedian: {phrases[], timestamp_laughs,
  goat_calls, n_comments}}. Reads only.

Rules: phrase = 4-9 words, >=2 distinct authors, quoted spans ("...")
score double. Pure sentiment ("so funny", "the goat") excluded — that's
praise, not material. Punctuation/case normalized; emoji stripped.
"""
from __future__ import annotations

import glob
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "fanbase"
OUT.mkdir(exist_ok=True)

PRAISE = set("so very really such much funny funnier funniest hilarious amazing incredible best greatest love loved awesome brilliant legend goat iconic classic perfect gold awesome one most ever time all time literally actually just really quite pretty great good bad watch watching video clip special show set joke jokes part scene man guy girl dude bro lol lmao haha favorite favourite fav".split())


def normalize(t: str) -> str:
    t = t.lower()
    t = re.sub(r"http\S+|@[A-Za-z0-9_.]+|#[A-Za-z0-9_]+", " ", t)
    t = re.sub(r"[\U0001F000-\U0001FAFF☀-➿⬅-⬏]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def phrases_of(text: str) -> list[tuple[str, bool]]:
    """(phrase, is_quoted) for 4-9 word windows + explicit quotes."""
    out = []
    for m in re.finditer(r'"([^"]{15,120})"', text):
        ws = m.group(1).split()
        if 4 <= len(ws) <= 9:
            out.append((" ".join(ws).lower(), True))
    words = re.findall(r"[a-z']+", text.lower())
    for n in (4, 5, 6, 7, 8, 9):
        for i in range(len(words) - n + 1):
            w = words[i:i + n]
            if sum(1 for x in w if x in PRAISE) > n // 2:
                continue
            out.append((" ".join(w), False))
    return out


def main() -> None:
    files = sorted(glob.glob(str(HERE / "rankings" / "pulse" / "comments-*.json")))
    if not files:
        raise SystemExit("no comment dumps (run pulse.py --mine-comments)")
    per: dict[str, dict] = defaultdict(lambda: {
        "phrases": defaultdict(lambda: {"n": 0, "authors": set(), "quoted": 0}),
        "timestamp_laughs": 0, "goat_calls": 0, "n_comments": 0})
    for fp in files:
        for v in json.loads(Path(fp).read_text()):
            comic = v.get("comedian") or v.get("comedian_id") or "?"
            r = per[comic]
            for c in v.get("comments", []):
                r["n_comments"] += 1
                if c.get("has_timestamp"):
                    r["timestamp_laughs"] += 1
                if c.get("goat_call"):
                    r["goat_calls"] += 1
                text = normalize(c.get("text", ""))
                if len(text) < 20:
                    continue
                seen = set()
                for ph, q in phrases_of(text):
                    if ph in seen:
                        continue
                    seen.add(ph)
                    e = r["phrases"][ph]
                    e["n"] += 1
                    if c.get("author"):
                        e["authors"].add(c["author"])
                    if q:
                        e["quoted"] += 1
    out = {}
    for comic, r in sorted(per.items()):
        quotes = []
        for ph, e in r["phrases"].items():
            na = len(e["authors"])
            if ("one of the" in ph or "one of a" in ph
                    or "one of my" in ph or "one of his" in ph
                    or "one of her" in ph or "one of our" in ph):
                continue
            if na < 2:
                continue  # quotability = repetition across voices;
                          # solo quotes (even "...") are one fan talking
            score = e["n"] + e["quoted"] * 2 + na
            quotes.append({"phrase": ph, "n": e["n"], "authors": na,
                           "quoted": e["quoted"], "score": score})
        quotes.sort(key=lambda q: -q["score"])
        out[comic] = {
            "n_comments": r["n_comments"],
            "timestamp_laughs": r["timestamp_laughs"],
            "goat_calls": r["goat_calls"],
            "quotables": quotes[:15],
        }
    (OUT / "quotables.json").write_text(json.dumps(out, indent=1))
    print(f"quotables: {len(out)} comics")
    for comic, r in sorted(out.items(), key=lambda kv: -len(kv[1]["quotables"]))[:8]:
        top = r["quotables"][0]["phrase"] if r["quotables"] else "—"
        print(f"  {comic[:20]:20} {len(r['quotables']):>2} phrases "
              f"ts={r['timestamp_laughs']:<3} goat={r['goat_calls']:<2} e.g. {top[:60]}")


ENDORSE = re.compile(r"\b(goat|greatest|best ever|genius|masterpiece|legend|national treasure|king|queen)\b", re.I)


def seed_bits(min_authors: int = 3) -> None:
    """Fan-quoted fragments -> known_bits (measured, never authored).

    A phrase repeated by N distinct fans across videos IS bit evidence:
    somebody's material survived transmission. Endorsements
    ("national treasure") skip — fandom, not material. Entries carry
    author counts + theory tag quote_back (the F3 mechanism code), status
    measured-fanquoted. Append-only, title-deduped.
    """
    from pathlib import Path as _P
    q = json.loads((_P(__file__).parent / "fanbase" / "quotables.json").read_text())
    slug_of = {}
    for d in (_P(__file__).parent / "comedians").iterdir():
        g = d / "comedian-graph.json"
        if not g.exists():
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        slug_of[(j.get("name") or d.name).lower()] = d.name
    n = 0
    for comic, r in q.items():
        slug = slug_of.get(comic.lower())
        if not slug:
            continue
        gpath = _P(__file__).parent / "comedians" / slug / "comedian-graph.json"
        g = json.loads(gpath.read_text())
        have = {(b.get("title") or "").lower() for b in g.get("known_bits", [])}
        # longest-first: overlapping windows collapse to the fullest quote
        for qu in sorted(r.get("quotables", []),
                         key=lambda q: (-len(q["phrase"]), -q["score"])):
            if qu["authors"] < min_authors or ENDORSE.search(qu["phrase"]):
                continue
            title = qu["phrase"][:80]
            tl = title.lower()
            if tl in have:
                continue
            # overlapping windows of one quote: keep the longest only
            if any(tl in h or h in tl for h in have):
                continue
            have.add(tl)
            g.setdefault("known_bits", []).append({
                "title": title,
                "why_it_works": f"Quoted back by {qu['authors']} distinct fans "
                                f"({qu['n']} occurrences): transmitted material — "
                                f"survived the audience-to-comment journey intact.",
                "theory_links": ["quote_back"],
                "source": "F3 fanbase mining",
                "status": "measured-fanquoted"})
            have.add(title.lower())
            n += 1
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
    print(f"seeded {n} fan-quoted bits (min {min_authors} authors)")


if __name__ == "__main__":
    import sys as _sys
    if "--seed" in _sys.argv:
        seed_bits()
    else:
        main()
