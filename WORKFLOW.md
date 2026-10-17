# WORKFLOW — the canonical loop (commands, costs, cadence)

> The loop: FIND → LINK → VERIFY → SETS → RATE → PULSE → PROMOTE.
> rate.py encodes the tail; this file encodes the whole. Quota unit = one
> YouTube Data API unit (10k/day free). Rules behind steps: DECISIONS.md.

## Weekly cadence (Monday, ~30 min, ~100 units)

```
# 1. FIND — what's new (incremental state; quiet weeks ≈ 5u)
python3 discover.py --scan                      # registry uploads, ~1u/50 vids
python3 indie.py --seed-lists                   # press CURATED (zero quota)

# 2. LINK — personal channels + sites for new drafts
python3 discover.py --link-channels             # evidence handles (~1u each)
python3 discover.py --guess-handles             # @FirstLast, verified only
python3 discover.py --link-websites             # Wikidata P856 + guesses
python3 youtube_harvest2.py --only <new-slug>   # pull their channel (~6u)

# 3. VERIFY — audit before rating (zero quota, mandatory)
python3 discover.py --audit-channels            # active/stale/dormant/variety
# MANUAL: tier audit (national credits = king), junk purge. See DECISIONS 22-28.

# 4. SETS — material (the bottleneck)
python3 discover.py --fetch-sets                # captions (BLOCKED: cookies)
python3 indie.py --score --match-greats          # gates on arrival
python3 indie.py --spotlight                    # queue check

# 5. RATE — boards + canonical table (~4s fast / ~12s full, zero quota)
python3 rate.py --check                         # no-op when clean
python3 rate.py                                 # full incl. validation

# 6. PULSE — week boards (~20u snapshot + free report)
python3 pulse.py --snapshot                     # video stats + channel subs
python3 pulse.py --report                       # velocity -> spotlight.json
python3 pulse.py --mine-comments --top 20       # sentiment/GOAT/timestamps

# 7. PROMOTE (human) — indie->king on canon evidence. Nothing auto-promotes.
```

## Monthly / quarterly

- **Bios**: `nohup python3 enrich_bios.py > /tmp/bios.log 2>&1 &` (Wikidata, free, throttled — resumes from cache).
- **Subs backfill**: `youtube_harvest2.py --all` minus carriers (quota-gated, registry only).
- **Fountain verification**: one candidate venue per month (fetch → verify → register → scan → audit).
- **Quarterly falsifiers** (PAPER_ARXIV §6.6): equal-coverage gap retest, BT-vs-Borda drift, stability widening check.
- **Roster re-resolution**: `--guess-handles` re-run (dormant channels wake).

## Annual

- **TOP 2026 election** (Dec 2026): arena battles + critic survey → BT leg + third time point (2004→2017→2026) → ALL-TIME CANON v2 + BREAKOUT + DISAGREEMENT boards.
- **List refresh**: Deadline/Vulture/Edinburgh/GOLD annual lists → PRESS_2026 successor block in indie.py.
- **Paper resync**: recompute every inline number, re-run secret-scan, submit.

## Cost table (measured 2026-10-17)

| Operation | Quota | Wall time |
|---|---|---|
| Full fountain sweep (8 channels, incremental) | ~0-50u | ~1 min |
| KT backfill (647 vids, one-time) | ~45u | ~3 min |
| Handle resolution (forHandle) | 1u each | +0.2s sleep |
| Personal channel harvest | ~6u each | ~8s |
| Pulse snapshot (3.4k vids + 56 channels) | ~70u | ~2 min |
| rate.py full / fast | 0u | ~12s / ~4s |
| Bios (Wikidata, throttled) | 0u | hours, backgrounded |
| Captions (InnerTube/yt-dlp) | 0u | BLOCKED (cookies) |

## Gates (things no cadence overrides)

- No snapshot without key; no scan without registry IDs; no draft without full names; no rank without audit; no crown under n≥30 verified votes; no push by agents; no spend without asking (owner rule).
- PROCEDURAL: `rate.py --check` before any board claim; `secret-scan` (.env only) before any commit.
