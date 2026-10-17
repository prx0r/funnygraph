# THEORY — how good the jokes are (feeds FUNNIER, not displayed)

> PRESENTATION CHANGE (2026-10-17): the profile lens slot is now FUNNIER
> (house percentile). Theory depth/content below still computed — v1 feeds
> house P2, v2 feeds house P1 and the per-type boards — but profiles show
> FUNNIER, not THEORY. This doc is the computation spec, not the display.

**One line:** documentation depth (v1, live) + measured joke quality
(v2, live for 18 comics from characters2 bit annotations).

## Formula v1 — depth (all 293, live in metrics.py)
+3 known_bits (capped) +2 essay_seeds/2 +2 measured timing present
+1 timing doctrine present, over 8 → 0-100.

## Formula v2 — content (18 measured comics, live in theory_content.py)
Per comic, from 29,617 theory-tagged bits (characters2, read live):
mean calibrated paper score + p90 + mean benign_violation/economy/
incongruity + operator entropy (breadth) + laugh-density aggregates.
Ranked within humor_type (n≥200 bits gate) → best-jokes-per-type boards:
7 types covered (dark-confessional 5, rant 4, absurdist/character/
observational/storytelling 2 each, meta 1 = thin).

Current v2 top (mean paper): Carlin .0250 (rant) · Seinfeld .0243
(observational) · Norm .0242 (absurdist) · Louis .0237
(dark-confessional) · Rock .0233 (observational).

## Fitted mechanism weights (stand-up THInC-analog)
Mean paper | operator present: mistake_identity +.0065 · juxtapose
+.0047 · status_invert +.0038 · repeat_variation +.0020 over global
mean; split_knowledge (commonest, n=3011) −.0014 — frequency ≠ quality.
M5-redo: authored priors vs measured rates, mean Pearson +.18 over 18
comics (old text-proxy M5: −.05). Best-authored: Chappelle .795, Bruce
.682, Mulaney .609. Authoring beats proxies but stays weak — priors
need per-theory proxy discipline (THInC pattern), scheduled.

## Inputs
- v1: `known_bits[]`, `essay_seeds[]`, `sets[].timing_measured`,
  `timing_profile.doctrine_hypothesis` (authored/measured in-graph)
- v2: characters2 `bits_theory.json` + `bits_annotated/` (ops) +
  `ml/operator_frequency.json` + `ml/laugh_density.json`, joined on
  identical slugs; funnygraph `humor_type.primary` for type boards.
  Output: `rankings/theory_content.json`.

## Justification
The only lens measuring the WORK rather than its reception. v1 predicts
video-script readiness and agent-harness writability (operational, not
ornamental). v2 answers "who has the best jokes in each type" with
laughter-fitted scores, not documentation effort — the lens's stated
limitation, now half-closed. Closest prior art: humour quotient 0-4 from
laughter duration (arXiv 2110.12765, clip-level; ours career-level) and
THInC per-theory weights (arXiv 2409.01232, joke-level; ours
mechanism-level for stand-up). Full theory grounding: PAPER_ARXIV.md §2.6.

## Limitations
- v1 rewards documentation effort, not just craft. Flagged as such.
- v2 covers 18/178 kings; 6 of 13 types have zero measured comics.
  Unmeasured comics keep v1 only — badges distinguish, never blend.
- Paper rubric held-out AUROC 0.5715 (weak but honest); bit quality is
  a noisy proxy, reported with n everywhere.
- Cannot compare across eras without era controls (v1 raw depth; v2
  within-type only — cross-type comparison unscheduled).

## References
arXiv 2110.12765 (humour quotient) · arXiv 2409.01232 (THInC) ·
characters2 theory lane (live dependency) · PAPER_ARXIV.md §2.6, §4.11.

## Roadmap (v3)
Per-theory proxy features + fitted weights (Mallows pattern on
operators); GTVH SO/LM fill from measured bits (shell exists in 32
graphs); HSQ-style per-comic scores; quote_rate (F3) + laughmap (F4)
as behavioral validation of theory tags.
