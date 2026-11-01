# Cow-hood character idle loop (2D mesh-warp rig)

Turns a single flat character illustration into a seamless 6 s idle loop (1080x1920, 30 fps) without redrawing frames.

1. `python3 prep.py <character.jpg> .` cuts the figure off the white background and lifts the tail onto its own layer (`body.png`, `tail.png`).
2. `python3 render.py video out.mp4` renders the loop (`render.py preview 0,54` saves single frames instead).

What moves: weight shift from the feet, breathing (the torso stretches, the shoulders and head lift), head tilt that trails the body, ear flicks, a pendulum bell, arm sway, tail sway, and three blinks (one of them a double blink). Every cycle uses a whole-number frequency, so the loop is seamless.

The artwork isn't committed. It belongs to the artist (ARVANES), so get their permission before posting anything made from it.

## Performance clips (`moves.py`)

`python3 moves.py <bounce|hop|sway|shy>` renders one clip. Use `moves.py hop preview 8,22` to save single frames instead.

- **bounce** (4 s loop): knees bend and spring back once a second. The ears, bell and tail follow a moment late.
- **hop** (3 s, two hops): crouch, launch with a stretch, airborne arc, squash on landing, settle. The ears and tail trail the body's speed, and the shadow fades while airborne.
- **sway** (4 s at 120 BPM): rocks to one side per beat and dips through the centre. The head counter-tilts, and the ears, bell and tail swing like pendulums.
- **shy** (4 s, starts and ends neutral): ears droop and tremble, head tilts down, shoulders shrug, eyes glance away, cheeks blush, then the pose relaxes back.

## Cinematic 16:9 reveal (`film.py`)

`python3 film.py 0 240 out.mp4` renders the 10 s, 1280x720, 24 fps clip (`film.py preview 60,150` saves single frames instead). The camera starts on the shoes, tilts up to a face close-up, then pulls back to a waist shot and slowly pushes in. Four-leaf clovers drift past at different depths, a gold light trail sweeps around the character, and sparkles and bokeh fill the background. The character does an idle, then a shy beat. The character layer is rendered at 3x so the close-up stays sharp.
