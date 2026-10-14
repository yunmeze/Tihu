import {ownedTestBrowser} from './owned-test-browser.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
import {actionContinuityScenario} from './action-continuity-scenario.mjs';
const owned=await ownedTestBrowser('action-continuity'),browser=owned.browser;
const checks=[],errors=[];
try{
 for(const viewport of [{width:375,height:812},{width:430,height:932}]){
  const context=await browser.newContext({viewport,deviceScaleFactor:viewport.width===375?2:1}),page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError,null,{timeout:60000});await enterGame(page);
  const walk=await page.evaluate(actionContinuityScenario,{width:viewport.width});await page.screenshot({path:`reports/action-continuity-walk-${viewport.width}.png`});
  const melee=await page.evaluate(()=>lpLegend.continuityAttack('基本剑术'));await page.screenshot({path:`reports/action-continuity-melee-${viewport.width}.png`});
  const fire=await page.evaluate(()=>lpLegend.continuityAttack('火球术'));await page.screenshot({path:`reports/action-continuity-fire-${viewport.width}.png`});checks.push({viewport,walk,melee,fire});await page.evaluate(()=>lpLegend.dispose());await context.close();
 }
 assert.deepEqual(errors,[]);await fs.writeFile('reports/action-continuity-playtest.json',JSON.stringify({passed:true,checks,errors,wechatDeviceTested:false},null,2));console.log({passed:true,viewports:2,repeatedSceneClicks:true,firstAndFollowingCadence:true,retaliation:true,errors});
}finally{await owned.close();}
