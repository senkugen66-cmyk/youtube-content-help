"""Renders the MeowDude outro and muxes it with output/outro_audio.wav.

The uploaded logo is split into layers straight from its pixels (no redrawing, no font swap):
  tile      - the orange rounded square
  cat       - the cream cat face (with the play-button hole filled)
  mouth     - the orange play triangle, drawn back on top of the face
  letters   - the 8 wordmark glyphs, each its own layer
With every transform at rest the layers recompose the original logo exactly; edges are rebuilt
at 2x supersampling so the small JPEG still lands crisp at 1080p.

Face, mouth and wordmark squash are driven by the loudness envelopes of the two voice stems,
so the animation is locked to MEOW and DUDE.

Usage:  python3 build_video.py   (run build_audio.py first) -> output/meowdude_outro.mp4
"""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.spatial import ConvexHull
from timeline import FPS, DURATION, SR, T_WIGGLE, T_MEOW, T_POP, T_DUDE, T_BOUNCE

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "output")
W, H, SS = 1920, 1080, 2           # output size, supersampling factor
LOGO_W = 1180                      # on-screen width of the full logo (px)
SOLO = 1.7                         # how much bigger the icon is while it's alone on screen

# ---------------------------------------------------------------------------------------------
# Logo -> layers
# ---------------------------------------------------------------------------------------------
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

class Layer:
    def __init__(self, alpha, color, R, region):
        ys, xs = np.where(alpha > 0.003)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        a = (alpha[y0:y1, x0:x1] * 255).round().astype(np.uint8)
        rgba = np.zeros(a.shape + (4,), np.uint8); rgba[..., :3] = color; rgba[..., 3] = a
        self.img = Image.fromarray(rgba, "RGBA")
        self.origin = np.array([x0 / R, y0 / R])                     # top-left in logo px
        self.R = R
        my, mx = np.where(region)
        self.box = (mx.min(), my.min(), mx.max() + 1, my.max() + 1)  # logo px

    def pix_to_logo(self):
        return np.array([[1 / self.R, 0, self.origin[0]], [0, 1 / self.R, self.origin[1]], [0, 0, 1]])

def build_layers(path, R):
    src = Image.open(path).convert("RGB")
    lo = np.asarray(src).astype(float)
    r, g, b = lo[..., 0], lo[..., 1], lo[..., 2]
    L = 0.3 * r + 0.59 * g + 0.11 * b

    # palette sampled from the logo itself
    org_px = (r - b) > 150
    orange = np.median(lo[org_px], axis=0)
    dark_px = L < 60
    dark = np.median(lo[dark_px], axis=0)
    bg = np.median(lo[:12].reshape(-1, 3), axis=0)

    # coarse masks at source resolution
    orange_bin = (r - b) > 88
    lab, n = ndi.label(orange_bin)
    sizes = ndi.sum(orange_bin, lab, range(1, n + 1))
    order = np.argsort(sizes)[::-1] + 1
    tile_bin, tri_bin = lab == order[0], lab == order[1]
    cream_px = ndi.binary_erosion(ndi.binary_fill_holes(tile_bin) & ((r - b) < 20), iterations=2)
    cream = np.median(lo[cream_px], axis=0)

    word_bin = (L < 140); word_bin[:, :tile_bin.nonzero()[1].max() + 20] = False
    wlab, wn = ndi.label(word_bin)
    letters = sorted([wlab == i for i in range(1, wn + 1) if (wlab == i).sum() > 30],
                     key=lambda m: m.nonzero()[1].min())

    # supersampled continuous features -> crisp anti-aliased alphas
    hs, ws = lo.shape[0] * R, lo.shape[1] * R
    up = np.asarray(src.resize((ws, hs), Image.BICUBIC)).astype(float)
    up = ndi.gaussian_filter(up, sigma=(0.6 * R, 0.6 * R, 0))
    ur, ug, ub = up[..., 0], up[..., 1], up[..., 2]
    uL = 0.3 * ur + 0.59 * ug + 0.11 * ub
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    bgL, oL, dL = lum(bg), lum(orange), lum(dark)
    # key the orange off luminance: JPEG keeps luma at full res but halves chroma (jaggy edges)
    a_or = smoothstep(0.38, 0.62, np.clip((bgL - uL) / (bgL - oL), 0, 1))
    a_dk = smoothstep(0.38, 0.62, np.clip((bgL - uL) / (bgL - dL), 0, 1))

    def upmask(m, grow=0):
        if grow: m = ndi.binary_dilation(m, iterations=grow)
        return np.asarray(Image.fromarray(m.astype(np.uint8) * 255).resize((ws, hs), Image.NEAREST)) > 127

    # tile = convex hull of the orange square, solid inside, original soft edge at the rim
    ys, xs = np.nonzero(tile_bin)
    pts = np.c_[xs + 0.5, ys + 0.5]
    hull = pts[ConvexHull(pts).vertices] * R
    hm = Image.new("L", (ws, hs), 0); ImageDraw.Draw(hm).polygon([tuple(p) for p in hull], fill=255)
    hull_m = np.asarray(hm) > 127
    inner = ndi.binary_erosion(hull_m, iterations=int(3 * R))
    outer = ndi.binary_dilation(hull_m, iterations=int(2 * R))
    a_tile = np.where(inner, 1.0, a_or * outer)

    tri_region = upmask(tri_bin, grow=2)
    a_mouth = a_or * tri_region
    a_cat = np.clip((1 - a_or) * inner + a_mouth, 0, 1)

    layers = {
        "tile": Layer(a_tile, orange, R, tile_bin),
        "cat": Layer(a_cat, cream, R, ndi.binary_fill_holes(~orange_bin & ndi.binary_erosion(
            ndi.binary_fill_holes(tile_bin), iterations=3))),
        "mouth": Layer(a_mouth, orange, R, tri_bin),
        "letters": [Layer(a_dk * upmask(m, grow=3), dark, R, m) for m in letters],
    }
    return layers, bg, (orange, cream, dark)

# ---------------------------------------------------------------------------------------------
# Little animation toolkit
# ---------------------------------------------------------------------------------------------
def T(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1.0]])
def about(p, sx=1, sy=1, rot=0, tx=0, ty=0):
    """Scale (local axes) then rotate (degrees, clockwise on screen) about pivot p, then translate."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return T(p[0] + tx, p[1] + ty) @ np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) @ \
        np.diag([sx, sy, 1.0]) @ T(-p[0], -p[1])

def clamp01(x): return min(1.0, max(0.0, x))
def ease(x): x = clamp01(x); return x * x * (3 - 2 * x)
def wobble(t, f=4.0, z=0.28):
    """Damped spring: 1 at t=0, rings and settles to 0. Negative t -> 1 (not started)."""
    if t < 0: return 1.0
    w = 2 * math.pi * f
    return math.exp(-z * w * t) * math.cos(w * math.sqrt(1 - z * z) * t)
def kick(t, f=4.0, z=0.3):
    """Damped sine: 0 at t=0, jolts out, rings back to 0."""
    if t < 0: return 0.0
    w = 2 * math.pi * f
    return math.exp(-z * w * t) * math.sin(w * math.sqrt(1 - z * z) * t)
def noise(t, seed=0):
    k = seed * 1.618
    return (math.sin(t * 2.1 + k) * 0.5 + math.sin(t * 3.7 + 2 * k) * 0.3 + math.sin(t * 7.3 + 3 * k) * 0.2)

def envelope(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(float)
    hop = SR // 200
    e = np.array([np.sqrt(np.mean(x[i:i + 2 * hop] ** 2)) for i in range(0, len(x), hop)])
    e = e / e.max()
    out, v = np.zeros_like(e), 0.0
    for i, s in enumerate(e):                      # fast attack, lazy release
        v += (s - v) * (0.6 if s > v else 0.12); out[i] = v
    return lambda t: float(np.interp(t * 200, np.arange(len(out)), out, left=0, right=0)) if t >= 0 else 0.0

# ---------------------------------------------------------------------------------------------
# Frame composer
# ---------------------------------------------------------------------------------------------
def draw(canvas, layer, M):
    """Composite `layer` onto `canvas`; M maps logo px -> supersampled canvas px."""
    A = M @ layer.pix_to_logo()
    w, h = layer.img.size
    c = A @ np.array([[0, w, 0, w], [0, 0, h, h], [1, 1, 1, 1]])
    x0, y0 = max(0, int(math.floor(c[0].min())) - 1), max(0, int(math.floor(c[1].min())) - 1)
    x1, y1 = min(canvas.width, int(math.ceil(c[0].max())) + 1), min(canvas.height, int(math.ceil(c[1].max())) + 1)
    if x1 <= x0 or y1 <= y0: return
    inv = np.linalg.inv(A) @ T(x0, y0)
    img = layer.img.transform((x1 - x0, y1 - y0), Image.AFFINE, data=tuple(inv[:2].ravel()),
                              resample=Image.BICUBIC)
    canvas.alpha_composite(img, (x0, y0))

def main():
    # logo bbox (in logo px) decides the display scale; layers are built at that scale x SS
    lo = np.asarray(Image.open(os.path.join(HERE, "assets", "meowdude-logo.jpg")).convert("RGB")).astype(float)
    ink = ((lo[..., 0] - lo[..., 2]) > 88) | ((0.3 * lo[..., 0] + 0.59 * lo[..., 1] + 0.11 * lo[..., 2]) < 140)
    ys, xs = np.nonzero(ink)
    lb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    S = LOGO_W / (lb[2] - lb[0])
    R = int(math.ceil(S * SS))
    layers, bg, _ = build_layers(os.path.join(HERE, "assets", "meowdude-logo.jpg"), R)
    bg = tuple(int(round(v)) for v in bg)

    logo_c = np.array([(lb[0] + lb[2]) / 2, (lb[1] + lb[3]) / 2])
    tb = layers["tile"].box
    icon_c = np.array([(tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2])
    cb = layers["cat"].box
    cat_foot = np.array([(cb[0] + cb[2]) / 2, cb[3]])
    mb = layers["mouth"].box
    mouth_c = np.array([(mb[0] + mb[2]) / 2, (mb[1] + mb[3]) / 2])
    letters = layers["letters"]
    word_base = np.array([(letters[0].box[0] + letters[-1].box[2]) / 2, max(l.box[3] for l in letters)])
    feet = [np.array([(l.box[0] + l.box[2]) / 2, l.box[3]]) for l in letters]

    env_meow = envelope(os.path.join(OUT, "meow.wav"))
    env_dude = envelope(os.path.join(OUT, "dude.wav"))
    rng = np.random.default_rng(42)
    letter_rot = rng.uniform(-9, 9, len(letters))
    letter_lag = rng.uniform(0, 0.025, len(letters))

    place = np.diag([SS, SS, 1.0]) @ T(W / 2, H / 2) @ np.diag([S, S, 1.0]) @ T(-logo_c[0], -logo_c[1])
    solo_dx = logo_c[0] - icon_c[0]

    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(OUT, "meowdude_outro.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", os.path.join(OUT, "outro_audio.wav"),
         "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "256k", "-shortest", out], stdin=subprocess.PIPE)

    n_frames = int(round(DURATION * FPS))
    for fi in range(n_frames):
        t = fi / FPS
        em, ed = env_meow(t - T_MEOW), env_dude(t - T_DUDE)

        # ---- camera: the DUDE literally shakes the screen ------------------------------------
        shake = 7.0 * ed
        cam = about((W / 2, H / 2), 1 + 0.03 * ed, 1 + 0.03 * ed,
                    rot=0.6 * ed * noise(t * 9, 3),
                    tx=shake * noise(t * 31, 1), ty=shake * noise(t * 29, 2))
        cam = np.diag([SS, SS, 1.0]) @ cam @ np.diag([1 / SS, 1 / SS, 1.0])

        # ---- icon group ------------------------------------------------------------------------
        p = t - T_POP
        travel = 0.0 if p < 0 else 1 - wobble(p, f=2.6, z=0.42)          # overshoots a little past home
        hop = -38 * math.sin(math.pi * clamp01(p / 0.24)) if 0 <= p < 0.24 else 0
        shrink = 0.0 if p < 0 else 1 - wobble(p, f=3.0, z=0.6)          # size settles with less overshoot
        solo = SOLO + (1 - SOLO) * shrink
        sx = sy = solo
        # the cat's whole body flinches when it first wakes up
        sy *= 1 - 0.07 * kick(t - T_WIGGLE, f=6, z=0.35)
        # meow: trembling + swelling with the squeak
        sx *= 1 + 0.05 * em; sy *= 1 + 0.07 * em
        jit = 1.6 * em
        # anticipation squash right before the pop, then landing squash
        ant = ease((t - (T_POP - 0.08)) / 0.08) if t < T_POP else 0
        sy *= 1 - 0.10 * ant; sx *= 1 + 0.07 * ant
        land = kick(p - 0.22, f=5, z=0.35)
        sy *= 1 - 0.12 * land; sx *= 1 + 0.08 * land
        icon_rot = 3.5 * em * math.sin(2 * math.pi * 6 * t) - 5 * kick(p, f=3, z=0.4) + 2.5 * ed * noise(t * 13, 5)
        icon_M = about(icon_c, sx, sy, icon_rot,
                       tx=solo_dx * (1 - travel) + jit * noise(t * 47, 7) - 5 * ed,
                       ty=hop + jit * noise(t * 43, 8))

        # ---- cat face --------------------------------------------------------------------------
        w = t - T_WIGGLE
        tilt = 13 * math.sin(2 * math.pi * 6.5 * w) * math.exp(-w * 7) if 0 <= w < 0.6 else 0
        peek = -6 * math.sin(math.pi * clamp01(w / 0.22)) if 0 <= w < 0.22 else 0
        cat_rot = tilt - 6 * em - 10 * ed + 8 * kick(t - (T_BOUNCE + 0.45), f=3.5, z=0.35)
        cat_sx = 1 - 0.08 * em + 0.05 * ed
        cat_sy = 1 + 0.22 * em - 0.10 * ed
        cat_M = about(cat_foot, cat_sx, cat_sy, cat_rot, ty=peek)
        mouth_s = 1 + 0.38 * em - 0.35 * ed                            # MEEEOW mouth vs. shocked tiny mouth
        mouth_M = about(mouth_c, mouth_s, mouth_s, 0)

        # ---- wordmark --------------------------------------------------------------------------
        word_M = about(word_base, 1 + 0.08 * ed, 1 - 0.18 * ed, 0,
                       ty=1.8 * ed * math.sin(2 * math.pi * 11 * t))
        letter_Ms = []
        for i, foot in enumerate(feet):
            q = t - (T_POP + 0.09 + 0.028 * i + letter_lag[i])
            if q < 0: letter_Ms.append(None); continue
            s = 1 - wobble(q, f=3.4, z=0.45)                          # 0 -> overshoot -> 1
            rot = letter_rot[i] * wobble(q, f=2.8, z=0.4)
            b = t - (T_BOUNCE + 0.05 * i)
            dy, bsx, bsy = 0.0, 1.0, 1.0
            if 0 <= b < 0.30:                                         # tiny hop
                u = b / 0.30
                dy = -15 * 4 * u * (1 - u)
                bsy, bsx = 1 + 0.10 * math.sin(math.pi * u), 1 - 0.05 * math.sin(math.pi * u)
            land = kick(b - 0.30, f=6, z=0.35)
            bsy *= 1 - 0.13 * land; bsx *= 1 + 0.07 * land
            if i == len(feet) - 1:                                    # the last "e" can't stop wobbling
                rot += 7 * kick(b - 0.30, f=4.0, z=0.4)
            letter_Ms.append(about(foot, max(s, 0) * bsx, max(s, 0) * bsy, rot, ty=dy))

        # ---- compose ---------------------------------------------------------------------------
        canvas = Image.new("RGBA", (W * SS, H * SS), bg + (255,))
        base = cam @ place
        draw(canvas, layers["tile"], base @ icon_M)
        draw(canvas, layers["cat"], base @ icon_M @ cat_M)
        draw(canvas, layers["mouth"], base @ icon_M @ cat_M @ mouth_M)
        for L, M in zip(letters, letter_Ms):
            if M is not None: draw(canvas, L, base @ word_M @ M)
        frame = canvas.convert("RGB").reduce(SS)
        ff.stdin.write(frame.tobytes())
        if fi in (0, n_frames - 1) or fi % 30 == 0:
            frame.save(os.path.join(BUILD, f"frame_{fi:03d}.png"))
    ff.stdin.close(); ff.wait()
    print("->", out)

if __name__ == "__main__":
    main()
