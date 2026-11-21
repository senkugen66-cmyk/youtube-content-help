import numpy as np, wave, os
from scipy import signal
from timeline import *

SR = 48000
N = int(DUR * SR)
rng = np.random.default_rng(1111)
HERE = os.path.dirname(os.path.abspath(__file__))
t = np.arange(N) / SR
mix = np.zeros((N, 2))


def load(name):
    with wave.open(f"{HERE}/vo/{name}.wav") as wf:
        sr = wf.getframerate()
        x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(float) / 32768
    return signal.resample_poly(x, SR, sr)


def lp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2))
    return signal.lfilter(b, a, x)


def hp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, f1, f2, o=2):
    b, a = signal.butter(o, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def reverb(x, secs=1.2, wet=0.35, damp=4000, seed=0):
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    env = np.exp(-6.9 * np.arange(n) / n)
    irl = lp(r.standard_normal(n) * env, damp)
    irr = lp(r.standard_normal(n) * env, damp)
    irl /= np.sqrt((irl ** 2).sum()); irr /= np.sqrt((irr ** 2).sum())
    pad = np.concatenate([x, np.zeros(n)])
    L = signal.fftconvolve(pad, irl)[: len(pad)]
    R = signal.fftconvolve(pad, irr)[: len(pad)]
    dry = np.stack([pad, pad], 1)
    return dry * (1 - wet) + np.stack([L, R], 1) * wet * 1.4


def place(x, start, gain=1.0, pan=0.0):
    if x.ndim == 1:
        x = np.stack([x * (1 - max(pan, 0)), x * (1 + min(pan, 0))], 1)
    i = int(start * SR)
    j = min(N, i + len(x))
    mix[i:j] += x[: j - i] * gain


def env_points(pts):
    """piecewise-linear envelope over whole timeline: [(time, value), ...]"""
    ts, vs = zip(*pts)
    return np.interp(t, ts, vs)


# ---------------- drone bed ----------------
drone = (np.sin(2 * np.pi * 55 * t) + 0.8 * np.sin(2 * np.pi * 55.35 * t)
         + 0.5 * np.sin(2 * np.pi * 82.4 * t + 0.3) + 0.25 * np.sin(2 * np.pi * 110.7 * t))
drone *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t)
brown = np.cumsum(rng.standard_normal(N)); brown = hp(brown, 20); brown /= np.abs(brown).max()
air = lp(brown, 400) * 0.6
bed = drone * 0.05 + air * 0.25
bed_env = env_points([(0, 0), (2.5, 0.7), (13, 0.9), (17, 0.55), (21.5, 0.35), (26, 0.8), (34, 1.0),
                      (38.45, 1.3), (38.5, 0), (40, 0), (42, 0.5), (54, 0.7), (55, 1.1), (61, 0.8),
                      (62, 0.3), (66, 0.2), (68, 0)])
place(np.stack([bed * bed_env, np.roll(bed, 900) * bed_env], 1), 0)

# electrical hum of the clock (shots 1 and 3)
hum = (np.sin(2 * np.pi * 60 * t) * 0.4 + np.sin(2 * np.pi * 120 * t) * 0.2 + bp(rng.standard_normal(N), 900, 2400) * 0.05)
hum_env = env_points([(0, 0), (1, 0.12), (4.3, 0.12), (4.5, 0), (13, 0), (13.2, 0.16), (16.9, 0.16), (17.0, 0), (68, 0)])
place(hum * hum_env, 0)

# ---------------- clock flip blip ----------------
bt = np.arange(int(0.35 * SR)) / SR
blip = np.sin(2 * np.pi * 1320 * bt) * np.exp(-bt * 14) * 0.25
blip2 = np.sin(2 * np.pi * 990 * bt) * np.exp(-bt * 14) * 0.2
place(reverb(blip, 0.8, 0.3), FLIP)
place(reverb(blip2, 0.8, 0.3), FLIP + 0.12)
# low sub drop under the flip
st = np.arange(int(1.6 * SR)) / SR
sub = np.sin(2 * np.pi * (48 - 14 * st) * st) * np.exp(-st * 2.2) * 0.55
place(sub, FLIP)


# ---------------- knocks ----------------
def knock(seed):
    r = np.random.default_rng(seed)
    n = int(0.45 * SR); kt = np.arange(n) / SR
    f = 150 * np.exp(-kt * 9) + 62
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 22)
    wood = bp(r.standard_normal(n), 180, 1400) * np.exp(-kt * 55) * 1.6
    click = hp(r.standard_normal(n), 2500) * np.exp(-kt * 400) * 0.6
    k = np.tanh((body + wood + click) * 1.8)
    return reverb(k, 1.4, 0.38, 2500, seed)


for i, kt0 in enumerate(KNOCKS):
    place(knock(7 + i), kt0, 0.95)
# door rattle tails
for kt0 in KNOCKS:
    n = int(0.3 * SR); rt = np.arange(n) / SR
    rat = bp(rng.standard_normal(n), 2000, 5000) * (np.sin(2 * np.pi * 38 * rt) > 0.3) * np.exp(-rt * 14) * 0.07
    place(rat, kt0 + 0.02)

# ---------------- voices ----------------
def door_voice(x):
    x = signal.resample_poly(x, 50, 47)  # slower + lower (played at SR) -> uncanny
    x = lp(x, 1700, 3) * 1.6 + hp(lp(x, 3200), 250) * 0.15
    return reverb(x, 0.9, 0.3, 1800, 3)


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-9) * peak


for name, start, _, who in VO:
    x = load(name)
    if who == "VOICE OUTSIDE":
        place(door_voice(norm(x)), start, 0.62)
        # a second, barely audible layer a few cents off: something is not right
        y = signal.resample_poly(norm(x), 100, 97)
        place(reverb(lp(y, 900), 1.5, 0.6, 1200, 9), start + 0.03, 0.12, pan=0.4)
    elif who == "MARA":
        y = hp(norm(x), 300) * 0.7
        place(reverb(y, 0.6, 0.18), start, 0.45, pan=-0.15)
    elif who == "NARRATOR":
        y = norm(x)
        y = np.tanh(y * 1.4) / np.tanh(1.4)
        place(reverb(y + lp(y, 180) * 0.4, 1.6, 0.16, 5000, 4), start, 0.6)
    elif who == "DLI":
        y = bp(norm(x), 300, 3800, 3)
        place(reverb(y, 1.8, 0.32, 4000, 5), start, 0.55)

# ---------------- handle creak ----------------
t0, t1 = HANDLE_TURN
n = int((t1 - t0) * SR); ct = np.arange(n) / SR
grains = np.zeros(n)
pos = 0
while pos < n:
    gl = int(r := rng.uniform(0.008, 0.02) * SR)
    g = np.sin(2 * np.pi * rng.uniform(520, 760) * np.arange(gl) / SR) * np.hanning(gl)
    grains[pos:pos + gl] += g[: n - pos] * rng.uniform(0.4, 1)
    pos += int(rng.uniform(0.012, 0.045) * SR)
creak = bp(grains + rng.standard_normal(n) * 0.05, 300, 2200) * np.sin(np.pi * ct / ct[-1]) ** 0.5
place(reverb(creak * 0.35, 0.7, 0.3), t0)
# latch click at the end of the turn
lt = np.arange(int(0.2 * SR)) / SR
latch = hp(rng.standard_normal(len(lt)), 1500) * np.exp(-lt * 90) * 0.5 + np.sin(2 * np.pi * 300 * lt) * np.exp(-lt * 60) * 0.4
place(reverb(latch, 0.8, 0.3), t1)

# ---------------- riser + sting at the cut ----------------
rs, re_ = 34.2, CUT
n = int((re_ - rs) * SR); rt = np.arange(n) / SR; fr = rt / rt[-1]
riser = bp(rng.standard_normal(n), 200, 6000) * fr ** 2.5 * 0.18
riser += np.sin(2 * np.pi * np.cumsum(70 + 280 * fr ** 2) / SR) * fr ** 2 * 0.12
riser += np.sin(2 * np.pi * np.cumsum(73 + 300 * fr ** 2) / SR) * fr ** 2 * 0.1
place(riser, rs)


def boom(dur=4.0, f0=55, metal=True, seed=0):
    n = int(dur * SR); bt = np.arange(n) / SR
    b = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-bt * 0.6) + 22) / SR) * np.exp(-bt * 1.3)
    b += lp(np.random.default_rng(seed).standard_normal(n), 300) * np.exp(-bt * 6) * 1.5
    if metal:
        for f, a in [(431, .2), (587, .15), (912, .1), (1307, .07), (1733, .05)]:
            b += np.sin(2 * np.pi * f * bt) * np.exp(-bt * 1.6) * a
    return reverb(np.tanh(b * 1.5), 3.0, 0.4, 3000, seed)


place(boom(4.5, 60, True, 2), CUT, 0.75)

# ---------------- title hit + reverse swell ----------------
sw = boom(2.2, 70, True, 6)[:, 0][::-1][-int(1.6 * SR):]
place(sw * np.linspace(0, 1, len(sw)) ** 2 * 0.4, TITLE_HIT - 1.6)
place(boom(5.0, 50, True, 8), TITLE_HIT, 0.7)

# glitch crackles on title reveal
for k in range(10):
    s = TITLE_HIT + rng.uniform(0, 0.8)
    gl = int(rng.uniform(0.01, 0.05) * SR)
    place(hp(rng.standard_normal(gl), 3000) * 0.08, s, pan=rng.uniform(-.6, .6))

# ---------------- DLI corporate chime ----------------
ct = np.arange(int(1.6 * SR)) / SR
def tone(f):
    return (np.sin(2 * np.pi * f * ct) + 0.3 * np.sin(4 * np.pi * f * ct)) * np.exp(-ct * 3)
chime = np.zeros(int(2.2 * SR))
chime[: len(ct)] += tone(659.3); chime[int(.28 * SR): int(.28 * SR) + len(ct)] += tone(523.3)
chime[int(.56 * SR): int(.56 * SR) + len(ct)] += tone(392.0) * 1.1
place(reverb(chime * 0.12, 2.0, 0.4), DLI_CHIME - 0.2)

# ---------------- master ----------------
fade = env_points([(0, 0), (0.3, 1), (DUR - 1.5, 1), (DUR, 0)])
mix *= fade[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.89
out = (mix * 32767).astype(np.int16)
with wave.open(f"{HERE}/audio.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(out.tobytes())
print("audio ok", out.shape[0] / SR)
