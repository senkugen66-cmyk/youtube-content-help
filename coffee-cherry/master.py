# Loudness master without ffmpeg 7: BS.1770 integrated loudness → −14 LUFS, then a 4× oversampled
# true-peak limiter at −1.2 dBTP. out/mix.wav → out/master.wav.   usage: $LIB/.venv/bin/python master.py
import os, numpy as np, soundfile as sf
from scipy.signal import lfilter, resample_poly
HERE = os.path.dirname(os.path.abspath(__file__))
x, sr = sf.read(os.path.join(HERE, 'out', 'mix.wav')); assert sr == 48000
def kweight(y):  # ITU-R BS.1770 K-weighting at 48 kHz (high shelf + RLB high-pass)
    y = lfilter([1.53512485958697, -2.69169618940638, 1.19839281085285], [1, -1.69065929318241, 0.73248077421585], y, axis=0)
    return lfilter([1.0, -2.0, 1.0], [1, -1.99004745483398, 0.99007225036621], y, axis=0)
def lufs(y):
    k = kweight(y); blk, hop = int(.4 * sr), int(.1 * sr)
    ms = np.array([(k[i:i + blk] ** 2).mean(0).sum() for i in range(0, len(k) - blk + 1, hop)])
    L = -.691 + 10 * np.log10(ms + 1e-12); ms = ms[L > -70]
    rel = -.691 + 10 * np.log10(ms.mean()) - 10
    ms = ms[-.691 + 10 * np.log10(ms) > rel]
    return -.691 + 10 * np.log10(ms.mean())
def tp(y): return 20 * np.log10(np.abs(resample_poly(y, 4, 1, axis=0)).max())
def tp_limit(y, ceil_db=-1.2, look=.005, rel=.08):
    up = resample_poly(y, 4, 1, axis=0); c = 10 ** (ceil_db / 20)
    pk = np.abs(up).max(1).reshape(-1, 4).max(1) if len(up) % 4 == 0 else np.abs(up[:len(y) * 4]).max(1).reshape(-1, 4).max(1)
    g = np.minimum(1, c / np.maximum(pk, 1e-9))
    n = int(look * sr); g = np.array([g[max(0, i - n):i + n + 1].min() for i in range(len(g))]) if n else g   # look-ahead (min over window)
    a = np.exp(-1 / (rel * sr)); out = g.copy()
    for i in range(1, len(g)): out[i] = min(g[i], a * out[i - 1] + (1 - a) * g[i])
    return y * out[:, None]
L0 = lufs(x); y = x * 10 ** ((-14 - L0) / 20)
for _ in range(4):
    y = tp_limit(y)
    L = lufs(y); y *= 10 ** ((-14 - L) / 20)
    if tp(y) <= -1.0: break
y = tp_limit(y, -1.3)
print(f'in {L0:.1f} LUFS → out {lufs(y):.2f} LUFS, true peak {tp(y):.2f} dBTP')
sf.write(os.path.join(HERE, 'out', 'master.wav'), y.astype(np.float32), sr, subtype='PCM_24')
