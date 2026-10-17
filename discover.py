#!/usr/bin/env python3
"""DISCOVER — small-comic fountain: registry uploads -> indie auto-drafts.

The discovery half of the indie loop. Finds working comics too small for
listicles, drafts them as tier-indie graphs, queues their sets for caption
pulls. rate.py --check picks up drafts automatically (DISCOVERY coverage
+ provisional headline). Humans promote to king. Nothing here guesses.

SOURCES (no-search law): uploads playlists of multi-comic registry
channels only — kill-tony (weekly episodes + guests = the fountain),
xiaoguo, basketmouth, netflix-is-a-joke, team-coco, tonight-show.
PlaylistItems newest-first, incremental via state (1 unit/page + stats
for NEW videos only). A full KT rescan (~2000 vids) costs ~45 units;
incremental weeks cost ~3. NEVER search.list (100 units + guesses).

NAME RULE (binding): full names only. Two-word Title Case segments draft
automatically; single names queue as needs-full-name, never drafted.

PIPELINE (weekly cadence, cron-safe):
  discover.py --scan          registry uploads -> drafts + queue.json (~50u)
  discover.py --fetch-sets    queue videoIds -> harvest_captions (InnerTube,
                              zero API quota) -> scribe/ sets
  indie.py --score            gates over material -> theory_score
  indie.py --match-greats     latent-space nearest kings
  rate.py --check             DISCOVERY rating + provisional headline
  pulse.py --report           velocity -> spotlight.json week boards

CHANNEL LINKING (the traffic loop — why we exist for these comics):
  Before a comic is truly onboarded, find their PERSONAL channel and link
  it: our pages drive traffic to them; their uploads feed our pulse.
  discover.py --link-channels resolves handles WITHOUT search:
    (1) @handles in evidence TITLES (DTC puts "@SamBiruComedy" in titles),
    (2) @handles + /channel/ links in evidence video DESCRIPTIONS
        (videos.list snippet, batched — costs ~1 unit/50, no search),
    (3) verify via forHandle/channels.list (1 unit): channel title must
        contain the comic's name (kills squat channels); ties -> max subs.
  Verified links register in channels.json[slug] + graph.youtube_channel{}
  {id, handle, subs, source}. Harvester then pulls their sets; pulse
  tracks velocity. forUsername also works for legacy /user/ names
  (1 unit — this is how Angel Comedy's own channel confirmed).

VENUE ROSTERS (static HTML mining, zero quota):
  discover.py --rosters fetches venue roster pages (proven: Angel Comedy
  /comedians/ — 15 regulars as ## headers) and drafts unknowns with
  source venue-roster:<venue> (a residency is stronger evidence than a
  clip). Winners/lineups behind JS walls or Facebook login are skipped
  and noted, never scraped with hacks.

Usage:
  python3 discover.py --dry-run     # zero quota: extraction over local titles
  python3 discover.py --scan        # live incremental scan (quota-light)
  python3 discover.py --fetch-sets  # captions for queued evidence videos
  python3 discover.py --link-channels  # resolve + verify personal channels
  python3 discover.py --rosters     # mine venue roster pages

State: data/discovery/state.json (per-channel last seen).
Queue: data/discovery/queue.json (evidence + status per candidate).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
COMEDIANS = HERE / "comedians"
DATA = HERE / "data" / "youtube"
DISC = HERE / "data" / "discovery"
DISC.mkdir(parents=True, exist_ok=True)
STATE = DISC / "state.json"
QUEUE = DISC / "queue.json"

try:
    from exclude import EXCLUDED
except ImportError:
    EXCLUDED = set()

sys.path.insert(0, str(HERE))
from indie import _blank_indie

API = "https://www.googleapis.com/youtube/v3"
# multi-comic fountains (registry keys). Talk/panel channels (team-coco,
# tonight-show, netflix-is-a-joke) are SETS sources for the harvester, NOT
# name mines: their guests are actors, movies, and game words ("Trap Door,
# Escalator, Stairs, Elevator" drafted as comics on 2026-10-17 — never again).
# Verified unknown-fountains (channel IDs confirmed via channels.list /
# video snippet, 2026-10-17; handles resolved via forHandle, 1 unit each —
# registry administration, never search):
#   kill-tony (bucket minutes + Behind the Tape guests),
#   dry-bar (debut/unknown full specials),
#   just-for-laughs (annual New Faces showcases),
#   dont-tell-comedy (up-and-comers + competition pipeline, 2.4M subs
#     — title @handles resolve personal channels, e.g. Sam Biru 374 subs),
#   frog-and-bucket (weekly new acts; ROAST-TITLES EXCLUDED by ROAST_RE),
#   angel-comedy (free nightly + New Act Showcase; own channel confirmed
#     via forUsername — roster page also mined, see ROSTERS),
#   xiaoguo, basketmouth (regional scenes).
FOUNTAINS = ["kill-tony", "dry-bar", "just-for-laughs", "dont-tell-comedy",
             "frog-and-bucket", "angel-comedy", "xiaoguo", "basketmouth"]
# Static venue roster pages: venue -> url. Residency = strong evidence.
# Winners/lineups behind JS calendars or Facebook login: skipped, noted.
ROSTERS = {
    "angel-comedy": "https://www.angelcomedy.co.uk/comedians/",
    # On The Mic (onthemic.co.uk): 1707-comedian Edinburgh directory.
    # A-Z index (?letter=X) + per-comic pages (/comedians_list/<slug>/)
    # carrying bio, TV/panel credits, representation, official websites.
    # Link-label extraction (names are link text — no NLP, near-zero junk).
    # Use: coverage cross-check (who are we missing?), websites, credits.
    "on-the-mic": ["https://www.onthemic.co.uk/comedians/?letter=" + c
                   for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
    # UNTESTED (fetch + verify before wiring): topsecretcomedy lineups,
    # komedia Krater lineups, just-the-tonic new-act nights.
}
# NO ROASTS (owner 2026-10-17): standup sets only. Roast battles, beefs,
# insults, and heckler clips are a different art form with different
# mechanics — they never enter discovery. 13 Manchester roast-battle
# drafts purged on sight; this filter prevents recurrence. (The roast
# humor_type/mode stays for kings — this is a discovery-scope rule.)
ROAST_RE = re.compile(r"roast|battle|beef|insult|heckler|destroyed|"
                      r"\bowns\b|owned|clapback|rap battle", re.I)
SHOWNAME_BLOCK = {"behind-the-tape", "behind-tape", "cold-open", "cold-openers",
                  "secret-show", "open-mic", "new-minutes", "golden-ticket",
                  "rabbit-hole", "just-laughs", "new-faces", "live-sessions",
                  "full-special", "secret-sets", "video-channel",
                  "polite-heckler", "peter-kay", "peter-kay-frog",
                  "angel-club-london", "angel-comedy-club"}
# Channel IDs proven WRONG (namesake collisions caught on audit, 2026-10-17):
# UCn7zFtvhBRfUpJcW_6fU0mA = LIAM NELSON the DJ (EDM tracks), not the comic.
# link/guess/audit skip these permanently.
COLLISION_BLOCK = {"UCn7zFtvhBRfUpJcW_6fU0mA"}
# Nav-boilerplate link texts that match the name regex but aren't people
# (2026-10-17: "More Info", "On The Mic", "Print Interviews" drafted as
# comics from OTM pages — the href filter passes since they link to real
# comic pages; the TEXT is boilerplate).
NAVTEXT_BLOCK = {"more info", "on the mic", "print interviews", "full bio",
                 "read more", "view all", "watch comedy", "more details",
                 "click here", "see more"}

SHOW_RE = re.compile(r"#\d{2,4}|\bkt\b|kill.?tony|\bw/|ft\.|guests?|"
                      r"\blive\b|episode|\bep\b|\bvs\.?|battle|finals?|"
                      r"semifinal|comedy night|new faces|secret sets?|"
                      r"full (comedy )?special|debut", re.I)
BOILER = re.compile(
    r"(kill\s*tony|kt\b|episode|ep\.?|live|austin|comedy\s*mothership|"
    r"netflix\s*is\s*a\s*joke|tonight\s*show|conan|xiaoguo|stand[\s-]?up|"
    r"comedy|special|full|clip|shorts|#\S+|\b\d{3,4}\b|\(.*?\)|\[.*?\])",
    re.I)


def _key() -> str:
    k = os.getenv("YOUTUBE_DATA_API_KEY", "").strip()
    if k:
        return k
    env = HERE / ".env"
    if env.exists():
        for ln in env.read_text().splitlines():
            if ln.startswith("YOUTUBE_DATA_API_KEY="):
                return ln.split("=", 1)[1].strip()
    return ""


def _get(url: str) -> dict:
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    return {}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)


def names_from_title(title: str) -> list[str]:
    """Full person names from a show title. Conservative by design.

    Marker-adjacency: in "Bit Title | NAME FULL SPECIAL" formats, the
    name sits in the marker's segment — bit-title segments never yield
    names ("Rabbit Hole" drafted as a comic on 2026-10-17, never again).
    """
    segs = re.split(r"\s+-\s+|[–—|:~#@]", title)
    # NOTE 2026-10-17: bare-hyphen split corrupted hyphenated surnames
    # ("Jade Catta-Preta" -> junk slug "jade-catta"). Split on SPACED
    # hyphens only; em/en dashes are never in names.
    if re.search(r"full (comedy )?special", title, re.I):
        segs = [s for s in segs
                if re.search(r"full (comedy )?special", s, re.I)] or segs
    # multi-guest separators inside segments
    parts = []
    for s in segs:
        parts += re.split(r",|\&|\+|\bw/|\bft\.?|\bvs\.?|\band\b", s)
    out = []
    for s in parts:
        s = BOILER.sub(" ", s)
        s = re.sub(r"\s+", " ", s).strip(" ,.!?'\"")
        words = [w for w in s.split() if w and w[0].isupper()]
        # person-name shape: 2-3 capitalized words, no digits, len>4
        if 2 <= len(words) <= 3 and len(s) > 4 and not re.search(r"\d", s):
            if all(re.match(r"^[A-Z][a-z'-]+$", w) for w in words):
                out.append(" ".join(words))
    # singles noted separately (never drafted)
    singles = []
    for s in parts:
        s = BOILER.sub(" ", s).strip(" ,.!?'\"")
        if re.match(r"^[A-Z][a-z'-]+$", s or ""):
            singles.append(s)
    return sorted(set(out)), sorted(set(singles))


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def load_queue() -> dict:
    try:
        return json.loads(QUEUE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def existing_slugs() -> set[str]:
    return {d.name for d in COMEDIANS.iterdir()
            if (d / "comedian-graph.json").exists()}


# Source -> scene region (conservative: only where the source IS the
# scene. Festival/showcase sources are international by format and map to
# nothing — Edinburgh nominees come from three continents. Stored with
# method venue-scene so origin-research can overwrite without conflict.)
REGION_BY_SRC = {
    "venue-roster:angel-comedy": "uk",
    "youtube-uploads:kill-tony": "us",
    "youtube-uploads:dry-bar": "us",
    "youtube-uploads:dont-tell-comedy": "us",
    "youtube-uploads:xiaoguo": "china",
    "youtube-uploads:basketmouth": "nigeria",
    "timeout-2026": "us", "timeout-2026-nyc-chi-la": "us",
}


def draft_indie(slug: str, name: str, evidence: dict, src: str) -> bool:
    if slug in EXCLUDED or (COMEDIANS / slug).exists():
        return False
    d = COMEDIANS / slug
    d.mkdir(exist_ok=True)
    g = _blank_indie(slug)
    g["name"] = name
    g["created"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    g["annotator"] = "discover.py"
    # src arrives bare ("kill-tony") from scans, prefixed from rosters —
    # normalize once (2026-10-17: roster drafts were double-prefixed).
    tag = src if ":" in src else f"youtube-uploads:{src}"
    g["discovery"] = {"discovered_from": [tag],
                      "discovery_note": f"Mined from {tag} "
                                        f"(registry/curated, no search).",
                      "evidence": [evidence],
                      "subs": "unknown (performer channel unregistered)"}
    if tag in REGION_BY_SRC:
        g["region"] = REGION_BY_SRC[tag]
        g["discovery"]["region_method"] = "venue-scene (overwrite on origin evidence)"
    (d / "comedian-graph.json").write_text(json.dumps(g, indent=1) + "\n",
                                           encoding="utf-8")
    return True


def backfill_regions() -> None:
    """One pass: region for region-less indies from discovery source.

    Fixes the 2026-10-17 double-prefix mangling, applies REGION_BY_SRC,
    stamps region_method. Never overwrites existing regions.
    """
    n = 0
    for d in sorted(COMEDIANS.iterdir()):
        gpath = d / "comedian-graph.json"
        if not gpath.exists() or d.name in EXCLUDED:
            continue
        try:
            g = json.loads(gpath.read_text())
        except json.JSONDecodeError:
            continue
        if g.get("tier") != "indie":
            continue
        disc = g.get("discovery") or {}
        srcs = disc.get("discovered_from") or []
        fixed = [s.replace("youtube-uploads:venue-roster:",
                           "venue-roster:") for s in srcs]
        if fixed != srcs:
            disc["discovered_from"] = fixed
            g["discovery"] = disc
        if g.get("region"):
            if fixed != srcs:
                gpath.write_text(json.dumps(g, indent=1) + "\n",
                                 encoding="utf-8")
            continue
        hit = next((REGION_BY_SRC[s] for s in fixed if s in REGION_BY_SRC),
                   None)
        if hit:
            g["region"] = hit
            g["discovery"] = {**disc, "region_method":
                              "venue-scene (overwrite on origin evidence)"}
            gpath.write_text(json.dumps(g, indent=1) + "\n",
                             encoding="utf-8")
            n += 1
    print(f"regions backfilled: {n}")


def process_videos(videos: list[dict], src: str, queue: dict,
                   known: set[str]) -> tuple[int, int]:
    """Two-stage: collect name candidates with evidence, then draft.

    DRAFT RULE: full name (2-3 words) AND (show-episode title OR seen in
    >=2 videos this batch). Recurrence kills bit-title junk ("Baby Cobra"
    airs once; working comics recur). Singles never draft (binding rule).
    """
    cands: dict[str, dict] = {}
    for v in videos:
        title = v.get("title", "")
        if ROAST_RE.search(title):
            continue  # no roasts, ever (discovery-scope rule)
        show = bool(SHOW_RE.search(title))
        if not show:
            continue  # clip/special titles never yield names (junk guard)
        full, singles = names_from_title(title)
        for name in full:
            slug = slugify(name)
            if not slug:
                continue
            e = cands.setdefault(slug, {"name": name, "n": 0, "show": False,
                                        "ev": None})
            e["n"] += 1
            e["show"] = e["show"] or show
            if e["ev"] is None:
                e["ev"] = {"videoId": v.get("videoId"), "title": title,
                           "views": v.get("views"),
                           "publishedAt": v.get("publishedAt")}
        for s in singles:
            slug = slugify(s)
            if not slug or slug in known or slug in queue:
                continue
            queue[slug] = {"name": s, "status": "needs-full-name",
                           "evidence": {"videoId": v.get("videoId"),
                                        "title": title},
                           "src": src}
    drafted, queued = 0, 0
    for slug, e in sorted(cands.items()):
        if slug in known or slug in queue or slug in SHOWNAME_BLOCK:
            continue
        if DUO_RE.search(slug):
            continue
        if not (e["show"] or e["n"] >= 2):
            continue
        if draft_indie(slug, e["name"], e["ev"], src):
            drafted += 1
            known.add(slug)
        queue[slug] = {"name": e["name"], "status": "drafted",
                       "evidence": e["ev"], "src": src,
                       "seen_in_batch": e["n"], "show_title": e["show"],
                       "first_seen": datetime.now(timezone.utc)
                       .strftime("%Y-%m-%d")}
        queued += 1
    return drafted, queued


def dry_run() -> None:
    """Zero quota: extraction over locally stored titles."""
    titles = []
    for p in sorted(DATA.glob("*.json")):
        try:
            d = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for r in d.get("rows", []):
            if r.get("title"):
                titles.append({"title": r["title"],
                               "videoId": r.get("videoId"),
                               "views": r.get("views"),
                               "publishedAt": r.get("publishedAt")})
    print(f"{len(titles)} local titles (zero quota)")
    queue: dict = {}
    d, q = process_videos(titles, "local-titles", queue, existing_slugs())
    print(f"would draft {d} indies, queue {q} candidates")
    full = sorted(s for s, e in queue.items() if e["status"] == "drafted")
    print("draftable full names:", ", ".join(full[:20]))
    if len(full) > 20:
        print(f"  ... +{len(full) - 20} more (dry run: nothing written)")


def scan(cap: int = 200) -> None:
    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")
    reg = json.loads((HERE / "data" / "channels.json").read_text())
    state, queue, known = load_state(), load_queue(), existing_slugs()
    for src in FOUNTAINS:
        chs = [c for c in reg.get(src, []) if c]
        if not chs:
            continue
        for ch in chs:
            try:
                d = _get(f"{API}/channels?part=contentDetails,statistics"
                         f"&id={ch}&key={key}")
                it = (d.get("items") or [None])[0]
                if not it:
                    continue
                pl = it["contentDetails"]["relatedPlaylists"]["uploads"]
                last = (state.get(src) or {}).get("last_videoId", "")
                vids, token, seen_last = [], "", False
                while len(vids) < cap:
                    url = (f"{API}/playlistItems?part=contentDetails"
                           f"&maxResults=50&playlistId={pl}&key={key}"
                           + (f"&pageToken={token}" if token else ""))
                    pg = _get(url)
                    batch = [i["contentDetails"]["videoId"]
                             for i in pg.get("items", [])
                             if i.get("contentDetails", {}).get("videoId")]
                    for vid in batch:
                        if vid == last:
                            seen_last = True
                            break
                        vids.append(vid)
                    token = pg.get("nextPageToken", "")
                    if seen_last or not token:
                        break
                    time.sleep(0.2)
                print(f"{src}: {len(vids)} new videos since {last[:8] or 'ever'}")
                if not vids:
                    continue
                stats = {}
                for i in range(0, len(vids), 50):
                    u = (f"{API}/videos?part=statistics,snippet&id="
                         + ",".join(vids[i:i + 50]) + f"&key={key}")
                    for it2 in _get(u).get("items", []):
                        sn, stt = it2.get("snippet", {}), it2.get("statistics", {})
                        stats[it2["id"]] = {
                            "videoId": it2["id"],
                            "title": sn.get("title", ""),
                            "views": int(stt.get("viewCount", 0) or 0),
                            "publishedAt": (sn.get("publishedAt") or "")[:10]}
                    time.sleep(0.3)
                ordered = [stats[v] for v in vids if v in stats]
                dr, q = process_videos(ordered, src, queue, known)
                print(f"  drafted {dr}, queued {q}")
                if ordered:
                    state[src] = {"last_videoId": ordered[0]["videoId"],
                                  "scanned_at": datetime.now(timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ")}
                QUEUE.write_text(json.dumps(queue, indent=1))
                STATE.write_text(json.dumps(state, indent=1))
            except Exception as e:
                print(f"  {src}/{ch} fail: {type(e).__name__} {str(e)[:100]}")
    print(f"\nqueue: {len(queue)} candidates "
          f"({sum(1 for e in queue.values() if e['status'] == 'drafted')} drafted)")


def fetch_sets(limit: int = 10) -> None:
    """InnerTube captions for queued evidence videos (zero API quota)."""
    queue = load_queue()
    todo = [(s, e) for s, e in queue.items()
            if e["status"] == "drafted" and e.get("evidence", {}).get("videoId")]
    print(f"{len(todo)} queued for sets")
    n = 0
    for slug, e in todo[:limit]:
        vid = e["evidence"]["videoId"]
        url = f"https://www.youtube.com/watch?v={vid}"
        r = subprocess.run(
            [sys.executable, str(HERE / "harvest_captions.py"), url,
             "--comedian", slug, "--title", e["evidence"].get("title", "")[:60]],
            capture_output=True, text=True, timeout=600)
        ok = r.returncode == 0 and "scribe" in (r.stdout + r.stderr).lower()
        print(f"  {'OK ' if ok else 'MISS'} {slug} {vid}")
        if ok:
            e["status"] = "sets-fetched"
            n += 1
    QUEUE.write_text(json.dumps(queue, indent=1))
    print(f"sets fetched for {n}")


HANDLE_RE = re.compile(r"@([\w.]{3,40})")
# Duos/troupes are not solo profiles (schema is per-comedian). Sklar
# Brothers drafted 2026-10-17, purged same day.
DUO_RE = re.compile(r"brothers|sisters|twins|\btrio\b|\bduo\b", re.I)
CHURL_RE = re.compile(r"youtube\.com/(?:channel/(UC[\w-]{22})|@([\w.]{3,40})|"
                      r"c/([\w-]+)|user/([\w-]+))")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z]+", "", s.lower())


def name_in_channel(name: str, ch_title: str) -> bool:
    """Channel title must contain the comic's name (kills squats)."""
    parts = [_norm(w) for w in name.split() if len(w) > 1]
    ct = _norm(ch_title)
    return bool(parts) and all(p and p in ct for p in parts)


def verify_channel(key: str, id_or_handle: str, by_id: bool = True) -> dict | None:
    """channels.list (1 unit). Returns {id, title, subs, handle} or None."""
    q = f"id={id_or_handle}" if by_id else \
        f"forHandle={urllib.parse.quote(id_or_handle)}"
    try:
        d = _get(f"{API}/channels?part=snippet,statistics&{q}&key={key}")
    except Exception:
        return None
    items = d.get("items") or []
    if not items:
        return None
    it = items[0]
    sn, st = it.get("snippet") or {}, it.get("statistics") or {}
    handle = (sn.get("customUrl") or "").lstrip("@")
    return {"id": it.get("id"), "title": sn.get("title", ""),
            "subs": int(st.get("subscriberCount", 0) or 0),
            "handle": handle}


def link_channels() -> None:
    """Resolve + verify personal channels for drafted indies (no search).

    Evidence, in order: @handles in evidence TITLES, then @handles +
    /channel/ links in evidence DESCRIPTIONS (videos.list snippet, batched).
    Each candidate verified (1 unit): title must contain the name; ties go
    to max subs. Links register in channels.json[slug] + graph field.
    """
    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")
    queue = load_queue()
    reg = json.loads((HERE / "data" / "channels.json").read_text())
    cands: dict[str, dict] = {}
    for slug, e in queue.items():
        if e.get("status") not in ("drafted", "sets-blocked"):
            continue
        gpath = COMEDIANS / slug / "comedian-graph.json"
        if not gpath.exists():
            continue
        try:
            g = json.loads(gpath.read_text())
        except json.JSONDecodeError:
            continue
        if g.get("youtube_channel", {}).get("id"):
            continue
        ev = e.get("evidence") or {}
        hs = HANDLE_RE.findall(ev.get("title", ""))
        cands[slug] = {"name": e.get("name", slug), "title_handles": hs,
                       "videoId": ev.get("videoId"), "graph": g,
                       "gpath": gpath}
    # descriptions for evidence videos (1 unit / 50, batched)
    vids = [c["videoId"] for c in cands.values() if c["videoId"]]
    descs: dict[str, str] = {}
    for i in range(0, len(vids), 50):
        try:
            d = _get(f"{API}/videos?part=snippet&id="
                     + ",".join(vids[i:i + 50]) + f"&key={key}")
        except Exception as ex:
            print(f"  snippet batch fail: {type(ex).__name__}")
            break
        for it in d.get("items", []):
            descs[it["id"]] = (it.get("snippet") or {}).get("description", "")
        time.sleep(0.3)
    linked = 0
    for slug, c in sorted(cands.items()):
        handles = list(dict.fromkeys(
            c["title_handles"] +
            HANDLE_RE.findall(descs.get(c["videoId"] or "", ""))))
        ch_urls = CHURL_RE.findall(descs.get(c["videoId"] or "", ""))
        ids = [m[0] for m in ch_urls if m[0]]
        best = None
        for h in handles:
            v = verify_channel(key, h, by_id=False)
            time.sleep(0.2)
            if v and v["id"] not in COLLISION_BLOCK \
                    and name_in_channel(c["name"], v["title"]):
                if best is None or v["subs"] > best["subs"]:
                    best = {**v, "handle": h, "via": "handle"}
        for cid in ids:
            v = verify_channel(key, cid, by_id=True)
            time.sleep(0.2)
            if v and name_in_channel(c["name"], v["title"]):
                if best is None or v["subs"] > best["subs"]:
                    best = {**v, "via": "description-link"}
        if best:
            reg.setdefault(slug, [])
            if best["id"] not in reg[slug]:
                reg[slug].append(best["id"])
            g = c["graph"]
            g["youtube_channel"] = {
                "id": best["id"], "handle": best.get("handle", ""),
                "title": best["title"], "subs": best["subs"],
                "via": best["via"],
                "source": "discover.py --link-channels (verified, no search)"}
            c["gpath"].write_text(json.dumps(g, indent=1) + "\n",
                                  encoding="utf-8")
            linked += 1
            print(f"  LINKED {slug} -> {best['title']} "
                  f"({best['subs']} subs, {best['via']})")
        else:
            print(f"  none  {slug} (handles tried: {handles[:3] or '—'})")
    (HERE / "data" / "channels.json").write_text(json.dumps(reg, indent=1))
    print(f"linked {linked}/{len(cands)} personal channels")


def _strip_tags(html: str) -> str:
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html,
               flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def mine_rosters() -> None:
    """Venue roster pages -> indie drafts (static HTML, zero quota).

    A residency listing is stronger evidence than a clip: the venue books
    them regularly. Full names only; existing slugs skipped (kings keep
    rank — press rule: lists never demote); roast/subject pages ignored.
    AUDIT RULE: rosters mix legends with unknowns (Angel page: Frank
    Skinner next to Blank Peng). Every roster batch gets a manual tier
    audit before rate.py — established names flip to king on sight.
    Bio pages: each new draft's page is fetched once for a style excerpt
    (deal/threads hypotheses — NEVER verbatim material) + social links.
    Bios are third-party prose: evidence for discovery fields only.
    """
    import urllib.request as _rq
    queue, known = load_queue(), existing_slugs()
    drafted = 0
    for venue, urls in ROSTERS.items():
        if isinstance(urls, str):
            urls = [urls]
        for url in urls:
            try:
                req = _rq.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                html = _rq.urlopen(req, timeout=30).read().decode("utf-8", "replace")
            except Exception as e:
                print(f"  {venue}: fetch fail {type(e).__name__} {url[-12:]}")
                continue
            # (name, page-url) pairs from headers + links.
            # VENUE-SCOPED href filter (2026-10-17: unscoped links drafted
            # menu items — "Watch Comedy", "Christmas Parties" — as comics):
            # only comedian-profile URLs yield names.
            pairs: dict[str, str] = {}
            must = {"angel-comedy": "/comedians/",
                    "on-the-mic": "/comedians_list/"}.get(venue, "")
            for m in re.finditer(
                    r'<a[^>]+href="([^"]+)"[^>]*>\s*(?:<[^>]+>\s*)*'
                    r"([A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){1,2})\s*"
                    r"(?:<[^>]+>\s*)*</a>", html):
                href, raw = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()
                if must and must not in href:
                    continue
                if re.match(r"^[A-Z][a-z'-]+(\s+[A-Z][a-z'-]+){1,2}$", raw):
                    pairs.setdefault(raw, href)
            if not pairs:  # fallback: bare headers, no links
                for raw in set(re.findall(
                        r"^#{2,3}\s+([A-Z][A-Za-z'’.-]+(?:\s+[A-Z][A-Za-z'’.-]+){1,2})\s*$",
                        html, re.M)):
                    pairs.setdefault(raw, "")
            seen = 0
            for name, href in sorted(pairs.items()):
                slug = slugify(name)
                if not slug or slug in known or slug in queue:
                    continue
                if name.lower() in NAVTEXT_BLOCK:
                    continue
                ev = {"roster": url, "venue": venue}
                base = {"angel-comedy": "https://www.angelcomedy.co.uk",
                        "on-the-mic": "https://www.onthemic.co.uk"}.get(venue, "")
                page_url = href if href.startswith("http") else (
                    base + href if href.startswith("/") and base else "")
                bio, socials = "", {}
                if page_url and venue != "on-the-mic":
                    try:
                        req2 = _rq.Request(page_url,
                                           headers={"User-Agent": "Mozilla/5.0"})
                        ph = _rq.urlopen(req2, timeout=20).read().decode(
                            "utf-8", "replace")
                        txt = _strip_tags(ph)
                        m2 = re.search(r"Biography(.{200,1200})", txt)
                        bio = (m2.group(1)[:600] if m2 else txt[:600])
                        for sm in re.finditer(
                                r'https?://(?:www\.)?(instagram\.com|tiktok\.com|'
                                r'twitter\.com|x\.com|youtube\.com)/([A-Za-z0-9_.@/-]+)',
                                ph):
                            socials.setdefault(sm.group(1).split(".")[0],
                                               sm.group(0)[:120])
                    except Exception:
                        pass
                    time.sleep(0.4)
                if page_url and venue == "on-the-mic":
                    ev["profile"] = page_url  # per-comic page: phase-2 enrichment
                if draft_indie(slug, name, ev, f"venue-roster:{venue}"):
                    drafted += 1
                    known.add(slug)
                    if bio or socials:
                        try:
                            gpath = COMEDIANS / slug / "comedian-graph.json"
                            g = json.loads(gpath.read_text())
                            if bio:
                                g["discovery"]["bio_note"] = bio
                            if socials:
                                g["socials"] = {**g.get("socials", {}), **{
                                    k: {"url": v, "source": f"venue-bio:{venue}"}
                                    for k, v in socials.items()}}
                            gpath.write_text(json.dumps(g, indent=1) + "\n",
                                             encoding="utf-8")
                        except (OSError, json.JSONDecodeError):
                            pass
                queue[slug] = {"name": name, "status": "drafted",
                               "evidence": ev, "src": f"venue-roster:{venue}",
                               "bio_fetched": bool(bio or socials),
                               "first_seen": datetime.now(timezone.utc)
                               .strftime("%Y-%m-%d")}
                seen += 1
            print(f"  {venue} [{url[-8:]}]: {seen} new names ({drafted} drafted total)")
            time.sleep(0.5)
    QUEUE.write_text(json.dumps(queue, indent=1))
    print(f"roster drafts: {drafted}")


def guess_handles(variants: int = 1) -> None:
    """forHandle resolution for indies without channels (no search).

    Tries @FirstLast (+@FirstLastComedy with variants=2) per channel-less
    indie, verified strictly (title must contain the name; ties -> max
    subs). Verification is the safeguard that makes guessing registry
    administration, not content search: wrong guesses fail to verify and
    register nothing. ~1 unit per attempt. Skips kings (canon track sorts
    its own channels via harvester) and already-linked profiles.
    """
    key = _key()
    if not key:
        raise SystemExit("no YOUTUBE_DATA_API_KEY")
    reg = json.loads((HERE / "data" / "channels.json").read_text())
    targets = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("tier") != "indie" or j.get("youtube_channel", {}).get("id"):
            continue
        name = j.get("name") or d.name.replace("-", " ")
        parts = [w for w in re.split(r"\s+", name) if len(w) > 1]
        if len(parts) < 2:
            continue
        first, last = _norm(parts[0]), _norm(parts[-1])
        hs = [first + last]
        if variants >= 2:
            hs += [first + last + "comedy", first + last + "comic"]
        targets.append((d.name, name, hs))
    print(f"{len(targets)} channel-less indies")
    linked, spent = 0, 0
    for slug, name, hs in targets:
        best = None
        for h in hs:
            v = verify_channel(key, h, by_id=False)
            spent += 1
            time.sleep(0.2)
            if v and v["id"] not in COLLISION_BLOCK \
                    and name_in_channel(name, v["title"]):
                if best is None or v["subs"] > best["subs"]:
                    best = {**v, "handle": h, "via": "handle-guess"}
        if best:
            reg.setdefault(slug, [])
            if best["id"] not in reg[slug]:
                reg[slug].append(best["id"])
            gpath = COMEDIANS / slug / "comedian-graph.json"
            g = json.loads(gpath.read_text())
            g["youtube_channel"] = {
                "id": best["id"], "handle": best.get("handle", ""),
                "title": best["title"], "subs": best["subs"],
                "via": best["via"],
                "source": "discover.py --guess-handles (verified, no search)"}
            gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")
            linked += 1
            print(f"  LINKED {slug} -> {best['title']} ({best['subs']} subs)")
    (HERE / "data" / "channels.json").write_text(json.dumps(reg, indent=1))
    print(f"linked {linked}/{len(targets)} (~{spent} quota units)")


def audit_channels(max_age_days: int = 365) -> None:
    """Freshness + compiler audit for every linked personal channel.

    A link counts only if the channel actually hosts THEIR standup, fresh:
      - dormant:  0 clips harvested (empty, dead, or wrong).
      - stale:    newest upload older than max_age_days (default 365).
      - mismatch: CHANNEL TITLE no longer carries their name (renamed/sold
                  — unlinked on sight). Clip-title hit rates are NOT used:
                  comics title videos by bit, not by name.
      - variety:  channel title matches but hosts others too (talk shows,
                  collabs, bit-title junk in mining). Link kept + guests
                  listed; theory-scoring treats with caution.
      - active:   clips + fresh + title matches.
    Unlinks: fountain-pointed links, COLLISION_BLOCK namesakes.
    """
    import datetime as _dt
    today = _dt.date.today()
    reg = json.loads((HERE / "data" / "channels.json").read_text())
    fountain_ids = {c for k in FOUNTAINS for c in reg.get(k, [])}
    queue = load_queue()
    stats: dict[str, int] = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        yc = j.get("youtube_channel") or {}
        if not yc.get("id"):
            continue
        name = j.get("name", d.name)
        cid = yc["id"]
        # compiler-pointed link? unlink, never personal.
        if cid in fountain_ids:
            yc.update({"status": "compiler",
                       "checked": str(today),
                       "note": "points at a multi-comic fountain; unlinked as personal"})
            j.pop("youtube_channel", None)
            if cid in reg.get(d.name, []):
                reg[d.name] = [c for c in reg[d.name] if c != cid]
            queue.setdefault(d.name, {}).update(
                {"channel_audit": "unlinked-compiler", "date": str(today)})
            stats["compiler-unlinked"] = stats.get("compiler-unlinked", 0) + 1
            print(f"  UNLINK {d.name}: points at fountain {cid[:8]}")
            g.write_text(json.dumps(j, indent=1) + "\n", encoding="utf-8")
            continue
        # proven collision? unlink permanently.
        if cid in COLLISION_BLOCK:
            j.pop("youtube_channel", None)
            if cid in reg.get(d.name, []):
                reg[d.name] = [c for c in reg[d.name] if c != cid]
            queue.setdefault(d.name, {}).update(
                {"channel_audit": "unlinked-collision", "date": str(today)})
            stats["collision-unlinked"] = stats.get("collision-unlinked", 0) + 1
            print(f"  UNLINK {d.name}: namesake collision {cid[:8]}")
            g.write_text(json.dumps(j, indent=1) + "\n", encoding="utf-8")
            continue
        try:
            rows = (json.loads((DATA / f"{d.name}.json").read_text())
                    .get("rows", []))
        except (OSError, json.JSONDecodeError):
            rows = []
        # ownership re-check: the CHANNEL TITLE must still carry the name.
        # (Clip titles carry bit names, not comic names — a <20% clip-hit
        # rate measures title conventions, not ownership. 2026-10-17: the
        # clip-rate rule false-flagged 18 real channels; replaced.)
        ch_title = (rows[0].get("channel") if rows else "") or yc.get("title", "")
        title_ok = name_in_channel(name, ch_title)
        first = _norm(name.split()[0]) if name.split() else ""
        last = _norm(name.split()[-1]) if name.split() else ""
        named = sum(1 for r in rows
                    if (first and first in _norm(r.get("title", "")))
                    or (last and last in _norm(r.get("title", ""))))
        dates = sorted(r.get("publishedAt", "") for r in rows if r.get("publishedAt"))
        newest = dates[-1] if dates else ""
        try:
            age = (today - _dt.date.fromisoformat(newest[:10])).days \
                if newest else None
        except ValueError:
            age = None
        # variety mining: distinct person-names across show-titled videos.
        # Bit-title junk ("Because Tuesday") pollutes this; treat as
        # advisory guests-list, demotion only via fountain/collision rules.
        found: set[str] = set()
        for r in rows:
            t = r.get("title", "")
            if not SHOW_RE.search(t) or ROAST_RE.search(t):
                continue
            full, _ = names_from_title(t)
            for n_ in full:
                if _norm(n_) != _norm(name):
                    found.add(n_)
        if not rows:
            status = "dormant"
        elif not title_ok:
            status = "mismatch"
        elif len(found) >= 4:
            status = "variety"
        elif age is None or age > max_age_days:
            status = "stale"
        else:
            status = "active"
        yc.update({"status": status, "checked": str(today),
                   "clips": len(rows), "newest_upload": newest,
                   "name_match_rate": round(named / max(1, len(rows)), 2),
                   "other_names": sorted(found)[:8]})
        j["youtube_channel"] = yc
        g.write_text(json.dumps(j, indent=1) + "\n", encoding="utf-8")
        stats[status] = stats.get(status, 0) + 1
    (HERE / "data" / "channels.json").write_text(json.dumps(reg, indent=1))
    QUEUE.write_text(json.dumps(queue, indent=1))
    print(f"channel audit: {stats}")


def link_websites() -> None:
    """Official websites: Wikidata P856 first, verified URL guesses second.

    Personal sites (louisck.com pattern) are the highest-trust outbound
    link: owned by the comic, stable for decades, zero platform risk.
    Sources, in order (no search anywhere):
      1. Wikidata P856 official-website claims for graphs carrying
         bio.wikidata_id (wbgetentities, 50/batch, free, CC0). Curated
         structured data — accepted with a liveness check.
      2. Curated URL guesses (firstnamelastname.com, + .net/.co.uk):
         fetched and KEPT only on HTTP 200 + comedy signals
         (comedian|comedy|stand-up|tour|shows|tickets) in-page.
         Guesses that fail verification register nothing.
    Stores graph.website{url, source, checked}. All tiers (kings need
    sites most — their pages get the traffic).
    """
    import urllib.request as _rq
    qids: dict[str, str] = {}
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("website", {}).get("url"):
            continue
        q = ((j.get("bio") or {}).get("wikidata_id")
             or (j.get("recognition") or {}).get("wikidata"))
        if q:
            qids[d.name] = q
    print(f"{len(qids)} profiles with QIDs, website missing")
    found: dict[str, dict] = {}
    ids = list(qids.values())
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        try:
            u = ("https://www.wikidata.org/w/api.php?action=wbgetentities"
                 "&props=claims&format=json&ids=" + "|".join(batch))
            d = json.loads(_rq.urlopen(
                _rq.Request(u, headers={"User-Agent": "funnygraph/1.0"}),
                timeout=30).read())
        except Exception as e:
            print(f"  wikidata batch fail: {type(e).__name__}")
            continue
        for qid, ent in (d.get("entities") or {}).items():
            try:
                p856 = ((ent.get("claims") or {}).get("P856") or [])
                if p856:
                    url = p856[0]["mainsnak"]["datavalue"]["value"]
                    slug = next(s for s, q in qids.items() if q == qid)
                    found[slug] = {"url": url, "source": "wikidata-P856"}
            except (KeyError, IndexError, StopIteration):
                continue
        time.sleep(0.5)
    print(f"wikidata P856: {len(found)} official sites")

    def live(url: str) -> tuple[bool, str]:
        if not url.startswith("http"):
            url = "https://" + url
        try:
            req = _rq.Request(url, headers={"User-Agent": "funnygraph/1.0"})
            body = _rq.urlopen(req, timeout=15).read()[:50000].decode(
                "utf-8", "replace").lower()
            if re.search(r"comedian|comedy|stand.?up|\btour\b|shows|tickets",
                         body):
                return True, url
            return False, "no-comedy-signals"
        except Exception as e:
            return False, type(e).__name__

    saved = 0
    for slug, meta in sorted(found.items()):
        ok, info = live(meta["url"])
        if not ok:
            print(f"  dead {slug}: {meta['url']} ({info})")
            continue
        _store_website(slug, info if info != meta["url"] else meta["url"],
                       meta["source"])
        saved += 1
    # guesses for the rest (all tiers, no site yet)
    todo = []
    for d in sorted(COMEDIANS.iterdir()):
        g = d / "comedian-graph.json"
        if not g.exists() or d.name in EXCLUDED:
            continue
        try:
            j = json.loads(g.read_text())
        except json.JSONDecodeError:
            continue
        if j.get("website", {}).get("url") or d.name in found:
            continue
        name = j.get("name") or d.name.replace("-", " ")
        parts = [w for w in re.split(r"\s+", name) if len(w) > 1]
        if len(parts) < 2:
            continue
        base = _norm(parts[0]) + _norm(parts[-1])
        doms = [base + ".com", base + ".net"]
        region = j.get("region", "")
        if isinstance(region, dict):
            region = region.get("id", "")
        if region == "uk":
            doms.append(base + ".co.uk")
        todo.append((d.name, doms))
    print(f"{len(todo)} profiles for URL guessing")
    for slug, doms in todo:
        for dom in doms:
            ok, info = live(dom)
            time.sleep(0.3)
            if ok:
                _store_website(slug, info, "url-guess-verified")
                saved += 1
                print(f"  GUESSED {slug} -> {info}")
                break
    print(f"websites stored: {saved}")


def _store_website(slug: str, url: str, source: str) -> None:
    import datetime as _dt
    gpath = COMEDIANS / slug / "comedian-graph.json"
    g = json.loads(gpath.read_text())
    g["website"] = {"url": url, "source": source,
                    "checked": str(_dt.date.today())}
    gpath.write_text(json.dumps(g, indent=1) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--fetch-sets", action="store_true")
    ap.add_argument("--link-channels", action="store_true")
    ap.add_argument("--rosters", action="store_true")
    ap.add_argument("--guess-handles", action="store_true")
    ap.add_argument("--audit-channels", action="store_true")
    ap.add_argument("--link-websites", action="store_true")
    ap.add_argument("--regions", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--cap", type=int, default=200)
    args = ap.parse_args()
    if args.dry_run:
        dry_run()
    if args.scan:
        scan(cap=args.cap)
    if args.fetch_sets:
        fetch_sets(limit=args.limit)
    if args.link_channels:
        link_channels()
    if args.rosters:
        mine_rosters()
    if args.guess_handles:
        guess_handles()
    if args.audit_channels:
        audit_channels()
    if args.link_websites:
        link_websites()
    if args.regions:
        backfill_regions()
    if not (args.dry_run or args.scan or args.fetch_sets or
            args.link_channels or args.rosters or args.guess_handles or
            args.audit_channels or args.link_websites or args.regions):
        ap.print_help()


if __name__ == "__main__":
    main()
