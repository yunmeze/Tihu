import {followingPet,friendlyCount} from './allies.js';
import {startDefense,upgradeDefense} from './defense.js';
import {planChallenge,queueChallenge} from './challenges.js';
import {planEnding,beginEnding} from './ending.js';
import {attributes} from './character.js';
import {nativeRound,monsterWalkable} from './monster-motion.js';
import {spawnUnit} from './monster-spawning.js';

export const SCRIPT_PET_SKILL='江湖召唤';
export const companionLimit=player=>player.class==='道士'?3:1;
export const companions=combat=>[...(combat.units||[]),...(combat.waitingPets||[])].filter(u=>u.alive&&followingPet(u));
export function scriptPetDefinition(base,level,player){
 const d={...base},skill=player.skills.find(s=>s.name==='诱惑之光')?.level||0;
 // Native 6052d4 copies the whole monster template; purchased pets are not
 // halved like the separate temptation spell. 605605 handles higher ranks.
 for(let i=2;i<=level;i++){d.hp=nativeRound(d.hp*1.1)+10*skill;d.attack+=1+(i<=5?2:i<=8?3:4);d.defense+=i<=5?2:i<=8?4:5;d.magicDefense+=i<=5?2:i<=8?3:4;d.regenFrames=i<=5?100:i<=8?70:50;}
 return d;
}
export function planScriptServices(combat,effects){
 const planned=[],occupied=new Set([combat.position,...combat.units.filter(u=>u.alive),...(combat.map.npcs||[]).filter(n=>!n.removed)].map(p=>Math.round(p.x)+','+Math.round(p.y)));
 const origin={x:Math.round(combat.position.x),y:Math.round(combat.position.y)},queue=[origin],seen=new Set([origin.x+','+origin.y]);
 let friendly=friendlyCount(combat),count=companions(combat).length,pool=combat.units.filter(u=>u.alive||!u.temporary).length;
 const defenseCounters=combat.defense?{hpUp:combat.defense.hpUp,dfUp:combat.defense.dfUp,dmUp:combat.defense.dmUp}:null;let challengePlanned=false,endingPlanned=false;
 for(const e of effects){
  if(e.kind==='gameover'){const entry=planEnding(combat,e);if(!entry||endingPlanned)return null;endingPlanned=true;planned.push(entry);continue;}
  if(e.kind==='challenge'){const entry=planChallenge(combat,e);if(!entry||challengePlanned)return null;challengePlanned=true;planned.push(entry);continue;}
  if(['reme','repet'].includes(e.kind)){if(combat.player.hp<=0)return null;planned.push(e);continue;}
  if(['stop','unstop'].includes(e.kind)){planned.push(e);continue;}
  if(e.kind==='defstart'){if(combat.defense||combat.map.id!==combat.content.defense?.map)return null;planned.push(e);continue;}
  if(['defhpup','defdfup','defdmup','defhpadd'].includes(e.kind)){const d=combat.defense,key={defhpup:'hpUp',defdfup:'dfUp',defdmup:'dmUp'}[e.kind];if(!d||d.status!=='active'||combat.player.hp<=0||key&&++defenseCounters[key]>(key==='hpUp'?5:6)||e.kind==='defhpadd'&&![.1,.2].includes(e.fraction))return null;planned.push(e);continue;}
  if(!['addfriendhero','addfriendheron','addmonhero'].includes(e.kind))continue;
  const base=combat.monsterNames.get(e.name);if(!base||++pool>600||combat.player.hp<=0)return null;
  if(e.kind==='addfriendhero'){if(++count>companionLimit(combat.player))return null;friendly++;}
  if(e.kind==='addfriendheron'&&(!combat.defense||combat.defense.status!=='active'||++friendly>13))return null;
  let point;
  for(let i=0;i<queue.length&&i<120;i++){
   const p=queue[i],key=p.x+','+p.y;
   if(i&&!occupied.has(key)){point=p;break;}
   for(const [dx,dy]of [[-1,0],[1,0],[0,-1],[0,1]]){const n={x:p.x+dx,y:p.y+dy},k=n.x+','+n.y;if(!seen.has(k)&&combat.walkable(n.x,n.y)&&monsterWalkable(combat.map,n.x,n.y)){seen.add(k);queue.push(n);}}
  }
  if(!point)return null;occupied.add(point.x+','+point.y);planned.push({...e,point,definition:e.kind!=='addmonhero'?scriptPetDefinition(base,e.level,combat.player):base});
 }
 return planned;
}
export function applyScriptServices(combat,planned){
 for(const e of planned){
  if(e.kind==='reme'){const p=combat.player,s=attributes(p,combat.content);p.hp=s.hp;p.mp=s.mp;p.healingPool=0;p.mpRecoveryPool=0;combat.recovery=[];}
  else if(e.kind==='repet')for(const u of companions(combat)){u.hp=u.definition.hp;u.healingPool=0;}
  else if(e.kind==='stop'){combat.scriptLocked=true;combat.stopFarming();}
  else if(e.kind==='unstop')combat.scriptLocked=false;
  else if(e.kind==='defstart')startDefense(combat);
  else if(e.kind==='challenge')queueChallenge(combat,e);
  else if(e.kind==='gameover')beginEnding(combat);
  else if(e.kind.startsWith('def'))upgradeDefense(combat,e);
  else spawnUnit(combat,e.definition,e.point,e.kind!=='addmonhero'?{summoned:true,mercenary:e.kind==='addfriendheron',summonSkill:SCRIPT_PET_SKILL,petLevel:e.level,petKills:0,scripted:true}:{scripted:true,trainingDummy:/木桩/.test(e.name)});
 }
}
