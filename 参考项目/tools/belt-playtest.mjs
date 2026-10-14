import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
import {beltScenario} from './belt-scenario.mjs';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),checks=[],errors=[];
try{for(const viewport of [{width:375,height:812},{width:430,height:932}]){
 const context=await browser.newContext({viewport,deviceScaleFactor:viewport.width===375?2:1});context.setDefaultTimeout(60000);const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
 const result=await page.evaluate(beltScenario);await page.screenshot({path:`reports/belt-battle-${viewport.width}.png`});
 await page.evaluate(()=>{lpLegend.tab='背包';lpLegend.selectedBelt=0;lpLegend.render();});await page.screenshot({path:`reports/belt-bag-${viewport.width}.png`});
 const pagination=await page.evaluate(async()=>{
  const a=lpLegend,p=a.player,original=JSON.parse(JSON.stringify(p));
  p.inventory=Array.from({length:15},(_,i)=>({itemId:252+i,quantity:1}));p.inventory.push({itemId:1,quantity:1});a.tab='背包';a.selectedBelt=null;a.selectedItem=1;a.page=1;a.render();
  if(!a.buttons.some(b=>b.label==='金创药中')||!a.buttons.some(b=>b.label==='下一页'))throw Error('Second bag page omitted its item');
  const b=a.buttons.find(b=>b.label==='放入腰带');await a.pointer(a.left+(b.x+b.w/2)*a.scale,a.top+(b.y+b.h/2)*a.scale);a.render();
  if(a.page!==0||a.buttons.some(b=>b.label==='下一页')||p.inventory.length!==15)throw Error('Belt transfer left an empty bag page');
  Object.assign(p,original);a.page=0;a.selectedBelt=0;a.save();a.render();return {lastPageMoveClamped:true};
 });
 await page.reload();await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);await page.evaluate(()=>lpLegend.platform.cancel(lpLegend.frame));assert.deepEqual(await page.evaluate(()=>lpLegend.player.belt),result.belt);
 await page.evaluate(async()=>{await lpLegend.gmCommand('清档');if(lpLegend.player.belt.some(Boolean))throw Error('GM clear retained belt items');lpLegend.dispose();});checks.push({viewport,...result,...pagination,fullPageReload:true,gmClear:true});await context.close();
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/belt-playtest.json',JSON.stringify({passed:true,checks,errors,wechatDeviceTested:false},null,2));console.log({passed:true,viewports:2,errors});
}finally{await browser.close();}
