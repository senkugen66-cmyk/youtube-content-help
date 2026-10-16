# youtube-content-help

SFW crime / bodycam / dashcam narration channel. Goal: high-retention edits.

- **Follow `STYLE.md`** for every edit and script: structure, narration tone, typography, colours.
  Fonts live in `assets/fonts/` (pass `fontsdir` to ffmpeg's `subtitles` filter).
- `PLAYBOOK.md` has the SFW / licensing rules. They override STYLE.md if they conflict.
- Tools: `tools/jumpcut.py` (silence cutting), `tools/shorts.py` (vertical Shorts from a JSON plan,
  example `edits/fridge.json`), `examples/build_demo.py`.
- Never commit footage or rendered video; only plans, tools and fonts.

## Workflow when the user submits a clip
1. Analyse it first: transcript (faster-whisper medium.en; decode with ffmpeg and pass the array), contact
   sheet, speakers, key moments.
2. Then, **only if necessary**, ask in ONE message for the assets the edit can't do without
   (see STYLE.md §6, e.g. officer headshot for the person card, department photo/patch, case outcome).
   If nothing is missing, don't ask; just edit.
3. Draft the narration script in the STYLE.md voice and show it before rendering long-form edits.
4. Flag uncertain transcript lines for the user to verify before posting.
