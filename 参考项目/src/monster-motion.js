import {canEnterCell} from './map-flags.js';
import {setAction} from './animation.js';
import {isParalyzed,isFrozen} from './statuses.js';

// Native idle loop: four frames, twelve engine ticks per frame, then a 20%
// walking attempt and an independent 30% direction change. No spawn leash.
export const MONSTER_MOTION={sourceFps:50,tileWidth:48,tileHeight:32,idleDecisionFrames:48,moveChance:.2,turnChance:.3,nativeIdleTimingVerified:true};
const DIRECTIONS=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
const key=(x,y)=>x+','+y;
export const sampleMonsterRandom=random=>Math.max(0,Math.min(.999999999,Number(random())||0));
export function nativeRound(value){const floor=Math.floor(value),fraction=value-floor;return Math.abs(fraction-.5)<1e-10?floor+(floor%2===0?0:1):Math.round(value);}
export const monsterBehavior=definition=>definition.behavior??definition.rawExtra?.[7]??0;
export const canWander=definition=>definition.speed>0&&monsterBehavior(definition)>-2;
export function monsterSpeed(unit){if(monsterBehavior(unit.definition)===9&&unit.hp<unit.definition.hp*.2)unit.speedBoosted=true;return unit.definition.speed*(monsterBehavior(unit.definition)===9&&unit.speedBoosted?1.5:1)*(isFrozen(unit)?.5:1);}
export function monsterWalkable(map,x,y){return Number.isInteger(x)&&Number.isInteger(y)&&x>=0&&y>=0&&x<map.width&&y<map.height&&canEnterCell(map.cells[x*map.height+y][1],'monster');}
export function initializeMonsterMotion(unit){unit.roamHome={x:unit.x,y:unit.y};resetMonsterMotion(unit);}
export function resetMonsterMotion(unit){unit.roamGoal=null;unit.roamFrom=null;unit.roamProgress=0;unit.roamWait=MONSTER_MOTION.idleDecisionFrames/MONSTER_MOTION.sourceFps;if(unit.roamHome){unit.x=unit.roamHome.x;unit.y=unit.roamHome.y;}}
export function updateMonsterMotion(combat,dt){
 const {map,units,position,monsterRandom}=combat,occupied=new Set([key(Math.round(position.x),Math.round(position.y)),...(map.npcs||[]).filter(n=>!n.removed).map(n=>key(n.x,n.y))]);
 for(const unit of units)if(unit.alive){occupied.add(key(Math.round(unit.x),Math.round(unit.y)));if(unit.roamFrom)occupied.add(key(unit.roamFrom.x,unit.roamFrom.y));if(unit.roamGoal)occupied.add(key(unit.roamGoal.x,unit.roamGoal.y));}
 for(const unit of units){
  if(!unit.alive||isParalyzed(unit)||!canWander(unit.definition)||unit.actionTime>0)continue;
  if(unit.roamGoal){
   const from=unit.roamFrom,to=unit.roamGoal,dx=to.x-from.x,dy=to.y-from.y;
   if(!monsterWalkable(map,to.x,to.y)||dx&&dy&&(!monsterWalkable(map,from.x+dx,from.y)||!monsterWalkable(map,from.x,from.y+dy))){unit.x=from.x;unit.y=from.y;unit.roamGoal=null;unit.roamFrom=null;unit.aiPath=[];unit.roamWait=MONSTER_MOTION.idleDecisionFrames/MONSTER_MOTION.sourceFps;setAction(unit,'idle',{family:'monster'});continue;}
   if(Math.round(position.x)===to.x&&Math.round(position.y)===to.y){if(unit.aggro){unit.roamGoal=null;unit.roamFrom=null;unit.aiPath=[];}setAction(unit,'idle',{family:'monster'});continue;}
   // Native 5d28c0: vertical speed per tick, horizontal speed × 1.5.
   unit.roamProgress=Math.min(1,unit.roamProgress+dt*monsterSpeed(unit)*MONSTER_MOTION.sourceFps/MONSTER_MOTION.tileHeight);
   unit.x=from.x+dx*unit.roamProgress;unit.y=from.y+dy*unit.roamProgress;setAction(unit,'walk',{family:'monster'});
   if(unit.roamProgress>=1){unit.roamGoal=null;unit.roamFrom=null;unit.roamWait=MONSTER_MOTION.idleDecisionFrames/MONSTER_MOTION.sourceFps;setAction(unit,'idle',{family:'monster'});}
   continue;
  }
  if(unit.summoned||unit.aggro||combat.player.hp<=0)continue;
  unit.roamWait-=dt*(isFrozen(unit)?12/13:1);if(unit.roamWait>0)continue;unit.roamWait+=MONSTER_MOTION.idleDecisionFrames/MONSTER_MOTION.sourceFps;
  const walking=![13,14,15].includes(monsterBehavior(unit.definition))&&nativeRound(sampleMonsterRandom(monsterRandom)*100)<MONSTER_MOTION.moveChance*100;
  if(sampleMonsterRandom(monsterRandom)<MONSTER_MOTION.turnChance)unit.direction=nativeRound(sampleMonsterRandom(monsterRandom)*7);
  if(!walking)continue;
  const from={x:Math.round(unit.x),y:Math.round(unit.y)};if(!monsterWalkable(map,from.x,from.y))continue;
  const priorities=[unit.direction];for(let turn=1;turn<=3;turn++){const sign=sampleMonsterRandom(monsterRandom)<.5?-1:1;priorities.push((unit.direction+turn*sign+8)%8,(unit.direction-turn*sign+8)%8);}
  const to=priorities.map(direction=>{const [dx,dy]=DIRECTIONS[direction];return {x:from.x+dx,y:from.y+dy,dx,dy,direction};}).find(to=>monsterWalkable(map,to.x,to.y)&&!occupied.has(key(to.x,to.y))&&(!to.dx||!to.dy||monsterWalkable(map,from.x+to.dx,from.y)&&monsterWalkable(map,from.x,from.y+to.dy)&&!occupied.has(key(from.x+to.dx,from.y))&&!occupied.has(key(from.x,from.y+to.dy))));
  if(!to)continue;unit.roamFrom=from;unit.roamGoal={x:to.x,y:to.y};unit.roamProgress=0;unit.direction=to.direction;occupied.add(key(to.x,to.y));setAction(unit,'walk',{family:'monster'});
 }
}
