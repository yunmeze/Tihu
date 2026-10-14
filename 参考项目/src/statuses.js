import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {emitNativeParticle} from './native-particles.js';
export const STATUS_RULES={fps:50,freezeFrames:500,burnFrames:500,poisonFrames:1000,paralysisMonsterFrames:250,paralysisPlayerFrames:150,corrosionFrames:400,dotFrames:100};
export function resetStatuses(actor){actor.statuses={};actor.statusRemainder=0;}
export const isParalyzed=actor=>(actor.statuses?.paralysis?.frames||0)>0;
export const isFrozen=actor=>(actor.statuses?.freeze?.frames||0)>0;
export function statusTint(actor){const s=actor.statuses||{},rgba=actor.definition?.color,base=rgba?'#'+rgba.slice(0,3).map(n=>Math.max(0,Math.min(255,n)).toString(16).padStart(2,'0')).join(''):'#ffffff';return s.corrosion?'#ffff64':s.poison?'#64ff64':s.burn?'#ff6464':s.freeze?'#6464ff':base;}
export function actorOpacity(actor){return Math.max(0,Math.min(1,(actor.definition?.color?.[3]??255)/255));}
export function applyStatus(actor,name,{power=1,frames,source='player',player=false}={}){
 actor.statuses||={};const s=actor.statuses;
 if(name==='freeze')delete s.burn;
 if(name==='burn')delete s.freeze;
 if(name==='paralysis'&&s.paralysis)return;
 frames??=name==='paralysis'?(player?150:250):STATUS_RULES[name+'Frames'];
 if(!frames||power<=0)return;
 s[name]={frames,power:Math.max(power,s[name]?.power||0),source};
}
export const effectiveDefense=(unit,magic=false)=>Math.max(0,(magic?unit.definition.magicDefense:unit.definition.defense)-(unit.statuses?.corrosion?.power||0));
export function updateStatuses(combat,actor,dt,{player=false}={}){
 if(actor.hp<=0)return;
 actor.statusRemainder=(actor.statusRemainder||0)+dt*50;
 const ticks=Math.floor(actor.statusRemainder+1e-8);actor.statusRemainder-=ticks;
 for(let i=0;i<ticks&&actor.hp>0;i++)for(const [name,status]of Object.entries(actor.statuses||{})){
  // Native unit +b2/+ae/+a6 emits at remaining-status ticks divisible by 30,
  // before decrement. Visual randomness never consumes a battle damage roll.
  if(!player&&status.frames%30===0){const type={freeze:0,burn:1,poison:2}[name];if(type!==undefined)emitNativeParticle(combat,type,actor);}
  if((name==='poison'||name==='burn')&&status.frames%100===0){
   // The native player has a separate 1..6 roll, reduced by the matching item attribute.
   const power=player?Math.max(1,nativeRound(sampleMonsterRandom(combat.battleRandom)*5+1-(combat.playerProperties?.[name]||0))):nativeRound(sampleMonsterRandom(combat.battleRandom)*status.power)+1;
   combat.hurt(actor,power,{player,source:status.source,color:name==='poison'?'#91dc73':'#ef9667'});
  }
  if(--status.frames<=0)delete actor.statuses[name];
 }
}
