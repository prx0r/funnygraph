#!/usr/bin/env python3
"""DEEPEN — upgrade hypothesis graphs to full theory graphs (Louis/Norm depth).

Adds to each comedian-graph.json:
  - sets[] linked to existing transcripts (characters2) with topics extracted
  - theory_links[] with academic citations (GTVH, Attardo, DPV timing, etc.)
  - timing_doctrine (hypothesis until measured)
  - known_bits[] — signature bits with WHY they work (theory-applied)
  - expanded essay_seeds
  - distinctive_terms from linked transcripts (measured stylometry)

The end goal: THE comedy database — theory applied to every comedian.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
TR = Path("/root/characters2/theory/transcripts")
SCRIBE = Path("/root/characters2/theory/scribe")

# ── shared theory library (cited in every graph) ────────────────────────────
THEORY = {
    "gtvh": {
        "id": "gtvh", "cite": "Attardo & Raskin — General Theory of Verbal Humor",
        "claim": "Joke = {SO, LM, SI, TA, NS, LA}. Technique and Narrative Strategy shape how the mechanism is staged.",
    },
    "attardo-pause": {
        "id": "attardo-pause-taxonomy", "cite": "Attardo & Pickering 2011 — Timing in the performance of jokes",
        "claim": "Punch lines preceded by substantial pauses (0.6-0.8s+); timing = pause distribution + speech rate.",
    },
    "dpv-timing": {
        "id": "dpv", "cite": "arxiv 2605.00143 — Timing is Everything: Temporal Scaffolding of Semantic Surprise in Humor",
        "claim": "Temporal features substantially outweigh semantic incongruity for audience appreciation; timing GATES cognitive access.",
    },
    "incongruity": {
        "id": "incongruity", "cite": "Shultz / Suls — incongruity-resolution theory",
        "claim": "Humor from the detection and resolution of an incongruity between expected and actual.",
    },
    "benign-violation": {
        "id": "benign_violation", "cite": "McGraw & Warren 2010 — Benign Violation Theory",
        "claim": "Something is funny when it is a violation (wrong, threatening, unsettling) AND benign (safe, acceptable, play-framed).",
    },
    "status-reversal": {
        "id": "status_reversal", "cite": "Roger & Duffy / status theory of humor",
        "claim": "Humor often involves the fall of status or the reversal of a status hierarchy.",
    },
    "split-knowledge": {
        "id": "split_knowledge", "cite": "Veatch 1978 — theory of joking relationships",
        "claim": "Audience and performer share knowledge the persona pretends not to have; the laugh is the alliance signal.",
    },
    "escalation": {
        "id": "escalation", "cite": "Norrick 2004 — Co-operative principle in conversational joking",
        "claim": "Humor escalates by building on prior material, violating cooperative expectations of relevance/quantity.",
    },
    "rigidify": {
        "id": "rigidify", "cite": "operator registry — apply the literal rule until it breaks",
        "claim": "Take a figurative phrase literally and apply its rules rigidly until the literal reading collapses into absurdity.",
    },
    "literalise": {
        "id": "literalise", "cite": "operator registry — literalize the metaphor",
        "claim": "Treat a metaphor as a literal description and follow its implications.",
    },
    "false-analogy": {
        "id": "false_analogy", "cite": "operator registry — false analogy",
        "claim": "Assert an equivalence between two things that share a surface feature but differ in the relevant dimension.",
    },
    "garden-path": {
        "id": "garden_path", "cite": "Frazier & Rayner — garden-path sentences / misdirection in joke structure",
        "claim": "Lead the audience down one interpretive path, then reveal the other path was there all along.",
    },
    "two-stories": {
        "id": "two_stories", "cite": "setup-punch two-stories rule (Corley / standard joke theory)",
        "claim": "Setup installs story A believably; punch reveals story B was there all along.",
    },
    "persona-gap": {
        "id": "persona_gap", "cite": "Goffman / performance theory",
        "claim": "The gap between performed identity and authored awareness is itself an engine — the room senses both layers.",
    },
    "bogus-logic": {
        "id": "bogus_logic", "cite": "operator registry — bogus logic",
        "claim": "Follow a flawed logical chain with total sincerity until the absurdity of the conclusion reveals the flaw.",
    },
    "repetition-variation": {
        "id": "repetition_variation", "cite": "Norrick 1993 — repetition in joking",
        "claim": "Repeat a structure or phrase with small variations until the repetition itself becomes the comic engine.",
    },
}

# ── deep theory seeds: signature bits + style + timing per comedian ─────────
# Each entry: known_bits (title, why_it_works, theory), style thesis, timing doctrine
DEEP: dict[str, dict] = {
    "shane-gillis": {
        "timing_doctrine": "Fast setup, dead stop on the dumb take, laugh into the mic. The break IS the timing — he cracks himself, and the room follows.",
        "style_thesis": "The lovable-idiot-warlord engine: takes every cultural cue at face value from inside the dumbest plausible reading, then commits so hard the reading becomes the joke. The half-second where the room believes him is where the laugh lives. The break character (cracking up) is not a flaw — it's the audience's permission structure.",
        "known_bits": [
            {"title": "Local advertising / small-business voice", "why_it_works": "He adopts the voice and worldview of a specific regional type (the confident local ad guy, the Wawa philosopher) and never winks. rigidify: applies the dumb logic as if it were law. The room laughs at the type they recognize AND at his total commitment.", "theory_links": ["rigidify", "benign_violation", "status_reversal"]},
            {"title": "The roast as a love language", "why_it_works": "Roast-mode bits work because the violation (cruelty) is framed as affiliative (the boys). benign_violation at max: the joke is mean AND the room knows everyone involved is in on it.", "theory_links": ["benign_violation", "split_knowledge"]},
            {"title": "Cancellation / culture-war bits", "why_it_works": "He treats the culture war as a series of guys being wrong out loud. status_reversal: the powerful (cancelers) are made to look stupid; the low-status (the idiot) is made to look free. The engine transfers because the topic is never the point — the confident-wrongness is.", "theory_links": ["status_reversal", "rigidify"]},
        ],
    },
    "matt-mccusker": {
        "timing_doctrine": "Slow build, accelerates mid-spiral, stops on the glitch. The pause before 'wait' is the tell — he's following the thought in real time, and the room comes with him.",
        "style_thesis": "Cosmic-gremlin engine: takes a mundane thing literally until it reveals a conspiracy between language, commerce, and consciousness — then narrates the conspiracy like weather. literalise at max. The spiral IS the form; the punchline is wherever the spiral happens to stop.",
        "known_bits": [
            {"title": "Apps as metaphysics", "why_it_works": "Treats DoorDash/Uber/etc. as literal cosmological systems, not services. literalize: the app's incentives ARE the laws of physics in this universe. The room recognizes the truth of the metaphor before they recognize the joke.", "theory_links": ["literalise", "incongruity"]},
            {"title": "Stoned epistemology", "why_it_works": "The stoner-philosopher persona gives him license to follow a thought past the point where normal conversation would stop. The room stays because he commits to the bit of following it ALL the way. false_analogy: connects two things that share no surface feature except his heightened attention.", "theory_links": ["false_analogy", "benign_violation"]},
        ],
    },
    "theo-von": {
        "timing_doctrine": "Slow drawl, long pause before the weird image, sudden precision inside the swamp of words. The drawl is a delivery system for the sharp observation — the room leans in because he sounds like he's not trying.",
        "style_thesis": "Swamp-philosopher engine: treats modern life as a foreign country he's reporting from with the wrong map — and the wrong map is funnier and sometimes truer. The goof-to-wisdom ratio is the engine: the room is laughing at the goof when the wisdom lands, and the wisdom hits harder because they were laughing.",
        "known_bits": [
            {"title": "The road story / small-town parable", "why_it_works": "One small road story becomes a cosmology if you let it. The structure is parable: concrete image → unexpected universal. The drawl sells the sincerity; the observation is too precise to be accidental.", "theory_links": ["garden_path", "incongruity"]},
            {"title": "Animals in people clothes", "why_it_works": "Treats people as animals wearing costumes (literalise) and describes the animal behavior with deadpan precision. The room recognizes the animal first, the person second — that order is the joke.", "theory_links": ["literalise", "status_reversal"]},
        ],
    },
    "jimmy-carr": {
        "timing_doctrine": "Even setup-punch-reload. The pause before the kill is surgical — always long enough for the room to see it coming, never long enough for them to escape. The grin after the kill is punctuation.",
        "style_thesis": "Surgical one-liner engine: takes the darkest available reading of a normal situation and delivers it with host-level polish so the contrast does the work. The grin is the benign frame that makes the violation benign. The economy is the craft — every word pays rent.",
        "known_bits": [
            {"title": "The dark turn on a normal premise", "why_it_works": "Setup installs a normal, even wholesome scenario. Punch reveals the darkest reading was there all along. two_stories at maximum darkness. The host grin is the benign frame — without it, the violation is just cruel; with it, it's comedy.", "theory_links": ["two_stories", "benign_violation"]},
            {"title": "Self-aware shock comedy", "why_it_works": "He names the mechanism ('I know, I know') which is itself a transgression — the room is shocked AND complicit. split_knowledge: everyone knows the joke is 'too far'; the grin says we all chose to be here.", "theory_links": ["split_knowledge", "benign_violation"]},
        ],
    },
    "sean-lock": {
        "timing_doctrine": "Rant with a hidden metronome. Escalates through the domestic epic, pauses on the precise image, resets with a sigh. The sigh is the tell — it says 'I've been here before and I'll be here again.'",
        "style_thesis": "Domestic-surrealist engine: treats every ordinary object as having a secret agenda, and narrates the war between man and objects as if it were a national emergency. rigidify + literalize: the kettle is not a kettle, it's an antagonist with a plan. The escalation into the epic is the comic form.",
        "known_bits": [
            {"title": "The object with an agenda", "why_it_works": "Takes a mundane annoyance (kettle, remote, supermarket) and treats it as evidence in a larger case against the design of modern life. rigidify: applies the logic of a national emergency to a domestic inconvenience. The room recognizes the feeling before the joke.", "theory_links": ["rigidify", "incongruity"]},
            {"title": "The domestic as national epic", "why_it_works": "Escalates a small complaint into a full narrative with stakes, characters, and a climax. The gap between the scale of the telling and the scale of the event IS the joke. garden_path: the room thinks it's a complaint, it's actually an epic.", "theory_links": ["garden_path", "escalation"]},
        ],
    },
    "james-acaster": {
        "timing_doctrine": "Slow build, logical acceleration, verdict. The pauses are architectural — each one is the room catching up to the next step of the case. The callback is the load-bearing wall.",
        "style_thesis": "Long-con-architect engine: takes a small absurd observation and treats it as a constitutional matter, following the logic until the absurdity becomes inevitable. rigidify + literalize at max. The bit is a legal case; the room is the jury; the verdict was always going to be absurd.",
        "known_bits": [
            {"title": "The absurd premise as a legal case", "why_it_works": "Starts with a stupid observation, then builds a complete logical framework around it as if it were a matter of law. The room is drawn into the logic before they notice they're in an absurd world. rigidify: every step follows from the last, even when the foundation is insane.", "theory_links": ["rigidify", "bogus_logic"]},
            {"title": "The callback architecture", "why_it_works": "A detail from 10 minutes ago returns as the punchline. The room's delayed recognition ('OH — that was the joke all along') is the second laugh. repetition_variation: the callback is a variation that recontextualizes the original.", "theory_links": ["repetition_variation", "two_stories"]},
        ],
    },
    "joe-list": {
        "timing_doctrine": "Fast, no wasted breath. The self-deprecating pivot is a beat, not a pause — he doesn't stop to be anxious, he speeds up into it. The 'anyway' resets the room.",
        "style_thesis": "Anxious-everyman engine: treats every normal adult situation as a mild hazard worth reporting with urgency. benign_violation at low voltage: the violation is mild (he's anxious about nothing), the benign frame is total (he's clearly fine). The speed is the anxiety made audible.",
        "known_bits": [
            {"title": "The airport as a philosophy course", "why_it_works": "Takes the most mundane modern experience (airport) and treats it as a series of small emergencies. The room has all felt this; he names it with enough urgency to make the shared feeling funny. status_reversal: the powerful system (airport) is revealed as an anxiety machine.", "theory_links": ["status_reversal", "benign_violation"]},
            {"title": "Health anxiety as a comic form", "why_it_works": "Reports bodily sensations with the gravity of a medical drama. The gap between the severity of the telling and the triviality of the event is the joke. garden_path: the room thinks it's a medical story, it's actually a comedy about anxiety.", "theory_links": ["garden_path", "benign_violation"]},
        ],
    },
    "william-montgomery": {
        "timing_doctrine": "Torrential, sudden freezes. The energy never drops until the freeze — and the freeze IS the punchline. The commitment to a bad idea is the timing device.",
        "style_thesis": "Chaos-machine engine: treats the set as a controlled demolition of normal comedy rules, and the demolition IS the act. character_violation at max: every social stop sign is walked past with total commitment. The room stays because they don't know what's coming next — and neither does he.",
        "known_bits": [
            {"title": "The committed bad idea", "why_it_works": "Takes a premise that shouldn't work and commits to it so hard that the commitment becomes the joke. The room laughs at the audacity of the commitment, not the content. benign_violation: the violation is the bad premise; the benign frame is the obvious joy of the performance.", "theory_links": ["benign_violation", "character_violation"]},
            {"title": "The KT regular as a force of nature", "why_it_works": "The persona has accumulated meta-status from appearing repeatedly. Each set is not just a set — it's an episode in the ongoing saga of William Montgomery. The room is laughing at the character as much as the bits.", "theory_links": ["status_reversal", "split_knowledge"]},
        ],
    },
    "hans-kim": {
        "timing_doctrine": "Even, clean setup, sudden kill. The pause after the setup is the ethnographer's beat — he's describing the ritual, and the pause is the room recognizing themselves in the description.",
        "style_thesis": "Immigrant-observer engine: treats American customs as alien ceremonies and describes them with the precision of an ethnographer who's also a little offended. The outsider lens is the misinterpretation rule: the room sees itself through his eyes, and the eyes are clearer because they're outside.",
        "known_bits": [
            {"title": "America as a strange customs office", "why_it_works": "Describes a normal American ritual with the precision of someone who wasn't raised in it. literalize: treats the ritual as if it were literally as strange as it sounds when described fresh. The room recognizes the absurdity they'd stopped seeing.", "theory_links": ["literalise", "incongruity"]},
        ],
    },
    "cam-patterson": {
        "timing_doctrine": "Fast, escalating. The commit to the bit is a beat, not a pause — he escalates without giving the room a reset. The closer is the explosion.",
        "style_thesis": "Firestarter engine: treats the everyman situation as a fight worth having out loud, and escalates until the room concedes. status_reversal + benign_violation: the low-status everyman wins the fight against the situation. The energy is the strategy — polish loses to commitment.",
        "known_bits": [
            {"title": "The everyday fight", "why_it_works": "Takes a normal annoyance and treats it as a fight he's going to win on volume and commitment alone. The room is drawn into the fight because the energy is contagious. status_reversal: the person who was losing (to the situation) is now winning (on stage).", "theory_links": ["status_reversal", "benign_violation"]},
        ],
    },
    "casey-rocket": {
        "timing_doctrine": "Torrential, sudden freezes. The stillness after the chaos is the punchline — the room is catching up to the images while he stands still. The image is the timing device.",
        "style_thesis": "Absurdist-firecracker engine: treats the set as a series of strange images that only make sense if you abandon the need for them to make sense. incongruity at max without resolution — the images don't resolve, they accumulate. The freeze is where the room decides how to feel.",
        "known_bits": [
            {"title": "The strange image cascade", "why_it_works": "A series of vivid, unconnected images delivered with total commitment. The room doesn't resolve the incongruity — they ride it. The freeze after the cascade is where the laugh lands, because the room has caught up to where he already was.", "theory_links": ["incongruity", "benign_violation"]},
        ],
    },
    "andrew-schulz": {
        "timing_doctrine": "Fast, reactive. The crowd-work pivot is a beat — he takes what the room gives and turns it into content. The 'this is going viral' energy is the timing device.",
        "style_thesis": "Clip-machine engine: treats the live room as raw material for the content engine, and the engine as the point. The special is a content factory; the clip is the unit of truth. Crowd work is collaboration AND domination — he takes the room's energy and makes it his.",
        "known_bits": [
            {"title": "Crowd work as co-writing", "why_it_works": "Takes a crowd member's response and turns it into a bit in real time. The room is both the material and the audience — the meta-awareness is part of the joke. split_knowledge: everyone knows the content engine is running, and they want to be in the clip.", "theory_links": ["split_knowledge", "status_reversal"]},
        ],
    },
    "bert-kreischer": {
        "timing_doctrine": "Torrential story, sudden freeze. The shirtless swagger is a timing device — the body is doing the energy so the voice can do the story. The freeze is where the myth catches up to the truth.",
        "style_thesis": "Man-child-epic engine: treats his own worst decisions as origin stories for legends, and the legend is always bigger than the truth. escalation at max: the story grows with each telling. The room loves him FOR the mess — the self-deprecation is the benign frame that makes the chaos charming.",
        "known_bits": [
            {"title": "The Machine story", "why_it_works": "A true(ish) story of a bad decision escalated to mythic proportions. The room knows it's exaggerated; the exaggeration IS the joke. escalation + repetition_variation: each telling adds a detail, the myth grows, the truth becomes irrelevant.", "theory_links": ["escalation", "repetition_variation"]},
            {"title": "The shirtless truth", "why_it_works": "The shirtless delivery is a status move: he's so comfortable in his mess that he's literally exposed. The body is the benign frame that makes the violations (bad decisions, chaos) acceptable. status_reversal: the man-child wins.", "theory_links": ["status_reversal", "benign_violation"]},
        ],
    },
    "tom-segura": {
        "timing_doctrine": "Even, calm, sudden kill. The calm is the timing device — the room has no warning because the delivery never signals the turn. The pause after the kill is the room deciding how to feel.",
        "style_thesis": "Deadpan-dark engine: treats the worst possible reading of a normal situation as the default, and delivers it with the calm of a weather report. benign_violation at maximum contrast: the violation is extreme, the benign frame is total (the calm). The contrast is the comedy.",
        "known_bits": [
            {"title": "The weather report of doom", "why_it_works": "Describes a terrible situation with the calm of a weather forecast. The contrast between content valence (dark) and delivery valence (calm) is the engine — the room doesn't know how to feel, and the not-knowing is the laugh. This is the OPPOSITE of Louis's split: text reads dark, delivery is flat.", "theory_links": ["incongruity", "benign_violation"]},
        ],
    },
    "robin-williams": {
        "timing_doctrine": "Torrential, sudden freezes. The cascade is a timing device — the room is catching up to the characters while he's already in the next one. The freeze is where the real feeling lands.",
        "style_thesis": "Manic-character-vault engine: treats every premise as a room full of people who each need a voice, then lets the loudest one accidentally tell the truth. The characters are both escape and exposure — he becomes other people to avoid himself, and the self leaks through anyway.",
        "known_bits": [
            {"title": "The character flood", "why_it_works": "A cascade of impressions and voices on a single premise. The room is laughing at the speed and the accuracy, but the flood is also a defense mechanism — the real feeling arrives in the freeze after the cascade. incongruity: the voices don't resolve into one point, they accumulate into a feeling.", "theory_links": ["incongruity", "escalation"]},
            {"title": "The sudden stillness", "why_it_works": "After the cascade, he stops. The stillness is where the real thing catches up. The room laughs AND feels — the dual response is the signature. This is the vulnerability engine: the chaos was buying time for the truth.", "theory_links": ["benign_violation", "persona_gap"]},
        ],
    },
    # ── classic GOATs (transcript-linked, same depth) ─────────────────────
    "george-carlin": {
        "timing_doctrine": "The list sermon: accelerates through a run of examples (rising rate, rising pitch), hard-stops on the key word (the euphemism being executed), lets the stop do the indignant work, then restarts the list engine. Timing is rhetorical, not confessional — a preacher's cadence.",
        "style_thesis": "Prophet-curmudgeon engine: treats any soft phrase as a crime scene and reconstructs what actually happened from the words people chose not to use. rigidify + literalize at max: hold the euphemism to its own literal meaning until it breaks. The list is the sermon form; the key word is the gavel.",
        "known_bits": [
            {"title": "The seven dirty words", "why_it_works": "Treats a language taboo as a constitutional question. rigidify: applies the rules of 'obscene' literally until the category collapses. The bit is jurisprudence — the courtroom is the stage, the audience is the jury.", "theory_links": ["rigidify", "literalise", "status_reversal"]},
            {"title": "Euphemism execution (soft language)", "why_it_works": "Takes a soft phrase ('passed away', 'persons of substance') and holds it to its literal meaning until the euphemism confesses. The list accelerates like a sermon; the key word lands like a gavel. The room laughs at the recognition of the lie they've been telling.", "theory_links": ["rigidify", "literalise"]},
            {"title": "The list as sermon form", "why_it_works": "Lists are rhetorical acceleration devices — the room is carried forward by the rhythm, the key word is the amen. The list is not a collection of jokes; it's a rhetorical structure that makes the final word inevitable and devastating.", "theory_links": ["escalation", "repetition_variation"]},
        ],
    },
    "bill-burr": {
        "timing_doctrine": "Accelerating rant, sudden self-check pause. The rant builds like a runaway train; the self-check is the hand on the brake that makes the room trust him again. The nervous laugh at his own darkness is the timing device — it says 'I know, I know.'",
        "style_thesis": "Rage-apologist engine: takes his own worst emotional read of a situation, escalates it to the absurd conclusion, then audits the escalation. The awareness is the act — he critiques his own rant mid-rant. The red face is the scoreboard; the self-check is the moral technology.",
        "known_bits": [
            {"title": "The rant that audits itself", "why_it_works": "The rant escalates to an absurd conclusion, then he catches himself ('I'm not saying...'). The self-check is the benign frame that makes the rage acceptable — the room knows he knows. split_knowledge: everyone shares the anger; he's the one who says it AND critiques it.", "theory_links": ["split_knowledge", "benign_violation"]},
            {"title": "Anger as a love language", "why_it_works": "The rage is real even when the bit is craft. The room laughs because they feel it too — the laugh is the alliance signal. The self-deprecation after the rant is the release valve: the anger was the setup, the self-awareness is the punch.", "theory_links": ["split_knowledge", "status_reversal"]},
        ],
    },
    "dave-chappelle": {
        "timing_doctrine": "Sprints in character, holds 2-3s+ after heavy point. The hold after the heavy point is the signature — the room needs the silence to metabolize what he just said. The story sermon: he tells it like it happened to someone he knew, then reveals it happened to all of us.",
        "style_thesis": "Philosophical-raconteur engine: treats every story as a parable with a moral he almost didn't notice. The character voices are both escape and exposure — he becomes other people to say the true thing. The hold after the heavy point is where the room catches up to what he actually said.",
        "known_bits": [
            {"title": "The story that turns", "why_it_works": "Tells a story with the cadence of a folktale, then the turn reveals the story was about something larger (race, power, America). garden_path: the room thinks it's a story, it's actually a thesis. The hold after the turn is the room metabolizing the double meaning.", "theory_links": ["garden_path", "two_stories"]},
            {"title": "The character as a shield and a weapon", "why_it_works": "Becomes a character to say the thing he couldn't say as himself. The character is the benign frame; the content is the violation. The room laughs at the character and absorbs the thesis at the same time.", "theory_links": ["benign_violation", "persona_gap"]},
        ],
    },
    "chris-rock": {
        "timing_doctrine": "Stammer-build, hard-stop punch, short hold for the 'I know' wave. The stammer is the windup; the hard stop is the punch landing; the short hold is the room's recognition catching up.",
        "style_thesis": "Rhythm-prosecutor engine: treats the contradiction nobody names as a crime scene and prosecutes it with the rhythm of a preacher. The stammer-build is the indictment; the hard-stop punch is the verdict. The 'I know' wave is the jury's response.",
        "known_bits": [
            {"title": "The contradiction nobody names", "why_it_works": "Names a thing everyone knows but nobody says. split_knowledge: the room has the knowledge; he's the one who says it out loud. The laugh is the alliance signal — 'yes, that's true, and I'm glad someone said it.'", "theory_links": ["split_knowledge", "status_reversal"]},
            {"title": "The stammer-build", "why_it_works": "The stammer is not a flaw — it's the windup. The room leans in because he seems to be losing his train of thought; the hard-stop punch arrives where they didn't expect. garden_path: the stammer is the misdirection.", "theory_links": ["garden_path"]},
        ],
    },
    "mitch-hedberg": {
        "timing_doctrine": "Setup-punch-restart, 300-500ms, no story mode. The reload is the timing device — the room barely has time to laugh before the next one. The deadpan is the constant; the surprise is the variable.",
        "style_thesis": "Whimsical-float engine: treats objects as having secret lives and reports their secret lives with total sincerity. literalize at max: the burrito has a future, the pillow is a sleeping hat. The one-liner is the form; the impossible object is the material.",
        "known_bits": [
            {"title": "The object with a secret life", "why_it_works": "Treats a normal object as having hidden properties and reports them with total sincerity. literalize: the object literally has the property he describes. The deadpan delivery is the benign frame — the room believes him for half a second, and the half-second is the joke.", "theory_links": ["literalise", "incongruity"]},
            {"title": "The one-liner as a haiku with a trapdoor", "why_it_works": "Short setup, short punch, no fat. The economy is the craft — every word pays rent. The restart is the timing device: the room is still laughing when the next one arrives, and the overlap is the form.", "theory_links": ["two_stories"]},
        ],
    },
    "richard-pryor": {
        "timing_doctrine": "Sprints through scenes, freezes on the confession. The freeze after the confession is the signature — the room needs the silence to metabolize what he just said. The character voices are the delivery system; the freeze is where the truth lands.",
        "style_thesis": "Confessional-firestorm engine: treats every personal catastrophe as raw material that only becomes his when he says the unsayable version out loud. status_reversal at max: the worst person in the room becomes the most honest. The confession is the moral act even when the content isn't.",
        "known_bits": [
            {"title": "The fire as origin story", "why_it_works": "Tells the story of his own worst night with the cadence of a survival narrative. The room is crying laughing at a crime scene he's still standing in. benign_violation: the violation is extreme; the benign frame is that he survived and is telling it.", "theory_links": ["benign_violation", "status_reversal"]},
            {"title": "Characters as escape hatches", "why_it_works": "Becomes a character to say the thing he couldn't say as himself. The character is the benign frame; the content is the violation. The room laughs at the character and absorbs the confession at the same time.", "theory_links": ["persona_gap", "benign_violation"]},
        ],
    },
    "jerry-seinfeld": {
        "timing_doctrine": "Surgical: short holds ~400/900ms, riff-restarts. The timing is engineered — every pause is load-bearing. The riff-restart is the form: the joke is built in public, piece by piece, and the room comes with him.",
        "style_thesis": "Observational-auditor engine: treats the mundane as a subject worthy of rigorous analysis. The noticing is the generative root — all comedy is noticing. The joke has WEIGHT: a physical density you can feel in the palm. The detail is the weight.",
        "known_bits": [
            {"title": "The noticing engine", "why_it_works": "Finds the one detail in a normal situation that nobody has named, then names it with the precision of a scientist. The room recognizes the detail before they recognize the joke — the recognition IS the laugh.", "theory_links": ["incongruity", "garden_path"]},
            {"title": "The word as seed", "why_it_works": "A word's sound and meaning connect across synapses that aren't supposed to cross. The joke is built from the word, not around it. The economy is the craft — the word is the load-bearing wall.", "theory_links": ["literalise", "two_stories"]},
        ],
    },
    "john-mulaney": {
        "timing_doctrine": "Story sprint, hard stop on the reveal. The callback is the load-bearing wall — a detail from 10 minutes ago returns as the punchline. The old-radio voice is the timing device: the cadence never signals the turn.",
        "style_thesis": "Old-radio-neurotic engine: treats ordinary social friction as a federal case, and narrates the case with the gravity of a Supreme Court opinion. The anxiety is real enough to fuel the engine; the polish is the delivery system. The callback is the architecture.",
        "known_bits": [
            {"title": "The social federal case", "why_it_works": "Takes a small social error and treats it as a matter of law. rigidify: applies the rules of social life as if they were constitutional law. The room recognizes the anxiety; the polish makes it funny instead of sad.", "theory_links": ["rigidify", "benign_violation"]},
            {"title": "The callback architecture", "why_it_works": "A detail from early in the hour returns as the punchline at the end. The room's delayed recognition is the second laugh. repetition_variation: the callback is a variation that recontextualizes the original.", "theory_links": ["repetition_variation", "two_stories"]},
        ],
    },
    "bill-hicks": {
        "timing_doctrine": "Accelerating sermon, hard stop on the kill. The sermon builds like a revival meeting; the hard stop is the amen. The cigarette is punctuation — the pause for the drag is the congregation catching up.",
        "style_thesis": "Prophet-curmudgeon engine (same lineage as Carlin, different fuel): treats every cultural product as propaganda until proven otherwise; the bit is the deconstruction performed at scream-volume. The anger is doctrine — the mission IS the act.",
        "known_bits": [
            {"title": "Advertising as a war on consciousness", "why_it_works": "Treats every ad as an assault on awareness and deconstructs it live. rigidify: applies the logic of the ad literally until the absurdity appears. The room recognizes the assault they've been enduring; the anger is the recognition made audible.", "theory_links": ["rigidify", "status_reversal"]},
            {"title": "Going to the fear", "why_it_works": "His own doctrine: go to the fear, that's where the material is. The bit works because he goes there first — the room follows because he's already in the dark place and he's not flinching.", "theory_links": ["benign_violation", "persona_gap"]},
        ],
    },
    "rodney-dangerfield": {
        "timing_doctrine": "Rapid-fire setups, each ending in another self-own. 'I tell ya' is the timing device — the windup for the next self-own. The sweat is the tell; the tie tug is the punctuation.",
        "style_thesis": "Zero-status engine: walks in already losing, converts every setup into another receipt for his own disrespect. status_reversal at max: the man who gets no respect has built an empire on not having it. The self-own ladder is the form — each rung is lower than the last.",
        "known_bits": [
            {"title": "The self-own ladder", "why_it_works": "Each setup ends in another self-own, each self-own is lower than the last. The room laughs at the descent. status_reversal: the man who loses everything can say anything.", "theory_links": ["status_reversal", "escalation"]},
            {"title": "'No respect' as a cosmology", "why_it_works": "The catchphrase is not a tag — it's an ontology. The whole act is organized around the fact that he gets no respect. The room recognizes the feeling; the exaggeration makes it funny instead of sad.", "theory_links": ["rigidify", "benign_violation"]},
        ],
    },
    "stewart-lee": {
        "timing_doctrine": "Slow build, deliberate sabotage, long hold. The repetition that turns a phrase into sludge is the timing device — the room is waiting for the phrase to break, and the break is the punch.",
        "style_thesis": "Meta-architect engine: builds a bit, sabotages it, critiques the sabotage, then lets the rubble become the punchline. The comedy special as a hostile novel — the audience is a character in the text. The repetition is the weapon; the sabotage is the form.",
        "known_bits": [
            {"title": "The comedy special as a hostile novel", "why_it_works": "Treats the special as a text to be annotated, and the audience as co-readers of a hostile text. The meta-awareness is the material — the bit is about being a bit.", "theory_links": ["persona_gap", "split_knowledge"]},
            {"title": "Repetition as a weapon", "why_it_works": "Repeats a phrase until it becomes sludge, then uses the sludge as the punch. The room is waiting for the phrase to break, and the break is the laugh.", "theory_links": ["repetition_variation", "rigidify"]},
        ],
    },
    "louis-ck": {
        "timing_doctrine": "Fast speech, many pauses. 14 topic-pauses (>0.8s) are the confession holds. The two longest holds (8.16s, 5.32s) sit at the two darkest turns. Timing gates the laugh: the room needs the silence to catch up.",
        "style_thesis": "Sincere-storyteller engine: treats his own worst impulse as universal law and keeps walking it until the room admits complicity. Content-valence and delivery-valence are OPPOSITE — the text reads like shame, the delivery is manic. That split is the engine.",
        "known_bits": [
            {"title": "Road Rage / the van", "why_it_works": "The 8.16s hold after the deflationary turn is the longest silence — the room metabolizes the whole story in that gap. The closer drops the story entirely and confesses the mechanism: he says terrible things because the audience's upset is enjoyable.", "theory_links": ["dpv", "status_reversal", "split_knowledge"]},
            {"title": "The intrusive thought", "why_it_works": "Shifts from storytelling to live intrusive thought. The 5.32s hold is the second-longest. He never resolves it; the discomfort IS the payload. Awareness of the thought's ugliness is stated before the room can reject it.", "theory_links": ["benign_violation"]},
        ],
    },
    "norm-macdonald": {
        "timing_doctrine": "THE never-stop engine: 6 pauses in 2 minutes, none shorter than 1.16s — rare and hard, punctuation not breathing. The refusal to give the room a reset IS the timing doctrine.",
        "style_thesis": "Suspension-deadpan engine: tells old jokes at deliberately stultifying length, defends the indefensible with professorial logic, never breaks. Persona as Prestige trick: dopey folksy innocent played by a well-read ironist. The gap between performer intelligence and performed innocence is the engine.",
        "known_bits": [
            {"title": "The moth joke", "why_it_works": "The digression BEFORE the punch carries the room into the wrong frame; the punch ('because the light was on') arrives clean, no tag. false_analogy: moth-to-flame, not moth-to-foot.", "theory_links": ["false_analogy", "garden_path", "bogus_logic"]},
            {"title": "The long winding journey", "why_it_works": "A 12-minute story told with calm practical tone. 'The progression is completely natural' — faux-logical escalation, each step reasonable from the last. The punchline is non-negotiable — the digression SERVES it, never replaces it.", "theory_links": ["bogus_logic", "escalation"]},
        ],
    },
}


def load_transcripts(cid: str) -> list[Path]:
    d = TR / cid
    if not d.exists():
        return []
    return sorted(d.glob("*.txt"))


def transcript_words(p: Path) -> list[str]:
    raw = p.read_text(encoding="utf-8", errors="replace")
    return re.findall(r"[a-z']{3,}", raw.lower())


_CONTRAST_CACHE: list[str] | None = None


def load_all_contrast(skip: str) -> list[str]:
    global _CONTRAST_CACHE
    if _CONTRAST_CACHE is None:
        words: list[str] = []
        for other in sorted(COMEDIANS.iterdir()):
            for tp in load_transcripts(other.name):
                words.extend(transcript_words(tp))
        _CONTRAST_CACHE = words
    # filter out the skip comedian's contribution lazily is hard; use full set
    # (slight contamination is fine for lift ranking)
    return _CONTRAST_CACHE


def distinctive(cid: str, words_a: list[str]) -> list[dict]:
    words_b = load_all_contrast(cid)
    if len(words_a) < 100 or len(words_b) < 500:
        return []
    a, b = Counter(words_a), Counter(words_b)
    n_a, n_b = sum(a.values()), sum(b.values())
    stop = set("""the a an and or of to in on for with is are was were be been have has had
    do does did i you he she it we they not no yes so if as at by from but that this
    what which who when where why how all any just like know right yeah oh really going
    get got one two would could should im ive dont doesnt""".split())
    out = []
    for w in set(a) | set(b):
        if w in stop or len(w) < 4:
            continue
        pa = (a[w] + 0.5) / (n_a + 0.5 * len(set(a) | set(b)))
        pb = (b[w] + 0.5) / (n_b + 0.5 * len(set(a) | set(b)))
        lift = pa / pb
        if lift > 2.0 and a[w] >= 3:
            out.append({"ngram": w, "lift": round(lift, 3), "count": a[w]})
    out.sort(key=lambda x: -x["lift"])
    return out[:20]


def deepen(cid: str) -> bool:
    gpath = COMEDIANS / cid / "comedian-graph.json"
    if not gpath.exists():
        return False
    g = json.loads(gpath.read_text())
    deep = DEEP.get(cid, {})
    links = list(THEORY.values())

    # timing doctrine
    if deep.get("timing_doctrine"):
        g.setdefault("timing_profile", {})
        g["timing_profile"]["doctrine_hypothesis"] = deep["timing_doctrine"]
        g["timing_profile"]["status"] = "hypothesis until word-timed sets measured"

    # style thesis into identity
    if deep.get("style_thesis"):
        g["identity"]["style_thesis"] = deep["style_thesis"]

    # known bits
    if deep.get("known_bits"):
        g["known_bits"] = deep["known_bits"]

    # link existing transcripts as sets
    tfiles = load_transcripts(cid)
    if tfiles and not g.get("sets"):
        sets = []
        for tp in tfiles[:5]:
            words = transcript_words(tp)
            sets.append({
                "set_id": f"{cid}_{tp.stem[:40]}",
                "title": tp.stem.replace(f"{cid}-", "").replace("-", " ").title(),
                "status": "transcript-linked (synthetic timing until ASR)",
                "transcript": {
                    "path": str(tp),
                    "format": "plain txt",
                    "words": len(words),
                },
                "timing_measured": None,
                "note": "content available for topics extraction; timing not measured",
            })
        g["sets"] = sets
        g["provenance"]["transcripts_linked"] = [str(p) for p in tfiles[:5]]

    # distinctive terms skipped in this pass (slow) — run profile_comedian.py separately
    # if tfiles:
    #     all_words = []
    #     for tp in tfiles:
    #         all_words.extend(transcript_words(tp))
    #     terms = distinctive(cid, all_words)
    #     if terms:
    #         g["distinctive_terms"] = terms

    # theory links — MERGE (never wipe measured graphs' authored links)
    existing_internal = {l.get("id") for l in (g.get("theory_links") or {}).get("internal", [])}
    new_internal = [
        {"id": t["id"], "cite": t["cite"], "claim": t["claim"],
         "applies_to": "primary move / timing / structure"}
        for t in links[:8] if t["id"] not in existing_internal
    ]
    if isinstance(g.get("theory_links"), dict):
        g["theory_links"]["internal"] = (
            g["theory_links"].get("internal", []) + new_internal)
        ext = g["theory_links"].get("external", [])
        ext_ids = {e.get("id") for e in ext if isinstance(e, dict)}
        for e in [
            {"id": "standup4ai", "cite": "StandUp4AI dataset (EMNLP 2025)",
             "use": "future laugh-position ground truth"},
            {"id": "tic-talk", "cite": "TIC-TALK (CHum 2026)",
             "use": "future cross-comedian timing normalization"},
        ]:
            if e["id"] not in ext_ids:
                ext.append(e)
        g["theory_links"]["external"] = ext
    else:
        g["theory_links"] = {
            "internal": new_internal,
            "external": [
                {"id": "standup4ai", "cite": "StandUp4AI dataset (EMNLP 2025)",
                 "use": "future laugh-position ground truth"},
                {"id": "tic-talk", "cite": "TIC-TALK (CHum 2026)",
                 "use": "future cross-comedian timing normalization"},
            ],
        }

    # essay seeds — MERGE with existing (never overwrite measured graphs)
    name = g.get("name", cid)
    mis = g["identity"].get("misinterpretation_rule", "")
    existing_ids = {s.get("id") for s in g.get("essay_seeds", [])}
    new_seeds = []
    # skip the generic engine essay if the graph already has 2+ authored essays
    if f"{cid}-essay-01" not in existing_ids and len(g.get("essay_seeds", [])) < 2:
        new_seeds.append({
            "id": f"{cid}-essay-01",
            "title": f"Why is {name} funny? The {g['identity'].get('archetype', 'engine').replace('_', ' ')} engine",
            "thesis": deep.get("style_thesis") or mis,
            "evidence": ["identity.misinterpretation_rule", "known_bits",
                         "identity.operator_priors", "timing_profile.doctrine_hypothesis"],
            "outline": ["the deal in one sentence", "the misinterpretation rule as engine",
                        "2-3 signature bits dissected", "timing doctrine",
                        "what makes this persona impossible to copy"],
            "status": "seed — ready to draft",
        })
    if deep.get("known_bits"):
        n_exist = len(g.get("essay_seeds", []))
        for i, kb in enumerate(deep["known_bits"][:2]):
            sid = f"{cid}-bit-{i+1:02d}"
            if sid in existing_ids:
                continue
            new_seeds.append({
                "id": sid,
                "title": f"{name}: '{kb['title']}' — how the bit works",
                "thesis": kb["why_it_works"],
                "evidence": [f"known_bits[{i}]", "theory_links"],
                "outline": ["the setup", "the mechanism", "why the room laughs",
                            "the theory link", "what this reveals about the engine"],
                "status": "seed",
            })
    g["essay_seeds"] = (g.get("essay_seeds") or []) + new_seeds

    # update provenance
    g["provenance"]["theory_applied"] = True
    g["provenance"]["deepened"] = "2026-10-16"
    g["version"] = max(g.get("version", 1), 2)

    gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> None:
    n = 0
    for d in sorted(COMEDIANS.iterdir()):
        if not (d / "comedian-graph.json").exists():
            continue
        if d.name in EXCLUDED:
            continue
        if deepen(d.name):
            n += 1
            bits = len(DEEP.get(d.name, {}).get("known_bits", []))
            tr = len(load_transcripts(d.name))
            print(f"  deepened {d.name} ({bits} known bits, {tr} transcripts)")
    print(f"\n=== {n} graphs deepened to theory depth ===")


if __name__ == "__main__":
    main()
