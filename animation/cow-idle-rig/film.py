"""16:9 cinematic version: camera tilt-up reveal, clovers, gold light trail, sparkles."""
import os, sys, math, subprocess
os.environ['MOVES_K'] = '3.0'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import moves as M

W, H, FPS, DUR = 1280, 720, 24, 10.0
N = int(FPS*DUR)
TAU = 2*math.pi
def ease(a, b, t):
    x = min(max((t-a)/(b-a), 0), 1); return x*x*x*(x*(6*x-15)+10)
def lerp(a, b, k): return a + (b-a)*k

# ---------------- character performance ----------------
def pose(t):
    T = TAU*t/5.0              # slow idle cycle
    p = dict(sway=0.5*math.sin(T), breath=math.sin(TAU*t/3 - 0.6),
             head=1.8*math.sin(T - 0.55) + 0.5*math.sin(3*T + 0.4),
             earL=-(4*math.sin(TAU*t/2.5 + 1.0)), earR=4*math.sin(TAU*t/2.5 + 2.3),
             bell=6*math.sin(T - 1.35) + 2*math.sin(TAU*t/1.7),
             armL=0.6*math.sin(TAU*t/3 - 1.2), armR=-0.6*math.sin(TAU*t/3 - 1.5),
             tail=10*math.sin(TAU*t/2.5) + 4*math.sin(TAU*t/1.6 + 1.1),
             blink=M.blink_at(t, [2.1, 4.6, 4.85, 9.55], 0.09))
    # ear flick as the camera arrives at the face
    for c, a in ((3.05, 15), (3.25, -8)):
        d = (t-c)/0.09
        if abs(d) < 3: p['earR'] += a*math.exp(-d*d); p['earL'] -= a*0.6*math.exp(-(d-0.5)**2)
    # shy beat near the end
    env = ease(6.4, 7.0, t)*(1-ease(9.0, 9.8, t))
    p['earL'] += -13*env; p['earR'] += 13*env
    p['head'] += -4*env; p['headDrop'] = 2*env
    p['shrug'] = -3.2*ease(6.5, 6.8, t)*(1-0.5*ease(6.8, 7.4, t))*(1-ease(9.0, 9.6, t))
    p['glance'] = -2.0*ease(6.5, 6.8, t)*(1-ease(8.8, 9.3, t))
    p['blush'] = ease(6.7, 7.6, t)*(1-ease(9.2, 10.0, t))
    if t > 6.6: p['bell'] += 7*math.exp(-(t-6.6)*2.8)*math.sin(TAU*1.7*(t-6.6))
    return p

def character(p):
    """premultiplied RGBA layer of the posed character (layer pixel space)."""
    layer = np.zeros((M.LH, M.LW, 4), np.float32)
    tu, tv = M.coords(p, 0.0, M.TREG)
    layer[M.TREG] = M.bilinear(M.tail, (tu-M.X0)*M.K, (tv-M.Y0)*M.K)
    src = M.face(M.body, p.get('blink', 0), p.get('glance', 0), p.get('blush', 0))
    u, v = M.coords(p, 0.0)
    s = M.bilinear(src, (u-M.X0)*M.K, (v-M.Y0)*M.K)
    layer = layer*(1-s[..., 3:]) + s
    return layer

# ---------------- camera (original-image coords: centre + visible height) ----------------
def camera(t):
    a = (312, 690, 300)          # shoes / socks
    b = (322, 140, 215)          # face close-up
    c = (322, 265, 440)          # head to thighs
    d = (322, 245, 395)          # slow push-in
    if t < 0.6: k = a
    elif t < 3.2:
        e = ease(0.6, 3.2, t); k = tuple(lerp(a[i], b[i], e) for i in range(3))
    elif t < 4.6:
        e = ease(3.6, 4.6, t); k = tuple(lerp(b[i], c[i], e) for i in range(3))
    else:
        e = ease(4.6, 10.0, t); k = tuple(lerp(c[i], d[i], e) for i in range(3))
    # gentle handheld drift
    return k[0] + 1.5*math.sin(TAU*t/4.3), k[1] + 1.2*math.sin(TAU*t/3.7 + 1), k[2]

# ---------------- background & effects ----------------
def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cream = np.array([255, 249, 236]); mint = np.array([226, 240, 214]); warm = np.array([255, 233, 196])
    g = np.clip((x/W*0.6 + y/H*0.6) - 0.1, 0, 1)[..., None]
    bg = cream*(1-g) + mint*g
    glow = np.exp(-(((x-180)/420)**2 + ((y-90)/330)**2))[..., None]
    bg = bg*(1-0.55*glow) + warm*0.55*glow
    centre = np.exp(-(((x-W/2)/360)**2 + ((y-H/2)/420)**2))[..., None]
    bg = bg*(1-0.4*centre) + np.array([255, 253, 248])*0.4*centre
    return bg.astype(np.float32)/255
BG = make_bg()

def clover_sprite(size, col):
    S = size*4
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = S/2; r = S*0.15
    dark = tuple(int(c*0.72) for c in col)
    for k in range(4):
        ang = TAU*k/4 + TAU/8
        lx, ly = cx + math.cos(ang)*S*0.2, cy + math.sin(ang)*S*0.2
        # heart-shaped leaf: two lobes + point toward centre
        for s in (-1, 1):
            ox = lx + math.cos(ang + s*TAU/4)*r*0.62 + math.cos(ang)*r*0.25
            oy = ly + math.sin(ang + s*TAU/4)*r*0.62 + math.sin(ang)*r*0.25
            d.ellipse([ox-r, oy-r, ox+r, oy+r], fill=col+(255,))
        tipx, tipy = cx + math.cos(ang)*S*0.02, cy + math.sin(ang)*S*0.02
        p1 = (lx + math.cos(ang + TAU/4)*r*1.45, ly + math.sin(ang + TAU/4)*r*1.45)
        p2 = (lx + math.cos(ang - TAU/4)*r*1.45, ly + math.sin(ang - TAU/4)*r*1.45)
        d.polygon([p1, p2, (tipx, tipy)], fill=col+(255,))
        d.line([(cx, cy), (lx + math.cos(ang)*r*0.6, ly + math.sin(ang)*r*0.6)], fill=dark+(255,), width=max(1, S//60))
    d.line([(cx, cy), (cx + S*0.08, cy + S*0.42)], fill=dark+(255,), width=max(2, S//28))
    return im.resize((size, size), Image.LANCZOS)

rng = np.random.default_rng(11)
GREENS = [(88, 178, 92), (110, 196, 104), (70, 156, 84), (128, 204, 120)]
CLOVERS = []
for i in range(30):
    depth = rng.uniform(0.3, 1.0)
    front = (i % 9 == 0)
    xx_ = rng.choice([rng.uniform(-30, 260), rng.uniform(W-260, W+30)]) if front else rng.uniform(-40, W+40)
    CLOVERS.append(dict(x=xx_, y=rng.uniform(-60, H+60), depth=depth,
                        size=int(26 + 40*depth), spin=rng.uniform(-60, 60), rot0=rng.uniform(0, 360),
                        fall=rng.uniform(18, 40)*depth, wob=rng.uniform(0, 1),
                        sprite=clover_sprite(int(26 + 40*depth)*2, GREENS[i % 4]), front=front))
SPARK = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, 1), rng.uniform(4, 11)) for _ in range(40)]
BOKEH = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 14), rng.uniform(0, 1)) for _ in range(46)]

def star(d, x, y, r, a, col):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r*0.22
        ang = TAU*k/8
        pts.append((x + math.cos(ang)*rr, y + math.sin(ang)*rr))
    d.polygon(pts, fill=col+(int(a),))

def draw_clovers(t, cam_dy, front):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for c in CLOVERS:
        if c['front'] != front: continue
        y = (c['y'] + c['fall']*t - cam_dy*0.5*c['depth']) % (H+140) - 70
        x = c['x'] + 22*c['depth']*math.sin(TAU*(t/5 + c['wob']))
        spr = c['sprite'].rotate(c['rot0'] + c['spin']*t, resample=Image.BICUBIC)
        s = c['size'] if not front else int(c['size']*2.2)
        spr = spr.resize((s, s), Image.LANCZOS)
        if front: spr = spr.filter(ImageFilter.GaussianBlur(4))
        elif c['depth'] < 0.5: spr = spr.filter(ImageFilter.GaussianBlur(1.6))
        if not front:
            a = np.asarray(spr).copy(); a[..., 3] = (a[..., 3]*(0.55 + 0.45*c['depth'])).astype(np.uint8); spr = Image.fromarray(a)
        im.alpha_composite(spr, (int(x - s/2), int(y - s/2)))
    return im

def gold_trail(t):
    """glowing particle ribbon sweeping an ellipse around the character between 4.8 s and 8.4 s."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if not (4.8 < t < 8.6): return im, im
    back = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    db, df = ImageDraw.Draw(back), ImageDraw.Draw(im)
    head = (t-4.8)/3.2
    fade = ease(4.8, 5.2, t)*(1-ease(8.0, 8.6, t))
    for i in range(130):
        q = head - i*0.0045
        if q < 0: break
        ang = TAU*(0.62 + 1.15*q)
        x = W/2 + 330*math.cos(ang); y = H*0.56 + 120*math.sin(ang) - 160*q
        k = (1 - i/130)**1.3
        r = 1.5 + 6.5*k
        dd = df if math.sin(ang) > 0 else db       # lower half of the ellipse passes in front
        dd.ellipse([x-r, y-r, x+r, y+r], fill=(255, 210, 110, int(255*k*fade)))
        if i % 3 == 0:
            jx, jy = x + rng.normal(0, 9), y + rng.normal(0, 9)
            dd.ellipse([jx-1.5, jy-1.5, jx+1.5, jy+1.5], fill=(255, 236, 170, int(200*k*fade)))
    def glow(x):
        g1 = x.filter(ImageFilter.GaussianBlur(14)); g2 = x.filter(ImageFilter.GaussianBlur(5))
        return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(g1, g1), g2), x)
    im = glow(im); back = glow(back)
    return back, im

def over(canvas, im):
    a = np.asarray(im).astype(np.float32)/255
    return canvas*(1-a[..., 3:]) + a[..., :3]*a[..., 3:]

def frame(i):
    t = i/FPS
    cx, cy, vh = camera(t)
    vw = vh*W/H
    canvas = BG.copy()
    cam_dy = (cy - 400)*(H/vh)*0.25
    fx = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fx)
    for (x, y, r, ph) in BOKEH:
        yy = (y - 10*t - cam_dy*0.2) % H
        a = 40 + 40*math.sin(TAU*(t/3 + ph))
        d.ellipse([x-r, yy-r, x+r, yy+r], fill=(255, 226, 160, int(a)))
    fx = fx.filter(ImageFilter.GaussianBlur(2.5))
    canvas = over(canvas, fx)
    canvas = over(canvas, draw_clovers(t, cam_dy, False))
    back, frontt = gold_trail(t)
    canvas = over(canvas, back)
    # character through the camera
    layer = character(pose(t))
    lx0 = (cx - vw/2 - M.X0)*M.K; ly0 = (cy - vh/2 - M.Y0)*M.K
    lx1 = (cx + vw/2 - M.X0)*M.K; ly1 = (cy + vh/2 - M.Y0)*M.K
    pim = Image.fromarray((np.clip(layer, 0, 1)*255).astype(np.uint8), 'RGBA')
    view = pim.transform((W, H), Image.EXTENT, (lx0, ly0, lx1, ly1), resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
    v = np.asarray(view).astype(np.float32)/255
    canvas = canvas*(1-v[..., 3:]) + v[..., :3]
    canvas = over(canvas, frontt)
    sp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sp)
    for (x, y, ph, r) in SPARK:
        tw = max(0, math.sin(TAU*(t/1.6 + ph)))**3
        if tw > 0.02: star(d, x, (y - 6*t) % H, r*(0.5 + 0.5*tw), 220*tw, (255, 244, 214) if ph > 0.3 else (226, 206, 255))
    canvas = over(canvas, sp)
    canvas = over(canvas, draw_clovers(t, cam_dy, True))
    # soft vignette + fade from white at the start
    out = np.clip(canvas, 0, 1)
    wf = 1 - ease(0.0, 0.5, t)
    out = out*(1-wf) + wf
    img = Image.fromarray((out*255).astype(np.uint8))
    ImageDraw.Draw(img).text((W-24, H-22), 'art: ARVANES', fill=(120, 105, 95), anchor='rs',
                             font=M.ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Medium.otf', 18))
    return img

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        for f in [int(x) for x in sys.argv[2].split(',')]: frame(f).save(f'film_{f:03d}.png')
        sys.exit()
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a, b): ff.stdin.write(frame(i).tobytes())
    ff.stdin.close(); ff.wait()
