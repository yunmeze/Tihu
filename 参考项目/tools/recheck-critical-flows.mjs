import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';

const dir='reports/game-recheck-20261012',owned=await ownedTestBrowser('recheck-critical-flows'),browser=owned.browser,checks=[],errors=[];
try{
 for(const viewport of [{width:375,height:812,dpr:2},{width:430,height:932,dpr:1}]){
  const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:viewport.dpr});context.setDefaultTimeout(60000);
  try{
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   const settle=async()=>{await page.waitForFunction(()=>!lpLegend.entering&&!lpLegend.changing&&!lpLegend.preparing&&!lpLegend.npcBusy&&!lpLegend.serviceBusy&&!lpLegend.appearanceLoading&&!lpLegend.entry.previewLoading);await page.evaluate(()=>{lpLegend.platform.cancel(lpLegend.frame);lpLegend.audio.pause(true);lpLegend.render();});};
   const click=async(label)=>{const p=await page.evaluate(label=>{const a=lpLegend,b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);await page.mouse.click(p.x,p.y);await settle();};
   const walk=async()=>{
    const result=await page.evaluate(async()=>{const a=lpLegend;let steps=0;for(;steps<10000&&!a.npcDialogue&&!a.serviceView;steps++){a.elapsed+=.02;a.combat.update(.02);a.hero=a.combat.position;await a.checkNpcInteraction();a.checkPortal();while(a.changing||a.preparing||a.npcBusy)await new Promise(r=>setTimeout(r,5));if(steps>20&&!a.combat.path.length&&!a.pendingNpc)break;}a.camera={x:a.hero.x,y:a.hero.y};await a.prepareVisible();a.render();return {steps,npc:a.npcDialogue?.name||a.serviceView?.name,map:a.mapId,pending:a.pendingNpc,position:{x:a.hero.x,y:a.hero.y}};});await settle();return result;
   };
   const approach=async name=>{await page.evaluate(async name=>{const a=lpLegend,index=a.map.npcs.findIndex(n=>n.name===name);if(index<0)throw Error('Missing NPC '+name);await a.selectNpc(index);},name);const result=await walk();assert.equal(result.npc,name);return result;};
   await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>lpLegendReady);await settle();await click('踏入江湖');await click('创建角色');
   assert.equal(await page.evaluate(()=>lpLegend.combat.story.kind),'opening');await click('下一页');
   await page.reload();await page.waitForFunction(()=>lpLegendReady);await settle();await click('再续前缘');await click('再续前缘');assert.equal(await page.evaluate(()=>lpLegend.combat.story.page),1);
   for(let i=1;i<5;i++)await click(i===4?'进入梦境':'下一页');
   for(const name of ['方丈','凌云子']){await approach(name);for(let i=0;i<12;i++){const label=await page.evaluate(()=>lpLegend.npcDialogue?.choices[0]?.label);if(!label)break;await click(label);}}
   assert.deepEqual(await page.evaluate(()=>({map:lpLegend.mapId,event:lpLegend.player.events[0],position:{x:lpLegend.hero.x,y:lpLegend.hero.y}})),{map:'A00',event:3,position:{x:138,y:12}});
   await click('任务');await click('与村长对话');const chief=await walk();assert.equal(chief.npc,'海曦村长');await page.screenshot({path:`${dir}/chief-after-house-${viewport.width}.png`});
   for(const action of ['A2','A3','A4','A5','OVER']){const label=await page.evaluate(action=>lpLegend.npcDialogue.choices.find(c=>c.action===action)?.label,action);assert.ok(label);await click(label);}assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),4);
   await click('角色');const stats=[];
   for(let i=0;i<4;i++){
    const state=await page.evaluate(()=>{const a=lpLegend,old=a.batch.text,text=[];a.batch.text=function(value,...args){text.push(String(value));return old.call(this,value,...args);};try{a.render();}finally{a.batch.text=old;}return {label:a.buttons.find(b=>b.label.startsWith('属性 '))?.label,text};});assert.equal(state.label,`属性 ${i+1}/4`);stats.push(state);
    if(i===3)await page.screenshot({path:`${dir}/character-last-stats-${viewport.width}.png`});await click(state.label);
   }
   assert.ok(stats[3].text.some(t=>t.startsWith('时间挑战 ')));assert.ok(stats[3].text.some(t=>t.startsWith('通关次数 ')));
   await click('任务');await click('前往北门');await walk();assert.equal(await page.evaluate(()=>lpLegend.mapId),'A01');
   await page.evaluate(async()=>{await lpLegend.changeMap('A00',null,{debug:true,unlock:true});});await settle();
   await approach('储物箱');assert.equal(await page.evaluate(()=>lpLegend.tab),'背包');const bagBefore=await page.evaluate(()=>JSON.stringify(lpLegend.player.inventory)),goldBefore=await page.evaluate(()=>lpLegend.player.gold);
   await click('存入');assert.equal(await page.evaluate(()=>lpLegend.player.storage.items.length),1);await click('取出');assert.equal(await page.evaluate(()=>JSON.stringify(lpLegend.player.inventory)),bagBefore);
   await click('存金币');await click('取金币');assert.equal(await page.evaluate(()=>lpLegend.player.gold),goldBefore);await page.screenshot({path:`${dir}/storage-roundtrip-${viewport.width}.png`});await click('关闭窗口');
   await approach('海曦小贩');await click('看看你的东西');const sword=await page.evaluate(()=>lpLegend.content.itemNames.get('木剑').id);await click('窗口物品:'+sword);await click('购买');
   assert.equal(await page.evaluate(()=>lpLegend.player.inventory.find(e=>lpLegend.content.items[e.itemId].name==='木剑')?.quantity),1);await page.screenshot({path:`${dir}/shop-properties-${viewport.width}.png`});await click('我要卖东西');await click('木剑');await click('出售');assert.equal(await page.evaluate(()=>lpLegend.player.inventory.some(e=>lpLegend.content.items[e.itemId].name==='木剑')),false);await click('关闭窗口');
   await click('菜单');await click('保存退出');await click('再续前缘');await page.screenshot({path:`${dir}/saved-preview-${viewport.width}.png`});await click('再续前缘');assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),4);
   // Explicit ground movement cancels the pending house-exit NPC journey.
   await page.evaluate(async()=>{const a=lpLegend;await a.changeMap('A00',{x:138,y:12},{debug:true,unlock:true});a.player.events[0]=3;a.camera={x:a.hero.x,y:a.hero.y};await a.followFirstQuest();a.render();const x=a.left+375*a.scale,y=a.top+(555+32*a.worldScale)*a.scale;await a.pointer(x,y,{pointerType:'mouse',button:0});a.render();});assert.equal(await page.evaluate(()=>lpLegend.pendingNpc),null);await walk();assert.ok(await page.evaluate(()=>lpLegend.hero.x>130));
   checks.push({viewport,openingSaveReload:true,nativeOpeningNpcSequence:true,chiefFromInsideHouse:chief,completeChiefDialogue:true,northExit:true,characterStatPages:stats.map(s=>s.label),storageItemAndGoldRoundtrip:true,shopBuySell:true,homeAndResume:true,manualMoveCancelsNpcRoute:true});await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(`${dir}/critical-flows.json`,JSON.stringify({passed:true,checks,errors},null,2));console.log({passed:true,viewports:checks.length,checks:checks.map(c=>({...c,viewport:c.viewport.width})),errors});
}finally{await owned.close();}
