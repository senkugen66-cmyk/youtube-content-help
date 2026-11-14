# Builds the edit decision list: which source ranges of the pitch audio survive,
# with long pauses tightened. Outputs edl.json (segments) and cues.json (words on output timeline).
import json
words=[w for s in json.load(open('words.json')) for w in s['w']]
# Source ranges to keep (drops the false start at 43-57s and the aborted/aside section 170-213s)
KEEP=[(0.0,41.95),(57.30,169.95),(213.75,245.2)]
# Silences longer than MIN get shrunk to KEEPGAP (split evenly around the cut)
MIN=0.42; KEEPGAP=0.26
# Moments that deserve room to land: keep a longer pause after these source times
LAND={11.06:0.75,22.56:0.7,41.76:0.8,81.96:0.55,88.20:0.7,117.98:0.9,145.32:0.8,169.66:0.8,239.70:0.9,241.78:0.45}
sil0=[tuple(map(float,l.split())) for l in open('sil.txt') if len(l.split())==2]
# only cut where silence falls in a gap between transcribed words (never inside a word)
gaps=[(words[i][1]+0.04,words[i+1][0]-0.04) for i in range(len(words)-1)]
sil=[]
for s,e in sil0:
    for g0,g1 in gaps:
        a2,b2=max(s,g0),min(e,g1)
        if b2-a2>0.05: sil.append((a2,b2))
segs=[]
for a,b in KEEP:
    cur=a
    for s,e in sil:
        if e<=a or s>=b: continue
        s2,e2=max(s,a),min(e,b)
        if e2-s2<MIN: continue
        keep=KEEPGAP
        for k,v in LAND.items():
            if abs(k-s2)<0.5 or (s2<=k<=e2): keep=max(keep,v)
        if e2-s2<=keep: continue
        cut0=s2+keep/2; cut1=e2-keep/2
        if cut0>cur: segs.append([cur,cut0])
        cur=cut1
    segs.append([cur,b])
segs=[s for s in segs if s[1]-s[0]>0.05]
out=0; edl=[]
for s,e in segs:
    edl.append({"src":[round(s,3),round(e,3)],"out":round(out,3)}); out+=e-s
json.dump(edl,open('edl.json','w'),indent=0)
def m(t):
    for x in edl:
        s,e=x['src']
        if t<s: return x['out']
        if t<=e: return x['out']+t-s
    return out
cues=[]
for w in words:
    if any(a<=w[0]<b for a,b in KEEP):
        cues.append({"s":w[0],"t":round(m(w[0]),3),"e":round(m(w[1]),3),"w":w[2].strip()})
json.dump({"dur":round(out,3),"words":cues},open('cues.json','w'))
print("segments",len(edl),"output duration",round(out,2))
