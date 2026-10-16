#!/usr/bin/env python3
"""Cut a clip into a vertical 1080x1920 Short from a JSON edit plan.

The plan lists source segments (speed; "zoom" punch-in, or "push": [z0, z1] for a
slow zoom; "focus": [x, y] 0-1 to aim it), dialogue
captions in *source* time, a persistent hook title, timed pop-up labels and an
optional freeze-frame end card. Caption/label times are remapped through the
cuts automatically (including repeated / out-of-order segments, e.g. a cold open),
so you only ever think in the original footage's timeline.

  python3 tools/shorts.py plan.json input.mp4 -o short.mp4

See edits/fridge.json for a worked example.
"""
import argparse, json, subprocess, tempfile, os

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
        for a, b in place(segs, c["start"], c["end"]):
            if b - a >= 0.15:
                ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\c{col}{size}}}{c['text']}")
    for p in plan.get("pops", []):
        spans = place(segs, p["start"], p["end"]) if "start" in p else [(total - plan.get("freeze", 0), total)]
        big = f"\\an5\\pos({W // 2},{TOP + SQ // 2})\\fs104\\c{RED}\\3c&H000000&\\bord7\\blur1" if p.get("big") else ""
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
    fc.append(f"[ca]apad=pad_dur={freeze},loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    try:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.input, "-filter_complex", ";".join(fc),
                        "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", a.output], check=True)
    finally:
        os.unlink(f.name)
    print(f"wrote {a.output}  ({total:.1f}s)")


if __name__ == "__main__":
    main()
