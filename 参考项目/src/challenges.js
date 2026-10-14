import {ANIMATIONS,setAction} from './animation.js';
import {monsterWalkable} from './monster-motion.js';
import {clearMonsterAggro} from './monster-ai.js';
import {validStatuses} from './pet-state.js';
import {followingPet} from './allies.js';
import {difficultyMonster} from './difficulty.js';

// Native command dispatcher6177a6/617889, result5d99d0, formatter5da230.
export const CHALLENGE_RULES={fps:50,time:{map:'E30',entry:[15,25],enemies:57,name:'时间挑战'},survival:{map:'C30',entry:[49,53],enemies:0,name:'生存挑战',entryExposed:false}};
export const isChallengeMap=id=>['E30','C30'].includes(id);
export function challengeDestinationAllowed(c,id){if(!isChallengeMap(id))return true;return [c.pendingChallenge?.kind,c.restoredChallenge?.kind].some(kind=>CHALLENGE_RULES[kind]?.map===id);}
const MAX_FRAMES=2147483647;
const validFrames=n=>Number.isSafeInteger(n)&&n>=0&&n<=MAX_FRAMES;
export function normalizeChallengeRecords(p){const old=p.challengeRecords;p.challengeRecords={timeFrames:validFrames(old?.timeFrames)?old.timeFrames:0,survivalFrames:validFrames(old?.survivalFrames)?old.survivalFrames:0};return p;}
export function challengeTime(frames){const seconds=Math.floor(Math.max(0,frames)/50);return (seconds>=60?Math.floor(seconds/60)+'分':'')+seconds%60+'秒';}
export function challengeRemaining(c){return c.units.filter(u=>!u.summoned&&!u.removed&&(u.alive||!u.refined&&c.elapsed-u.diedAt<ANIMATIONS.monster.death.seconds-1e-8)).length;}
export function planChallenge(c,e){
 const r=CHALLENGE_RULES[e.mode];if(!r||c.player.hp<=0||c.pendingChallenge||c.challenge?.status==='active'||c.defense?.status==='active')return null;
 return {...e,origin:{map:c.map.id,x:c.position.x,y:c.position.y}};
}
export function queueChallenge(c,e){c.pendingChallenge={kind:e.mode,origin:{...e.origin}};}
export function enterChallenge(c){
 c.challenge=null;c.challengeNotice=false;
 const pending=c.pendingChallenge,saved=c.restoredChallenge;c.pendingChallenge=null;c.restoredChallenge=null;
 const kind=pending?.kind||saved?.kind,r=CHALLENGE_RULES[kind];if(!r||c.map.id!==r.map)return;
 c.challenge={version:1,kind,map:r.map,status:'active',frames:0,remainder:0,origin:pending?.origin||{map:'J00',x:109,y:16}};
 for(const u of c.units)if(!u.summoned)u.temporary=true;
 if(!pending&&saved&&!restoreChallenge(c,saved)){
  // The arena is recreated from immutable source data if the checkpoint is
  // malformed. No completion or record is granted from unvalidated input.
  c.challengeNotice=true;
 }
}
export function endChallenge(c,status){
 const s=c.challenge;if(!s||s.status!=='active')return false;
 if(status==='complete'&&(s.kind!=='time'||c.player.hp<=0||challengeRemaining(c)>0))return false;
 if(!['complete','failed','abandoned'].includes(status))return false;
 s.status=status;c.stopFarming();for(const u of c.units)clearMonsterAggro(u);
 if(status==='complete'){c.autoLoot=c.groundItems.length>0;c.lootAfter=c.elapsed;}
 const records=c.player.challengeRecords;
 if(s.kind==='time'&&status==='complete'&&s.frames>0&&(!records.timeFrames||s.frames<records.timeFrames))records.timeFrames=s.frames;
 if(s.kind==='survival'&&status==='failed'&&c.player.hp<=0)records.survivalFrames=Math.max(records.survivalFrames,s.frames);
 c.challengeNotice=true;return true;
}
export function updateChallenge(c,dt){
 const s=c.challenge;if(!s||s.status!=='active')return;
 s.remainder+=dt*50;const ticks=Math.floor(s.remainder+1e-8);s.remainder=Math.max(0,s.remainder-ticks);s.frames=Math.min(MAX_FRAMES,s.frames+ticks);
 // Pool release and hero death result are reached after their original strips.
 if(c.player.hp<=0){if(c.position.animationElapsed>=ANIMATIONS.hero.death.seconds-1e-8)endChallenge(c,'failed');}
 else if(s.kind==='time'&&challengeRemaining(c)===0)endChallenge(c,'complete');
}
export function saveChallenge(c){
 const s=c.challenge;if(!s)return null;
 const actors=[...c.units,...c.waitingPets];
 const originals=c.map.spawns.map((_,i)=>{const id=c.map.id+':'+i,u=actors.find(u=>u.id===id||u.originId===id);if(!u||u.summoned)return {id,gone:true};return {id,gone:!u.alive,hp:u.alive?u.hp:0,x:u.x,y:u.y,deadFor:u.alive?0:Math.min(ANIMATIONS.monster.death.seconds,Math.max(0,c.elapsed-u.diedAt)),refined:!!u.refined,statuses:validStatuses(u.statuses),regenClock:u.regenClock||0,speedBoosted:!!u.speedBoosted,attackSpeedBoosted:!!u.attackSpeedBoosted};});
 const friends=actors.filter(u=>u.alive&&followingPet(u)).slice(0,3).map((u,slot)=>({id:u.id,slot,monsterId:u.monsterId,summonSkill:u.summonSkill,originId:u.originId}));
 return {...s,originals,friends};
}
function restoreChallenge(c,s){
 if(s?.version!==1||s.map!==c.map.id||!['active','complete','failed','abandoned'].includes(s.status)||!validFrames(s.frames)||!Number.isFinite(s.remainder)||s.remainder<0||s.remainder>=1||!Array.isArray(s.originals)||s.originals.length!==c.map.spawns.length)return false;
 if(!s.origin||!c.content.mapList.some(m=>m.id===s.origin.map&&Number.isFinite(s.origin.x)&&Number.isFinite(s.origin.y)&&s.origin.x>=0&&s.origin.y>=0&&s.origin.x<m.width&&s.origin.y<m.height))return false;
 const ids=new Set();
 for(const row of s.originals){
  if(!row||typeof row.id!=='string'||ids.has(row.id))return false;ids.add(row.id);
  const index=Number(row.id.split(':').at(-1)),spec=c.map.spawns[index];if(!Number.isInteger(index)||!spec||row.id!==c.map.id+':'+index||typeof row.gone!=='boolean')return false;
  if(row.gone&&row.hp===undefined)continue;
  const base=c.monsterNames.get(spec.name)||c.content.monsters[spec.monsterId],d=difficultyMonster(base,c.player);
  if(!d)return false;
  if(!Number.isSafeInteger(row.hp)||row.hp<0||row.hp>d.hp||row.gone!==(row.hp===0)||!Number.isFinite(row.x)||!Number.isFinite(row.y)||!monsterWalkable(c.map,Math.round(row.x),Math.round(row.y))||!Number.isFinite(row.deadFor)||row.deadFor<0||row.deadFor>1.2)return false;
 }
 if(s.status==='complete'&&(s.kind!=='time'||s.originals.some(r=>!r.gone||r.hp!==undefined&&!r.refined&&r.deadFor<1.2)))return false;
 if(s.status==='failed'&&c.player.hp>0)return false;
 Object.assign(c.challenge,{status:s.status,frames:s.frames,remainder:s.remainder,origin:{...s.origin}});
 for(const row of s.originals){const u=c.units.find(u=>u.id===row.id&&!u.summoned);if(!u)continue;
  if(row.gone&&row.hp===undefined){Object.assign(u,{hp:0,alive:false,removed:true,refined:true,diedAt:c.elapsed-2,respawnAt:Infinity});continue;}
  Object.assign(u,{x:row.x,y:row.y,roamHome:{x:row.x,y:row.y},hp:row.hp,alive:!row.gone,refined:row.refined,statuses:validStatuses(row.statuses),regenClock:Number.isFinite(row.regenClock)&&row.regenClock>=0&&row.regenClock<1000?row.regenClock:0,speedBoosted:row.speedBoosted,attackSpeedBoosted:row.attackSpeedBoosted});
  if(row.gone){u.diedAt=c.elapsed-row.deadFor;u.respawnAt=Infinity;setAction(u,'death',{family:'monster'});u.animationElapsed=row.deadFor;}
 }
 const pets=[...c.units,...c.waitingPets].filter(u=>u.alive&&followingPet(u)).slice(0,3),owners=new Map();
 for(const old of Array.isArray(s.friends)?s.friends.slice(0,3):[]){const next=pets[old.slot];if(typeof old.id==='string'&&next&&next.monsterId===old.monsterId&&next.summonSkill===old.summonSkill&&next.originId===old.originId)owners.set(old.id,next.id);}
 for(const u of c.units)for(const state of Object.values(u.statuses||{}))if(owners.has(state.source))state.source=owners.get(state.source);
 if(s.status!=='active')c.challengeNotice=true;
 return true;
}
