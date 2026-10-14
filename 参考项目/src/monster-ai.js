import {followingPet} from './allies.js';
import {setAction} from './animation.js';
import {MAP_FLAG} from './map-flags.js';
import {monsterBehavior,monsterWalkable,monsterSpeed,nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {findMonsterPath} from './monster-path.js';
import {isParalyzed,isFrozen} from './statuses.js';

// Checked against the shipped executable; see reports/native-ai-source.json.
export const NATIVE_AI={fps:50,aggroFrames:750,fleeFrames:200,fleeChance:.1,fleeOffsetScale:9,fleeOffsetBase:-4,attackFrameTicks:4,attackFrames:6,damageFrame:5/6,routeRetrySeconds:.3};
const key=(x,y)=>x+','+y;
const distance=(a,b)=>Math.max(Math.abs(Math.round(a.x)-Math.round(b.x)),Math.abs(Math.round(a.y)-Math.round(b.y)));
const PIERCING=new Set([7,8,9,10,14,15,20]),FLEEING=new Set([6,8,20]);
function nearestLiving(unit,candidates,allowed=()=>true){
 let nearest,range=Infinity;
 for(const candidate of candidates){if(!candidate.alive||!allowed(candidate))continue;const d=distance(unit,candidate);if(d<range){nearest=candidate;range=d;}}
 return nearest;
}
export function monsterAttackRange(unit){return unit.definition.attackKind>10?Math.max(1,unit.definition.vision):1;}
export function monsterAttackSeconds(unit){const behavior=monsterBehavior(unit.definition);if([10,15].includes(behavior)&&unit.hp<unit.definition.hp*.3)unit.attackSpeedBoosted=true;const frames=[10,15].includes(behavior)&&unit.attackSpeedBoosted?nativeRound(unit.definition.attackFrames*.7):unit.definition.attackFrames;return Math.max(1,frames)/NATIVE_AI.fps;}
export function monsterSeesPlayer(unit,player,position){return monsterBehavior(unit.definition)>=0&&unit.definition.vision>0&&distance(unit,position)<=unit.definition.vision&&(!player.invisible||unit.definition.hp>999||PIERCING.has(monsterBehavior(unit.definition))&&distance(unit,position)<unit.definition.vision);}
export function clearMonsterAggro(unit){unit.aggro=false;unit.targetUnitId=null;unit.aggroUntil=0;unit.aiPath=[];unit.fleeTarget=null;unit.fleeUntil=0;unit.aiMode='idle';unit.attackWindup=null;unit.postAttackFlee=false;}
export function resetMonsterAI(unit){clearMonsterAggro(unit);unit.speedBoosted=false;unit.attackSpeedBoosted=false;unit.nextAttackAt=0;unit.nextAIPathAt=0;unit.aiPathTarget=null;unit.monsterHitCount=0;}
export function provokeMonster(combat,unit){if(!unit.alive||monsterBehavior(unit.definition)<0)return;unit.aggro=true;unit.aggroUntil=combat.elapsed+NATIVE_AI.aggroFrames/NATIVE_AI.fps;unit.nextAIPathAt=0;}

// Terrain checks block diagonal wall corners before the attack can be released.
export function monsterCanStrike(map,unit,position){
 const range=monsterAttackRange(unit);if(Math.max(Math.abs(unit.x-position.x),Math.abs(unit.y-position.y))>range+.1)return false;
 let x=Math.round(unit.x),y=Math.round(unit.y),tx=Math.round(position.x),ty=Math.round(position.y);
 const wall=(x,y)=>{const c=x>=0&&y>=0&&x<map.width&&y<map.height&&map.cells[x*map.height+y];return !c||[MAP_FLAG.GROUND_BLOCKED,MAP_FLAG.MIDDLE_BLOCKED].includes(c[1]);};
 const dx=Math.abs(tx-x),dy=Math.abs(ty-y),sx=Math.sign(tx-x),sy=Math.sign(ty-y);let error=dx-dy;
 while(x!==tx||y!==ty){const twice=2*error,nx=x+(twice>-dy?sx:0),ny=y+(twice<dx?sy:0);if(nx!==x&&ny!==y&&(wall(nx,y)||wall(x,ny)))return false;if(wall(nx,ny))return false;if(nx!==x)error-=dy;if(ny!==y)error+=dx;x=nx;y=ny;}
 return true;
}
function planStep(combat,unit,target,occupied,{flee=false,follow=false}={}){
 const targetKey=(flee?'flee:':'chase:')+key(Math.round(target.x),Math.round(target.y));
 if(targetKey!==unit.aiPathTarget||combat.elapsed>=unit.nextAIPathAt||!unit.aiPath.length){
  if(targetKey===unit.aiPathTarget&&combat.elapsed<unit.nextAIPathAt&&!unit.aiPath.length)return;
  unit.aiPathTarget=targetKey;unit.nextAIPathAt=combat.elapsed+NATIVE_AI.routeRetrySeconds;
  const blockers=new Set(occupied);blockers.delete(key(Math.round(unit.x),Math.round(unit.y)));
  unit.aiPath=findMonsterPath(combat.map,unit,target,blockers,{range:flee?0:follow?3:monsterAttackRange(unit),canStop:flee||follow?()=>true:p=>monsterCanStrike(combat.map,{...unit,...p},target),closest:flee||follow})||[];
 }
 const to=unit.aiPath[0];if(!to)return;
 const from={x:Math.round(unit.x),y:Math.round(unit.y)},dx=to.x-from.x,dy=to.y-from.y;
 if(occupied.has(key(to.x,to.y))||!monsterWalkable(combat.map,to.x,to.y)||dx&&dy&&(occupied.has(key(from.x+dx,from.y))||occupied.has(key(from.x,from.y+dy)))){unit.aiPath=[];return;}
 unit.aiPath.shift();unit.roamFrom=from;unit.roamGoal=to;unit.roamProgress=0;unit.direction=combat.direction(from,to);occupied.add(key(to.x,to.y));setAction(unit,'walk',{family:'monster'});
}
function chooseFleeTarget(combat,unit){
 if(!FLEEING.has(monsterBehavior(unit.definition))||!unit.aggro||monsterSpeed(unit)<=0||sampleMonsterRandom(combat.monsterRandom)>=NATIVE_AI.fleeChance)return;
 const offset=()=>nativeRound(sampleMonsterRandom(combat.monsterRandom)*NATIVE_AI.fleeOffsetScale)+NATIVE_AI.fleeOffsetBase;
 unit.fleeTarget={x:Math.round(unit.x)+offset(),y:Math.round(unit.y)+offset()};unit.fleeUntil=combat.elapsed+NATIVE_AI.fleeFrames/NATIVE_AI.fps;unit.aiPath=[];unit.aiPathTarget=null;unit.nextAIPathAt=0;
}
export function updateMonsterAI(combat,dt){
 const {player,position,map,units}=combat,occupied=new Set([key(Math.round(position.x),Math.round(position.y)),...(map.npcs||[]).map(n=>key(n.x,n.y))]);
 // One index per simulation step. Candidate order remains the source unit
 // order, including nearest-distance ties; liveness is checked when consumed.
 const byId=new Map(),friends=[],enemies=[],flags=[];
 const indexUnits=()=>{byId.clear();friends.length=enemies.length=flags.length=0;for(const unit of units){byId.set(unit.id,unit);if(unit.summoned)friends.push(unit);else enemies.push(unit);if(unit.defenseFlag)flags.push(unit);}};indexUnits();
 for(const unit of units)if(unit.alive){occupied.add(key(Math.round(unit.x),Math.round(unit.y)));if(unit.roamFrom)occupied.add(key(unit.roamFrom.x,unit.roamFrom.y));if(unit.roamGoal)occupied.add(key(unit.roamGoal.x,unit.roamGoal.y));}
 for(const unit of units){
  if(!unit.alive)continue;
  if(isParalyzed(unit))continue;
  if(player.hp<=0||monsterBehavior(unit.definition)<0){clearMonsterAggro(unit);continue;}
  let victim=byId.get(unit.targetUnitId);if(!victim?.alive||!!victim.summoned===!!unit.summoned)victim=undefined;
  if(unit.summoned&&!victim){victim=nearestLiving(unit,enemies,u=>(monsterBehavior(u.definition)>=0||u.trainingDummy)&&distance(unit,u)<=unit.definition.vision);if(victim){unit.targetUnitId=victim.id;provokeMonster(combat,unit);}}
  if(unit.siege&&!victim&&!unit.aggro&&!monsterSeesPlayer(unit,player,position)){victim=nearestLiving(unit,flags);if(victim){unit.targetUnitId=victim.id;provokeMonster(combat,unit);}}
  if(!unit.summoned&&!victim&&!unit.aggro){victim=nearestLiving(unit,friends,u=>distance(unit,u)<=unit.definition.vision);if(victim){unit.targetUnitId=victim.id;provokeMonster(combat,unit);}}
  if(unit.summoned&&!victim){clearMonsterAggro(unit);if(followingPet(unit)&&!unit.roamGoal&&unit.actionTime<=0&&distance(unit,position)>3){unit.aiMode='follow';planStep(combat,unit,position,occupied,{follow:true});}continue;}
  const destination=victim||position,sees=unit.summoned||victim||monsterSeesPlayer(unit,player,position);
  if(player.invisible&&PIERCING.has(monsterBehavior(unit.definition))&&distance(unit,position)<unit.definition.vision)player.invisible=false;
  if(unit.aggro&&combat.elapsed>=unit.aggroUntil){clearMonsterAggro(unit);if(sees)provokeMonster(combat,unit);}
  if(!unit.aggro&&sees)provokeMonster(combat,unit);
  if(!unit.aggro)continue;
  if(unit.attackWindup){unit.attackWindup.remaining-=dt*(isFrozen(unit)?.8:1);if(unit.attackWindup.remaining<=1e-8){unit.attackWindup=null;if(monsterCanStrike(map,unit,destination)){combat.monsterStrike(unit,victim);unit.monsterHitCount++;indexUnits();}}}
  if(player.hp<=0)continue;
  if(unit.postAttackFlee&&unit.actionTime<=0){unit.postAttackFlee=false;unit.nextAttackAt=combat.elapsed+unit.attackCooldown;provokeMonster(combat,unit);chooseFleeTarget(combat,unit);}
  if(unit.fleeTarget&&(combat.elapsed>=unit.fleeUntil||Math.hypot(unit.x-unit.fleeTarget.x,unit.y-unit.fleeTarget.y)<.08)){unit.fleeTarget=null;unit.aiPath=[];unit.aiPathTarget=null;}
  if(unit.actionTime>0||unit.roamGoal)continue;
  if(unit.fleeTarget){unit.aiMode='flee';planStep(combat,unit,unit.fleeTarget,occupied,{flee:true});continue;}
  if(monsterCanStrike(map,unit,destination)){
   unit.aiMode='attack';unit.aiPath=[];
   if(combat.elapsed<unit.nextAttackAt)continue;const cooldown=monsterAttackSeconds(unit),duration=NATIVE_AI.attackFrameTicks*NATIVE_AI.attackFrames/NATIVE_AI.fps;
   unit.direction=combat.direction(unit,destination);setAction(unit,'attack',{restart:true,family:'monster'});unit.actionTime=duration;unit.animationDuration=duration;unit.attackCooldown=cooldown;unit.attackWindup={remaining:duration*(unit.definition.attackKind===5?1/6:NATIVE_AI.damageFrame)};unit.postAttackFlee=true;
  }else{unit.aiMode='chase';if(monsterSpeed(unit)>0)planStep(combat,unit,destination,occupied);}
 }
}
