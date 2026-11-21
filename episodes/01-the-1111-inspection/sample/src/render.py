import numpy as np, subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from timeline import *

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = int(W * 1.2), int(H * 1.2)
rng = np.random.default_rng(1111)

F = lambda p, s: ImageFont.truetype(p, s)
FONT_SUB = F("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 40)
FONT_NARR = F("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", 66)
FONT_TITLE = F("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 124)
FONT_MONO = F("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf", 30)
FONT_MONO_B = F("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf", 34)
FONT_CORP = F("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 46)
FONT_PM = F("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 60)

RED = (255, 38, 32)


def ease(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)


def lerp(a, b, f):
    return a + (b - a) * f


def cam(plate, z=1.0, cx=0.5, cy=0.5, sx=0.0, sy=0.0):
    pw, ph = plate.size
    cw, ch = pw / z, ph / z
    x0 = min(max(cx * pw - cw / 2 + sx, 0), pw - cw)
    y0 = min(max(cy * ph - ch / 2 + sy, 0), ph - ch)
    return plate.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def glow(layer, radius, gain=1.0):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    if gain != 1.0:
        g = Image.fromarray(np.clip(np.asarray(g, np.float32) * gain, 0, 255).astype(np.uint8))
    return g


def add(a, b):
    return ImageChops.add(a, b)


def radial(w, h, cx, cy, r, color, power=2.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    m = np.clip(1 - d, 0, 1) ** power
    return m[..., None] * np.array(color, np.float32)[None, None, :]


def shake(t, t0, amp, decay=9, freq=31):
    if t < t0:
        return 0, 0
    d = t - t0
    a = amp * math.exp(-d * decay)
    return a * math.sin(d * freq * 6.28), a * math.cos(d * freq * 4.9)


# ---------------------------------------------------------------- 7-seg digits
SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
        "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg_polys(x, y, w, h, th):
    g = th * 0.18
    hh = h / 2
    def hor(x0, x1, yy):
        return [(x0, yy), (x0 + th / 2, yy - th / 2), (x1 - th / 2, yy - th / 2), (x1, yy), (x1 - th / 2, yy + th / 2), (x0 + th / 2, yy + th / 2)]
    def ver(xx, y0, y1):
        return [(xx, y0), (xx + th / 2, y0 + th / 2), (xx + th / 2, y1 - th / 2), (xx, y1), (xx - th / 2, y1 - th / 2), (xx - th / 2, y0 + th / 2)]
    L, R, T, M, B = x + th / 2, x + w - th / 2, y + th / 2, y + hh, y + h - th / 2
    p = {"a": hor(L + g, R - g, T), "g": hor(L + g, R - g, M), "d": hor(L + g, R - g, B),
         "f": ver(L, T + g, M - g), "b": ver(R, T + g, M - g), "e": ver(L, M + g, B - g), "c": ver(R, M + g, B - g)}
    sk = 0.07
    cy = y + hh
    return {k: [(px - (py - cy) * sk, py) for px, py in v] for k, v in p.items()}


def draw_clock(d, text, x, y, dw, dh, th, on=RED, off=(13, 2, 2), colon=True):
    cx = x
    for ch in text:
        if ch == ":":
            if colon:
                r = th * 0.55
                for yy in (y + dh * 0.3, y + dh * 0.7):
                    d.ellipse([cx + th * 0.3 - r, yy - r, cx + th * 0.3 + r, yy + r], fill=on)
            cx += th * 1.6
            continue
        polys = seg_polys(cx, y, dw, dh, th)
        for k, poly in polys.items():
            d.polygon(poly, fill=on if k in SEGS[ch] else off)
        cx += dw + th * 0.9
    return cx


# ---------------------------------------------------------------- blocky figure (R6-style)
def figure(d, cx, feet, height, body, legs, skin, rim=None, rim_side=-1, head_tilt=0, child=False):
    u = height / (5.4 if not child else 4.6)
    head_w, head_h = u * 1.25, u * 1.1
    torso_w, torso_h = u * 2.0, u * 2.0
    leg_h = u * 2.0 if not child else u * 1.3
    top_leg = feet - leg_h
    top_torso = top_leg - torso_h
    # legs
    d.rectangle([cx - torso_w / 2, top_leg, cx - 0.02 * u, feet], fill=legs)
    d.rectangle([cx + 0.02 * u, top_leg, cx + torso_w / 2, feet], fill=legs)
    # torso + arms
    d.rectangle([cx - torso_w / 2, top_torso, cx + torso_w / 2, top_leg + 2], fill=body)
    d.rectangle([cx - torso_w / 2 - u, top_torso, cx - torso_w / 2 - 0.04 * u, top_leg], fill=body)
    d.rectangle([cx + torso_w / 2 + 0.04 * u, top_torso, cx + torso_w / 2 + u, top_leg], fill=body)
    # head
    hx = cx + head_tilt * u
    d.rounded_rectangle([hx - head_w / 2, top_torso - head_h - 0.04 * u, hx + head_w / 2, top_torso - 0.04 * u],
                        radius=u * 0.28, fill=skin)
    if rim:
        rw = max(2, u * 0.08)
        if rim_side < 0:
            xs = [cx - torso_w / 2 - u, hx - head_w / 2]
        else:
            xs = [cx + torso_w / 2 + u - rw, hx + head_w / 2 - rw]
        d.rectangle([xs[0], top_torso, xs[0] + rw, top_leg], fill=rim)
        d.rectangle([xs[1], top_torso - head_h + u * 0.25, xs[1] + rw, top_torso - u * 0.2], fill=rim)
    return dict(left_hand=(cx - torso_w / 2 - u / 2, top_leg - u * 0.2), right_hand=(cx + torso_w / 2 + u / 2, top_leg - u * 0.2), u=u)


# ================================================================= PLATES
def plate_clock_room():
    img = Image.new("RGB", (PW, PH), (4, 5, 9))
    d = ImageDraw.Draw(img)
    # nightstand top edge
    d.rectangle([0, 900, PW, PH], fill=(9, 9, 13))
    d.rectangle([0, 896, PW, 902], fill=(22, 20, 24))
    # clock body
    d.rounded_rectangle([880, 610, 1520, 900], radius=26, fill=(13, 13, 16))
    d.rounded_rectangle([910, 640, 1490, 860], radius=14, fill=(6, 4, 5))
    return img


def clock_layer(size, text, x, y, dw, dh, th, colon=True, pm_xy=None, pm_size=None):
    lay = Image.new("RGB", size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    end = draw_clock(d, text, x, y, dw, dh, th, colon=colon)
    if pm_xy:
        f = F("/usr/share/fonts/opentype/inter/Inter-Bold.otf", pm_size)
        d.text((end + pm_size * 0.15, pm_xy[1]), "PM", font=f, fill=RED)
    return lay


def build_hallway():
    alb = Image.new("RGB", (PW, PH))
    d = ImageDraw.Draw(alb)
    bx0, bx1, by0, by1 = 772, 1532, 330, 1010
    d.polygon([(0, 0), (PW, 0), (bx1, by0), (bx0, by0)], fill=(70, 72, 80))           # ceiling
    d.polygon([(0, PH), (PW, PH), (bx1, by1), (bx0, by1)], fill=(92, 64, 44))          # floor
    d.polygon([(0, 0), (bx0, by0), (bx0, by1), (0, PH)], fill=(110, 112, 118))        # left wall
    d.polygon([(PW, 0), (bx1, by0), (bx1, by1), (PW, PH)], fill=(100, 102, 110))      # right wall
    d.rectangle([bx0, by0, bx1, by1], fill=(118, 118, 124))                           # end wall
    # floor boards
    for i in range(1, 14):
        f = i / 14
        x0 = lerp(0, PW, f); x1 = lerp(bx0, bx1, f)
        d.line([(x0, PH), (x1, by1)], fill=(80, 54, 38), width=3)
    # skirting
    d.line([(0, PH - 2), (bx0, by1)], fill=(140, 140, 146), width=6)
    d.line([(PW, PH - 2), (bx1, by1)], fill=(140, 140, 146), width=6)
    # front door on end wall
    dx0, dx1, dy0 = 1000, 1300, 560
    d.rectangle([dx0 - 14, dy0 - 14, dx1 + 14, by1], fill=(150, 150, 150))
    d.rectangle([dx0, dy0, dx1, by1], fill=(78, 46, 30))
    d.rectangle([dx0 + 24, dy0 + 270, dx1 - 24, by1 - 30], outline=(62, 36, 24), width=5)
    d.ellipse([dx1 - 46, 790, dx1 - 30, 806], fill=(170, 150, 100))
    # picture frames on right wall
    for f, hgt in [(0.25, 180), (0.6, 120)]:
        s = 1 - f * 0.67
        x = lerp(PW, bx1, f); yt = lerp(0, by0, f) + 260 * s
        d.polygon([(x - 30 * s, yt), (x - 230 * s, yt + 20 * s), (x - 230 * s, yt + 20 * s + hgt * s), (x - 30 * s, yt + hgt * s)], fill=(40, 36, 34))
    # side table + lamp on left wall
    f = 0.42; s = 1 - f * 0.67
    x = lerp(0, bx0, f) + 40 * s; fy = lerp(PH, by1, f)
    d.rectangle([x, fy - 330 * s, x + 260 * s, fy - 300 * s], fill=(60, 40, 28))
    d.rectangle([x + 20 * s, fy - 300 * s, x + 40 * s, fy], fill=(50, 34, 24))
    d.rectangle([x + 220 * s, fy - 300 * s, x + 240 * s, fy], fill=(50, 34, 24))
    lamp_x, lamp_y = x + 130 * s, fy - 470 * s
    d.rectangle([lamp_x - 12 * s, lamp_y + 60 * s, lamp_x + 12 * s, fy - 330 * s], fill=(40, 34, 30))
    # characters (albedo)
    figs = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    fd = ImageDraw.Draw(figs)
    # Alex by the door, back to camera
    figure(fd, 900, 1036, 640 * 0.6, (40, 52, 80), (30, 30, 38), (150, 120, 96))
    # Mara + June, closer
    m = figure(fd, 1640, 1210, 620, (96, 46, 52), (36, 34, 44), (150, 116, 92))
    j = figure(fd, 1440, 1200, 400, (150, 130, 60), (50, 50, 70), (160, 126, 100), child=True)
    # holding hands
    hx = sorted([j["right_hand"][0] - 10, m["left_hand"][0] + 10]); hy = sorted([j["right_hand"][1], m["left_hand"][1]])
    fd.polygon([(hx[0], j["right_hand"][1] - 8), (hx[1], m["left_hand"][1] - 8), (hx[1], m["left_hand"][1] + 8), (hx[0], j["right_hand"][1] + 8)], fill=(150, 116, 92))
    alb.paste(figs, (0, 0), figs)
    A = np.asarray(alb, np.float32) / 255

    fig_alpha = np.asarray(figs.getchannel("A"), np.float32)[..., None] / 255
    rims = Image.new("RGB", (PW, PH)); rd = ImageDraw.Draw(rims)
    blk = (0, 0, 0)
    figure(rd, 900, 1036, 640 * 0.6, blk, blk, blk, rim=(70, 100, 150), rim_side=1)
    figure(rd, 1640, 1210, 620, blk, blk, blk, rim=(90, 120, 175), rim_side=-1)
    figure(rd, 1440, 1200, 400, blk, blk, blk, rim=(90, 120, 175), rim_side=-1, child=True)
    amb = np.array([0.15, 0.17, 0.23], np.float32)
    lamp = radial(PW, PH, lamp_x, lamp_y, 900, (1.25, 0.78, 0.38), 1.6)
    window_light = radial(PW, PH, 1150, 700, 520, (0.25, 0.38, 0.6), 2.0)
    base = A * (amb + window_light)
    lampimg = A * lamp
    # emissive
    em = Image.new("RGB", (PW, PH))
    ed = ImageDraw.Draw(em)
    ed.polygon([(lamp_x - 70 * s, lamp_y + 60 * s), (lamp_x + 70 * s, lamp_y + 60 * s), (lamp_x + 45 * s, lamp_y - 40 * s), (lamp_x - 45 * s, lamp_y - 40 * s)], fill=(255, 196, 120))
    em = add(em, glow(em, 40, 1.6))
    win = Image.new("RGB", (PW, PH))
    wd = ImageDraw.Draw(win)
    wd.rectangle([1110, 600, 1190, 800], fill=(120, 160, 210))
    win = add(win, glow(win, 30, 1.2))
    base = base * 255 + np.asarray(win, np.float32) * (1 - fig_alpha) + np.asarray(rims, np.float32)
    return base, lampimg * 255 + np.asarray(em, np.float32)


def build_door():
    """front door, frontal; returns (plain, with_figure) float arrays + under-door feet layer"""
    img = Image.new("RGB", (PW, PH), (24, 26, 34))
    d = ImageDraw.Draw(img)
    # wall gradient
    A = np.asarray(img, np.float32)
    A *= np.linspace(0.75, 1.1, PW)[None, :, None]
    img = Image.fromarray(A.astype(np.uint8)); d = ImageDraw.Draw(img)
    d.rectangle([0, 1180, PW, PH], fill=(30, 20, 15))
    for i in range(0, PW, 140):
        d.line([(i, 1180), (i - 60, PH)], fill=(24, 16, 12), width=3)
    x0, x1, y0, y1 = 772, 1532, 70, 1176
    d.rectangle([x0 - 40, y0 - 40, x1 + 40, y1 + 4], fill=(48, 48, 54))  # frame
    d.rectangle([x0, y0, x1, y1], fill=(58, 34, 24))                      # door
    for (a, b, c, e) in [(x0 + 60, 820, x1 - 60, y1 - 70)]:
        d.rectangle([a, b, c, e], outline=(44, 26, 18), width=10)
        d.rectangle([a + 14, b + 14, c - 14, e - 14], outline=(70, 42, 30), width=3)
    # handle backplate + lever (static here)
    d.rounded_rectangle([1404, 610, 1444, 810], radius=12, fill=(70, 64, 56))
    d.rounded_rectangle([1300, 680, 1430, 708], radius=12, fill=(120, 110, 90))
    d.ellipse([1414, 760, 1434, 780], fill=(20, 18, 16))
    # light gap under door
    d.rectangle([x0 + 6, y1 - 4, x1 - 6, y1 + 3], fill=(130, 170, 230))
    # warm spill from lamp behind camera (left)
    A = np.asarray(img, np.float32)
    A = A * (0.55 + radial(PW, PH, 300, 900, 1600, (0.9, 0.55, 0.3), 1.2) / 1.0)
    plain = A.copy()

    def window(with_fig, alpha=1.0):
        wx0, wx1, wy0, wy1 = 1032, 1272, 190, 740
        win = Image.new("RGB", (wx1 - wx0, wy1 - wy0))
        wa = np.zeros((wy1 - wy0, wx1 - wx0, 3), np.float32)
        yy = np.linspace(0, 1, wy1 - wy0)[:, None, None]
        wa[:] = np.array([70, 105, 160]) * (1.2 - 0.5 * yy) + rng.normal(0, 8, wa.shape)
        win = Image.fromarray(np.clip(wa, 0, 255).astype(np.uint8))
        if with_fig:
            wd = ImageDraw.Draw(win)
            cx = 128
            wd.rounded_rectangle([cx - 62, 150, cx + 62, 285], radius=24, fill=(14, 16, 24))  # head
            wd.rectangle([cx - 150, 290, cx + 150, 600], fill=(16, 18, 26))                  # shoulders
            wd.rectangle([cx - 210, 300, cx - 150, 600], fill=(16, 18, 26))
            wd.rectangle([cx + 150, 300, cx + 210, 600], fill=(16, 18, 26))
        win = win.filter(ImageFilter.GaussianBlur(9))
        # frosted texture
        fa = np.asarray(win, np.float32) + rng.normal(0, 7, (wy1 - wy0, wx1 - wx0, 1))
        out = Image.new("RGB", (PW, PH))
        out.paste(Image.fromarray(np.clip(fa, 0, 255).astype(np.uint8)), (wx0, wy0))
        dd = ImageDraw.Draw(out)
        # mullions
        dd.rectangle([wx0 - 10, wy0 - 10, wx1 + 10, wy0], fill=(40, 24, 16))
        dd.rectangle([wx0 - 10, wy1, wx1 + 10, wy1 + 10], fill=(40, 24, 16))
        dd.rectangle([wx0 - 10, wy0, wx0, wy1], fill=(40, 24, 16))
        dd.rectangle([wx1, wy0, wx1 + 10, wy1], fill=(40, 24, 16))
        mask = Image.new("L", (PW, PH)); ImageDraw.Draw(mask).rectangle([wx0 - 10, wy0 - 10, wx1 + 10, wy1 + 10], fill=255)
        return np.asarray(out, np.float32), np.asarray(mask, np.float32)[..., None] / 255

    w0, m = window(False)
    w1, _ = window(True)
    glowl = Image.fromarray(np.clip(w0 * m, 0, 255).astype(np.uint8))
    gl = np.asarray(glow(glowl, 60, 0.9), np.float32)
    plain_img = plain * (1 - m) + w0 * m + gl * 0.6
    fig_img = plain * (1 - m) + w1 * m + gl * 0.5
    # feet shadows breaking the light gap
    feet = np.zeros_like(plain)
    for fx in (1080, 1220):
        feet[1170:1182, fx:fx + 90] = 1
    return plain_img, fig_img, feet


def build_handle_lever():
    lev = Image.new("RGBA", (1400, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(lev)
    d.rounded_rectangle([60, 90, 1100, 200], radius=55, fill=(150, 138, 112, 255))
    d.rounded_rectangle([60, 96, 1100, 130], radius=20, fill=(205, 192, 160, 255))   # highlight
    d.rounded_rectangle([60, 170, 1100, 200], radius=20, fill=(90, 80, 64, 255))     # shade
    d.ellipse([960, 40, 1260, 260], fill=(130, 118, 96, 255))
    d.ellipse([1000, 80, 1220, 220], fill=(170, 158, 130, 255))
    return lev  # pivot at (1110,150)


def build_handle_bg():
    img = Image.new("RGB", (W, H), (40, 24, 16))
    A = np.asarray(img, np.float32)
    A = A * (0.6 + radial(W, H, 400, 300, 1600, (0.7, 0.6, 0.6), 1.0)) + rng.normal(0, 3, (H, W, 1))
    # wood grain
    yy = np.arange(H)[:, None]
    A *= (1 + 0.06 * np.sin(yy / 9 + np.sin(np.arange(W)[None, :] / 80) * 3))[..., None]
    img = Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1250, 100, 1570, 1000], radius=60, fill=(84, 76, 64))
    d.rounded_rectangle([1262, 112, 1558, 988], radius=54, outline=(120, 110, 92), width=4)
    d.ellipse([1370, 780, 1450, 860], fill=(16, 14, 12))
    d.rectangle([1400, 810, 1420, 900], fill=(16, 14, 12))
    return img


def build_street():
    w, h = int(W * 1.5), H
    sky = np.zeros((h, w, 3), np.float32)
    yy = np.linspace(0, 1, h)[:, None, None]
    sky[:] = np.array([6, 8, 16]) * (1 - yy) + np.array([18, 22, 34]) * yy
    img = Image.fromarray(sky.astype(np.uint8))
    d = ImageDraw.Draw(img)
    ground = 900
    x = -60
    lit_porch = None
    k = 0
    while x < w:
        hw = rng.integers(360, 470); hh = rng.integers(260, 330)
        d.rectangle([x, ground - hh, x + hw, ground], fill=(5, 6, 10))
        d.polygon([(x - 30, ground - hh), (x + hw / 2, ground - hh - 170), (x + hw + 30, ground - hh)], fill=(5, 6, 10))
        for wx in (x + 60, x + hw - 130):
            d.rectangle([wx, ground - hh + 60, wx + 70, ground - hh + 140], fill=(10, 12, 18))
        if k == 3:
            lit_porch = (x + hw / 2, ground)
        x += hw + rng.integers(90, 160); k += 1
    d.rectangle([0, ground, w, h], fill=(8, 9, 13))
    em = Image.new("RGB", (w, h))
    ed = ImageDraw.Draw(em)
    px, py = lit_porch
    ed.rectangle([px - 50, py - 200, px + 50, py - 4], fill=(70, 50, 30))        # open-looking door glow
    ed.ellipse([px - 12, py - 250, px + 12, py - 226], fill=(255, 210, 150))     # porch lamp
    # street lamp
    d.rectangle([w * 0.18, 520, w * 0.18 + 12, ground], fill=(14, 14, 18))
    ed.ellipse([w * 0.18 - 20, 505, w * 0.18 + 32, 530], fill=(200, 210, 230))
    em = add(em, glow(em, 50, 2.2))
    img = add(img, em)
    d = ImageDraw.Draw(img)
    # tiny figure at the lit door
    figure(d, px, py, 150, (18, 18, 22), (14, 14, 18), (20, 20, 24))
    return img


def fog_tex():
    small = rng.random((20, 60)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W * 3, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    return np.asarray(im, np.float32) / 255


# ================================================================= POST
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1.15 - 0.85 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2), 0.15, 1)[..., None]
GRAIN = [rng.normal(0, 1, (H, W, 1)).astype(np.float32) for _ in range(6)]


def post(img, t, grain=9.0, vig=True, bars=True, flicker=0.0):
    A = np.asarray(img, np.float32)
    if vig:
        A = A * VIG
    if flicker:
        A = A * (1 - flicker * (0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13.7)))
    A = A + GRAIN[int(t * FPS) % len(GRAIN)] * grain
    # slight teal/orange grade: lift blacks to blue
    A = A * np.array([0.98, 1.0, 1.04]) + np.array([0, 1, 4])
    if bars:
        A[:BAR] = 0; A[H - BAR:] = 0
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))


def subtitles(img, t):
    for name, start, text, who in VO:
        if not text or who == "NARRATOR":
            continue
        dur = {"dad1": 2.6, "mara1": 1.2, "dad2": 3.9}[name]
        if start - 0.05 <= t <= start + dur:
            d = ImageDraw.Draw(img)
            label = text if who != "VOICE OUTSIDE" else f"[through the door]  {text}"
            if who == "MARA":
                label = f"MARA:  {text}"
            w = d.textlength(label, font=FONT_SUB)
            d.text(((W - w) / 2, H - BAR / 2 - 24), label, font=FONT_SUB, fill=(235, 235, 235))
    return img


def rich_center(d, y, parts, font, alpha):
    total = sum(d.textlength(s, font=font) for s, _ in parts)
    x = (W - total) / 2
    for s, c in parts:
        d.text((x, y), s, font=font, fill=tuple(int(v * alpha) for v in c))
        x += d.textlength(s, font=font)


def tracked(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track


def tracked_width(d, text, font, track):
    return sum(d.textlength(ch, font=font) + track for ch in text) - track


# ================================================================= BUILD
print("building plates…", flush=True)
P_ROOM = plate_clock_room()
CL_A = clock_layer((PW, PH), "11:10", 960, 672, 100, 160, 22, pm_xy=(1395, 690), pm_size=40)
CL_A_nc = clock_layer((PW, PH), "11:10", 960, 672, 100, 160, 22, colon=False, pm_xy=(1395, 690), pm_size=40)
HALL_BASE, HALL_LAMP = build_hallway()
DOOR_PLAIN, DOOR_FIG, DOOR_FEET = build_door()
LEVER = build_handle_lever()
HANDLE_BG = build_handle_bg()
STREET = build_street()
FOG = fog_tex()

BIG = {}
for txt in ("11:10", "11:11"):
    for c in (True, False):
        lay = clock_layer((W, H), txt, 170, 300, 270, 480, 58, colon=c, pm_xy=(0, 330), pm_size=90)
        BIG[(txt, c)] = add(lay, add(glow(lay, 30, 1.4), glow(lay, 90, 1.2)))


def clock_bg_big():
    img = Image.new("RGB", (W, H), (5, 3, 4))
    d = ImageDraw.Draw(img)
    for i in range(0, H, 4):  # LCD scanlines texture
        d.line([(0, i), (W, i)], fill=(8, 4, 5))
    return img


BIG_BG = clock_bg_big()


def to_img(A):
    return Image.fromarray(np.clip(A, 0, 255).astype(np.uint8))


# ================================================================= SHOTS
def shot_clock_wide(t):
    lt = t
    colon = (t % 1.0) < 0.6
    lay = CL_A if colon else CL_A_nc
    img = add(P_ROOM, add(lay, glow(lay, 40, 1.5)))
    img = cam(img, lerp(1.0, 1.12, ease(lt / 4.5)), 0.52, 0.55)
    fade = ease(lt / 2.2)
    img = Image.fromarray((np.asarray(img, np.float32) * fade).astype(np.uint8))
    return post(img, t, 7)


def shot_hallway(t):
    lt = t - 4.5
    fl = 0.85 + 0.15 * (0.5 + 0.5 * math.sin(t * 23) * math.sin(t * 7.3))
    if 9.0 < t < 9.25:
        fl *= 0.45   # lamp stutters
    A = HALL_BASE + HALL_LAMP * fl
    img = to_img(A)
    z = lerp(1.0, 1.28, ease(lt / 8.5))
    img = cam(img, z, lerp(0.5, 0.49, lt / 8.5), lerp(0.55, 0.53, lt / 8.5),
              math.sin(t * 0.9) * 3, math.sin(t * 0.7) * 2)
    return post(img, t, 10)


def shot_clock_flip(t):
    lt = t - 13
    flipped = t >= FLIP
    txt = "11:11" if flipped else "11:10"
    colon = True if flipped else ((t % 1.0) < 0.6)
    lay = BIG[(txt, colon)]
    img = add(BIG_BG, lay)
    z = lerp(1.0, 1.05, lt / 4)
    if flipped:
        pf = t - FLIP
        z += 0.06 * math.exp(-pf * 5)
        A = np.asarray(img, np.float32)
        A *= 1 + 0.8 * math.exp(-pf * 6)
        img = to_img(A)
    sx, sy = shake(t, FLIP, 10, 7)
    img = cam(img, z, 0.5, 0.5, sx, sy)
    return post(img, t, 8)


def door_frame(t, z, cx, cy, fig_alpha, sx=0, sy=0, kick=0.0):
    A = DOOR_PLAIN * (1 - fig_alpha) + DOOR_FIG * fig_alpha
    A = A * (1 - DOOR_FEET * 0.9 * fig_alpha)
    if kick:
        A = A * (1 + kick)
    return cam(to_img(A), z, cx, cy, sx, sy)


def dust(img, t, t0):
    if t < t0 or t > t0 + 2.5:
        return img
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(int(t0 * 100))
    for _ in range(40):
        x = r.uniform(500, 1400); v = r.uniform(120, 340); y = BAR + (t - t0) * v + r.uniform(-60, 40)
        a = max(0, 1 - (t - t0) / 2.5)
        s = r.uniform(1.5, 4)
        d.ellipse([x, y, x + s, y + s], fill=(int(150 * a),) * 3)
    return img


def shot_door_knock(t):
    sx = sy = 0; kick = 0
    for k in KNOCKS:
        a, b = shake(t, k, 26, 11, 23)
        sx += a; sy += b
        if 0 <= t - k < 0.12:
            kick = 0.12
    fa = ease((t - SILHOUETTE_IN) / 1.6)
    z = lerp(1.05, 1.18, ease((t - 21.5) / 5)) if t > 21.5 else 1.05
    img = door_frame(t, z, 0.5, 0.42, fa, sx, sy, kick)
    for k in KNOCKS:
        img = dust(img, t, k)
    return post(img, t, 9)


def shot_faces(t):
    lt = t - 26.5
    img = Image.new("RGB", (W, H), (10, 12, 18))
    A = np.asarray(img, np.float32) + radial(W, H, 1500, 300, 1400, (60, 80, 120), 1.4) + radial(W, H, 200, 900, 1200, (90, 50, 20), 1.6)
    img = to_img(A)
    d = ImageDraw.Draw(img)
    jx = math.sin(t * 40) * 1.5
    # Mara behind (soft)
    mara = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mara)
    md.rectangle([1050, 560, 1650, 1200], fill=(70, 34, 40, 255))
    md.rounded_rectangle([1150, 120, 1550, 520], radius=80, fill=(110, 86, 70, 255))
    md.ellipse([1270, 260, 1300, 320], fill=(14, 10, 10, 255)); md.ellipse([1400, 260, 1430, 320], fill=(14, 10, 10, 255))
    md.arc([1300, 360, 1400, 420], 200, 340, fill=(30, 18, 18, 255), width=6)  # worried brow-ish mouth
    mara = mara.filter(ImageFilter.GaussianBlur(7))
    img.paste(mara, (0, 0), mara)
    # Alex in front
    d.rectangle([420, 700, 1180, 1300], fill=(32, 42, 66))
    hx0, hy0, hx1, hy1 = 540 + jx, 230, 1060 + jx, 730
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=100, fill=(150, 118, 94))
    d.rounded_rectangle([hx1 - 30, hy0 + 40, hx1, hy1 - 40], radius=20, fill=(110, 140, 190))  # cold rim from door
    # eyes: wide, trembling
    ey = 400 + math.sin(t * 55) * 1.2
    for ex in (690, 880):
        d.ellipse([ex + jx, ey, ex + 48 + jx, ey + 96], fill=(12, 10, 10))
        d.ellipse([ex + 12 + jx, ey + 14, ex + 26 + jx, ey + 30], fill=(230, 230, 240))
    # mouth (open, small)
    d.ellipse([770 + jx, 590, 830 + jx, 640], fill=(40, 16, 16))
    # Mara's hand covers mouth
    hp = ease((t - 27.15) / 0.35)
    if hp > 0:
        x = lerp(1500, 690, hp) + jx; y = lerp(1100, 545, hp)
        d.rectangle([x + 150, y + 60, x + 900, y + 170], fill=(70, 34, 40))       # sleeve/arm
        d.rounded_rectangle([x, y, x + 220, y + 150], radius=26, fill=(160, 124, 100))
        d.line([(x + 10, y + 50), (x + 200, y + 50)], fill=(130, 98, 78), width=4)
        d.line([(x + 10, y + 95), (x + 200, y + 95)], fill=(130, 98, 78), width=4)
    img = cam(img, lerp(1.0, 1.06, lt / 3.1), 0.45, 0.5, math.sin(t * 2) * 4, math.cos(t * 1.7) * 3)
    return post(img, t, 10)


def shot_door_push(t):
    lt = t - 29.6
    z = lerp(1.2, 1.85, ease(lt / 4.6))
    img = door_frame(t, z, 0.5, lerp(0.42, 0.33, ease(lt / 4.6)), 1.0, math.sin(t * 3) * 2, 0)
    return post(img, t, 10)


def shot_handle(t):
    t0, t1 = HANDLE_TURN
    p = ease((t - t0) / (t1 - t0))
    ang = -34 * p + (math.sin(t * 60) * 0.6 * p if t < t1 else 0)
    canvas = HANDLE_BG.copy()
    lev = LEVER.rotate(ang, resample=Image.BICUBIC, center=(1110, 150))
    # shadow
    sh = Image.new("RGBA", lev.size, (0, 0, 0, 0))
    sh.putalpha(lev.getchannel("A").point(lambda a: a * 0.6))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    px, py = 1410 - 1110, 820 - 150
    canvas.paste(Image.new("RGB", lev.size, (0, 0, 0)), (px + 30, py + 40), sh)
    canvas.paste(lev, (px, py), lev)
    z = lerp(1.0, 1.12, (t - 34.2) / 4.3)
    rise = max(0, (t - 36.5)) * 4
    img = cam(canvas, z, 0.62, 0.55, math.sin(t * 50) * rise, math.cos(t * 43) * rise)
    return post(img, t, 11)


NARR_LINES = {
    "narr1": [("In Bellwether, everyone follows ", (225, 225, 230)), ("one rule.", (255, 255, 255))],
    "narr2": [("At exactly ", (225, 225, 230)), ("11:11 PM", RED), (", you never open your front door.", (225, 225, 230))],
    "narr3": [("Not for your friends. Not for your family.", (225, 225, 230))],
    "narr4": [("And especially… not for someone you thought was gone.", (240, 240, 245))],
}
NARR_END = {"narr1": 43.4, "narr2": 47.8, "narr3": 51.1, "narr4": 54.6}


def shot_narration(t):
    lt = t - 40
    ox = lerp(0, W * 0.5, lt / 15)
    img = STREET.crop((int(ox), 0, int(ox) + W, H))
    A = np.asarray(img, np.float32)
    fx = int(lt * 60) % (W * 2)
    fog = FOG[:, fx:fx + W]
    if fog.shape[1] < W:
        fog = np.concatenate([fog, FOG[:, : W - fog.shape[1]]], 1)
    A = A + fog[..., None] * np.array([22, 26, 36]) * 1.2
    A *= ease(lt / 1.5) * (1 - ease((t - 54.4) / 0.6))
    img = to_img(A)
    d = ImageDraw.Draw(img)
    for name, start, _, who in VO:
        if who != "NARRATOR":
            continue
        end = NARR_END[name]
        if start - 0.2 <= t <= end:
            a = min(ease((t - start + 0.2) / 0.5), ease((end - t) / 0.5))
            rich_center(d, 250, NARR_LINES[name], FONT_NARR, a)
    return post(img, t, 9)


def shot_title(t):
    lt = t - TITLE_HIT
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    parts = [("THE ", (236, 232, 226)), ("11:11", RED), (" INSPECTION", (236, 232, 226))]
    track = 14
    total = sum(tracked_width(d, s, FONT_TITLE, track) + track for s, _ in parts) - track
    x = (W - total) / 2; y = 415
    for s, c in parts:
        tracked(d, (x, y), s, FONT_TITLE, c, track)
        x += tracked_width(d, s, FONT_TITLE, track) + track
    sub = "DURREN LAGGAN INCORPORATED  ·  EPISODE 01"
    sw = tracked_width(d, sub, FONT_MONO, 8)
    tracked(d, ((W - sw) / 2, 620), sub, FONT_MONO, (150, 150, 155), 8)
    d.rectangle([(W - 120) / 2, 595, (W + 120) / 2, 598], fill=RED)
    A = np.asarray(img, np.float32)
    # glitch
    g = 0
    if lt < 0.9:
        g = 1 - lt / 0.9
    elif (lt % 2.3) < 0.08:
        g = 0.35
    if g > 0:
        r = np.random.default_rng(int(t * FPS))
        for _ in range(int(12 * g) + 2):
            y0 = r.integers(330, 680); hgt = r.integers(6, 50)
            A[y0:y0 + hgt] = np.roll(A[y0:y0 + hgt], int(r.integers(-80, 80) * g), axis=1)
        A[..., 0] = np.roll(A[..., 0], int(14 * g), axis=1)
        A[..., 2] = np.roll(A[..., 2], -int(14 * g), axis=1)
        if lt < 0.12:
            A *= lt / 0.12
    A *= 1 - ease((t - 61.3) / 0.7)
    img = cam(to_img(A), lerp(1.0, 1.04, lt / 7), 0.5, 0.5)
    return post(img, t, 8)


def dli_logo(d, cx, cy, s, col):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=col, width=int(s * 0.09))
    d.polygon([(cx - s * 0.5, cy + s * 0.42), (cx - s * 0.5, cy - s * 0.05), (cx, cy - s * 0.5), (cx + s * 0.5, cy - s * 0.05), (cx + s * 0.5, cy + s * 0.42)], outline=col, width=int(s * 0.08))
    d.rectangle([cx - s * 0.12, cy + s * 0.1, cx + s * 0.12, cy + s * 0.42], fill=col)


def shot_dli(t):
    lt = t - 62
    img = Image.new("RGB", (W, H), (226, 228, 230))
    d = ImageDraw.Draw(img)
    col = (40, 46, 56)
    a = ease(lt / 0.6)
    dli_logo(d, W / 2, 400, 110, col)
    name = "DURREN LAGGAN INCORPORATED"
    nw = tracked_width(d, name, FONT_CORP, 10)
    tracked(d, ((W - nw) / 2, 560), name, FONT_CORP, col, 10)
    tag = "YOUR HOME. OUR RESPONSIBILITY."
    tw = tracked_width(d, tag, FONT_MONO, 6)
    tracked(d, ((W - tw) / 2, 650), tag, FONT_MONO, (110, 114, 122), 6)
    A = np.asarray(img, np.float32)
    # glitch into the warning at the end
    if t > 66.4:
        g = min(1, (t - 66.4) / 0.25)
        r = np.random.default_rng(int(t * FPS))
        for _ in range(10):
            y0 = r.integers(0, H - 40); A[y0:y0 + 30] = np.roll(A[y0:y0 + 30], int(r.integers(-120, 120) * g), 1)
        A = A * (1 - g) + 0 * g
        wimg = to_img(A); wd = ImageDraw.Draw(wimg)
        if t > 66.6:
            msg = "RESIDENTIAL VERIFICATION: SCHEDULED"
            mw = tracked_width(wd, msg, FONT_MONO_B, 6)
            if (t * 4) % 1 < 0.7:
                tracked(wd, ((W - mw) / 2, H / 2 - 20), msg, FONT_MONO_B, RED, 6)
        A = np.asarray(wimg, np.float32)
    A *= a
    A *= 1 - ease((t - 67.4) / 0.6)
    return post(to_img(A), t, 4, vig=False, bars=False)


def frame(t):
    if t < 4.5: img = shot_clock_wide(t)
    elif t < 13: img = shot_hallway(t)
    elif t < 17: img = shot_clock_flip(t)
    elif t < 26.5: img = shot_door_knock(t)
    elif t < 29.6: img = shot_faces(t)
    elif t < 34.2: img = shot_door_push(t)
    elif t < CUT: img = shot_handle(t)
    elif t < 40: img = post(Image.new("RGB", (W, H)), t, 6)
    elif t < 55: img = shot_narration(t)
    elif t < 62: img = shot_title(t)
    else: img = shot_dli(t)
    return subtitles(img, t)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        os.makedirs(f"{HERE}/stills", exist_ok=True)
        for ts in [float(x) for x in sys.argv[2:]]:
            frame(ts).save(f"{HERE}/stills/t{ts:05.1f}.png")
        sys.exit()
    out = sys.argv[1]
    nfr = int(DUR * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", f"{HERE}/audio.wav", "-c:v", "libx264", "-preset", "medium",
                           "-b:v", "7M", "-maxrate", "10M", "-bufsize", "14M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                           "-shortest", out], stdin=subprocess.PIPE)
    for i in range(nfr):
        ff.stdin.write(frame(i / FPS).tobytes())
        if i % 120 == 0:
            print(f"frame {i}/{nfr}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done", out)
