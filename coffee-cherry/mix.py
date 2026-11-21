# score (felt piano + kalimba) + foley (brush, pen, mist, birds) + narration → out/mix.wav (48 kHz stereo)
# usage: LIB=<library> $LIB/.venv/bin/python mix.py      (reads events.json written by core/render/events.mjs)
import json, os, sys, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.environ['LIB']
sys.path.insert(0, LIB)
from core.audio import sampler as S, pluck as P
from core.audio.sfx import SR, bp, lp, hp, add, compress, limit
from scipy.signal import resample_poly

E = json.load(open(os.path.join(HERE, 'events.json'))); DUR = E['dur']; EV = E['ev']; N = int(DUR * SR) + SR
rng = np.random.default_rng(7); S.seed(7)
def noise(n): return rng.standard_normal(n)
def pink(n):
    w = np.fft.rfft(noise(n)); f = np.arange(len(w)); f[0] = 1
    return np.fft.irfft(w / np.sqrt(f), n)
def norm(x, p=1.0): return x / (np.abs(x).max() + 1e-9) * p
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)

# ---------- music: 72 bpm, D major ----------
B = 60 / 72
score = [
    # bar 1: a soft open Dmaj9, rolled
    (0.15, 'piano', 'D3', 3.2, .32, -.25), (0.25, 'piano', 'A3', 3.1, .28, -.1), (0.38, 'piano', 'F#4', 3.0, .26, .1), (0.52, 'piano', 'E5', 2.9, .22, .25),
    # bar 2 → Gmaj7 under the ripening
    (3.33, 'piano', 'G2', 2.6, .30, -.25), (3.43, 'piano', 'D4', 2.5, .24, -.05), (3.55, 'piano', 'F#4', 2.4, .24, .1), (3.68, 'piano', 'B4', 2.3, .22, .25),
    # bar 3: Bm7 → A, held
    (5.83, 'piano', 'B2', 1.8, .26, -.25), (5.93, 'piano', 'F#4', 1.7, .2, .05), (6.05, 'piano', 'A4', 1.6, .2, .2),
    (6.67, 'piano', 'A2', 1.0, .24, -.2), (6.77, 'piano', 'E4', 0.9, .18, .1), (6.89, 'piano', 'C#5', 0.8, .17, .25),
    # bar 4: home to D as the page mists away, let it ring
    (7.50, 'piano', 'D2', 3.2, .30, -.2), (7.60, 'piano', 'A3', 3.0, .24, -.05), (7.72, 'piano', 'F#4', 2.9, .22, .1), (7.86, 'piano', 'D5', 2.8, .2, .2),
]
mus = S.render(score, dur=N / SR, master=False)[:N]
# kalimba: one tine per cherry cluster appearing, one per cluster turning red, two for the title
kal = np.zeros((N, 2))
dab_p = ['D5', 'E5', 'F#5', 'A5', 'B5']; rip_p = ['A5', 'F#5', 'B5', 'D6', 'E6']
for e in EV:
    if e['type'] == 'dab': add(kal, P.pluck('kalimba', dab_p[e['node']], None, vel=.45), e['t'], .5, -.4 + .2 * e['node'])
    if e['type'] == 'ripen': add(kal, P.pluck('kalimba', rip_p[e['node']], None, vel=.35), e['t'], .38, .4 - .2 * e['node'])
    if e['type'] == 'hero': add(kal, P.pluck('kalimba', 'F#6', None, vel=.4), e['t'], .4, 0)
    if e['type'] == 'title':
        add(kal, P.pluck('kalimba', 'A5', None, vel=.4), e['t'] + .05, .45, -.15); add(kal, P.pluck('kalimba', 'D6', None, vel=.38), e['t'] + .05 + B, .42, .15)
music = mus + kal * .9
music = S.room(music.astype(np.float32), size=.5, mix=.24)

# ---------- foley ----------
fx = np.zeros((N, 2))
def brush(d, g, pan0=-.5, pan1=.5):
    n = int(d * SR); p = np.arange(n) / n
    x = bp(noise(n), 1500, 7000) * (.6 + .4 * np.abs(np.sin(np.arange(n) / SR * 2 * np.pi * 9))) + bp(pink(n) * 20, 300, 1500) * .5
    y = norm(x * np.sin(np.pi * p) ** .8, .5) * g; pan = pan0 + (pan1 - pan0) * p
    return np.stack([y * np.cos((pan + 1) * np.pi / 4) * 1.414, y * np.sin((pan + 1) * np.pi / 4) * 1.414], 1)
def put(buf, t, x):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i]
def dab(g):  # a wet brush touch
    n = int(.18 * SR); t = np.arange(n) / SR
    x = bp(noise(n), 800, 4000) * np.exp(-t * 28) * np.minimum(1, t / .01)
    return norm(x, .5) * g
def pen(d, g):  # pencil/pen scratch: band-passed noise in short bursts
    n = int(d * SR); t = np.arange(n) / SR
    burst = (np.sin(2 * np.pi * 7.5 * t) > -.2) * (.6 + .4 * np.sin(2 * np.pi * 23 * t) ** 2)
    x = bp(noise(n), 2500, 9000) * lp(burst.astype(float), 60)
    return norm(x * np.maximum(0, np.sin(np.pi * t / t[-1])) ** .6, .4) * g
def mist(d, g):  # a soft rising breath
    n = int(d * SR); t = np.arange(n) / SR; p = t / t[-1]
    x = np.stack([lp(pink(n), 900), lp(pink(n), 900)], 1) * 20
    return norm(x * (np.maximum(0, np.sin(np.pi * p)) ** 1.4)[:, None], .5) * g
for e in EV:
    pan = rng.uniform(-.5, .5)
    if e['type'] == 'brush': put(fx, e['t'], brush(e['d'], .32, pan - .3, pan + .3))
    if e['type'] == 'dab':
        for k in range(3): put(fx, e['t'] + k * .07, np.stack([dab(.2)] * 2, 1) * [1 + pan, 1 - pan])
    if e['type'] == 'pen': put(fx, e['t'], np.stack([pen(e['d'], .16)] * 2, 1) * [.8, 1.2])
    if e['type'] == 'mist': put(fx, e['t'] - .2, mist(e['d'] + .8, .22))
# a quiet morning bed: air + a few distant birds, gone with the mist
bed = np.stack([lp(pink(N), 500), lp(pink(N), 500)], 1) * 20
bed = norm(bed, .06)
def chirp(g, f0):
    n = int(.11 * SR); t = np.arange(n) / SR; f = f0 * (1 + .25 * np.sin(2 * np.pi * 30 * t)) * (1 - .3 * t / t[-1])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) ** 2 * g
for k in range(9):
    tt = 1.2 + k * .72 + rng.uniform(-.2, .2); p = rng.uniform(-.8, .8); c = chirp(.035, rng.uniform(2800, 4200))
    put(bed, tt, np.stack([c * (1 - p), c * (1 + p)], 1)); put(bed, tt + .14, np.stack([c * (1 - p), c * (1 + p)], 1) * .7)
env = np.ones(N); i0, i1 = int(7.4 * SR), int(8.8 * SR); env[i0:i1] = np.linspace(1, .15, i1 - i0); env[i1:] = .15
fx += bed * env[:, None]

# ---------- voice ----------
vo = np.zeros((N, 2))
for e in EV:
    if e['type'] != 'vo': continue
    x, sr = sf.read(os.path.join(HERE, 'voices', e['id'] + '.wav'))
    if x.ndim > 1: x = x.mean(1)
    x = resample_poly(x, SR, sr)
    x = compress(hp(x, 80) / (np.abs(x).max() + 1e-9) * .9, thr=.22, ratio=3.2)
    put(vo, e['t'], np.stack([x, x], 1))
vmask = (np.abs(vo[:, 0]) > 1e-4).astype(float)
duck = 1 - .37 * np.clip(np.convolve(vmask, np.ones(int(.35 * SR)) / int(.35 * SR), 'same') * 3, 0, 1)   # ≈ −4 dB under voice

# ---------- balance: voice ≈ 10 dB over the music where it speaks ----------
sp = vmask > 0
music *= 10 ** ((rms_db(vo[sp]) - 10 - rms_db(music[sp])) / 20)
# once the voice is done the music comes forward (+5 dB) for the ending
lift = 1 + (10 ** (5 / 20) - 1) * np.clip((np.arange(N) / SR - 5.6) / 1.2, 0, 1)
fxduck = 1 - .6 * np.clip(np.convolve(vmask, np.ones(int(.35 * SR)) / int(.35 * SR), 'same') * 3, 0, 1)   # foley ≈ −8 dB under voice
mix = vo + music * (duck * lift)[:, None] + fx * fxduck[:, None]
fade_n = int(.6 * SR); mix = mix[:int(DUR * SR)]; mix[-fade_n:] *= np.linspace(1, 0, fade_n)[:, None] ** 1.5
mix = limit(mix / (np.abs(mix).max() + 1e-9) * .8, ceil=.9)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
print('mix.wav', round(len(mix) / SR, 2), 's')
