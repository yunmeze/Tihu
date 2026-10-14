import {nativeAttributes} from './native-stats.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';

// Native sources and boundaries: reports/native-combat-source.json.
export const nativeRoll=(range,random=Math.random)=>nativeRound(range[0]+sampleMonsterRandom(random)*(range[1]-range[0]));
export const skillLevel=(player,name)=>player.skills?.find(s=>s.name===name)?.level||0;
export const combatProperties=(player,content)=>{const stats=nativeAttributes(player,content);return {...stats,accuracy:stats.accuracy-(player.base.accuracy||0)};};
// 624eb0/624fa0/625090 add computed equipment-set bonus to each offensive roll.
export const offenseRoll=(stats,key,random=Math.random)=>nativeRound(stats[key][0]+sampleMonsterRandom(random)*(stats[key][1]-stats[key][0])+(stats.setBonus||0));
export function damageAfterDefense(attack,defense){return Math.max(1,nativeRound(attack)-nativeRound(defense));}
export function rollEvade(rating,multiplier,random){return sampleMonsterRandom(random)*100<rating*multiplier;}
// 61cd72..61cdd6, default player rating 7 at 59328f; unit 94 = DB physical evade.
export function swordMiss(player,unit,properties,random){return sampleMonsterRandom(random)*100>8*(skillLevel(player,'基本剑术')+(player.base.accuracy??7)+(properties.accuracy||0)-unit.definition.physicalEvade);}
export function equipmentStatus(properties,random,{monster=false}={}){
 const order=monster?['freeze','burn','poison','paralysis']:['paralysis','freeze','burn','poison'];
 for(const name of order)if(sampleMonsterRandom(random)*100<properties[name]*(name==='paralysis'?2.8:5))return name;
 return null;
}
// These four spell formulas are traced in 6286e0/6289b0/628dd0/6290a0.
export function spellPower(name,level,magic){
 if(name==='火球术')return nativeRound(magic*.75+2*(level-1)+1);
 if(name==='爆裂火球')return magic+4*level-3;
 if(name==='御冰术')return nativeRound(magic*.7+2*(level-1));
 if(name==='强冰术')return nativeRound(magic*.9+4*(level-1));
 return null;
}
