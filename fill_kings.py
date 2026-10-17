#!/usr/bin/env python3
"""FILL KINGS — known_bits + timing + signature titles for thin in-scope kings."""
from __future__ import annotations
import json
from pathlib import Path

FILL: dict[str, dict] = {
    "joan-rivers": {
        "sigtitle": "glamour assassin",
        "timing": "Rapid setup, surgical hold, kill. The pause before the kill lets the room see it coming and not escape. The hand on the hip is punctuation.",
        "bits": [
            {"title": "Can we talk? (the dressed insult)", "why_it_works": "Opens with faux-intimacy, then delivers the surgical insult in couture. The glamour is the benign frame; the cruelty is precise, never sloppy. The room laughs at the annotation AND the audacity.", "theory_links": ["status_reversal", "benign_violation"]},
            {"title": "Age as a battlefield", "why_it_works": "Turns her own face/life into the primary text, annotated live. Self-targeting first buys the license to target everyone else. The workaholism is the engine; the stage is where it pays.", "theory_links": ["split_knowledge", "status_reversal"]},
        ]},
    "steven-wright": {
        "sigtitle": "deadpan physicist",
        "timing": "Even, no acceleration, hold for the absurdity. The pause after the impossible claim lets the room process that he said it flat. The non-reaction is the tell.",
        "bits": [
            {"title": "Impossible objects", "why_it_works": "Reports objects with impossible properties as fact ('I have a map of the United States... actual size'). The deadpan is the benign frame; the half-second of belief is the joke. Literalise at max.", "theory_links": ["literalise", "incongruity"]},
            {"title": "The one-liner as haiku with a trapdoor", "why_it_works": "Short setup, short punch, no fat. Every word pays rent. The restart is the timing device — the room is still laughing when the next one arrives.", "theory_links": ["two_stories"]},
        ]},
    "ray-romano": {
        "sigtitle": "put-upon everyman",
        "timing": "Whiny build, self-defeating landing. The voice cracks upward on the complaint, then drops into the shrug. The shrug says 'what can you do' and the room answers by laughing.",
        "bits": [
            {"title": "Marriage as a complaint department", "why_it_works": "Reports domestic life as a series of small defeats he walked into with eyes open. The room recognizes the dynamic before the joke — recognition IS the laugh. Everybody loves Raymond because everybody IS Raymond.", "theory_links": ["benign_violation", "split_knowledge"]},
        ]},
    "bill-maher": {
        "sigtitle": "smug prosecutor",
        "timing": "New-Rules cadence: setup, beat, verdict. The smugness is the metronome — the room knows the kill is coming and leans in anyway.",
        "bits": [
            {"title": "New Rules as verdicts", "why_it_works": "Treats weekly pieties as defendants, delivers verdicts with total certainty. The research is the weapon; the smugness is the delivery system. The room laughs at the sentence being passed.", "theory_links": ["rigidify", "status_reversal"]},
        ]},
    "billy-connolly": {
        "sigtitle": "big yin raconteur",
        "timing": "Banjaxed anecdote build with musical timing — long shaggy setups, grace-note punchlines. The accent carries the room; the warmth does the rest.",
        "bits": [
            {"title": "The shaggy story sermon", "why_it_works": "Ten-minute stories that earn every laugh twice — once for the telling, once for the landing. The warmth is the benign frame for genuinely filthy content. The Big Yin energy makes rudeness feel like love.", "theory_links": ["storytelling", "persona_gap"]},
        ]},
    "adam-sandler": {
        "sigtitle": "man-child opera",
        "timing": "Goat-boy voices at full commitment, songs as emotional crescendos. The silliness never winks — that's why it lands and why it lasts.",
        "bits": [
            {"title": "The Chanukah Song as Trojan horse", "why_it_works": "A silly list song that smuggles genuine belonging to Jewish kids who'd never heard themselves in pop culture. The joke is the delivery system; the inclusion is the payload.", "theory_links": ["persona_gap", "split_knowledge"]},
        ]},
    "dick-gregory": {
        "sigtitle": "civil-rights punchline",
        "timing": "Calm setup, devastating fact, hold for the room to catch up. The calm IS the weapon — no rant needed when the facts are the punchlines.",
        "bits": [
            {"title": "The calm indictment", "why_it_works": "Made white rooms laugh at their own racism in the 1960s — the most dangerous room-work ever attempted. The facts do the violating; the calm provides the benign frame. Nobody else could have survived the rooms he played.", "theory_links": ["status_reversal", "benign_violation"]},
        ]},
    "demetri-martin": {
        "sigtitle": "joke designer",
        "timing": "Even, setup and punch on the same breath. The diagram is the timing device — the room sees the structure while he's handing them the object.",
        "bits": [
            {"title": "The palindromes and charts", "why_it_works": "Visual aids as punchlines — the chart IS the joke, not illustration. The room laughs at the rigor AND the silliness simultaneously. Precision as a comic position.", "theory_links": ["literalise", "bisociation"]},
        ]},
    "russell-peters": {
        "sigtitle": "accent arsenal",
        "timing": "Setup in narrator voice, detonation in character voice. The switch IS the timing — the room braces for the accent and it still lands.",
        "bits": [
            {"title": "Somebody gonna get a hurt real bad", "why_it_works": "The dad-voice catchphrase that became a global meme before memes. Becomes every ethnicity in the room — the accuracy disarms the audacity. Post-racial by way of pre-racial.", "theory_links": ["persona_gap", "benign_violation"]},
        ]},
    "aziz-ansari": {
        "sigtitle": "millennial anthropologist",
        "timing": "Fast escalation into panic. The panic is the timing device — the room rides the escalation, the punch is the landing.",
        "bits": [
            {"title": "The food voice", "why_it_works": "Treats food opinions with religious intensity. The gap between stakes (low) and passion (total) is the joke. Raaaandy-level commitment to the bit about nothing.", "theory_links": ["escalation", "incongruity"]},
        ]},
    "lewis-black": {
        "sigtitle": "apoplexy correspondent",
        "timing": "Simmer, sputter, explosion, finger-shake. The Daily Show rants built the cadence: reasonable man driven mad by unreasonable world, on schedule.",
        "bits": [
            {"title": "The finger-shake indictment", "why_it_works": "Takes a news absurdity and performs a man having a stroke about it. The apoplexy is choreographed — every sputter placed. The room laughs at the performance of losing it, safely.", "theory_links": ["escalation", "status_reversal"]},
        ]},
    "ron-white": {
        "sigtitle": "scotch philosopher",
        "timing": "Drawl with a glass in hand. The pause for the sip IS the timing — the room waits, he drinks, the tag lands smoother for the wait.",
        "bits": [
            {"title": "Tater Salad aftermath", "why_it_works": "The arrest story told like a war medal ceremony. Drunk wisdom delivered sober — the gap between the teller (composed) and the tale (chaos) is the engine.", "theory_links": ["storytelling", "persona_gap"]},
        ]},
    "iliza-shlesinger": {
        "sigtitle": "millennial prosecutor",
        "timing": "Physical sprint + character voices. The party-girl voice vs the feminist thesis — she performs both sides of the argument at full speed.",
        "bits": [
            {"title": "Elder Millennial autopsy", "why_it_works": "Dissects her own generation's rituals (weddings, Instagram, dating) with anthropologist energy + party-girl characters. The double position (inside AND above it) is the engine.", "theory_links": ["status_reversal", "persona_gap"]},
        ]},
    "dylan-moran": {
        "sigtitle": "drunk philosopher",
        "timing": "Sprawl with a hidden metronome. The sigh before the observation, the sudden precise image inside the ramble. The glass is a prop and a metronome.",
        "bits": [
            {"title": "Modernity as a bad houseguest", "why_it_works": "Treats every innovation as a personal insult to the order of things. The curmudgeonry is warm — he loves the world he's yelling at. The sprawl IS the form; editing would kill it.", "theory_links": ["rigidify", "persona_gap"]},
        ]},
    "katt-williams": {
        "sigtitle": "pimp-prophet truth-teller",
        "timing": "Rapid-fire street philosophy with preacher cadence. The suit says showman; the content says revolutionary. Speed is the intelligence made audible.",
        "bits": [
            {"title": "The Pimp Chronicles sermon", "why_it_works": "Street knowledge delivered with rhetorical genius — every anecdote has a moral, every moral has a laugh. The pimp persona is the benign frame for genuinely radical observation.", "theory_links": ["status_reversal", "persona_gap"]},
        ]},
    "patton-oswalt": {
        "sigtitle": "nerd professor",
        "timing": "Reference-dense cascades with sincere landings. The cascade is the timing device; the sudden sincerity is the punch that makes nerds cry.",
        "bits": [
            {"title": "Pop culture as scripture", "why_it_works": "Treats franchises with theological seriousness, then finds the human truth inside. Star Wars theory that ends in grief counseling. The reference is the door; the heart is the room.", "theory_links": ["bisociation", "persona_gap"]},
        ]},
    "brian-regan": {
        "sigtitle": "physical everyman",
        "timing": "Full-body commitment, befuddled reset. The body does the talking — becomes the UPS guy, the doctor, the animal. The reset is the breath before the next commitment.",
        "bits": [
            {"title": "The full-body mundane", "why_it_works": "Becomes the thing he's describing with total physical commitment. Clean as doctrine: no shock available, so the observation must be perfect. The face IS the punchline.", "theory_links": ["literalise", "incongruity"]},
        ]},
    "mike-epps": {
        "sigtitle": "neighborhood philosopher",
        "timing": "Laid-back story build, sudden character detonation. The chill is the setup; the explosion is the punch. Indy timing — never rushed.",
        "bits": [
            {"title": "Under Rated survivor stories", "why_it_works": "Hood anecdotes told with survivor's pride and comedian's timing. The room gets the tour of a world they don't know, guided by someone who loves it. Authenticity as engine.", "theory_links": ["storytelling", "persona_gap"]},
        ]},
    "donald-glover": {
        "sigtitle": "multihyphenate ironist",
        "timing": "Deadpan with trapdoors. The Weirdo hour plays awkwardness as a weapon — the room never knows if he's bombing on purpose until it's too late.",
        "bits": [
            {"title": "Awkward as weapon", "why_it_works": "Performs discomfort so precisely the room feels it physically. The irony has layers — is he awkward, playing awkward, or playing someone playing awkward? The unresolvability IS the bit.", "theory_links": ["persona_gap", "garden_path"]},
        ]},
    "wanda-sykes": {
        "sigtitle": "exasperated truth-teller",
        "timing": "Eye-roll setup, flat verdict. The exasperation is the metronome — the room knows the kill is coming and leans in for it.",
        "bits": [
            {"title": "The flat verdict", "why_it_works": "States the obvious truth about race, marriage, politics with total flatness. No escalation needed — the truth stated plainly IS the punch. The eye-roll does the work of ten tags.", "theory_links": ["rigidify", "status_reversal"]},
        ]},
    "jack-whitehall": {
        "sigtitle": "posh chaos agent",
        "timing": "Polished setup, lad detonation. The gap between the private-school polish and the content is the engine — posh boy saying exactly what posh boys aren't supposed to.",
        "bits": [
            {"title": "Posh vs lad split", "why_it_works": "Performs the war between upbringing and appetite. The room laughs at the posh delivery of unposh content — the contrast never gets old because the commitment never wavers.", "theory_links": ["persona_gap", "status_reversal"]},
        ]},
    "jerrod-carmichael": {
        "sigtitle": "quiet radical",
        "timing": "Soft setup, devastating turn. The quiet IS the timing — the room leans in so far the punch barely needs volume. Rothaniel proved silence scales.",
        "bits": [
            {"title": "Rothaniel confessional", "why_it_works": "Came out on stage in real time with no jokes as shield. The bravest hour in modern comedy — vulnerability with zero punchline protection. The room didn't laugh; it witnessed. Then it laughed.", "theory_links": ["benign_violation", "persona_gap"]},
        ]},
    "kathleen-madigan": {
        "sigtitle": "shot-drinking realist",
        "timing": "Conversational build, blue-collar landing. The Catholic-Missouri voice is the delivery system — plain speech carrying sharp observation.",
        "bits": [
            {"title": "Midwest Catholic autopsy", "why_it_works": "Dissects family, faith, and drinking with insider precision. The room trusts her because she's clearly from the world she's roasting. Authenticity as armor.", "theory_links": ["split_knowledge", "benign_violation"]},
        ]},
    "sam-morril": {
        "sigtitle": "dry technician",
        "timing": "Flat setup, flat punch, no tell. The dryness IS the timing — the room supplies the energy he withholds. Economy as ethic.",
        "bits": [
            {"title": "The dry anecdote", "why_it_works": "Tells wild stories with zero affect — the gap between content (insane) and delivery (bored) is the whole joke. The withheld energy makes the room lean in.", "theory_links": ["incongruity", "garden_path"]},
        ]},
    "tig-notaro": {
        "sigtitle": "deadpan witness",
        "timing": "Glacial setup, seismic punch. The famous Largo set proved stillness scales — illness, loss, and Taylor Dayne delivered without flinching.",
        "bits": [
            {"title": "Hello, I have cancer", "why_it_works": "Opened with the diagnosis, no preamble. The bravest cold open ever — the room didn't know whether to laugh, and that not-knowing became the most famous set of the decade.", "theory_links": ["benign_violation", "persona_gap"]},
        ]},
    "whitney-cummings": {
        "sigtitle": "ambition engineer",
        "timing": "Rapid analysis, personal counterexample, furious tag. Speed is the intelligence made audible — the room can't keep up and loves it.",
        "bits": [
            {"title": "Codependency autopsy", "why_it_works": "Reverse-engineers her own relationships like systems with bugs. The engineer brain on dating chaos — flowcharts optional, fury mandatory. Smart women recognize the debugger.", "theory_links": ["rigidify", "persona_gap"]},
        ]},
    "paul-mooney": {
        "sigtitle": "hollywood conscience",
        "timing": "Slow setup, devastating racial truth, hold for the room to deal with it. The elder-statesman pace forces attention — no rush, nowhere to hide.",
        "bits": [
            {"title": "The race verdict", "why_it_works": "States Hollywood's racial truth baldly from forty years inside the rooms. The authority is the engine — he was there. Negrodamus sees.", "theory_links": ["status_reversal", "split_knowledge"]},
        ]},
    "sarah-cooper": {
        "sigtitle": "lip-sync satirist",
        "timing": "Trump's cadence, her face. The mimicry IS the timing — every pause and sniff reproduced until the content indicts itself.",
        "bits": [
            {"title": "How to medical", "why_it_works": "Lip-syncing Trump suggesting disinfectant, deadpan. The verbatim reproduction is the whole joke — no commentary needed when the source material convicts itself.", "theory_links": ["literalise", "persona_gap"]},
        ]},
    "tom-papa": {
        "sigtitle": "cheerful neurotic",
        "timing": "Upbeat setup, anxious spiral, cheerful landing. The cheer never breaks — that's what makes the anxiety funny instead of sad.",
        "bits": [
            {"title": "Bread and marriage", "why_it_works": "Finds existential dread in carbs and commitment, delivered with a smile. The gap between the sunny delivery and the spiraling content is the engine.", "theory_links": ["benign_violation", "incongruity"]},
        ]},
    "phil-wang": {
        "sigtitle": "polite subversive",
        "timing": "Gentle setup, sharp turn. The politeness IS the misdirection — the room relaxes, then the blade arrives with a smile.",
        "bits": [
            {"title": "Empire politeness autopsy", "why_it_works": "Dissects British-Malaysian identity with exquisite manners and a knife. The courtesy makes the cuts land deeper — you don't see them coming.", "theory_links": ["garden_path", "status_reversal"]},
        ]},
    "sam-jay": {
        "sigtitle": "dry truth-teller",
        "timing": "Flat delivery, sharp turn. SNL-writer precision with standup soul — every line placed, nothing wasted.",
        "bits": [
            {"title": "3 in the Morning excavation", "why_it_works": "Late-night honesty about race, relationships, and self — delivered like texts to a friend. The intimacy is the engine; the flatness is the trust mechanism.", "theory_links": ["benign_violation", "split_knowledge"]},
        ]},
    },
}


def main() -> None:
    from pathlib import Path
    n = 0
    for cid, f in FILL.items():
        g = Path("comedians") / cid / "comedian-graph.json"
        if not g.exists():
            continue
        j = json.loads(g.read_text())
        if len(j.get("known_bits", [])) >= 2 and (j.get("timing_profile") or {}).get("doctrine_hypothesis") and (j.get("modes") or {}).get("signature_title"):
            continue
        ident = j["identity"]
        if f.get("timing") and not (j.get("timing_profile") or {}).get("doctrine_hypothesis"):
            j.setdefault("timing_profile", {})["doctrine_hypothesis"] = f["timing"]
        if f.get("bits") and len(j.get("known_bits", [])) < 2:
            j["known_bits"] = f["bits"]
            ex = {s.get("id") for s in j.get("essay_seeds", [])}
            for i, kb in enumerate(f["bits"][:2]):
                sid = f"{cid}-bit-{i+1:02d}"
                if sid not in ex:
                    j.setdefault("essay_seeds", []).append({
                        "id": sid, "title": f"{j.get('name',cid)}: '{kb['title']}' — how the bit works",
                        "thesis": kb["why_it_works"],
                        "evidence": [f"known_bits[{i}]", "theory_links"],
                        "outline": ["the setup","the mechanism","why the room laughs","the theory link","what this reveals"],
                        "status": "seed"})
        m = j.get("modes") or {}
        if f.get("sigtitle") and not m.get("signature_title"):
            m["signature_title"] = f["sigtitle"]
            j["modes"] = m
        j["version"] = max(j.get("version", 1), 2)
        g.write_text(json.dumps(j, indent=2) + "\n", encoding="utf-8")
        n += 1
    print(f"filled: {n}")


if __name__ == "__main__":
    main()
