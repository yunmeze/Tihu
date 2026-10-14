import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';
const dir='reports/hero-hurt-20261013',results=[],errors=[];
await fs.mkdir(dir,{recursive:true});const owned=await ownedTestBrowser('hero-hurt-20261013');
const timer=setTimeout(()=>owned.close().catch(()=>{}),180000);
try{
 for(const width of [375,430]){
  const context=await owned.browser.newContext({viewport:{width,height:width===375?812:932}}),page=await context.newPage();page.setDefaultTimeout(60000);
  page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
  try{
   await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
   await page.evaluate(async()=>{
    const a=lpLegend;a.platform.cancel(a.frame);a.audio.pause(true);a.player.events[0]=3;await a.changeMap('A03',{x:26,y:78},{debug:true});a.platform.cancel(a.frame);
    const anim=await import('/src/animation.js'),appearance=await import('/src/appearance.js');globalThis.hurtQA={anim,appearance};
    globalThis.resetHurt=async()=>{
     const c=a.combat;c.enter(a.map,{x:26,y:78});const u=c.units[2];if(!u)throw Error('Missing native fixture spawn');
     Object.assign(u,{name:'鸡',x:27,y:78,hp:10000});u.definition={...a.content.monsterNames.get('鸡'),hp:10000,attack:10,behavior:-1,vision:0,speed:0,regenFrames:0,defense:0,magicDefense:0,physicalEvade:0,magicEvade:0,freeze:0,burn:0,poison:0,paralysis:0};
     a.units=c.units=[u];a.player.hp=a.player.base.hp=10000;a.player.mp=a.player.base.mp=10000;a.player.statuses={};a.player.equipment={weapon:298,armor:252};a.player.equipmentMeta={};a.player.autoSkills=[];a.player.magicShieldFrames=0;a.player.invisible=false;c.battleRandom=c.monsterRandom=()=>.5;c.events=[];c.stopFarming();
     a.hero=c.position;a.camera={...c.position};a.tab='战斗';a.npcDialogue=a.featureView=a.serviceView=null;a.systemMenu=false;a.message=null;
     await a.prepareVisible();a.render();return u.id;
    };
    globalThis.advanceHurt=async n=>{for(let i=0;i<n;i++)a.combat.update(.02);a.hero=a.combat.position;await a.prepareVisible();a.render();return {action:a.hero.action,index:a.animationFrame(a.hero),x:a.hero.x,y:a.hero.y};};
   });
   await page.evaluate(()=>resetHurt());
   const hit=await page.evaluate(()=>{const a=lpLegend,c=a.combat,before=a.animationFrame(a.hero),hp=a.player.hp;c.enemyHit(c.units[0]);c.stopFarming();a.render();return {before,index:a.animationFrame(a.hero),action:a.hero.action,damage:hp-a.player.hp};});
   assert.equal(hit.action,'hurt');assert.equal(hit.before,hit.index);assert.ok(hit.damage>0);results.push({width,kind:'landed-hit',...hit});
   const phases=[];for(let phase=0;phase<3;phase++){const state=await page.evaluate(()=>advanceHurt(5));assert.equal(state.index,237+phase);assert.equal(state.x,26);assert.equal(state.y,78);phases.push(state);await page.screenshot({path:`${dir}/hurt-${width}-${phase}.png`});}
   const done=await page.evaluate(()=>advanceHurt(5));assert.equal(done.action,'idle');results.push({width,kind:'three-visible-phases-and-recovery',phases,done});
   const layers=await page.evaluate(()=>{const a=lpLegend,c=a.combat,rows=[];for(let direction=0;direction<8;direction++){hurtQA.anim.setAction(c.position,'idle');c.position.direction=direction;c.enemyHit(c.units[0]);c.stopFarming();for(const t of [.1,.2,.3]){c.position.animationElapsed=t;rows.push(hurtQA.appearance.avatarLayers(a.appearance,c.position).map(l=>({part:l.part,index:l.index,valid:!!a.packs.get(l.pack)?.frames[l.index]})));}}return rows;});assert.equal(layers.length,24);for(const row of layers){assert.ok(row.every(l=>l.valid));assert.equal(new Set(row.map(l=>l.index)).size,1);}results.push({width,kind:'eight-direction-equipment-sync',poses:layers.length});
   await page.evaluate(()=>resetHurt());
   const click=await page.evaluate(()=>{const a=lpLegend,c=a.combat;c.enemyHit(c.units[0]);c.stopFarming();const p=a.screenPoint(29,78);return {x:a.left+(p.x+24*a.worldScale)*a.scale,y:a.top+(p.y+16*a.worldScale)*a.scale};});
   await page.mouse.click(click.x,click.y);
   const queued=await page.evaluate(()=>({manual:lpLegend.combat.manualPath,length:lpLegend.combat.path.length,action:lpLegend.hero.action}));assert.ok(queued.manual);assert.ok(queued.length);assert.equal(queued.action,'hurt');
   const waiting=await page.evaluate(()=>advanceHurt(19));assert.equal(waiting.x,26);const moved=await page.evaluate(()=>advanceHurt(180));assert.ok(moved.x>27);await page.screenshot({path:`${dir}/movement-${width}.png`});results.push({width,kind:'real-click-queues-movement',queued,waiting,moved});
   await page.evaluate(()=>resetHurt());
   const attack=await page.evaluate(()=>{const a=lpLegend,c=a.combat;c.select(c.units[0].id);c.update(.02);const before=c.heroWindup,remaining=before.remaining;c.enemyHit(c.units[0]);const preserved=c.heroWindup===before&&before.remaining===remaining,action=c.position.action;c.stopFarming();return {preserved,action};});assert.ok(attack.preserved);assert.equal(attack.action,'attack');results.push({width,kind:'attack-not-interrupted',...attack});
   await page.evaluate(()=>resetHurt());
   const absorbed=await page.evaluate(()=>{const a=lpLegend,c=a.combat;a.player.equipment.ringLeft=a.content.itemNames.get('护身戒指').id;const hp=a.player.hp,mp=a.player.mp;c.enemyHit(c.units[0],null,{magic:true});c.stopFarming();return {action:c.position.action,hpLoss:hp-a.player.hp,mpLoss:mp-a.player.mp};});assert.equal(absorbed.action,'hurt');assert.equal(absorbed.hpLoss,0);assert.ok(absorbed.mpLoss>0);results.push({width,kind:'ring-absorption-reaction',...absorbed});
   await page.evaluate(()=>resetHurt());
   const paused=await page.evaluate(()=>{const a=lpLegend;a.combat.enemyHit(a.combat.units[0]);a.combat.stopFarming();a.systemMenu=true;const before=a.hero.animationElapsed;a.lastTime=0;a.tick(20);a.platform.cancel(a.frame);a.systemMenu=false;return {before,after:a.hero.animationElapsed,action:a.hero.action};});assert.equal(paused.before,paused.after);assert.equal(paused.action,'hurt');results.push({width,kind:'menu-pauses-reaction',...paused});
  }finally{await page.evaluate(()=>globalThis.lpLegend?.dispose()).catch(()=>{});await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(dir+'/playtest.json',JSON.stringify({passed:true,cases:results.length,results,errors},null,2));console.log({passed:true,cases:results.length});
}catch(error){await fs.writeFile(dir+'/playtest-attempt.json',JSON.stringify({passed:false,error:String(error),results,errors},null,2));throw error;}
finally{clearTimeout(timer);await owned.close();}
