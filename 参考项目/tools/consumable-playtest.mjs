import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
import {consumableScenario} from './consumable-scenario.mjs';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),checks=[],errors=[];
try{for(const viewport of [{width:375,height:812},{width:430,height:932}]){
 const context=await browser.newContext({viewport,deviceScaleFactor:1});context.setDefaultTimeout(60000);const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
 const result=await page.evaluate(consumableScenario);await page.screenshot({path:`reports/consumable-battle-${viewport.width}.png`});
 await page.evaluate(()=>{lpLegend.tab='背包';lpLegend.selectedBelt=1;lpLegend.render();});await page.screenshot({path:`reports/consumable-bag-${viewport.width}.png`});
 await page.reload();await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);await page.evaluate(()=>lpLegend.platform.cancel(lpLegend.frame));
 assert.deepEqual(await page.evaluate(()=>lpLegend.player.belt),result.belt);assert.deepEqual(await page.evaluate(()=>lpLegend.player.inventory),result.inventory);assert.equal(await page.evaluate(()=>lpLegend.player.returnTown),'A00');
 await page.evaluate(()=>lpLegend.dispose());checks.push({viewport,...result,fullPageReload:true});await context.close();
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/consumable-playtest.json',JSON.stringify({passed:true,checks,errors,wechatDeviceTested:false},null,2));console.log({passed:true,viewports:checks.length,errors});
}finally{await browser.close();}
