#!/usr/bin/env python3
"""Cut a clip into a vertical 1080x1920 Short from a JSON edit plan.

The plan lists source segments (speed; "zoom" punch-in, or "push": [z0, z1] for a
slow zoom; "focus": [x, y] 0-1 to aim it), dialogue
captions in *source* time, a persistent hook title, timed pop-up labels and an
optional freeze-frame end card. Caption *word* = key-word emphasis; pops may
use "freeze": [from, to] to stage cards inside the freeze, or "arrow": [x, y, angle] (canvas px)
for the red pointer + label; "sfx" places low hits. Caption/label times are remapped through the
cuts automatically (including repeated / out-of-order segments, e.g. a cold open),
so you only ever think in the original footage's timeline.

  python3 tools/shorts.py plan.json input.mp4 -o short.mp4

See edits/fridge.json for a worked example.
"""
import argparse, json, re, subprocess, tempfile, os, wave
import numpy as np

W, H, SQ, TOP = 1080, 1920, 1080, 420          # video window: 1080x1080 at y=420
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
# STYLE.md palette, as ASS &HBBGGRR&
RED, PALE, GOLD = "&H001B20E3&", "&H00A6EBF3&", "&H0043C4F5&"
SPEAKER_PALETTE = ["&H00FF7B2F&", "&H0043C4F5&", "&H00DFE68E&", "&H003D8AFF&"]   # blue, gold, teal, orange


def atempo(speed):
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0"); speed /= 2.0
    return ",".join(parts + [f"atempo={speed:.4f}"])


def timeline(segs):
    """Attach output start times; return (segments, edit duration)."""
    t = 0.0
    for s in segs:
        s["out"] = t
        t += (s["end"] - s["start"]) / s.get("speed", 1.0)
    return segs, t


def place(segs, a, b):
    """Source span [a, b] -> output spans, one per segment that shows it.
    Works for cuts, speed changes, and segments that repeat or play out of order."""
    out = []
    for s in segs:
        lo, hi = max(a, s["start"]), min(b, s["end"])
        if hi - lo > 0.05:
            sp = s.get("speed", 1.0)
            out.append((s["out"] + (lo - s["start"]) / sp, s["out"] + (hi - s["start"]) / sp))
    return out


def arrow(tx, ty, angle=225, length=230):
    """ASS drawing of the house red arrow with its tip at canvas (tx, ty).
    angle sets where it comes from: 225 = upper left, 315 = upper right."""
    pts = [(-length, -11), (-52, -11), (-52, -34), (0, 0), (-52, 34), (-52, 11), (-length, 11)]
    a = np.radians(angle - 180)
    rot = [(tx + x * np.cos(a) - y * np.sin(a), ty + x * np.sin(a) + y * np.cos(a)) for x, y in pts]
    mx, my = min(x for x, _ in rot), min(y for _, y in rot)
    path = "m " + " l ".join(f"{x - mx:.0f} {y - my:.0f}" for x, y in rot)
    tail = (tx - length * np.cos(a) * 1.08, ty - length * np.sin(a) * 1.08)
    return f"{{\\an7\\pos({mx:.0f},{my:.0f})\\p1\\bord2\\shad0\\c{RED}\\3c&H000000&}}{path}", tail


def hit_track(times, dur, path, sr=48000):
    """Write a mono track with a short low 'impact' at each time (output seconds)."""
    x = np.zeros(int((dur + 1) * sr), dtype=np.float32)
    t = np.arange(int(1.2 * sr)) / sr
    f = 38 + 50 * np.exp(-t * 9)                                  # pitch drops 88 -> 38 Hz
    hit = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 3.2)
    hit[: int(0.004 * sr)] *= np.linspace(0, 1, int(0.004 * sr))
    for at in times:
        i = int(at * sr)
        x[i:i + len(hit)] += hit[: len(x) - i]
    pcm = (np.clip(x * 0.9, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def sfx_times(plan, segs, total):
    """sfx entries: {"seg": i, "src": t} (only in segment i) or {"freeze": offset}."""
    out, fz = [], total - plan.get("freeze", 0)
    for e in plan.get("sfx", []):
        if "freeze" in e:
            out.append(fz + e["freeze"])
        else:
            s = segs[e["seg"]]
            out.append(s["out"] + (e["src"] - s["start"]) / s.get("speed", 1.0))
    return out


def ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def build_ass(plan, segs, total):
    ev = []
    title = plan["title"].replace("*", f"{{\\c{RED}}}", 1).replace("*", "{\\c&HFFFFFF&}", 1)
    speakers = {}
    ev.append(f"Dialogue: 0,{ts(0)},{ts(total)},Title,,0,0,0,,{title}")
    for c in plan.get("captions", []):
        sp = c.get("speaker", "")
        col = speakers.setdefault(sp, SPEAKER_PALETTE[len(speakers) % len(SPEAKER_PALETTE)])
        size = "\\fs84" if c.get("emphasis") else ""
        text = re.sub(r"\*(.+?)\*", lambda m: f"{{\\c{RED}\\fscx118\\fscy118}}{m.group(1)}{{\\c{col}\\fscx100\\fscy100}}", c["text"])
        for a, b in place(segs, c["start"], c["end"]):
            if b - a >= 0.15:
                ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\c{col}{size}}}{text}")
    for p in plan.get("pops", []):
        fz = total - plan.get("freeze", 0)
        if "start" in p:
            spans = place(segs, p["start"], p["end"])
        else:
            f0, f1 = p.get("freeze", [0, plan.get("freeze", 0)])
            spans = [(fz + f0, fz + f1)]
        big = f"\\an5\\pos({W // 2},{TOP + SQ // 2})\\fs104\\c{RED}\\3c&H000000&\\bord7\\blur1" if p.get("big") else ""
        if "arrow" in p:
            shape, (lx, ly) = arrow(*p["arrow"])
            for a, b in spans:
                ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Pop,,0,0,0,,{{\\fad(80,0)}}{shape}")
                ev.append(f"Dialogue: 3,{ts(a)},{ts(b)},Pop,,0,0,0,,{{\\an2\\pos({lx:.0f},{ly - 6:.0f})\\fad(80,0)}}{p['text']}")
            continue
        for a, b in spans:
            ev.append(f"Dialogue: 2,{ts(a)},{ts(b)},Pop,,0,0,0,,{{{big}\\fad(120,0)\\t(0,180,\\fscx112\\fscy112)\\t(180,320,\\fscx100\\fscy100)}}{p['text']}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Special Elite,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,3,4,8,50,50,140,1
Style: Cap,Montserrat,72,&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,1,0,0,0,100,100,-1,0,1,3,3,8,70,70,{TOP + SQ + 50},1
Style: Pop,Special Elite,66,{PALE},{PALE},&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,6,4,8,60,60,{TOP + 60},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return head + "\n".join(ev) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    segs, edit_dur = timeline(plan["segments"])
    freeze = plan.get("freeze", 0)
    total = edit_dur + freeze

    fc = []
    for i, s in enumerate(segs):
        sp = s.get("speed", 1.0)
        z0, z1 = s.get("push", [s.get("zoom", 1.0)] * 2)
        fx, fy = s.get("focus", [0.5, 0.5])
        nfr = max(1, round((s["end"] - s["start"]) / sp * 30))
        z = f"{z0}+({z1}-{z0})*on/{nfr}"
        fc.append(f"[0:v]trim={s['start']}:{s['end']},setpts=(PTS-STARTPTS)/{sp},fps=30,"
                  f"scale={SQ * 2}:{SQ * 2}:flags=lanczos,"
                  f"zoompan=z='{z}':d=1:s={SQ}x{SQ}:fps=30:"
                  f"x='max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))':y='max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))',setsar=1[v{i}]")
        fc.append(f"[0:a]atrim={s['start']}:{s['end']},asetpts=PTS-STARTPTS"
                  + ("" if sp == 1.0 else "," + atempo(sp)) + f",afade=t=in:d=0.02[a{i}]")
    n = len(segs)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append(f"[cv]tpad=stop_mode=clone:stop_duration={freeze},split[fg][bgsrc]")
    fc.append(f"[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,eq=brightness=-0.22:saturation=0.8[bg]")
    with tempfile.NamedTemporaryFile("w", suffix=".ass", delete=False) as f:
        f.write(build_ass(plan, segs, total))
    fc.append(f"[bg][fg]overlay=0:{TOP},subtitles={f.name}:fontsdir={FONTS}[v]")
    hits = sfx_times(plan, segs, total)
    extra = []
    if hits:
        hit_wav = f.name + ".hits.wav"
        hit_track(hits, total, hit_wav)
        extra = ["-i", hit_wav]
        fc.append(f"[ca]apad=pad_dur={freeze}[cp];[1:a]volume={plan.get('sfx_volume', 0.5)}[hx];"
                  "[cp][hx]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        fc.append(f"[ca]apad=pad_dur={freeze},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    try:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.input] + extra + ["-filter_complex", ";".join(fc),
                        "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", a.output], check=True)
    finally:
        os.unlink(f.name)
        if hits:
            os.unlink(hit_wav)
    print(f"wrote {a.output}  ({total:.1f}s)")


if __name__ == "__main__":
    main()
