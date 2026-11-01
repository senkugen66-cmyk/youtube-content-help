# Cow-hood character idle loop (2D mesh-warp rig)

Turns a single flat character illustration into a seamless 6 s idle loop (1080x1920, 30 fps) without redrawing frames.

1. `python3 prep.py <character.jpg> .` cuts the figure off the white background and lifts the tail onto its own layer (`body.png`, `tail.png`).
2. `python3 render.py video out.mp4` renders the loop (`render.py preview 0,54` saves single frames instead).

What moves: weight shift from the feet, breathing (the torso stretches, the shoulders and head lift), head tilt that trails the body, ear flicks, a pendulum bell, arm sway, tail sway, and three blinks (one of them a double blink). Every cycle uses a whole-number frequency, so the loop is seamless.

The artwork isn't committed. It belongs to the artist (ARVANES), so get their permission before posting anything made from it.
