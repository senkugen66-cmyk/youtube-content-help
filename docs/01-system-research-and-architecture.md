# Gaming Thumbnail Intelligence System: Research, Architecture, and Plan

Research date: 2026-10-26. Every number below was retrieved or measured on that date unless it is marked **unverified**.

---

## 1. Executive summary

- **None of the four suggested repositories is ready to use as-is.** All four have **0 stars and 0 forks** and one or two authors. Some are still useful. ThumbGen is a mature thumbnail-generation app (482 commits, 317 test files, active October 2026). yt-thumbnail-ctr-bench is a sound harness for checking whether a vision model can predict CTR. The other two have little reuse value.
- **The biggest technical finding is about measurement, not image generation.** The **YouTube Analytics API does not list a thumbnail-impressions or impressions-CTR metric** (checked against the official metrics page today). Impressions and CTR per video are available from the **YouTube Reporting API "reach" reports** (`channel_reach_basic_a1`, `channel_reach_combined_a1`). The combined report includes `traffic_source_type`. YETi asks the Analytics API for `impressions` and `impressionClickThroughRate`, so its CTR path probably fails. pauling-ai/youtube-mcp-server advertises CTR, but its source code doesn't implement it.
- **The only truly randomized thumbnail A/B test is YouTube Studio's native "Test & compare".** It takes up to 3 variants, is desktop-only, and needs advanced features. It **picks winners by watch-time share, not CTR.** The system should design variants *for* Test & compare and record its outcomes. Do not swap thumbnails before and after and call that an A/B test.
- **Recommended MVP:** a small Python toolkit driven from Claude Code (no autonomous multi-agent framework). It has:
  - HasData MCP and YouTube Data API for research
  - Pillow plus OCR plus a vision LLM for analysis
  - one image-generation API with **deterministic Pillow text overlay** (models misspell text)
  - automated QC
  - Reporting/Analytics API ingest with proper statistics
  - SQLite as the store
- **Research test (see `02-youtube-research-test.md`):** the HasData MCP works for search, video, and channel data, and I could inspect real thumbnails visually. It does **not** provide CTR, impressions, or subscriber counts in search results. Absolute publish dates only come from the video endpoint.

---

## 2. Ranked repository comparison

Columns: ★ = stars, ⑂ = forks. "Last commit" is the HEAD commit date, from cloning each repo for read-only inspection. I **did not run** any third-party code or tests (see §9).

| Rank | Repository | ★ / ⑂ | Last commit | Commits / authors | Releases | License | Language / stack | Role it could play |
|---|---|---|---|---|---|---|---|---|
| 1 | [ohvignas/ThumbGen](https://github.com/ohvignas/ThumbGen) | 0 / 0 | 2026-10-01 | 482 / 2 | none (no tags) | MIT. **Bundles `@imgly/background-removal`, which is AGPL-3.0** (verified) | Next.js 16, React 19, SQLite, Docker | Thumbnail-generation GUI (optional) |
| 2 | [adamholter/yt-thumbnail-ctr-bench](https://github.com/adamholter/yt-thumbnail-ctr-bench) | 0 / 0 | 2026-06-14 | 1 / 1 | none | MIT | Python ≥3.11, pandas/scipy/pydantic | Validation harness for "can a vision model predict CTR?" |
| 3 | [pandich93/youtube-niche-finder](https://github.com/pandich93/youtube-niche-finder) *(found in discovery)* | 22 / 4 | 2026-10-25 | 317 / 4 | v0.1.0–v0.5.0, CI | MIT | FastAPI, PostgreSQL, Docker, MCP | Outlier/niche research at scale (later) |
| 4 | [calmannix/YETi](https://github.com/calmannix/YETi) | 0 / 0 | 2026-03-02 | 5 / 2 | 2.0.0, v2.1.0, v2.2.0 | MIT text plus appended third-party notice (GitHub detects "Other") | Python, Flask, statsmodels, pingouin, OpenAI | Reference for statistical tests only |
| 5 | [pauling-ai/youtube-mcp-server](https://github.com/pauling-ai/youtube-mcp-server) *(found in discovery)* | 29 / 28 | 2026-10-23 | 25 / 6 | v0.2.0, v0.3.0 | MIT | Python, FastMCP, google-api-python-client | Analytics/Reporting API access (with caveats) |
| 6 | [prekshaaggarwal/youtube-thumbnail-studio](https://github.com/prekshaaggarwal/youtube-thumbnail-studio) | 0 / 0 | 2026-04-15 | 10 / 1 | v1.0.0 | MIT | Flask, scikit-learn | Not recommended |

Other searches turned up nothing better: thumbnail CTR, thumbnail vision analysis, outlier finders, analytics MCP servers. `per-simmons/thumbgen` (2★, the upstream of ThumbGen) is older and smaller.

**Mature building-block libraries** (star counts verified today; licenses as commonly published, **not re-verified in this session**):

| Library | ★ | Purpose |
|---|---|---|
| googleapis/google-api-python-client | 8,957 | Official Data, Analytics, and Reporting API client |
| statsmodels/statsmodels | 11,717 | Proportion tests, Wilson CIs, GLMs |
| JaidedAI/EasyOCR | 30,105 | OCR for text-density and spelling QC |
| PaddlePaddle/PaddleOCR | 91,707 | Alternative OCR (heavier) |
| mlfoundations/open_clip | 14,222 | Visual-similarity embeddings |
| danielgatis/rembg | 25,191 | Background removal (alternative to the AGPL imgly package) |
| JohannesBuchner/imagehash | (not returned by search) | Perceptual hashing for near-duplicates |

### 2.1 Per-repository findings

**ThumbGen.** It has the largest real feature set of any candidate.
- What exists: a node canvas, character references, an A/B/C variant generator (capped at 3 to match Test & compare), an in-app agent with skills, YouTube Data API research, followed-channel "outlier" scoring, an MCP server, and Docker.
- Implemented, not just planned: the outlier formula is in `src/lib/youtube/performance.ts`. It divides views by the median of the channel's 50 latest videos that are older than 7 days, and flags ≥3× as "over". There are 317 `*.test.*` files and vitest config.
- Requirements: an OpenRouter key for all image and agent models, plus a YouTube Data API key. Optional: Perplexity and OpenAI (voice).
- Cost (README estimates, **unverified**): about $0.01–$0.05 per image and $0.75–$75 per million agent tokens depending on model.
- Risks:
  - single maintainer, 0 adoption
  - French-only UI
  - no CI or releases
  - large dependency tree (package-lock has 16,786 lines)
  - the AGPL-3.0 background-removal dependency (fine for private local use; matters if you ever host it as a service)
  - routes every model call through OpenRouter, a third party
- Integration: it's a standalone web app, not a library. Integrate through its MCP server or by exporting images. Don't embed it.

**yt-thumbnail-ctr-bench.**
- What it does: a clean, deterministic pipeline. It joins Studio CTR to thumbnails, builds ranking tasks, calls vision models through OpenRouter, and scores pairwise accuracy, Spearman, Kendall, NDCG, and MAE.
- Tests: there are 4 test files with 10 test functions. The README says they passed on 2026-06-14; **not reproduced by me**.
- Main limitation: the bundled dataset is **Ken Jee's data-science channel** (224 videos in the raw CSV, 74 in `benchmark.csv`). That's not gaming, so any model score on it says nothing about gaming thumbnails.
- How to use it: run the harness on *your own* Studio export once you have enough videos, to decide whether to trust a model's CTR guesses at all.
- Single commit, no CI.

**YETi.**
- What it does: before/after **period comparisons** (treatment video lists across date ranges) using z-tests, Welch t-tests, Cohen's d/h, and power. It's not concurrent randomization.
- The bug: it requests `impressions` and `impressionClickThroughRate` from the Analytics API. Those metrics aren't in the official metric list, so the CTR analysis very likely fails. Its own test treats the metric as "may not be available".
- Footprint: about 6,000 lines of Python, a Flask UI, OpenAI "insights", and many status/marketing markdown files.
- Tests: 9 test files with 205 test functions. Several need live API credentials.
- Reuse value: low. Copy the idea (two-proportion z-test plus effect size plus power), not the code.

**youtube-niche-finder.**
- The most actively maintained YouTube research tool found. It has outlier-vs-channel-median detection, niche scoring, CI, releases, and 100 MCP tools (per its README badge, unverified).
- It needs PostgreSQL, Docker, and a YouTube Data API key. That's too heavy for the MVP. Revisit if you want continuous niche monitoring.

**pauling-ai/youtube-mcp-server.**
- Analytics, Reporting, and Data API tools.
- **The README claims CTR support, but `grep` finds no CTR or impressions metric in the source.**
- It requests broad write scopes: upload, `youtube`, `force-ssl`, and monetary. That's more access than an analytics reader needs.
- Its generic `reporting.jobs().create` tool *could* create a reach-report job.
- Recommendation: write about 150 lines against the official client with read-only scopes instead.

**youtube-thumbnail-studio.**
- The "CTR prediction" model is a logistic regression. Its label is `target_good`, meaning views-based `perf_score` is at or above the 60th percentile. **It is not trained on CTR.**
- Features: simple color/edge statistics plus title TF-IDF.
- Tests are UI smoke tests only. Inactive since April 2026.
- Not recommended.

---

## 3. Recommended components

| Need | Recommendation | Why |
|---|---|---|
| **Thumbnail-generation foundation** | **Own thin adapter around one image API, plus Pillow for all text.** ThumbGen is the optional GUI if you want a canvas. | Keeps dependencies and credentials minimal. Text rendered by Pillow is spelled correctly every time. ThumbGen is the best candidate found but carries adoption and AGPL risk, so evaluate it in Docker before relying on it. |
| **Thumbnail-analysis component** | **Own module:** Pillow/NumPy metrics, EasyOCR, mobile-scale renders, and Claude vision critique against a fixed rubric. Use yt-thumbnail-ctr-bench later to *validate* any CTR-prediction claim on your own data. | No candidate does credible visual analysis. The bench repo is the only one that measures prediction honestly. |
| **Performance-measurement component** | **Own module:** YouTube Reporting API reach reports (impressions and CTR by traffic source), YouTube Analytics API (views, watch time, average view %, traffic sources, retention), statsmodels, plus a log of Studio "Test & compare" outcomes. | The only official CTR source. YETi and pauling-ai don't actually retrieve CTR. |
| **Research** | **HasData MCP** (verified, already connected) for search, channel, and video data, with the **YouTube Data API v3** as an official fallback. | Search costs 100 quota units per call out of 10,000 per day by default. HasData has no YouTube quota but costs credits (pricing **unverified**). |
| **Glue** | `google-api-python-client`, `google-auth-oauthlib`, `pydantic`, `statsmodels`, `Pillow`, `easyocr`, `imagehash`, SQLite (`sqlite3`, stdlib). Optional: `open_clip_torch` for similarity. | All mature. No agent framework is needed; Claude Code skills orchestrate the steps. |

---

## 4. Major risks

**Security**
- OAuth tokens for your channel must live outside the repo (e.g. `~/.config/thumbintel/`) with **read-only scopes** (`yt-analytics.readonly`, `youtube.readonly`).
- Request upload/`youtube` scope only if you later want the tool to *set* thumbnails, and keep it as a separate credential.
- Never vendor third-party code without review. ThumbGen's 16k-line lockfile is a real supply-chain surface.

**Privacy**
- Your analytics must not be sent to OpenRouter, OpenAI, or similar without your explicit decision.
- The performance module runs locally. Only aggregated, non-identifying summaries go to an LLM, and only if you opt in.

**Licensing**
- The AGPL-3.0 dependency in ThumbGen.
- Competitor thumbnails are copyrighted. Store **URLs and derived features**, not redistributed image files. Use them as references for analysis, never as generation inputs that copy a design.
- Game logos and screenshots: use them for identification or commentary only. Never imply endorsement.

**Cost** (all **unverified estimates**)
- HasData credits per call. One research run of about 6 searches, 6 channel calls, and 1 video call used 13 requests.
- Image generation is roughly $0.01–$0.05 per image (ThumbGen's table). With 3 concepts × 2–4 images, that's under about $1 per video.
- LLM critique tokens on top.

**Technical**
- Reach-report data needs a reporting job created ahead of time. Historical backfill on job creation is **unverified**.
- Test & compare is desktop-only, needs advanced features, and judges by watch-time share.
- Small channels may not get enough impressions for a conclusive test.

**Methodological**
- Public views don't reveal CTR.
- Channel-median ratios are confounded by topic, timing, and age.
- Vision-model CTR predictions are unvalidated until tested on your own data.

---

## 5. Minimum viable architecture

```
                 ┌──────────── Claude Code session (orchestrator = skills/commands) ────────────┐
 you: game,      │                                                                              │
 topic, query,──►│ A Research ──► B Visual analysis ──► C Concepts ──► D Generate ──► E QC ─────┼─► 3 variants
 assets          │   │  HasData MCP / Data API   │ Pillow+OCR+vision   │ LLM+templates  │ image API + Pillow text
                 │   ▼                           ▼                     ▼                ▼          │
                 │ ┌──────────────────────── SQLite + files (local) ────────────────────────────┐│
                 │ │ videos · snapshots · thumbnails(features,phash) · concepts · variants ·    ││
                 │ │ experiments · metrics_daily(traffic_source) · hypotheses/lessons           ││
                 │ └────────────────────────────────────────────────────────────────────────────┘│
                 │   ▲                                                                          │
                 │ F Performance ◄── Reporting API reach reports + Analytics API (OAuth, read-only)
                 │   └── Test & compare outcomes (entered by you) ── stats ── lessons ─► feeds C  │
                 └──────────────────────────────────────────────────────────────────────────────┘
```

**Agents are prompts plus deterministic tools, not separate services.** Each "agent" is a Claude Code skill that calls a Python CLI subcommand and writes to SQLite.

| Agent | Input | Output (stored) | Tools |
|---|---|---|---|
| A Research | game, topic, query, region | `videos`, `snapshots` (views at retrieved_at, source, request id), channel medians, outlier ratio, age-normalized views/day | HasData MCP or REST, Data API |
| B Visual analysis | thumbnail URLs | `thumbnail_features`: size, brightness, contrast, colorfulness, edge density, OCR words and area %, face count, phash, mobile render; plus an LLM critique tagged **observation** vs **hypothesis** | Pillow, EasyOCR, vision LLM |
| C Concepts | brief + research report + past `lessons` | 3 concepts (Clarity / Curiosity / Differentiation) with hypothesis, focal point, text, prompt | LLM with fixed templates |
| D Generate | approved concept + your assets | raw images plus composited 1280×720 variants | image API adapter, Pillow |
| E QC | variant | pass/fail report: 16:9, ≥1280×720, ≤2 MB, OCR text equals intended text, legibility at 168 px, similarity to competitors (no copying), checklist for misleading or invented content | Pillow, EasyOCR, imagehash/CLIP, LLM checklist |
| F Performance | video IDs, experiment window | `metrics_daily` (by traffic source), experiment results with CIs, `lessons` | Reporting API, Analytics API, statsmodels |

**Storage:**
- one SQLite file
- `assets/` for your inputs and generated variants (git-ignored)
- `research/<date>/` holds provenance CSVs (URLs only, no competitor images)

**Scoring rubric (Phase 5).** Score each 1–5 with a written justification:
- topic relevance
- clarity
- focal-point strength
- mobile readability (judged on the 168 px render)
- differentiation (CLIP/phash distance from the competitor set)
- title complementarity (the thumbnail must not repeat the title)
- promise accuracy (anything shown must appear in the video)
- technical quality

This is labelled a **design critique, not a CTR prediction**, until a model passes the bench harness on your data.

**Statistics (Phase 6):**
- **Controlled:** Test & compare is the primary evidence. Record winner / same / inconclusive, the watch-time share, and the test dates.
- **Observational:** report CTR per traffic source with Wilson 95% CIs. Compare variants only within the same traffic source and similar video age. Use a two-proportion test only when both arms have ≥1,000 impressions and the windows match. Apply Holm correction across many comparisons, and pre-register the stopping rule.
- **Never declare a winner from a CTR bump alone.** Always check average view duration and average view %. A higher CTR with lower watch time is flagged as a possible over-promise.
- **Across videos:** tag each variant with hypothesis labels (e.g. `proof-object`, `no-text`, `face`, `redeem-ui`). Accumulate beta-binomial posteriors per tag *within traffic source*, and treat them as directional until there are ≥10 videos per tag.

---

## 6. Implementation plan (priority order; build only after you approve)

1. **P0 – Skeleton and storage.**
   - `thumbintel/` package, pydantic models, SQLite schema, `.env.example`, git-ignored `assets/` and `secrets/`.
   - Research ingest from HasData JSON with provenance, plus channel-median and views/day scoring (the scripts in `research/2026-10-26/` are the prototype).
2. **P1 – Visual analysis.**
   - Feature extractor, EasyOCR text area and words, contact sheets, and 168 px mobile previews (prototype in `research/2026-10-26/contact_sheet.py`).
   - Critique prompt that separates observations from hypotheses.
3. **P2 – Concepts and QC.**
   - Concept templates (A/B/C).
   - QC: dimensions and size, OCR spelling match, mobile legibility, competitor similarity, misleading-content checklist.
4. **P3 – Generation.**
   - One image-API adapter (provider is your choice).
   - Pillow text compositor with your fonts and brand colours.
   - Test & compare-ready export (3 variants).
5. **P4 – Performance.**
   - Read-only OAuth, create the reach-report job (do this **early**; data accrues from creation), daily ingest, and Analytics API pulls.
   - Stats module, experiment log, lessons.
6. **P5 – Validation.**
   - Once you have about 30 or more of your own videos with Studio CTR, run yt-thumbnail-ctr-bench-style ranking tasks to decide whether any vision model's CTR guesses can be trusted.

Tests come with each stage: unit tests for the stats (against known values), the feature extractor (on fixtures), the QC checks, and the schema. API calls are mocked.

**Keys and permissions needed:**
- HasData (already connected via MCP; a REST key only if run outside Claude)
- a Google Cloud project with the YouTube Data API v3, YouTube Analytics API, and YouTube Reporting API enabled, plus an OAuth desktop client with `yt-analytics.readonly` and `youtube.readonly`
- one image-generation provider key
- optional: an Anthropic API key if you run critiques outside Claude Code

---

## 7. Proposed directory structure

```
thumbintel/
  models.py          # pydantic: Video, Snapshot, Thumbnail, Concept, Variant, Experiment, MetricDaily, Lesson
  db.py              # SQLite schema + migrations
  research.py        # HasData/Data API ingest, channel baselines, outlier & views/day
  analyze.py         # features, OCR, mobile render, contact sheets
  concepts.py        # templates + prompt assembly
  generate.py        # image-API adapter + Pillow compositor
  qc.py              # automated checks
  performance.py     # Reporting/Analytics ingest, Wilson CI, z-test, Holm, lessons
  cli.py
.claude/skills/      # research / analyze / concept / qc / review-experiment workflows
tests/
research/<date>/     # provenance CSVs, scripts
docs/
```

---

## 8. Open questions for you (each changes what gets built)

1. **Image-generation provider and budget.** Options include OpenAI GPT Image, Google Gemini image, or OpenRouter (one key for many models, but a third party in the path).
2. **Channel eligibility.** Do your channels have advanced features enabled, so you can use Test & compare? Roughly how many impressions per video in the first 7 days? This decides whether controlled tests can reach a conclusion.
3. **Your assets.** Do you have a recurring on-camera face or mascot, a font, and brand colours? Or should thumbnails be gameplay-only?

---

## 9. Claims that remain unverified

- Whether any third-party test suite passes. I **did not run** them; I only inspected code. ThumbGen has 317 test files, the bench repo 10 test functions, YETi 205, thumbnail-studio 3 smoke tests.
- ThumbGen's cost table, model list, and feature claims beyond the code paths I read (outlier scoring, A/B/C limit, OpenRouter routing).
- niche-finder's "100 MCP tools" and coverage badge.
- Library licenses in the §2 building-block table (not re-checked today). The `@imgly/background-removal` AGPL-3.0 license **was** verified.
- HasData pricing per request.
- Whether Test & compare results are available through any API. I found no evidence they are; assume manual entry.
- Reporting API historical backfill when a job is first created.
- Whether YETi's Analytics `impressions` query errors or silently returns something else (`adImpressions` was formerly named `impressions`).
- All competitor CTRs. **No competitor CTR was observed.** Views and channel-median ratios are proxies only.
