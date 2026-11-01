import numpy as np, sys, subprocess, math
from PIL import Image, ImageFilter, ImageDraw, ImageFont
FPS, SECS = 30, 6
N = FPS*SECS
CW, CH = 1080, 1920
K = 2.25                      # upscale from source pixels
X0, Y0 = 160, 15              # crop origin in original image coords
OX, OY = None, 95             # layer placement on canvas
MODE = sys.argv[1] if len(sys.argv) > 1 else 'video'

def load(p):
    im = Image.open(p).convert('RGBA')
    w, h = im.size
    im = im.resize((round(w*K), round(h*K)), Image.LANCZOS)
    rgb = im.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    a = np.asarray(im)[..., 3:].astype(np.float32)/255
    c = np.asarray(rgb).astype(np.float32)/255
    return np.dstack([c*a, a])            # premultiplied

body = load('body.png'); tail = load('tail.png')
LH, LW = body.shape[:2]
OX = (CW - LW)//2
yy, xx = np.mgrid[0:LH, 0:LW].astype(np.float32)
U = xx/K + X0; V = yy/K + Y0          # output pixel -> original-image coords

def ss(e0, e1, x):
    t = np.clip((x-e0)/(e1-e0), 0, 1); return t*t*(3-2*t)

def rot_sample(u, v, w, px, py, deg):
    """inverse-rotate sample positions by weight w around pivot."""
    th = -math.radians(deg); c, s = math.cos(th), math.sin(th)
    du, dv = u-px, v-py
    ru, rv = px + c*du - s*dv, py + s*du + c*dv
    return u + w*(ru-u), v + w*(rv-v)

def bilinear(img, x, y):
    h, w = img.shape[:2]
    x = np.clip(x, 0, w-1.001); y = np.clip(y, 0, h-1.001)
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = (x-x0)[..., None]; fy = (y-y0)[..., None]
    a = img[y0, x0]; b = img[y0, x0+1]; c = img[y0+1, x0]; d = img[y0+1, x0+1]
    return (a*(1-fx)+b*fx)*(1-fy) + (c*(1-fx)+d*fx)*fy

# static weights (original coords)
wHead = (1-ss(136, 164, V)) * ss(222, 240, U) * (1-ss(422, 440, U))
def radial(cx, cy, r0, r1): return 1-ss(r0, r1, np.hypot(U-cx, V-cy))
wEarL = radial(262, 90, 13, 24)
wEarR = radial(385, 79, 18, 30)
wBell = ss(312, 318, U)*(1-ss(343, 349, U))*ss(155, 160, V)*(1-ss(186, 192, V))
wArm = ((1-ss(248, 262, U)) + ss(398, 410, U)) * ss(185, 200, V) * (1-ss(405, 420, V))
wLegs = ss(330, 360, V)
torsoLift = (1-wArm)*np.clip(345-V, 0, 185) + wArm*185
wArmL = (1-ss(248, 262, U))*ss(195, 210, V)
wArmR = ss(398, 410, U)*ss(195, 210, V)

# eyes: (x0,x1, top, bottom) in original coords
EYES = [(307, 109.5, 11.5, 6.8), (346.5, 103.5, 11.5, 6.8)]   # cx, cy, rx, ry (original coords)
SKIN = np.array([247, 219, 214], np.float32)/255

def blink_img(src, b):
    if b <= 0.001: return src
    out = src.copy()
    for (cx, cy, rx, ry) in EYES:
        x0, x1 = int((cx-rx-2-X0)*K), int((cx+rx+2-X0)*K)+1
        y0, y1 = int((cy-ry-2-Y0)*K), int((cy+ry+3-Y0)*K)+1
        fill = src[y0:y1, x0:x1].copy()
        for j in range(x1-x0):
            col = x0+j
            f = (col/K + X0 - cx)/rx
            if abs(f) >= 1: continue
            h = math.sqrt(1-f*f)
            etop = (cy - ry*h - Y0)*K
            top = etop
            for r_ in range(int(etop), int(etop + 5*K)):
                if src[r_, col, :3].mean() < 0.33: top = r_; break
            closed = (cy + 0.45*ry*h - Y0)*K
            lid = top + b*(closed-top)
            lash = 2.1*K*(0.5+0.5*h)
            for row in range(int(top), int(closed + lash + 2.2*K)+1):
                i = row - y0
                if i < 0 or i >= fill.shape[0]: continue
                if row < lid:
                    shade = 0.955 + 0.045*(lid-row)/max(lid-top, 1)
                    fill[i, j, :3] = SKIN*shade; fill[i, j, 3] = 1
                elif row < lid + lash:
                    fill[i, j] = src[int(top + (row-lid)), col]
                elif b > 0.85:
                    fill[i, j, :3] = SKIN; fill[i, j, 3] = 1
        gy, gx = np.mgrid[y0:y1, x0:x1]
        e = ((gx/K + X0 - cx)/(rx+0.5))**2 + ((gy/K + Y0 - cy)/(ry+1.2))**2
        m = (1 - ss(0.62, 1.0, e))[..., None]
        out[y0:y1, x0:x1] = src[y0:y1, x0:x1]*(1-m) + fill*m
    return out

def blink_amt(t):
    b = 0
    for c in (0.30, 0.86, 0.925):
        d = abs(t-c)/0.028
        if d < 1: b = max(b, min(1, (1-d)*1.6))
    return b

def pulse(t, c, s=0.02):
    d = (t-c+0.5) % 1 - 0.5
    return math.exp(-(d/s)**2) * math.sin(min(abs(d)/s, 3)*math.pi/1.5 + (math.pi/2 if d<0 else math.pi/2))

def frame_pose(t):
    T = 2*math.pi*t
    return dict(
        sway=0.55*math.sin(T),
        breath=math.sin(2*T - 0.6),
        head=1.9*math.sin(T - 0.55) + 0.5*math.sin(3*T + 0.4),
        earL=-(4*math.sin(2*T + 1.0) + 16*pulse(t, 0.44)),
        earR=4*math.sin(2*T + 2.3) + 16*pulse(t, 0.70) + 10*pulse(t, 0.77),
        bell=7*math.sin(T - 1.35) + 2.5*math.sin(3*T - 0.6),
        armL=0.7*math.sin(2*T - 1.2), armR=-0.7*math.sin(2*T - 1.5),
        tail=10*math.sin(2*T) + 4*math.sin(3*T + 1.1),
    )

def warp_coords(p, layer='body'):
    u, v = U.copy(), V.copy()
    u, v = rot_sample(u, v, 1.0, 308, 790, p['sway'])            # whole-body weight shift (from feet)
    if layer == 'tail':
        return rot_sample(u, v, 1.0, 388, 577, p['tail'])
    v = v + 0.0075*p['breath']*torsoLift*(1-wLegs*0)              # breathing: torso stretch, shoulders/arms/head lift
    u, v = rot_sample(u, v, wArmL, 257, 203, p['armL'])
    u, v = rot_sample(u, v, wArmR, 403, 203, p['armR'])
    u, v = rot_sample(u, v, wHead, 330, 152, p['head'])            # head tilt (overlaps body sway)
    u, v = rot_sample(u, v, wEarL*wHead, 279, 88, p['earL'])
    u, v = rot_sample(u, v, wEarR*wHead, 363, 66, p['earR'])
    u, v = rot_sample(u, v, wBell, 330, 157, p['bell'])
    return u, v

# ---- background ----
def make_bg():
    g = np.linspace(0, 1, CH)[:, None, None]
    top = np.array([255, 241, 236]); bot = np.array([246, 222, 228])
    bg = (top*(1-g) + bot*g) * np.ones((1, CW, 1))
    yy2, xx2 = np.mgrid[0:CH, 0:CW]
    glow = np.exp(-(((xx2-CW/2)/430)**2 + ((yy2-640)/520)**2))
    bg = bg*(1-0.35*glow[..., None]) + np.array([255, 252, 246])*0.35*glow[..., None]
    im = Image.fromarray(bg.astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)/255

BG = make_bg()
rng = np.random.default_rng(7)
PARTS = [(rng.uniform(0, CW), rng.uniform(0, CH), rng.uniform(3, 9), rng.integers(1, 3), rng.uniform(0, 1)) for _ in range(26)]
font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 26)

def shadow(p):
    im = Image.new('L', (CW, CH), 0); d = ImageDraw.Draw(im)
    cx = CW/2 + 6 + p['sway']*6; cy = OY + (790-Y0)*K - 8
    d.ellipse([cx-300, cy-34, cx+300, cy+34], fill=95)
    return np.asarray(im.filter(ImageFilter.GaussianBlur(22))).astype(np.float32)/255

def particles(t):
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (x, y, r, sp, ph) in PARTS:
        yy_ = (y - t*CH*sp) % (CH+60) - 30
        xx_ = x + 18*math.sin(2*math.pi*(t*sp + ph))
        al = int(120*(0.55+0.45*math.sin(2*math.pi*(2*t+ph))))
        d.ellipse([xx_-r, yy_-r, xx_+r, yy_+r], fill=(255, 255, 255, al))
    return im.filter(ImageFilter.GaussianBlur(1.2))

def render(i):
    t = i/N
    p = frame_pose(t)
    canvas = BG.copy()
    sh = shadow(p)[..., None]
    canvas = canvas*(1-0.22*sh) + np.array([0.45, 0.30, 0.35])*0.22*sh
    pim = np.asarray(particles(t)).astype(np.float32)/255
    canvas = canvas*(1-pim[..., 3:]) + pim[..., :3]*pim[..., 3:]
    src = blink_img(body, blink_amt(t))
    region = canvas[OY:OY+LH, OX:OX+LW]
    for layer, img in (('tail', tail), ('body', src)):
        u, v = warp_coords(p, layer)
        s = bilinear(img, (u-X0)*K, (v-Y0)*K)
        region[:] = region*(1-s[..., 3:]) + s[..., :3]
    out = Image.fromarray((np.clip(canvas, 0, 1)*255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    d.text((CW-40, CH-44), 'art: ARVANES', font=font, fill=(120, 95, 105), anchor='rs')
    return out

if MODE == 'preview':
    for i in [int(x) for x in sys.argv[2].split(',')]:
        render(i).save(f'prev_{i:03d}.png')
else:
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{CW}x{CH}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', sys.argv[2]], stdin=subprocess.PIPE)
    for i in range(N):
        ff.stdin.write(render(i).tobytes())
    ff.stdin.close(); ff.wait()
