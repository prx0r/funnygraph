# HEAT — who's hot now (0-100)

**One line:** view velocity + recent-special momentum. The moment, not the career.

## Formula
- v1 (now): YouTube total views percentile blended with latest-special year recency.
- v2 (needs 2+ pulse snapshots): views/day + likes/day velocity percentile,
  bracketed by channel size (a KT clip gaining 50k/wk beats Netflix gaining
  200k/wk at 1% of the subs).

## Inputs
- `youtube.*` per-clip stats, weekly snapshots (`rankings/pulse/snap-*.json`)
- `specials_rated[].year` (recency)

## Justification
Canon moves yearly; heat moves weekly. A breakout (Gillis Beautiful Dogs:
26.5M hrs as a debut) must be visible NOW, not after canonization. Velocity
within sub-brackets prevents big-channel dominance of trending.

## Limitations (v0.2 correction: code ships null, not the proxy below)
- UNIMPLEMENTED in metrics.py (heat: None). The v1 views+recency proxy is
  spec-only; a metric that moves weekly must not be faked from a snapshot.
- Weekly cadence required; velocity needs 2+ pulse snapshots (subs_growth
  needs 2+ subs-bearing snaps).
- Viral one-offs spike (that's the point — heat is volatile by design).

## References
Pulse design (pulse.py) · TOP2026.md.
