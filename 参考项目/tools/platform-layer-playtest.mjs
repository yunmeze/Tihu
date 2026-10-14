import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const baseline=process.argv.includes('--baseline'),mode=baseline?'before':'after',browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const cases=[],errors=[];
try{
 for(const dpr of [1,2]){
  const p=await browser.newPage({viewport:{width:375,height:812},deviceScaleFactor:dpr});p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:5180');await p.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(p);assert.equal(await p.evaluate(()=>globalThis.lpLegendError),undefined);
  await p.evaluate(()=>{const a=lpLegend;a.platform.cancel(a.frame);a.elapsed=0;a.units=[];a.combat.events=[];a.player.clearCount=1;a.player.events[7]=0;for(const n of a.map.npcs)if(n.name==='老药师')n.removed=false;});
  for(const fixture of [{name:'doctor-platform',names:['村大夫','老药师'],camera:{x:93.5,y:59.5},hero:{x:91,y:61}},{name:'village-chief-platform',names:['海曦村长'],camera:{x:75,y:54},hero:{x:73,y:58}}]){
   const results=await p.evaluate(async({names,camera,hero})=>{
    const a=lpLegend;a.hero={...hero,direction:4,action:'idle'};a.camera=camera;await a.prepareVisible();const b=a.batch,frame=b.frame.bind(b),text=b.text.bind(b),world=a.drawWorld.bind(a),npc=a.packs.get('Npc'),gl=a.renderer.getContext(),w=gl.drawingBufferWidth,h=gl.drawingBufferHeight;
    // Second-cycle fixture: A00 load script hides the pharmacist before the first clear.
    // Neighboring name labels can overlap a sprite; measure map occlusion alone.
    b.text=()=>{};
    const read=()=>{const pixels=new Uint8Array(w*h*4);gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pixels);return pixels;},result=[];
    for(const name of names){const n=a.map.npcs.find(n=>n.name===name),index=1+n.appearance*12+n.direction*4;
     a.render();const actual=read();b.frame=(pack,i,...args)=>{if(pack.id!=='Npc'||i!==index)frame(pack,i,...args);};a.render();const background=read();
     // The doctor and pharmacist share a sprite, so the reference draws both.
     a.drawWorld=()=>{world();for(const actor of a.map.npcs.filter(v=>1+v.appearance*12+v.direction*4===index)){const q=a.mapPoint(actor.x,actor.y);frame(npc,index,q.x,q.y,a.worldScale);}};a.render();const front=read();
     let total=0,covered=0;const q=a.screenPoint(n.x,n.y),sx=a.left+(q.x+npc.frames[index].offset[0]*a.worldScale)*a.scale,sy=a.top+(q.y+npc.frames[index].offset[1]*a.worldScale)*a.scale,ex=sx+npc.frames[index].original[0]*a.worldScale*a.scale,ey=sy+npc.frames[index].original[1]*a.worldScale*a.scale,dpr=a.renderer.getPixelRatio();
     for(let y=Math.floor(sy*dpr);y<Math.ceil(ey*dpr);y++)for(let x=Math.floor(sx*dpr);x<Math.ceil(ex*dpr);x++){if(x<0||y<0||x>=w||y>=h)continue;const j=((h-1-y)*w+x)*4,diff=(v,u)=>Math.max(...[0,1,2].map(c=>Math.abs(v[j+c]-u[j+c])));if(diff(front,background)>16){total++;if(diff(actual,front)>16)covered++;}}
     b.frame=frame;a.drawWorld=world;a.render();result.push({name,x:n.x,y:n.y,pixels:total,covered,occludedRatio:covered/total});
    }b.text=text;a.render();return result;
   },fixture);
   await p.screenshot({path:`reports/platform-${mode}-${fixture.name}-dpr${dpr}.png`});if(fixture.name==='doctor-platform')await p.screenshot({path:`reports/platform-${mode}-closeup-dpr${dpr}.png`,clip:{x:80,y:180,width:270,height:200}});cases.push({fixture:fixture.name,dpr,npcs:results});for(const r of results){assert.ok(r.pixels>100);if(!baseline)assert.ok(r.occludedRatio<.01,`${r.name}: platform covers NPC body`);}
  }
  await p.evaluate(()=>lpLegend.dispose());await p.close();
 }
 assert.deepEqual(errors,[]);await fs.writeFile(`reports/platform-layering-${mode}.json`,JSON.stringify({passed:true,cases,errors},null,2));console.log(JSON.stringify({mode,cases,errors}));
}finally{await browser.close();}
