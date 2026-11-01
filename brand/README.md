# MeowDude

MeowDude is a gaming tutorial channel with one recurring host: an abstract orange cat with a folded ear, a screen in its belly and a tail that ends in a pointer. Every video is a short, fast explainer: MeowDude shows you the thing, points at it, and moves on.

The look is a minimalist, hand-drawn 2D editorial illustration. It should feel clever, modern and a little playful. It should not feel childish, corporate or like generic AI animation.

This folder is the single source for that look. Use these files in every video:

| File | What it is |
| --- | --- |
| `README.md` | This page: principles, colour, type, layout, do's and don'ts, the per-video checklist |
| `character.md` | MeowDude's construction, proportions, poses and expressions |
| `motion.md` | Animation timing, entrances, annotation draw-ons, transitions |
| `tokens.json` / `tokens.css` | Colours, type styles, spacing, radii, stroke weights, motion timings |
| `mascot/` | The six poses, avatar, silhouette mark and construction sheet (SVG) |
| `annotations/` | Arrows, circles, underlines, brackets, tick, cross and highlighter (SVG) |
| `ui/` | Key caps, mouse, cursor, pad button and UI panel props (SVG) |
| `tools/build_assets.py` | Regenerates every SVG from one set of shapes and colours |

Never redraw MeowDude by hand for a video. Import the SVGs. If a new pose is needed, add it to `tools/build_assets.py` so it shares the same body, outlines and colours, then run `python3 brand/tools/build_assets.py`.

## Five principles

1. **MeowDude leads, the game follows.** Every beat starts from the character: it looks, points, reacts. Footage and UI support the character, not the other way round.
2. **One idea per frame.** One instruction, one highlighted word, one pointer. If a frame needs two arrows, it is two beats.
3. **Things appear when they matter.** A UI element, key or item enters the frame on the line of voice-over that names it, and leaves when the point is made.
4. **Flat and drawn.** Solid fills, ink outlines, nothing rendered. If it could have been drawn with a marker and cut from coloured paper, it fits.
5. **Same every time.** Same proportions, same seven colours, same line weights, same two typefaces. Recognition comes from repetition.

## Colour

Seven flat colours. No gradients, no shadows from lighting, no gloss, no textures, no transparency effects, no glows. The only "shadow" allowed is the hard, solid ink offset under key caps and pad buttons, which is a drawn shape, not light.

| Token | Hex | Role |
| --- | --- | --- |
| `ink` | `#17161F` | Every outline, the eyes, clean type on Paper |
| `paper` | `#ECEAF3` | Default ground, belly screen, key caps, UI panels |
| `night` | `#22223A` | Alternate ground for menus, dark scenes, end cards |
| `tangerine` | `#FF7A2F` | MeowDude only (body, hands, tail tip) and the logo |
| `marker` | `#FFD84A` | Emphasis: highlighter swipe, hype |
| `signal` | `#3EC5E8` | Do this: interactive UI, correct choice, tick |
| `alert` | `#FF5C8A` | Don't do this: warnings, crosses, mistakes |

### Colour rules

- **Tangerine belongs to MeowDude.** No other object, UI element or piece of text is tangerine. That keeps the character the brightest, most recognisable thing in every frame.
- **Colour carries meaning.** Marker means "remember this", signal means "do this", alert means "avoid this". Never use them decoratively.
- **At most two accent colours per frame**, plus tangerine on the mascot. A frame with marker, signal and alert at once is a frame doing too much.
- **Text is ink on Paper and Paper on Night.** Never put type in tangerine, signal or alert; those fail contrast on Paper. A highlighted word is ink type on a marker swipe.
- **Game footage** sits inside a Paper-outlined frame (`stroke-detail`, `radius-panel`) so it reads as an object MeowDude can point at, not as the background.
- **Grounds**: Paper by default. Use Night for in-menu walkthroughs, dark game areas and the end card. Only the ground, text and annotation lines change colour; the mascot and props keep their ink outlines on both grounds.

## Line

- One outline colour: `ink`.
- Three weights at the mascot's base size (330 px tall): `stroke-body` 6 px, `stroke-detail` 5 px, `stroke-mark` 9 px. Scale whole drawings so these stay proportional; never thicken or thin single strokes.
- Round caps and round joins everywhere.
- Annotations use the same 5 px weight relative to a 1080p frame, so arrows feel like they were drawn with the same pen as the character.
- No sketchy multi-pass lines, no line boil. The hand-drawn feel comes from slightly uneven curves and asymmetry, not from texture.

## Typography

Two families, both on Google Fonts and free for commercial video.

- **Archivo** (clean): instructions, labels, captions, key glyphs. Use ExtraBold 800 at 112% width for the bold instruction. That expanded weight is MeowDude's voice: confident, a bit chunky, not corporate.
- **Shantell Sans** (hand): annotations and asides. It is built from real marker handwriting, so it reads as drawn but stays legible at speed.

| Style | Font | Size at 1080p | Use |
| --- | --- | --- | --- |
| `instruction` | Archivo 800, 112% width | 72 px | The one bold instruction per beat, max six words |
| `label` | Archivo 700 | 40 px | UI element names, stats, item names |
| `caption` | Archivo 500 | 34 px | Optional supporting fact |
| `keyglyph` | Archivo 800 | 44 px | Letter inside a key cap or pad button |
| `note` | Shantell Sans 600 | 48 px | Handwritten label next to an arrow or circle, lowercase |
| `aside` | Shantell Sans 500 | 36 px | Jokes and asides, rotated -4 to 4 deg |

### Type rules

- **Minimal text.** The voice-over explains; the screen shows. An instruction is six words or fewer. A handwritten note is two to four.
- **Bold the action.** In an instruction the verb and the input are what matter: "**Hold E**, then jump". Put the single most important word on a marker swipe.
- Handwritten notes are lowercase and never more than one line. Clean type is sentence case. Never all caps except key names (`ESC`, `TAB`).
- Never set a full sentence in Shantell Sans, and never use Archivo for jokes.

## Layout (1920 x 1080)

- **Title-safe margin** `space-4` (96 px). Nothing readable outside it.
- **MeowDude lives in a third.** Standing in the lower-left or lower-right third, 40 to 45% of frame height (about 440 to 480 px), feet on an implied floor 96 px above the bottom edge. The rest of the frame is content.
- **MeowDude faces the content.** The pointing pose and the tail aim into the frame, never out of it. Flip the SVG horizontally when MeowDude stands on the right.
- **Close-ups**: for reactions, crop to the head and screen at 70 to 90% of frame height. Never crop through the eyes or the folded ear.
- **The instruction** sits top-left or top-centre, aligned to the margin, `space-3` (48 px) above whatever it describes.
- **Annotations** sit `space-1` (12 px) from what they label. Arrows start near the note and end just short of the target, never touching it.
- Flush-left composition is the default. Centre only for title cards and the end card.

## Do and don't

| Do | Don't |
| --- | --- |
| Flat fills, ink outlines | Gradients, glows, bevels, drop shadows, gloss, grain, 3D |
| One pointer per beat | Several arrows fighting for attention |
| Recolour annotations only by meaning (signal / alert / marker) | Rainbow arrows, decorative colour |
| Import MeowDude from `mascot/` | Redraw, restyle, add a mouth full of teeth, give it a nose, add fur or whiskers |
| Simplify game UI into flat panels and keys from `ui/` | Paste screenshots of UI as decoration |
| Hard cuts, the tail wipe at section changes | Spins, whip pans, zoom blur, glitch, 3D flips, star wipes |
| Let MeowDude react to the information | Bounce or wiggle elements just to fill time |

## Per-video checklist

Before export, check every frame against this list.

- [ ] MeowDude imported from `mascot/` at an unchanged aspect ratio; outlines not restyled.
- [ ] Only the seven palette colours appear outside raw game footage. Nothing is tangerine except MeowDude and the logo.
- [ ] No gradients, shadows, glows, textures or transparency effects anywhere.
- [ ] Every instruction is six words or fewer with the action in bold, and at most one highlighted word.
- [ ] Each frame has at most one pointer and at most two accent colours.
- [ ] Every element appears on the voice-over line that names it and leaves when its point is made.
- [ ] Timings follow `motion.md`: 6-frame pops, 8 to 12-frame draw-ons, 45-frame minimum hold.
- [ ] Transitions are hard cuts, plus the tail wipe at section changes only.
- [ ] Text inside the 96 px title-safe margin and readable on a phone.
