import {nativeRound} from './monster-motion.js';
import {emitNativeParticle} from './native-particles.js';
import {difficultyMonster} from './difficulty.js';

const rebirthDefinition=d=>({...d,speed:d.speed+.2,attack:d.attack-15,defense:d.defense+10,magicDefense:d.magicDefense+5,vision:5,attackKind:22});
// Rebuild both the current phase and the next spawn from the new difficulty.
// Keep HP/recovery percentages and action clocks; changing mode is not a heal.
export function setMonsterDifficulty(u,base,player){
 if(!base||u.summoned||u.mercenary||u.defenseFlag)return false;
 const max=u.definition.hp,ratio=max>0?u.hp/max:0,recovery=max>0?(u.rebirthRecovery||0)/max:0,d=difficultyMonster(base,player);
 if(u.reborn){u.birthDefinition=d;u.definition=rebirthDefinition(d);if(u.rebirthRecovery!==undefined)u.rebirthRecovery=Math.max(0,nativeRound(d.hp*recovery));}
 else u.definition=d;
 u.hp=u.alive?Math.min(d.hp,Math.max(1,nativeRound(d.hp*ratio))):0;return true;
}

// 5c91b3..5c930e: exact name, once per spawn, before the death/reward branch.
export function tryMonsterRebirth(c,u){
 if(!u.alive||u.hp>0||u.removed||u.refined||u.reborn||u.definition.name!=='明阳守卫')return false;
 const d=u.definition;u.birthDefinition=d;u.reborn=true;
 u.definition=rebirthDefinition(d);
 u.hp=nativeRound(d.hp*.3);u.rebirthRecovery=nativeRound(d.hp*.7);
 // Preserve the native original max HP for rage thresholds and existing DOTs.
 emitNativeParticle(c,7,u);c.audio?.hero('复活',u);
 c.artRevision=(c.artRevision||0)+1;return true;
}
export function resetMonsterRebirth(u){
 if(u.birthDefinition)u.definition=u.birthDefinition;
 delete u.birthDefinition;delete u.rebirthRecovery;u.reborn=false;
}
// +84 is a restoration pool: 5c8568..5c859b consumes three HP each 50Hz tick.
export function updateMonsterRebirth(u){
 if(!u.alive||u.hp<=0||!(u.rebirthRecovery>0))return;
 u.rebirthRecovery=Math.max(0,u.rebirthRecovery-3);
 u.hp=Math.min(u.definition.hp,u.hp+3);
 if(u.hp===u.definition.hp)u.rebirthRecovery=0;
}
