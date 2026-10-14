import {tryMonsterRebirth,resetMonsterRebirth} from './monster-rebirth.js';
import {autoSkillMode} from './auto-skill-config.js';
import {automaticAttackSkill,automaticUtilitySkill,recordAutomaticCast} from './auto-combat.js';
import {updateRingCooldowns} from './ring-items.js';
import {reduceBossTimerOnDeath} from './boss-timers.js';
import {hitMagicShield} from './magic-shield.js';
import {recordCollectionMonster} from './permanent-state.js';
import {takeItem,inventoryKey} from './inventory.js';
import {isMoving,setMovementAction,chooseMovementMode,advanceMovement} from './hero-movement.js';
import {carryAmount,weaponUseBonus,instanceItem} from './native-stats.js';
import {itemName} from './item-names.js';
import {combatText} from './combat-text.js';
import {readNpcDialogue} from './npc-dialogue.js';
import {executeScriptView} from './npc-world.js';
// Source-backed core rules are separated from portrait controls and routing.
import {attributes,addItem} from './character.js';
import {gainExperience} from './progression.js';
import {savePets,restorePets} from './pet-state.js';
import {canEnterCell} from './map-flags.js';
import {ANIMATIONS,setAction,advanceAnimation,skillAction} from './animation.js';
import {rollGroundDrops,restoreGroundItems} from './loot.js';
import {findNearestPath,finishEmptyPath} from './pathfinding.js';
import {initializeMonsterMotion,resetMonsterMotion,updateMonsterMotion} from './monster-motion.js';
import {updateMonsterAI,resetMonsterAI,provokeMonster,clearMonsterAggro,monsterCanStrike} from './monster-ai.js';
import {nativeRoll,damageAfterDefense,rollEvade,combatProperties,equipmentStatus,swordMiss,offenseRoll} from './native-damage.js';
import {resetStatuses,updateStatuses,isParalyzed,isFrozen,applyStatus,effectiveDefense} from './statuses.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {initializeSpecial,updateSpecialSpawns,spawnUnit,emptySpawnCell} from './monster-spawning.js';
import {updateProjectiles,launchProjectile,addVisual,MONSTER_EFFECTS} from './projectiles.js';
import {usableSkill,explicitSkill,corpseTarget,attackRange,SELF_SKILLS,beginHeroSkill,releaseHeroSkill} from './combat-skills.js';
import {updateCombatEffects} from './combat-effects.js';
import {monsterStrike} from './monster-attacks.js';
import {petKill} from './pet-growth.js';
import {followingPet} from './allies.js';
import {difficultyMonster} from './difficulty.js';
import {updateDefense,saveDefense} from './defense.js';
import {enterChallenge,normalizeChallengeRecords,updateChallenge,saveChallenge} from './challenges.js';
import {normalizeAura} from './dark-aura.js';
export const COMBAT_RULES={sourceFps:50,playerAttackSeconds:.96,walkTilesPerSecond:1.5625,runTilesPerSecond:3.125,coreDamageVerified:true,damageFormulaVerified:false,skillFormulaVerified:false,respawnSeconds:20};
export class Combat {
 constructor(player,content,random=Math.random,groundState={},monsterRandom=Math.random,battleRandom=Math.random,petState=[],defenseState=null,challengeState=null){this.restoredChallenge=challengeState;normalizeChallengeRecords(player);this.restoredDefense=defenseState;this.scriptLocked=false;this.restoredPets=restorePets(petState,content);this.waitingPets=[];this.zones=[];this.battleRandom=battleRandom;this.nextSpawnId=0;this.nextEffectId=0;this.effectVersion=0;this.effects=[];this.projectiles=[];resetStatuses(player);this.player=normalizeAura(player);this.content=content;this.random=random;this.monsterRandom=monsterRandom;this.monsterNames=new Map(content.monsters.filter(m=>m&&m.name!=='0').map(m=>[m.name,m]));this.targetId=null;this.elapsed=0;this.hitClock=COMBAT_RULES.playerAttackSeconds;this.attackPeriod=COMBAT_RULES.playerAttackSeconds;this.events=[];this.recovery=[];this.hitCount=0;this.groundByMap=restoreGroundItems(groundState,content);this.lootVersion=0;this.nextDropId=Object.values(this.groundByMap).flat().reduce((n,g)=>Math.max(n,Number(g.id.match(/:loot:(\d+)$/)?.[1])||0),0);}
 enter(map,position){const pets=this.units?[...this.units.filter(u=>u.alive&&followingPet(u)),...this.waitingPets]:this.restoredPets;this.defense=null;this.defenseNotice=null;this.waitingPets=[];this.restoredPets=[];this.events=[];this.effects=[];this.particles=[];this.particleView=null;this.projectiles=[];this.zones=[];this.heroWindup=null;this.pendingSkill=null;this.stepDistance=0;this.map=map;this.position={...position,direction:4,action:'idle',actionTime:0,animationElapsed:0};if(this.player.hp<=0){this.recovery=[];this.player.healingPool=0;this.player.mpRecoveryPool=0;this.player.invisible=false;this.player.invisibleFrames=0;this.player.magicShieldFrames=0;setAction(this.position,'death');this.position.animationElapsed=ANIMATIONS.hero.death.seconds;this.position.actionTime=0;}this.units=map.spawns.map((s,index)=>{const d=difficultyMonster(this.monsterNames.get(s.name)||this.content.monsters[s.monsterId],this.player);return d&&d.name!=='0'?{...s,sourceMonsterId:s.monsterId,monsterId:d.id,id:map.id+':'+index,definition:d,hp:d.hp,alive:true,direction:4,action:'idle',actionTime:0,animationElapsed:0,attackClock:0,regenClock:0}:null;}).filter(u=>u&&!pets.some(p=>p.originId===u.id));for(const unit of this.units){initializeMonsterMotion(unit);resetMonsterAI(unit);resetStatuses(unit);initializeSpecial(unit,this.battleRandom);}this.waitingPets=pets;this.restoreWaitingPets();this.farmType=null;this.manualPath=false;this.moveMode='walk';this.counterTargetId=null;this.resumeTargetId=null;this.threats=new Map();this.nextSearchAt=0;this.targetId=null;this.path=[];this.trackedTargetCell=null;this.nextTargetPathAt=0;this.groundItems=this.groundByMap[map.id]=(this.groundByMap[map.id]||[]).filter(g=>g.x>=0&&g.y>=0&&g.x<map.width&&g.y<map.height);this.autoLoot=this.player.hp>0&&this.groundItems.length>0;this.lootingId=null;this.lootWaitingForSpace=false;this.nextLootRetryAt=0;this.lootAfter=0;this.nextAutoTemptAt=0;this.lastAutoCast=null;this.lootVersion++;enterChallenge(this);}
 restoreWaitingPets(){
  if(!this.waitingPets.length)return;const origin={x:Math.round(this.position.x),y:Math.round(this.position.y)},queue=[origin],seen=new Set([origin.x+','+origin.y]),candidates=[];
  for(let i=0;i<queue.length&&i<120;i++){const p=queue[i];if(i)candidates.push(p);for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const n={x:p.x+dx,y:p.y+dy},key=n.x+','+n.y;if(!seen.has(key)&&this.walkable(n.x,n.y)){seen.add(key);queue.push(n);}}}
  this.waitingPets=this.waitingPets.filter(pet=>{const point=emptySpawnCell(this,origin,candidates);const moved=spawnUnit(this,pet.definition,point,{summoned:true,summonSkill:pet.summonSkill,petLevel:pet.petLevel,petKills:pet.petKills,originId:pet.originId,healingPool:pet.healingPool||0});if(!moved)return true;moved.hp=pet.hp;moved.statuses=pet.statuses||{};return false;});
 }
 saveChallenge(){return saveChallenge(this);}
 saveDefense(){return saveDefense(this);}
 savePets(){return savePets([...(this.units||[]),...this.waitingPets]);}
 runScript(script,page='Start',destination=null){const view=readNpcDialogue(script,this.player,this.content,page,{map:this.map,units:this.units,waitingPets:this.waitingPets,defense:this.defense,random:this.random});this.scriptState||={};this.mapFlagsByMap||={};view.applied=executeScriptView(this,view,this.scriptState,this.mapFlagsByMap,destination||this.map);this.lastScript=view;this.scriptRevision=(this.scriptRevision||0)+1;return view;}
 inRange(unit){return !unit.removed&&Math.abs(unit.x-this.position.x)<=12&&Math.abs(unit.y-this.position.y)<=15;}
 nearby(limit=6){return this.units.filter(u=>u.alive&&!u.summoned&&this.inRange(u)).sort((a,b)=>Math.hypot(a.x-this.position.x,a.y-this.position.y)-Math.hypot(b.x-this.position.x,b.y-this.position.y)).slice(0,limit);}
 nearbyTypes(){const groups=new Map();for(const u of this.units.filter(u=>!u.summoned&&this.inRange(u)).sort((a,b)=>Math.hypot(a.x-this.position.x,a.y-this.position.y)-Math.hypot(b.x-this.position.x,b.y-this.position.y))){const id=u.definition.id;if(!groups.has(id))groups.set(id,{kind:'monster',monsterId:id,definition:u.definition,alive:0});if(u.alive)groups.get(id).alive++;}if(this.farmType!==null&&this.farmType!==undefined&&!groups.has(this.farmType))groups.set(this.farmType,{kind:'monster',monsterId:this.farmType,definition:this.content.monsters[this.farmType],alive:0});return [...groups.values()];}
 stopFarming({keepWalking=false}={}){this.manualPath=false;this.counterTargetId=null;this.resumeTargetId=null;this.threats?.clear();this.farmType=null;this.targetId=null;this.path=[];this.autoLoot=false;this.lootingId=null;this.lootWaitingForSpace=false;this.nextSearchAt=0;this.heroWindup=null;this.pendingSkill=null;if(this.position&&(['attack','cast'].includes(this.position.action)||!keepWalking&&isMoving(this.position)))setAction(this.position,'idle');}
 startFarming(monsterId,preferredId=null){if(this.scriptLocked||this.player.hp<=0||!this.units.some(u=>!u.summoned&&u.definition.id===monsterId))return false;this.stopFarming({keepWalking:true});this.farmType=monsterId;this.acquireFarmTarget(preferredId);return true;}
 acquireFarmTarget(preferredId=null){this.nextSearchAt=this.elapsed+.5;const candidates=this.nearby(Infinity).filter(u=>u.definition.id===this.farmType);if(preferredId)candidates.sort((a,b)=>Number(b.id===preferredId)-Number(a.id===preferredId));for(const u of candidates){const path=this.findPath(u);if(path===null)continue;this.targetId=u.id;this.path=path;return true;}this.targetId=null;return false;}
 approach(point){if(this.player.hp<=0)return false;this.stopFarming({keepWalking:true});const path=findNearestPath(this.map,this.position,point,(x,y)=>this.walkable(x,y),{range:1,canStop:p=>this.canAttackFrom(p,point)});if(path===null)return false;this.path=path;this.manualPath=true;this.movePolicy='auto';this.moveMode=chooseMovementMode(this);if(isMoving(this.position))setMovementAction(this.position,this.moveMode);return true;}
 target(){return this.units.find(u=>u.id===this.targetId&&u.alive&&!u.summoned);}
 counterAttack(unit){
  if(this.scriptLocked||!unit?.alive||unit.summoned||this.player.hp<=0||this.manualPath)return;
  this.threats||=new Map();this.threats.set(unit.id,this.elapsed+15);
  if(this.counterTargetId&&this.target()?.id===this.counterTargetId)return;
  const path=this.findPath(unit);if(path===null)return;
  if(!this.counterTargetId){this.resumeTargetId=this.targetId;}
  this.counterTargetId=unit.id;this.targetId=unit.id;this.path=path;this.autoLoot=false;this.lootingId=null;this.trackedTargetCell=null;
 }
 finishCounter(){
  const resume=this.resumeTargetId;this.threats?.delete(this.counterTargetId);
  this.counterTargetId=null;this.targetId=null;this.path=[];
  const next=[...(this.threats||[])].map(([id,until])=>({u:this.units.find(u=>u.id===id&&u.alive&&!u.summoned),until})).filter(t=>t.u&&t.until>this.elapsed&&this.inRange(t.u)).sort((a,b)=>Math.hypot(a.u.x-this.position.x,a.u.y-this.position.y)-Math.hypot(b.u.x-this.position.x,b.u.y-this.position.y));
  for(const {u}of next){this.counterAttack(u);if(this.counterTargetId){this.resumeTargetId=resume;return;}}
  const previous=this.units.find(u=>u.id===resume&&u.alive&&!u.summoned);this.resumeTargetId=null;
  if(previous&&this.autoLoot){this.resumeTargetId=previous.id;return;}
  if(previous){const path=this.findPath(previous);if(path!==null){this.targetId=previous.id;this.path=path;}}
 }
 select(id){if(this.scriptLocked)return false;const u=this.units.find(u=>u.id===id&&u.alive&&!u.summoned);if(!u||this.player.hp<=0)return false;const path=this.findPath(u);if(path===null){this.targetId=null;return false;}this.manualPath=false;this.counterTargetId=null;this.resumeTargetId=null;this.targetId=id;this.path=path;this.autoLoot=false;this.lootingId=null;return true;}
 walkable(x,y){if(x<0||y<0||x>=this.map.width||y>=this.map.height)return false;const c=this.map.cells[x*this.map.height+y];return canEnterCell(c[1]);}
 canAttackFrom(position,target,range=1,skillName=null){if(range===2&&(skillName||this.player.activeSkill)==='地狱雷光'&&Math.abs(Math.round(position.x)-Math.round(target.x))+Math.abs(Math.round(position.y)-Math.round(target.y))>=4)return false;if(Math.max(Math.abs(position.x-target.x),Math.abs(position.y-target.y))>range+.1)return false;const x=Math.round(position.x),y=Math.round(position.y),dx=Math.sign(Math.round(target.x)-x),dy=Math.sign(Math.round(target.y)-y);return !dx||!dy||this.walkable(x+dx,y)&&this.walkable(x,y+dy);}
 moveTo(x,y,options={}){return this.moveAlong(findNearestPath(this.map,this.position,{x,y},(x,y)=>this.walkable(x,y)),options);}
 // Navigation commits its already validated walking segment, preserving the
 // same walk/run policy and continuous animation clock as ordinary movement.
 moveAlong(path,{run}={}){if(this.scriptLocked||this.player.hp<=0||path===null)return false;this.stopFarming({keepWalking:true});this.path=path;this.manualPath=true;this.movePolicy=typeof run==='boolean'?(run?'run':'walk'):'auto';this.moveMode=chooseMovementMode(this);if(isMoving(this.position))setMovementAction(this.position,this.moveMode);return true;}
 collect(id){if(this.scriptLocked)return false;const item=this.groundItems.find(g=>g.id===id);if(!item||this.player.hp<=0)return false;const path=this.findPath(item,0);if(path===null||!this.moveAlong(path))return false;this.autoLoot=true;this.lootingId=id;this.lootAfter=this.elapsed;return true;}
 planPickup(){
  this.lootWaitingForSpace=false;this.nextLootRetryAt=this.elapsed+.5;
  const nearby=this.groundItems.filter(g=>Math.hypot(g.x-this.position.x,g.y-this.position.y)<=12).sort((a,b)=>Math.hypot(a.x-this.position.x,a.y-this.position.y)-Math.hypot(b.x-this.position.x,b.y-this.position.y));
  for(const item of nearby){if(item.kind!=='gold'&&carryAmount(this.player,this.content,item.itemId,item.quantity,item)<=0){this.lootWaitingForSpace=true;continue;}const path=this.findPath(item,0);if(path!==null){this.autoLoot=true;this.path=path;this.lootingId=item.id;return;}}
  this.autoLoot=false;this.lootingId=null;
 }
 pickupAtFeet(){
  if(this.player.hp<=0)return;
  for(let i=this.groundItems.length-1;i>=0;i--){const g=this.groundItems[i];if(Math.hypot(g.x-this.position.x,g.y-this.position.y)>.08||!this.walkable(g.x,g.y))continue;
   const quantity=g.kind==='gold'?g.quantity:carryAmount(this.player,this.content,g.itemId,g.quantity,g);if(!quantity)continue;
   if(g.kind==='gold')this.player.gold+=quantity;else {
    let metadata={...g,dropSources:[{mode:this.player.gameMode||0,quantity}]};
    let remainingSources;if(g.discarded){const clone=JSON.parse(JSON.stringify(g)),taken=takeItem([clone],inventoryKey(clone),quantity);metadata={...g,dropSources:taken.dropSources||[]};remainingSources=clone.dropSources;}
    if(!addItem(this.player,g.itemId,quantity,metadata))continue;
    if(g.discarded)g.dropSources=remainingSources;
   }
   this.audio?.pickup(this.content.items[g.itemId],g.kind==='gold');const name=g.kind==='gold'?'金币':itemName(instanceItem(this.content.items[g.itemId],g));combatText(this,g,name+' +'+quantity,{kind:'loot',actorId:'player',color:'#ffe3a0',duration:1.2});g.quantity-=quantity;if(g.quantity===0)this.groundItems.splice(i,1);if(this.lootingId===g.id)this.lootingId=null;this.lootVersion++;
  }
 }
 automaticAttackSkill(target){return automaticAttackSkill(this,target);}
 attackSkill(target=this.target()){return autoSkillMode(this.player)?this.automaticAttackSkill(target):usableSkill(this);}
 findPath(target,range,skillName=null){const skill=range===undefined?this.attackSkill(target):null;range??=attackRange(this,skill);skillName??=skill?.name;const start={x:Math.round(this.position.x),y:Math.round(this.position.y)},key=p=>p.x+','+p.y,queue=[start],seen=new Map([[key(start),null]]);let end=null;for(let i=0;i<queue.length&&i<8000;i++){const p=queue[i];if(Math.max(Math.abs(p.x-target.x),Math.abs(p.y-target.y))<=range&&(range===0||this.canAttackFrom(p,target,range,skillName)&&this.lineOfSight(p,target))){end=p;break;}const directions=[[0,-1],[1,0],[0,1],[-1,0],[1,-1],[1,1],[-1,1],[-1,-1]].sort((a,b)=>Math.hypot(p.x+a[0]-target.x,p.y+a[1]-target.y)-Math.hypot(p.x+b[0]-target.x,p.y+b[1]-target.y));for(const [dx,dy]of directions){const n={x:p.x+dx,y:p.y+dy};if(seen.has(key(n))||!this.walkable(n.x,n.y))continue;if(dx&&dy&&(!this.walkable(p.x+dx,p.y)||!this.walkable(p.x,p.y+dy)))continue;seen.set(key(n),p);queue.push(n);}}if(!end)return null;const path=[];for(let p=end;seen.get(key(p));p=seen.get(key(p)))path.unshift(p);return finishEmptyPath(path,this.position,(x,y)=>this.walkable(x,y));}
 direction(a,b){const angle=Math.atan2(b.x-a.x,-(b.y-a.y));return (Math.round(angle/(Math.PI/4))+8)%8;}
 damage(attack,defense){return damageAfterDefense(attack,defense);}
 randomRange(range){return nativeRoll(range,this.random);}
 update(dt){if(this.story)return;try{if(['failed','abandoned'].includes(this.challenge?.status)){this.elapsed+=dt;advanceAnimation(this.position,dt);for(const u of this.units)if(!u.alive)advanceAnimation(u,dt,'monster');return;}this.updateWorld(dt);}finally{updateChallenge(this,dt);}}
 updateWorld(dt){if(this.defense?.status==='failed'){this.elapsed+=dt;for(const u of this.units)if(!u.alive)advanceAnimation(u,dt,'monster');return;}this.elapsed+=dt;updateDefense(this,dt);if(this.defense?.status==='failed')return;this.bossTimerClock=(this.bossTimerClock||0)+dt;const seconds=Math.floor(this.bossTimerClock);if(seconds){this.bossTimerClock-=seconds;updateRingCooldowns(this.player,seconds);this.player.bossTimers=(this.player.bossTimers||[]).map(t=>t>0?Math.max(0,t-seconds):t);}this.playerProperties=combatProperties(this.player,this.content);this.events=this.events.filter(e=>e.until>this.elapsed);
 updateStatuses(this,this.player,dt,{player:true});this.playerProperties=combatProperties(this.player,this.content);const action=this.position.action,stepTicks=action==='walk'?7:action==='run'||action==='hurt'?5:action==='attack'?8-Math.min(5,this.playerProperties.fastAttack):action==='cast'?8-Math.min(5,this.playerProperties.fastCast):12,heroDt=isParalyzed(this.player)?0:dt*(isFrozen(this.player)?stepTicks/(stepTicks+1):1);
 // One bounded actor clock recharges during animation, travel and idle. Target
 // changes and retaliation must never reset it or make an early second attack.
 if(this.player.hp>0)this.hitClock=Math.min(this.attackPeriod,this.hitClock+heroDt);advanceAnimation(this.position,heroDt);
 for(const u of this.units){if(!u.alive&&!u.temporary&&u.respawnAt<=this.elapsed&&(u.bossTimerIndex===undefined||!(this.player.bossTimers?.[u.bossTimerIndex]>0))){resetMonsterRebirth(u);u.alive=true;u.hp=u.definition.hp;resetMonsterMotion(u);resetMonsterAI(u);resetStatuses(u);initializeSpecial(u,this.battleRandom);u.refined=false;setAction(u,'idle',{restart:true,family:'monster'});}if(!u.alive){advanceAnimation(u,dt,'monster');continue;}updateStatuses(this,u,dt);advanceAnimation(u,isParalyzed(u)?0:dt*(isFrozen(u)?(u.action==='idle'?12/13:4/5):1),'monster');if(u.alive&&u.definition.regenFrames>0){u.regenClock+=dt;const period=u.definition.regenFrames/50;while(u.regenClock>=period){u.regenClock-=period;u.hp=Math.min(u.definition.hp,u.hp+1);}}}
 this.restoreWaitingPets();updateSpecialSpawns(this,dt);updateCombatEffects(this,dt);updateProjectiles(this,dt);
 if(this.heroWindup&&this.player.hp>0){this.heroWindup.remaining-=heroDt;if(this.heroWindup.remaining<=1e-8){const w=this.heroWindup;this.heroWindup=null;const target=this.units.find(u=>u.id===w.targetId&&(u.alive||w.skill.name==='炼尸咒'&&!u.refined));if(SELF_SKILLS.has(w.skill.name)||target&&this.canAttackFrom(this.position,target,w.range,w.skill.name)&&this.lineOfSight(this.position,target))releaseHeroSkill(this,w.skill,target);}}

 updateMonsterAI(this,dt);updateMonsterMotion(this,dt);
 if(this.player.hp<=0){this.recovery=[];this.player.healingPool=0;this.player.mpRecoveryPool=0;}
 for(const effect of this.recovery){effect.clock+=dt;if(effect.clock>=1){effect.clock-=1;const n=Math.min(5,effect.remaining);this.player[effect.stat]=Math.min(this.player.base[effect.stat],this.player[effect.stat]+n);effect.remaining-=n;}}this.recovery=this.recovery.filter(e=>e.remaining>0);
 if(this.player.hp<=0||isParalyzed(this.player))return;if(this.pendingSkill&&this.attackReady()){const name=this.pendingSkill;this.pendingSkill=null;this.player.activeSkill=name;const skill=explicitSkill(this,name),target=name==='炼尸咒'?corpseTarget(this):null;if(skill&&(SELF_SKILLS.has(name)||target))beginHeroSkill(this,skill,target);}if(this.manualPath&&!this.path.length)this.manualPath=false;if(this.counterTargetId&&(!this.target()||!this.inRange(this.target())||this.threats.get(this.counterTargetId)<=this.elapsed))this.finishCounter();this.pickupAtFeet();if(!this.target()&&!this.path.length&&this.position.actionTime<=0&&(this.autoLoot&&this.elapsed>=this.lootAfter||this.lootWaitingForSpace&&this.elapsed>=this.nextLootRetryAt))this.planPickup();if(!this.counterTargetId&&!this.target()&&!this.autoLoot&&!this.path.length&&this.resumeTargetId){const previous=this.units.find(u=>u.id===this.resumeTargetId&&u.alive&&!u.summoned);this.resumeTargetId=null;if(previous){const path=this.findPath(previous);if(path!==null){this.targetId=previous.id;this.path=path;}}}if(this.farmType!==null&&this.farmType!==undefined&&!this.target()&&!this.autoLoot&&!this.path.length&&!this.lootingId&&this.position.actionTime<=0&&this.elapsed>=this.nextSearchAt)this.acquireFarmTarget();
 if(autoSkillMode(this.player)&&this.attackReady()){const choice=automaticUtilitySkill(this);if(choice&&beginHeroSkill(this,choice.skill,choice.target)){recordAutomaticCast(this,choice.skill);return;}}
 const target=this.target(),skill=this.attackSkill(target),range=attackRange(this,skill);
 if(target){
  if(this.canAttackFrom(this.position,target,range,skill.name)&&this.lineOfSight(this.position,target))this.path=[];
  else if(this.position.actionTime<=0){const cell=Math.round(target.x)+','+Math.round(target.y);if(!this.path.length||cell!==this.trackedTargetCell&&this.elapsed>=this.nextTargetPathAt){const path=this.findPath(target,range,skill.name);this.nextTargetPathAt=this.elapsed+.25;this.trackedTargetCell=cell;if(path===null){this.targetId=null;this.path=[];this.nextSearchAt=this.elapsed+.5;return;}this.path=path;}}
 }
 if(this.path.length&&this.position.actionTime<=0){
  const distance=advanceMovement(this,dt*(isFrozen(this.player)?.5:1),COMBAT_RULES);
  this.stepDistance=(this.stepDistance||0)+distance;if(this.stepDistance>=.65){this.stepDistance%=.65;this.audio?.step(this);}return;
 }
 if(isMoving(this.position))setAction(this.position,'idle');if(!target||!this.canAttackFrom(this.position,target,range,skill.name)||!this.lineOfSight(this.position,target))return;if(this.position.actionTime<=0)this.position.direction=this.direction(this.position,target);
 if(target.alive&&this.attackReady()&&beginHeroSkill(this,skill,target)&&autoSkillMode(this.player))recordAutomaticCast(this,skill);

 }
 attackReady(){return this.player.hp>0&&this.position.actionTime<=0&&this.hitClock>=this.attackPeriod-1e-8;}
 lineOfSight(a,b){return monsterCanStrike(this.map,{...a,definition:{attackKind:11,vision:Math.max(1,Math.ceil(Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y))))}},b);}
 requestSkill(name){if(this.scriptLocked||this.player.hp<=0||!explicitSkill(this,name)||!SELF_SKILLS.has(name)&&name!=='炼尸咒'||name==='炼尸咒'&&!corpseTarget(this))return false;this.pendingSkill=name;return true;}
 provoke(unit){provokeMonster(this,unit);}
 hurt(actor,damage,{player=false,source='player',color='#ffe5a2',continuous=false}={}){if(actor.hp<=0)return;actor.hp=Math.max(0,actor.hp-damage);if(player&&actor.magicShieldFrames>0){hitMagicShield(this);const shell=this.effects.find(e=>e.shield);if(shell)shell.shieldHitAt=shell.age;}const p=player?this.position:actor;combatText(this,p,(player?'−':'')+damage,{color:player?'#ffaaa0':color,actorId:player?'player':actor.id,appearance:player?null:actor.definition.appearance,aggregate:continuous,amount:damage,prefix:player?'−':''});if(actor.hp===0){if(player){this.audio?.hero(this.player.gender===1?'死亡-女':'死亡-男',this.position);this.stopFarming();this.recovery=[];resetStatuses(this.player);this.player.healingPool=0;this.player.mpRecoveryPool=0;this.player.invisible=false;this.player.invisibleFrames=0;this.player.magicShieldFrames=0;setAction(this.position,'death',{restart:true});}else{const pet=this.units.find(u=>u.id===source&&u.summoned);this.kill(actor,{reward:!actor.summoned&&(source==='player'||!!pet)});if(pet&&!actor.alive)petKill(this,pet);}}else if(damage>0&&!continuous){if(player)this.audio?.hero(this.player.gender===1?'被攻击-女':'被攻击-男',this.position,{cooldown:280});else this.audio?.monster(actor,3);}}
 heroHit(unit,attack,{magic=false,status=undefined,ignoreDefense=false,melee=false,continuous=false}={}){
  if(!unit.alive||unit.summoned||this.player.hp<=0)return;
  const props=this.playerProperties||combatProperties(this.player,this.content),tao=()=>offenseRoll(attributes(this.player,this.content),'tao',this.battleRandom);
  if(melee&&swordMiss(this.player,unit,props,this.battleRandom)){this.audio?.hero(this.player.equipment.weapon!==undefined?'挥空':'徒手',this.position);combatText(this,unit,'Miss',{kind:'miss',color:'#e9e2cc',actorId:unit.id,appearance:unit.definition.appearance});this.provoke(unit);return;}
  if(melee)this.audio?.hero(this.player.equipment.weapon!==undefined?'剑击':'手击',this.position);if(status===undefined)status=equipmentStatus(props,this.battleRandom);
  attack+=weaponUseBonus(this.player,this.content);
  if(status){if(status==='freeze'&&unit.statuses?.burn||status==='burn'&&unit.statuses?.freeze)attack=nativeRound(attack*1.1+1);const power=nativeRound(tao()/20+1);applyStatus(unit,status,{power,source:'player'});}
  if(!melee&&rollEvade(magic?unit.definition.magicEvade:unit.definition.physicalEvade,3,this.battleRandom)){combatText(this,unit,'Miss',{kind:'miss',color:'#e9e2cc',actorId:unit.id,appearance:unit.definition.appearance});return;}
  const damage=damageAfterDefense(attack,ignoreDefense?0:effectiveDefense(unit,magic));this.hitCount++;
  if(!status&&sampleMonsterRandom(this.battleRandom)*100<props.vampire*5){this.player.hp=Math.min(this.player.base.hp,this.player.hp+Math.min(50,props.vampire*3+Math.trunc(damage/8)));addVisual(this,73,this.position,{follow:this.position});status='vampire';}
  if(!status&&sampleMonsterRandom(this.battleRandom)*100<props.luck*5){this.player.mpRecoveryPool=(this.player.mpRecoveryPool||0)+Math.min(50,props.luck*2+Math.trunc(damage/10));addVisual(this,74,this.position,{follow:this.position});status='luck';}
  this.hurt(unit,damage,{continuous});
  if(unit.alive)provokeMonster(this,unit);
 }
 enemyHit(unit,target,{magic=false,continuous=false}={}){
  const player=target?.id==='player'||!target,actor=player?this.player:target;
  if(!unit.alive||actor.hp<=0)return;if(player)this.counterAttack(unit);
  const props=player?this.playerProperties||combatProperties(this.player,this.content):actor.definition;
  if(rollEvade(magic?props.magicEvade:props.physicalEvade,5,this.battleRandom))return;
  const status=equipmentStatus(unit.definition,this.battleRandom,{monster:true});
  if(status){let power=1;if(!player){power=nativeRound(sampleMonsterRandom(this.battleRandom)*3+1)-(status==='poison'?actor.definition.poison:0);}applyStatus(actor,status,{power,player,source:unit.id});}
  let defense=player?nativeRoll(attributes(this.player,this.content)[magic?'magicDefense':'defense'],this.battleRandom):effectiveDefense(actor,magic);
  if(player&&this.player.magicShieldFrames>0)defense+=(this.player.skills.find(s=>s.name==='魔法盾')?.level||0)*(magic?5:6);
  const damage=damageAfterDefense(unit.definition.attack,defense);
  const protectedByRing=player&&['ringLeft','ringRight'].some(slot=>this.content.items[this.player.equipment[slot]]?.name==='护身戒指');
  if(protectedByRing){this.player.mp-=damage*2;if(this.player.mp<0||!magic&&this.player.mp===0){this.player.mp=0;this.hurt(actor,damage,{player,source:unit.id,color:'#df7e68',continuous});}}
  else this.hurt(actor,damage,{player,source:unit.id,color:'#df7e68',continuous});
  const reflected=player&&props.reflect>0&&sampleMonsterRandom(this.battleRandom)*100<props.reflect*5;
  if(reflected){this.audio?.hero('伤害反弹',this.position);this.hurt(unit,Math.trunc(unit.definition.attack/2)+1,{source:'player'});}
  // Native 5d4460/5d4a20: only action 1 (idle) enters 225 (hurt).
  // This belongs to the landed enemy-hit branch, even when a protection ring
  // pays with MP. Poison/burn use a different path; repeated hits never restart
  // the clip, and movement/attack/cast clocks and pending strikes survive.
  if(player&&!reflected&&this.player.hp>0&&this.position.action==='idle')setAction(this.position,'hurt');
  if(!player&&actor.alive){actor.targetUnitId=unit.id;provokeMonster(this,actor);}
 }
 monsterStrike(unit,target=null){monsterStrike(this,unit,target);}

 kill(u,{reward=!u.summoned}={}){
  if(!u.alive||tryMonsterRebirth(this,u))return;this.audio?.monster(u,4);u.alive=false;clearMonsterAggro(u);u.roamGoal=null;u.roamFrom=null;setAction(u,'death',{restart:true,family:'monster'});u.diedAt=this.elapsed;u.statuses={};u.respawnAt=u.temporary?Infinity:this.elapsed+COMBAT_RULES.respawnSeconds;this.threats?.delete(u.id);if(u.definition.event?.includes('#')){const event=this.runScript(u.definition.event);if(event.applied){const timer=event.effects.find(e=>e.kind==='change'&&/^bt\d*$/i.test(e.field));if(timer){u.bossTimerIndex=Number(timer.field.slice(2)||0);u.respawnAt=this.elapsed+Math.max(0,this.player.bossTimers[u.bossTimerIndex]);}}}const refresh=reduceBossTimerOnDeath(this,u);if(refresh)combatText(this,this.position,refresh.name+' 刷新-'+refresh.seconds+'秒',{kind:'refresh',actorId:'player',color:'#dddddd',duration:1.3});if(!reward)return;if(u.monsterId>=4)recordCollectionMonster(this.player,u.monsterId);if(gainExperience(this.player,u.definition.experience)){this.audio?.hero('升级',this.position);combatText(this,this.position,'Lv.'+this.player.level,{kind:'level',actorId:'player',color:'#ffe09a',duration:1.6});}
  const offsets=[[0,0],[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[1,-1],[-1,-1]],origin={x:Math.round(u.x),y:Math.round(u.y)},feet={x:Math.round(this.position.x),y:Math.round(this.position.y)};
  // A walkable tile can still be isolated by walls. Use the same player path
  // rules as collection, including blocked diagonal corners, before placing loot.
  let landings=offsets.map(([dx,dy])=>({x:origin.x+dx,y:origin.y+dy})).filter(p=>this.walkable(p.x,p.y)&&this.findPath(p,0)!==null);
  if(!landings.length)landings=offsets.map(([dx,dy])=>({x:feet.x+dx,y:feet.y+dy})).filter(p=>this.walkable(p.x,p.y)&&this.findPath(p,0)!==null);
  for(const drop of rollGroundDrops(u.definition,this.content,this.random,this.player)){
   const away=p=>Math.hypot(p.x-this.position.x,p.y-this.position.y)>.1,p=landings.find(p=>away(p)&&!this.groundItems.some(g=>g.x===p.x&&g.y===p.y))||landings.find(away)||landings[0];if(!p)continue;
   this.groundItems.push({id:this.map.id+':loot:'+(++this.nextDropId),...p,...drop});this.lootVersion++;
  }
  if(this.targetId===u.id){this.targetId=null;this.path=[];}this.autoLoot=this.player.hp>0&&this.groundItems.length>0;this.lootingId=null;this.lootAfter=this.elapsed+this.position.actionTime;
 }
 usePotion(item){if(this.player.hp<=0||!item||![3,4].includes(item.type))return false;let used=false;for(const stat of ['hp','mp'])if(item[stat]>0&&this.player[stat]<this.player.base[stat]){if(item.type===4)this.player[stat]=Math.min(this.player.base[stat],this.player[stat]+item[stat]);else {const key=stat==='hp'?'healingPool':'mpRecoveryPool';this.player[key]=(this.player[key]||0)+item[stat];}used=true;}if(used)this.audio?.ui(item.type===4?'道具-吃东西':'道具-喝药');return used;}
 revive(home){if(this.player.hp>0)return false;this.audio?.ui('复活');this.stopFarming();this.recovery=[];resetStatuses(this.player);this.heroWindup=null;this.events=[];this.effects=[];this.particles=[];this.particleView=null;this.projectiles=[];this.zones=[];this.player.invisible=false;this.player.invisibleFrames=0;this.player.magicShieldFrames=0;this.player.healingPool=0;this.player.mpRecoveryPool=0;for(const unit of this.units)clearMonsterAggro(unit);this.player.hp=this.player.base.hp;this.player.mp=this.player.base.mp;this.position={x:home.x,y:home.y,direction:4,action:'idle',actionTime:0,animationElapsed:0};return true;}
}
