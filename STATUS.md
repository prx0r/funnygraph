# STATUS — live snapshot 2026-10-17 (refresh by re-running the counts)

> What exists right now. For rules see DECISIONS.md, for loop see
> WORKFLOW.md, for site wiring see SITE.md. Previous snapshot: HANDOVER.md
> (2026-10-17 day-zero, now historical). Full session log: HANDOVER-2026-10-17.md.

## Profiles: 1959 (415 kings + 1545 indies)

| Coverage | n | Meaning |
|---|---|---|
| king FULL | 18 | measured jokes + theory depth |
| king PARTIAL | 80 | depth only (authored until measured) |
| king UNRANKED | 317 | zero owned evidence; provisional headline, no rank |
| indie DISCOVERY | 1545 | drafts + press + venue finds; provisional |

## Boards (all in rankings/, all recomputable via rate.py)

- **house.json** (proprietary): Norm .922, Louis .911, Carlin .812. 18 FULL.
- **consensus.json** (reference): Carlin 8.49, Pryor 7.71, Rock 7.16.
- **canon.json**: Carlin/Robin/Pryor. **peoples.json**: Burnham 8.59 #1 (76 rated).
- **era_adjusted**: Chappelle 13.0, Carlin 11.4, Hicks 11.0.
- **by_type** (13 crowns), by_generation/decade/mode/continent, specials (100),
  bits (195), neighbors (178), bt (BT vs Borda τ.64 on 4 lists; was .876 on 2),
  stability (minority stable — 12/295 latest), agreement (τ ca≈0, W p.04),
  mallows (φ .82/.90/.86, precision .43/.23/.34), theory_content
  (18 measured, 7 type boards), spotlight.json (weekly).
- **ratings.json**: canonical site table, 1959 rows, pipeline rate/v1.

## Lenses (metrics.json, 417 rows)

Gap extremes: Iglesias +0.83 (most overrated; Hart +0.525 famous case),
Hicks −0.70 / Lee −0.61 (most underrated), Burr +.11 balanced. Median
+0.087 (n=64). HEAT null everywhere (no proxy shipped).

## Indie lane

- Channels linked 91 (active 22 / stale 19 / variety 7 / dormant 36 / unverified 7).
- Websites 597 (107 Wikidata P856 + 81 verified guesses + OTM profile sites).
- Regions known 305/1959 (indie unknowns: 79).
- Theory: scored 2 (material wall), known_bits 195, measured
  priors 23 KT + 3 synthetic-authored, style_tags 172 matched, for-you +
  compare views live.
- Fountains: KT, Dry Bar, JFL, DTC, Frog (sets-only post-roast), Angel
  (+roster), Xiaoguo, Basketmouth. Pending: Top Secret, Komedia, Just-the-Tonic.
- Press compilers: deadline-2026 (20), edinburgh newcomers (8), vulture-2026
  (3 quarantined), gold-2026 (16), timeout-2026 (11).
- On The Mic (1,707-comedian directory): 1,464 drafts, 112 flipped to king
  (audit), 582 pages enriched (bio+credits+sites+socials — RERUNNABLE:
  `python3 discover.py --otm-pages --limit 1200`).

## Papers

PAPER_ARXIV.md (full manuscript w/ §2.6 humor theory + §4.11 house),
PAPER.md v0.2, METRICS_PAPER.md v0.2, METHODOLOGY.md, GAPS.md (3 closed),
ENDPOINTS.md (10 crowns: canon/velocity live, TOP2026 gated),
SITE_METRICS.md (panel v2), SITE.md, DECISIONS.md, WORKFLOW.md.

## Blocked (owner gates)

Cookies/yt-dlp (all captions), TOP2026 ballot+voters, whisper audio call,
Monday snapshot habit (velocity live, subs_growth needs one more subs-bearing snap).
Dupe verdict (colin/collin, cameron-frisk — flagged, not merged).
Push policy: owner pushes; agent committed locally twice today.

## Known limitations (full register: GAPS.md + PAPER_ARXIV §7)

Only a minority of positions stable (12/295 latest) · n=29 fitting set
(fragile — grid fit flipped between runs) · critics leg frozen 2004/2017
(C4-2007 added, still old) · IMDb/awards/YT skews · non-English thin ·
1523/1545 indies unscored (204 material wall, 1523 zero-leg) · BT
strengths uncalibrated (τ=0.64 on 4 lists) · crowd-vs-WR duality open ·
single-author seeds.
