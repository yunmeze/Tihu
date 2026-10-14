import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';

const dir='reports/mode-removal-20261014',checks=[],errors=[];
await fs.mkdir(dir,{recursive:true});
const owned=await ownedTestBrowser('mode-removal-20261014');
const timer=setTimeout(()=>owned.close().catch(()=>{}),180000);
try{
 for(const width of [375,430]){
  const context=await owned.browser.newContext({viewport:{width,height:width===375?812:932}}),page=await context.newPage();
  page.setDefaultTimeout(60000);
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
  const ready=async()=>{
   await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);
   assert.equal(await page.evaluate(()=>globalThis.lpLegendError),undefined);
   await page.evaluate(()=>{lpLegend.platform.cancel(lpLegend.frame);lpLegend.audio.pause(true);lpLegend.render();});
  };
  const settle=async()=>{
   await page.waitForFunction(()=>!lpLegend.entering&&!lpLegend.changing&&!lpLegend.preparing&&!lpLegend.entry.previewLoading&&!lpLegend.npcBusy);
   await page.evaluate(()=>lpLegend.render());
  };
  const click=async label=>{
   const p=await page.evaluate(label=>{const a=lpLegend,b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);
   await page.mouse.click(p.x,p.y);await settle();
  };
  try{
   await page.goto('http://127.0.0.1:5180');await ready();
   assert.deepEqual(await page.evaluate(()=>lpLegend.buttons.map(b=>b.label)),['声音','踏入江湖']);
   await page.screenshot({path:`${dir}/home-${width}.png`});checks.push({width,kind:'original-home'});
   await click('踏入江湖');await click('创建角色');
   const creation=await page.evaluate(()=>{const a=lpLegend;return {class:a.player.class,hp:a.player.hp,mp:a.player.mp,skills:a.player.skills,story:a.combat.story.kind,combat:a.combat.constructor.name};});
   assert.equal(creation.class,'战士');assert.equal(creation.hp,25);assert.equal(creation.mp,5);assert.deepEqual(creation.skills,[]);assert.equal(creation.story,'opening');assert.equal(creation.combat,'Combat');
   await page.screenshot({path:`${dir}/opening-${width}.png`});checks.push({width,kind:'original-new-character',...creation});
   for(let i=0;i<5;i++)await click(i===4?'进入梦境':'下一页');
   for(const name of ['方丈','凌云子']){
    await page.evaluate(async name=>{const a=lpLegend;await a.selectNpc(a.map.npcs.findIndex(n=>n.name===name));for(let i=0;i<300&&a.combat.path.length;i++)a.combat.update(.02);a.hero=a.combat.position;await a.checkNpcInteraction();a.render();},name);
    for(let i=0;i<8;i++){const label=await page.evaluate(()=>lpLegend.npcDialogue?.choices[0]?.label||null);if(!label)break;await click(label);}
   }
   assert.equal(await page.evaluate(()=>lpLegend.mapId),'A00');
   assert.equal(await page.evaluate(()=>lpLegend.player.events[0]),3);
   checks.push({width,kind:'original-opening-and-village'});
   // Model the actual v2 shape produced by the retired mode. Its top-level
   // world is the original map; retired stage position must never replace it.
   const fixture=await page.evaluate(async()=>{
    const a=lpLegend;await a.changeMap('A03',{x:26,y:78},{unlock:true});
    const weapon=a.content.itemNames.get('木剑').id;a.player.equipment.weapon=weapon;
    a.player.inventory.push({itemId:a.content.itemNames.get('金创药小').id,quantity:2});a.player.gold=713;a.player.experience=3;
    const animal=a.content.monsterNames.get('鸡');a.combat.waitingPets.push({definition:{...animal},monsterId:animal.id,hp:Math.min(4,animal.hp),alive:true,summoned:true,summonSkill:'江湖召唤',petLevel:2,petKills:7,statuses:{}});a.combat.restoreWaitingPets();
    const ground={id:'A03:loot:42',kind:'item',itemId:weapon,quantity:1,x:28,y:78};a.combat.groundByMap.A03.push(ground);
    await a.updateAppearance();await a.prepareVisible();a.save();
    const root=a.platform.load(),original=JSON.parse(JSON.stringify(root));
    const mark=state=>{state.playStyle='side';state.sideAdventure={version:1,stage:2,wave:4,position:{x:61,y:4},status:'cleared'};state.player.sideSupplies=true;};
    mark(root);for(const r of root.characters)mark(r.state);
    const inactive=JSON.parse(JSON.stringify(root.characters[0]));inactive.id='character-2';inactive.state.player.name='青云';inactive.state.player.gold=99;root.characters.push(inactive);
    a.dispose();a.platform.save(root);return original;
   });
   await page.reload();await ready();
   assert.deepEqual(await page.evaluate(()=>lpLegend.buttons.map(b=>b.label)),['声音','踏入江湖','再续前缘','自废武功']);
   assert.equal(await page.evaluate(()=>lpLegend.roster.characters.length),2);
   assert.equal(await page.evaluate(()=>lpLegend.roster.characters.every(r=>!('playStyle' in r.state)&&!('sideAdventure' in r.state)&&!('sideSupplies' in r.state.player))),true);
   await click('再续前缘');await click('再续前缘');
   const resumed=await page.evaluate(()=>{const a=lpLegend;return {map:a.mapId,position:{x:a.hero.x,y:a.hero.y},combat:a.combat.constructor.name,player:JSON.parse(JSON.stringify(a.player)),pets:JSON.parse(JSON.stringify(a.combat.savePets())),ground:a.combat.groundByMap,script:a.scriptState,flags:a.mapFlagsByMap};});
   assert.equal(resumed.map,fixture.map);assert.deepEqual(resumed.position,fixture.position);assert.equal(resumed.combat,'Combat');
   for(const key of ['gold','experience','level','equipment','inventory','skills','events'])assert.deepEqual(resumed.player[key],fixture.player[key]);
   assert.deepEqual(resumed.pets,fixture.pets);assert.deepEqual(resumed.ground,fixture.groundItems);assert.deepEqual(resumed.script,fixture.scriptState);assert.deepEqual(resumed.flags,fixture.mapFlagsByMap);
   await page.screenshot({path:`${dir}/restored-world-${width}.png`});checks.push({width,kind:'retired-save-resumes-original-world',map:resumed.map,position:resumed.position,equipmentAndGrowth:true,questsAndGround:true,pets:true});
   for(const tab of ['背包','角色','技能','任务','战斗'])await click(tab);
   await click('菜单');await click('保存退出');checks.push({width,kind:'original-navigation-and-exit'});
   const saved=await page.evaluate(()=>lpLegend.platform.load());
   assert.equal(saved.characters.length,2);assert.equal(saved.characters.find(r=>r.id==='character-2').state.player.gold,99);
   for(const state of [saved,...saved.characters.map(r=>r.state)]){assert.equal('playStyle' in state,false);assert.equal('sideAdventure' in state,false);assert.equal('sideSupplies' in state.player,false);}
   await page.reload();await ready();await click('再续前缘');await click('再续前缘');
   assert.equal(await page.evaluate(()=>lpLegend.mapId),fixture.map);assert.equal(await page.evaluate(()=>lpLegend.player.gold),713);
   checks.push({width,kind:'clean-save-roundtrip-and-inactive-character'});
   await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(dir+'/playtest.json',JSON.stringify({passed:true,cases:checks.length,checks,errors,wechatDeviceTested:false},null,2));
 console.log({passed:true,cases:checks.length,originalHome:true,originalGameplay:true,retiredSaveMigration:true});
}finally{clearTimeout(timer);await owned.close();}
