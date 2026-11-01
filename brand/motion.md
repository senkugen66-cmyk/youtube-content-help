# Motion

Fast, clean 2D motion that is led by the character. Movement exists to move information. If an animation doesn't point at, reveal or react to something, cut it.

All timings are in frames at **30 fps** (1920 x 1080). At 60 fps, double them.

## Frame rate and feel

- Deliver at 30 fps.
- **Character on twos.** MeowDude's poses and arm moves are animated at 15 drawings per second. That gives a hand-made cadence.
- **Graphics on ones.** Annotations, UI pops, camera moves and text run at the full 30 fps so they stay crisp.
- No motion blur, no line boil, no idle jitter.

## Timing table

| Action | Frames | How |
| --- | --- | --- |
| Pop in (UI, key cap, item, panel) | 6 | Scale 0 to 108% over 4 frames, settle to 100% over 2. Ease `ease-pop`. No fade. |
| Exit | 4 | Scale to 0 or a hard cut. Never fade out. |
| Annotation draw-on (arrow, circle, underline) | 8 to 12 | Stroke reveals start to end, ease `ease-draw`. The arrowhead draws in the last 2 frames. |
| Highlighter swipe | 6 | Marker shape wipes left to right behind the word. The word is already there. |
| Handwritten note | 3 per word | Words appear one at a time, each with a 2-frame pop. No letter-by-letter typing. |
| Instruction text | 6 | Whole line pops as one block. The highlight swipe follows 2 frames after. |
| Tick / cross | 6 | Two strokes: the short stroke in 2 frames, the long in 4. |
| Pose change | 4 | Anticipation frame, one smear frame, the new pose, 2-frame settle. |
| Ear follow-through | +2 | Ears land 2 frames after the body on every pose change. |
| Squash on landing | 2 | 94% height and 106% width, then back. Never more than 6%. |
| Blink | 2 | Every 2 to 4 seconds at random while MeowDude is on screen. Eyes go to a 4 px line. |
| Hold | 45 minimum | Every information beat holds at least 1.5 s after its last element lands. |
| Push-in | 12 | 100 to 110% scale, ease out. Max one per scene. |

`tokens.css` has these as CSS custom properties (`--pop`, `--draw`, `--exit`, `--ease-pop`, `--ease-draw`).

## Sequencing a beat

A beat is one idea. Build every beat in this order:

1. **MeowDude reacts** (pose change, 4 frames), reading the line of voice-over.
2. **The subject appears** (pop, 6 frames) on the word that names it.
3. **The pointer** (arm, tail or drawn arrow, 8 to 12 frames) lands on the subject.
4. **The instruction** pops (6 frames), and the highlight swipe follows.
5. **Hold** for at least 45 frames.
6. **Clear**: elements exit (4 frames) or the shot hard-cuts to the next beat.

Stagger entrances by 2 to 4 frames. Never bring in more than three elements in one beat.

## Pointing

- The pointing arm extends in 4 frames, overshoots by about 5% and settles in 2.
- MeowDude's eyes look at the target 2 frames before the arm moves. Viewers follow the eyes first.
- Drawn arrows begin at the note and end 12 px short of the target.
- The scribble circle starts at the top left, goes clockwise and overshoots its start.

## Objects and UI

- Simplify game UI into flat props from `ui/`: Paper fill, ink outline, `radius-panel` corners. Show only the part of the UI that matters.
- Key caps press down by 4 px (onto their ink base) for 2 frames when the voice-over says "press".
- Game footage enters in a framed panel with a 6-frame pop and can be pointed at like any other object.

## Transitions

Hard cuts by default. Inside a section, every change of beat is a cut or an in-shot change.

One signature transition, used **only between sections**:

- **Tail wipe** (10 frames): MeowDude's pointer tail sweeps across the frame from one side to the other, and the new ground (Paper or Night) fills in behind it as a flat shape. No blur and no easing tail.

Never use cross-dissolves, spins, whip pans, zoom blurs, glitches, page curls, 3D flips or light leaks.

## Things that read as generic

Avoid these; they make the channel look like template or AI-generated animation.

- Everything gently floating or bobbing at rest.
- Elements bouncing in with long elastic wobble.
- Text typing on letter by letter with a cursor.
- Particles, sparkles, confetti or lens flares.
- Camera drift that isn't motivated by a new subject.
- Characters lip-syncing with a cycling mouth. MeowDude's mouth changes by expression only.

## Reduced-motion and accessibility

- Every instruction stays on screen for at least 1.5 s, long enough to read on a phone.
- Never flash an alert colour more than three times per second.
- Captions are styled in `caption` (Archivo 500), ink on Paper, bottom-centre inside the safe margin.
