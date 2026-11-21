# Night-town animation kit

A code-driven 2D illustrated animation pipeline for the channel's cartoon mysteries.
Every frame is a pure function of time, so any frame can be re-rendered exactly, and
episodes are plain JS files you can edit.

```
engine/core.js     seeded RNG, noise, easing, keyframe tracks, parallax camera
engine/draw.js     ink-wobble shapes (line "boil" at 8 drawings/sec), glows, grain + vignette
engine/props.js    reusable set: sky/moon/clouds, distant town, houses, windows, lamps, trees, fence, fog
episodes/<ep>/     scene.js (layout + CONFIG timing), storyboard.json (panel notes)
player.html        live preview with scrubber: player.html?ep=ep00-lit-town
tools/render.mjs   Playwright renderer: stills or full frame sequence
tools/storyboard.py  labelled storyboard sheet from rendered stills
```

## Commands (run from `animation/`)

```bash
node tools/render.mjs stills ep00-lit-town 0.5 4.57 8 10.3 11.2 12.4 14.1 14.7
python3 tools/storyboard.py ep00-lit-town
node tools/render.mjs frames ep00-lit-town
```

Preview: `python3 -m http.server` in `animation/`, then open `http://localhost:8000/player.html`.

## New episode

Copy `episodes/ep00-lit-town/`, change `META`, the house layout and `CONFIG`
(camera keys, flicker events, reveal times). Props in `engine/` are shared.
