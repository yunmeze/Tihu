import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const checks=[],errors=[];
try{for(const config of [{width:375,height:812,dpr:2},{width:430,height:932,dpr:1}]){
 const context=await browser.newContext({viewport:{width:config.width,height:config.height},deviceScaleFactor:config.dpr}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);assert.equal(await page.evaluate(()=>globalThis.lpLegendError),undefined);
 const fixture=await page.evaluate(()=>{
  const a=lpLegend,c=a.combat;a.platform.cancel(a.frame);a.render();a.pathTestNotifications=[];const notify=a.notify.bind(a);a.notify=message=>{a.pathTestNotifications.push(message);notify(message);};
  const start={x:Math.round(a.hero.x),y:Math.round(a.hero.y)};let chosen=null;
  for(let radius=2;radius<=8&&!chosen;radius++)for(let dx=-radius;dx<=radius&&!chosen;dx++)for(let dy=-radius;dy<=radius&&!chosen;dy++){
   if(Math.max(Math.abs(dx),Math.abs(dy))!==radius)continue;const target={x:start.x+dx,y:start.y+dy},point=a.screenPoint(target.x,target.y);
   if(c.walkable(target.x,target.y)||point.x<190||point.x>535||point.y<200||point.y>900||a.map.npcs.some(n=>a.hitNpc(point,n))||c.units.some(u=>u.alive&&Math.hypot(point.x-a.screenPoint(u.x,u.y).x,point.y-a.screenPoint(u.x,u.y).y+35)<50))continue;
   const before=performance.now();if(!c.moveTo(target.x,target.y)||c.path.length<2)continue;const route=c.path.map(p=>({...p}));chosen={start,target,end:route.at(-1),steps:route.length,searchMs:performance.now()-before,route,pixel:{x:a.left+point.x*a.scale,y:a.top+point.y*a.scale}};
  }
  if(!chosen)throw Error('No unobstructed blocked native-map click fixture');c.startFarming(4);a.render();return chosen;
 });
 await page.screenshot({path:`reports/pathfinding-before-${config.width}.png`});await page.mouse.click(fixture.pixel.x,fixture.pixel.y);
 const result=await page.evaluate(async fixture=>{
  const a=lpLegend,c=a.combat;if(c.farmType!==null)throw Error('Manual fallback did not cancel farming');if(!c.path.length)throw Error('Blocked click remained stationary');if(JSON.stringify(c.path.at(-1))!==JSON.stringify(fixture.end))throw Error('Wrong nearest endpoint');
  let previous=fixture.start;for(const p of c.path){if(!c.walkable(p.x,p.y))throw Error('Route entered a wall');const dx=p.x-previous.x,dy=p.y-previous.y;if(dx&&dy&&(!c.walkable(previous.x+dx,previous.y)||!c.walkable(previous.x,previous.y+dy)))throw Error('Route crossed a blocked corner');previous=p;}
  for(let i=0;i<1500&&c.path.length;i++)c.update(.05);a.hero=c.position;a.camera={x:a.hero.x,y:a.hero.y};await a.prepareVisible();a.render();
  return {end:{x:a.hero.x,y:a.hero.y},notifications:a.pathTestNotifications,moved:Math.hypot(a.hero.x-fixture.start.x,a.hero.y-fixture.start.y)>0,noPendingPath:c.path.length===0};
 },fixture);
 assert.deepEqual(result.end,fixture.end);assert.equal(result.moved,true);assert.equal(result.noPendingPath,true);assert.deepEqual(result.notifications,[]);await page.screenshot({path:`reports/pathfinding-after-${config.width}.png`});
 checks.push({viewport:config,fixture,result});await page.evaluate(()=>lpLegend.dispose());await context.close();
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/pathfinding-playtest.json',JSON.stringify({passed:true,checks,errors},null,2));console.log({passed:true,viewports:checks.length,searchMs:checks.map(c=>c.fixture.searchMs),errors});
}finally{await browser.close();}
