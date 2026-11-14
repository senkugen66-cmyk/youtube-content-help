# EditFlo — product film

This folder turns the Loom pitch recording into a motion-graphics product film (1920×1080, 30 fps). The final file is `EditFlo_ProductFilm.mp4`.

## How it's built

| Step | File | What it does |
|---|---|---|
| 1. Cut list | `edl.py` | Keeps the clean take, drops the false start (source 0:43–0:57) and the aside (source 2:50–3:34), and shortens long pauses. Writes `edl.json` and `cues.json` |
| 2. Voice | `voice.py` | Cuts the narration to the edit list, then applies a high-pass filter, light denoise, compression and loudness normalisation → `build/voice.wav` |
| 2b. Presenter | `face.py` | Cuts the Loom webcam bubble to the same edit list, so lips stay in sync, enlarges it and writes `build/face/%05d.jpg`. Run before rendering |
| 3. Motion graphics | `film.html` | Every frame is a pure function of time (`render(t)`). Scenes are timed to the source-recording timestamps of the words being spoken |
| 4. Frames | `render.js` | Headless Chromium renders each frame and pipes it to x264 (`node render.js 30 4 build`) |
| 5. Music + SFX | `audio.py` | Synthesises an original, quiet music bed and restrained UI sounds, placed at the cue points declared in `film.html` |
| 6. Mix + mux | see below, then `finish.sh` | Music is side-chain ducked under the voice; final loudness is −15 LUFS |

The mix command used:

```
ffmpeg -i build/voice.wav -i build/music.wav -i build/sfx.wav -filter_complex "[0]aresample=48000,apad=whole_dur=181.0,asplit[v][key];[1]volume=-3dB[m];[m][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500:makeup=1[md];[2]volume=0dB[s];[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.94:level=disabled" -ar 48000 -ac 2 build/mix.wav
```

The source recording isn't committed. Put it at the path at the top of `voice.py` to rebuild.

## Revision 02: founder presence

`PRES` in `film.html` lists the source-time ranges where the presenter appears: the opening line, introducing EditFlo, "only half the work", "I spoke directly with creators", "a clear condition", "meet your new assistant editor", "an assistant, not a replacement", the business model, the next step, "I'd rather show you", and the closing. During each range, the existing scene layer eases into the right-hand column, scaled about the right edge, and the presenter window takes the left column. The scenes themselves are unchanged. The presenter is on screen for about 57s of 181s (32%).

The source camera is about 86px across in a 480p Loom export, so there are no full-screen presenter shots. A sharper recording can be dropped into `face.py` (adjust the crop) and everything else re-renders unchanged.

## Brand tokens

| Token | Value |
|---|---|
| Purple | `#7B2CBF` |
| Lavender | `#C8A2E8` |
| Background | `#F8F5F0` |
| Ink | `#1E1B22` |
| Type | Inter Display / Inter, with JetBrains Mono for labels |
