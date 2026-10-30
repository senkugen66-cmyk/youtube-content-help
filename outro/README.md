# MeowDude outro (4.8 s)

**Watch:** [`output/meowdude_outro.mp4`](output/meowdude_outro.mp4) (1920×1080, 30 fps, AAC stereo, ~-12 LUFS)

| t (s) | what happens |
|---|---|
| 0.00 | The icon sits there, perfectly still. |
| 0.30 | The cat face suddenly comes alive: head-tilt wiggle, little peek, *blip-blip*. |
| 0.50 | **"MEEEEOW!"**: squeaky kitten voice (~650 → 1000 → 500 Hz). The face stretches, the play-button "mouth" opens, and the tile shivers along with the squeak. |
| 1.42 | *pop*: the icon hops left and the wordmark pops on letter by letter, a bit sloppy. |
| 1.48 | **"DUUUUUDE!"**: deep slow-mo bellow (~47 Hz). Sub thump, the screen shakes, the wordmark gets squished, and the cat leans away with a tiny shocked mouth. |
| 3.38 | *boing*: a small wave bounce across the letters. The last "e" wobbles a bit. |
| ~4.45 to 4.80 | Hold on the untouched logo. |

## Files

- `output/meowdude_outro.mp4`: the finished outro
- `output/outro_audio.wav`: the full soundtrack on its own
- `output/meow.wav`, `output/dude.wav`: the two voice lines alone, for reuse elsewhere
- `assets/meowdude-logo.jpg`: the logo exactly as supplied
- `assets/voice_src/`: the raw neural-TTS takes the voices are made from

## How it's made

- **Logo:** `build_video.py` splits the supplied JPEG into layers (orange tile, cream cat face,
  orange play triangle, 8 letter glyphs) by keying its own pixels. Nothing is redrawn and the font is
  not swapped. When every layer is at rest they recompose the original logo, and edges are rebuilt
  at 2× so the small JPEG stays crisp at 1080p. The colours are sampled from the logo itself.
- **Voices:** `build_audio.py` starts from [Piper](https://github.com/rhasspy/piper) TTS takes.
  - MEOW gets a formant-preserving pitch-up, then a tape-speed warp that swoops up into the "EEE",
    with a kitten wobble on the "-ow".
  - DUDE has its "uuu" stretched on its own so the consonants stay crisp. It is then played back at
    about 0.55× speed and sags further as it goes, with some throat grit and a small room.
- **Sync:** the face, mouth and wordmark squash follow the loudness envelopes of the voice stems.
  All timings are in `timeline.py`.
- **SFX:** blip, pop, thump and boing are synthesised in code. There is no music.

## Rebuild

Requires Python 3 with `numpy scipy pillow soundfile`, plus `ffmpeg` built with librubberband.

```bash
cd outro
python3 build_audio.py      # -> output/meow.wav, dude.wav, outro_audio.wav
python3 build_video.py      # -> output/meowdude_outro.mp4
```

To tweak the jokes:

- Timing: edit `timeline.py`.
- Voices: the knobs are in `make_meow()` and `make_dude()` in `build_audio.py`.
  - In `make_meow()`, `pitch` and `base`/`peak` set how squeaky the meow is.
  - In `make_dude()`, the `warp` rate sets how deep the dude is (lower is deeper and slower).
- New voice takes: `pip install piper-tts` and run `python3 build_audio.py --regen-tts`. Each run
  gives a slightly different read.
