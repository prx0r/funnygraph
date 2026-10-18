# PRODUCTION — how the video pieces fit together

## Read order (for a producer or next agent)

1. `SERIES.md` — WHAT we're making (5 series, episode maps, reference channel)
2. `production/FORMULA.md` — the decoded 11-beat gold structure + tone rules
3. `STRUCTURES.md` — HOW each episode works (18 frameworks, data-driven)
4. `BEAT_MAP.md` — WHEN things happen (60-min v2 arc + MUSIC overlay)
5. `production/LITERATURE.md` — timing/music research backing the moves
6. `production/GOLD.md` — WHAT it sounds like (Louis Monopoly, Nerdwriter)
7. `production/GOLD-LOCKE.md` + `GOLD-LOCKE-FULL.md` — CwE Sean Lock (notes + full transcript)
8. `production/GOLD-CARLIN.md` — rhythm/delivery Carlin essay (full transcript)
9. `production/ACASTER-GOLD.md` — unreliable narrator Acaster/Lee (full transcript)
10. `production/PALETTE.md` — WHAT it looks like (colour per comedian)
11. `episodes/louis-deconstruction-spec.md` — the ONE fully-specified episode (v3, gold-formula)

## The system

```
SERIES.md defines the WHAT
  ↓
FORMULA.md defines the BEAT ORDER (11-beat gold arc + tone rules)
  ↓
STRUCTURES.md defines the HOW (18 frameworks, all data-driven)
  ↓
BEAT_MAP.md v2 defines the WHEN (60-min revised arc, MUSIC overlay)
  ↓
LITERATURE.md backs the moves (timing is a cognitive mechanism)
  ↓
GOLD transcripts define the VOICE (4 references, ~157 min total)
  ↓
PALETTE.md defines the LOOK (colour, typography, face treatment)
  ↓
The comedian graph fills the CONTENT
  ↓
BEAT_MAP + STRUCTURES generate the EPISODE BLUEPRINT (JSON)
  ↓
A video editor follows the blueprint
```

## What's built vs what's missing

| Piece | Status | Notes |
|---|---|---|
| SERIES.md | ✅ built | 5 series + reference channel (Comedy Without Errors) |
| FORMULA.md | ✅ built | 11-beat gold arc decoded from 4 transcripts + tone rules |
| STRUCTURES.md | ✅ built | 18 frameworks (14 original + LENS/CHARACTER/DISCOVERY/FAIRNESS) |
| BEAT_MAP.md | ✅ built | v1 preserved + v2 revised arc + MUSIC overlay grammar |
| LITERATURE.md | ✅ built | 5 core papers + supporting findings + safe-claims list |
| GOLD.md | ✅ built | Nerdwriter Louis Monopoly bit |
| GOLD-LOCKE.md | ✅ built | CwE analysis notes (10 moves) |
| GOLD-LOCKE-FULL.md | ✅ built | Full CwE transcript, 27 chapters, ~70 min |
| GOLD-CARLIN.md | ✅ built | Rhythm/delivery essay, 14 chapters, ~34 min |
| ACASTER-GOLD.md | ✅ built | Unreliable narrator essay, ~46 min |
| PALETTE.md | ✅ built | 9 confirmed colours + 13 suggestions + rasa mapping |
| Louis spec | ✅ v3 built | Gold-formula revision on top of v2 essay form |
| characters2 UNRELIABLE-NARRATOR.md | ✅ built | Named device + 5 variants + operator stack |
| Gillis draft | ✅ built | 8-10 min episode (Gillis template) |
| Theo draft | ✅ built | 8-10 min episode (establishment gap thesis) |
| Carlin draft | ✅ built | 8-10 min episode (control group thesis) |
| Episode blueprint generator | ❌ missing | The script that turns graph → JSON blueprint |
| Motion graphics templates | ❌ missing | After Effects / Remotion components |
| Narrator voice recording | ❌ missing | The actual voice |
| Clip library | ❌ missing | Timestamped clip index per comedian |
| Interview mining pipeline | ❌ built (Structure 11) | Needs YouTube search per comedian |
| Self-analysis extraction | ❌ built (Structure 11) | Needs interview transcripts |

## The gap: blueprint generator

The missing piece is a script that takes a comedian_id and outputs
the episode blueprint JSON. It would:

1. Load the graph → extract thesis, engine, timing, bits
2. Apply STRUCTURES.md frameworks → select cold open, montage bits,
   comparison targets, interlude placement
3. Apply BEAT_MAP.md timing → assign second-by-second positions
4. Apply PALETTE.md → fill visual identity
5. Apply GOLD.md tone → generate narrator copy templates
6. Output: episode blueprint JSON → script → production notes

This is the bridge between "we have data" and "we have a video."
