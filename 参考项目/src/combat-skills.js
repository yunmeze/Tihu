import {startMagicShield} from './magic-shield.js';
import {followingPet} from './allies.js';
import {attributes} from './character.js';
import {setAction,releaseTime} from './animation.js';
import {nativeRoll,skillLevel,spellPower,equipmentStatus,combatProperties,offenseRoll} from './native-damage.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {applyStatus} from './statuses.js';
import {launchProjectile,addVisual} from './projectiles.js';
import {canSummon,summon} from './monster-spawning.js';
import {resetMonsterAI} from './monster-ai.js';
import {clearMonsterAggro} from './monster-ai.js';
import {queueHealing,firewall} from './combat-effects.js';
import {SKILL_ORDER} from './character.js';
import {instanceItem,recordWeaponUse} from './native-stats.js';

export const FLIGHT_SKILLS={火球术:14,爆裂火球:15,御冰术:16,强冰术:17,灵魂火符:6};
import {SUMMON_SKILLS,SELF_SKILLS,PASSIVE_SKILLS} from './skill-roles.js';
import {autoSkillMode} from './auto-skill-config.js';
export {SUMMON_SKILLS,SELF_SKILLS,PASSIVE_SKILLS} from './skill-roles.js';
export const IMPLEMENTED_SKILLS=new Set(SKILL_ORDER);
const BASIC={name:'基本剑术',action:'attack',mpCost:0};
function lightningAftershock(combat,point,level,remaining){
 if(remaining<=0)return;
 const cell={x:Math.round(point.x),y:Math.round(point.y)};
 // Native 5bcac7 / 5bcd46: hit on frame 2, four visible frames per
 // cycle, then repeat L-1 times. 628590 uses magicRoll / 10 + 2*L.
 addVisual(combat,56,cell,{duration:.4,clipFrames:4,hitAt:.1,onHit:()=>{
  const victim=combat.units.find(u=>u.alive&&!u.summoned&&Math.round(u.x)===cell.x&&Math.round(u.y)===cell.y);
  if(victim)combat.heroHit(victim,nativeRound(offenseRoll(attributes(combat.player,combat.content),'magic',combat.battleRandom)/10+2*level),{magic:true});
 },onComplete:()=>lightningAftershock(combat,cell,level,remaining-1)});
}
export function explicitSkill(combat,name){
 const record=combat.content.skills?.records?.find(s=>s.name===name);
 if(!IMPLEMENTED_SKILLS.has(name)||!skillLevel(combat.player,name)||combat.player.mp<(record?.mpCost||0)||SUMMON_SKILLS.has(name)&&!canSummon(combat,name)||name==='诱惑之光'&&combat.units.filter(u=>u.alive&&followingPet(u)).length>=3)return null;
 return {name,action:PASSIVE_SKILLS.has(name)||['半月斩','烈火斩','冰封斩'].includes(name)?'attack':'cast',mpCost:record?.mpCost||0};
}
export function usableSkill(combat){if(autoSkillMode(combat.player))return combat.automaticAttackSkill(combat.target());const name=combat.player.activeSkill;if(PASSIVE_SKILLS.has(name)||SELF_SKILLS.has(name)&&name!=='地狱雷光'||name==='炼尸咒')return BASIC;return explicitSkill(combat,name)||BASIC;}
export function attackRange(combat,skill=usableSkill(combat)){return skill.name==='地狱雷光'?2:skill.action==='cast'&&!SELF_SKILLS.has(skill.name)?6:1;}
export function corpseTarget(combat){return combat.units.filter(u=>!u.alive&&!u.summoned&&!u.refined&&combat.elapsed-u.diedAt<=20&&Math.max(Math.abs(u.x-combat.position.x),Math.abs(u.y-combat.position.y))<=6&&combat.lineOfSight(combat.position,u)).sort((a,b)=>Math.hypot(a.x-combat.position.x,a.y-combat.position.y)-Math.hypot(b.x-combat.position.x,b.y-combat.position.y))[0];}
export function releaseWeaponSkill(combat,target){
 // 61c8ce..61ccd7: basic sword contact invokes the item's effect directly,
 // even if its spell has not been learned; mages do not pay this MP charge.
 const item=instanceItem(combat.content.items[combat.player.equipment.weapon],combat.player.equipmentMeta?.weapon),type=item?.rawFields[30],name=({18:'雷电术',19:'火墙',20:'冰咆哮'})[type];
 if(!name||!target?.alive)return false;
 const cost=combat.player.class==='法师'?0:type===18?5:16;
 if(combat.player.mp<cost)return false;combat.player.mp-=cost;
 releaseHeroSkill(combat,{name,mpCost:0,attached:true},target);return true;
}
export function releaseHeroSkill(combat,skill,target){
 const swordAction=PASSIVE_SKILLS.has(skill.name)||['半月斩','烈火斩','冰封斩'].includes(skill.name);
 if(!skill.attached&&(!swordAction||target?.alive))recordWeaponUse(combat.player,combat.content);
 const {name}=skill,level=skillLevel(combat.player,name),stats=attributes(combat.player,combat.content),properties=combat.playerProperties||combatProperties(combat.player,combat.content),roll=k=>offenseRoll(stats,k,combat.battleRandom),enemies=()=>combat.units.filter(u=>u.alive&&!u.summoned);
 if(SUMMON_SKILLS.has(name)){const unit=summon(combat,name);if(!unit){combat.player.mp+=skill.mpCost;return;}addVisual(combat,name==='召唤骷髅'?12:13,unit,{duration:name==='召唤骷髅'?1.2:2.04,follow:unit});return;}
 if(name==='回生术'){queueHealing(combat.player,roll('tao')/8+8*level+5);addVisual(combat,7,combat.position,{duration:1.2,follow:combat.position});return;}
 if(name==='治愈术'){const amount=nativeRound(roll('tao')/3+30*level);queueHealing(combat.player,amount);addVisual(combat,8,combat.position,{duration:1.2,follow:combat.position});for(const u of combat.units.filter(u=>u.alive&&followingPet(u)&&Math.max(Math.abs(Math.round(u.x)-Math.round(combat.position.x)),Math.abs(Math.round(u.y)-Math.round(combat.position.y)))<=1)){queueHealing(u,amount);addVisual(combat,8,u,{duration:1.2,follow:u});}return;}
 if(name==='隐身术'){combat.player.invisible=true;combat.player.invisibleFrames=(stats.tao[1]+400)*level+100;addVisual(combat,9,combat.position,{duration:1.2,follow:combat.position});for(const u of enemies())clearMonsterAggro(u);return;}
 if(name==='魔法盾'){startMagicShield(combat,5*(roll('magic')+80*level));return;}
 if(name==='炼尸咒'){
  if(!target||target.alive||target.refined)return;target.refined=true;addVisual(combat,91,target,{duration:1.2});
  if(sampleMonsterRandom(combat.battleRandom)*100>=15*(level+1))return;
  const max=target.definition.hp,potions=max<=100?['金创药小','魔法药小']:max<=200?['金创药中','魔法药中']:max<=500?['金创药大','魔法药大']:max<=1000?['强效金创药','强效魔法药']:['绝强金创药','绝强魔法药'],itemName=potions[sampleMonsterRandom(combat.battleRandom)*100<60?0:1],item=combat.content.itemNames.get(itemName);
  const offsets=[[0,0],[1,0],[-1,0],[0,1],[0,-1]],point=offsets.map(([dx,dy])=>({x:Math.round(target.x)+dx,y:Math.round(target.y)+dy})).find(p=>combat.walkable(p.x,p.y)&&combat.findPath(p,0)!==null);
  if(item&&point){combat.groundItems.push({id:combat.map.id+':loot:'+(++combat.nextDropId),...point,kind:'item',itemId:item.id,quantity:1});combat.lootVersion++;combat.autoLoot=true;combat.lootAfter=combat.elapsed+combat.position.actionTime;}return;
 }
 if(name==='地狱雷光'){
  const point={...combat.position};
  addVisual(combat,90,point,{duration:.56,clipFrames:7,hitAt:.24,onHit:()=>{
   for(const u of enemies().filter(u=>{const dx=Math.abs(Math.round(u.x)-Math.round(point.x)),dy=Math.abs(Math.round(u.y)-Math.round(point.y));return dx<=2&&dy<=2&&dx+dy<4&&combat.lineOfSight(point,u);})){const power=nativeRound(roll('magic')/2.5+6*level+(combat.player.class==='道士'?roll('tao')/4:0));combat.heroHit(u,power,{magic:true,status:sampleMonsterRandom(combat.battleRandom)*100<2*level?'paralysis':null});}
  }});return;
 }
 if(!target?.alive)return;
 if(name==='雷电术'){addVisual(combat,18,target,{duration:.4,clipFrames:4,variant:level>=5?'lightningWide':null,follow:target,hitAt:.3,onHit:()=>{if(target.alive)combat.heroHit(target,roll('magic')+5*level+3,{magic:true,status:sampleMonsterRandom(combat.battleRandom)*100<(level<3?2:level<5?3.5:5.5)?'paralysis':equipmentStatus(properties,combat.battleRandom,{monster:true})});},onComplete:e=>lightningAftershock(combat,e,level,level-1)});return;}
 if(name==='冰咆哮'){
  const point={x:Math.round(target.x),y:Math.round(target.y)};
  addVisual(combat,20,point,{duration:1.36,hitAt:.4,onHit:()=>{
   for(const u of enemies().filter(u=>Math.max(Math.abs(Math.round(u.x)-point.x),Math.abs(Math.round(u.y)-point.y))<=1))combat.heroHit(u,nativeRound(roll('magic')+5*level+(combat.player.class==='道士'?roll('tao')/4:0)),{magic:true,status:sampleMonsterRandom(combat.battleRandom)*100<8*level+5?'freeze':null});
  }});return;
 }
 if(name==='火墙'){combat.audio?.hero('放置火墙',combat.position);const point={x:Math.round(target.x),y:Math.round(target.y)};for(const [dx,dy]of [[0,0],[-1,0],[1,0],[0,-1],[0,1]])if(combat.walkable(point.x+dx,point.y+dy))firewall(combat,{x:point.x+dx,y:point.y+dy},level);return;}
 if(name==='诱惑之光'){
  addVisual(combat,22,target,{duration:1.2});combat.provoke(target);
  if(target.definition.attackKind!==0||target.definition.hp>=60*level||combat.units.filter(u=>u.alive&&followingPet(u)).length>=3||nativeRound(sampleMonsterRandom(combat.battleRandom)*100)>=10*level)return;
  if(nativeRound(sampleMonsterRandom(combat.battleRandom)*(100+8*level))<target.hp/target.definition.hp*100){if(nativeRound(sampleMonsterRandom(combat.battleRandom)*10)<4)combat.kill(target,{reward:false});return;}
  const d=target.definition={...target.definition};for(const k of ['hp','attack','defense','magicDefense'])d[k]=Math.max(1,nativeRound(d[k]/2));d.regenFrames=100;d.speed=1.8;d.behavior=6;
  for(let i=2;i<=level;i++){d.hp=nativeRound(d.hp*1.1)+10*level;d.attack+=level<=5?1:level<=8?2:3;d.defense+=level<=5?1:level<=8?2:3;d.magicDefense+=level<=8?1:2;d.regenFrames=50;}
  Object.assign(target,{hp:d.hp,summoned:true,summonSkill:name,petLevel:Math.min(10,level),petKills:0,originId:target.id,temporary:true,roamGoal:null,roamFrom:null});resetMonsterAI(target);target.statuses={};combat.threats?.delete(target.id);if(combat.targetId===target.id){combat.targetId=null;combat.path=[];}return;
 }
 if(FLIGHT_SKILLS[name]){
  launchProjectile(combat,{from:combat.position,to:target,type:FLIGHT_SKILLS[name],onHit:hit=>{
   const victims=['爆裂火球','强冰术'].includes(name)?enemies().filter(u=>Math.abs(Math.round(u.x)-Math.round(hit.x))+Math.abs(Math.round(u.y)-Math.round(hit.y))<=1):[hit];
   for(const u of victims){if(!u.alive)continue;const hitStats=attributes(combat.player,combat.content),value=offenseRoll(hitStats,name==='灵魂火符'?'tao':'magic',combat.battleRandom),power=name==='灵魂火符'?nativeRound(value*.9+3*(level-1)):spellPower(name,level,value);let status=null;
    if(['火球术','爆裂火球'].includes(name)&&sampleMonsterRandom(combat.battleRandom)*100<level+(name==='火球术'?7:9))status='burn';
    if(['御冰术','强冰术'].includes(name)&&sampleMonsterRandom(combat.battleRandom)*100<(name==='御冰术'?2*level+7:level+9))status='freeze';
    if(name==='灵魂火符')status=equipmentStatus(properties,combat.battleRandom,{monster:true});
    combat.heroHit(u,power,{magic:true,status});
   }
  }});return;
 }
 if(name==='施毒术'||name==='侵蚀术'){
  const poison=name==='施毒术',frames=10*(roll('tao')+level*(poison?30:10)),power=nativeRound(roll('tao')/10+level*(poison?2:4)+(poison?0:1));
  applyStatus(target,poison?'poison':'corrosion',{power,frames,source:'player'});combat.provoke(target);addVisual(combat,poison?10:11,target);return;
 }
 const power=skill.attackPower??roll('attack');
 if(['基本剑术','剑气斩','火龙斩','自然之力'].includes(name))releaseWeaponSkill(combat,target);
 if(name==='冰封斩'){
  const face=combat.direction(combat.position,target);
  for(const u of enemies().filter(u=>combat.canAttackFrom(combat.position,u)&&Math.min((combat.direction(combat.position,u)-face+8)%8,(face-combat.direction(combat.position,u)+8)%8)<=1))combat.heroHit(u,nativeRound(roll('attack')+power*.1*level+level),{status:sampleMonsterRandom(combat.battleRandom)*100<13*level?'freeze':null});return;
 }
 if(name==='半月斩'){
  combat.audio?.hero('半月',combat.position);const face=combat.direction(combat.position,target);
  for(const u of enemies().filter(u=>combat.canAttackFrom(combat.position,u)&&Math.min((combat.direction(combat.position,u)-face+8)%8,(face-combat.direction(combat.position,u)+8)%8)<=1))combat.heroHit(u,u===target?nativeRound(power+roll('attack')*(level-1)*.1+level):nativeRound(roll('attack')*.7+power*(level-1)*.06+level));
  return;
 }
 if(name==='烈火斩'){
  combat.audio?.hero('烈火',combat.position);const direction=combat.direction(combat.position,target);
  for(const u of enemies().filter(u=>Math.max(Math.abs(u.x-combat.position.x),Math.abs(u.y-combat.position.y))<=6&&combat.direction(combat.position,u)===direction&&combat.lineOfSight(combat.position,u))){
   combat.heroHit(u,nativeRound(stats.attack[1]+power*level*.1),{status:sampleMonsterRandom(combat.battleRandom)*100<level*10?'burn':null});
  }return;
 }
 // Sword energy and fire dragon are learned passive procs, never repeat casts.
 const energy=skillLevel(combat.player,'剑气斩'),dragon=skillLevel(combat.player,'火龙斩'),direction=combat.direction(combat.position,target);
 if(skill.proc==='energy'||skill.proc===undefined&&energy&&sampleMonsterRandom(combat.battleRandom)*100<8*energy){combat.audio?.hero('剑气斩',combat.position);if(skill.proc===undefined)addVisual(combat,2,combat.position,{direction,duration:.72});for(const u of enemies().filter(u=>Math.max(Math.abs(u.x-combat.position.x),Math.abs(u.y-combat.position.y))<=2&&combat.direction(combat.position,u)===direction&&combat.lineOfSight(combat.position,u)))combat.heroHit(u,power+3*energy,{ignoreDefense:true});return;}
 if(skill.proc==='dragon'||skill.proc===undefined&&dragon&&sampleMonsterRandom(combat.battleRandom)*100<(dragon===1?2:4*dragon)){addVisual(combat,72,combat.position,{direction,duration:.32});combat.heroHit(target,nativeRound(stats.attack[1]*(1+.1*dragon)));return;}
 combat.heroHit(target,power,{melee:true});
}
export function beginHeroSkill(combat,skill,target){
 if(!skill||!combat.attackReady()||combat.player.mp<skill.mpCost||SUMMON_SKILLS.has(skill.name)&&!canSummon(combat,skill.name))return false;
 if(!['隐身术','回生术','治愈术','魔法盾',...SUMMON_SKILLS].includes(skill.name)){combat.player.invisible=false;combat.player.invisibleFrames=0;}
 const range=attackRange(combat,skill);combat.hitClock=0;combat.player.mp-=skill.mpCost;combat.position.skill=skill.name;if(target)combat.position.direction=combat.direction(combat.position,target);setAction(combat.position,skill.action,{restart:true});
 const properties=combatProperties(combat.player,combat.content),fast=skill.action==='attack'?properties.fastAttack:properties.fastCast;
 combat.attackPeriod=(8-Math.min(5,fast))*6/50;combat.position.animationDuration=combat.attackPeriod;combat.position.actionTime=combat.attackPeriod;
 if(skill.action==='attack'){
  skill={...skill};const stats=attributes(combat.player,combat.content);skill.attackPower=offenseRoll(stats,'attack',combat.battleRandom);
  let type=({'半月斩':3,'烈火斩':4,'冰封斩':5})[skill.name]||1;
  if(!['半月斩','烈火斩','冰封斩'].includes(skill.name)){
   const energy=skillLevel(combat.player,'剑气斩'),dragon=skillLevel(combat.player,'火龙斩');skill.proc=energy&&sampleMonsterRandom(combat.battleRandom)*100<8*energy?'energy':dragon&&sampleMonsterRandom(combat.battleRandom)*100<(dragon===1?2:4*dragon)?'dragon':null;
   if(skill.proc==='energy')type=2;
  }
  addVisual(combat,type,combat.position,{direction:combat.position.direction,duration:combat.position.actionTime,owner:combat.position});
 }
 combat.heroWindup={remaining:releaseTime(combat.position),skill,targetId:target?.id,range,animationVersion:combat.position.animationVersion};return true;
}
