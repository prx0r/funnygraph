# funnygraph

> **THE comedy database: theory applied to every comedian + principled
> rankings with honest uncertainty + autonomous discovery of unknowns.**
> 417 comedian graphs (211 kings + 206 indies) · proprietary house election
> · reference elections (critics/audience canon) · weekly pulse · indie
> discovery loop (fountains → drafts → channels → sets → ratings).
> Started as graphs for the **"Why is X Funny?"** video series; grew into
> the measurement instrument. Schema `pogtown.comedian.v1` (same as
> `characters2/theory/comedians`). Every value is **hypothesis** until
> measured. No verbatim bits. Stage persona only — no biography.

## Start here (read in order)

| Doc | For whom |
|---|---|
| `STATUS.md` | live snapshot: counts, boards, blocked items |
| `SITE.md` | the site builder: files, schemas, panel assembly, rules |
| `WORKFLOW.md` | the operator: canonical loop, commands, quota, cadence |
| `DECISIONS.md` | everyone: 46 binding calls + the incidents behind them |
| `PAPER_ARXIV.md` | reviewers: full manuscript (§2.6 humor theory, §4 method) |
| `ENDPOINTS.md` | product: 10 crowns as endpoints with LIVE/NEEDS/BLOCKED |
| `GAPS.md` | skeptics: everything wrong, stated plainly |

## The loop (30s version)

```
FIND     discover.py --scan + press lists + venue rosters -> indie drafts
LINK     --link-channels / --guess-handles / --link-websites (traffic out, uploads in)
VERIFY   --audit-channels + manual tier audit (national credits = king)
SETS     captions (BLOCKED: cookies) or --from-transcript; indie --score on arrival
RATE     rate.py --check -> boards + ratings.json + per-graph rating{}
PULSE    pulse.py --snapshot/--report -> spotlight.json week boards
PROMOTE  human flips indie->king on canon evidence (nothing auto-promotes)
```

## Pipelines

| Script | Reads | Writes |
|---|---|---|
| `rate.py` | graphs | all boards + ratings.json + rating{} (THE entry point) |
| `rank_comedians.py` | graphs | consensus/era/generation/disagreement (reference) |
| `split_boards.py` | mallows | canon.json, peoples.json (reference) |
| `house_rank.py` | theory_content + metrics | house.json (proprietary) |
| `metrics.py` | boards + YT | metrics{} + metrics.json (5 lenses) |
| `kendall_w/stability/mallows_phi/bt_leg/fit_weights.py` | boards | agreement/stability/mallows/bt (validation) |
| `theory_content.py` | characters2 bits (live) | theory_content.json (joke quality) |
| `discover.py` | YT API + venue pages | drafts + queue + channels + websites + regions |
| `indie.py` | graphs + scribe | scores, greats-matches, style tags, spotlight, compare |
| `pulse.py` | YT API | snapshots + spotlight.json + comment mines |
| `recommend.py` | graphs | neighbors.json (for-you latent space) |
| `seed_bits.py` | press notes | hypothesis-flagged known_bits |
| `harvest_captions.py` | InnerTube/yt-dlp | scribe/ word JSON (BLOCKED: cookies) |

Enrichment (fetchers, need keys/quota): `enrich_bios/ratings/recognition/generations.py`,
`youtube_harvest2.py` (registry only, never search), `netflix_reports/views.py`.

## Rules (full log: DECISIONS.md)

1. No YouTube search, ever. No roasts in discovery. Full names only.
2. Popularity never enters quality. External judgments display, never score.
3. Missing = neutral; withheld, not shown; nulls ship; momentum shown-not-blended.
4. Stage persona only; no verbatim bits; bio prose is style evidence, never material.
5. Press lists never demote; human promotes; everything auto-rates.
6. Owner pushes; agents commit locally only when asked. Secrets in .env.

## Status

- [x] 417 graphs (211 kings + 206 indies), all rated by default (rate.py)
- [x] Proprietary house board + reference elections + stability intervals
- [x] Indie discovery loop live (8 fountains, press compilers, venue rosters)
- [x] Week boards live (velocity mode; subs_growth needs one more snap)
- [x] Full manuscript + methodology + audit docs
- [ ] Captions unblocked (cookies) — THE material bottleneck
- [ ] TOP 2026 ballot distributed (owner) — the election
- [ ] Episodes 2-3 (Theo, Carlin drafts)
- [ ] Serve layer (static JSON ready; no API yet)
