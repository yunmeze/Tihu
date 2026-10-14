import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {enterGame} from './enter-game.mjs';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}),checks=[],errors=[];
try{for(const viewport of [{width:375,height:812},{width:430,height:932}]){
 const context=await browser.newContext({viewport,deviceScaleFactor:1});context.setDefaultTimeout(60000);const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);
 const click=async label=>{const point=await page.evaluate(label=>{const a=lpLegend;a.render();const b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing chapter control '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);await page.mouse.click(point.x,point.y);await page.waitForFunction(()=>!lpLegend.entering&&!lpLegend.npcBusy&&!lpLegend.preparing);await page.evaluate(()=>lpLegend.render());};
 await click('踏入江湖');await click('创建角色');await page.evaluate(()=>lpLegend.platform.cancel(lpLegend.frame));
 assert.equal(await page.evaluate(()=>lpLegend.player.creationProfile),'native-classes-v2');assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),3);assert.equal(await page.evaluate(()=>lpLegend.player.inventory.length),0);
 const approach=async()=>{await click('任务');await click('与村长对话');await page.evaluate(async()=>{const a=lpLegend;for(let i=0;i<2500&&a.pendingNpc;i++){a.combat.update(.05);a.elapsed+=.05;a.hero=a.combat.position;await a.checkNpcInteraction();}a.camera={x:a.hero.x,y:a.hero.y};await a.prepareVisible();a.render();if(!a.npcDialogue)throw Error('Village chief approach did not open dialogue');});};
 await approach();for(const action of ['A2','A3','A4','A5','OVER']){const label=await page.evaluate(action=>{const choice=lpLegend.npcDialogue?.choices.find(c=>c.action===action);if(!choice)throw Error('Missing village chief action '+action);return choice.label;},action);await click(label);}
 const accepted=await page.evaluate(()=>{const a=lpLegend;a.save();return {event:a.player.events[0],gold:a.player.gold,inventory:a.player.inventory,flags:a.mapFlagsByMap.A00};});assert.equal(accepted.event,4);assert.equal(accepted.gold,100);assert.deepEqual(accepted.inventory.map(e=>[e.itemId,e.quantity]),[[0,3],[5,3]]);assert.equal(accepted.flags.length,9);
 await click('任务');await page.screenshot({path:`reports/first-quest-accepted-${viewport.width}.png`});await click('战斗');
 await page.reload();await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);await page.evaluate(()=>lpLegend.platform.cancel(lpLegend.frame));assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),4);
 const travel=async(targetId)=>{
  await click('任务');await click({A01:'前往北门',A02:'前往树林深处',A03:'前往南门'}[targetId]);const start=await page.evaluate(()=>{const a=lpLegend;return {map:a.mapId,destination:a.combat.path.at(-1),route:a.combat.path.length};});
  const progress=await page.evaluate(async()=>{const a=lpLegend;for(let i=0;i<10000;i++){a.elapsed+=.05;a.combat.update(.05);a.hero=a.combat.position;a.checkPortal();if(a.changing)return {transition:true,steps:i};if(!a.combat.path.length&&a.combat.position.actionTime<=0&&!a.combat.targetId)return {transition:false,position:{x:a.hero.x,y:a.hero.y},hp:a.player.hp};}return {transition:false,reason:'step budget',hp:a.player.hp};});
  if(!progress.transition)throw Error('Chapter portal did not transition '+JSON.stringify({targetId,start,progress}));await page.waitForFunction(id=>lpLegend.mapId===id&&!lpLegend.changing&&!lpLegend.preparing,targetId);await page.evaluate(async()=>{const a=lpLegend;a.camera={x:a.hero.x,y:a.hero.y};await a.prepareVisible();a.render();});return {from:start.map,to:targetId,route:start.route,steps:progress.steps};
 };
 const north=await travel('A01');await page.screenshot({path:`reports/first-quest-north-${viewport.width}.png`});
 // Explicit durability fixture beyond village exit: isolate quest routing and
 // native boss-death effects from the time needed to level a new character.
 await page.evaluate(()=>{lpLegend.player.base.hp=lpLegend.player.hp=100000;});const forest=await travel('A02');
 const boss=await page.evaluate(()=>{const a=lpLegend,u=a.combat.units.find(u=>u.definition.name==='甲虫王');if(!u)throw Error('Missing native beetle king');a.combat.kill(u);a.combat.stopFarming();return {nativeId:u.definition.id,event:a.player.events[0],script:a.combat.lastScript};});assert.equal(boss.event,5);
 await page.evaluate(async()=>{await lpLegend.changeMap('A00');});await approach();assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),6);const over=await page.evaluate(()=>lpLegend.npcDialogue.choices.find(c=>c.action==='OVER').label);await click(over);const south=await travel('A03');
 await page.evaluate(()=>{lpLegend.save();lpLegend.dispose();});checks.push({viewport,newCharacterViaUI:true,completeChiefDialogue:true,taskNavigation:true,accepted,saveReloadBeforeExit:true,north,forest,bossEvent:boss.event,south,secondChiefEvent:6,durabilityFixtureAfterVillage:true});await context.close();
 }assert.deepEqual(errors,[]);await fs.writeFile('reports/first-quest-playtest.json',JSON.stringify({passed:true,checks,errors,fullGameTraversal:false},null,2));console.log({passed:true,viewports:2,northExit:true,bossQuest:true,southExit:true});
}finally{await browser.close();}
