# Ep. 01 · Roll into it

A 25-second sample MeowDude tutorial built entirely from the `brand/` kit. Topic: dodge-roll invincibility frames (a mechanic shared by many action games), so it doesn't depend on any one game's footage.

| Time | Frames | Beat | MeowDude |
| --- | --- | --- | --- |
| 0:00 | 0-89 | "Stop rolling **away**." | neutral |
| 0:03 | 90-299 | The boss swing out-reaches a backwards roll: hit | think, then oops |
| 0:10 | 300-509 | "Roll **into** the swing": roll timeline, invincible window, roll through | point, then hype |
| 0:17 | 510-669 | "Press it **as it swings**": tell, then Space | point |
| 0:22 | 660-749 | Tail wipe to the Night end card: "next: parry windows" | hype |

There is no audio yet. Record the voice-over to the beat timings above.

## Files

- `episode.src.html`: the scene. Every visual state is a pure function of the frame number (`render(f)`), so the browser preview and the MP4 match frame for frame.
- `build.mjs`: inlines the mascot SVGs and fonts into `episode.html` and renders `episode.mp4`.
- `episode.html`: self-contained, playable in any browser, with a frame scrubber and timecode.
- `episode.mp4`: 1920x1080, 30 fps, H.264.
- `fonts/`: Archivo and Shantell Sans (SIL Open Font License), latin subset.

```sh
node videos/01-iframes/build.mjs            # rebuild episode.html
node videos/01-iframes/build.mjs --render   # also render episode.mp4 (needs ffmpeg + Playwright)
```
