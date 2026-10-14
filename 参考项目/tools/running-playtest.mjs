import {ownedTestBrowser} from './owned-test-browser.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
import {runningScenario} from './running-scenario.mjs';
const owned=await ownedTestBrowser('automatic-running'),browser=owned.browser,checks=[],errors=[];
try{for(const viewport of [{width:375,height:812},{width:430,height:932}]){
 const context=await browser.newContext({viewport,deviceScaleFactor:viewport.width===375?2:1});context.setDefaultTimeout(60000);const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
 const result=await page.evaluate(runningScenario);await page.screenshot({path:`reports/running-touch-${viewport.width}.png`});
 await page.evaluate(start=>{const a=lpLegend,c=a.combat;c.stopFarming();Object.assign(c.position,start);a.lastMoveTap=null;a.render();a.platform.canvas.addEventListener('contextmenu',e=>a.lastContextMenuPrevented=e.defaultPrevented);},result.start);
 await page.mouse.click(result.nearPixel.clientX,result.nearPixel.clientY);assert.equal(await page.evaluate(()=>lpLegend.combat.moveMode),'walk');await page.evaluate(()=>lpLegend.combat.update(.02));await page.mouse.click(result.nearPixel.clientX,result.nearPixel.clientY,{button:'right'});assert.equal(await page.evaluate(()=>lpLegend.combat.moveMode),'walk');assert.equal(await page.evaluate(()=>lpLegend.lastContextMenuPrevented),true);await page.mouse.click(result.farPixel.clientX,result.farPixel.clientY);assert.equal(await page.evaluate(()=>lpLegend.combat.moveMode),'run');
 await page.evaluate(()=>{for(let i=0;i<15;i++)lpLegend.combat.update(.02);lpLegend.hero=lpLegend.combat.position;lpLegend.render();});await page.screenshot({path:`reports/running-mouse-${viewport.width}.png`});
 // Check actual browser PointerEvents also forward the touch type/time.
 await page.evaluate(()=>{const a=lpLegend;a.lastMoveTap=null;const point=a.screenPoint(a.combat.position.x+1,a.combat.position.y),canvas=a.platform.canvas;for(let i=0;i<2;i++){const data={bubbles:true,clientX:a.left+point.x*a.scale,clientY:a.top+point.y*a.scale,pointerType:'touch',pointerId:91,button:0};canvas.dispatchEvent(new PointerEvent('pointerdown',data));canvas.dispatchEvent(new PointerEvent('pointerup',data));}if(a.combat.moveMode!=='walk')throw Error('Repeated near touch must remain walking');a.dispose();});
 checks.push({viewport,...result,desktopAutomaticPace:true,rightButtonSamePace:true,contextMenuSuppressed:true,browserTouchEvents:true});await context.close();
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/running-playtest.json',JSON.stringify({passed:true,checks,errors,wechatDeviceTested:false},null,2));console.log({passed:true,viewports:2,automaticPace:true,touchSingleAndDouble:true,errors});
}finally{await owned.close();}
