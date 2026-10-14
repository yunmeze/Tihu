import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';

const baseline=process.argv.includes('--baseline'),mode=baseline?'before':'after';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const fixtures=[
 {name:'stairs',x:76,y:60,visible:true},
 {name:'stairs-walkable',x:74,y:60,visible:true},
 {name:'stairs-front',x:77,y:62,visible:true},
 {name:'raised-platform',x:80,y:59,visible:true},
 {name:'railing-front',x:80,y:62,visible:true},
 {name:'tree-behind',x:86,y:44,occluded:true},
 {name:'tree-front',x:86,y:47,visible:true},
 {name:'roof-overhead',x:74,y:48,occluded:true},
 {name:'blocked-middle-building',x:98,y:57,occluded:true},
 {name:'blocked-middle-tree',x:36,y:75,occluded:true},
];
const cases=[],errors=[];
try{
 for(const dpr of [1,2]){
  const p=await browser.newPage({viewport:{width:375,height:812},deviceScaleFactor:dpr});
  p.on('pageerror',e=>errors.push(e.message));
  await p.goto('http://127.0.0.1:5180');await p.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(p);
  assert.equal(await p.evaluate(()=>globalThis.lpLegendError),undefined);
  await p.evaluate(()=>{const a=lpLegend;a.platform.cancel(a.frame);a.elapsed=0;a.combat.events=[];a.units=[];a.map.npcs=[];a.drawChrome=()=>{};a.drawSystem=()=>{};});
  for(const f of fixtures){
   const result=await p.evaluate(async({x,y})=>{
    const a=lpLegend;a.hero={x,y,direction:4,action:'idle'};a.camera={x,y};await a.prepareVisible();
    const b=a.batch,frame=b.frame.bind(b),world=a.drawWorld.bind(a),gl=a.renderer.getContext(),w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
    const pixels=()=>{const v=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,v);return v;};
    a.render();const actual=pixels();
    b.frame=(pack,...args)=>{if(!pack.id.startsWith('Hero/')&&!pack.id.startsWith('Weapon/'))frame(pack,...args);};
    a.render();const background=pixels();
    a.drawWorld=()=>{world();const q=a.mapPoint(x,y),hidden=b.frame;b.frame=frame;try{a.drawAvatar(a.hero,q.x,q.y,a.worldScale);}finally{b.frame=hidden;}};
    a.render();const front=pixels();let covered=0,total=0;
    for(let i=0;i<actual.length;i+=4){const diff=(u,v)=>Math.max(Math.abs(u[i]-v[i]),Math.abs(u[i+1]-v[i+1]),Math.abs(u[i+2]-v[i+2]));if(diff(front,background)>16){total++;if(diff(actual,front)>16)covered++;}}
    b.frame=frame;a.drawWorld=world;a.render();
    return {walkable:a.combat.walkable(x,y),heroPixels:total,coveredPixels:covered,occludedRatio:covered/total};
   },f);
   await p.screenshot({path:`reports/layers-${mode}-${f.name}-dpr${dpr}.png`});
   cases.push({fixture:f.name,dpr,...result});assert.ok(result.heroPixels>100,'hero must be loaded');
   if(!baseline){if(f.visible)assert.ok(result.occludedRatio<.01,`${f.name}: terrain covers the character`);if(f.occluded)assert.ok(result.occludedRatio>.05,`${f.name}: character shows through foreground`);}
  }
  await p.evaluate(()=>lpLegend.dispose());await p.close();
 }
 assert.deepEqual(errors,[]);await fs.writeFile(`reports/layering-${mode}.json`,JSON.stringify({passed:true,cases,errors},null,2));console.log(JSON.stringify({mode,cases,errors}));
}finally{await browser.close();}
