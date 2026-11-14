#!/bin/bash
# Joins rendered parts and muxes the final mix. Run after render.js + audio.py + mix step.
set -e
cd "$(dirname "$0")"
ffmpeg -v error -y -f concat -safe 0 -i build/parts.txt -c copy build/video.mp4
ffmpeg -v error -y -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=8 -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart EditFlo_ProductFilm.mp4
ffprobe -v error -show_entries format=duration,size -of compact EditFlo_ProductFilm.mp4
