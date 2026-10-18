# R2 PROFILE BUILD — status (2026-10-18)

> Work done this session: imported all R2 comedians/bits/transcripts,
> linked clips→transcripts for site embedding, built graph profiles
> for every R2 comedian. Nothing pushed to git (per owner instruction).

## What was built

### 1. Transcript↔clip linkage (site embed layer)
| Layer | Count |
|---|---|
| Clips linked to transcripts | **2,373** (1,983 timed / karaoke-syncable) |
| Specials linked | **644** (12 timed, rest published-text) |
| Comedians in site manifest | **700** |
| Transcript words (clips) | **492k+** |

Files: `data/r2/site_manifest.json` (site eats this), `data/youtube/*.json` (556 files, 418 r2_linked), `data/r2/specials/*.json` (292 files). Embed recipe in SITE.md.

### 2. Graph profiles
| Action | Count |
|---|---|
| Graphs created (were missing) | **415** |
| Existing stubs linked | **116** |
| Full graphs linked (R2 data added) | **169** |
| Total graphs now | **2,375** (was 1,960) |
| Tier: king / indie | 415 / 1,960 |

Every R2 comedian now has:
- `discovery` provenance (r2:comedy-specials + clip/special counts)
- `youtube` block (clip stats + top_clip + r2 linkage)
- `set_queue` → R2 specials (ready for analyze_set)
- `transcripts` summary (clip_words, special_words, timed counts)
- `region`/`continent` defaults (uk/europe for the UK harvest)

### 3. Enrichment
- **Regions**: 137 tagged from bio + 28 overrides → `region`/`continent`
- **Generations**: 166 assigned (breakthrough era)
- **Bios**: running (Wikidata). ~245/700 r2_profiled matched so far;
  many small UK indies have no Wikidata entry (expected — miss ≠ error).
  Cache at `wikidata_cache.json` (~1,260 entries); rerunnable/resumable.

## Gold standard comparison (Louis vs the new profiles)

| Field | Louis (gold) | New R2 profiles |
|---|---|---|
| identity (deal/archetype/operators) | ✅ full | stub (indie_draft) — needs deepening |
| known_bits | 2 | 0 (specials ready for ingest) |
| sets / timing_measured | 12 | 0 (blocked on analyze_set) |
| bio (wikidata) | ✅ | ~35% matched |
| youtube clips | ✅ | ✅ linked |
| specials | rated | linked, not rated |
| rating / boards | ✅ FULL | will appear on next `rate.py` run |

## What still needs doing (priority order)

1. **Deepen 415 new graphs + 116 stubs** — fill identity block
   (deal, archetype, operator_priors) for comedians with enough
   transcript material. Start with those having timed specials
   (12 timed + high-word specials).
2. **Ingest specials → known_bits + timing_measured** — run
   analyze_set on timed specials (Sloss socio-2021, Stewart Lee
   10 timed specials, Jimmy Carr clips, etc.)
3. **Run `rate.py`** — new graphs need ratings; boards will update.
4. **Bio backfill** — rerun `enrich_bios.py` for remaining ~455
   (many will miss on Wikidata; that's fine).
5. **Site render** — wire site_manifest.json into profile pages:
   YouTube embed + transcript panel (karaoke if words_timed).

## Rerunning after debz/local handoffs

```bash
python3 sync_r2_clips.py       # re-enumerate R2
python3 sync_r2_metadata.py    # fetch new clip JSONs
python3 sync_r2_merge.py       # merge + specials + manifest
python3 sync_r2_profiles.py    # create/update graph profiles
python3 regions.py --tag-all
python3 enrich_bios.py         # resumable via cache
python3 enrich_generations.py
python3 rate.py                # recompute boards
```

All local, uncommitted. R2 creds via env (never commit).

---

## PHASE 2 COMPLETE (2026-10-18): specials ingested + boards live

### Ingested 12 timed specials → measured sets

| Comedian | Sets | Words | known_bits | max_pause | wpm |
|---|---|---|---|---|---|
| Stewart Lee | 10 new (18 total) | 71.5k | 52 | **36.76s** (Carpet Remnant World) | 123–150 |
| Daniel Sloss | 1 (socio-2021) | 13.0k | 5 | 12.56s | 177 |
| Simon Amstell | 1 (do-nothing-live) | 9.4k | 5 | 13.71s | 155 |

Stewart Lee's Carpet Remnant World max_pause = 36.76s — that's the
failed-callback moment from ACASTER-GOLD, now measured.

### rate.py recomputed — boards live

| Comedian | headline | coverage | house | consensus | canon |
|---|---|---|---|---|---|
| louis-ck | 97.1 | FULL | #2 | #10 | #16 |
| stewart-lee | 88.2 | FULL | **#5** | #71 | #150 |
| daniel-sloss | 87.9 | UNRANKED | — | #241 | #206 |
| jimmy-carr | 26.5 | UNRANKED | — | #83 | #146 |
| simon-amstell | 62.5 | DISCOVERY | — | — | — |

2,373 profiles rated, 2,339 provisional. All boards recomputed.

### Analysis files saved

`analysis/stewart-lee-*-analysis.json` (10), `daniel-sloss-socio-2021_analysis.json`,
`simon-amstell-do-nothing-live_analysis.json` — each with timing profile,
punch_candidates, beat segmentation, GTVH (code-only).

### Remaining (priority)

1. Deepen identity blocks for measured comedians (Lee/Sloss/Amstell have
   data for authored deal/archetype now)
2. Ingest more timed specials as debz/local ASR them (rerun ingest script)
3. Run identity authoring for the 301 R2 comedians with clips but no measured sets
4. Bio backfill continues in background (resumable)
