# SFW crime-scene dashcam narration — retention playbook

## Format
Dashcam / bodycam-style footage as the visual layer, your voiceover as the story.
Target 8–14 min. Each video = one incident, told as a mini-mystery.

## Structure (retention-first)
| Time | Beat |
|---|---|
| 0:00–0:20 | Cold open: the most striking *clean* frame + one-line stakes ("Nobody noticed what the dashcam caught at 2:14 a.m."). No intro, no logo, no "hey guys". |
| 0:20–1:00 | Context: where / when / who, fast. Plant one open question you won't answer yet. |
| 1:00–end | Alternate **footage beat → your narration → reveal**, every 20–40 s something changes (new angle, zoom, map, text callout, speed change). |
| ~60% | Mid-video re-hook: "But here's what the police didn't know yet…" |
| Last 60 s | Payoff of the opening question, outcome, one-line tease for the next video (no "like and subscribe" speech). |

## Pacing rules
- Cut every pause > 0.25 s in narration (tools/jumpcut.py does this).
- Speed up dead driving stretches 4–6× (`--mode footage`), slow/freeze and zoom on the key frame.
- Never hold one static visual > ~8 s: zoom, crop, pan, or add a map/timestamp overlay.
- Burn in a timestamp/location overlay — it reads as "evidence" and keeps eyes on screen.
- Music: low, tense bed; duck 10–15 dB under voice. Sparse SFX at reveals only.
- Captions on: most views are muted/mobile; also a retention aid.

## Staying SFW and monetizable
- Pick incidents with no gore or visible serious injury; crop/blur/cut before impact if needed. Describe, don't show.
- Blur faces and license plates of private individuals; omit victims' names unless widely public and the case is closed.
- Avoid graphic audio (screams, gunshots) — mute or replace.
- State facts only from court records / police releases / news; label speculation as such. Never accuse unconvicted people.
- Add a short "based on public records" line in the description.

## Sourcing footage (do this before you edit)
- Use footage you have a licence for: public-record releases (check the agency's terms),
  Creative Commons / explicit permission from the owner, or licensed stock/news libraries.
- Don't just rip other channels' clips; that gets strikes and demonetization.
- Keep a `sources.csv` per video (URL, licence, date obtained).

## Titles / thumbnails
- Title = open loop, concrete: "The Dashcam Caught Something the Detectives Missed". Avoid shock-bait that promises gore.
- Thumbnail: one clear frame, one red circle/arrow, ≤3 words, no blood or bodies.

## Workflow with the tools here
1. Write script → record narration (quiet room, same mic distance, one take per paragraph).
2. `python3 tools/jumpcut.py narration.wav --report cuts.json -o tight.wav` — check the % removed (aim 10–25%; if it eats natural pauses, lower `--threshold` or raise `--min-gap`).
3. Pre-trim long footage: `python3 tools/jumpcut.py raw_dashcam.mp4 --mode footage --silent-speed 5 -o dashcam_fast.mp4`.
4. Assemble: either drop `tight.wav` + clips on your NLE timeline, or for a quick rough cut:
   `python3 tools/jumpcut.py narration.wav --bg dashcam_fast.mp4 -o rough.mp4`
5. In the NLE add zooms, overlays, music, captions. Export 1080p.
6. After 48 h check the retention graph: every sharp drop = a beat to tighten next time.

## Benchmarks to aim for
Avg view duration ≥ 50%; ≥ 70% still watching at 0:30; no cliff in the first 15 s.
