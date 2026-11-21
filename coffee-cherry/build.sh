#!/bin/sh
# One command: picture → events → mix → master → ripening.mp4.   Usage: LIB=<lemo-opuscar library> sh build.sh
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$HOME/lemo-opuscar}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder (sh <skill>/scripts/setup.sh prints it)"; exit 1; }
PY="$LIB/.venv/bin/python"
[ -f "$HERE/paper.jpg" ] || "$PY" "$HERE/paper.py" "$HERE/paper.jpg"
[ -f "$HERE/fonts.css" ] || (cd "$HERE" && node fetch_fonts.mjs)
[ -f "$HERE/voices/v01.wav" ] || { "$PY" "$LIB/core/tts/tts.py" "$HERE/tts/lines.json" "$HERE/voices"; "$PY" "$LIB/core/tts/asr_check.py" "$HERE/tts/lines.json" "$HERE/voices" --lang en; }
"$PY" "$LIB/core/audio/sampler.py" --need piano
cd "$LIB"
node core/render/events.mjs "$HERE"
rm -f "$HERE/out/video.mp4"
node core/render/video.mjs "$HERE" --fps 60 --workers 4 --out "$HERE/out/video.mp4"
"$PY" "$HERE/mix.py"
# ffmpeg 7+: the library's own master. ffmpeg 6 (refused by mux.sh): BS.1770 master in Python, then a plain mux.
if ! sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/ripening.mp4" 60 1; then
  echo "mux.sh unavailable here; mastering with master.py"
  "$PY" "$HERE/master.py"
  ffmpeg -v error -y -i "$HERE/out/video.mp4" -i "$HERE/out/master.wav" -map 0:v -map 1:a \
    -vf "fps=60,noise=c0s=1:allf=t,format=yuv420p" -c:v libx264 -preset slow -crf 19 -r 60 \
    -c:a aac -b:a 256k -movflags +faststart -shortest "$HERE/ripening.mp4"
fi
