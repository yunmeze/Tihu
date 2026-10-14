import {followingPet} from './allies.js';
import {difficultyMonster} from './difficulty.js';
import {initializeMonsterMotion,monsterBehavior,monsterWalkable,nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {resetMonsterAI} from './monster-ai.js';
import {resetStatuses} from './statuses.js';
import {nativeRoll,skillLevel} from './native-damage.js';
import {attributes} from './character.js';
export const SPAWN_RULES={fps:50,maxUnits:600,eggRandomFrames:100000,parentFrames:200};
const key=(x,y)=>x+','+y;
export function initializeSpecial(unit,random){unit.specialRemainder=0;unit.specialFrames=0;unit.bossFrames=0;unit.bossRemainder=0;unit.eggFrames=monsterBehavior(unit.definition)===1?nativeRound(sampleMonsterRandom(random)*100000):0;}
export function emptySpawnCell(combat,origin,candidates){
 const occupied=new Set([key(Math.round(combat.position.x),Math.round(combat.position.y)),...(combat.map.npcs||[]).filter(n=>!n.removed).map(n=>key(n.x,n.y))]);
 for(const u of combat.units)if(u.alive){occupied.add(key(Math.round(u.x),Math.round(u.y)));if(u.roamFrom)occupied.add(key(u.roamFrom.x,u.roamFrom.y));if(u.roamGoal)occupied.add(key(u.roamGoal.x,u.roamGoal.y));}
 return candidates.find(p=>monsterWalkable(combat.map,p.x,p.y)&&!occupied.has(key(p.x,p.y))&&(p.x===origin.x||p.y===origin.y||monsterWalkable(combat.map,p.x,origin.y)&&monsterWalkable(combat.map,origin.x,p.y)));
}
export function spawnUnit(combat,definition,point,extra={}){
 if(!point||!definition||combat.units.filter(u=>u.alive||!u.temporary).length>=600)return null;
 definition=difficultyMonster(definition,combat.player,!!(extra.summoned||extra.mercenary||extra.defenseFlag));
 // Reclaim temporary corpses; native pool also reuses released slots.
 for(let i=combat.units.length-1;i>=0;i--)if(combat.units[i].temporary&&!combat.units[i].defenseFlag&&!combat.units[i].alive&&combat.elapsed-combat.units[i].diedAt>2)combat.units.splice(i,1);
 const u={...point,id:combat.map.id+':spawn:'+(++combat.nextSpawnId),name:definition.name,monsterId:definition.id,definition,hp:definition.hp,alive:true,direction:4,action:'idle',actionTime:0,animationElapsed:0,regenClock:0,temporary:true,...extra};
 initializeMonsterMotion(u);resetMonsterAI(u);resetStatuses(u);initializeSpecial(u,combat.battleRandom);combat.units.push(u);return u;
}
export function summonDefinition(combat,name,level){
 const base=combat.monsterNames.get(name);if(!base)return null;
 const d={...base},skeleton=name==='召唤骷髅',tao=()=>nativeRoll(attributes(combat.player,combat.content).tao,combat.battleRandom);
 for(let i=2;i<=level;i++){
  d.hp=nativeRound(d.hp*1.1)+level*(skeleton?20:40);d.attack++;
  const a=i<=4?2:i<=8?(skeleton?3:4):(skeleton?5:6);
  d.attack+=a;d.defense+=i<=4?(skeleton?2:3):i<=8?(skeleton?4:5):(skeleton?6:7);d.magicDefense+=a;d.regenFrames=Math.max(10,d.regenFrames-2);
 }
 d.hp+=tao();d.attack+=nativeRound(tao()/20+level);
 if(level>=5)d.appearance=skeleton?200:174;
 return d;
}
export function summonLimit(combat,name){const level=skillLevel(combat.player,name);return name==='召唤骷髅'?(level>=2?2:1):1;}
export function canSummon(combat,name){return combat.units.filter(u=>u.alive&&followingPet(u)).length<3&&combat.units.filter(u=>u.alive&&u.summonSkill===name).length<summonLimit(combat,name);}
export function summon(combat,name){
 if(!canSummon(combat,name))return null;
 const p={x:Math.round(combat.position.x),y:Math.round(combat.position.y)},offsets=[[-1,0],[1,0],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[1,1]],point=emptySpawnCell(combat,p,offsets.map(([dx,dy])=>({x:p.x+dx,y:p.y+dy})));
 if(!point)return null;
 return spawnUnit(combat,summonDefinition(combat,name,skillLevel(combat.player,name)),point,{summoned:true,summonSkill:name,petLevel:skillLevel(combat.player,name),petKills:0});
}
export function updateSpecialSpawns(combat,dt){
 for(const u of [...combat.units]){
  if(!u.alive||u.summoned)continue;if([27,28].includes(u.definition.attackKind)){u.bossRemainder+=dt*50;const frames=Math.floor(u.bossRemainder+1e-8);u.bossRemainder-=frames;u.bossFrames=Math.min(10000,u.bossFrames+frames);}
  const behavior=monsterBehavior(u.definition);if(![1,-3,-4].includes(behavior))continue;
  if(behavior===1&&u.action!=='idle')continue;
  u.specialRemainder+=dt*50;const ticks=Math.floor(u.specialRemainder+1e-8);u.specialRemainder-=ticks;
  for(let i=0;i<ticks;i++){
   if(behavior===1){
    if(u.eggFrames>0&&--u.eggFrames===0){
     const item=combat.content.itemNames.get('鸡蛋');if(!item)continue;
     const origin={x:Math.round(u.x),y:Math.round(u.y)},offsets=[[1,-1],[0,0],[1,0],[0,-1],[-1,0],[0,1]];
     const point=offsets.map(([dx,dy])=>({x:origin.x+dx,y:origin.y+dy})).find(p=>combat.walkable(p.x,p.y)&&combat.findPath(p,0)!==null);
     if(point){combat.groundItems.push({id:combat.map.id+':loot:'+(++combat.nextDropId),...point,kind:'item',itemId:item.id,quantity:1});combat.lootVersion++;}
    }
   }else if(++u.specialFrames%200===0){
    const roll=sampleMonsterRandom(combat.battleRandom),name=(behavior===-3?['暗月飞蛾','暗月飞蛾-火焰','暗月飞蛾-精英']:['暗月蜘蛛','暗月天狼','暗月黑鄂'])[roll<.6?0:roll<.8?1:2],origin={x:Math.round(u.x),y:Math.round(u.y)},sign=sampleMonsterRandom(combat.battleRandom)<.5?-1:1;
    const point=emptySpawnCell(combat,origin,[{x:origin.x+sign,y:origin.y}]);spawnUnit(combat,combat.monsterNames.get(name),point,{parentId:u.id});
   }
  }
 }
}
