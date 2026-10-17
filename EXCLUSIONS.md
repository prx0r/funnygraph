# EXCLUSIONS — comedians deliberately absent, with reasons

> A canon with secret deletions isn't auditable. Every exclusion is listed
> here with who ordered it and why. Data already collected is purged;
> historical pulse snapshots stay immutable (they record what was tracked,
> not what's endorsed).

| comedian_id | ordered | reason |
|---|---|---|
| ellen-degeneres | owner, 2026-10-17 | owner's prerogative ("i hate her lol" — verbatim) |

## Rule
Excluded comedians: no graph, no transcripts, no boards, no future harvests.
Pipeline scripts check `excluded.json` and skip. Re-admission requires
reversing this file + re-harvest (nothing is unrecoverable — transcripts
survive upstream at HF/scrapsfromtheloft).
