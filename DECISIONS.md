# DECISIONS — the log of binding calls (2026-10-17 sessions)

> Every rule below was paid for (quota burn, junk drafts, false flags, or a
> failed test). Reversing one requires re-paying: cite the incident,
> re-run the validation, update code + papers + this file together.
> Owner calls marked (owner). Everything else is agent-built, owner-tolerated.

## Ranking doctrine

1. **No single number without uncertainty** — every board ships leg
   breakdowns; every position ships an interval (stability 71 regimes or
   house sweeps). Rejected: point-estimate crowns.
2. **Never blend what disagrees** — fit_weights proved CC-only 0.692 >
   weighted 0.658. Split CANON/PEOPLE'S; consensus demoted to legacy view.
   Rejected: better-weights tinkering.
3. **House is first-party only (owner)** — critics/IMDb/awards/Netflix/YT
   counts are display-only reference, never inputs. Awards prestige moved
   to reference too (external judgments; facts kept). Rejected: prestige leg.
4. **FUNNIER replaces theory at presentation** — house percentile is the
   quality slot; theory depth feeds P2 behind it. Rejected: two quality numbers.
4b. **House scoring corrected (v2, 2026-10-17 audit)**: P1 shrunk by
   sample size (k=500 Empirical-Bayes); P2 capped as modifier (+15% max),
   never co-equal. P2-only comics get NO rank (no joke-quality data means
   no rank on a joke-quality board — owner caught Bert at #11 with zero
   P1). Norm was #1 under v1 because his graph had measured timing
   (characters2 coverage artifact, not craft signal). Under any
   sample-size adjustment, Carlin wins (4478-bit sample + highest paper).
   Rejected: co-equal P1/P2 legs; P2-only ranking.
5. **Weights fitted, else plain mean** — Mallows precision where fittable
   (canon .634/.366); house = mean of available legs until 50+ measured.
   Rejected: all asserted weights (3/2/1 survives only in legacy consensus).
6. **Missing = neutral, never rewarded/punished** — z=0, excluded from
   denominators, median-not-mean, min group 5. Rejected: mean-centering
   (giants cratered good comics), rewarding emptiness (Ellen-style wins
   on absent data, caught twice).
7. **Withheld, not shown** — zero-leg profiles get NO board ranks and NO
   intervals (they're ties at zero = noise). Provisional headline only,
   method stated. Rejected: bottom-rank display.
8. **Nulls ship** — HEAT null (no proxy faked), momentum shown-not-blended.
   Rejected: plausible-looking proxies.
9. **Borda + local Kemenization, not exact Kemeny** — 5-approximation with
   guarantee (Dwork) at O(n log n); exact is NP-hard at n=178. Validated:
   BT order agrees τ=.876. Kemenization cost unweighted (known inconsistency,
   v0.3 work).
10. **Postdate distinction, stated precisely** — postdate excluded, contemporary
    scores 0; admitted the distinction is NOT operational in the Borda sum
    itself (only in z-gates/disagreement/badges). Rejected: marketing it.
11. **Era = breakthrough decade, not birth** — Seinfeld/Rock same gen by
    construction. Cusp cases flagged, not smoothed.
12. **WR calibrated to corpus (m=500, C=7.5)** — film defaults drowned
    specials signal. Crowd *display* stays raw (what viewers said) while
    *ranking* uses shrinkage; duality open, both documented.

## Data doctrine

13. **No YouTube search, ever** — quota death (100u/guess) → registry
    channels + uploads playlists (~1u/50). Retired script kept as
    `_LEGACY` warning. forHandle/forUsername handle resolution (1u) is
    registry administration, NOT search (verification gate is the line).
14. **Full names only for mining** — "che" is Italian, "Martin" is Fluffy's
    buddy. Singles queue as needs-full-name, never draft.
15. **Comedian-name-in-title for IMDb matches** — Pixar's Up struck 3 times.
16. **Standup only** — manzai duos removed; discovery skips duos
    (brothers/sisters/twins), roasts (ROAST_RE titles), actors/podcasters/
    musicians found in comic channels. Roast *type* kept for kings;
    discovery scope is sets-only (owner).
17. **Press compilers precision-ordered** — Deadline (stand-ups-first, no
    groups/SNL/repeats) gold; Vulture quarantined to confirmed standups
    (sketch/improv/clown mix); Edinburgh = Fringe-hour standups, duos
    skipped; festivals map to NO region (international by format).
18. **Venue-scene regions, method-stated** — Angel→uk, KT/DTC/DryBar→us,
    Xiaoguo→china, Basketmouth→nigeria, TimeOut→us. Overwritable on origin
    evidence. Stored as region_method, not silent.
19. **Socials evidence-only, never metrics** — a million followers moves no
    number. YouTube sole measurement source (only legal time-series APIs).
20. **Secrets in .env only**; secret-scan before push. Owner pushes.
21. **IMDb 83k index lives in /tmp** — regenerate risk accepted, noted
    (persist to data/ when touched next).

## Discovery doctrine (each guard has an incident)

22. **Audit every batch before rate.py** — 190 junk drafts (bit-titles),
    18 actor/movie/game-word drafts, 13 roast drafts, 3 segment drafts.
    All purged same-day; guards below prevent recurrence.
23. **Show-titles only for name mining** — clip/special titles never yield
    names. Episode-or-recurrence draft rule (KT #NNN marker or seen ≥2).
24. **Blocklists are incident logs**: SHOWNAME (segments/shows), ROAST_RE
    (battles/beefs), COLLISION_BLOCK (Liam Nelson DJ), DUO_RE.
25. **Marker-adjacency extraction** — "Bit | NAME FULL SPECIAL": names come
    from the marker's segment (Rabbit Hole rule).
26. **Spaced-hyphen splitting** — bare-hyphen split corrupted "Catta-Preta"
    into junk slug "jade-catta".
27. **Channel links need freshness + ownership** — active/stale/dormant/
    variety via audit; fountain/collision links unlinked. Clip-title hit
    rates measure title conventions, NOT ownership (18 false flags) —
    channel-title reverify instead.
28. **Tier line (owner)** — national credits = king; literally-unknown =
    indie. Press lists never demote. Corrections on audit (6 KT guests,
    Spittle, 6 Angel, 20 KT backfill). Borderline stays indie (DISCOVERY
    is honest; canon promotable later).
29. **Human promotes, nothing auto-promotes; everything auto-rates.**
30. **Bio prose is style evidence, never material** — venue-bio excerpts
    seed deal hypotheses; verbatim acts never ingested (fair-use analysis
    of transcripts only, per characters2 precedent).

## Theory doctrine

31. **M5 failure published, then retested properly** — text-proxy r=−.05
    stood until characters2 measured rates allowed the direct test (+.18).
    Proxy-discipline program (THInC pattern) is next.
32. **known_bits without verbatim** — title + why + theory_links + source,
    hypothesis-flagged, append-only. Press-described bits qualify;
    undescribed titles don't.
33. **KT judge analyses → priors with status levels** — measured-kt-jezv
    (judge-aggregated) ranks below transcript-measured, above authored.
34. **Style tags inferred, sim shown** — resemblance, not measurement.
35. **Compare views label units, never blend** — theory_score (0-1) vs
    paper (~.02) vs house (0-100) side-by-side for judgment only.

## Presentation doctrine (site lies prevented)

36. **Nulls render as information** ("—", "unranked", "no pulse"), never 0,
    never hidden, never filled. Rising needs d≥500 (Wright +36/z12 rule).
37. **First-seen videos excluded from velocity** — lifetime views ≠ weekly
    gains (Basketmouth 12.5M artifact). Newly-tracked listed separately.
38. **Reference numbers labeled reference** — ref:true in data, "reference
    election" on page. House numbers never carry external inputs (in code).
39. **Freshness must LOOK stale** — updated timestamps + week/mode on every
    surface. Snapshots ordered by mtime (W41/W42 filename bug), weeks by
    isocalendar.
40. **Reattribute, don't misattribute** — KT minutes belong to performers
    (Jefferies→Stroud rule); reattr runs inside pulse.
41. **New = indie tier only** — created-dates labeled Hart a newcomer;
    synthetic/test profiles excluded from new-comic.

## Process doctrine

42. **rate.py never fetches** — enrich/harvest collect (keys/quota);
    rating is pure from graphs. Content-hash manifest (mtime self-trigger
    bug) makes --check safe. Run receipts in runs.jsonl (gitignored).
43. **One canonical code path** — new scripts reuse leg computation by
    import (kendall_w.compute_legs), never copy. Overlapping logic gets
    factored or documented, not forked.
44. **Papers sync to code, code governs** — v0.1→v0.2 drift log kept in
    PAPER_ARXIV Appendix C. Numbers recomputed at submit time.
45. **Bibliography: verified or flagged** — no fabricated cites; seven
    author-unknown arXiv entries sit in an explicit verify block.
46. **Dead artifacts stay dead, noted** — clips.json (94 rows, nothing
    reads it), youtube_harvest_search_LEGACY (retired), by_continent.json
    (no owner script). Delete on sight only with a replacement; else note.
