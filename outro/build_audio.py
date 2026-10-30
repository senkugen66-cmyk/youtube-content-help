"""Builds the outro soundtrack: squeaky MEOW + absurdly deep DUDE + a few tiny cartoon sfx.

Voices start from neural TTS takes (Piper) saved in assets/voice_src/, then get mangled:
  MEOW  - formant-preserving pitch-up, then a tape-speed warp that swoops UP into the "EEE",
          holds, and wobbles down on the "-ow" (~650 -> 1000 -> 500 Hz, kitten territory).
  DUDE  - the "uuu" is stretched on its own (consonants stay crisp), then the whole thing is
          played back at ~0.55x speed and sags even slower as it runs out of breath (~50 Hz),
          with a bit of throat grit, chest boost and a small room.

Usage:  python3 build_audio.py            -> output/meow.wav, output/dude.wav, output/outro_audio.wav
        python3 build_audio.py --regen-tts  (re-roll the raw TTS takes; needs `pip install piper-tts`)
"""
import os, subprocess, sys, urllib.request
import numpy as np
import soundfile as sf
from timeline import SR, DURATION, T_WIGGLE, T_MEOW, T_POP, T_DUDE, T_BOUNCE

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "voice_src")
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "output")

# --- raw takes -------------------------------------------------------------------------------
VOICES = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/"
TAKES = {
    # name: (voice path, speaker, phonemes, length_scale)
    "meow_take": ("lessac/high/en_US-lessac-high", 0, "[[ mˈiːːaʊ ]]", 2.0),
    "dude_take": ("libritts_r/medium/en_US-libritts_r-medium", 3, "[[ dˈuːːːd ]]", 2.2),
}

def regen_tts():
    cache = os.path.join(HERE, ".cache", "voices"); os.makedirs(cache, exist_ok=True)
    for name, (voice, spk, text, ls) in TAKES.items():
        model = os.path.join(cache, os.path.basename(voice) + ".onnx")
        for ext in (".onnx", ".onnx.json"):
            if not os.path.exists(model[:-5] + ext):
                urllib.request.urlretrieve(VOICES + voice + ext, model[:-5] + ext)
        subprocess.run(["piper", "-m", model, "-s", str(spk), "--length-scale", str(ls),
                        "-f", os.path.join(SRC, name + ".wav")], input=text.encode(), check=True)

# --- dsp helpers -----------------------------------------------------------------------------
def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)

def ff(x, af):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", af, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode())
    return np.frombuffer(p.stdout, np.float32).astype(np.float64)

def trim(x, th=0.01, pad=0.01):
    i = np.where(np.abs(x) > th * np.abs(x).max())[0]
    return x[max(0, i[0] - int(pad * SR)):min(len(x), i[-1] + int(pad * SR))]

def warp(x, rate_fn):
    """Variable-speed playback (tape-style): pitch, formants and speed move together."""
    pos, out, n = 0.0, [], len(x)
    while pos < n - 1:
        out.append(pos); pos += rate_fn(pos / n)
    return np.interp(np.array(out), np.arange(n), x)

def stretch_vowel(x, factor, lo=0.22, hi=0.72, xf=0.012):
    """Time-stretch only the steady middle of the voiced region (the 'uuu'), keeping consonants crisp."""
    env = np.convolve(np.abs(x), np.ones(int(0.02 * SR)) / int(0.02 * SR), "same")
    v = np.where(env > 0.25 * env.max())[0]; a0, a1 = v[0], v[-1]
    a, b, n = int(a0 + lo * (a1 - a0)), int(a0 + hi * (a1 - a0)), int(xf * SR)
    mid = ff(x[a - n:b + n], f"rubberband=tempo={1 / factor}:transients=smooth:window=long")
    ramp = np.linspace(0, 1, n)
    return np.concatenate([x[:a - n], x[a - n:a] * (1 - ramp) + mid[:n] * ramp, mid[n:-n],
                           mid[-n:] * (1 - ramp) + x[b:b + n] * ramp, x[b + n:]])

def fade(x, a=0.006, b=0.03):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    x[:na] *= np.linspace(0, 1, na); x[-nb:] *= np.linspace(1, 0, nb) ** 2
    return x

def norm(x, peak=0.89): return x / np.abs(x).max() * peak

# --- the two voices --------------------------------------------------------------------------
def make_meow():
    x = trim(load(os.path.join(SRC, "meow_take.wav")))
    x = ff(x, "rubberband=tempo=0.55:pitch=2.1:formant=preserved:transients=smooth")
    base, peak = 1.5, 1.9
    def rate(u):
        up = np.clip((u - 0.05) / 0.3, 0, 1); dn = np.clip((u - 0.62) / 0.38, 0, 1)
        r = base + (peak - base) * np.sin(up * np.pi / 2) ** 2 - (peak - base) * 0.45 * dn
        return r * (1 + 0.05 * np.sin(2 * np.pi * u * 9) * dn)      # little kitten wobble on the "-ow"
    y = warp(x, rate)
    y = ff(y, "highpass=f=320,equalizer=f=3500:t=q:w=1.2:g=4,"
              "acompressor=threshold=0.2:ratio=3:attack=3:release=60")
    return fade(norm(y))

def make_dude():
    x = trim(load(os.path.join(SRC, "dude_take.wav")))
    x = stretch_vowel(x, 2.0)
    y = warp(x, lambda u: 0.6 - 0.08 * u)                            # slow-mo, sagging as it goes
    y = norm(y); y = 0.65 * y + 0.35 * np.tanh(2.4 * y)              # throat grit
    y = ff(y, "highpass=f=32,lowshelf=f=110:g=6,equalizer=f=1000:t=q:w=1:g=3,lowpass=f=7500,"
              "aecho=0.85:0.5:45|95:0.2|0.1,acompressor=threshold=0.25:ratio=4:attack=5:release=120")
    return fade(norm(y), b=0.08)

# --- tiny cartoon sfx (synthesised, deliberately cheap-sounding) ------------------------------
def tone(freq_fn, dur, env_fn, harm=(1.0,)):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * np.cumsum(freq_fn(t)) / SR
    return sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harm)) * env_fn(t)

def sfx_blip():
    one = tone(lambda t: 1300 + 9000 * t, 0.05, lambda t: np.sin(np.pi * t / 0.05) ** 2)
    gap = np.zeros(int(0.035 * SR))
    return 0.22 * np.concatenate([one, gap, one * 0.8])

def sfx_pop():
    p = tone(lambda t: 240 + 1100 * (t / 0.06), 0.07, lambda t: np.exp(-t / 0.025), harm=(1, 0.3))
    p[:int(0.004 * SR)] += np.random.default_rng(7).normal(0, 0.6, int(0.004 * SR))
    return 0.55 * p

def sfx_thump():
    return 0.55 * tone(lambda t: 62 - 25 * t, 0.35, lambda t: np.minimum(t / 0.004, 1) * np.exp(-t / 0.09))

def sfx_boing():
    f = lambda t: 210 * (1 + 0.6 * t) * (1 + 0.22 * np.exp(-7 * t) * np.sin(2 * np.pi * 15 * t))
    return 0.28 * tone(f, 0.7, lambda t: np.minimum(t / 0.005, 1) * np.exp(-t / 0.13), harm=(1, 0.45, 0.2))

def place(bus, clip, t):
    i = int(t * SR); bus[i:i + len(clip)] += clip[:len(bus) - i]

def onset(x, th=0.3):
    """Seconds until the voice really kicks in (envelope crosses th of its max)."""
    env = np.convolve(np.abs(x), np.ones(int(0.02 * SR)) / int(0.02 * SR), "same")
    return np.argmax(env > th * env.max()) / SR

def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 0.05 * np.abs(x).max()] ** 2))

def main():
    if "--regen-tts" in sys.argv: regen_tts()
    os.makedirs(BUILD, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    meow, dude = make_meow(), make_dude()
    sf.write(os.path.join(OUT, "meow.wav"), meow.astype(np.float32), SR)
    sf.write(os.path.join(OUT, "dude.wav"), dude.astype(np.float32), SR)

    bus = np.zeros(int(DURATION * SR))
    place(bus, meow * 0.30 / rms(meow), T_MEOW)
    place(bus, dude * 0.36 / rms(dude), T_DUDE)      # the punchline gets to be a bit louder
    place(bus, fade(sfx_blip(), b=0.01), T_WIGGLE)
    place(bus, fade(sfx_pop(), a=0, b=0.03), T_POP)
    place(bus, fade(sfx_thump(), a=0, b=0.1), T_DUDE + onset(dude) - 0.01)
    place(bus, fade(sfx_boing(), a=0, b=0.2), T_BOUNCE)
    raw = os.path.join(BUILD, "mix_raw.wav")
    sf.write(raw, bus.astype(np.float32), SR)

    # two-pass loudness to YouTube-ish level, mono voice in a stereo file
    meas = subprocess.run(["ffmpeg", "-v", "info", "-i", raw, "-af",
                           "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    import json
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = ("loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
          f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']},alimiter=limit=0.84")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), "-ac", "2",
                    os.path.join(OUT, "outro_audio.wav")], check=True)
    print("meow %.2fs  dude %.2fs  -> output/outro_audio.wav" % (len(meow) / SR, len(dude) / SR))

if __name__ == "__main__":
    main()
