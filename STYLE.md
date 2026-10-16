# House style (learned from licensed reference video)

Source: reference video the channel owner licensed for style study, analysed chunk by chunk.
We imitate **patterns** (structure, pacing, typography system, tone). Never reuse its script lines,
footage, or its exact font files; the fonts below are free look-alikes in `assets/fonts/`.

Status: built from reference **part 1** (0:00–2:30). Update as more parts arrive.

---

## 1. Format at a glance
- Long-form **compilation**: one premise, several cases ("starting with…"). Each case ≈ 5–8 min.
- Raw bodycam carries the story; narration is the glue. In part 1, narration is **42%** of the runtime
  and footage dialogue is the other 58%.
- Narration blocks are short: 2–23 s (median ≈ 9 s). Footage stretches between them: 5–31 s.
- Audio: ambient low drone/music bed throughout, very low under everything. The reference sits at
  −20.6 LUFS; **we master to −14 LUFS** (YouTube target).

## 2. Voice and tone
- **Pace: fast, ~200 words/min** while speaking (normal documentary pace is 150). No dead air
  between narration and footage, since each handoff is a hard cut.
- Male, mid-low voice (median pitch ≈ 140 Hz) with a wide, expressive range. Confident and conversational,
  like retelling a story to a friend, not reading a news report.
- Short sentences, ~9 words per line on average and 20 at most. Plain words.
- Clear hero/antagonist framing: the narrator takes a side (in the reference, the outsmarted officer is the
  antagonist and the suspects are the clever underdogs).
- Narration is **not subtitled**; only footage dialogue gets subtitles.

**Guardrail for our channel:** strong framing is fine, but only call a real, named person
"corrupt", "illegal", or a "liar" if a court, agency, or official finding says so. Otherwise attribute it:
"the lawsuit claims…", "he was later charged with…", "the footage shows…". This keeps it SFW and safe from
defamation claims, and keeps the videos monetizable.

## 3. Story structure (beat map from part 1)
| Time | Beat | What happens | Visual |
|---|---|---|---|
| 0:00–0:09 | **Premise hook** | Two lines: the normal situation, then the twist ("But what happens when…?") | Fast teaser montage from cases later in the video |
| 0:09–0:17 | **Cold-open proof** | ~8 s of the juiciest *dialogue* from a later case, subtitled | Raw bodycam |
| 0:17–0:24 | **Thesis + first case** | "Here's how [group] reacted when [twist]… starting with [name/title]." | Torn-paper **title collage** → **person card** |
| 0:24–0:40 | **Setup** | Date ("On [Month D, YYYY],"), who/what/where, then a foreshadowing line ("…and they were about to show him…") | **Date card** (typewriter type-on), **red arrow + name label** on bodycam |
| 0:40–0:53 | **Footage: antagonist's side** | Let them talk; establishes the conflict | Subtitled bodycam |
| 0:53–0:57 | **Re-hook** | 2 short lines: escalation, then who knew it ("What X did next was illegal. And Y knew it.") | — |
| 0:57–1:19 | **Footage: the incident** | Peak confrontation | Subtitled, zoom-ins, arrow on key action |
| 1:19–1:40 | **Explain + escalate** | What happened off-camera / intent / why it matters | **Quote card** of the officer's own words |
| 1:40–2:11 | **Footage: the argument** | Back-and-forth | Subtitled |
| 2:11–2:13 | **Cliffhanger** | "You won't believe what X did next." | — |
| 2:13–2:19 | **Footage: twist** | — | — |
| 2:19–2:28 | **Interpret** | Narrator explains the motive, then a counter line ("But the teens knew better than that.") | — |

**The core loop, repeated all video:**
> narration (2–20 s) **ending on a tension line** → hard cut → footage that proves it (5–30 s) → repeat.

Tension-line formulas to rotate:
- "What [X] did next was [shocking]. And [Y] knew it."
- "You won't believe what [X] did next."
- "But [Y] knew better than that." / "But that didn't work."
- "…and they were about to show [X] that [twist]."
- "[X] had no idea [Y] was [recording / a lawyer / right]."

## 4. Typography system
| Element | Font (free match) | Colour | Placement / motion |
|---|---|---|---|
| Video title band | Special Elite | red `#E3201B`, thin dark shadow | Black band across the middle of a torn-paper 4-clip collage |
| Person card | Special Elite | red `#E3201B` | Desaturated headshot, white border, left; name right; dark grunge background |
| Date card | Special Elite, large | red `#E3201B` with a soft red glow | Full-screen dark grunge + light leaks; **types on letter by letter** |
| Name label on footage | Special Elite | pale yellow `#F3EBA6`, dark shadow | Next to a **red arrow** (`#E61E1E`) pointing at the person on first appearance |
| Quote card | Special Elite | pale yellow `#F3EBA6`, in "double quotes" | Over darkened footage, left-center, 2 lines max |
| Dialogue subtitles | Montserrat Bold, tight tracking | **one colour per speaker**: blue `#2F7BFF`, gold `#F5C443`, teal `#8EE6DF`, orange `#FF8A3D` | Bottom-center, sentence case, thin dark outline + soft shadow, no box, ~5% of frame height |

Other visual rules:
- Keep the native bodycam timestamp / "AXON BODY" overlay; it reads as authentic.
- Soft circular face blur on bystanders and minors.
- Footage is mostly uncut; cuts come at beat changes (≈ one hard cut every 7 s in part 1). Use punch-in zooms for emphasis.

## 5. Storyboard template for a new episode
1. Premise hook (2 lines) over a 6–9 s teaser montage
2. Cold-open proof clip (6–10 s, subtitled)
3. Thesis + "starting with…" → title collage → person card
4. Date card → setup (3–4 lines) ending on foreshadowing → arrow + name label
5. Loop: footage → narration ending on a tension line, × 4–8
6. Mid-case cliffhanger before the biggest moment
7. Outcome (what happened after: charges, lawsuit, firing) → bridge line to the next case

## 6. Assets to ask the user for (only if needed)
Ask once, in one message, after a clip is submitted, and only for things the edit can't do well without:
- headshot of the main officer / subject for the **person card** (if public)
- department name / patch / building photo, if the department is named and no frame shows it
- case outcome (charges, lawsuit, settlement) if the footage doesn't show it and the ending needs it
- the narrator voice recording, or approval to use TTS
Don't ask for anything that can be pulled from the footage itself (stills, names on screen, dates on the overlay).
