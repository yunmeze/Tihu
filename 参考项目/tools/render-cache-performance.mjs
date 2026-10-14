import fs from 'node:fs/promises';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';

// Pair both render paths on exactly the same moving scene. Alternate order to
// avoid giving either implementation all of the first-render upload cost.
const owned=await ownedTestBrowser('render-cache-comparison'),browser=owned.browser,cases=[];
try{
 const context=await browser.newContext({viewport:{width:375,height:812},deviceScaleFactor:1});
 try{
  const page=await context.newPage();await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady);await enterGame(page);
  for(const map of ['A00','A02']){
   const result=await page.evaluate(async map=>{
    const a=lpLegend;if(a.mapId!==map)await a.changeMap(map,null,{debug:true,unlock:true});a.platform.cancel(a.frame);a.audio.pause(true);a.tab='战斗';a.player.base.hp=a.player.hp=100000;a.player.autoSkills=[];a.nextSave=Infinity;a.combat.scriptLocked=false;a.combat.stopFarming();await a.prepareVisible();
    const source=a.content.rectUV,uv=a.content.uv,values={cached:[],direct:[]},calculations={cached:0,direct:0};let mode='cached',previous;
    const direct=function(frame,page){return this.uv(page.file,...frame.rect,page.width,page.height);};
    a.content.uv=function(...args){calculations[mode]++;return uv.apply(this,args);};
    const render=a.render;a.render=function(){const start=performance.now();try{return render.call(this);}finally{values[mode].push(performance.now()-start);}};
    try{
     const start={...a.hero};for(const dx of [24,-24,18,-18]){a.combat.moveTo(Math.round(start.x+dx),Math.round(start.y));if(a.combat.path.length>=12)break;}
     for(let i=0;i<210;i++){
      const stamp=await new Promise(r=>requestAnimationFrame(r)),dt=previous?Math.min((stamp-previous)/1000,.1):1/60;previous=stamp;
      mode=i%2?'cached':'direct';a.content.rectUV=mode==='cached'?source:direct;a.previous=stamp-dt*1000;a.tick(stamp);a.platform.cancel(a.frame);
      mode=mode==='cached'?'direct':'cached';a.content.rectUV=mode==='cached'?source:direct;a.render();
      if(i===29){values.cached.length=values.direct.length=0;calculations.cached=calculations.direct=0;}
     }
    }finally{a.render=render;a.content.rectUV=source;a.content.uv=uv;a.platform.cancel(a.frame);}
    const stats=v=>{const sorted=[...v].sort((a,b)=>a-b);return {frames:v.length,mean:v.reduce((n,x)=>n+x,0)/v.length,p50:sorted[Math.floor(v.length*.5)],p95:sorted[Math.floor(v.length*.95)]};};
    return {map,cached:stats(values.cached),direct:stats(values.direct),coordinateCalculations:calculations};
   },map);cases.push(result);console.log(result);
  }
  await page.evaluate(()=>lpLegend.dispose());
 }finally{await context.close();}
}finally{await owned.close();await fs.writeFile('reports/audit-fixes-20261012/render-cache-performance.json',JSON.stringify({softwareWebGL:true,method:'Alternating paired renders of the same moving scene, 30 warm-up frames then 180 pairs per map. Frame rate is intentionally not assessed by this two-render experiment.',cases},null,2));}
