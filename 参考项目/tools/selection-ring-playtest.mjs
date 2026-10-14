import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
import {selectionRingBounds} from '../src/selection-ring.js';

let nativePacks=0,livingFrames=0;
for(const id of await fs.readdir('public/assets/sprites/Mon')){
 const pack=JSON.parse(await fs.readFile(`public/assets/sprites/Mon/${id}/index.json`,'utf8')),r=selectionRingBounds(pack);
 assert.ok(Number.isFinite(r.radiusX)&&Number.isFinite(r.radiusY));assert.ok(r.radiusX>=30&&r.radiusY>=15);assert.equal(selectionRingBounds(pack),r);
 for(const f of pack.frames.slice(1,129)){if(!f||f.rect[2]<=0||f.rect[3]<=0)continue;assert.ok(r.y+r.radiusY-3>f.offset[1]+f.crop[1]+f.rect[3],id+' covers front arc');livingFrames++;}nativePacks++;
}

const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),checks=[],errors=[];
try{for(const viewport of [{width:375,height:812},{width:430,height:932}]){
 const context=await browser.newContext({viewport,deviceScaleFactor:1});context.setDefaultTimeout(60000);const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 try{
  await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
  await page.evaluate(()=>{const a=lpLegend;a.platform.cancel(a.frame);a.audio.pause(true);a.combat.stopFarming();a.tab='战斗';a.message=null;});
  for(const name of ['鸡','甲虫王','骷髅精灵','赤龙神']){
   const result=await page.evaluate(async name=>{
    const a=lpLegend,c=a.combat,definition=a.content.monsters.find(d=>d.name===name);
    if(!definition)throw Error('Missing native monster '+name);
    // An unobstructed native map area isolates model occlusion from fences
    // and trees, which should still cover a ground marker naturally.
    const u={id:'ring-fixture',monsterId:definition.id,definition,name,x:20,y:26,hp:definition.hp,alive:true,action:'idle',actionTime:0,animationElapsed:0,direction:4};
    c.units=a.units=[u];c.targetId=u.id;c.farmType=u.monsterId;c.effects=[];c.projectiles=[];c.events=[];c.groundItems=[];
    Object.assign(c.position,{x:u.x-3,y:u.y+3,action:'idle',animationElapsed:0});a.hero=c.position;a.camera={x:u.x+.5,y:u.y+2};await a.prepareVisible();
    const originalRing=a.batch.ellipseRing,originalFrame=a.batch.frame,poses=[],width=a.worldTarget.width,height=a.worldTarget.height;
    const pixels=()=>{const buffer=new Uint8Array(width*height*4);a.renderer.readRenderTargetPixels(a.worldTarget,0,0,width,height,buffer);return buffer;};
    try{
     for(const [action,direction,time]of [['idle',4,0],['walk',2,.25],['attack',0,.4],['attack',6,.4]]){
      Object.assign(u,{action,direction,animationElapsed:time});const calls=[],order=[];
      a.batch.ellipseRing=function(...args){calls.push(args.slice(0,7));order.push('ring');return originalRing.apply(this,args);};
      a.batch.frame=function(pack,...args){if(pack?.id==='Mon/'+definition.appearance)order.push('model');return originalFrame.call(this,pack,...args);};
      a.render();const selected=pixels();
      a.batch.ellipseRing=()=>{};a.render();const plain=pixels();
      a.batch.ellipseRing=originalRing;a.batch.frame=originalFrame;
      if(calls.length!==3||order.lastIndexOf('ring')>=order.indexOf('model'))throw Error('Ground ring drawn after creature '+name);
      const [x,y,rx,ry,stroke]=calls[1],frame=a.packs.get('Mon/'+definition.appearance).frames[a.animationFrame(u,'monster')],point=a.mapPoint(u.x,u.y),bottom=point.y+(frame.offset[1]+frame.crop[1]+frame.rect[3])*a.worldScale;
      if(y+ry-stroke<=bottom)throw Error('Creature covers front arc '+name);
      let visiblePixels=0,frontPixels=0;
      for(let py=0;py<height;py++)for(let px=0;px<width;px++){
       const i=(py*width+px)*4,change=Math.max(Math.abs(selected[i]-plain[i]),Math.abs(selected[i+1]-plain[i+1]),Math.abs(selected[i+2]-plain[i+2]));
       if(change>25){visiblePixels++;const sx=(px+.5)*a.worldScale,sy=(height-py-.5)*a.worldScale;if(Math.abs(sx-x)<rx*.45&&sy>y+ry-stroke-4*a.worldScale)frontPixels++;}
      }
      if(visiblePixels<50||frontPixels<8)throw Error('Ring not visible in actual WebGL image '+JSON.stringify({name,action,direction,visiblePixels,frontPixels}));
      poses.push({action,direction,radiusX:rx/a.worldScale,radiusY:ry/a.worldScale,visiblePixels,frontPixels,groundBeforeModel:true});
     }
    }finally{a.batch.ellipseRing=originalRing;a.batch.frame=originalFrame;}
    if(poses.some(p=>p.radiusX!==poses[0].radiusX||p.radiusY!==poses[0].radiusY))throw Error('Ground footprint changes with animation '+name);
    Object.assign(u,{action:'attack',direction:2,animationElapsed:.4});a.render();
    return {name,appearance:definition.appearance,poses};
   },name);
   await page.screenshot({path:`reports/selection-ring-${result.appearance}-${viewport.width}.png`});checks.push({viewport,...result});
  }
  const lifecycle=await page.evaluate(()=>{
   const a=lpLegend,c=a.combat,u=a.units[0],original=a.batch.ellipseRing;let calls=0;a.batch.ellipseRing=function(...args){calls++;return original.apply(this,args);};
   const count=()=>{calls=0;a.render();return calls;};
   try{
    c.targetId=null;if(count()!==0)throw Error('Cancelled selection leaves ring');
    c.targetId=u.id;u.alive=false;u.action='death';u.animationElapsed=.1;if(count()!==0)throw Error('Dead target leaves ring');
    u.animationElapsed=2;if(count()!==0)throw Error('Expired corpse leaves ring');
    u.alive=true;u.action='walk';u.x+=.4;u.y+=.25;c.targetId=u.id;const moved=count();if(moved!==3)throw Error('Moving target loses ring');
    c.moveTo(a.hero.x+1,a.hero.y);if(count()!==0)throw Error('Manual movement leaves attack ring');
    const other={...u,id:'ring-other',x:u.x+1},centers=[];c.units=a.units=[u,other];c.targetId=other.id;
    a.batch.ellipseRing=function(x,y,...rest){centers.push({x,y});return original.call(this,x,y,...rest);};a.render();const p=a.mapPoint(other.x,other.y);
    if(centers.length!==3||Math.abs(centers[1].x-(p.x+24*a.worldScale))>.01)throw Error('Target switch leaves previous ring');
    return {cancel:true,death:true,expiredCorpse:true,movingTarget:true,manualMovement:true,targetSwitch:true};
   }finally{a.batch.ellipseRing=original;}
  });checks.push({viewport,lifecycle});
  await page.evaluate(async()=>{
   const a=lpLegend,c=a.combat;c.enter(a.map,{x:97,y:73});a.units=c.units;a.hero=c.position;
   const u=c.units.find(u=>u.definition.name==='鸡'&&u.x===98&&u.y===72);if(!u)throw Error('Missing village chicken');
   c.startFarming(4,u.id);c.update(.2);a.camera={x:u.x+.5,y:u.y+1};await a.prepareVisible();a.render();
   const original=a.batch.ellipseRing;let count=0;a.batch.ellipseRing=function(...args){count++;return original.apply(this,args);};
   try{a.render();if(count!==3)throw Error('Native village attack missing ground ring');}finally{a.batch.ellipseRing=original;}
  });await page.screenshot({path:`reports/selection-ring-village-${viewport.width}.png`});checks.push({viewport,nativeVillageAttack:true});await page.evaluate(()=>lpLegend.dispose());
 }finally{await context.close();}
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/selection-ring-playtest.json',JSON.stringify({passed:true,nativePacks,livingFrames,checks,errors,wechatDeviceTested:false},null,2));console.log({passed:true,nativePacks,livingFrames,viewports:2,nativeModels:4,animationPoses:32,realWebGLVisibility:true});
}finally{await browser.close();}
