# FANBASE ML — spec: what YouTube comments give us and how we use it

> Every comment is a fan telling us who they are, what they love, and who
> else they watch. Author channel IDs (hashed, no PII) let us track fans
> across comedians. This doc specs all of it.

## Data we store per comment

`author_hash` (sha256 of channelId — no PII, joinable across videos),
text, likes, publishedAt, sentiment, has_timestamp, goat_call, quoted_bit.

## Pipelines

### F1. Fanbase fingerprints (per comedian)
Vocab profile (distinctive words vs global comment corpus), emoji profile,
sentiment distribution, avg comment length, timestamp density, GOAT-call
rate, defense patterns ("you don't get it", "watch the full special").
Output: `fanbase/{cid}.json` — "Burr fans say ___, use ___ emoji, defend by ___."

### F2. Overlap graph → taste communities
Shared commenters across comedians' videos → affinity matrix (Jaccard on
commenter sets) → community detection → "Pryor fans also watch X" clusters.
Output: `fanbase/overlap.json` + communities. Feeds the recommender AND
proves taste segments exist (validates generation/scene theory empirically).

### F3. Quote-back → bit validation
Fuzzy-match comment text against transcript bits; bits quoted back by fans
get quote_rate scores. A bit nobody quotes is a bit nobody remembers.
Output: per-bit `quote_rate` in graphs. Feeds agent harness as a judge:
"write bits with high predicted quote_rate."

### F4. Timestamp aggregation → laugh map
"4:32 killed me" comments → timestamps → aggregate per special → laugh-density
curve. Ground truth for timing analysis at scale (no ASR needed).
Output: `fanbase/laughmap/{special}.json`.

### F5. GOAT-debate extraction → pairwise votes
"X is better than Y", "X clears Y", "nobody touches X" → directed pairwise
preferences → Bradley-Terry leg for rankings. The fans vote every day in
comments; we just count.
Output: `fanbase/pairwise.json` → feeds rank_comedians.py leg 4.

### F6. Comedy sentiment lexicon (learned)
Seed: GOAT-call/timestamp contexts are positive by construction. Learn which
words/phrases ("I'm dead", "killed me", skull emoji, "rewatching for the
5th time") predict them. Replaces the dead generic lexicon.
Output: `fanbase/lexicon.json` — comedy-tuned, learned from our own data.

### F7. Fanbase characterization (the fun one)
Per comedian: age signals (slang era), loyalty (repeat commenters across
their videos), evangelism (caps, exclamation, "show this to..."), gatekeeping
("real ones know", "you had to be there"), cross-fandom wars (who they argue
with). Output: human-readable fanbase profiles — content in itself
("The Two Types of Chappelle Fans, According to 10,000 Comments").

### F8. Temporal fanbase shifts
Sentiment/quote patterns per special over a career → "when did the fanbase
turn?" (e.g. post-2017 Louis, post-Inside Bo). Needs multiple specials per
comic with comment timestamps — we have the specials, harvest over time.

## Collection plan

- Phase 1 (now): top 25 clips × 50 comments — proves F1/F4/F6 patterns.
  Author hashes stored from here on.
- Phase 2: all 240 tracked clips × 100 comments (~24k comments, ~240 API
  units/wk — trivial). Enables F2 overlap (needs breadth).
- Phase 3: deep dives (500+ comments) on top-20 specials for F3/F5/F7.
- Weekly: new comments on tracked videos → velocity of sentiment (F8).

## Privacy

Author IDs hashed at collection. No usernames stored. No profiling of
individuals — only aggregates per comedian. Public comments, aggregate use,
no PII in tree (secret-scan covers hashes the same as tokens).
