import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const p=await browser.newPage({viewport:{width:375,height:812},deviceScaleFactor:2});
 await p.goto('http://127.0.0.1:5180');await p.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(p);
 assert.equal(await p.evaluate(()=>globalThis.lpLegendError),undefined);
 const result=await p.evaluate(async()=>{
  const a=lpLegend;a.hidden=true;await a.changeMap('A00',{x:74,y:64},{debug:true});a.tab='战斗';a.portalDelay=Infinity;a.previous=0;a.hidden=false;
  const stream=a.platform.canvas.captureStream(30),recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp9',videoBitsPerSecond:3000000}),parts=[],routes=[];
  recorder.ondataavailable=e=>parts.push(e.data);const done=new Promise(ok=>recorder.onstop=ok);recorder.start();
  try{
   for(const destination of [{x:74,y:60},{x:73,y:58},{x:74,y:64}]){
    if(!a.combat.moveTo(destination.x,destination.y))throw Error('Blocked staircase route');
    const route=[...a.combat.path],deadline=performance.now()+8000;
    while(a.combat.path.length){if(performance.now()>deadline)throw Error('Movement timeout');await new Promise(ok=>setTimeout(ok,30));}
    if(Math.hypot(a.hero.x-destination.x,a.hero.y-destination.y)>.01)throw Error('Destination not reached');
    routes.push({destination,route,arrived:{x:a.hero.x,y:a.hero.y}});await new Promise(ok=>setTimeout(ok,300));
   }
  }finally{recorder.stop();await done;stream.getTracks().forEach(t=>t.stop());}
  const bytes=new Uint8Array(await new Blob(parts,{type:recorder.mimeType}).arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));
  return {base64:btoa(binary),routes};
 });
 await fs.writeFile('reports/layering-fixed.webm',Buffer.from(result.base64,'base64'));
 await fs.writeFile('reports/layering-route.json',JSON.stringify({passed:true,routes:result.routes},null,2));
 await p.screenshot({path:'reports/layering-battle-fixed.png'});await p.evaluate(()=>lpLegend.dispose());
 console.log(JSON.stringify({passed:true,file:'reports/layering-fixed.webm',routes:result.routes}));
}finally{await browser.close();}
