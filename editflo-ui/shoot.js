// Renders each screen at 1440x1024, 2x scale. Also reports any overflow past the viewport.
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:1440,height:1024},deviceScaleFactor:+(process.argv[2]||2)});
 p.on('pageerror',e=>console.log('ERR',e.message));
 const names={1:'01-dashboard',2:'02-workflow-detail',3:'03-integrations'};
 for(const s of [1,2,3]){await p.goto('file://'+path.resolve('app.html')+'?s='+s);await p.evaluate(()=>document.fonts.ready);
  const of=await p.evaluate(()=>{const c=document.querySelector('.content');return {scroll:c.scrollHeight,client:c.clientHeight}});
  console.log(names[s],JSON.stringify(of));
  await p.screenshot({path:`${names[s]}.png`});}
 await b.close()})();
