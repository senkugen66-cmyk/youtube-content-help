// usage: node still.js out_dir t1 t2 ... (output-time seconds)
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve('film.html'));await p.evaluate(()=>document.fonts.ready);
 const [out,...ts]=process.argv.slice(2);
 for(const t of ts){await p.evaluate(t=>render(+t),t);await p.screenshot({path:`${out}/s_${(+t).toFixed(2)}.png`});}
 if(errs.length)console.log('ERR',errs);await b.close()})();
