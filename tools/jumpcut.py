#!/usr/bin/env python3
"""Silence-based auto editor, ported from carykh/jumpcutter's logic
(volume threshold + frame margin) onto ffmpeg filter graphs, so no per-frame
JPEG dump, no temp folder, and long videos are fine.

Modes
  narration : cut the dead air out of a voiceover (wav/mp3/mp4).
              Optionally lay it over dashcam footage with --bg.
  footage   : speed up / drop the quiet stretches of a video that has its own
              audio (e.g. long driving before the incident).

Examples
  jumpcut.py narration.wav -o tight.wav
  jumpcut.py narration.wav --bg dashcam.mp4 -o episode.mp4
  jumpcut.py dashcam.mp4 --mode footage --silent-speed 6 -o dashcam_fast.mp4
"""
import argparse, json, subprocess, sys, tempfile, os
import numpy as np

RATE = 16000


def decode_mono(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def has_video(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_type", "-of", "csv=p=0", path], capture_output=True, text=True)
    return "video" in out.stdout


def find_segments(samples, threshold, margin, min_gap, win=0.02):
    """Return [(start_s, end_s, loud)] covering the whole file."""
    n = int(RATE * win)
    frames = len(samples) // n
    peak = np.abs(samples[: frames * n]).reshape(frames, n).max(axis=1)
    # relative to a robust "loud" level so one cough/click doesn't skew it
    ref = max(np.percentile(peak, 99), 1e-6)
    loud = (peak / ref) >= threshold
    m = int(round(margin / win))
    if m:
        loud = np.convolve(loud.astype(int), np.ones(2 * m + 1, dtype=int), "same") > 0
    # bridge short silences (breaths between words) so speech isn't chopped up
    g = int(round(min_gap / win))
    segs, start = [], 0
    for i in range(1, frames + 1):
        if i == frames or loud[i] != loud[start]:
            segs.append([start, i, bool(loud[start])])
            start = i
    for s in segs:
        if not s[2] and (s[1] - s[0]) < g and s is not segs[0] and s is not segs[-1]:
            s[2] = True
    merged = []
    for s in segs:
        if merged and merged[-1][2] == s[2]:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [(a * win, b * win, l) for a, b, l in merged]


def atempo_chain(speed):
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0"); speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5"); speed /= 0.5
    parts.append(f"atempo={speed:.5f}")
    return ",".join(parts)


def build_graph(segments, silent_speed, with_video, fade=0.01):
    """segments: [(start, end, loud)]. silent_speed 0 => drop silence."""
    lines, labels = [], []
    k = 0
    for a, b, loud in segments:
        speed = 1.0 if loud else silent_speed
        if speed == 0 or b - a < 0.03:
            continue
        af = f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS"
        if speed != 1.0:
            af += "," + atempo_chain(speed)
        d = (b - a) / speed
        if d > 2 * fade:
            af += f",afade=t=in:d={fade},afade=t=out:st={d - fade:.3f}:d={fade}"
        lines.append(af + f"[a{k}]")
        if with_video:
            vf = f"[0:v]trim={a:.3f}:{b:.3f},setpts=(PTS-STARTPTS)/{speed}"
            lines.append(vf + f"[v{k}]")
            labels.append(f"[v{k}][a{k}]")
        else:
            labels.append(f"[a{k}]")
        k += 1
    if not k:
        sys.exit("No segments survived; lower --threshold.")
    n_v = 1 if with_video else 0
    outs = "[v][a]" if with_video else "[a]"
    lines.append("".join(labels) + f"concat=n={k}:v={n_v}:a=1{outs}")
    return ";\n".join(lines)


def run_ffmpeg(args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats"] + args, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("--mode", choices=["narration", "footage"], default="narration")
    p.add_argument("--threshold", type=float, default=0.06, help="0-1, relative to loud speech level (raise if hiss is kept)")
    p.add_argument("--margin", type=float, default=0.12, help="seconds kept around speech")
    p.add_argument("--min-gap", type=float, default=0.25, help="silences shorter than this are kept (natural pauses)")
    p.add_argument("--silent-speed", type=float, default=0, help="0 = cut silence; >1 = speed it up instead")
    p.add_argument("--bg", help="dashcam footage to loop/trim under the narration (narration mode)")
    p.add_argument("--bg-volume", type=float, default=0.0, help="footage's own audio level under narration (0 = mute)")
    p.add_argument("--report", help="write segments + timing JSON here")
    a = p.parse_args()

    segs = find_segments(decode_mono(a.input), a.threshold, a.margin, a.min_gap)
    total = probe_duration(a.input)
    kept = sum((b - s) / (1.0 if l else a.silent_speed) for s, b, l in segs if l or a.silent_speed)
    print(f"{total:.1f}s -> {kept:.1f}s ({100 * (1 - kept / total):.0f}% removed)")
    if a.report:
        json.dump({"input_s": total, "output_s": kept, "segments": segs}, open(a.report, "w"), indent=1)

    footage = a.mode == "footage"
    if footage and not has_video(a.input):
        sys.exit("footage mode needs a video input")
    graph = build_graph(segs, a.silent_speed, with_video=footage)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(graph)
    try:
        if footage:
            run_ffmpeg(["-i", a.input, "-filter_complex_script", f.name, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", a.output])
        elif a.bg:
            tmp_audio = a.output + ".narr.wav"
            run_ffmpeg(["-i", a.input, "-filter_complex_script", f.name, "-map", "[a]", tmp_audio])
            dur = probe_duration(tmp_audio)
            fc = "[1:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[v]"
            amap = "0:a"
            if a.bg_volume > 0:
                fc += f";[1:a]volume={a.bg_volume}[bg];[0:a][bg]amix=inputs=2:duration=first:normalize=0[am]"
                amap = "[am]"
            run_ffmpeg(["-i", tmp_audio, "-stream_loop", "-1", "-i", a.bg, "-filter_complex", fc,
                        "-map", "[v]", "-map", amap, "-t", f"{dur:.3f}", "-c:v", "libx264",
                        "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-shortest", a.output])
            os.remove(tmp_audio)
        else:
            run_ffmpeg(["-i", a.input, "-filter_complex_script", f.name, "-map", "[a]", a.output])
    finally:
        os.unlink(f.name)
    print("wrote", a.output)


if __name__ == "__main__":
    main()
