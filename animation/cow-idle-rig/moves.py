"""Four performance clips on the mesh-warp rig: bounce, hop, sway, shy."""
import numpy as np, sys, subprocess, math, os
from PIL import Image, ImageFilter, ImageDraw, ImageFont
FPS = 30
CW, CH = 1080, 1920
K = float(os.environ.get("MOVES_K", 2.1))
X0, Y0 = 160, 15
OY = 160
FOOT, HIP = 700, 345

def load(p):
    im = Image.open(p).convert('RGBA'); w, h = im.size
    im = im.resize((round(w*K), round(h*K)), Image.LANCZOS)
    rgb = im.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    a = np.asarray(im)[..., 3:].astype(np.float32)/255
    return np.dstack([np.asarray(rgb).astype(np.float32)/255*a, a])

body = load('body.png'); tail = load('tail.png')
LH, LW = body.shape[:2]
OX = (CW-LW)//2
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
U = xx/K + X0; V = yy/K + Y0

def ss(e0, e1, x):
    t = np.clip((x-e0)/(e1-e0), 0, 1); return t*t*(3-2*t)
def sss(e0, e1, x):   # scalar smoothstep
    t = min(max((x-e0)/(e1-e0), 0), 1); return t*t*(3-2*t)

def rot(u, v, w, px, py, deg):
    if deg == 0: return u, v
    th = -math.radians(deg); c, s = math.cos(th), math.sin(th)
    du, dv = u-px, v-py
    return u + w*(px + c*du - s*dv - u), v + w*(py + s*du + c*dv - v)

def bilinear(img, x, y):
    h, w = img.shape[:2]
    x = np.clip(x, 0, w-1.001); y = np.clip(y, 0, h-1.001)
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = (x-x0)[..., None]; fy = (y-y0)[..., None]
    return (img[y0, x0]*(1-fx)+img[y0, x0+1]*fx)*(1-fy) + (img[y0+1, x0]*(1-fx)+img[y0+1, x0+1]*fx)*fy

def radial(cx, cy, r0, r1): return 1-ss(r0, r1, np.hypot(U-cx, V-cy))
wHead = (1-ss(136, 164, V))*ss(222, 240, U)*(1-ss(422, 440, U))
wEarL = radial(262, 90, 13, 24)*wHead
wEarR = radial(388, 81, 22, 32)*wHead
wBell = ss(312, 318, U)*(1-ss(343, 349, U))*ss(155, 160, V)*(1-ss(186, 192, V))
wArm = ((1-ss(248, 262, U)) + ss(398, 410, U))*ss(185, 200, V)*(1-ss(405, 420, V))
torsoLift = (1-wArm)*np.clip(HIP-V, 0, 185) + wArm*185
wArmL = (1-ss(248, 262, U))*ss(195, 210, V)*(1-ss(405, 425, V))
wArmR = ss(398, 410, U)*ss(195, 210, V)*(1-ss(405, 425, V))
wShrug = np.maximum(1-ss(185, 235, V), wArm)

# tail sampled only inside its neighbourhood
ty0, ty1 = int((520-Y0)*K), int((650-Y0)*K); tx0, tx1 = int((290-X0)*K), int((420-X0)*K)

# blush maps in source-layer pixel space
sy, sx = np.mgrid[0:LH, 0:LW].astype(np.float32); su = sx/K+X0; sv = sy/K+Y0
BLUSH = (np.exp(-(((su-301)/9)**2 + ((sv-121)/4.5)**2)) + np.exp(-(((su-351)/9)**2 + ((sv-115)/4.5)**2)))[..., None]
PINK = np.array([0.98, 0.55, 0.60], np.float32)
del sy, sx, su, sv

EYES = [(307, 109.5, 11.5, 6.8), (346.5, 103.5, 11.5, 6.8)]
SKIN = np.array([247, 219, 214], np.float32)/255

def face(src, b, glance, blush):
    if b <= 0.001 and abs(glance) < 0.01 and blush < 0.01: return src
    out = src.copy()
    if blush > 0.01:
        lum = (src[..., :3].mean(2, keepdims=True)/np.maximum(src[..., 3:], 1e-3))
        a = BLUSH*0.42*blush*ss(0.62, 0.85, lum)
        out[..., :3] = out[..., :3]*(1-a) + PINK*a*out[..., 3:]
    base = out.copy()
    for (cx, cy, rx, ry) in EYES:
        x0, x1 = int((cx-rx-2-X0)*K), int((cx+rx+2-X0)*K)+1
        y0, y1 = int((cy-ry-2-Y0)*K), int((cy+ry+3-Y0)*K)+1
        gy, gx = np.mgrid[y0:y1, x0:x1]
        if abs(glance) >= 0.01:   # slide the iris inside the eye opening
            sh = glance*K
            xs = np.clip(gx - sh, 0, LW-2)
            moved = bilinear(base, xs.astype(np.float32), gy.astype(np.float32))
            e2 = ((gx/K+X0-cx)/(rx-1.5))**2 + ((gy/K+Y0-cy-1.5)/(ry-2.6))**2
            m2 = (1-ss(0.55, 1.0, e2))[..., None]
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1]*(1-m2) + moved*m2
        if b <= 0.001: continue
        src_e = out.copy()
        fill = src_e[y0:y1, x0:x1].copy()
        for j in range(x1-x0):
            col = x0+j
            f = (col/K+X0-cx)/rx
            if abs(f) >= 1: continue
            h = math.sqrt(1-f*f)
            etop = (cy-ry*h-Y0)*K; top = etop
            for r_ in range(int(etop), int(etop+5*K)):
                if src_e[r_, col, :3].mean() < 0.33: top = r_; break
            closed = (cy+0.45*ry*h-Y0)*K
            lid = top + b*(closed-top)
            lash = 2.1*K*(0.5+0.5*h)
            for row in range(int(top), int(closed+lash+2.2*K)+1):
                i = row-y0
                if i < 0 or i >= fill.shape[0]: continue
                if row < lid:
                    fill[i, j, :3] = SKIN*(0.955+0.045*(lid-row)/max(lid-top, 1)); fill[i, j, 3] = 1
                elif row < lid+lash:
                    fill[i, j] = src_e[int(top+(row-lid)), col]
                elif b > 0.85:
                    fill[i, j, :3] = SKIN; fill[i, j, 3] = 1
        e = ((gx/K+X0-cx)/(rx+0.5))**2 + ((gy/K+Y0-cy)/(ry+1.2))**2
        m = (1-ss(0.62, 1.0, e))[..., None]
        out[y0:y1, x0:x1] = src_e[y0:y1, x0:x1]*(1-m) + fill*m
    return out

def blink_at(t, centers, w=0.09):
    b = 0
    for c in centers:
        d = abs(t-c)/w
        if d < 1: b = max(b, min(1, (1-d)*1.6))
    return b

def squash_legs(v, c):
    """knee-bend squash (c>0) / stretch (c<0): legs between HIP and FOOT scale toward feet, upper body rides along."""
    if c == 0: return v
    L = FOOT-HIP
    hip_out = FOOT - L*(1-c)
    return np.where(v >= FOOT, v, np.where(v >= hip_out, FOOT-(FOOT-v)/(1-c), v - c*L))

def coords(p, frac, region=None):
    u, v = (U, V) if region is None else (U[region], V[region])
    v = v + frac/K
    u, v = rot(u, v, 1.0, 308, 790, p.get('sway', 0))
    if region is not None:                      # tail layer
        v = squash_legs(v, p.get('c', 0))
        return rot(u, v, 1.0, 388, 577, p.get('tail', 0))
    v = squash_legs(v, p.get('c', 0))
    v = v + 0.0075*p.get('breath', 0)*torsoLift
    v = v + p.get('shrug', 0)*wShrug
    u, v = rot(u, v, wArmL, 257, 203, p.get('armL', 0))
    u, v = rot(u, v, wArmR, 403, 203, p.get('armR', 0))
    v = v - p.get('headDrop', 0)*wHead
    u, v = rot(u, v, wHead, 330, 152, p.get('head', 0))
    u, v = rot(u, v, wEarL, 279, 88, p.get('earL', 0))
    u, v = rot(u, v, wEarR, 363, 66, p.get('earR', 0))
    u, v = rot(u, v, wBell, 330, 157, p.get('bell', 0))
    return u, v

# ---------------- clips ----------------
TAU = 2*math.pi
def bounce(t):          # 4 s, 1 bounce / s
    ph = t % 1
    c = 0.016*(1-math.cos(TAU*ph))**1.3
    lag = lambda d: math.sin(TAU*(ph-d))
    return dict(c=c, breath=0.4*math.sin(TAU*t/2),
                earL=-9*lag(0.12), earR=9*lag(0.12), bell=-6*lag(0.25) + 2*math.sin(TAU*2*ph),
                tail=-10*lag(0.22), head=0.8*lag(0.1), armL=-0.8*lag(0.15), armR=0.8*lag(0.15),
                blink=blink_at(t, [1.55, 3.5]))

def hop_h(ph):
    if 0.18 <= ph <= 0.62:
        s = (ph-0.18)/0.44; return 4*s*(1-s)
    return 0.0
def hop(t):             # 3 s, 2 hops
    ph = t % 1.5 / 1.5
    H = 115
    if ph < 0.15:   c = 0.05*sss(0, 0.15, ph)
    elif ph < 0.22: c = 0.05 + (-0.035-0.05)*sss(0.15, 0.22, ph)
    elif ph < 0.40: c = -0.035*(1-sss(0.22, 0.40, ph))
    elif ph < 0.62: c = 0
    elif ph < 0.70: c = 0.05*sss(0.62, 0.70, ph)
    elif ph < 0.85: c = 0.05 + (-0.012-0.05)*sss(0.70, 0.85, ph)
    else:           c = -0.012*(1-sss(0.85, 1.0, ph))
    vel = lambda q: (hop_h((q+0.01) % 1) - hop_h((q-0.01) % 1))/0.02/9.1
    v = vel((ph-0.06) % 1)                       # ears/tail drag behind the body
    land = c if ph >= 0.62 else 0
    return dict(jump=H*hop_h(ph), c=c,
                earL=-15*v + 170*land, earR=15*v - 170*land,
                tail=-16*v, bell=7*vel((ph-0.12) % 1) + 80*land,
                head=-1.0*vel((ph-0.08) % 1), armL=1.6*v, armR=-1.6*v,
                blink=blink_at(t, [0.98, 2.48], 0.08))

def sway(t):            # 4 s @ 120 BPM, one side per beat
    ph = t % 1
    s = lambda d: math.sin(TAU*(ph-d))
    return dict(sway=2.4*s(0), c=0.011*(1+math.cos(2*TAU*ph)),
                head=-1.7*s(0.12), earL=-7*s(0.16), earR=-7*s(0.16),
                bell=-9*s(0.22), tail=-13*s(0.2), armL=-1.4*s(0.1), armR=-1.4*s(0.1),
                breath=0.3*math.sin(TAU*t/2), blink=blink_at(t, [1.75, 3.25]))

def shy(t):             # 4 s one-shot that returns to neutral
    env = sss(0.6, 1.1, t)*(1-sss(3.0, 3.7, t))
    sh = sss(0.85, 1.15, t)*(1-0.55*sss(1.15, 1.8, t))*(1-sss(3.0, 3.6, t))
    gl = sss(0.75, 1.0, t)*(1-sss(2.9, 3.3, t))
    bl = sss(1.0, 1.9, t)*(1-sss(3.1, 3.9, t))
    ring = lambda t0, a: a*math.exp(-(t-t0)*2.8)*math.sin(TAU*1.7*(t-t0)) if t > t0 else 0
    tremble = 1.2*math.sin(TAU*5*t)*env
    return dict(earL=-14*env + tremble, earR=14*env - tremble,
                head=-4.5*env, headDrop=2.2*env, shrug=-3.8*sh,
                armL=-1.3*env, armR=1.3*env, tail=-9*env + 2*math.sin(TAU*1.5*t)*env,
                bell=ring(0.9, 7) + ring(3.0, -6), breath=0.5*math.sin(TAU*t/1.33),
                glance=-2.0*gl, blush=bl, blink=blink_at(t, [1.45, 3.4]))

CLIPS = dict(bounce=(bounce, 4), hop=(hop, 3), sway=(sway, 4), shy=(shy, 4))

# ---------------- stage ----------------
def make_bg():
    g = np.linspace(0, 1, CH)[:, None, None]
    bg = (np.array([255, 241, 236])*(1-g) + np.array([246, 222, 228])*g)*np.ones((1, CW, 1))
    y2, x2 = np.mgrid[0:CH, 0:CW]
    glow = np.exp(-(((x2-CW/2)/430)**2 + ((y2-700)/520)**2))[..., None]
    return (bg*(1-0.35*glow) + np.array([255, 252, 246])*0.35*glow).astype(np.float32)/255
BG = make_bg()
FEET_Y = OY + (790-Y0)*K - 8
sh_im = Image.new('L', (CW, CH), 0); ImageDraw.Draw(sh_im).ellipse([CW/2-290, FEET_Y-32, CW/2+290, FEET_Y+32], fill=95)
SHADOW = (np.asarray(sh_im.filter(ImageFilter.GaussianBlur(22))).astype(np.float32)/255)[..., None]
rng = np.random.default_rng(7)
PARTS = [(rng.uniform(0, CW), rng.uniform(0, CH), rng.uniform(3, 8), rng.uniform(0, 1)) for _ in range(24)]
font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 26)
TREG = (slice(ty0, ty1), slice(tx0, tx1))

def render(fn, t, dur):
    p = fn(t)
    canvas = BG.copy()
    jump = p.get('jump', 0)
    sx = int(round(p.get('sway', 0)*6)); k = 0.22*(1-0.65*jump/115)
    shd = np.roll(SHADOW, sx, axis=1)
    canvas = canvas*(1-k*shd) + np.array([0.45, 0.30, 0.35])*k*shd
    pim = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(pim)
    for (x, y, r, ph) in PARTS:
        y_ = (y - (t/dur)*CH*0.25) % (CH+40) - 20; x_ = x + 14*math.sin(TAU*(t/dur+ph))
        d.ellipse([x_-r, y_-r, x_+r, y_+r], fill=(255, 255, 255, int(70+50*math.sin(TAU*(2*t/dur+ph)))))
    pa = np.asarray(pim).astype(np.float32)/255
    canvas = canvas*(1-pa[..., 3:]) + pa[..., :3]*pa[..., 3:]
    off = int(math.floor(jump)); frac = jump-off
    top = OY - off
    region = canvas[top:top+LH, OX:OX+LW]
    tu, tv = coords(p, -frac, TREG)
    ts = bilinear(tail, (tu-X0)*K, (tv-Y0)*K)
    r2 = region[TREG]; r2[:] = r2*(1-ts[..., 3:]) + ts[..., :3]
    src = face(body, p.get('blink', 0), p.get('glance', 0), p.get('blush', 0))
    u, v = coords(p, -frac)
    s = bilinear(src, (u-X0)*K, (v-Y0)*K)
    region[:] = region*(1-s[..., 3:]) + s[..., :3]
    out = Image.fromarray((np.clip(canvas, 0, 1)*255).astype(np.uint8))
    ImageDraw.Draw(out).text((CW-40, CH-44), 'art: ARVANES', font=font, fill=(120, 95, 105), anchor='rs')
    return out

if __name__ == '__main__':
    name = sys.argv[1]; fn, dur = CLIPS[name]
    if len(sys.argv) > 2 and sys.argv[2] == 'preview':
        for f in [int(x) for x in sys.argv[3].split(',')]:
            render(fn, f/FPS, dur).save(f'pv_{name}_{f:03d}.png')
        sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{name}.mp4'], stdin=subprocess.PIPE)
    for f in range(int(dur*FPS)):
        ff.stdin.write(render(fn, f/FPS, dur).tobytes())
    ff.stdin.close(); ff.wait()
