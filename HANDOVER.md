# HANDOVER — funnygraph (2026-10-17, end of day-zero session)

> For the next agent (human or model) picking this up. Read this + AGENTS.md-equivalent
> rules below, then check `git log --oneline -5` for drift.

## What this repo is
The canonical comedy resource: 290 comedian graphs (178 kings + 112 indies),
theory applied to every comic, auditable rankings, global coverage (21 regions).
Feeds "Why is X Funny?" videos, TOP 2026 election, agent joke-writers.

## State: LIVE and committed (main, clean tree)
- **Graphs:** 290 (178 kings tier-tagged, 112 indies). English US/UK/AUS/NZ kings are P0-complete-ish.
- **Rankings:** consensus (178), era-adjusted, by_generation/type/mode/decade/continent, metrics, neighbors, specials (+dark, +by_type), clips, netflix_specials.
- **Theory:** 150+ known_bits, 118+ essay seeds, 14 humor types, modes w/ signatures, 162 style fingerprints.
- **Data:** 404 transcripts (19MB), 57 YouTube pulls (556 clips), 7 Netflix reports, 83k-entry IMDb index in /tmp (REGENERATE — not in repo).
- **Papers:** PAPER.md (rankings), METRICS_PAPER.md (metrics), RANKINGS.md, GAPS.md (honest audit), TOP2026.md, SITE_METRICS.md, ENDPOINTS.md, COUNTRY_THEORY.md, ML_PIPELINES.md, FANBASE_ML.md.

## Running right now (background, may be dead — check)
- `enrich_bios.py` → /tmp/bios4.log (Wikidata bios, kept dying on throttling at ~B; 142/290 have bios; restart resumes from cache).

## Open threads (priority order)
1. **TOP 2026 ballot distribution** — BALLOT_2026.md + ARENA_BALLOT.md written; needs owner to approve ballot + seed voter list. THE differentiator.
2. **Episode drafts** — episodes/why-shane-gillis-funny.md done; Theo + Carlin queued (graphs ready).
3. **Monday pulse #2** — `pulse.py --snapshot` weekly; unlocks velocity/HEAT/rising-star.
4. **Bios completion** — restart enrich_bios.py; fills awards leg + region unknowns.
5. **Subs backfill** — YouTube search quota resets midnight PT; ~120 comics need `youtube_harvest2.py` refresh (registry channels only, NEVER search).
6. **Auto-draft reviews** — fill_kings.py pattern; ~100 thin kings remain (batches by rank).
7. **Critic special lists** — Paste/RS rank specials; third leg for GOAT-Special.
8. **Whisper timing** — needs audio-access decision (owner). Unlocks timing→rating (M7).
9. **Regional awards** — Humour Awards (NG), Edinburgh, Melbourne Barry as equal legs.
10. **Xiaoguo captions** — unavailable via InnerTube (recorded); whisper path when audio accessible.

## Binding rules (learned today, do not re-violate)
1. **No YouTube search, ever** — registry channels.json + uploads playlists only. Search burns 100 units and guesses. (`youtube_harvest_search_LEGACY.py` is retired.)
2. **Never blend popularity into quality** — split boards (fit_weights proved averaging destroys signal: 0.658 < 0.692 CC-only).
3. **Modulation must never reward missingness** — type crowns are legacy-primary (caught Ellen winning on absent data twice).
4. **Missing = neutral in z-scores; min group 5; median not mean** — giants must not crater good comics.
5. **Full names only for mention-mining** — "che" is Italian, "Martin" is Fluffy's buddy, "may" is a month.
6. **Comedian-name-in-title required for IMDb matches** — Pixar's Up struck 3 times.
7. **Secrets in .env only** (gitignored): YOUTUBE_DATA_API_KEY, HF_TOKEN, OPENCODE key via auth store. Secret-scan before push.
8. **Excluded list is auditable, not secret** — EXCLUSIONS.md + exclude.py guard in all 13 pipelines (trap-tested). Currently: ellen-degeneres (owner prerogative).
9. **One schema + tier, never two schemas** — indie/ dir was migrated; promotion = flip flag.
10. **Standup only** — manzai duos removed; rakugo reference stays in docs. Foreign comics are discovery-tier until English core complete (owner call 2026-10-17 eve).

## Key numbers to trust
- Hedberg→Wright 0.92 (recommender validated) · Hicks→Lee 0.56 (real lineage)
- Hart +0.83 overrated · Hicks −0.75 underrated · Burr ±0.07 balanced
- Profanity peaked in 70s, declining (M6) · ratings R²=0.09, profanity effect ~0 (M2)
- Authored rigidify vs measured r=−0.05 — theory check FAILED, recalibrate don't hide (M5)
- Top-1 flips Carlin/Pryor by regime; 4 stable across all (Hicks/Rock/Chappelle/Carlin)

## Resume commands
```bash
cd /root/funnygraph
git log --oneline -5                    # drift check
nohup python3 enrich_bios.py > /tmp/bios.log 2>&1 &   # resume bios
python3 pulse.py --snapshot            # Monday cadence
python3 rank_comedians.py && python3 metrics.py && python3 recommend.py  # rebuild all
python3 indie.py --spotlight           # small comic queue
python3 indie.py --for-you "a,b,c"     # recommender demo
```
