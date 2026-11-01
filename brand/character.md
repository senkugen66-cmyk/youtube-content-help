# Character: MeowDude

MeowDude is a cat reduced to three ideas: a soft upright slab of a body, one sharp ear and one folded ear. Everything else is a tool for explaining things. The belly is a screen, the tail is a pointer, the arms are lines that can reach anything in frame.

Personality: a competent friend who has already 100%'d the game. Dry, quick, a little smug when the trick works, openly embarrassed when showing a mistake. Never hyperactive, never babyish.

## Construction

All measurements use **E**, the height of one eye (28 px on the 330 px master).

| Part | Rule |
| --- | --- |
| Total height | **10 E**, ear tip to foot |
| Body width | **5 E** at the widest point (the hips) |
| Silhouette | One closed shape: head, body and both ears with no neck. Slightly wider at the base. The left flank is straighter than the right. |
| Left ear | Sharp triangle. Its tip is the highest point of the character. |
| Right ear | **Folded outward**, with a flat top and one crease line. This is the signature: it must be visible in every shot. |
| Eyes | Two vertical pills, 0.5 E wide by 1 E tall, about 1.6 E apart (centre to centre). The right eye sits slightly higher. No pupils, no highlights. |
| Mouth | A small cat "w", centred under the eyes, 0.9 E wide. No nose, no whiskers, no teeth. |
| Belly screen | Rounded rectangle, about 2.4 E x 2 E, `radius-screen`, Paper fill with an ink outline. Centred, its top edge 1.5 E below the mouth. |
| Arms | Single ink lines (`stroke-body`) from the shoulders, ending in round tangerine mitten hands, 0.65 E across. No fingers. |
| Legs | Two short ink lines with flat feet turned outward. |
| Tail | Ink line from the lower right of the body, ending in a **tangerine triangle pointer**. |

`mascot/meowdude-construction.svg` shows the 10 E grid on the neutral pose.

### Colour on the character

- Body, hands and tail tip: `tangerine`.
- Outlines, eyes, mouth, limbs: `ink`.
- Screen: `paper` by default, recoloured only by state (below).
- Nothing else. MeowDude never gets shading, blush, highlights or a second body colour.

## The belly screen

The screen is MeowDude's status display, and it's how the character carries information without extra UI.

| Screen colour | Glyph | Meaning |
| --- | --- | --- |
| `paper` | play triangle | Ready, intro, default |
| `signal` | arrow | Look here / do this |
| `paper` | three dots | Thinking, setting up a problem |
| `marker` | tick | It worked, the payoff |
| `alert` | ! | Mistake, warning |
| `paper` | blank | Deadpan |

The screen can also show **content**: a key glyph (`E`, `LMB`, `RB`), an item icon or a number. Keep it to one glyph in ink, drawn flat. When the screen shows content it stays Paper.

## The pointer tail

The tail tip is a pointer. Use it:

- to point at a second thing while the arm points at the first (the only time a frame may have two pointers);
- as the **tail wipe** transition between sections (see `motion.md`);
- in the oops pose, drooping down as a visual "fail".

## Poses

Six master poses live in `mascot/`. Each one is a recurring beat in a tutorial, so viewers learn to read them.

| File | Pose | Use it for |
| --- | --- | --- |
| `meowdude-neutral.svg` | Arms down, tail up, play screen | Intros, listening, idle between beats |
| `meowdude-point.svg` | Hand on hip, arm and tail pointing right, signal screen | Directing attention to UI, a map spot, an item |
| `meowdude-think.svg` | Hand to chin, eyes up, dots screen | Setting up a problem or question |
| `meowdude-hype.svg` | Both arms up, happy eyes, open mouth, marker tick screen | The payoff, the trick works |
| `meowdude-oops.svg` | Scrunched eyes, hand on head, tail drooping, alert screen | Common mistakes, what not to do |
| `meowdude-deadpan.svg` | Half-lidded eyes, shrug, blank screen | Dry humour, obvious bad ideas |

Also in `mascot/`:

- `meowdude-avatar.svg`: channel avatar, head on Night.
- `meowdude-silhouette.svg`: one-colour mark for watermarks and the end card.

### Rules for new poses

- Change only arms, tail, eyes, mouth and the screen. The silhouette never changes shape, except for squash and stretch in motion (`motion.md`).
- Keep both ears visible. If a pose hides the folded ear, change the pose.
- Hands stay round mittens. Gestures are made with arm direction, not fingers.
- Expressions use only the eye and mouth parts in `tools/build_assets.py`. If you need a new one, add it there so every video gets the same version.
- Mirror the whole SVG when MeowDude stands on the right of frame. The folded ear then appears on the left; that is correct.

## Voice and presence

- MeowDude reacts to information more than it performs. A slight lean and a screen change beats a jump.
- The character never talks over the content. When the instruction appears, MeowDude holds still or points; it does not gesture at the same time.
- Use the hype pose sparingly, once or twice per video, so it still means something.
