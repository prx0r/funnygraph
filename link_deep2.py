#!/usr/bin/env python3
"""LINK + DEEP2 — link HF transcripts as sets, add known_bits for thin comics.

Thin comics (score 4, no bits): ali-wong, bo-burnham, gary-gulman,
hannibal-buress, maria-bamford, mark-normand, michael-che, nate-bargatze,
sarah-silverman, taylor-tomlinson + demetri, emo, steven-wright, schulz,
giraldo, oneal, dangerfield, rivers.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
TR = HERE / "transcripts"

DEEP2: dict[str, dict] = {
    "ali-wong": {
        "timing_doctrine": "Story sprint, hard stop on the kill. The pregnant-body commitment is a timing device — the room is watching the body while she delivers the thesis. The pause after the dark turn is the room deciding how to feel about a pregnant woman saying that.",
        "style_thesis": "Confessional-assassin engine: turned the most vulnerable physical state into a power move and the domestic into a battlefield. The ambition is the thesis; the pregnancy is the delivery system. She says the thing about ambition, marriage, and motherhood that everyone was thinking.",
        "known_bits": [
            {"title": "Ambition as a love language", "why_it_works": "Says she wants to be the breadwinner with the directness of a business plan. The room laughs because the ambition is stated without apology — the violation is wanting it openly; the benign frame is the obvious love for the husband she's roasting.", "theory_links": ["benign_violation", "status_reversal"]},
            {"title": "The domestic as a war crime", "why_it_works": "Treats marriage and motherhood as a battlefield with casualties. The hyperbole is the engine — every domestic detail escalates to war-crime status. The room recognizes the feeling; the exaggeration makes it funny instead of bitter.", "theory_links": ["escalation", "incongruity"]},
        ],
    },
    "bo-burnham": {
        "timing_doctrine": "Song-sprint, freeze on the confession. The piano is both weapon and shield — the song carries the room forward, the freeze after the big number is where the meta lands. The silence after the song is the real punchline.",
        "style_thesis": "Meta-pop-prophet engine: writes the song that diagnoses the room he's performing it in. The special is a crisis meeting about comedy, and the piano is both weapon and apology. Peak aware: the awareness is the material and the prison.",
        "known_bits": [
            {"title": "The song that diagnoses the room", "why_it_works": "The song is funny AND it names the mechanism of why the room is laughing. The meta-turn is the second punch — the room laughs at the song, then laughs at themselves for laughing. split_knowledge: everyone knows the manipulation is happening; the honesty about it is the joke.", "theory_links": ["split_knowledge", "persona_gap"]},
            {"title": "The apology from inside the machine", "why_it_works": "Performs the critique of performance while performing. The contradiction IS the content — the room can't resolve whether he's sincere or performing sincerity, and the unresolvability is the point.", "theory_links": ["persona_gap", "incongruity"]},
        ],
    },
    "mark-normand": {
        "timing_doctrine": "Fast, no wasted breath, flip on a dime. The 'this is new' warning is a timing device — the room leans in because it might fail. The mid-bit flip is the form: the premise is never precious.",
        "style_thesis": "Page-to-stage engine: works jokes out loud the way a mechanic works an engine — in public, at speed, with the hood up. The flip is a first-class move: if the angle stalls, invert it (complaint → advantage, fear → welcome). The volume is the work ethic made audible.",
        "known_bits": [
            {"title": "The joke as a live animal", "why_it_works": "Tests the premise live, reads the reaction, commits or flips. The room is watching the process AND the product — the transparency is the charm. The flip (when it works) is funnier than the original because the room saw the work.", "theory_links": ["garden_path", "benign_violation"]},
            {"title": "The flip as a first-class move", "why_it_works": "When the jealous-angle stalls, flip to the opposite stance. The room laughs at the audacity of the flip as much as the new angle. The process is visible; the visibility is the trust mechanism.", "theory_links": ["status_reversal", "incongruity"]},
        ],
    },
    "nate-bargatze": {
        "timing_doctrine": "Even, no rush, the story does the work. The innocent observation is a beat, not a pause — he doesn't stop to be confused, he reports the confusion at speed. The self-deprecating shrug resets the room.",
        "style_thesis": "Wholesome-confused engine: treats normal life like a series of small bafflements he's too polite to fight. The confusion is played straight; the craft is invisible under the speed. Clean comedy as a hard mode — the constraint forces better observation.",
        "known_bits": [
            {"title": "Normal life as a mild hazard", "why_it_works": "Takes the most mundane modern experience (airports, coffee orders) and treats it as a series of small emergencies. The room has all felt this; he names it with enough urgency to make the shared feeling funny. The wholesomeness is the benign frame.", "theory_links": ["benign_violation", "incongruity"]},
            {"title": "The dad as a confused narrator", "why_it_works": "Reports fatherhood with the energy of a man who wandered into it by accident. The gap between the responsibility and the confusion is the joke. The room laughs WITH him because the confusion is honest.", "theory_links": ["status_reversal", "benign_violation"]},
        ],
    },
    "sarah-silverman": {
        "timing_doctrine": "Even, the voice is the metronome. The sweet voice on the dark line is the timing device — the contrast arrives before the content. The pause after the kill is the room deciding how to feel about a Disney princess saying that.",
        "style_thesis": "Toddler-provocateur engine: says the most shocking thing in the sweetest voice and lets the contrast detonate. The innocence is a delivery system for the least innocent thoughts. The shock is a door; the heart is the room behind it.",
        "known_bits": [
            {"title": "Innocence as a delivery system", "why_it_works": "The toddler voice makes the taboo thought land as a surprise — the room wasn't braced because the voice said 'safe.' The contrast IS the mechanism. benign_violation at max contrast: violation extreme, benign frame total (the voice).", "theory_links": ["benign_violation", "incongruity"]},
            {"title": "The shock as a door", "why_it_works": "The shock opens the room; the heart walks through. After the detonation, the real feeling arrives — and the room is open because the shock broke the defenses. The two-beat structure (shock → heart) is the signature.", "theory_links": ["two_stories", "persona_gap"]},
        ],
    },
    "taylor-tomlinson": {
        "timing_doctrine": "Story sprint, freeze on the real thing. The 'anyway' after the dark turn is the timing device — it's the reset that says 'we're moving on' while the room is still feeling it. The self-deprecating pivot is a beat.",
        "style_thesis": "Therapy-neurotic engine: treats her own mental health like a group project she's both acing and failing. The therapy frame is the delivery system; the grief is the material. The 'anyway' is the survival mechanism made audible.",
        "known_bits": [
            {"title": "Therapy as a comic form", "why_it_works": "Reports emotional events as case studies in her own psychology, presented like book reports. The clinical frame makes the mess discussable. The room laughs because they've all been in the session.", "theory_links": ["benign_violation", "split_knowledge"]},
            {"title": "Grief as a tight five", "why_it_works": "Takes the heaviest material (loss, depression) and gives it the tightest structure. The economy is the respect — the grief is honored by the craft, not exploited by it. The freeze on the real thing is where the room feels it.", "theory_links": ["benign_violation", "persona_gap"]},
        ],
    },
    "maria-bamford": {
        "timing_doctrine": "Rapid character switches, freeze on the real. The instant voice change is the timing device — the room is catching up to who she's being. The voice crack on the real thing is where the vulnerability lands.",
        "style_thesis": "Character-vault engine: treats her own breakdown as a cast of characters and gives each one a voice. The ad in the head, the mother, the therapist — each gets a voice, and the meeting is the bit. The vulnerability is radical; the craft is the safety net.",
        "known_bits": [
            {"title": "The self as a cast", "why_it_works": "Gives each internal voice a distinct character. The room laughs at the accuracy of the voices AND feels the reality of the chorus. The character is the benign frame; the illness is the content. The meeting of the voices is the form.", "theory_links": ["persona_gap", "benign_violation"]},
            {"title": "The ad in the head", "why_it_works": "Performs the intrusive commercial jingle voice that lives in everyone's head. The room recognizes the voice before they recognize the joke — the recognition IS the laugh. The specificity of the voice is the craft.", "theory_links": ["incongruity", "split_knowledge"]},
        ],
    },
    "michael-che": {
        "timing_doctrine": "Even, the grin is the metronome. The grin before the kill is the timing device — the room sees the grin and braces, but the content still lands. The casual shrug after the grenade resets the room.",
        "style_thesis": "Grin-assassin engine: says the dangerous thing in the friendliest voice and lets the contrast do the work. The news is a comedy writers' room that forgot it was funny — he's just reading it out loud. The grin is both weapon and shield.",
        "known_bits": [
            {"title": "The news as a comedy writers' room", "why_it_works": "Treats every headline as a joke the culture is already telling, and reads it back in a friendly voice. The room laughs because the absurdity was already there — he just said it out loud. The grin is the benign frame.", "theory_links": ["benign_violation", "status_reversal"]},
            {"title": "The dangerous thing in a friendly voice", "why_it_works": "The contrast between content (dangerous) and delivery (friendly) is the engine. The room doesn't know how to feel, and the not-knowing is the laugh. The shrug after says 'I just work here.'", "theory_links": ["incongruity", "benign_violation"]},
        ],
    },
    "hannibal-buress": {
        "timing_doctrine": "Even, no acceleration, hold for the weirdness. The flat delivery of the insane detail is the timing device — the room catches up while he's already moved on. The almost-smile that never fully arrives is the tell.",
        "style_thesis": "Sleepy-surrealist engine: says the weirdest true detail in a flat voice and lets the room fall into the gap. Under-reaction is a form of respect for the weirdness. The calm is the constant; the strange detail is the variable.",
        "known_bits": [
            {"title": "The quietly insane detail", "why_it_works": "Reports a normal situation with one detail that's quietly insane, without comment. The room does the work — the flat delivery is the trust mechanism. The detail is the joke; the flatness is the delivery system.", "theory_links": ["literalise", "incongruity"]},
        ],
    },
    "gary-gulman": {
        "timing_doctrine": "Even, no rush, the image does the work. The pause before the image lands is the timing device — the room is waiting for the picture. The small smile at his own observation is the tell.",
        "style_thesis": "Melancholy-craftsman engine: takes a small observation, turns it over until it reveals the whole sad beauty of being a person. The punchline is a window, and the window opens onto something that makes you laugh and cry in the same breath.",
        "known_bits": [
            {"title": "The ordinary as a cathedral", "why_it_works": "Looks at an ordinary thing long enough that it becomes beautiful. The room laughs AND feels — the dual response is the signature. The craft is the delivery system: the observation is too precise to be accidental.", "theory_links": ["incongruity", "persona_gap"]},
            {"title": "The punchline as a window", "why_it_works": "The punch doesn't close the bit — it opens it. The room sees through the joke to something real. The economy is the respect: every word pays rent, and the rent is the feeling.", "theory_links": ["two_stories", "benign_violation"]},
        ],
    },
    "demetri-martin": {
        "timing_doctrine": "Even, setup and punch on the same breath. The diagram is the timing device — the room sees the structure while he's handing them the object. The tiny smile after a clean turn is the tell.",
        "style_thesis": "Architect one-liner engine: builds joke objects so precisely that the structure is half the laugh. Economy is kindness; every word must pay rent. The deadpan is the lab coat; the precision is the experiment.",
        "known_bits": [
            {"title": "The joke as an object", "why_it_works": "The joke is a load-bearing structure — remove one word and it collapses. The room laughs at the perfection of the object AND the content. The diagram (when he shows it) is the second punch.", "theory_links": ["literalise", "incongruity"]},
        ],
    },
    "emo-philips": {
        "timing_doctrine": "Wandering setup, sudden precise punch. The longer-than-needed pause is the timing device — the room is waiting for the wander to resolve. The voice crack on the normal word is the tell.",
        "style_thesis": "Anxious-surrealist engine: narrates his own confusion like a nature documentary about a very nervous animal. The self is a rumor issuing press releases. Kindness to the confused is the highest virtue — and the comic strategy.",
        "known_bits": [
            {"title": "The self as a bad tour guide", "why_it_works": "Reports his own confusion with the energy of a tour guide who's lost the group. The room laughs at the accuracy of the confusion — they've all been the bad tour guide of their own brain.", "theory_links": ["benign_violation", "persona_gap"]},
        ],
    },
    "steven-wright": {
        "timing_doctrine": "Even, no acceleration, hold for the absurdity to land. The pause after the impossible claim is the timing device — the room needs the silence to process that he said it flat. The non-reaction to his own image is the tell.",
        "style_thesis": "Deadpan-absurdist engine: delivers impossible statements with the cadence of a man reading a weather report. Surrealism as the default setting; normality as the thing that needs explaining. Maximum calm, maximum nonsense.",
        "known_bits": [
            {"title": "Impossible objects", "why_it_works": "Reports an object with impossible properties as fact. The deadpan is the benign frame — the room believes him for half a second. The half-second is the joke. literalize at max.", "theory_links": ["literalise", "incongruity"]},
        ],
    },
    "andrew-schulz": {
        "timing_doctrine": "Fast, reactive. The crowd-work pivot is a beat — he takes what the room gives and turns it into content in real time.",
        "style_thesis": "Clip-machine engine (already seeded). The special is a content factory; the crowd is both material and audience.",
        "known_bits": [],
    },
    "greg-giraldo": {
        "timing_doctrine": "Accelerating cross-examination, hard stop on the kill. The deposition voice is the timing device — the room feels like witnesses. The sudden tender turn is the release.",
        "style_thesis": "Lawyer-demolition engine: cross-examines a premise until it confesses to being stupid. The logic is the weapon; the tenderness is the surprise. The smartest man in the room dismantling the room's assumptions.",
        "known_bits": [
            {"title": "The cultural claim as a witness", "why_it_works": "Treats every cultural claim as a witness with something to hide, then cross-examines it until it confesses. The room is the jury. The logic is airtight; the conclusion is devastating.", "theory_links": ["rigidify", "bogus_logic"]},
        ],
    },
    "patrice-oneal": {
        "timing_doctrine": "Accelerating interrogation, hard stop on the kill. The bully voice is the timing device — the room braces, then the tender turn arrives. The laugh that is also a cry is the tell.",
        "style_thesis": "Truth-bully engine: loved the room so much he'd fight it until it told the truth back. The bully is a love language; the interrogation is the craft. The truth is a form of love, even when it doesn't feel like it.",
        "known_bits": [
            {"title": "The social lie as an enemy", "why_it_works": "Treats every social lie as a challenge, then follows it until the room confesses. The room laughs because the lie is exposed AND because the exposure is done with love. The bully is the benign frame.", "theory_links": ["status_reversal", "benign_violation"]},
        ],
    },
    "rodney-dangerfield": {
        "timing_doctrine": "Rapid-fire setups, each ending in another self-own. 'I tell ya' is the windup.",
        "style_thesis": "Zero-status engine (already seeded).",
        "known_bits": [],
    },
    "joan-rivers": {
        "timing_doctrine": "Rapid setup, surgical hold, kill. The pause before the kill is the timing device — the room sees it coming and can't escape. The hand on the hip is punctuation.",
        "style_thesis": "Status-assassin engine: dressed up the cruelest observation in couture and never pretended it was kindness. The cruelty was craft. The smile is a weapon; the annotation IS the joke.",
        "known_bits": [
            {"title": "The dressed insult", "why_it_works": "The insult arrives in couture — the glamour is the benign frame that makes the cruelty acceptable. The room laughs at the precision of the annotation AND the audacity of saying it. The pause before the kill is the room bracing.", "theory_links": ["status_reversal", "benign_violation"]},
        ],
    },
}


def link_transcripts() -> dict:
    """Link funnygraph/transcripts/*.txt into graphs as sets. Returns counts."""
    counts = {}
    for tdir in sorted(TR.iterdir()):
        if not tdir.is_dir():
            continue
        cid = tdir.name
        gpath = COMEDIANS / cid / "comedian-graph.json"
        if not gpath.exists():
            continue
        txts = sorted(tdir.glob("*.txt"))
        if not txts:
            continue
        g = json.loads(gpath.read_text())
        existing = {s.get("set_id") for s in g.get("sets", [])}
        added = 0
        for tp in txts:
            sid = f"{cid}_{tp.stem[:50]}"
            if sid in existing:
                continue
            words = len(re.findall(r"[a-z']{3,}", tp.read_text(
                encoding="utf-8", errors="replace").lower()))
            if words < 200:
                continue
            g.setdefault("sets", []).append({
                "set_id": sid,
                "title": tp.stem.replace("-", " ").title(),
                "status": "transcript-linked (synthetic timing until ASR)",
                "transcript": {"path": f"transcripts/{cid}/{tp.name}",
                               "format": "plain txt", "words": words},
                "timing_measured": None,
                "note": "from HF comedy-transcripts (scrapsfromtheloft)",
            })
            added += 1
        if added:
            g["provenance"]["transcripts_linked"] = [
                s["transcript"]["path"] for s in g["sets"]
                if s["transcript"]["path"].startswith("transcripts/")]
            counts[cid] = added
            gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
    return counts


def apply_deep2() -> dict:
    counts = {}
    for cid, deep in DEEP2.items():
        gpath = COMEDIANS / cid / "comedian-graph.json"
        if not gpath.exists():
            continue
        g = json.loads(gpath.read_text())
        changed = False
        if deep.get("timing_doctrine") and not (
                g.get("timing_profile") or {}).get("doctrine_hypothesis"):
            g.setdefault("timing_profile", {})["doctrine_hypothesis"] = \
                deep["timing_doctrine"]
            changed = True
        if deep.get("style_thesis") and not g["identity"].get("style_thesis"):
            g["identity"]["style_thesis"] = deep["style_thesis"]
            changed = True
        if deep.get("known_bits") and not g.get("known_bits"):
            g["known_bits"] = deep["known_bits"]
            # bit essays
            existing = {s.get("id") for s in g.get("essay_seeds", [])}
            for i, kb in enumerate(deep["known_bits"][:2]):
                sid = f"{cid}-bit-{i+1:02d}"
                if sid not in existing:
                    g.setdefault("essay_seeds", []).append({
                        "id": sid,
                        "title": f"{g.get('name', cid)}: '{kb['title']}' — how the bit works",
                        "thesis": kb["why_it_works"],
                        "evidence": [f"known_bits[{i}]", "theory_links"],
                        "outline": ["the setup", "the mechanism", "why the room laughs",
                                    "the theory link",
                                    "what this reveals about the engine"],
                        "status": "seed",
                    })
            changed = True
        if changed:
            g["version"] = max(g.get("version", 1), 2)
            gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
            counts[cid] = len(deep.get("known_bits", []))
    return counts


def main() -> None:
    print("=== linking transcripts ===")
    lc = link_transcripts()
    for cid, n in sorted(lc.items()):
        print(f"  {cid}: +{n} sets")
    print(f"  total: {sum(lc.values())} sets linked")
    print("=== applying deep2 ===")
    dc = apply_deep2()
    for cid, n in sorted(dc.items()):
        print(f"  {cid}: {n} known bits")
    print(f"  total: {len(dc)} graphs enriched")


if __name__ == "__main__":
    main()
