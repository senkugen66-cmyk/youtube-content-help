#!/usr/bin/env python3
"""Builds a fully fictional, SFW example episode that follows PLAYBOOK.md.

Pipeline: Piper TTS (stand-in for your voice) -> raw take with dead air ->
tools/jumpcut.py -> procedural dashcam visuals timed to the tightened audio
-> ducked music bed -> mp4.

  pip install piper-tts pillow numpy ; apt install ffmpeg
  python3 examples/build_demo.py --voice path/to/en_US-ryan-high.onnx --out demo.mp4
"""
import argparse, json, math, random, subprocess, sys, wave, os, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1280, 720, 30
HOR, F, CAMH = 330, 700.0, 1.3

# (beat, [sentences]) -- the narration script, structured like the playbook.
SCRIPT = [
    ("hook", ["At two fourteen in the morning, a taxi dashcam recorded forty seconds of an empty road.",
              "Police almost deleted it.",
              "Then a detective noticed the one thing that should not be there."]),
    ("context", ["This is Mill Road, a quiet industrial strip.",
                 "That night, a hardware store three blocks away was emptied.",
                 "No cameras inside. No witnesses. No leads."]),
    ("footage", ["Watch the right side of the road.",
                 "Streetlights. Parked cars. Nothing unusual.",
                 "Now look at the van by the corner.",
                 "Its headlights are off."]),
    ("rehook", ["But here is what the police did not know yet.",
                "That van had been stolen three days earlier."]),
    ("reveal", ["Freeze the frame at two fourteen thirty seven.",
                "The side door is open, and the roof rack carries a bright yellow strap.",
                "Only one supplier in town sold that strap."]),
    ("payoff", ["Detectives traced the strap to the supplier, the supplier to a buyer, and the buyer to an arrest.",
                "The case closed because of a ten cent piece of nylon.",
                "Next time: the traffic camera that was pointed the wrong way."]),
]
CAPTION_TAIL = 0.15


def synth(voice, text, path):
    subprocess.run([sys.executable, "-m", "piper", "-m", voice, "-f", str(path)],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768, w.getframerate()


def build_raw_take(voice, tmp):
    """Concatenate sentences with sloppy pauses + room noise, like a real take."""
    rng = random.Random(7)
    chunks, sr, t = [], None, 0.0
    sents = []  # (beat, text, raw_start, raw_end)
    for beat, lines in SCRIPT:
        for k, text in enumerate(lines):
            a, sr = synth(voice, text, tmp / "s.wav")
            gap = np.zeros(int(sr * (rng.uniform(0.9, 1.6) if k == 0 else rng.uniform(0.6, 1.3))), dtype=np.float32)
            chunks += [gap, a]
            t0 = t + len(gap) / sr
            t = t0 + len(a) / sr
            sents.append((beat, text, t0, t))
    chunks.append(np.zeros(int(sr * 1.0), dtype=np.float32))
    audio = np.concatenate(chunks)
    audio += np.random.default_rng(1).normal(0, 0.0015, audio.shape).astype(np.float32)  # room tone
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(tmp / "raw.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    return sents


def mapper(report):
    kept, out = [], 0.0
    for a, b, loud in report["segments"]:
        if loud:
            kept.append((a, b, out)); out += b - a

    def f(t):
        for a, b, o in kept:
            if t <= b:
                return o + max(0.0, t - a)
        return out
    return f


# ---------------------------------------------------------------- visuals
def font(sz, bold=True, mono=False):
    n = "DejaVuSansMono-Bold" if mono else ("DejaVuSans-Bold" if bold else "DejaVuSans")
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{n}.ttf", sz)

F_CAP, F_TS, F_SM, F_BIG = font(36), font(26, mono=True), font(20), font(54)
rng0 = random.Random(3)
BUILD = [(i, rng0.choice([-1, 1]), rng0.uniform(9, 14), rng0.uniform(5, 13), rng0.uniform(14, 26),
          [(rng0.random(), rng0.random()) for _ in range(14)]) for i in range(60)]
POLES = [(i, s) for i in range(40) for s in (-1, 1)]
CARS = [(rng0.uniform(20, 1100), -4.6, rng0.choice([(60, 20, 20), (30, 45, 70), (55, 55, 58), (25, 60, 40)])) for _ in range(22)]
NOISE = np.random.default_rng(5).integers(-14, 14, (H, W, 1), dtype=np.int16)
yy, xx = np.mgrid[0:H, 0:W]
VIGN = np.clip(1.15 - (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .7)) ** 2), 0.25, 1)[..., None]
GLOW = np.clip(1 - np.hypot((xx - W / 2) / 520, (yy - 640) / 330), 0, 1)[..., None] * 38


def P(X, Y, z):
    return (W / 2 + X * F / z, HOR + (CAMH - Y) * F / z)


def quad(d, pts, fill):
    d.polygon([P(*p) for p in pts], fill=fill)


def speed_at(t, beats):
    b = beat_at(t, beats)
    return {"context": 40.0, "rehook": 3.5}.get(b, 11.0)


def beat_at(t, beats):
    cur = beats[0][0]
    for name, t0 in beats:
        if t >= t0:
            cur = name
    return cur


def road_scene(s, vanZ, t, show_van_lights=False):
    img = Image.new("RGB", (W, H), (7, 9, 16))
    d = ImageDraw.Draw(img)
    d.rectangle([0, HOR, W, H], fill=(24, 26, 31))
    d.polygon([(W / 2 - 30, HOR), (W / 2 + 30, HOR), (W + 400, H), (-400, H)], fill=(31, 33, 38))  # road
    for n in range(-2, 60):                                           # centre dashes
        z1, z2 = n * 6 - (s % 6) + 3, n * 6 - (s % 6) + 6
        if z2 > 2.2:
            quad(d, [(-.12, 0, max(z1, 2.2)), (.12, 0, max(z1, 2.2)), (.12, 0, z2), (-.12, 0, z2)], (190, 190, 175))
    for side in (-1, 1):                                               # kerbs
        quad(d, [(side * 4.0, 0, 2.2), (side * 4.25, 0, 2.2), (side * 4.25, 0, 190), (side * 4.0, 0, 190)], (70, 70, 74))
    items = []
    for i, side, gap, hgt, ln, wins in BUILD:                          # buildings
        zf = i * 30 - (s % 1800) - 20
        zf = zf + 1800 if zf < -ln else zf
        if zf < 190:
            items.append((zf + ln, "b", (side, gap, hgt, ln, zf, wins)))
    for i, side in POLES:                                              # streetlights
        z = i * 25 - (s % 1000)
        z = z + 1000 if z < 2.3 else z
        if z < 190:
            items.append((z, "p", (side, z)))
    for cz, cx, col in CARS:                                           # parked cars
        z = cz - (s % 1100)
        z = z + 1100 if z < 2.3 else z
        if z < 140:
            items.append((z, "c", (cx, z, col)))
    zv = vanZ - s
    if zv > 2.4:
        items.append((zv, "v", (4.4, zv)))
    for _, kind, a in sorted(items, key=lambda x: -x[0]):
        if kind == "b":
            side, gap, hgt, ln, zf, wins = a
            zf_, zb = max(zf, 2.4), zf + ln
            if zb <= 2.4:
                continue
            xin = side * gap
            quad(d, [(xin, 0, zf_), (xin, 0, zb), (xin, hgt, zb), (xin, hgt, zf_)], (14, 16, 22))
            quad(d, [(xin, 0, zf_), (xin + side * 8, 0, zf_), (xin + side * 8, hgt, zf_), (xin, hgt, zf_)], (11, 12, 18))
            for u, v in wins:
                if v > .55 and u > .1:
                    zz = zf + u * ln
                    if zz > 2.6 and (int(u * 1000) % 3):
                        quad(d, [(xin, hgt * v, zz), (xin, hgt * v, zz + 1.1), (xin, hgt * v - .8, zz + 1.1), (xin, hgt * v - .8, zz)], (120, 105, 60))
        elif kind == "p":
            side, z = a
            x0, y0 = P(side * 5.8, 0, z); x1, y1 = P(side * 5.8, 6.2, z)
            d.line([x0, y0, x1, y1], fill=(40, 42, 48), width=max(1, int(120 / z)))
            for r, c in ((26, (40, 36, 22)), (14, (110, 95, 50)), (6, (235, 215, 150))):
                rr = r * 12 / max(z, 6) * 2.2
                d.ellipse([x1 - rr, y1 - rr, x1 + rr, y1 + rr], fill=c)
            quad(d, [(side * 5.8 - 1.6, 0, z), (side * 5.8 + 1.6, 0, z), (side * 5.8 + 1.6, 0, z + 5), (side * 5.8 - 1.6, 0, z + 5)], (44, 42, 36))
        elif kind == "c":
            cx, z, col = a
            quad(d, [(cx - .9, .25, z), (cx + .9, .25, z), (cx + .9, 1.35, z), (cx - .9, 1.35, z)], col)
            quad(d, [(cx - .7, 1.35, z), (cx + .7, 1.35, z), (cx + .6, 1.7, z), (cx - .6, 1.7, z)], tuple(int(c * .7) for c in col))
        else:
            vx, z = a
            quad(d, [(vx - 1.05, .3, z), (vx + 1.05, .3, z), (vx + 1.05, 2.5, z), (vx - 1.05, 2.5, z)], (176, 178, 182))
            quad(d, [(vx - .9, 1.5, z), (vx + .9, 1.5, z), (vx + .9, 2.3, z), (vx - .9, 2.3, z)], (20, 24, 30))
            for sx in (-.75, .75):
                c = (255, 244, 200) if show_van_lights else (50, 52, 58)
                quad(d, [(vx + sx - .2, .7, z), (vx + sx + .2, .7, z), (vx + sx + .2, 1.05, z), (vx + sx - .2, 1.05, z)], c)
            quad(d, [(vx - 1.1, 2.5, z), (vx + 1.1, 2.5, z), (vx + 1.1, 2.62, z), (vx - 1.1, 2.62, z)], (60, 60, 64))
    return img


def post(img, cam_shake=0.0):
    img = img.filter(ImageFilter.GaussianBlur(0.9))
    a = np.asarray(img, dtype=np.int16) + GLOW.astype(np.int16)
    a = a * VIGN + np.roll(NOISE, random.randint(0, H - 1), axis=0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def van_closeup(t, k):
    """Enhanced zoom on the van's side. k in 0..1 = zoom progress."""
    img = Image.new("RGB", (W, H), (12, 13, 18))
    d = ImageDraw.Draw(img)
    sc = 1.0 + .35 * k
    cx, cy = W * .5, H * .56

    def R(x0, y0, x1, y1):
        return [cx + (x0 - 640) * sc, cy + (y0 - 400) * sc, cx + (x1 - 640) * sc, cy + (y1 - 400) * sc]
    d.rectangle([0, int(cy + 190 * sc), W, H], fill=(24, 26, 31))
    d.rounded_rectangle(R(190, 290, 1090, 560), 36, fill=(176, 178, 182))            # body
    d.rounded_rectangle(R(900, 330, 1060, 430), 14, fill=(30, 36, 46))                # cab window
    d.rectangle(R(430, 330, 760, 540), fill=(8, 8, 10))                               # open side door
    d.rectangle(R(430, 330, 760, 346), fill=(60, 60, 64))
    for xr in (260, 560, 860):                                                        # roof rack
        d.rectangle(R(xr, 262, xr + 14, 292), fill=(70, 70, 74))
    d.rectangle(R(230, 262, 1050, 276), fill=(70, 70, 74))
    for x in range(250, 1040, 60):
        d.line(R(x, 262, x, 276), fill=(40, 40, 44), width=3)
    d.polygon([(cx + (560 - 640) * sc, cy + (276 - 400) * sc), (cx + (590 - 640) * sc, cy + (276 - 400) * sc),
               (cx + (606 - 640) * sc, cy + (380 - 400) * sc), (cx + (584 - 640) * sc, cy + (392 - 400) * sc),
               (cx + (572 - 640) * sc, cy + (360 - 400) * sc)], fill=(250, 205, 30))   # yellow strap
    for wx in (330, 960):
        r = 62 * sc
        wcx, wcy = cx + (wx - 640) * sc, cy + (570 - 400) * sc
        d.ellipse([wcx - r, wcy - r, wcx + r, wcy + r], fill=(10, 10, 12))
    plate = R(1010, 500, 1080, 530)
    d.rectangle(plate, fill=(90, 90, 90))                                              # blurred plate
    # pulsing red circle on the strap
    pr = (62 + 6 * math.sin(t * 6)) * sc
    px, py = cx + (584 - 640) * sc, cy + (330 - 400) * sc
    d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=(235, 40, 40), width=6)
    return img


def chain_card(t_in, nxt):
    img = Image.new("RGB", (W, H), (10, 12, 18))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line([x, 0, x, H], fill=(16, 19, 27))
    for y in range(0, H, 60):
        d.line([0, y, W, y], fill=(16, 19, 27))
    labels = ["YELLOW STRAP", "SUPPLIER", "BUYER", "ARREST"]
    colors = [(250, 205, 30), (150, 170, 200), (150, 170, 200), (235, 70, 70)]
    bw, gap = 250, 50
    x0 = (W - (4 * bw + 3 * gap)) / 2
    shown = min(4, int(t_in / 2.2) + 1) if t_in >= 0 else 0
    for i in range(shown):
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, 250, x + bw, 350], 14, outline=colors[i], width=4, fill=(18, 21, 30))
        tw = d.textlength(labels[i], font=F_SM)
        d.text((x + (bw - tw) / 2, 288), labels[i], font=F_SM, fill=colors[i])
        if i < 3 and i + 1 < shown:
            d.polygon([(x + bw + 8, 300), (x + bw + gap - 10, 300 - 0), (x + bw + gap - 10, 292), (x + bw + gap - 2, 300),
                       (x + bw + gap - 10, 308), (x + bw + gap - 10, 300)], fill=(200, 200, 200))
    if t_in > nxt:
        tw = d.textlength("NEXT: THE CAMERA POINTED THE WRONG WAY", font=F_CAP)
        d.text(((W - tw) / 2, 470), "NEXT: THE CAMERA POINTED THE WRONG WAY", font=F_CAP, fill=(230, 230, 230))
    return img


def overlay(img, t, ts_clock, speed_kmh, label=None, caption=None, frozen=False, fast=False):
    d = ImageDraw.Draw(img, "RGBA")
    h, m, sec = ts_clock
    d.text((28, 22), f"2024-03-09  {h:02d}:{m:02d}:{sec:02d}", font=F_TS, fill=(255, 255, 255, 235))
    d.text((28, 56), "MILL RD  CAM 1  %3d km/h" % speed_kmh, font=F_SM, fill=(255, 255, 255, 200))
    if (int(t * 2) % 2) == 0 and not frozen:
        d.ellipse([W - 150, 28, W - 130, 48], fill=(230, 30, 30, 255))
    d.text((W - 118, 24), "REC" if not frozen else "PAUSE", font=F_SM, fill=(255, 255, 255, 235))
    d.rounded_rectangle([W - 300, 66, W - 24, 96], 8, fill=(0, 0, 0, 150))
    d.text((W - 288, 71), "FICTIONAL RE-CREATION", font=F_SM, fill=(255, 220, 120, 255))
    if fast:
        d.text((28, 90), ">> 4x", font=F_BIG, fill=(255, 220, 120, 255))
    if label:
        lw = d.textlength(label, font=F_SM)
        d.rounded_rectangle([W / 2 - lw / 2 - 16, 150, W / 2 + lw / 2 + 16, 190], 8, fill=(0, 0, 0, 170), outline=(235, 40, 40, 255), width=3)
        d.text((W / 2 - lw / 2, 158), label, font=F_SM, fill=(255, 255, 255, 255))
    if caption:
        lines = caption
        tw = max(d.textlength(l, font=F_CAP) for l in lines)
        y0 = H - 60 - 52 * len(lines)
        d.rounded_rectangle([W / 2 - tw / 2 - 22, y0 - 10, W / 2 + tw / 2 + 22, H - 40], 14, fill=(0, 0, 0, 170))
        for i, l in enumerate(lines):
            w = d.textlength(l, font=F_CAP)
            d.text((W / 2 - w / 2, y0 + 52 * i), l, font=F_CAP, fill=(255, 255, 255, 255))
    return img


def caption_chunks(sents, f):
    """Split each sentence into balanced <=6-word chunks with time proportional to characters."""
    out = []
    for _, text, a, b in sents:
        a, b = f(a), f(b)
        words = text.replace(" ten cent", " 10-cent").split()
        n = max(1, math.ceil(len(words) / 6))
        per = math.ceil(len(words) / n)
        parts = [words[i:i + per] for i in range(0, len(words), per)]
        lens = [sum(len(w) + 1 for w in p) for p in parts]
        t = a
        for p, ln in zip(parts, lens):
            e = t + (b - a) * ln / sum(lens)
            out.append((t, e, " ".join(p)))
            t = e
    return out


def music(dur, path, sr=44100):
    t = np.arange(int(dur * sr)) / sr
    x = (np.sin(2 * np.pi * 55 * t) * .5 + np.sin(2 * np.pi * 82.4 * t + .4) * .3 + np.sin(2 * np.pi * 110.5 * t) * .15)
    x *= .6 + .4 * np.sin(2 * np.pi * .12 * t)
    x += (np.sin(2 * np.pi * 1.0 * t) > .99) * np.sin(2 * np.pi * 70 * t) * .3   # slow pulse
    x *= np.minimum(1, t / 2) * np.minimum(1, (dur - t) / 2)
    pcm = (x / np.abs(x).max() * 0.6 * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True)
    ap.add_argument("--out", default="demo.mp4")
    ap.add_argument("--stills", help="also save a PNG every 5s into this dir (for checking looks)")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp())
    sents = build_raw_take(a.voice, tmp)
    subprocess.run([sys.executable, str(ROOT / "tools/jumpcut.py"), str(tmp / "raw.wav"), "-o", str(tmp / "tight.wav"),
                    "--report", str(tmp / "r.json")], check=True)
    rep = json.load(open(tmp / "r.json"))
    f = mapper(rep)
    total = rep["output_s"] + 1.0
    beats, seen = [], set()
    for b, _, t0, _ in sents:
        if b not in seen:
            seen.add(b); beats.append((b, max(0.0, f(t0) - 0.15)))
    beats[0] = (beats[0][0], 0.0)
    bstart = dict(beats)
    caps = caption_chunks(sents, f)
    music(total + 1, tmp / "music.wav")

    # camera distance travelled, integrated once so scenes are continuous
    N = int(total * FPS)
    S = np.zeros(N + 1)
    for i in range(N):
        S[i + 1] = S[i] + speed_at(i / FPS, beats) / FPS
    t_freeze = bstart["reveal"]
    vanZ = S[int(bstart["rehook"] * FPS)] + 7.5
    next_t = f(next(a for _, tx, a, _ in sents if tx.startswith("Next time")))

    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", str(tmp / "tight.wav"), "-i", str(tmp / "music.wav"),
                           "-filter_complex",
                           "[1:a]apad=pad_dur=3,asplit[n1][n2];[2:a]volume=0.55[m];"
                           "[m][n1]sidechaincompress=threshold=0.015:ratio=9:attack=15:release=500[duck];"
                           "[n2][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[a]",
                           "-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", a.out], stdin=subprocess.PIPE)
    for i in range(N):
        t = i / FPS
        beat = beat_at(t, beats)
        cap = next(((c[2]) for c in caps if c[0] <= t < c[1] + CAPTION_TAIL), None)
        cap = None if cap is None else [cap]
        clock = (2, 14, 9 + int(t * .55)) if beat != "reveal" else (2, 14, 37)
        label, frozen, fast = None, False, beat == "context"
        if beat in ("reveal",):
            k = (t - bstart["reveal"]) / max(0.1, bstart["payoff"] - bstart["reveal"])
            img = post(van_closeup(t, min(1, k)))
            label = "ENHANCED FRAME  02:14:37"
            frozen = True
        elif beat == "payoff":
            img = post(chain_card(t - bstart["payoff"], next_t - bstart["payoff"]))
            clock = (2, 14, 37); frozen = True
        else:
            s = S[i]
            zv = vanZ - s
            img = post(road_scene(s, vanZ, t))
            if beat in ("footage", "rehook") and zv < 140:
                d = ImageDraw.Draw(img)
                x, y = P(4.4, 1.5, max(zv, 3))
                r = 520 / max(zv, 3) + 14
                d.rectangle([x - r, y - r * .9, x + r, y + r * .9], outline=(235, 40, 40), width=3)
                label = "VAN - LIGHTS OFF" if beat == "footage" else "REPORTED STOLEN - 3 DAYS EARLIER"
        sp = 0 if frozen else (40 if beat == "context" else int(speed_at(t, beats) * 3.6))
        img = overlay(img, t, clock, sp, label, cap, frozen, fast)
        if a.stills and i % (FPS * 5) == FPS:
            os.makedirs(a.stills, exist_ok=True); img.save(f"{a.stills}/t{int(t):03d}_{beat}.png")
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    print("wrote", a.out, f"{total:.1f}s", "| raw take", f"{rep['input_s']:.1f}s -> tight {rep['output_s']:.1f}s")


if __name__ == "__main__":
    main()
