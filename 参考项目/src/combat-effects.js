import {followingPet} from './allies.js';
import {updateNativeParticles} from './native-particles.js';
import {emitAmbientParticles} from './ambient-particles.js';
import {emitGroundParticles} from './ground-particles.js';
import {updateMonsterRebirth} from './monster-rebirth.js';
import {skillLevel,nativeRoll,offenseRoll} from './native-damage.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {attributes} from './character.js';
import {addVisual} from './projectiles.js';
import {applyStatus} from './statuses.js';
import {updateDarkAura} from './dark-aura.js';
import {advanceMagicShield} from './magic-shield.js';

export const onCell=(a,b)=>Math.round(a.x)===Math.round(b.x)&&Math.round(a.y)===Math.round(b.y);
export function addZone(combat,{point,type,frames,source='player',startFrame=0,hitFrame,hit}){
 const existing=combat.zones.find(z=>z.type===type&&z.source===source&&onCell(z,point));
 if(existing&&[19,40].includes(type)){existing.frames=frames;existing.visual.duration=existing.visual.age+frames/50;return existing;}
 const zone={x:Math.round(point.x),y:Math.round(point.y),type,source,frames,frame:startFrame,hitFrame,hit,visual:addVisual(combat,type,point,{duration:frames/50,loop:[19,40].includes(type)})};
 if(zone.visual.loop)zone.visual.frameSeconds=.12;combat.zones.push(zone);return zone;
}
export function updateCombatEffects(combat,dt){
 combat.ruleRemainder=(combat.ruleRemainder||0)+dt*50;const ticks=Math.floor(combat.ruleRemainder+1e-8);combat.ruleRemainder-=ticks;
 const p=combat.player;
 for(let i=0;i<ticks;i++){
  combat.ruleFrame=(combat.ruleFrame||0)+1;
  for(const u of combat.units)updateMonsterRebirth(u);
  emitAmbientParticles(combat);
  emitGroundParticles(combat);
  updateDarkAura(combat);
  updateNativeParticles(combat);
  advanceMagicShield(combat);
  if(p.hp>0){
   if(p.invisibleFrames>0&&--p.invisibleFrames===0)p.invisible=false;
   const natural=skillLevel(p,'自然之力'),period=p.class==='道士'&&natural?Math.max(10,250-40*natural):300;
   if(combat.ruleFrame%period===0){p.hp=Math.min(p.base.hp,p.hp+1);p.mp=Math.min(p.base.mp,p.mp+2);}
   if(p.mpRecoveryPool>0&&combat.ruleFrame%4===0){p.mpRecoveryPool--;p.mp=Math.min(p.base.mp,p.mp+1);if(p.mp===p.base.mp)p.mpRecoveryPool=0;}
   const healingRing=p.inventory.some(e=>(e.name||combat.content.items[e.itemId]?.name)==='回阳珠');
   if(p.healingPool>0&&healingRing&&combat.ruleFrame%4===0){p.healingPool--;p.hp=Math.min(p.base.hp,p.hp+1);if(p.hp===p.base.hp)p.healingPool=0;}
   if(p.healingPool>0&&combat.ruleFrame%(p.class==='道士'?5:3)===0){p.healingPool--;p.hp=Math.min(p.base.hp,p.hp+1);if(p.hp===p.base.hp)p.healingPool=0;}
  }
  for(const u of combat.units)if(u.alive&&followingPet(u)&&u.healingPool>0&&combat.ruleFrame%3===0){u.healingPool--;u.hp=Math.min(u.definition.hp,u.hp+1);if(u.hp===u.definition.hp)u.healingPool=0;}
  for(const z of combat.zones){
   const owner=z.source==='player'?p:combat.units.find(u=>u.id===z.source);
   if(!owner||owner.hp<=0){z.frames=0;z.visual.duration=z.visual.age;continue;}
   if(z.hitFrame!==undefined?z.frame===z.hitFrame:[19,40].includes(z.type)&&Math.floor(z.frame/6)%2===1){
    const targets=z.source==='player'||owner.summoned?combat.units.filter(u=>u.alive&&!u.summoned):[{...combat.position,id:'player',hp:p.hp},...combat.units.filter(u=>u.alive&&u.summoned)];
    for(const t of targets)if(t.hp>0&&onCell(t,z))z.hit(t);
   }
   z.frame++;z.frames--;
  }
  combat.zones=combat.zones.filter(z=>z.frames>0);
 }
 // The shell follows its owner; the original Mgc/17 supplies the animation.
 if(p.magicShieldFrames>0&&p.hp>0){let shell=combat.effects.find(e=>e.shield);if(!shell){shell=addVisual(combat,21,combat.position,{duration:p.magicShieldFrames/50+1,loop:true});shell.shield=true;}shell.x=combat.position.x;shell.y=combat.position.y;shell.duration=shell.age+p.magicShieldFrames/50+1;shell.shieldFrame=combat.magicShieldState?.frame||1;}
 else for(const e of combat.effects)if(e.shield)e.duration=e.age;
}
export function firewall(combat,point,level,{source='player',type=19,frames}={}){
 const stats=attributes(combat.player,combat.content);
 return addZone(combat,{point,type,source,frames:frames??300*level+8*stats.magic[1],hit:t=>{
  if(source==='player')combat.heroHit(t,nativeRound(offenseRoll(attributes(combat.player,combat.content),'magic',combat.battleRandom)/3+2*level),{magic:true,continuous:true,status:sampleMonsterRandom(combat.battleRandom)*100<5*(level+1)?'burn':null});
  else {const u=combat.units.find(u=>u.id===source);if(u)combat.enemyHit(u,t.id==='player'?null:t,{magic:true,continuous:true});}
 }});
}
export function queueHealing(actor,amount){actor.healingPool=(actor.healingPool||0)+Math.max(0,nativeRound(amount));}
