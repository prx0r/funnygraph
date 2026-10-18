# SITE — populate the site from funnygraph (consumer guide)

> For the agent building the site. Read this + SITE_METRICS.md, then read
> JSON. You never need the pipelines; you need these files and their rules.
> Pipeline version: `rate/v1` (field `pipeline` on every row). If it reads
> differently, this doc is stale — check `git log` on rate.py.

## The three files you need (everything else is provenance)

| File | What | Refresh |
|---|---|---|
| `rankings/ratings.json` | **ONE ROW PER PROFILE**: headline, coverage, provisional, boards, interval, lenses. The canonical site table — start here, end here for profile pages. | every `rate.py` run |
| `rankings/spotlight.json` | Weekly boards: comedian_of_week, bracket_champs, rising_star, new_comic_of_week, trending_clips, newly_tracked, subs_growth. Homepage + week pages. | every `pulse.py --report` |
| `rankings/house.json` | Proprietary board rows (rank, house 0-1, house_pct, legs P1/P2, coverage, sweep_lo/hi). Leaderboard page. | every `rate.py` run |

Reference elections (display verbatim, labeled "reference" — never inputs):
`consensus.json`, `canon.json` (+weights), `peoples.json` (WR + momentum),
`era_adjusted.json`, `by_generation/type/mode/decade/continent.json`,
`specials.json`, `bits.json` (134), `neighbors.json` (for-you),
`theory_content.json` (by_type joke-quality boards, mechanism_weights),
`metrics.json` (5-lens panel source), `agreement/stability/mallows/bt.json`
(methodology receipts — link from a "how we rank" page).

## Profile page assembly (worked example: norm-macdonald)

```
HEADLINE 100 · FULL · ours (house #1, sweep [1,10])
  <- rating.headline, rating.coverage, boards.house.rank, interval.lo/hi
  RULE: headline null is impossible (provisional ladder always yields one).
  RULE: coverage UNRANKED -> show provisional method ("neighbor-inferred"),
        NO house rank, NO interval. DISCOVERY (indies) -> same + tier badge.

FUNNIER 100 | LEGACY 87 | AUDIENCE 63 | POPULARITY 34 | HEAT —
  <- lenses.{funnier,legacy,audience,popularity,heat}
  RULE: heat null renders as "—" (NEVER 0, NEVER a proxy).
  RULE: lenses.theory does not exist at presentation (feeds house P2).

Underrated (−0.29) · Canon lag −0.24
  <- lenses.gap_value + lenses.overrated (band), lenses.canon_lag

REFERENCE (labeled, verbatim):
  consensus #25 · canon #38 · people's #18 (WR 7.5) · era #39
  <- boards.{consensus,canon,peoples,era}.rank (+peoples.wr)
  RULE: every reference number carries ref:true in data; render a
  "reference election" label. These are other parties' judgments.

Generation: nineties · Region: us · Type: absurdist (style_tags if indie)
Standout: Nothing Special (IMDb 7.5)  <- peoples row standout fields
Closest match / For fans of  <- neighbors.json[slug][:3]
Outbound (traffic loop): website.url (louisck.com pattern) +
  youtube_channel{id,title,subs,status} (ONLY when status active/variety;
  stale/dormant render de-emphasized or not at all)
Freshness footer: "ratings updated {rating.updated}" <- always show.
```

## Board pages

- **Leaderboard**: house.json rows (rank, name, house_pct, coverage badge, sweep interval on hover/expand). Split tabs: CANON (canon.json), PEOPLE'S (peoples.json) — labeled reference elections.
- **By type/decade/generation/continent**: by_*.json (kings). **Best jokes per type**: theory_content.by_type (measured comics only; thin flags honored — don't crown a 1-comic board without the "thin data" badge).
- **Week page**: spotlight.json verbatim (mode field tells velocity vs absolute; null rising_star renders as "no pulse this week", never a filler pick).
- **Methodology page**: PAPER_ARXIV.md renders as-is (it's written for this) + agreement/stability numbers as charts. The honest audit (GAPS.md) links from every board footer.

## Rules that prevent site lies

1. Nulls render as information ("—", "unranked", "no pulse"), never 0, never hidden, never filled.
2. Provisional/UNRANKED/DISCOVERY profiles show method + coverage, never a rank.
3. Reference numbers always labeled reference; house numbers never carry external inputs (enforced in code, not convention).
4. `updated` timestamps on every row; spotlight `week`+`mode` on every week page. Stale data must LOOK stale.
5. Dont invent fields: schema above is exhaustive. `socials{}` (evidence links) and `discovery{}` (provenance) may render as "elsewhere"/"how we found them" rails.

## Freshness contract (what updates when)

- Profiles/boards: `rate.py --check` (seconds; no-op when clean). Poll `ratings.json:updated`.
- Week boards: Monday `pulse.py --snapshot --report` (velocity needs 2+ snaps; subs_growth needs 2+ subs-bearing snaps).
- New comics appear automatically (DISCOVERY + provisional) — no site deploy needed to list them.
- Outbound links (website/youtube_channel) change on discover runs; re-render profiles when `rating.updated` moves.

---

## TRANSCRIPT-LINKED EMBEDS (added 2026-10-18)

R2 bucket `comedy-specials` now synced into local linkage layer.
Clips and specials carry transcript URLs so the site can embed
YouTube + show/sync the transcript side-by-side.

### Data files

| File | What | Count |
|---|---|---|
| `data/r2/site_manifest.json` | **Site index**: comedian → clips[] + specials[], each with videoId/url + transcript_url | 700 comedians, 2373 clips, 644 specials |
| `data/youtube/*.json` | Per-comedian clip rows (harvest + R2 merged). Rows with `r2_clip_key` + `transcript_url` are transcript-linkable | 556 files, 418 r2_linked |
| `data/r2/specials/{slug}.json` | Per-comedian specials (full-length transcripts) | 292 files |
| `data/r2/live_index.jsonl` | Fresh filename-based clip index (videoId↔r2 key) | 2373 rows |
| `data/r2/specials_index.json` | Specials index | 644 rows |

### Embedding recipe (site/worker)

```
1. READ  data/r2/site_manifest.json
2. FOR each comedian:
     clips[]   → YouTube embed via videoId/url
     specials[] → full-special player or transcript reader
3. WHEN user opens a clip/special with transcript_url:
     FETCH transcript_url (server-side; R2 S3 endpoint, creds required
     or use a Cloudflare Worker with R2 binding / presigned URL)
     JSON has: {id, url, title, words[], transcript, transcript_method}
     - words[] WITH start/end  → timed transcript (karaoke sync)
     - words[] WITHOUT start   → text-only (published transcript)
4. RENDER: YouTube iframe + transcript panel. If words_timed,
   highlight current word from video currentTime.
```

### Row schema (clips in data/youtube + manifest)

```json
{
  "videoId": "i577LmfHOsk",
  "title": "...", "channel": "...", "views": 202296, "duration_s": 178,
  "url": "https://www.youtube.com/watch?v=...",
  "n_words": 452,
  "words_timed": true,          // true = karaoke-syncable
  "transcript_method": "youtube-auto-captions",  // or published-transcript / asr
  "transcript_available": true,
  "transcript_preview": "first 200 chars…",
  "r2_clip_key": "comedians/stewart-lee/clips/stewart-lee-i577lmfhosk.json",
  "transcript_url": "https://<r2-endpoint>/comedy-specials/<r2_clip_key>"
}
```

### Counts at sync time (2026-10-18T16:07Z)

- **2373 clips** linked (1983 with timed words, karaoke-syncable)
- **644 specials** linked (12 with timed words; most are published text transcripts)
- **700 comedians** in manifest
- Timed-word clips come from YouTube auto-captions or ASR; published
  transcripts (Scraps mirror) are text-only — render as reader, not karaoke.

### Rerunning the sync

```bash
python3 sync_r2_clips.py      # enumerate R2 → live_index + pass-1 linkage
python3 sync_r2_metadata.py   # fetch clip JSONs → fill data/youtube rows
python3 sync_r2_merge.py      # merge overlap + specials + site_manifest
```

Requires `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env for the R2
S3 endpoint. Never commit keys.

### Rules

1. `transcript_url` points at raw R2 S3 — the browser can't fetch it
   without creds. Site must route through a Worker (R2 binding) or
   presigned URL. Never expose S3 keys client-side.
2. `words_timed: false` → render as transcript reader, not karaoke.
   Never fake timing.
3. Harvest rows without `r2_clip_key` have no transcript — render
   the YouTube embed alone, no transcript panel.
4. `transcript_preview` is display-safe (first 200 chars). Full text
   lives in R2 only.
5. Sync scripts are rerunnable; debz/local workers keep R2 fresh.
   Re-run sync after their handoff to pull new clips.
