import wave, sys, os
from piper import PiperVoice
from piper.config import SynthesisConfig
V=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices/')
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vo/')
lines = {
 'dad1': ('en_GB-alan-medium', "Alex? ... It's Dad.", 1.25),
 'mara1': ('en_US-lessac-medium', "Don't.", 1.1),
 'dad2': ('en_GB-alan-medium', "Alex, please. ... I've been looking for you.", 1.25),
 'narr1': ('en_US-ryan-high', "In Bellwether, everyone follows one rule.", 1.2),
 'narr2': ('en_US-ryan-high', "At exactly eleven eleven P.M., you never open your front door.", 1.2),
 'narr3': ('en_US-ryan-high', "Not for your friends. ... Not for your family.", 1.2),
 'narr4': ('en_US-ryan-high', "And especially... not for someone you thought was gone.", 1.3),
 'dli': ('en_US-lessac-medium', "Durren Laggan Incorporated. Your home. Our responsibility.", 1.05),
}
cache={}
for k,(m,t,ls) in lines.items():
    v = cache.get(m) or PiperVoice.load(V+m+'.onnx'); cache[m]=v
    with wave.open(OUT+k+'.wav','wb') as wf:
        v.synthesize_wav(t, wf, syn_config=SynthesisConfig(length_scale=ls, noise_scale=0.6, noise_w_scale=0.7))
    with wave.open(OUT+k+'.wav') as wf: print(k, wf.getframerate(), round(wf.getnframes()/wf.getframerate(),2))
