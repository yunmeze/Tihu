import {applyNpcEffects} from './npc-dialogue.js';
import {spawnUnit} from './monster-spawning.js';
import {resetMonsterMotion} from './monster-motion.js';
import {resetMonsterAI} from './monster-ai.js';
import {planScriptServices,applyScriptServices} from './script-services.js';
import {CHALLENGE_RULES} from './challenges.js';

const inside=(map,x,y)=>Number.isInteger(x)&&Number.isInteger(y)&&x>=0&&y>=0&&x<map.width&&y<map.height;
export function restoreScriptWorld(map,state){
 for(const [index,entry]of Object.entries(state?.npcs||{})){const npc=map.npcs[index];if(!npc)continue;if(entry.removed)npc.removed=true;if(inside(map,entry.x,entry.y)){npc.x=entry.x;npc.y=entry.y;}}
 for(const row of state?.objects||[]){const [x,y,type,index]=row;if(inside(map,x,y)&&[0,1,2,3,4,5,8].includes(type)&&Number.isInteger(index)&&index>=0){map.cells[x*map.height+y][2]=type;map.cells[x*map.height+y][3]=index;}}
}
export function executeScriptView(combat,view,stateByMap={},flagsByMap={},destination=null){
 const {map,player,content}=combat;if(view.unsupported.length)return false;
 const services=planScriptServices(combat,view.worldEffects);if(!services)return false;if(services.some(e=>e.kind==='gameover')&&(view.move||view.worldEffects.some(e=>!['gameover','unstop'].includes(e.kind))))return false;
 for(const e of services.filter(e=>e.kind==='challenge')){const r=CHALLENGE_RULES[e.mode];if(view.move?.id!==r.map||view.move.x!==r.entry[0]||view.move.y!==r.entry[1])return false;}
 // Native SETMAPFLAG: 0 clears, 1 blocks invisibly, 2 adds a visible pillar.
 if(view.mapFlags.some(([x,y,flag])=>!inside(map,x,y)||![0,1,2].includes(flag)))return false;
 let available=600-combat.units.filter(u=>u.alive||!u.temporary).length-services.filter(e=>['addfriendhero','addfriendheron','addmonhero'].includes(e.kind)).length;
 for(const e of view.worldEffects){
  if(['reme','repet','stop','unstop','addfriendhero','addfriendheron','addmonhero','defstart','defhpup','defdfup','defdmup','defhpadd','challenge','gameover'].includes(e.kind))continue;
  if(e.kind==='delallmon'){available=600-combat.units.filter(u=>u.alive&&u.summoned).length;continue;}
  if(!inside(map,e.x,e.y))return false;
  if(e.kind==='movenpc'&&!inside(map,e.toX,e.toY))return false;
  if(e.kind==='setmapdata'&&(![0,1,2,3,4,5,8].includes(e.type)||!Number.isInteger(e.index)||e.index<0))return false;
  if(e.kind==='addmon'&&(!combat.monsterNames.has(e.name)||--available<0))return false;
 }
 if(view.move&&(!destination||destination.id!==view.move.id||!inside(destination,view.move.x,view.move.y)))return false;
 if(!applyNpcEffects(player,view.effects,content))return false;
 applyScriptServices(combat,services);
 for(const drop of player.pendingGroundItems||[]){const feet={x:Math.round(combat.position.x),y:Math.round(combat.position.y)};combat.groundItems.push({...drop,...feet,id:map.id+':loot:'+(++combat.nextDropId)});combat.lootVersion++;}delete player.pendingGroundItems;
 const state=stateByMap[map.id]||={npcs:{},objects:[]};state.npcs||={};state.objects||=[];
 const setObject=(x,y,type,index)=>{const cell=map.cells[x*map.height+y];cell[2]=type;cell[3]=index;const old=state.objects.find(p=>p[0]===x&&p[1]===y);if(old){old[2]=type;old[3]=index;}else state.objects.push([x,y,type,index]);};
 const flags=flagsByMap[map.id]||=[];
 for(const [x,y,flag]of view.mapFlags){const cell=map.cells[x*map.height+y];if(flag&&cell[1]!==0)continue;const stored=flag?-1:0;cell[1]=stored;if(flag===2)setObject(x,y,8,1);else if(!flag&&cell[2]===8)setObject(x,y,0,0);const old=flags.find(p=>p[0]===x&&p[1]===y);if(old)old[2]=stored;else flags.push([x,y,stored]);}
 const remove=u=>{u.removed=true;u.refined=true;u.alive=false;u.temporary=true;u.diedAt=combat.elapsed;u.respawnAt=Infinity;u.roamGoal=null;u.roamFrom=null;combat.threats?.delete(u.id);if(combat.targetId===u.id){combat.targetId=null;combat.path=[];}};
 for(const e of view.worldEffects){
  if(['reme','repet','stop','unstop','addfriendhero','addfriendheron','addmonhero','defstart','defhpup','defdfup','defdmup','defhpadd','challenge','gameover'].includes(e.kind))continue;
  if(e.kind==='setmapdata')setObject(e.x,e.y,e.type,e.index);
  else if(e.kind==='delallmon'){for(const u of combat.units)if(!u.summoned)remove(u);}
  else if(e.kind==='addmon')spawnUnit(combat,combat.monsterNames.get(e.name),{x:e.x,y:e.y},{scripted:true});
  else {
   const matches=map.npcs.map((npc,index)=>({npc,index})).filter(({npc})=>!npc.removed&&npc.x===e.x&&npc.y===e.y);
   for(const {npc,index}of matches){if(e.kind==='delnpc'){npc.removed=true;state.npcs[index]={...state.npcs[index],removed:true};}else{npc.x=e.toX;npc.y=e.toY;state.npcs[index]={...state.npcs[index],x:e.toX,y:e.toY};}}
   for(const u of combat.units.filter(u=>!u.removed&&Math.round(u.x)===e.x&&Math.round(u.y)===e.y)){if(e.kind==='delnpc')remove(u);else{resetMonsterMotion(u);resetMonsterAI(u);Object.assign(u,{x:e.toX,y:e.toY,roamHome:{x:e.toX,y:e.toY}});}}
  }
 }
 return true;
}
