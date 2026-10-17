# COMEDIAN AXES — plottable schema (v1, 2026-10-15)

Normalized dimensions extracted from every `theory/comedians/*/comedian-graph.json`
so any two performers can be plotted against each other on shared,
theory-grounded axes. This is the endgame artifact: the graphs are the
deep stores; this is the projection layer for comparison, arena matching,
and the "back-to-back" analysis videos.

Every value is a **hypothesis** unless marked `measured`. Sources cited
per axis. Values are 0-1 unless noted. Categorical axes use fixed
vocabularies so distance is computable.

## The roster

| id | file | sets | status |
|---|---|---|---|
| louis-ck | louis-ck/comedian-graph.json | 1 partial (roadrage) | timing measured, rest hypothesis |
| norm-macdonald | norm-macdonald/comedian-graph.json | 1 partial (moth, ASR-noisy) | timing measured, rest hypothesis |
| jerry-seinfeld | jerry-seinfeld/comedian-graph.json | 0 | all hypothesis |
| dave-chappelle | dave-chappelle/comedian-graph.json | 0 | all hypothesis |
| mitch-hedberg | mitch-hedberg/comedian-graph.json | 0 | all hypothesis |
| george-carlin | george-carlin/comedian-graph.json | 0 | all hypothesis |
| chris-rock | chris-rock/comedian-graph.json | 0 | all hypothesis |

## Axes

### A1 — Status capital (0=zero, 1=peak legend)
What they bring into the room that the room already grants them.
Theory: status economics from louis-ck/personality.md §Framework 4.
- louis 0.00 (measured-from-persona: nothing to lose)
- hedberg 0.25 (cult favorite who wished you'd stop calling him the next X)
- norm 0.45 (comics' comic; capital held in reserve as independence)
- seinfeld 0.70 (elder statesman; observational distance needs implied superiority)
- carlin 0.75 (prophet with a following; institution he claimed to hate)
- chappelle 0.85 (legend who quit and returned on his own terms)
- rock 0.85 (the voice that names it first; still pacing like he's got something to prove)

### A2 — Exit strategy (categorical, from the status game)
How they position relative to the status contest everyone else is in.
Vocabulary: `floor` | `chair` | `outside` | `chain` | `pulpit` | `throne` | `courtroom`
- louis: `floor` — exited from below; zero capital, confesses from the floor
- norm: `chair` — exited into the philosopher's chair; defends the joke from there
- seinfeld: `outside` — never entered; audits from outside the mess
- hedberg: `chain` — never played; reloads one-liners like a machine that doesn't know there's a game
- carlin: `pulpit` — became the sermon; capital spent on prophecy
- chappelle: `throne` — left the throne, came back to it; capital is the exit itself
- rock: `courtroom` — never left; prosecutes from inside the system he's indicting

Distance: any two different categories = maximally distant (nominal, not ordinal).

### A3 — Timing doctrine (categorical + measured sub-axes)
Vocabulary: `big_stop` | `never_stop` | `surgical` | `sermon` | `percussive` | `reload`
- louis: `big_stop` (measured: 57 pauses, max hold 8.16s, holds mid-story at darkest turns)
- norm: `never_stop` (measured: 6 pauses/2min, holds harden toward punch 1.16→1.58)
- seinfeld: `surgical` (hypo: short holds ~400/900ms, riff-restarts)
- chappelle: `sermon` (hypo: sprints in character, holds 2-3s+ after heavy point)
- rock: `percussive` (hypo: stammer-build, hard-stop punch, short hold for the 'I know' wave)
- hedberg: `reload` (hypo: setup-punch-restart, 300-500ms, no story mode)
- carlin: `sermon` (hypo: list accelerates, key word lands like gavel, hold for congregation)

Numeric companions (measured where available):
- pauses_per_min: louis 28.5 (measured) | norm 3.0 (measured) | others null
- max_hold_s: louis 8.16 (measured) | norm 1.7 (measured) | others null
- hold_placement: `mid_story` (louis, measured) | `pre_punch_escalating` (norm, measured) | `post_point` (chappelle/carlin, hypo) | `between_chain` (hedberg/seinfeld/rock, hypo)

### A4 — Target direction (TA, GTVH)
Who the butt is. Vocab: `self` | `peers` | `powerful` | `systems` | `objects` | `code`
- louis: `self` (measured from roadrage TA=self on every beat)
- norm: `self` / `none` (hypo: defends the joke; the butt is often the premise itself)
- seinfeld: `code` (hypo: the unwritten custom is the target; never a person)
- chappelle: `systems` (hypo: race, fame, power — the room indicting itself)
- rock: `systems` / `peers` (hypo: social groups, in-group contradictions)
- carlin: `systems` / `powerful` (hypo: euphemisms of power; language as target)
- hedberg: `objects` (hypo: never punches a person; objects with secret lives)

### A5 — HSQ humor styles (0-1 each, from personality.md framework 1)
Martin et al. 2003 four-style model. Only louis/norm have full personality.md;
others hypothesis from persona shape.
- self_defeating: louis .95 (meas-adj) | hedberg .35 | norm .20 | chappelle .20 | rock .30 | seinfeld .15 | carlin .10
- self_enhancing: norm .90 | chappelle .70 | louis .70 | carlin .60 | rock .60 | seinfeld .50 | hedberg .60
- affiliative: hedberg .70 | seinfeld .60 | chappelle .50 | rock .50 | louis .50 | norm .40 | carlin .20
- aggressive: carlin .85 | rock .60 | chappelle .45 | norm .45 | seinfeld .35 | louis .10 | hedberg .10

### A6 — Big Five persona estimates (0-1)
From personality.md where available; hypothesis elsewhere. NOTE: these
describe the STAGE PERSONA, not the person. Ruch et al. 2009 found real
comedians score low-C/low-E/low-A vs students — persona often inverts
the population (Norm's persona is high-C; flagged in his personality.md).
- openness: carlin .95 | hedberg .95 | chappelle .85 | norm .90 | seinfeld .70 | rock .70 | louis .75
- conscientiousness: norm .95 | seinfeld .90 | carlin .85 | rock .75 | chappelle .70 | hedberg .50 | louis .25
- extraversion: rock .75 | seinfeld .60 | carlin .65 | chappelle .55 | louis .45 | norm .30 | hedberg .25
- agreeableness: hedberg .60 | seinfeld .50 | chappelle .40 | norm .45 | louis .35 | rock .30 | carlin .15
- neuroticism_display: louis .85 (high-N display) | rock .45 | seinfeld .45 | chappelle .35 | hedberg .40 | carlin .30 | norm .30 (low-N display)

### A7 — Awareness (0=unaware, 0.5=fluctuating, 1=aware)
Head's frame: unaware failings = unearned-confidence comedy; aware = neurotic;
Norm's fluctuating = plays unaware, hyper-aware underneath.
- unaware 0.0 | fluctuating 0.5 | aware 1.0
- louis 1.0 | seinfeld 1.0 | chappelle 1.0 | carlin 1.0 | rock 1.0
- norm 0.5 | hedberg 0.5
(The two 0.5s are the constructed innocents — the Prestige-trick family.)

### A8 — Operator signature (top operator priors, from graphs)
Not a single axis — a fingerprint vector. Plottable as radar.
- louis: split_knowledge .85, expose_self_blindness .8, character_violation .75, double_interpret .7
- norm: false_analogy .9, repeat_variation .85, split_knowledge .7, double_interpret .65
- seinfeld: rigidify .95, literalize .85, double_interpret .65
- chappelle: split_knowledge .9, double_interpret .85, status_invert .75
- hedberg: literalize .9, double_interpret .85, rigidify .6
- carlin: rigidify .9, literalize .8, double_interpret .75, status_invert .7
- rock: double_interpret .85, status_invert .75, split_knowledge .7

### A9 — GTVH SO/LM/NS fingerprint
Same idea at the KR level (gtvh.py vocab).
- SO: louis caring/cruel | norm normal/absurd | seinfeld normal/absurd | chappelle normal/absurd-social | hedberg normal/absurd | carlin sacred/profane | rock normal/absurd-social
- LM: louis garden_path+perspective_shift | norm false_analogy+garden_path | seinfeld rigidify | chappelle double_interpret+status_invert | hedberg literalize+double_interpret | carlin rigidify+literalize | rock double_interpret+juxtapose
- NS: louis anecdote | norm narrative | seinfeld one-liner-chain/monologue-list | chappelle anecdote/character-chain | hedberg one-liner-chain | carlin monologue-list | rock monologue-list/anecdote

## Recommended plots (4-way and 2-way)

1. **Status × Exit** (A1 × A2) — the triangle/quadrant we've been building:
   floor(chappelle? no, louis) vs chair(norm) vs outside(seinfeld) vs the rest.
   Best 2D view of the "who can say what" question.
2. **Timing doctrine map** (A3 categorical + pauses_per_min × max_hold_s) —
   the measured scatter once more sets land. Currently: Louis top-right
   (many pauses, long holds), Norm bottom-left (few pauses, short holds).
   The other five fill in as data arrives.
3. **HSQ plane** (self_defeating × aggressive) — the tortured-vs-resolute
   reading. Louis alone in the high-SD corner; Carlin alone in the
   high-Ag corner; Norm top-right on self_enhancing (the resolute cell).
4. **Big Five radar** (A6) — persona shape as polygon. Norm's high-C/low-N
   polygon vs Louis's low-C/high-N is the starkest contrast.
5. **Operator radar** (A8) — the mechanism fingerprint. Seinfeld's
   rigidify-heavy shape vs Chappelle's split_knowledge-heavy shape.
6. **Awareness × Self-target** (A7 × A4) — the two constructed innocents
   (Norm, Hedberg) cluster at fluctuating/non-self; the aware confessor
   (Louis) is alone at aware/self.

## Provenance rules (inherit from SPEC-comedian-analysis.md)

- Every plotted value carries measured|hypothesis status from its graph.
- Never plot a hypothesis against a measurement without labeling both.
- n>=3 sets before any operator/HSQ value leaves hypothesis.
- Stage persona only — these axes describe performers-as-acted.
- The projection is derived; the graphs are the source of truth. When
  a graph updates, regenerate this file (it's a view, not a store).

## How this feeds the system

- **Arena matching**: pair maximally-distant comics on A3 (timing) or
  A4 (target) for contrast bits; pair near-neighbors for the
  "same mechanism, different voice" comparison videos.
- **Comparison videos**: A3 + A1 + A4 give the back-to-back script
  skeleton — two timing doctrines, two status positions, two targets,
  played against the same scenario.
- **New comic intake**: fill this file's row first from public persona,
  then let measured sets correct it. The row IS the falsifiable claim.
- **Freak casting**: a freak's WHO cell can be checked against this
  table to find which real comic's exit-strategy it occupies (e.g. the
  empty `chair` cell in our freaks roster = a Norm-shaped creature).
