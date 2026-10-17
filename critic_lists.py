#!/usr/bin/env python3
"""CRITIC LISTS — Paste 2017 comics leg + specials corroboration.

Two gaps closed in one file:
  1. THIRD CRITICS LEG. Paste's 50 Greatest Stand-up Comics (2017, panel
     ballots, standup-only, Cosby deliberately excluded by Paste) joins
     CC2004 + RS2017 in rank_comedians.py (same Borda machinery, same
     postdate rule). 21 Paste legends missing from graphs draft as KINGS
     (established by definition) with recognition.paste_2017. Ellen ranks
     #29 on Paste but stays excluded (owner prerogative — skipped).
  2. GOAT-SPECIAL THIRD LEG (ENDPOINTS #2). RS 25 (2015) + Vulture 20
     (2014) + Flavorwire 50 (2013) + Paste 25-of-2017 special ranks matched
     to specials.json entries -> rankings/critic_specials.json: per-special
     citations + citation-count mini-board. Cosby entries skipped (no graph).

Usage: python3 critic_lists.py [--no-draft]
Reads: nothing external (lists transcribed below with URLs).
Writes: graphs (recognition.paste_2017 + 21 drafts), rankings/critic_specials.json.
Then: rank_comedians.py reads paste_2017 (wired separately) + rate.py rebuilds.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
OUT = HERE / "rankings"

# Paste 50 Greatest Stand-up Comics, 2017-06-09 (Garrett Martin).
# https://www.pastemagazine.com/comedy/stand-up/the-50-greatest-stand-up-comics-of-all-time
PASTE = {
 "richard-pryor": 1, "chris-rock": 2, "george-carlin": 3, "steve-martin": 4,
 "joan-rivers": 5, "andy-kaufman": 6, "bob-newhart": 7, "mort-sahl": 8,
 "steven-wright": 9, "dave-chappelle": 10, "eddie-murphy": 11, "louis-ck": 12,
 "lenny-bruce": 13, "robin-williams": 14, "moms-mabley": 15, "lily-tomlin": 16,
 "redd-foxx": 17, "bill-hicks": 18, "garry-shandling": 19, "don-rickles": 20,
 "albert-brooks": 21, "mitch-hedberg": 22, "dick-gregory": 23,
 "jonathan-winters": 24, "robert-klein": 25, "roseanne-barr": 26,
 "rodney-dangerfield": 27, "phyllis-diller": 28, "bernie-mac": 30,
 "norm-macdonald": 31, "sarah-silverman": 32, "aziz-ansari": 33,
 "maria-bamford": 34, "hannibal-buress": 35, "paul-mooney": 36,
 "whoopi-goldberg": 37, "george-burns": 38, "henny-youngman": 39,
 "jim-gaffigan": 40, "gilbert-gottfried": 41, "todd-barry": 42,
 "patton-oswalt": 43, "wanda-sykes": 44, "margaret-cho": 45,
 "john-mulaney": 46, "paul-f-tompkins": 47, "kevin-hart": 48,
 "mike-birbiglia": 49, "jerry-seinfeld": 50,
}
# NOTE: Paste #29 Ellen deliberately absent (EXCLUDED, owner prerogative).

# slug -> (name, generation id, note). All US, all established = kings.
DRAFTS = {
 "steve-martin": ("Steve Martin", "seventies", "Wild and Crazy Guy; banjo; SNL"),
 "andy-kaufman": ("Andy Kaufman", "seventies", "Anti-comedy; Latka; wrestling"),
 "bob-newhart": ("Bob Newhart", "pioneers", "Button-Down Mind; deadpan phone calls"),
 "mort-sahl": ("Mort Sahl", "pioneers", "First modern political satirist; hungry i"),
 "moms-mabley": ("Moms Mabley", "pioneers", "Chitlin Circuit legend; Apollo"),
 "lily-tomlin": ("Lily Tomlin", "pioneers", "Laugh-In breakout; characters"),
 "redd-foxx": ("Redd Foxx", "pioneers", "Party records; Sanford and Son"),
 "garry-shandling": ("Garry Shandling", "eighties-boom", "Show-biz satire; Larry Sanders"),
 "don-rickles": ("Don Rickles", "pioneers", "Merchant of venom; insult pioneer"),
 "albert-brooks": ("Albert Brooks", "seventies", "Absurdist shorts; SNL films"),
 "jonathan-winters": ("Jonathan Winters", "pioneers", "Improv characters; Maude Frickert"),
 "robert-klein": ("Robert Klein", "seventies", "First HBO hour; Harvard Lampoon"),
 "roseanne-barr": ("Roseanne Barr", "eighties-boom", "Working-class sitcom queen"),
 "phyllis-diller": ("Phyllis Diller", "pioneers", "Self-deprecating pioneer; Fang"),
 "bernie-mac": ("Bernie Mac", "nineties", "Original Kings; I ain't scared of you"),
 "whoopi-goldberg": ("Whoopi Goldberg", "eighties-boom", "Direct from Broadway; EGOT"),
 "george-burns": ("George Burns", "pioneers", "Vaudeville to Gracie to Oh God"),
 "henny-youngman": ("Henny Youngman", "pioneers", "Take my wife, please"),
 "gilbert-gottfried": ("Gilbert Gottfried", "seventies", "Filthiest clean comic; Aristocrats"),
 "margaret-cho": ("Margaret Cho", "nineties", "I'm the One That I Want"),
 "paul-f-tompkins": ("Paul F. Tompkins", "nineties", "Mr Show; dapper absurdism"),
}

# (list_id, [entries...]) — specials corroboration. (comedian-slug, title, rank)
SPECIALS = {
 "rs-2015": [
  ("mitch-hedberg", "Comedy Central Presents", 25), ("denis-leary", "No Cure for Cancer", 24),
  ("dennis-miller", "Black and White", 23), ("patrice-o-neal", "Elephant in the Room", 22),
  ("janeane-garofalo", "HBO Comedy Half-Hour", 21), ("kevin-hart", "Let Me Explain", 20),
  ("david-cross", "The Pride Is Back", 19), ("sam-kinison", "Breaking All the Rules", 18),
  ("steven-wright", "A Steven Wright Special", 17), ("sarah-silverman", "Jesus Is Magic", 16),
  ("roseanne-barr", "The Roseanne Barr Show", 15), ("eddie-izzard", "Dress to Kill", 14),
  ("bill-hicks", "Relentless", 13), ("whoopi-goldberg", "Direct From Broadway", 12),
  ("bill-cosby", "Himself", 11), ("dave-chappelle", "Killin Them Softly", 10),
  ("eddie-murphy", "Delirious", 9), ("george-carlin", "Carlin at USC", 8),
  ("louis-ck", "Shameless", 7), ("chris-rock", "Bring the Pain", 6),
  ("robin-williams", "An Evening at the Met", 5), ("robert-klein", "An Evening With Robert Klein", 4),
  ("wanda-sykes", "Ima Be Me", 3), ("david-cross", "Let America Laugh", 2),
  ("richard-pryor", "Live in Concert", 1)],
 "vulture-2014": [
  ("eddie-izzard", "Dress to Kill", 20), ("mike-birbiglia", "My Girlfriends Boyfriend", 19),
  ("whoopi-goldberg", "Direct From Broadway", 18), ("zach-galifianakis", "Live at the Purple Onion", 17),
  ("roseanne-barr", "The Roseanne Barr Show", 16), ("mitch-hedberg", "Comedy Central Half Hour", 15),
  ("maria-bamford", "The Special Special Special", 14), ("janeane-garofalo", "HBO Comedy Half Hour", 13),
  ("bill-hicks", "Revelations", 12), ("steven-wright", "A Steven Wright Special", 11),
  ("paula-poundstone", "Cats Cops and Stuff", 10), ("bill-cosby", "Himself", 9),
  ("dave-chappelle", "Killin Them Softly", 8), ("robin-williams", "An Evening with Robin Williams", 7),
  ("louis-ck", "Shameless", 6), ("eddie-murphy", "Delirious", 5),
  ("steve-martin", "A Wild and Crazy Guy", 4), ("george-carlin", "Carlin at Carnegie", 3),
  ("chris-rock", "Bring the Pain", 2), ("richard-pryor", "Live on the Sunset Strip", 1)],
 "flavorwire-2013": [
  ("chris-rock", "Bring the Pain", 1), ("george-carlin", "Jammin in New York", 3),
  ("eddie-murphy", "Delirious", 4), ("louis-ck", "Chewed Up", 2),
  ("richard-pryor", "Live in Concert", 5), ("dave-chappelle", "Killin Them Softly", 6),
  ("bill-hicks", "Relentless", 8), ("steven-wright", "A Steven Wright Special", 14),
  ("eddie-izzard", "Dress to Kill", 6), ("jim-gaffigan", "Beyond the Pale", 36),
  ("bill-burr", "Let It Go", 32), ("maria-bamford", "The Special Special Special", 19),
  ("mike-birbiglia", "My Girlfriends Boyfriend", 17), ("patton-oswalt", "No Reason to Complain", 20),
  ("colin-quinn", "Long Story Short", 31), ("lewis-black", "Black on Broadway", 39),
  ("rob-delaney", "Live at the Bowery Ballroom", 40), ("reggie-watts", "Why Shit So Crazy", 42),
  ("wanda-sykes", "Ima Be Me", 33), ("robin-williams", "Live at the Met", 35),
  ("patrice-o-neal", "Elephant in the Room", 37), ("kevin-hart", "Seriously Funny", 38),
  ("denis-leary", "No Cure for Cancer", 41), ("dennis-miller", "Mr Miller Goes to Washington", 44),
  ("david-cross", "Let America Laugh", 23), ("janeane-garofalo", "HBO Comedy Half Hour", 10),
  ("paula-poundstone", "Cops Cats and Stuff", 9), ("roseanne-barr", "The Roseanne Barr Show", 5),
  ("whoopi-goldberg", "Direct From Broadway", 16), ("steve-martin", "A Wild and Crazy Guy", 8),
  ("zach-galifianakis", "Live at the Purple Onion", 15), ("sam-kinison", "Breaking the Rules", 16)],
 "paste-2017": [
  ("maria-bamford", "Old Baby", 1), ("michelle-wolf", "Nice Lady", 2),
  ("chris-gethard", "Career Suicide", 3), ("hasan-minhaj", "Homecoming King", 4),
  ("patton-oswalt", "Annihilation", 5), ("mike-birbiglia", "Thank God for Jokes", 7),
  ("tiffany-haddish", "She Ready", 8), ("neal-brennan", "3 Mics", 13),
  ("jim-gaffigan", "Cinco", 14), ("dave-chappelle", "Age of Spin", 20)],
}


# Known specials per comic for direct IMDb matching (no transcript needed).
# Titles are release titles; matcher enforces comedian-name-in-title +
# non-surname keyword overlap (same strict rule as critic matching).
KNOWN_SPECIALS = {
 "jimmy-carr": ["Jimmy Carr: Comedian", "Jimmy Carr: Making People Laugh",
                "Jimmy Carr: Being Funny", "Jimmy Carr: Laughing and Joking"],
 "sean-lock": ["Sean Lock: Live!", "Sean Lock: Lockipedia", "Sean Lock: Purple Van Man"],
 "lee-mack": ["Lee Mack: Live", "Lee Mack: Going Out"],
 "greg-davies": ["Greg Davies: Firing Cheeseballs at a Dog",
                 "Greg Davies: You Magnificent Beast", "Greg Davies: Full Fat Legend"],
}



# C4 100 Greatest Stand-Ups (Channel 4, 2007, public vote).
# https://www.comedy.co.uk/tv/100_greatest_stand_ups/episodes/1/1/
# Fourth critics leg (UK-weighted). Cosby #96 deliberately absent.
C4 = {
 "peter-kay": 2,
 "harry-hill": 5,
 "bill-bailey": 7,
 "victoria-wood": 8,
 "jack-dee": 13,
 "woody-allen": 14,
 "jerry-sadowitz": 15,
 "al-murray": 16,
 "alexei-sayle": 18,
 "les-dawson": 19,
 "jasper-carrott": 20,
 "ben-elton": 21,
 "jo-brand": 22,
 "lee-evans": 23,
 "steve-coogan": 25,
 "bernard-manning": 29,
 "bob-monkhouse": 31,
 "roy-chubby-brown": 33,
 "david-baddiel": 34,
 "denis-leary": 35,
 "mark-thomas": 36,
 "jim-davidson": 37,
 "andrew-dice-clay": 38,
 "jenny-eclair": 39,
 "sean-hughes": 40,
 "johnny-vegas": 43,
 "paul-ogrady": 45,
 "rob-newman": 46,
 "jackie-mason": 47,
 "ken-dodd": 48,
 "graham-norton": 49,
 "bob-hope": 50,
 "lenny-henry": 51,
 "tommy-cooper": 53,
 "julian-clary": 57,
 "dave-spikey": 58,
 "omid-djalili": 60,
 "phill-jupitus": 61,
 "alan-davies": 63,
 "rhona-cameron": 65,
 "chris-addison": 66,
 "mike-reid": 67,
 "lee-hurst": 68,
 "jethro": 70,
 "john-thomson": 71,
 "frankie-howerd": 72,
 "ed-byrne": 73,
 "dave-gorman": 75,
 "arthur-smith": 76,
 "chic-murray": 77,
 "frank-carson": 79,
 "freddie-starr": 81,
 "barry-humphries": 82,
 "tommy-trinder": 83,
 "harry-enfield": 85,
 "reginald-d-hunter": 87,
 "ronnie-corbett": 88,
 "joe-pasquale": 90,
 "paul-merton": 92,
 "rik-mayall": 93,
 "ardal-ohanlon": 94,
 "alan-carr": 98,
 "patrick-kielty": 99,
 "tim-vine": 100,
}
UK_META = {
 "al-murray": ('Al Murray', "nineties", "uk"),
 "alan-carr": ('Alan Carr', "aughts", "uk"),
 "alan-davies": ('Alan Davies', "nineties", "uk"),
 "alexei-sayle": ('Alexei Sayle', "eighties-boom", "uk"),
 "andrew-dice-clay": ('Andrew Dice Clay', "eighties-boom", "us"),
 "ardal-ohanlon": ("Ardal O'Hanlon", "nineties", "ireland"),
 "arthur-smith": ('Arthur Smith', "eighties-boom", "uk"),
 "barry-humphries": ('Barry Humphries', "pioneers", "australia"),
 "ben-elton": ('Ben Elton', "eighties-boom", "uk"),
 "bernard-manning": ('Bernard Manning', "seventies", "uk"),
 "bill-bailey": ('Bill Bailey', "nineties", "uk"),
 "bob-hope": ('Bob Hope', "pioneers", "us"),
 "bob-monkhouse": ('Bob Monkhouse', "pioneers", "uk"),
 "chic-murray": ('Chic Murray', "pioneers", "uk"),
 "chris-addison": ('Chris Addison', "aughts", "uk"),
 "dave-gorman": ('Dave Gorman', "aughts", "uk"),
 "dave-spikey": ('Dave Spikey', "aughts", "uk"),
 "david-baddiel": ('David Baddiel', "nineties", "uk"),
 "denis-leary": ('Denis Leary', "nineties", "us"),
 "ed-byrne": ('Ed Byrne', "nineties", "uk"),
 "frank-carson": ('Frank Carson', "seventies", "uk"),
 "frankie-howerd": ('Frankie Howerd', "pioneers", "uk"),
 "freddie-starr": ('Freddie Starr', "seventies", "uk"),
 "graham-norton": ('Graham Norton', "nineties", "uk"),
 "harry-enfield": ('Harry Enfield', "eighties-boom", "uk"),
 "harry-hill": ('Harry Hill', "nineties", "uk"),
 "jack-dee": ('Jack Dee', "nineties", "uk"),
 "jackie-mason": ('Jackie Mason', "pioneers", "us"),
 "jasper-carrott": ('Jasper Carrott', "seventies", "uk"),
 "jenny-eclair": ('Jenny Eclair', "nineties", "uk"),
 "jerry-sadowitz": ('Jerry Sadowitz', "eighties-boom", "uk"),
 "jethro": ('Jethro', "eighties-boom", "uk"),
 "jim-davidson": ('Jim Davidson', "seventies", "uk"),
 "jo-brand": ('Jo Brand', "nineties", "uk"),
 "joe-pasquale": ('Joe Pasquale', "eighties-boom", "uk"),
 "john-thomson": ('John Thomson', "nineties", "uk"),
 "johnny-vegas": ('Johnny Vegas', "nineties", "uk"),
 "julian-clary": ('Julian Clary', "eighties-boom", "uk"),
 "ken-dodd": ('Ken Dodd', "pioneers", "uk"),
 "lee-evans": ('Lee Evans', "nineties", "uk"),
 "lee-hurst": ('Lee Hurst', "nineties", "uk"),
 "lenny-henry": ('Lenny Henry', "eighties-boom", "uk"),
 "les-dawson": ('Les Dawson', "pioneers", "uk"),
 "mark-thomas": ('Mark Thomas', "nineties", "uk"),
 "mike-reid": ('Mike Reid', "seventies", "uk"),
 "omid-djalili": ('Omid Djalili', "aughts", "uk"),
 "patrick-kielty": ('Patrick Kielty', "nineties", "uk"),
 "paul-merton": ('Paul Merton', "eighties-boom", "uk"),
 "paul-ogrady": ("Paul O'Grady", "nineties", "uk"),
 "peter-kay": ('Peter Kay', "aughts", "uk"),
 "phill-jupitus": ('Phill Jupitus', "nineties", "uk"),
 "reginald-d-hunter": ('Reginald D Hunter', "nineties", "uk"),
 "rhona-cameron": ('Rhona Cameron', "nineties", "uk"),
 "rik-mayall": ('Rik Mayall', "eighties-boom", "uk"),
 "rob-newman": ('Rob Newman', "nineties", "uk"),
 "ronnie-corbett": ('Ronnie Corbett', "pioneers", "uk"),
 "roy-chubby-brown": ('Roy Chubby Brown', "seventies", "uk"),
 "sean-hughes": ('Sean Hughes', "nineties", "uk"),
 "steve-coogan": ('Steve Coogan', "nineties", "uk"),
 "tim-vine": ('Tim Vine', "nineties", "uk"),
 "tommy-cooper": ('Tommy Cooper', "pioneers", "uk"),
 "tommy-trinder": ('Tommy Trinder', "pioneers", "uk"),
 "victoria-wood": ('Victoria Wood', "eighties-boom", "uk"),
 "woody-allen": ('Woody Allen', "pioneers", "us"),
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


STOP = set("the a an and or of to in on for with live special show evening night hour half presents at from by".split())


def _load_index():
    import gzip
    sys.path.insert(0, str(HERE))
    from enrich_ratings import load_comedy_index
    ratings = {}
    with gzip.open("/tmp/title.ratings.tsv.gz", "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 3:
                try:
                    ratings[p[0]] = (float(p[1]), int(p[2]))
                except ValueError:
                    continue
    return load_comedy_index(ratings)


def _match_one(slug: str, title: str, idx: list) -> dict | None:
    """Strict single-title IMDb match (surname + non-surname keyword)."""
    gpath = COMEDIANS / slug / "comedian-graph.json"
    if not gpath.exists():
        return None
    g = json.loads(gpath.read_text())
    surname = norm((g.get("name") or slug).split()[-1])
    keys = {w for w in re.split(r"[^a-z]+", title.lower())
            if len(w) > 2 and w not in STOP}
    keys -= {norm((g.get("name") or slug).split()[0]), surname}
    if not keys:
        return None
    best = None
    for e in idx:
        pt = (e["primary"] + " " + e["original"]).lower()
        if surname and surname not in norm(pt):
            continue
        hit = {w for w in re.split(r"[^a-z]+", pt)
               if len(w) > 2 and w not in STOP}
        ov = len(keys & hit)
        if not ov:
            continue
        score = (ov, e["votes"])
        if best is None or score > best[0]:
            best = (score, e)
    return best[1] if best else None


def _attach(slug: str, title: str, e: dict, source: str) -> bool:
    gpath = COMEDIANS / slug / "comedian-graph.json"
    g = json.loads(gpath.read_text())
    sp = g.setdefault("specials_rated", [])
    if any(s.get("imdb_id") == e["tconst"] for s in sp):
        return False
    sp.append({"special": e["primary"], "year": e["year"],
               "imdb_id": e["tconst"], "imdb_rating": e["rating"],
               "imdb_votes": e["votes"], "source": source,
               "standout": False})
    gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
    return True


def match_imdb() -> None:
    """Match unmatched critic specials against the local IMDb comedy index.

    Rules (binding): comedian SURNAME must appear in the title
    (comedian-name-in-title — the Pixar-Up rule); >=1 significant keyword
    from the critic title must match; best = most overlap, tiebreak votes.
    Hits append specials_rated entries (source-tagged, standout False) so
    the audience leg, specials board, and PEOPLE'S all refresh on rebuild.
    """
    idx = _load_index()
    d = json.loads((OUT / "critic_specials.json").read_text())
    unmatched = [u for u in d["unmatched"] if u["why"] == "no-imdb-match"]
    n_hit = 0
    for u in unmatched:
        e = _match_one(u["comedian"], u["title"], idx)
        if e is None:
            continue
        if _attach(u["comedian"], u["title"], e, f"critic-list:{u['list']}"):
            n_hit += 1
            print(f"  IMDb {e['rating']} ({e['votes']}v): {u['comedian']} — {e['primary'][:50]}")
    print(f"imdb-matched {n_hit}/{len(unmatched)} critic specials "
          f"(rebuild boards with rate.py)")


def match_known() -> None:
    """Direct known-title matching (KNOWN_SPECIALS — no transcript needed).

    Same strict rule as critic matching. For comics whose specials never
    entered via transcripts (UK catalogue gaps etc.).
    """
    idx = _load_index()
    n_hit = n_miss = 0
    for slug, titles in sorted(KNOWN_SPECIALS.items()):
        for title in titles:
            e = _match_one(slug, title, idx)
            if e is None:
                print(f"  MISS {slug}: {title[:50]}")
                n_miss += 1
                continue
            if _attach(slug, title, e, "known-title"):
                print(f"  IMDb {e['rating']} ({e['votes']}v): {slug} — {e['primary'][:50]}")
                n_hit += 1
    print(f"known-title matched {n_hit} ({n_miss} missed)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-draft", action="store_true")
    ap.add_argument("--match-imdb", action="store_true",
                    help="match unmatched critic specials to local IMDb index")
    ap.add_argument("--match-known", action="store_true",
                    help="match KNOWN_SPECIALS titles to local IMDb index")
    args = ap.parse_args()
    sys.path.insert(0, str(HERE))
    from exclude import EXCLUDED

    # 1. Paste ranks into recognition (+ drafts)
    n_rank, n_draft = 0, 0
    for slug, rank in sorted(PASTE.items()):
        if slug in EXCLUDED:
            continue
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if gpath.exists():
            g = json.loads(gpath.read_text())
            rec = g.setdefault("recognition", {})
            if rec.get("paste_2017") != rank:
                rec["paste_2017"] = rank
                gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
            n_rank += 1
    # 1b. C4 ranks into recognition (+ UK legend drafts; Cosby absent)
    for slug, rank in sorted(C4.items()):
        if slug in EXCLUDED:
            continue
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if gpath.exists():
            g = json.loads(gpath.read_text())
            rec = g.setdefault("recognition", {})
            if rec.get("c4_2007") != rank:
                rec["c4_2007"] = rank
                gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
            n_rank += 1
    if not args.no_draft:
        for slug, (name, gen, note) in sorted(DRAFTS.items()):
            if slug in EXCLUDED:
                continue
            gpath = COMEDIANS / slug / "comedian-graph.json"
            if gpath.exists():
                g = json.loads(gpath.read_text())
                if g.get("tier") == "king":
                    g.setdefault("recognition", {})["paste_2017"] = PASTE[slug]
                    gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
                    n_rank += 1
                continue
            g = {"schema": "pogtown.comedian.v1", "comedian_id": slug,
                 "name": name, "tier": "king", "region": "us",
                 "generation": {"id": gen},
                 "recognition": {"paste_2017": PASTE[slug]},
                 "identity": {"deal": "", "operator_priors": {}},
                 "known_bits": [], "essay_seeds": [],
                 "provenance": {"tier": "king",
                                "rule": "Paste-2017 legend: established by list inclusion",
                                "note": note},
                 "version": 1, "created": "2026-10-17",
                 "annotator": "critic_lists.py"}
            (COMEDIANS / slug).mkdir(exist_ok=True)
            gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
            n_draft += 1
    if not args.no_draft:
        for slug, (name, gen, region) in sorted(UK_META.items()):
            if slug in EXCLUDED or slug in PASTE:
                continue
            gpath = COMEDIANS / slug / "comedian-graph.json"
            if gpath.exists():
                continue
            g = {"schema": "pogtown.comedian.v1", "comedian_id": slug,
                 "name": name, "tier": "king", "region": region,
                 "generation": {"id": gen},
                 "recognition": {"c4_2007": C4[slug]},
                 "identity": {"deal": "", "operator_priors": {}},
                 "known_bits": [], "essay_seeds": [],
                 "provenance": {"tier": "king",
                                "rule": "C4-2007 ranked: established by list inclusion",
                                "note": "UK canon onboarding (owner goal: UK scene)"},
                 "version": 1, "created": "2026-10-17",
                 "annotator": "critic_lists.py"}
            (COMEDIANS / slug).mkdir(exist_ok=True)
            gpath.write_text(json.dumps(g, indent=2) + "\n", encoding="utf-8")
            n_draft += 1
    print(f"paste/c4 ranks: {n_rank} set, {n_draft} legend drafts")

    # 2. specials corroboration: match critic entries to specials.json
    specials = json.loads((OUT / "specials.json").read_text())
    by_comic: dict[str, list] = {}
    for s in specials:
        by_comic.setdefault(s.get("comedian_id", ""), []).append(s)
    cites: dict[str, list] = {}
    unmatched = []
    for list_id, entries in SPECIALS.items():
        for slug, title, rank in entries:
            if slug in EXCLUDED or "cosby" in slug:
                unmatched.append((list_id, slug, title, "skipped"))
                continue
            cands = by_comic.get(slug, [])
            hit = None
            nt = norm(title)
            for s in cands:
                st = norm(s.get("special", ""))
                if nt and (nt in st or st in nt):
                    hit = s
                    break
            if hit is None:
                for s in cands:
                    st = norm(s.get("special", ""))
                    if nt[:8] and nt[:8] in st:
                        hit = s
                        break
            if hit is None:
                unmatched.append((list_id, slug, title, "no-imdb-match"))
                continue
            key = f"{slug}::{hit.get('special')}"
            cites.setdefault(key, []).append(
                {"list": list_id, "rank": rank,
                 "comedian": hit.get("comedian"), "special": hit.get("special"),
                 "year": hit.get("year"), "wr": hit.get("wr")})
    board = []
    for key, cl in cites.items():
        board.append({"key": key, "comedian": cl[0]["comedian"],
                      "special": cl[0]["special"], "year": cl[0].get("year"),
                      "wr": cl[0].get("wr"), "n_lists": len(cl),
                      "best_rank": min(c["rank"] for c in cl),
                      "cites": cl})
    board.sort(key=lambda r: (-r["n_lists"], r["best_rank"]))
    (OUT / "critic_specials.json").write_text(json.dumps({
        "note": "GOAT-Special third leg (ENDPOINTS #2): critic-list citations "
                "per special (RS2015/Vulture2014/Flavorwire2013/Paste2017). "
                "Ranked by citation count, then best rank. Cosby skipped.",
        "n_cited": len(board), "n_unmatched": len(unmatched),
        "board": board,
        "unmatched": [{"list": l, "comedian": c, "title": t, "why": w}
                      for l, c, t, w in unmatched[:60]],
    }, indent=1))
    print(f"critic specials: {len(board)} cited, {len(unmatched)} unmatched")
    for r in board[:10]:
        print(f"  {r['n_lists']} lists best#{r['best_rank']}  "
              f"{str(r['comedian'])[:20]:20} {str(r['special'])[:40]}")
    if args.match_imdb:
        match_imdb()
    if args.match_known:
        match_known()


if __name__ == "__main__":
    main()
