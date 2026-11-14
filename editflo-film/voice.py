import json,subprocess
edl=json.load(open('edl.json'))
f=[];labels=[]
for i,x in enumerate(edl):
    s,e=x['src'];d=e-s
    f.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0,d-0.015)}:d=0.015[a{i}]")
    labels.append(f"[a{i}]")
f.append("".join(labels)+f"concat=n={len(edl)}:v=0:a=1,highpass=f=80,afftdn=nf=-30,acompressor=threshold=-24dB:ratio=3:attack=8:release=120,loudnorm=I=-16:TP=-1.5:LRA=9[v]")
subprocess.run(["ffmpeg","-v","error","-y","-i","../../../tmp/x" if False else "/tmp/claude-0/-home-user-youtube-content-help/587339b7-98ba-5b52-bebd-5abd082497a2/scratchpad/pitch/pitch.mp4","-filter_complex",";".join(f),"-map","[v]","-ar","48000","-ac","1","build/voice.wav"],check=True)
