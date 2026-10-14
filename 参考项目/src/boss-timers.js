import {monsterBehavior,nativeRound,sampleMonsterRandom} from './monster-motion.js';

const nameCache=new WeakMap();
export function bossTimerNames(content){
 const tasks=content.tasks;if(!tasks?.text)return [];
 if(!nameCache.has(tasks))nameCache.set(tasks,tasks.text.split(/\r?\n/).map(s=>s.trim()).filter(Boolean).slice(-30));
 return nameCache.get(tasks);
}
// Native 5c968b..5c9847: a non-boss death outside a timed/survival challenge
// reduces only the highest eligible BT index. +2278 accumulates the reduction;
// it resets only when the subtraction passes below zero, not on exact zero.
export function reduceBossTimerOnDeath(combat,unit){
 if(combat.challenge||monsterBehavior(unit.definition)===10)return null;
 const p=combat.player,names=bossTimerNames(combat.content);
 for(let index=Math.min(29,names.length-1);index>=0;index--){
  if(names[index]==='设置'||!(p.bossTimers?.[index]>0))continue;
  const seconds=nativeRound(sampleMonsterRandom(combat.battleRandom)*10)+5,before=p.bossTimers[index],after=Math.max(0,before-seconds);
  p.bossTimers[index]=after;p.bossCycles||=Array(30).fill(1);p.bossCycles[index]=before-seconds<0?0:(p.bossCycles[index]||0)+seconds;
  for(const u of combat.units)if(!u.alive&&!u.removed&&u.bossTimerIndex===index&&Number.isFinite(u.respawnAt))u.respawnAt=Math.min(u.respawnAt,combat.elapsed+after);
  return {index,name:names[index],seconds,before,after};
 }
 return null;
}
