# youtube-content-help

Tools and notes for a SFW crime-scene dashcam narration channel.

- `PLAYBOOK.md` — format, retention structure, SFW/licensing rules, workflow.
- `tools/jumpcut.py` — auto-editor based on [carykh/jumpcutter](https://github.com/carykh/jumpcutter)'s
  silence-detection idea, rebuilt on ffmpeg filter graphs (no frame dumping, handles long videos).
  Requires `ffmpeg`, `ffprobe`, `python3`, `numpy`. Run with `-h` for options.
- `examples/build_demo.py` — builds a fully fictional ~50 s example episode end to end (TTS stand-in voice →
  raw take with dead air → `tools/jumpcut.py` → timed dashcam-style visuals, captions, ducked music).
