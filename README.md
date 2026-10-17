# funnygraph

> Comedian graphs for the **"Why is X Funny?"** video series.
> One graph per comedian = one episode spine: the engine, the misinterpretation
> rule, the threads, the operator priors that make the laugh inevitable.
>
> **THE comedy database: theory applied to every comedian.** Every graph carries
> style_thesis, timing_doctrine, known_bits (signature bits with why-they-work),
> academic theory_links, essay_seeds, and transcript/measured links where
> available. The Louis/Norm measured graphs are the depth bar; every other
> graph is heading there.

Schema: `pogtown.comedian.v1` (same as `characters2/theory/comedians`).
Every value is **hypothesis** until sets are ingested. No verbatim bits.
Stage persona only — no biography.

## Roster (48)

**Copied from characters2 (7):**
Carlin · Chappelle · Chris Rock · Hedberg · Louis CK · Norm Macdonald · Seinfeld

**Wave 1 (28):**
Gillis · McCusker · Pryor · Hicks · Dangerfield · Lenny Bruce · Rivers · Burr ·
Steven Wright · Emo Philips · Demetri Martin · Stewart Lee · Dylan Moran ·
Normand · Bargatze · Mulaney · Burnham · Ali Wong · Tomlinson · Gulman ·
Bamford · Buress · Che · Silverman · Stanhope · Izzard · O'Neal · Giraldo

**Wave 2 (13):**
Robin Williams · Theo Von · Jimmy Carr · Sean Lock · James Acaster · Joe List ·
William Montgomery · Hans Kim · Cam Patterson · Casey Rocket · Andrew Schulz ·
Bert Kreischer · Tom Segura

| Tier | Comedians |
|---|---|
| User's GOATs | Shane Gillis · Matt McCusker |
| Legends | Richard Pryor · Bill Hicks · Rodney Dangerfield · Lenny Bruce · Joan Rivers |
| Modern GOATs | Bill Burr |
| Craft icons | Steven Wright · Emo Philips · Demetri Martin |
| Meta architects | Stewart Lee · Dylan Moran |
| Working comics | Mark Normand · Nate Bargatze · John Mulaney · Bo Burnham |
| New school | Ali Wong · Taylor Tomlinson · Gary Gulman · Maria Bamford |
| Culture critics | Hannibal Buress · Michael Che · Sarah Silverman · Doug Stanhope |
| Unsung goats | Eddie Izzard · Patrice O'Neal · Greg Giraldo |

## Tooling

| Script | What it does |
|---|---|
| `seed_comedians.py` / `seed_wave2.py` | author hypothesis graphs (wave 1 / wave 2) |
| `deepen_graph.py` | upgrade every graph to theory depth: style_thesis, timing_doctrine, known_bits, theory_links, essay_seeds, transcript links |
| `harvest_captions.py` | YouTube captions (InnerTube, works when yt-dlp is IP-blocked) → scribe word JSON |
| `analyze_set.py` | scribe JSON → timing_measured + punch_candidates + beats (vendored from characters2, path-fixed) |
| `profile_comedian.py` | YouTube search + captions + analysis + distinctive-term lift → graph-patch JSON |

```
scribe/    word-timed transcripts (scribe format)
analysis/  timing + punches + profiles + graph patches
```

## Depth levels

```
LEVEL 1 — hypothesis graph (all 48)
  identity / misinterp / priors / threads / style_thesis / timing_doctrine
  → enough for a "Why is X Funny?" episode draft

LEVEL 2 — transcript-linked (16 comics with characters2 specials)
  sets[] with titles + word counts; content available for topics extraction
  → Carlin 19 · Chappelle 15 · Louis 11 · Rock 9 · Burr 8 · Mulaney 5 · Pryor 4 · Hicks 4 · Izzard 4 · Lee 4 · Norm 3 · Seinfeld 2 · Robin 1 · Bruce 1 · Hedberg 1 · KT regulars (scribe)

LEVEL 3 — measured (Louis roadrage, Norm moth, WT/Kam/Casey KT sets)
  timing_measured, pause_bins, punch holds, beat_decomposition
  → THIS is what makes the video undeniable
```

## What's in a graph

```
identity.deal                 one-sentence engine
identity.misinterpretation_rule  THE lens (the video's thesis)
identity.operator_priors      rigidify / literalize / double_interpret / status_invert / character_violation
identity.threads              5 episode seeds per comic
identity.problem_space        what they're actually about
identity.physosophy           ontology / epistemology / axiology / causality / agency
identity.dramatic_core        want / fear / need / self_model / blind_spots
essay_seeds[0]                "Why is X funny?" outline scaffold
```

## Making a "Why is X Funny?" episode

1. Open `comedians/<id>/comedian-graph.json`
2. Thesis = `identity.misinterpretation_rule`
3. Structure = `essay_seeds[0].outline`
4. Evidence = `threads` + `operator_priors` + (when available) measured `timing_profile`
5. Compare on axes: `comedians/axes.json` (shared projection layer)

## Pipeline hookup

These graphs feed the same agent harness as characters2:

```bash
# copy a graph into characters2's roster and run the writer
python3 characters2/theory/agent_harness.py --only shane-gillis --writer llm
```

Or point the harness at this repo's `comedians/` directory.

## Rules

1. Stage persona only — no biography, no private life.
2. No verbatim bits anywhere in the graph.
3. 0 sets = all hypothesis. Mark `measured` only with ASR evidence.
4. Historical/commercial figures: persona-as-acted, not the person.
5. Axes values are projection, not store — graphs are the source of truth.

## Status

- [x] 35 graphs authored (hypothesis)
- [ ] Ingest 1 signature set per comic (ASR, word-timed)
- [ ] Measure timing → fill `timing_profile.measured`
- [ ] Regenerate `axes.json` across full roster
- [ ] First 3 episode scripts: Gillis, Carlin, Pryor
