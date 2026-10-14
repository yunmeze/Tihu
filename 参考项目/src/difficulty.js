import {nativeRound} from './monster-motion.js';
export const DIFFICULTIES=['普通模式','专家模式','地狱模式'];
// Enemy initializer 5a1916..5a1c86. Friendly actors (+34 != 0) bypass both
// difficulty and cleared-cycle scaling. Apply to fresh definitions only.
export function difficultyMonster(base,player,friendly=false){
 if(friendly||!base)return base;const mode=player.gameMode||0,cleared=(player.clearCount||0)>0;if(!mode&&!cleared)return base;
 const d={...base};if(mode===1){d.hp=nativeRound(d.hp*1.3);d.attack=nativeRound(d.attack*1.3+1);d.defense=nativeRound(d.defense*1.2+1);d.magicDefense=nativeRound(d.magicDefense*1.2+1);d.experience=nativeRound(d.experience*1.1+1);}
 if(mode===2){d.hp=nativeRound(d.hp*1.8);d.attack=nativeRound(d.attack*1.5+2);d.defense=nativeRound(d.defense*1.4+2);d.magicDefense=nativeRound(d.magicDefense*1.4+2);d.experience=nativeRound(d.experience*1.2+5);}
 if(cleared){if(d.hp<100)d.hp=nativeRound(d.hp/2+100);else if(d.hp<200)d.hp=nativeRound(d.hp/2+200);else if(d.hp<300)d.hp=nativeRound(d.hp*1.5);d.attack=Math.max(d.attack,d.attackKind===0?40:35);}return d;
}
export function availableCharacterModes(roster){return roster.hellUnlocked?[0,1,2]:[0,1];}
