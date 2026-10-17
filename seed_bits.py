#!/usr/bin/env python3
"""SEED BITS — press-described bits -> hypothesis-flagged known_bits.

known_bits need title + why-it-works + theory_links. NO verbatim material
is required (or used): every entry below is scaffolded from a bit the
press verifiably describes (Timeout/Vulture/Deadline/GOLD bodies,
2025-2026), each carrying its source + hypothesis flag. Graphs are
hypothesis until measured — these entries obey that contract explicitly.

RULES (do not loosen):
  - described bit (press narrates the joke/premise) -> full entry.
  - premise-in-title only (Edinburgh show titles) -> minimal scaffold,
    flagged premise-inferred, thin by design.
  - no description, no entry. Titles alone without premise content skip.
  - never overwrite existing known_bits; append only.

Usage: python3 seed_bits.py
Writes: known_bits[] per listed graph. Reads/writes graphs only.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"

BITS: dict[str, list[dict]] = {
 "maddie-wiener": [
  {"title": "Body positivity, inverted",
   "why": "Takes the body-positivity script literally and past its limit ('let people be ugly'): rigidify — applies the moral logic as law until it breaks. Teenage-philosopher delivery sells the sincerity the joke needs. (Time Out 2026; hypothesis)",
   "theories": ["rigidify", "benign_violation"], "source": "timeout-2026"},
  {"title": "Lazy they/them",
   "why": "Gender-identity premise defused by pure inertia ('more lazy than trans'): the violation (identity confession) lands benign through self-deprecation, never polemic. (Time Out 2026; hypothesis)",
   "theories": ["benign_violation", "expose_self_blindness"], "source": "timeout-2026"},
 ],
 "max-higgins": [
  {"title": "Breakup-to-transition timing",
   "why": "Asks the audience to calibrate grief against becoming ('how soon after a breakup is too soon to transition'): juxtapose of two life events at mismatched scales; observational precision from the English-major eye. (Time Out 2026; hypothesis)",
   "theories": ["juxtapose", "double_interpret"], "source": "timeout-2026"},
 ],
 "jessie-lee": [
  {"title": "Sharon and the impressions",
   "why": "Middle-aged Sharon + Coolidge/Spears/Harris rotations on one line ('you shaved your bush'): character_violation through rapid mask-switching; the line stays fixed while the person doesn't. (Time Out 2026; hypothesis)",
   "theories": ["character_violation", "repeat_variation"], "source": "timeout-2026"},
 ],
 "sam-rocha": [
  {"title": "Anxiety made literal",
   "why": "Carry-on bomb panic, DMV trans ID with Rock Johnson's photo, astronaut-wife film logic: takes intrusive thoughts staging-ready (literalize) and plays them dead straight. (Time Out 2026; hypothesis)",
   "theories": ["literalize", "split_knowledge"], "source": "timeout-2026"},
 ],
 "victoria-vincent": [
  {"title": "Deadpan dread",
   "why": "Boss beefs, surgeon-dad fortune, Good Charlotte fanfic to 27: dreadful material delivered flat — the gap between content horror and affect calm IS the joke (status_invert of the confessional). (Time Out 2026; hypothesis)",
   "theories": ["status_invert", "benign_violation"], "source": "timeout-2026"},
 ],
 "richard-perez": [
  {"title": "Crowdwork without hostages",
   "why": "Interactive bits engineered so the audience never has to be funny: inverts the crowdwork power dynamic (the comic carries the risk), pantomimed vignettes literalize stories into silent film. (Time Out 2026; hypothesis)",
   "theories": ["status_invert", "literalize"], "source": "timeout-2026"},
 ],
 "bo-johnson": [
  {"title": "Closer performed by his father",
   "why": "Debut hour ends with his father performing a joke: status_reversal (the act hands the stage to its source) + genuine sentiment as misdirection — the room laughs, then feels. (Deadline 2026; hypothesis)",
   "theories": ["status_reversal", "benign_violation"], "source": "deadline-2026"},
 ],
 "brent-weinbach": [
  {"title": "Key-change Christmas",
   "why": "Plays Christmas songs in minor keys until they become melancholic Hanukkah songs: literalize applied to music theory; the joke is a proof. Absurdist precision, Fielder-adjacent. (Deadline 2026; hypothesis)",
   "theories": ["literalize", "rigidify"], "source": "deadline-2026"},
 ],
 "tanael-joachim": [
  {"title": "Polyglot set (English/French/Creole)",
   "why": "Learned English from Carlin specials; performs across three languages: the outsider earns insider status joke by joke — split_knowledge where the audience supplies half the translations. (Deadline 2026; hypothesis)",
   "theories": ["split_knowledge", "status_invert"], "source": "deadline-2026"},
 ],
 "orion-levine": [
  {"title": "Read the Room (tarot crowdwork)",
   "why": "Tarot reader + crowdwork Q&A: outsources the premise to the audience's own burning questions, then riffs the answers — repeat_variation on strangers' lives. Format IS the bit. (Deadline 2026; hypothesis)",
   "theories": ["repeat_variation", "split_knowledge"], "source": "deadline-2026"},
 ],
 "brittany-schmitt": [
  {"title": "Specificity as voice (sobriety, womanhood)",
   "why": "Sobriety/relationships/sexuality material works through hyper-specificity: the more exact the detail, the more universal the recognition — specificity as benign_violation engine. (Deadline 2026; hypothesis)",
   "theories": ["benign_violation", "expose_self_blindness"], "source": "deadline-2026"},
 ],
 "usama-siddiquee": [
  {"title": "Kicked off AGT / Muslim in Texas",
   "why": "Growing-up-Muslim-in-Texas premises + the getting-kicked-off-TV story: identity_contradict played warm — the contradiction (belonging vs otherness) resolves through charm, not argument. (Deadline 2026; hypothesis)",
   "theories": ["identity_contradict", "benign_violation"], "source": "deadline-2026"},
 ],
 "jenny-tian": [
  {"title": "Internet-fame immigrant tale",
   "why": "Multimedia hours narrating TikTok fame + Chinese-Australian shuttling: the medium documents the message — fame story told in the fame format (form-content collapse). (Deadline 2026; hypothesis)",
   "theories": ["double_interpret", "status_invert"], "source": "deadline-2026"},
 ],
 "jay-jurden": [
  {"title": "Yes Ma'am (Black, Southern, queer love letter)",
   "why": "Punchline-dense hour where three identity frames collide per premise: juxtapose at speed — the density IS the style, love letter as misdirection for precision. (Deadline 2026; hypothesis)",
   "theories": ["juxtapose", "identity_contradict"], "source": "deadline-2026"},
 ],
 "leah-rudick": [
  {"title": "Wealthy Woman / Joannie / Love Coach",
   "why": "Recurring grotesques (wealthy woman, Joannie, love coach): character_violation through commitment — each figure is a complete status system, and she never breaks it. (Deadline/GOLD 2026; hypothesis)",
   "theories": ["character_violation", "status_invert"], "source": "deadline-2026"},
 ],
 "vittorio-angelone": [
  {"title": "Translations (Fringe hour)",
   "why": "Show built on mistranslation (Belfast ear, classical-musician precision): double_interpret as autobiography — every premise arrives in two languages at once. (Deadline 2026; premise-inferred hypothesis)",
   "theories": ["double_interpret", "false_analogy"], "source": "deadline-2026"},
 ],
 "rahkie-mateen": [
  {"title": "Unapologetically Rocky (vulnerability set)",
   "why": "Solo show converting vulnerability to power on stage: expose_self_blindness as method — the wound is the premise, the scar is the punchline. (GOLD 2026; premise-inferred hypothesis)",
   "theories": ["expose_self_blindness", "status_reversal"], "source": "gold-2026"},
 ],
 "charlene-kaye": [
  {"title": "Tiger Daughter (solo show)",
   "why": "Tiger-daughter premise as full-hour vehicle: rigidify the upbringing logic, then live inside it — autobiography with the volume stuck. (GOLD 2026; premise-inferred hypothesis)",
   "theories": ["rigidify", "expose_self_blindness"], "source": "gold-2026"},
 ],
 "laura-ramoso": [
  {"title": "Hyper-specific cultural impressions",
   "why": "Cross-border impressions pitched at maximum specificity: mistake_identity played lovingly — the audience recognizes themselves inside the exaggeration. (GOLD 2026; hypothesis)",
   "theories": ["mistake_identity", "benign_violation"], "source": "gold-2026"},
 ],
 "elouise-eftos": [
  {"title": "Australia's First Attractive Comedian",
   "why": "Title-as-premise: national self-image vs the claim — status_invert where the boast is the setup and Australianness is the punchline. (Edinburgh 2025; premise-inferred hypothesis)",
   "theories": ["status_invert", "identity_contradict"], "source": "edinburgh-2025-newcomer"},
 ],
 "kate-owens": [
  {"title": "Cooking with Kathryn",
   "why": "Domestic-instruction format housing standup: juxtapose of recipe logic with life logic — the dish is the misdirection. (Edinburgh 2025; premise-inferred hypothesis)",
   "theories": ["juxtapose", "literalize"], "source": "edinburgh-2025-newcomer"},
 ],
 "toussaint-douglass": [
  {"title": "Accessible Pigeon Material",
   "why": "Pigeons as universal-lowbrow subject treated with high-effort craft: status_invert of the bit itself — prestige form, gutter subject. (Edinburgh 2025; premise-inferred hypothesis)",
   "theories": ["status_invert", "rigidify"], "source": "edinburgh-2025-newcomer"},
 ],
}


def main() -> None:
    n_bits = n_comics = 0
    for slug, bits in sorted(BITS.items()):
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            print(f"  MISS dir: {slug}")
            continue
        g = json.loads(gpath.read_text())
        have = {(b.get("title") or "") for b in g.get("known_bits", [])}
        for b in bits:
            if b["title"] in have:
                continue
            g.setdefault("known_bits", []).append({
                "title": b["title"],
                "why_it_works": b["why"],
                "theory_links": b["theories"],
                "source": b["source"],
                "status": "hypothesis (press-described, unmeasured)"})
            n_bits += 1
        gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
        n_comics += 1
    print(f"seeded {n_bits} bits across {n_comics} comics")


if __name__ == "__main__":
    main()
