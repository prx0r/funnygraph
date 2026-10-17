# BUILD NOTES — 2026-10-17 session (funnygraph day zero → canonical resource)

> Everything built today, thread by thread. 20 commits. Start here to orient,
> then see PRIORITY at the bottom for where to start next.

## Thread 0 — where we came from (other repos, same session)
- Reviewed `/root/influence` (execution runtime, voice casting, YT dash live)
  vs `/root/influence2` (manager layer, AgentRun workflows, character track).
- Pulled `prx0r/characters`, cloned `prx0r/characters2` (comedy-writing lane).
- Built per-comedian autonomous agent harness in characters2
  (`theory/agent_harness.py` + `theory/writer.py`): skill.md + identity graph
  → mimo LLM write → coherence/NoSlop gates → FLIP/sculpt → reputation.
  Killed the .py template writer (mass-production = slop, per architecture doc).
  Live: 6/7 stage personas won. Pushed `60b0bba` to prx0r/characters2.

## Thread 1 — funnygraph founded (35 → 48 graphs)
- New local repo `/root/funnygraph` for "Why is X Funny?" video series.
- Copied 7 graphs from characters2 + authored 28 GOATs (Gillis, McCusker,
  Pryor, Hicks, Dangerfield, Bruce, Rivers, Burr, Wright, Philips, Martin,
  Lee, Moran, Normand, Bargatze, Mulaney, Burnham, Wong, Tomlinson, Gulman,
  Bamford, Buress, Che, Silverman, Stanhope, Izzard, O'Neal, Giraldo).
- Schema pogtown.comedian.v1. Essay seed per comic = episode scaffold.

## Thread 2 — theory depth (Louis/Norm standard)
- Deep-dived Louis CK graph (measured roadrage: 8.16s holds, beat decomposition,
  GTVH per beat) + Norm graph + personality.md files as the depth bar.
- `deepen_graph.py`: style_thesis, timing_doctrine, known_bits with
  why-they-work, academic theory_links, essay seeds — applied to all 48.
- Wave 2 (13): Robin Williams, Theo Von, Jimmy Carr, Sean Lock, Acaster,
  Joe List, KT regulars (Montgomery, Hans Kim, Cam, Casey), Schulz, Kreischer, Segura.

## Thread 3 — transcripts at scale (all comedians)
- Found HuggingFace `zachgitt/comedy-transcripts` (419 specials) + scrapsfromtheloft (600).
- Downloaded all: 174 comedians, 383 files → 181 graphs (48 curated + 10 wave3
  + 123 transcript-grounded auto-drafts with measured vocabulary, flagged review).
- Wave 3 seeds: Jefferies, Gervais, Noah, Ansari, Jeselnik, Brennan, Oswalt,
  Regan, Maniscalco, Birbiglia.
- Thin-comic rescue: 34 sets for Wong/Burnham/Normand/Bargatze/Silverman/
  Tomlinson/Bamford/Che/Buress/Kreischer/Segura/Demetri + known_bits for 16.

## Thread 4 — canonical resource (bios, generations, ratings, recognition)
- `enrich_bios.py`: Wikidata DOB/birthplace/occupations (91+, still running).
- `enrich_generations.py`: breakthrough-era generations (167 assigned) —
  Seinfeld/Rock same gen by construction, not birth year.
- `enrich_ratings.py`: IMDb public datasets (83k comedy entries) → 216 matched
  specials with ratings/votes/years, standout flagged. Fixed Pixar-Up + Mo-Amer bugs.
- `enrich_recognition.py`: CC2004 (98/100) + RS2017 (50/50) + Wikidata awards
  (P166: Grammys, Mark Twain, Emmys) + trajectories.

## Thread 5 — rankings science (arXiv-grade)
- `RANKINGS.md`: Arrow/Kemeny/Borda/Bradley-Terry theory, prior art, our design.
- `rank_comedians.py`: Borda legs → weighted sum → local Kemenization →
  consensus + disagreement + by-generation boards.
- `fit_weights.py` shocker: CC-only predicts RS2017 (0.692) BETTER than
  weighted sum (0.658) → legs disagree → split boards (GAPS.md).
- Era-normalization: within-generation z-scores (median, missing=neutral,
  min group 5). Era top: Chappelle/Hicks/Carlin/Burr/Pryor/Robin/Louis/Hart.
- `PAPER.md`: full arXiv draft (abstract → validation roadmap → limitations).
- `TOP2026.md`: our 2026 election (arena + recent specials + views + critic survey).

## Thread 6 — proprietary metrics (RT model)
- `METRICS.md` + `metrics.py`: CANON/CROWD/PULL/HEAT/CRAFT + GAP/canon-lag.
- Live: overrated Fluffy +0.83; underrated Hicks −0.75, Stewart Lee −0.70;
  balanced Burr/Chappelle. The gaps write their own headlines.

## Thread 7 — YouTube (popularity, not quality)
- Search-based harvest → quota death → **no-search law**: registry channels.json
  + uploads playlists (~1 unit/50 vids). 240 clips with views/likes/comments.
- Complete pulls: Normand 100/30M, Louis 79/50M, Norm 9/8.7M (invisibility explained).
- Subs brackets: micro/small/mid/big. Micro find: 6.4k-sub channel, 2.4M-view KT comp.

## Thread 8 — weekly pulse (fast board)
- `pulse.py`: snapshots → velocity → trending clips, comedian-of-week.
  First snapshot W42 (230 videos). Velocity unlocks on snapshot #2.
- Comment mining: sentiment (weak — needs comedy lexicon), timestamp laughs,
  GOAT calls. `fanbase.py`: fingerprints, overlap (needs breadth), learned lexicon.

## Thread 9 — specials + humor types (algorithm fuel)
- `rankings/specials.json` (197 best all-time): Inside 8.6, Dress to Kill 8.6.
- Darkest (87), by-type boards. 14 humor types from archetype+theories+transcript.

## Thread 10 — discovery (indies, for-you, spotlight)
- Unified schema decision: tier field, NOT separate graph (evidence: 123
  auto-drafts already live fine with nulls). 53 indies migrated.
- `recommend.py`: TF-IDF latent space, neighbors.json. Validated Hedberg→Wright 0.92.
- `indie.py`: for-you matcher + spotlight queue (Kam Patterson 0.69 theory).
- Theory_score = fame-blind joke quality (coherence + NoSlop over material).

## Thread 11 — global (21 regions)
- Region tagging (148: bio + overrides), continent boards.
- Nigeria (7: Alibaba→Basketmouth lineage), Japan (manzai decoded, standup-only kept),
  India (7: Zakir 960M), China (8: Xiaoguo EN channel registered),
  LatAm+Spain (19), Aus/NZ (11), Europe (13).
- `COUNTRY_THEORY.md`: 7 variables (tsukkomi, taboo, censorship, solo/duo,
  language play, status, distribution).
- Cross-nation similarity: Hicks→Lee 0.56 (real lineage!), Pryor→Noah.
- Netflix viewership leg: 7 official reports → 347 specials with hours.
  Gillis Beautiful Dogs 26.5M hrs (#3 debut).

## Open loops (running now)
- enrich_bios at R/181 (awards leg + bio coverage depend on it)
- YouTube search quota resets midnight Pacific (subs backfill for ~120)
- Pulse snapshot #2 Monday (velocity mode)
- 84 region-unknowns (mostly KT names) await bios/authoring

---

## PRIORITY — best places to start (ranked)

### P0 — Ship TOP 2026 ballot (the differentiator)
Nothing else makes us definitive. Open arena battles + send critic survey.
Without fresh 2026 legs, we're a better-arranged museum. With them, we're
the election. Owner actions: approve ballot design, seed voter list.

### P0 — Draft 3 episodes (public proof)
Gillis, Theo, Carlin. Graphs are ready; scripts are half-written in
essay_seeds. Videos prove the resource publicly and feed the funnel.
No dependencies — start today.

### P1 — Monday pulse #2 (velocity unlock)
Second snapshot → first real trending chart → first pulse post. Scheduled,
no decisions needed. Enables HEAT metric + rising-star board.

### P1 — Bios to completion (fills gaps behind everything)
Awards leg (13→50+), bio coverage (91→181), region unknowns (84→~20).
Running; just needs time. Check R→Z progress.

### P2 — Small-channel backfill (quota reset)
~120 comics' subs + brackets. Unlocks discovery boards fully. Midnight PT.

### P2 — Human-review top auto-drafts
Gaffigan, Norton, Maron, Iglesias, Cummings, Epps, Tom Papa — 3+ specials
each, one review pass turns drafts into curated.

### P3 — Whisper timing pipeline (DPV at scale)
4 measured sets → 20+. Highest-value ML unlock (timing→rating).
Needs audio access decisions.

### P3 — Xiaoguo subtitled harvest (China proof)
Registered channel + tlang pipeline = first non-English theory graphs.
Validates the global thesis.

---

## Addendum — autonomous session (10 threads, same day)

1. **41 signature titles** added (Burr rage auditor, Mulaney anxiety architect...).
2. **Pulse snapshot #2** (540 videos) + versioned snap IDs (velocity-ready).
3. **Xiaoguo harvest**: 100 clips/159k views, EN-titled taboo-adjacent sets. Captions unavailable (no tracks) — recorded, whisper path noted.
4. **Basketmouth harvest**: 100 clips/12.5M views (Nigeria's digital footprint).
5. **BALLOT_2026.md**: critic survey design (top-20 + breakout + underrated + best special + pairwise, anti-brigading rules, Nov 30 deadline).
6. **ARENA_BALLOT.md**: blind A/B battles → Bradley-Terry, 3-phase pairing, integration spec.
7. **First episode draft**: episodes/why-shane-gillis-funny.md (thesis + numbers + 3 bits + sources).
8. **5 auto-draft reviews**: Gaffigan, Norton, Maron, Iglesias, Cummings → curated identity/theses.
9. **Pulse snap versioning** fix (multiple snapshots per week).
10. **This log update.**
