# funnygraph

> Comedian graphs for the **"Why is X Funny?"** video series.
> One graph per comedian = one episode spine: the engine, the misinterpretation
> rule, the threads, the operator priors that make the laugh inevitable.

Schema: `pogtown.comedian.v1` (same as `characters2/theory/comedians`).
Every value is **hypothesis** until sets are ingested. No verbatim bits.
Stage persona only — no biography.

## Roster (35)

**Copied from characters2 (7):**
Carlin · Chappelle · Chris Rock · Hedberg · Louis CK · Norm Macdonald · Seinfeld

**New (28):**

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
