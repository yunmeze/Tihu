import fs from 'node:fs/promises';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';
const dir='reports/movement-20261013',phase=process.argv.includes('--after')||process.env.LP_PROFILE_PHASE==='after'?'after':'before';await fs.mkdir(dir,{recursive:true});
const owned=await ownedTestBrowser('movement-profile-'+phase),results=[];
try{const context=await owned.browser.newContext({viewport:{width:375,height:812},deviceScaleFactor:1});
 try{const page=await context.newPage();page.setDefaultTimeout(90000);await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady);await enterGame(page);const cdp=await context.newCDPSession(page);await cdp.send('Profiler.enable');await cdp.send('Profiler.setSamplingInterval',{interval:500});
  for(const map of ['A02','K24']){
   await page.evaluate(async map=>{const a=lpLegend;a.platform.cancel(a.frame);a.audio.pause(true);a.player.base.hp=a.player.hp=100000;a.player.autoSkills=[];a.nextSave=Infinity;await a.changeMap(map,null,{debug:true,unlock:true});a.combat.story=null;a.combat.stopFarming();a.platform.cancel(a.frame);let seed=12345;const random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296);a.combat.monsterRandom=a.combat.battleRandom=a.combat.visualRandom=random;await a.prepareVisible();},map);
   await cdp.send('Profiler.start');
   const data=await page.evaluate(async()=>{
    const a=lpLegend,rows=[],uploads=[],undo=[];let current;
    for(const [o,name,key]of [[a,'drawWorld','world'],[a,'drawWorldLabels','labels'],[a,'drawSystem','hud'],[a,'render','render'],[a.combat,'update','simulation'],[a,'prepareVisible','prepare'],[a.batch,'finish','batch'],[a.renderer,'render','gpu']]){const old=o[name];o[name]=function(...args){const start=performance.now();try{return old.apply(this,args);}finally{if(current)current[key]=(current[key]||0)+performance.now()-start;}};undo.push(()=>o[name]=old);}
    const gl=a.renderer.getContext();for(const name of ['texImage2D','texSubImage2D','texStorage2D']){const old=gl[name];gl[name]=function(...args){const start=performance.now();try{return old.apply(this,args);}finally{uploads.push({frame:rows.length,api:name,ms:performance.now()-start,width:args.find(v=>v?.width)?.width});}};undo.push(()=>gl[name]=old);}
    const start={x:a.hero.x,y:a.hero.y};let target;
    for(const dx of [24,-24,18,-18]){for(const dy of [0,12,-12]){a.combat.moveTo(Math.round(start.x+dx),Math.round(start.y+dy));if(a.combat.path.length>=15){target={x:Math.round(start.x+dx),y:Math.round(start.y+dy)};break;}}if(target)break;}
    let previous;try{for(let i=0;i<360;i++){const stamp=await new Promise(r=>requestAnimationFrame(r));current={i,interval:previous?stamp-previous:0};const dt=previous?Math.min((stamp-previous)/1000,.1):1/60;previous=stamp;a.previous=stamp-dt*1000;a.tick(stamp);a.platform.cancel(a.frame);current.x=a.hero.x;current.y=a.hero.y;rows.push(current);}}finally{undo.forEach(f=>f());a.platform.cancel(a.frame);}return {map:a.mapId,units:a.units.length,target,rows,uploads};
   });
   const {profile}=await cdp.send('Profiler.stop');await fs.writeFile(`${dir}/${phase}-${map}.cpuprofile`,JSON.stringify(profile));
   const weights=new Map();for(let i=0;i<profile.samples.length;i++){const id=profile.samples[i];weights.set(id,(weights.get(id)||0)+(profile.timeDeltas[i]||0));}
   const top=profile.nodes.map(n=>({name:n.callFrame.functionName||'(anonymous)',file:n.callFrame.url,line:n.callFrame.lineNumber+1,ms:(weights.get(n.id)||0)/1000})).filter(n=>n.ms>0).sort((a,b)=>b.ms-a.ms).slice(0,25);
   const sorted=data.rows.slice(30).map(r=>r.interval).sort((a,b)=>a-b),stats={p50:sorted[Math.floor(sorted.length*.5)],p95:sorted[Math.floor(sorted.length*.95)],max:sorted.at(-1)},spikes=data.rows.filter(r=>r.render>20||r.simulation>10);
   results.push({...data,stats,top,spikes});console.log(JSON.stringify({phase,map,units:data.units,stats,top:top.slice(0,14),uploads:data.uploads,spikes:spikes.slice(0,10)}));await page.screenshot({path:`${dir}/${phase}-${map}.png`});
  }
  await cdp.detach();await page.evaluate(()=>lpLegend.dispose());
 }finally{await context.close();}
}finally{await owned.close();await fs.writeFile(`${dir}/profile-${phase}.json`,JSON.stringify({phase,softwareWebGL:true,samplingIntervalMicroseconds:500,results},null,2));}
