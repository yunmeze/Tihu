import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createNewCharacter,createCharacter,equip,unequip} from '../src/character.js';
import {Combat} from '../src/combat.js';
import {LPApp} from '../src/game.js';
import {ITEM_INSTANCE_FIELDS,inventoryKey,sameItemStack} from '../src/inventory.js';
import {instanceItem} from '../src/native-stats.js';
import {restoreGroundItems} from '../src/loot.js';
import {applySpecialConsumable} from '../src/special-consumables.js';
import {SaveRoster} from '../src/save-roster.js';
import {availableCharacterModes,difficultyMonster} from '../src/difficulty.js';
import {prepareQuestJournal,drawQuestJournal} from '../src/quest-journal.js';
import {spawnUnit} from '../src/monster-spawning.js';
import {tryMonsterRebirth} from '../src/monster-rebirth.js';
import {bossTimerNames,reduceBossTimerOnDeath} from '../src/boss-timers.js';
import {startMagicShield,hitMagicShield,advanceMagicShield,magicShieldVisible} from '../src/magic-shield.js';
import {releaseHeroSkill} from '../src/combat-skills.js';
import {effectFrame} from '../src/effect-animation.js';
import {updateCombatEffects} from '../src/combat-effects.js';
import {updateProjectiles} from '../src/projectiles.js';
import {drawWorldText} from '../src/world-text-renderer.js';

const dir='reports/restoration-parity-20261013',read=async f=>JSON.parse(await fs.readFile('public/assets/'+f,'utf8'));
const content={items:await read('data/items.json'),skills:await read('data/skills.json'),monsters:await read('data/monsters.json'),mapList:await read('data/maps.json'),tasks:await read('data/tasks.json'),permanent:await read('data/permanent.json'),json:read};
content.itemNames=new Map(content.items.filter(i=>i.name!=='0').map(i=>[i.name,i]));content.monsterNames=new Map(content.monsters.filter(i=>i.name!=='0').map(i=>[i.name,i]));
const flat={id:'A00',width:16,height:16,npcs:[],spawns:[],cells:Array.from({length:256},()=>[1,0,0,0])},checks=[];
const fresh=()=>createNewCharacter(content),make=(p=fresh(),ground={})=>{p.base.hp=p.hp=10000;const c=new Combat(p,content,()=>.99,ground,()=>.99,()=>.5);c.enter(structuredClone(flat),{x:5,y:5});return c;};
const check=async(name,run)=>{await run();checks.push(name);};
const weapon=content.itemNames.get('扎克'),gear={id:'A00:loot:test',kind:'item',itemId:weapon.id,quantity:1,x:5,y:5,instanceId:'native:enchanted',name:'扎克(注灵)',fieldOverrides:{1:960,2:82,7:7},waterUses:3,forgeLevel:2,fused:true,mergeLevel:1,priceBonus:9,tint:[200,100,50],affixModel:'native-random-v1',discarded:true,dropSources:[{mode:1,quantity:1}]};
await check('Drop/save/reload/pickup/equip retains all instance fields and the three-water cap',()=>{
 const p=fresh();p.level=130;p.base.attack=p.base.tao=p.base.magic=[1000,1000];const saved=JSON.parse(JSON.stringify({A00:[gear]})),c=make(p,saved);c.pickupAtFeet();assert.equal(c.groundItems.length,0);
 const entry=p.inventory.find(e=>e.itemId===weapon.id);assert.ok(entry);for(const field of ITEM_INSTANCE_FIELDS)assert.deepEqual(entry[field],gear[field],field);
 assert.ok(equip(p,content,inventoryKey(entry)));assert.equal(p.equipmentMeta.weapon.waterUses,3);assert.equal(applySpecialConsumable(p,content,'战神水',()=>0).ok,false);
 assert.ok(unequip(p,'weapon'));const restored=createCharacter(content,JSON.parse(JSON.stringify({version:2,player:p})));assert.equal(restored.inventory.find(e=>e.itemId===weapon.id).waterUses,3);
 assert.equal(sameItemStack(gear,{...gear,waterUses:0}),false);
});
await check('Ground restoration remains compatible with old plain drops/gold and rejects duplicates',()=>{
 const gold={id:'gold',kind:'gold',x:5,y:5,quantity:100},plain={...gear,id:'plain',waterUses:undefined,instanceId:undefined};const r=restoreGroundItems({A00:[plain,gold,gold,{...plain,id:'bad',quantity:0}],BAD:[gear]},content);
 assert.equal(r.A00.length,2);assert.equal(r.A00[0].waterUses,undefined);assert.equal(r.BAD,undefined);assert.deepEqual(r.A00[1],gold);
});
await check('Original UpWeapon renamed/re-iconed drop uses instance icon and name both on ground and pickup',async()=>{
 const g={...gear,forgeLevel:0,mergeLevel:0},pack=await read('sprites/Item1/index.json'),calls=[];
 LPApp.prototype.drawGroundItem.call({packs:new Map([['Item1',pack]]),content,worldScale:1.6,mapPoint:()=>({x:0,y:0}),player:{},batch:{frame:(p,index)=>calls.push({icon:index}),textWidth:()=>100,quad(){},white:{}},hud:{centered:label=>calls.push({label})}},g);
 assert.equal(calls[0].icon,960);const c=make(fresh(),{A00:[g]});c.player.insights=Array(13).fill(0);
 const app={map:c.map,player:c.player,hero:c.position,combat:c,content,packs:new Map([['Item1',pack]]),units:[],worldScale:1.6,appearance:{body:0,head:0},tab:'战斗',nearbyEntries:()=>[],screenPoint:(x,y)=>({x:375+(x-5)*76.8,y:555+(y-5)*51.2}),batch:{textWidth:text=>String(text).length*24,quad(){},outlinedText:label=>calls.push({label}),white:{}}};
 drawWorldText(app);assert.equal(calls[1].label,'扎克(注灵)');assert.equal(app.worldText.groundHits[0].dropId,g.id);c.pickupAtFeet();assert.ok(c.events.some(e=>e.kind==='loot'&&e.text==='扎克(注灵) +1'));
});
await check('Every difficulty transition retains the guard phase, HP ratio, recovery pool and attack clock',()=>{
 for(const from of [0,1,2])for(const to of [0,1,2])if(from!==to){const p=fresh();p.gameMode=from;p.modeUnlock=2;const c=make(p),u=spawnUnit(c,content.monsterNames.get('明阳守卫'),{x:8,y:5});u.hp=0;assert.ok(tryMonsterRebirth(c,u));u.hp=u.definition.hp*.2;u.rebirthRecovery=u.definition.hp*.4;u.attackCooldown=.7;u.animationElapsed=.3;
  const app={player:p,units:c.units,content,save(){},notify(){throw Error('Refused valid mode');}};assert.ok(LPApp.prototype.setDifficulty.call(app,to));const d=difficultyMonster(content.monsters[u.monsterId],p);
  assert.equal(u.reborn,true);assert.equal(u.definition.attackKind,22);assert.equal(u.definition.attack,d.attack-15);assert.equal(u.definition.defense,d.defense+10);assert.equal(u.hp,Math.round(d.hp*.2));assert.equal(u.rebirthRecovery,Math.round(d.hp*.4));assert.equal(u.birthDefinition.hp,d.hp);assert.equal(u.attackCooldown,.7);assert.equal(u.animationElapsed,.3);
 }
});
await check('Guard final death and natural respawn use the newly selected difficulty',()=>{
 const p=fresh();p.modeUnlock=2;const c=make(p),u=spawnUnit(c,content.monsterNames.get('明阳守卫'),{x:8,y:5});u.hp=0;tryMonsterRebirth(c,u);LPApp.prototype.setDifficulty.call({player:p,units:c.units,content,save(){}},1);u.temporary=false;
 c.kill(u,{reward:false});assert.equal(u.alive,false);p.bossTimers[20]=0;u.respawnAt=c.elapsed;c.update(.02);assert.equal(u.alive,true);assert.equal(u.reborn,false);assert.equal(u.definition.attackKind,0);assert.equal(u.definition.hp,5200);assert.equal(u.hp,5200);
});
await check('Mode changes leave pets, mercenaries, defense flags and dead-unit HP intact',()=>{
 const p=fresh();p.modeUnlock=2;const c=make(p);for(const extra of [{summoned:true},{mercenary:true},{defenseFlag:true}]){const u=spawnUnit(c,content.monsterNames.get('召唤骷髅'),{x:8,y:5},extra);u.hp=2;u.expected={definition:u.definition,hp:u.hp};}
 const dead=spawnUnit(c,content.monsterNames.get('鸡'),{x:9,y:5});dead.alive=false;dead.hp=0;LPApp.prototype.setDifficulty.call({player:p,units:c.units,content,save(){}},2);for(const u of c.units.filter(u=>u.expected)){assert.equal(u.definition,u.expected.definition);assert.equal(u.hp,u.expected.hp);}assert.equal(dead.hp,0);
});
await check('Hell creation requires a saved hell character, survives deletion, and retains old explicit unlocks',()=>{
 const p=fresh();p.gameMode=1;p.modeUnlock=2;const s={version:2,player:p},r=new SaveRoster({},content);r.set('expert',s);assert.deepEqual(availableCharacterModes(r),[0,1]);const loaded=new SaveRoster(r.serialize(),content);assert.equal(loaded.hellUnlocked,false);
 p.gameMode=2;loaded.set('expert',{version:2,player:p});assert.deepEqual(availableCharacterModes(loaded),[0,1,2]);loaded.remove('expert');assert.equal(new SaveRoster(loaded.serialize(),content).hellUnlocked,true);assert.equal(new SaveRoster({hellUnlocked:true},content).hellUnlocked,true);
 const legacy=new SaveRoster({version:2,player:p},content);assert.equal(legacy.hellUnlocked,true);
});
for(const [event,mapId,values] of [[3,'E00',[0,1,2]],[4,'F01',[0,1]],[6,'H00',[0,1,2]]])await check('Quest '+event+' tracks active/turn-in/completed stages without granting preview rewards',async()=>{
 const p=fresh();p.events=Array(30).fill(0);p.events[0]=16;p.unlockedMaps=['A00',mapId];const map=await read('maps/'+mapId+'.json');
 for(const value of values){p.events[event]=value;const before=JSON.stringify(p),a={player:p,content,mapId,map};await prepareQuestJournal(a);assert.equal(JSON.stringify(p),before);const row=a.questJournal.find(r=>r.event===event);assert.ok(row);assert.ok(row.description);assert.equal(row.status,value===0?'进行中':event===4||value===2?'已完成':'可交付');}
 if(event===4){p.events[4]=0;p.inventory=[{itemId:content.itemNames.get('铁锤').id,quantity:1}];const a={player:p,content,mapId,map};await prepareQuestJournal(a);assert.equal(a.questJournal.find(r=>r.event===4).status,'可交付');}
});
await check('Herbalist objective switches from rescue NPC to village doctor and completed journal has no turn-in button',async()=>{
 const p=fresh();p.events=Array(30).fill(0);p.unlockedMaps=['A00','H00','H40'];const map=await read('maps/H40.json'),a={player:p,content,mapId:'H40',map};await prepareQuestJournal(a);let r=a.questJournal.find(r=>r.event===6);assert.equal(r.mapId,'H40');assert.equal(r.name,'采药人');p.events[6]=1;await prepareQuestJournal(a);r=a.questJournal.find(r=>r.event===6);assert.equal(r.mapId,'H00');assert.equal(r.name,'村大夫');p.events[6]=2;await prepareQuestJournal(a);
 a.questPage=a.questJournal.findIndex(r=>r.event===6);a.questTextPage=9;a.content.font={glyphs:{}};const labels=[];a.batch={text(){}};a.hud={image(){},centered(){}};a.button=label=>labels.push(label);drawQuestJournal(a);assert.ok(!labels.some(l=>l.includes('对话')));
});
await check('Original herbalist rescue/removal, return reward and repeated doctor dialogue settle exactly once',async()=>{
 const p=fresh(),c=make(p),map=await read('maps/H40.json');c.enter(map,{x:map.home[0],y:map.home[1]});const n=map.npcs.find(n=>n.name==='采药人');assert.ok(c.runScript(n.script,'A2').applied);assert.equal(p.events[6],1);assert.equal(n.removed,true);
 const village=await read('maps/H00.json');c.enter(village,{x:village.home[0],y:village.home[1]});const doctor=village.npcs.find(n=>n.name==='村大夫'),gold=p.gold;assert.ok(c.runScript(doctor.script).applied);assert.equal(p.events[6],2);assert.equal(p.gold-gold,1000);assert.equal(p.inventory.find(e=>e.itemId===content.itemNames.get('太阳水(小)').id).quantity,3);const saved=JSON.stringify(p);assert.ok(c.runScript(doctor.script).applied);assert.equal(JSON.stringify(p),saved);
});
await check('Original spider death flag/timer and town reward settle once without journal preview side effects',async()=>{
 const p=fresh();p.events=Array(30).fill(0);p.events[0]=16;const c=make(p),map=await read('maps/E12.json');c.enter(map,{x:map.home[0],y:map.home[1]});const u=c.units.find(u=>u.definition.name==='魔灵蜘蛛');assert.ok(u);c.kill(u,{reward:false});assert.equal(p.events[3],1);assert.equal(p.bossTimers[6],1200);
 const town=await read('maps/E00.json');c.enter(town,{x:town.home[0],y:town.home[1]});const npc=town.npcs.find(n=>n.name==='镇长'),gold=p.gold;assert.ok(c.runScript(npc.script).applied);assert.equal(p.events[3],2);assert.equal(p.gold-gold,1000);const saved=JSON.stringify(p);assert.ok(c.runScript(npc.script).applied);assert.equal(JSON.stringify(p),saved);
});
await check('Original iron-hammer return consumes one hammer and awards silver ore/gold exactly once',async()=>{
 const p=fresh(),c=make(p),map=await read('maps/F01.json');c.enter(map,{x:map.home[0],y:map.home[1]});const id=content.itemNames.get('铁锤').id;p.inventory.push({itemId:id,quantity:1});const n=map.npcs.find(n=>n.name==='隐士'),gold=p.gold;assert.ok(c.runScript(n.script,'A1').applied);assert.equal(p.events[4],1);assert.equal(p.gold-gold,1000);assert.ok(!p.inventory.some(e=>e.itemId===id));assert.equal(p.inventory.find(e=>e.itemId===content.itemNames.get('银矿石').id).quantity,1);const saved=JSON.stringify(p);assert.ok(c.runScript(n.script,'A1').applied);assert.equal(JSON.stringify(p),saved);
});
await check('Rescued herbalist stays tracked before discovering the doctor town; spider turn-in respects the native main-quest gate',async()=>{
 const p=fresh();p.events=Array(30).fill(0);p.events[6]=1;p.unlockedMaps=['A00','H40'];const a={player:p,content,mapId:'H40',map:await read('maps/H40.json')};await prepareQuestJournal(a);assert.equal(a.questJournal.find(r=>r.event===6).mapId,'H00');
 p.events[3]=1;p.events[0]=15;await prepareQuestJournal(a);assert.equal(a.questJournal.find(r=>r.event===3).status,'进行中');p.events[0]=16;await prepareQuestJournal(a);assert.equal(a.questJournal.find(r=>r.event===3).status,'可交付');
});
await check('Native boss names/order, highest eligible timer and banker rounding are used',()=>{
 const c=make(),u=spawnUnit(c,content.monsterNames.get('鸡'),{x:8,y:5});assert.equal(bossTimerNames(content).length,30);assert.equal(bossTimerNames(content)[20],'明阳守卫');c.player.bossTimers=Array(30).fill(-1);c.player.bossTimers[4]=200;c.player.bossTimers[20]=100;c.battleRandom=()=>.25;
 const r=reduceBossTimerOnDeath(c,u);assert.equal(r.index,20);assert.equal(r.seconds,7);assert.equal(c.player.bossTimers[20],93);assert.equal(c.player.bossTimers[4],200);assert.equal(c.player.bossCycles[20],8);
});
await check('Boss deaths/challenges/settings/non-positive slots do not receive refresh acceleration',()=>{
 const c=make(),u=spawnUnit(c,content.monsterNames.get('甲虫王'),{x:8,y:5});c.player.bossTimers=Array(30).fill(100);assert.equal(reduceBossTimerOnDeath(c,u),null);u.definition=content.monsterNames.get('鸡');c.challenge={status:'active'};assert.equal(reduceBossTimerOnDeath(c,u),null);c.challenge=null;
 const names=bossTimerNames(content),text=content.tasks.text.replace(/天龙\r?\n\s*$/,'设置\r\n');c.content={...content,tasks:{text}};assert.equal(bossTimerNames(c.content)[29],'设置');const r=reduceBossTimerOnDeath(c,u);assert.equal(r.index,28);assert.equal(c.player.bossTimers[29],100);c.player.bossTimers=Array(30).fill(-1);c.player.bossTimers[0]=0;assert.equal(reduceBossTimerOnDeath(c,u),null);assert.equal(names[29],'天龙');
});
await check('Native exact-zero vs overshoot accumulation and early respawn deadline differ correctly',()=>{
 for(const before of [10,9]){const c=make(),u=spawnUnit(c,content.monsterNames.get('鸡'),{x:8,y:5});c.player.bossTimers=Array(30).fill(-1);c.player.bossTimers[4]=before;c.player.bossCycles=Array(30).fill(1);c.units.push({alive:false,bossTimerIndex:4,respawnAt:100});const r=reduceBossTimerOnDeath(c,u);assert.equal(r.seconds,10);assert.equal(r.after,0);assert.equal(c.player.bossCycles[4],before===10?11:0);assert.equal(c.units.at(-1).respawnAt,0);}
});
await check('Actual enemy death gives one refresh notice and one deduction, never again for a corpse',()=>{
 const c=make(),u=spawnUnit(c,content.monsterNames.get('鸡'),{x:8,y:5});c.player.bossTimers=Array(30).fill(-1);c.player.bossTimers[4]=100;c.kill(u);assert.equal(c.player.bossTimers[4],90);assert.ok(c.events.some(e=>e.text==='狼王 刷新-10秒'));c.kill(u);assert.equal(c.player.bossTimers[4],90);
});
await check('Magic-shield formula converts native five-tick counter units into 50Hz frames',()=>{
 const p=fresh();p.skills=[{name:'魔法盾',level:2}];p.base.magic=[20,20];const c=make(p);releaseHeroSkill(c,{name:'魔法盾'},null);assert.equal(p.magicShieldFrames,4500);assert.deepEqual(c.magicShieldState,{phase:1,frame:1});
});
await check('Shield unfold/hold/hit stages use the original frame map and pause lifetime outside holding',()=>{
 const c=make();startMagicShield(c,100);for(let i=1;i<=45;i++){c.ruleFrame=i;advanceMagicShield(c);}assert.deepEqual(c.magicShieldState,{phase:2,frame:10});assert.equal(c.player.magicShieldFrames,500);
 for(let i=46;i<=50;i++){c.ruleFrame=i;advanceMagicShield(c);}assert.equal(c.player.magicShieldFrames,495);assert.equal(c.magicShieldState.frame,11);hitMagicShield(c);for(let i=51;i<=70;i++){c.ruleFrame=i;advanceMagicShield(c);}assert.deepEqual(c.magicShieldState,{phase:2,frame:11});assert.equal(c.player.magicShieldFrames,495);for(let i=71;i<=75;i++){c.ruleFrame=i;advanceMagicShield(c);}assert.equal(c.player.magicShieldFrames,490);
});
await check('Shield warning flashes on exactly native phases 1..7 of twelve without removing defense',async()=>{
 const c=make();c.player.magicShieldFrames=245;const visible=[];for(let i=0;i<12;i++){c.ruleFrame=i;if(magicShieldVisible(c))visible.push(i);}assert.deepEqual(visible,[1,2,3,4,5,6,7]);c.player.magicShieldFrames=250;c.ruleFrame=0;assert.equal(magicShieldVisible(c),true);
 const pack=await read('sprites/Mgc/17/index.json');assert.equal(effectFrame({shield:true,shieldFrame:16},pack),16);c.player.hp=0;assert.equal(magicShieldVisible(c),false);
});
await check('Shield timing is independent of browser frequency and expires after unfolding plus native lifetime',()=>{
 const outcomes=[];for(const hz of [30,50,60,120]){const c=make();startMagicShield(c,20);for(let i=0;i<hz;i++){updateCombatEffects(c,1/hz);updateProjectiles(c,1/hz);}outcomes.push([c.ruleFrame,c.player.magicShieldFrames,c.magicShieldState.frame]);assert.ok(c.effects.some(e=>e.shield&&e.shieldFrame===11));}
 for(const outcome of outcomes)assert.deepEqual(outcome,outcomes[0]);assert.deepEqual(outcomes[0],[50,95,11]);const c=make();startMagicShield(c,20);for(let i=0;i<145;i++){updateCombatEffects(c,.02);updateProjectiles(c,.02);}assert.equal(c.player.magicShieldFrames,0);assert.equal(magicShieldVisible(c),false);assert.ok(c.effects.every(e=>!e.shield));
});
await fs.mkdir(dir,{recursive:true});const report={passed:true,checks,fullOriginalEquivalent:false,scope:'Production-function save/drop/pickup/equip, phase/respawn, journal, boss timer, and original shield state/clock regressions. Test characters only.',pid:process.pid};await fs.writeFile(dir+'/targeted-tests.json',JSON.stringify(report,null,2));console.log({passed:true,checks:checks.length,pid:process.pid});
