# Search-first title workflow

A manual process for choosing and titling videos. No software required.

## Research capabilities (confirmed 2026-10-26)

| Source | What it gives | What it doesn't |
|---|---|---|
| YouTube autocomplete (public suggest endpoint) | Real suggested phrases for a seed, roughly in rank order | Search volume |
| HasData YouTube search (MCP) | Results page: titles, views, upload age, channel, Shorts, chapters; filters for date, sort and type | Impressions, CTR, traffic sources |
| HasData video / channel / transcript (MCP) | Exact publish date, tags, subscriber counts, a channel's recent uploads, transcripts | Private analytics |
| Web search | Update and code context (third-party, often conflicting) | — |
| YouTube Studio data | Only when you paste or export it | — |

Autocomplete check (browser or curl):
`https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&gl=us&q=YOUR+SEED`

## Steps per topic

1. **Seeds.** Run autocomplete on `<game>`, `<game> how to`, `how to get … in <game>`, `best way to … <game>`, and drill into any modifier that looks specific (solo, without X, fast, new update).
2. **Split intents.** Group phrases by what the viewer wants (method, codes, unlock, fix, alternative game). Drop exploit, script and giveaway intents.
3. **Results page, two views.** Search the target phrase with default relevance, then again filtered to the past month. Record title, views, age and channel size.
4. **Is it winnable?** Look for recent uploads from small channels that got meaningful views. If only old videos from large channels have views, it's locked. If 15+ uploads appeared in a day, it's a speed race.
5. **Find the gap.** Look for a modifier people type that no top title answers.
6. **Write five titles.** Use different structures, put the search phrase early, and include the differentiator early. Use numbers and "fast" only when the footage supports them.
7. **Recommend one and log uncertainties.** Save the report to `research/YYYY-MM-DD-<topic>.md`.

## After publishing (needs Studio data from you)

Record for each video: search impressions, CTR from search, views from YouTube Search, the top search terms, and average view duration. Compare against the phrases targeted in the research file and note which ones actually brought traffic.
