# YouTube Research Test: HasData MCP Verification and Gaming Thumbnail Findings

Retrieved 2026-10-26, region `gl=us`, `hl=en`. The raw evidence (video IDs, views, HasData request IDs, thumbnail URLs) is in `research/2026-10-26/evidence.csv`. The baseline computation is `research/2026-10-26/channel_baselines.py`.

## 1. MCP tool verification

| Tool | Tested with | Works | What it actually returns | Gaps |
|---|---|---|---|---|
| `getYoutubeSearchResults` | 5 queries (codes, browser games, hidden features, ads vs reality, Minecraft tips <4 min) | ✅ | title, videoId, URL, views (exact integer), length, **relative** publish date, channel name and link, verified flag, static thumbnail URL, chapters, ads/sponsored blocks, pagination | no subscriber count, no absolute date, no likes |
| `getYoutubeVideo` | `pK3FLCC6Qs0` | ✅ | **absolute** publish date, exact views, likes, channel subscribers, lengthSeconds, category, tags, detected game, captions list, related videos | no comments count seen, no CTR |
| `getYoutubeChannel` (tab=videos) | 6 channels | ✅ | subscribers, video count, ~30 latest uploads with views and relative dates, pagination tokens | Shorts are on a separate tab; dates are relative |
| `getYoutubeTranscript` | not tested | — | — | — |

**No tool provides impressions, CTR, retention, or traffic sources for any video.** Those exist only in your own channel's analytics.

**Thumbnail inspection works.** `i.ytimg.com/vi/<id>/hq720.jpg` downloads directly. I viewed 22 thumbnails at full size and at a 168 px mobile-list size.

## 2. Method

1. For each query I looked at the first results page and marked candidates that had high views *for their channel*.
2. For 6 channels I pulled about 30 recent uploads and computed **views ÷ median views of the channel's other uploads that are at least 7 days old**. This is the same idea as ThumbGen's outlier score.
3. Where possible I picked **same-channel or same-series controls**: same creator and format, much lower ratio. Holding the creator constant is the closest thing to a control that public data allows.
4. I compared outliers with low performers on the same query, especially videos near your ~3-minute format.

## 3. Outliers found

| Video | Channel (subs) | Views | Ratio vs channel median | Length |
|---|---|---|---|---|
| [You can play OG Fortnite on browser now.](https://www.youtube.com/watch?v=pK3FLCC6Qs0) | Intangible (33.9K) | 484,509 | **50×** | 3:53 |
| [What's with all the Browser Games?](https://www.youtube.com/watch?v=0D8Qk6JotAE) | Rob Humm (168) | 42,830 | **373×** (tiny base; unstable) | 1:39 |
| [Meowdoku – ads vs gameplay](https://www.youtube.com/watch?v=lYBvP2T-jU8) | WalrusLimePie (14.6K) | 468,521 | **43×** vs its own series | 11:35 |
| [Roblox Added FREE ROBUX REWARD!](https://www.youtube.com/watch?v=9OUuqetxSAQ) | BlxeWolf (682K) | 445,741 | 4.9× | 5:07 |
| [Those Ads Lied... So I Made The Real Game.](https://www.youtube.com/watch?v=7pA-9rinD44) | The Greatest Developer (71.7K) | 900,844 | 4.7× (only 5 comparisons) | 7:36 |
| [BEST Unblocked Gaming Website (2026)](https://www.youtube.com/watch?v=xuQdQcpzB0Y) | Macrolo (75K) | 100,656 | 2.4× | 1:18 |

High absolute views where no baseline was pulled:
- [Top 25 Browser Games](https://www.youtube.com/watch?v=pBt8FuO3zf4) (3.25M)
- [Minecraft Features NOBODY Uses](https://www.youtube.com/watch?v=DaSMd9aDDjs) (2.40M)
- [Kingshot Ads are FAKE](https://www.youtube.com/watch?v=IWaVLMQeOYk) (1.79M)
- [This Website Just Made EVERY Game Free](https://www.youtube.com/watch?v=dd9GucH8HkQ) (1.34M)

Low performers on the same queries:
- [9 Best New Browser Games in 2026](https://www.youtube.com/watch?v=0g0RICmWqlo) (1,606 views, 2:58)
- [6 Free Browser Games](https://www.youtube.com/watch?v=kl9jCZhHzq4) (5)
- [Ads vs Reality… Surprised Me](https://www.youtube.com/watch?v=91rd3M-Yftc) (4)
- [20 MORE Minecraft Tips](https://www.youtube.com/watch?v=zaN48de6nCM) (132, 2:57)

## 4. Observations vs hypotheses

**O = observed in the images or data. H = hypothesis, not established.**

**Pattern 1. A recognizable "proof object" beats a category label.**
- O: Every outlier shows something a viewer recognizes instantly:
  - OG Fortnite gameplay plus the Chrome logo
  - a laptop running The Simpsons: Hit & Run
  - the Meowdoku logo
  - the Robux coin plus a "Redeem" button
  - a laptop grid of real game icons (Roblox, Brawl Stars, Minecraft, Mario)
- O: The low performers on the same queries show generic imagery: an unbranded drift car, abstract gears, a grid of unknown mini-games, an item icon without context.
- H: For search-driven gaming topics, a specific, recognizable entity is what earns the click, more than a generic headline. Confound: the low performers are also tiny channels with weak distribution.

**Pattern 2. Same creator, same template, very different results, so the topic drives most of the variance.**
- O: WalrusLimePie uses an identical template (face, open-palm gesture, game logo) for Meowdoku (43×) and Warline (0.7×).
- O: BlxeWolf uses the same mock-UI-plus-arrows template for Free Robux (4.9×) and Free Happy Face (0.3×).
- O: THE GAMER KH uses the same "ALL NEW CODES!" layout for Rivals (285K) and Blox Fruits (545; only 3 hours old, so not comparable yet).
- H: Thumbnail style alone doesn't explain these gaps. Topic and offer value (Robux > a face; a cute oddball game > a generic shooter) dominate. **This is the strongest reason to never credit a thumbnail with a win without a controlled test.**

**Pattern 3. Clearer evidence on the thumbnail itself: Rob Humm.**
- O: One small channel, one topic (browser-ported games), one two-week window.
  - Selfie with a skeptical face next to a laptop showing a recognizable game, **no text**: 42,830 views.
  - Two podcast thumbnails with two people and 4–6 words of overlay text: 139 and 223 views.
- H: The proof object plus a single expressive face did better than talking heads plus abstract text. Confounds remain: the titles differ ("What's with all the Browser Games?" is a broader question), and the length differs (1:39 vs 3–4 min).

**Pattern 4. Text is minimal or absent on outliers.**
- O: The outliers carry 0–2 words: "What.", "Meowdoku", "FREE ROBUX!!", "BEST UNBLOCKER", or nothing.
- O: Several low performers carry 3–6 words that restate the title: "BEST BROWSER GAMES 2026", "6 FREE GAMES NO DOWNLOAD", "AD vs REALITY FAKE? SCAM?".
- O: At 168 px, all of these words are legible. The low performers aren't failing on readability. They're failing on *what* the text and image say.
- H: Text that duplicates the title wastes the thumbnail. One word that adds emotion ("What.") or the offer itself ("FREE ROBUX") works better.

**Pattern 5. The mock redeem UI is the convention for codes, and it is saturated.**
- O: Code and free-item videos (BlxeWolf, THE GAMER KH, TaoBlox-style titles) repeat the same pieces: a big yellow/green headline, a fake "Redeem" box, red arrows, and a Roblox avatar.
- H: In the codes niche, a thumbnail that shows the **actual reward item, large** (or the real game's UI) may stand out more than another redeem box. This is testable, not proven.

**Pattern 6. Faces, when used, show a reaction to the proof object.**
- O: Rob Humm (skeptical), ohnepixel (shocked, next to GTA running in a browser), and WalrusLimePie (side-eye plus gesture) all have the face looking at or pointing to the object.
- H: A face helps only when it reacts to something specific. The faceless outliers (Intangible, Greatest Developer, Prism) show a face isn't required.

## 5. Limitations

- **No CTR was observed for any competitor.** Views reflect topic, timing, distribution, title, and thumbnail together.
- **Small, biased sample:** 22 thumbnails, 6 baselines, one region, and only the first results page, which is itself ranked by YouTube's own signals.
- **Baseline caveats:**
  - Channel medians use relative dates ("2w ago"), and the most recent ~30 uploads mix Shorts-length and long videos.
  - Rob Humm's 373× ratio rests on a 112-view median, so it's unstable.
  - Meowdoku's baseline videos are younger than Meowdoku itself, which inflates its ratio.
- **The visual coding is my own reading**, done by one rater, not a validated instrument.

## 6. Recommended approaches for a growing gaming channel (≈3-minute videos)

1. **Lead with the proof object.** Show the exact game, item, reward, or UI the video delivers, captured from your own footage.
2. **Use 0–2 words, and only if they add something the title doesn't say.** Render text with Pillow, never with the image model.
3. **Make the topic recognizable at 168 px.** Use the game's own art style, an iconic character or item, or a logo used for identification.
4. **Design every upload as a 3-variant Test & compare set**, each testing a different hypothesis (proof object vs reaction word vs reward close-up). Log the hypothesis tags.
5. **Choose topics where public outliers show demand** (see the method in §2). The data says the topic matters more than the template.

## 7. Five initial thumbnail directions

These are reusable directions, not designs for a specific video, because no video brief was given yet. `[BRACKETS]` are filled from your brief and **your own captured frames**.

Rules for every direction:
- Never show items, rewards, or mechanics that aren't in the video.
- Image prompts are for the background/scene only. Text is composited afterwards.
- Prefer image-to-image from a real frame, so game visuals aren't invented.

### 1. "Proof Shot": for browser games, unusual ways to play, hidden features
- **Main idea:** a recognizable game running somewhere surprising (a browser window, a Chromebook, a phone), captured for real.
- **Composition and focal point:** the device fills the left ~60%, showing an unmistakable game frame. The right side is an optional reaction face or empty negative space. The focal point is the game frame.
- **Colors and lighting:** the game's native palette inside the screen; the room dimmed to about 70% so the screen is the brightest area.
- **Text:** none, or one word in the empty space ("Wait.").
- **Curiosity gap:** "How is *that* running *there*?"
- **Evidence:** Intangible (50×), Rob Humm (42.8K vs 139/223 on the same topic), ohnepixel (1.3M), Macrolo (2.4×).
- **Prompt:** "Photorealistic close-up of a slim laptop on a dark wooden desk in a dim bedroom, the laptop screen showing [REFERENCE FRAME: exact gameplay screenshot of GAME] inside a plain web-browser window, screen is the brightest element, soft blue screen glow on the desk, shallow depth of field, empty dark negative space on the right third for later text, 16:9, no text, no logos other than what appears in the reference frame."

### 2. "Reward Close-Up": for codes, free items, rewards
- **Main idea:** the actual reward the code gives, rendered huge and crisp, instead of yet another redeem box.
- **Composition and focal point:** the reward item at about 55% of the frame height, slightly left of center, rim-lit. A small, real game UI element (e.g. that game's own redeem button), bottom-right, for context. The focal point is the item.
- **Colors and lighting:** a saturated complementary background (item colour vs background hue 180° apart), radial glow behind the item.
- **Text:** "FREE" or the code's actual value (e.g. "+500 [CURRENCY]"), only if that's what the code really gives.
- **Curiosity gap:** "Which code gives this?"
- **Evidence:** BlxeWolf's Robux (4.9×) vs Happy Face (0.3×) on the same template, so the *offer* drives the result. The redeem box is saturated across code videos.
- **Prompt:** "Hero product shot of [EXACT REWARD ITEM from GAME, matching reference image] floating at center-left, [GAME] art style, strong rim light, radial glow, clean [COMPLEMENTARY COLOR] gradient background, crisp edges, large and readable at small size, empty space top-right for a short word, 16:9, no text."

### 3. "One-Word Reaction": for discoveries, updates, surprising mechanics
- **Main idea:** one striking real gameplay frame plus a single reaction word.
- **Composition and focal point:** the strongest moment from your footage, full-bleed, with the subject on a rule-of-thirds point. One word in heavy sans-serif set in the sky or other low-detail area.
- **Colors and lighting:** boost contrast and saturation about 10–15% over the raw frame; slight vignette.
- **Text:** "What." / "Wait." / "Huh?", one word only.
- **Curiosity gap:** something in the frame looks wrong or new, and the word confirms it.
- **Evidence:** Intangible's "What." over real OG Fortnite gameplay (50×).
- **Prompt (enhancement, not invention):** "Enhance this [REFERENCE FRAME]: increase clarity and contrast, subtle vignette, keep all game elements exactly as they are, clean up the sky area to a smooth gradient for text placement, 16:9." *Use image-to-image only; never generate the gameplay from scratch.*

### 4. "Named Contrast": for "ad vs reality", expectations vs reality
- **Main idea:** a split frame of the real ad frame vs the real gameplay frame, with the game's name or logo for identification.
- **Composition and focal point:** a diagonal split. Left: the ad frame, with saturation pushed up. Right: the real frame, slightly desaturated. A logo or game name centred on the split. Optional reaction face at the right edge, looking at the right side.
- **Colors and lighting:** the left half warm and vivid, the right half cooler, so the difference reads at a glance.
- **Text:** the game name (if the logo is unclear), plus nothing else. Avoid "FAKE?/SCAM?" stamps.
- **Curiosity gap:** "How different is it really?"
- **Evidence:** WalrusLimePie's Meowdoku (43×) and William Kitten's Kingshot (1.79M) name a specific game. The generic AI-gears "AD vs REALITY" thumbnail got 4 views.
- **Prompt:** "Diagonal split-screen composition, left half [REFERENCE: real ad frame of GAME] with vivid warm grading, right half [REFERENCE: real gameplay frame of GAME] with cooler muted grading, thin white diagonal divider, center area left clear for a logo, 16:9, no text." Composite the real frames yourself where possible.

### 5. "Question Object": for "how do I…?" search questions
- **Main idea:** the single object, setting, or location that answers the viewer's search question, isolated and spot-lit. No arrows or circles.
- **Composition and focal point:** the object (item, menu toggle, map location) cut out and placed large left-of-center on a softly blurred in-game background. A spotlight vignette does the job of an arrow.
- **Colors and lighting:** the background desaturated and darkened about 30%; the object at full saturation with a soft glow.
- **Text:** 1–2 words naming the *outcome*, not the question (e.g. "INFINITE [X]"), only if accurate.
- **Curiosity gap:** the viewer recognizes the object but not how it helps.
- **Evidence:** Prism's text-free, three-panel item close-ups (2.40M, no baseline). The low-performing Minecraft tips thumbnail (132 views) relied on "KEEP THESE!" text plus a red arrow instead of a clear subject.
- **Prompt:** "Isolated [OBJECT from GAME, matching reference] large at left-center, soft glow, background is a blurred, darkened, desaturated [GAME LOCATION reference], spotlight vignette centered on the object, clean and minimal, readable at thumbnail size, 16:9, no arrows, no circles, no text."

**Choosing a set of 3 for Test & compare:** pick directions that test *different hypotheses*, for example #1 (proof object), #3 (reaction word), and #2 or #5 (object close-up). Keep the title fixed during the test.
