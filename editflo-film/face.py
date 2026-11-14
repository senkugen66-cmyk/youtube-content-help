# Extracts the presenter (Loom webcam bubble) on the OUTPUT timeline. Every output frame n
# is mapped back through the edit list to its exact source time, so the face stays
# frame-accurate with the cut narration. Writes build/face/%05d.jpg (frame n = t*30+1).
import json,subprocess,os,numpy as np
from PIL import Image
SRC="/tmp/claude-0/-home-user-youtube-content-help/587339b7-98ba-5b52-bebd-5abd082497a2/scratchpad/pitch/pitch.mp4"
edl=json.load(open('edl.json'));cues=json.load(open('cues.json'))
SZ=320
# 1) decode the bubble region of the whole source at its native 30 fps, enlarged and cleaned
raw=subprocess.run(["ffmpeg","-v","error","-i",SRC,"-vf",f"crop=86:86:13:384,hqdn3d=2:2:4:4,scale={SZ}:{SZ}:flags=lanczos,unsharp=5:5:0.45:5:5:0,eq=saturation=1.05:contrast=1.03","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True,check=True).stdout
src=np.frombuffer(raw,np.uint8).reshape(-1,SZ,SZ,3); FPS=30
def inv(o):
    for x in edl:
        a,b=x['src']; d=b-a
        if o<x['out']+d: return a+max(0,o-x['out'])
    return edl[-1]['src'][1]
os.makedirs('build/face',exist_ok=True)
n=int(cues['dur']*FPS)+1
for i in range(n):
    k=min(len(src)-1,int(round(inv(i/FPS)*FPS)))
    Image.fromarray(src[k]).save(f'build/face/{i+1:05d}.jpg',quality=92)
print(n,'frames from',len(src),'source frames')
