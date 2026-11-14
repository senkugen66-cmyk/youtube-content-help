# Synthesises an original, subtle music bed and restrained UI sound effects.
import json,numpy as np,wave
SR=48000
edl=json.load(open('edl.json'));cues=json.load(open('cues.json'))
def T(s):
    for x in edl:
        a,b=x['src']
        if s<a: return x['out']
        if s<=b: return x['out']+s-a
    return cues['dur']
VEND=cues['dur']; DUR=VEND+4.2; N=int(DUR*SR)
t=np.arange(N)/SR
rng=np.random.default_rng(7)
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.0
    # vectorised one-pole via lfilter-like loop in chunks
    from itertools import accumulate
    y=np.zeros_like(x); prev=0.0
    for i in range(0,len(x),SR):
        seg=x[i:i+SR]; out=np.empty_like(seg)
        for j,v in enumerate(seg): prev=(1-a)*v+a*prev; out[j]=prev
        y[i:i+SR]=out
    return y
def hz(n): return 440*2**((n-69)/12)
BPM=96; beat=60/BPM; bar=4*beat; CH=2*bar
# D major-ish, warm and unresolved: Dmaj9, Bm9, Gmaj9, Asus
chords=[[50,54,57,61,64],[47,50,54,57,61],[43,47,50,54,57],[45,50,52,57,59]]
music=np.zeros(N)
# pad
nch=int(DUR/CH)+2
for k in range(nch):
    c=chords[k%4]; s0=k*CH-0.6; s1=s0+CH+1.2
    i0=max(0,int(s0*SR)); i1=min(N,int(s1*SR))
    if i1<=i0: continue
    tt=t[i0:i1]-s0; L=s1-s0
    env=np.clip(tt/1.4,0,1)*np.clip((L-tt)/1.4,0,1)
    sig=np.zeros(i1-i0)
    for n in c:
        f=hz(n+12)
        for d in (-0.0016,0.0016):
            sig+=np.sin(2*np.pi*f*(1+d)*tt)+0.25*np.sin(2*np.pi*2*f*(1+d)*tt)+0.08*np.sin(2*np.pi*3*f*tt)
    music[i0:i1]+=sig*env*0.022
# arrangement masks
def ramp(a,b,up=True,d=1.0):
    m=np.clip((t-a)/d,0,1) if up else 1-np.clip((t-b)/d,0,1); return m
quiet=[(T(39.6),T(41.9)),(T(79.3),T(83.0)),(VEND-0.2,DUR)]
arpmask=np.clip((t-2.5)/2,0,1)
for a,b in quiet:
    arpmask*=1-np.clip((t-a)/0.5,0,1)*np.clip((b+0.6-t)/0.6,0,1) if b<DUR else 1-np.clip((t-a)/0.8,0,1)
bassmask=np.clip((t-T(13.84))/0.3,0,1)
for a,b in quiet:
    bassmask*=1-np.clip((t-a)/0.4,0,1)*np.clip((b+0.6-t)/0.6,0,1) if b<DUR else 1-np.clip((t-a)/1.2,0,1)
# pluck arpeggio (8ths)
arp=np.zeros(N); step=beat/2; L=int(0.9*SR); env=np.exp(-np.arange(L)/SR/0.22)
pat=[0,2,4,3,1,3,4,2]
i=0
while i*step<DUR:
    k=int(i*step/CH); c=chords[k%4]; n=c[pat[i%8]]+24
    s=int(i*step*SR)
    if s+L<N:
        tt=np.arange(L)/SR; f=hz(n)
        v=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt/0.06))*env*(0.9 if i%2==0 else 0.6)
        arp[s:s+L]+=v
    i+=1
# simple echo
d=int(beat*0.75*SR); arp[d:]+=0.32*arp[:-d]
music+=arp*0.012*arpmask
# soft sub bass on chord roots
bass=np.zeros(N)
for k in range(nch):
    f=hz(chords[k%4][0]-12); s0=k*CH
    for bb in range(2):
        st=s0+bb*bar; i0=int(st*SR); i1=min(N,int((st+bar)*SR))
        if i0>=N: break
        tt=t[i0:i1]-st
        bass[i0:i1]+=np.sin(2*np.pi*f*tt)*np.clip(tt/0.05,0,1)*np.exp(-tt/1.2)
music+=bass*0.05*bassmask
# final resolve: Dmaj9 swell at the end card
s0=VEND-0.1; i0=int(s0*SR); tt=t[i0:]-s0
fin=sum(np.sin(2*np.pi*hz(n+12)*tt)+0.2*np.sin(2*np.pi*hz(n+24)*tt) for n in [50,57,61,64,66])
music[i0:]+=fin*0.02*np.clip(tt/0.8,0,1)*np.exp(-np.clip(tt-1,0,None)/1.6)
# global fade in/out
music*=np.clip(t/1.5,0,1)*np.clip((DUR-t)/1.0,0,1)
# ---------- SFX ----------
sfx=np.zeros(N)
def put(x,at,g):
    s=int(at*SR); e=min(N,s+len(x));
    if s<N: sfx[s:e]+=x[:e-s]*g
def tick():
    L=int(.05*SR);tt=np.arange(L)/SR;return np.sin(2*np.pi*2200*tt)*np.exp(-tt/.008)*.5+rng.normal(0,1,L)*np.exp(-tt/.002)*.15
def pop():
    L=int(.12*SR);tt=np.arange(L)/SR;f=lerp=700-250*np.clip(tt/.06,0,1);ph=2*np.pi*np.cumsum(f)/SR;return np.sin(ph)*np.exp(-tt/.03)*.6
def swish():
    L=int(.45*SR);tt=np.arange(L)/SR;n=rng.normal(0,1,L);
    # band-limited noise: smoothed noise minus heavily smoothed noise
    k1=np.ones(6)/6;k2=np.ones(60)/60;b=np.convolve(n,k1,'same')-np.convolve(n,k2,'same')
    env=np.sin(np.pi*np.clip(tt/.45,0,1))**2;return b*env*.5
def thud():
    L=int(.5*SR);tt=np.arange(L)/SR;f=95-40*np.clip(tt/.2,0,1);ph=2*np.pi*np.cumsum(f)/SR;return np.sin(ph)*np.exp(-tt/.14)*.9
def chime():
    L=int(2.2*SR);tt=np.arange(L)/SR;return sum(a*np.sin(2*np.pi*hz(n)*tt)*np.exp(-tt/dcy) for n,a,dcy in [(74,.5,.9),(81,.35,.7),(86,.18,.5)])*np.clip(tt/.004,0,1)
def typ():
    out=np.zeros(int(.8*SR))
    for k in range(7):
        x=tick()*rng.uniform(.4,.8); s=int((k*.11+rng.uniform(0,.03))*SR); out[s:s+len(x)]+=x[:len(out)-s]
    return out
G={'tick':(tick,.22),'pop':(pop,.2),'swish':(swish,.16),'thud':(thud,.5),'chime':(chime,.16),'type':(typ,.14)}
for e in json.load(open('build/sfx.json')):
    f,g=G[e['k']]; put(f(),e['t'],g*e['v'])
def w(name,x):
    x=np.clip(x,-1,1); d=(x*32767).astype(np.int16)
    with wave.open(name,'wb') as f: f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes(d.tobytes())
w('build/music.wav',music); w('build/sfx.wav',sfx)
print('ok',DUR, 'sfx events',len(json.load(open('build/sfx.json'))))
