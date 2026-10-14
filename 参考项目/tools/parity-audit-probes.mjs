import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createNewCharacter} from '../src/character.js';
import {Combat} from '../src/combat.js';
import {LPApp} from '../src/game.js';
import {restoreGroundItems} from '../src/loot.js';
import {applySpecialConsumable} from '../src/special-consumables.js';
import {instanceItem} from '../src/native-stats.js';
import {SaveRoster} from '../src/save-roster.js';
import {availableCharacterModes} from '../src/difficulty.js';
import {prepareQuestJournal} from '../src/quest-journal.js';
import {readNpcDialogue} from '../src/npc-dialogue.js';
import {spawnUnit} from '../src/monster-spawning.js';
import {tryMonsterRebirth,resetMonsterRebirth} from '../src/monster-rebirth.js';

const dir='reports/parity-audit-20261013';await fs.mkdir(dir,{recursive:true});
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8'));
const content={items:await read('data/items.json'),skills:await read('data/skills.json'),monsters:await read('data/monsters.json'),mapList:await read('data/maps.json'),tasks:await read('data/tasks.json'),permanent:await read('data/permanent.json'),json:read};
content.itemNames=new Map(content.items.filter(i=>i.name!=='0').map(i=>[i.name,i]));content.monsterNames=new Map(content.monsters.filter(i=>i.name!=='0').map(i=>[i.name,i]));
const result={scope:'Isolated production-function probes. Findings reproduced, not a pass claim for native parity; no user saves changed.',findings:[]};
const add=(id,data)=>result.findings.push({id,...data});

// An actual original #UpWeapon recipe can rename/re-icon 扎克.
const weapon=content.itemNames.get('扎克'),changed={id:'A00:loot:1',kind:'item',itemId:weapon.id,quantity:1,x:138,y:13,name:'扎克(注灵)',fieldOverrides:{1:960,2:82},waterUses:3,discarded:true};
const calls=[],pack=await read('sprites/Item1/index.json');
LPApp.prototype.drawGroundItem.call({packs:new Map([['Item1',pack]]),content,worldScale:1.6,mapPoint:()=>({x:0,y:0}),player:{},batch:{frame:(p,index)=>calls.push({icon:index}),textWidth:()=>100,quad(){},white:{}},hud:{centered:label=>calls.push({label})}},changed);
const actual=instanceItem(weapon,changed);
assert.equal(calls[0].icon,weapon.icon);assert.equal(calls[1].label,weapon.name);assert.notEqual(weapon.icon,actual.icon);
add('ground-instance-display',{expected:{icon:actual.icon,name:actual.name},actual:{icon:calls[0].icon,name:calls[1].label},originalRecipe:'G00/克钦/#UpWeapon'});

const restored=restoreGroundItems({A00:[changed]},content).A00[0];assert.equal(restored.waterUses,undefined);assert.equal(restored.name,changed.name);
const before=createNewCharacter(content),after=createNewCharacter(content);for(const [p,meta]of [[before,changed],[after,restored]]){p.equipment.weapon=weapon.id;p.equipmentMeta.weapon=structuredClone(meta);}
const refused=applySpecialConsumable(before,content,'战神水',()=>0),allowed=applySpecialConsumable(after,content,'战神水',()=>0);
assert.equal(refused.ok,false);assert.equal(allowed.ok,true);
add('ground-water-use-save',{beforeCount:3,restoredCount:restored.waterUses??null,beforeUse:refused,afterUse:allowed,trigger:'Drop previously enhanced weapon, save/reload while on ground, pick up and equip.'});

const p=createNewCharacter(content,{gameMode:1});p.modeUnlock=2;p.clearCount=1;
const roster=new SaveRoster({},content);roster.set('audit',{version:2,player:p});assert.equal(p.gameMode,1);assert.equal(roster.hellUnlocked,true);
add('hell-global-unlock',{currentMode:p.gameMode,unlockedTier:p.modeUnlock,globalHellUnlocked:roster.hellUnlocked,availableNewModes:availableCharacterModes(roster),helpRequires:'A character enters hell mode and saves before hell is exposed in new-character creation.'});

for(const [id,event,name]of [['H00',6,'村大夫'],['E00',3,'镇长'],['F01',4,'隐士']]){
 const p=createNewCharacter(content);p.unlockedMaps=['A00',id];p.events=Array(30).fill(0);p.events[0]=16;p.events[event]=event===4?0:1;
 if(event===4)p.inventory.push({itemId:content.itemNames.get('铁锤').id,quantity:1});
 const map=await read('maps/'+id+'.json'),npc=map.npcs.find(n=>n.name===name),view=readNpcDialogue(npc.script,p,content,'Start',{map});
 const app={player:p,content,mapId:id,map};await prepareQuestJournal(app);assert.ok(!app.questJournal.some(row=>row.event===event));assert.equal(view.unsupported.length,0);
 add('unlisted-side-quest-'+event,{map:id,npc:name,eventValue:p.events[event],journal:app.questJournal.map(r=>({title:r.title,event:r.event})),dialogue:view.text,effects:view.effects,choices:view.choices});
}

const map={id:'A00',width:12,height:12,npcs:[],spawns:[],cells:Array.from({length:144},()=>[1,0,0,0])},hero=createNewCharacter(content),combat=new Combat(hero,content,()=>.5,{},()=>.5,()=>.5);combat.enter(map,{x:5,y:5});
const guard=spawnUnit(combat,content.monsterNames.get('明阳守卫'),{x:7,y:5});guard.hp=0;assert.ok(tryMonsterRebirth(combat,guard));
hero.modeUnlock=1;const beforeGuard={attackKind:guard.definition.attackKind,attack:guard.definition.attack,reborn:guard.reborn};
LPApp.prototype.setDifficulty.call({player:hero,units:combat.units,content,save(){},notify(){throw Error('Unexpected refusal');}},1);
const switched={attackKind:guard.definition.attackKind,attack:guard.definition.attack,reborn:guard.reborn,hpMax:guard.definition.hp};
resetMonsterRebirth(guard);const respawn={hpMax:guard.definition.hp,mode:hero.gameMode};
assert.equal(beforeGuard.attackKind,22);assert.notEqual(switched.attackKind,22);assert.equal(switched.reborn,true);assert.notEqual(respawn.hpMax,switched.hpMax);
add('difficulty-rebirth-reset',{before:beforeGuard,afterDifficultySwitch:switched,afterRespawnReset:respawn});

const chicken=spawnUnit(combat,content.monsterNames.get('鸡'),{x:6,y:6});hero.bossTimers=Array(30).fill(-1);hero.bossTimers[5]=100;const timer=hero.bossTimers[5];combat.kill(chicken);
assert.equal(hero.bossTimers[5],100);add('kill-boss-timer',{before:timer,after:hero.bossTimers[5],note:'Current kill only applies the victim script; native 5c968b..5c9847 has an additional eligible-kill decrement branch.'});

await fs.writeFile(dir+'/probes.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
