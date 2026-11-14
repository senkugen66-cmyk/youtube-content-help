// Deterministic frame renderer: node render.js <fps> <workers> <outdir>
const {chromium}=require('playwright');const path=require('path');const {spawn}=require('child_process');
const [fps,W,out]=[+process.argv[2]||30,+process.argv[3]||4,process.argv[4]||'build'];
(async()=>{
 const b=await chromium.launch();
 const p0=await b.newPage();await p0.goto('file://'+path.resolve('film.html'));const dur=await p0.evaluate(()=>DUR);
 const sfx=await p0.evaluate(()=>SFX);require('fs').writeFileSync(out+'/sfx.json',JSON.stringify(sfx));await p0.close();
 const N=Math.ceil(dur*fps);const per=Math.ceil(N/W);const t0=Date.now();
 await Promise.all([...Array(W).keys()].map(async w=>{
   const a=w*per,z=Math.min(N,a+per);
   const p=await b.newPage({viewport:{width:1920,height:1080}});await p.goto('file://'+path.resolve('film.html'));await p.evaluate(()=>document.fonts.ready);
   const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',`${out}/part${w}.mp4`]);
   for(let i=a;i<z;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:95});
     if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
     if(w==0&&i%150==0)console.log(`w0 ${i-a}/${z-a} ${((Date.now()-t0)/1000).toFixed(0)}s`);}
   ff.stdin.end();await new Promise(r=>ff.on('close',r));await p.close();}));
 await b.close();
 require('fs').writeFileSync(out+'/parts.txt',[...Array(W).keys()].map(w=>`file 'part${w}.mp4'`).join('\n'));
 console.log('frames',N,'secs',(Date.now()-t0)/1000)})();
