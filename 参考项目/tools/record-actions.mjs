import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const p=await browser.newPage({viewport:{width:375,height:812},deviceScaleFactor:2});await p.goto('http://127.0.0.1:5180');await p.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(p);assert.equal(await p.evaluate(()=>globalThis.lpLegendError),undefined);
 const result=await p.evaluate(async()=>{
  const a=lpLegend;a.hidden=true;await a.gmCommand('解锁全技能');a.message=null;const u=a.combat.nearby()[0],adj=[[1,0],[-1,0],[0,1],[0,-1]].map(([dx,dy])=>({x:u.x+dx,y:u.y+dy})).find(p=>a.combat.walkable(p.x,p.y));if(!adj)throw Error('No adjacent test position');
  a.combat.position={...adj,direction:4,action:'idle',actionTime:0,animationElapsed:0};a.hero=a.combat.position;a.camera={...adj};a.combat.random=()=>0;a.player.activeSkill='基本剑术';a.combat.select(u.id);a.combat.hitClock=0;await a.prepareVisible();a.previous=0;a.hidden=false;
  const stream=a.platform.canvas.captureStream(30),recorder=new MediaRecorder(stream,{mimeType:'video/webm;codecs=vp9',videoBitsPerSecond:3000000}),parts=[],trace=[],started=performance.now();recorder.ondataavailable=e=>parts.push(e.data);const done=new Promise(ok=>recorder.onstop=ok);recorder.start();
  const timer=setInterval(()=>trace.push({time:Math.round((performance.now()-started)/10)/100,action:a.hero.action,frame:a.animationFrame(a.hero),mp:a.player.mp,hits:a.combat.hitCount}),100);
  try{await new Promise(ok=>setTimeout(ok,3400));a.player.activeSkill='火球术';a.skillPage=Math.floor(a.player.skills.findIndex(s=>s.name==='火球术')/4);await new Promise(ok=>setTimeout(ok,4000));}
  finally{clearInterval(timer);recorder.stop();await done;stream.getTracks().forEach(t=>t.stop());}
  const bytes=new Uint8Array(await new Blob(parts,{type:recorder.mimeType}).arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=32768)binary+=String.fromCharCode(...bytes.subarray(i,i+32768));return {base64:btoa(binary),trace,hits:a.combat.hitCount,mp:a.player.mp};
 });
 assert.ok(result.trace.some(t=>t.action==='attack'));assert.ok(result.trace.some(t=>t.action==='cast'));for(const t of result.trace){if(t.action==='attack')assert.ok(t.frame>=129&&t.frame<=176);if(t.action==='cast')assert.ok(t.frame>=177&&t.frame<=224);}
 await fs.writeFile('reports/actions-fixed.webm',Buffer.from(result.base64,'base64'));delete result.base64;await fs.writeFile('reports/actions-recording.json',JSON.stringify({passed:true,...result},null,2));await p.evaluate(()=>lpLegend.dispose());console.log(JSON.stringify({passed:true,file:'reports/actions-fixed.webm',samples:result.trace.length,hits:result.hits,mp:result.mp}));
}finally{await browser.close();}
