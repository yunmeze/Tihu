import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {combatText} from './combat-text.js';
import {emitNativeParticle} from './native-particles.js';

// Native GH=2: 5c40b2..5c4320. This is an aggro aura, not poison or
// reflected attack damage. Native HP is clamped to one; it cannot kill.
export const DARK_AURA={kind:2,frames:[67,68,69],enemyFrame:67,period:120,randomScale:4,minimumHp:1,rotationPerTick:.01,scaleX:.7,scaleY:.5};
export function normalizeAura(player){
 player.aura=player.aura===2?2:0;
 const flags=player.auraUnlocks||[];player.auraUnlocks=Array.from({length:10},(_,i)=>flags[i]===1?1:0);
 return player;
}
export const auraVictim=(combat,unit)=>combat.player.aura===2&&combat.player.hp>0&&unit.alive&&unit.hp>0&&!unit.summoned&&unit.aggro&&unit.aggroUntil>combat.elapsed&&!unit.removed&&!combat.units.some(u=>u.id===unit.targetUnitId&&u.alive&&u.summoned);
export function updateDarkAura(combat){
 if(combat.ruleFrame%40===0)for(const unit of combat.units)if(auraVictim(combat,unit)&&combat.inRange(unit))emitNativeParticle(combat,4,unit);
 if(combat.ruleFrame%DARK_AURA.period)return;
 for(const unit of combat.units){
  if(!auraVictim(combat,unit)||!combat.inRange(unit))continue;
  const rolled=nativeRound(sampleMonsterRandom(combat.battleRandom)*DARK_AURA.randomScale)+1;
  const before=unit.hp;unit.hp=Math.max(DARK_AURA.minimumHp,before-rolled);
  // Display actual loss. The native displays the roll even when clamped.
  if(unit.hp<before)combatText(combat,unit,String(before-unit.hp),{color:'#dc8caa',actorId:unit.id,appearance:unit.definition.appearance,amount:before-unit.hp});
 }
}
export function auraAppearance(tick){
 // Native shared pulse: 0 -> 200 (+1), 200 -> 60 (-2), then repeat.
 const t=Math.max(0,Math.trunc(tick)||0),phase=t<200?t:(t-200)%210;
 const alpha=t<200?t:phase<70?200-2*phase:60+phase-70;
 return {angle:(t*.01)%360,opacity:alpha/255};
}
export function drawAura(app,point,{enemy=false}={}){
 const z=app.worldScale,p=app.mapPoint(point.x,point.y),style=auraAppearance(app.combat.ruleFrame||0),pack=app.packs.get('Data4');
 if(!pack)return;
 for(const frame of enemy?[DARK_AURA.enemyFrame]:DARK_AURA.frames)app.batch.rotatedFrame(pack,frame,p.x+24*z,p.y+16*z,z*.7,z*.5,style.angle,style.opacity);
}
