import {skillLevel} from './native-damage.js';
import {nativeRound} from './monster-motion.js';

// 5d1811..5d1a42: (next level)*25 kills; no XP from a pet death.
// The generic pet branch reads the player's temptation rank, including NPC pets.
export function petKill(combat,pet){
 if(!pet?.alive||!pet.summoned||pet.defenseFlag||(pet.petLevel||1)>=10)return false;
 pet.petKills=(pet.petKills||0)+1;const level=(pet.petLevel||1)+1;if(pet.petKills<level*25)return false;
 pet.petKills=0;pet.petLevel=level;const d=pet.definition={...pet.definition},skill=skillLevel(combat.player,pet.summonSkill==='江湖召唤'?'诱惑之光':pet.summonSkill);
 d.hp=nativeRound(d.hp*1.1);if(pet.mercenary)d.attack++;
 if(pet.summonSkill==='召唤骷髅'){
  const a=level<=4?2:level<=8?3:5;d.attack+=a;d.defense+=level<=4?2:level<=8?4:6;d.magicDefense+=a;d.hp+=20*skill;d.regenFrames-=2;if(level>=5)d.appearance=200;
 }else if(pet.summonSkill==='召唤神兽'){
  const a=level<=4?2:level<=8?4:6;d.attack+=a;d.defense+=level<=4?3:level<=8?5:8;d.magicDefense+=a;d.hp+=40*skill;d.regenFrames-=2;if(level>=5)d.appearance=174;
 }else{
  const a=level<=5?2:level<=8?3:4;d.attack+=a;d.defense+=level<=5?2:level<=8?4:6;d.magicDefense+=a;d.hp+=10*skill;d.regenFrames=level<=5?100:level<=8?70:50;
 }
 d.regenFrames=Math.max(10,d.regenFrames);pet.hp=d.hp;pet.healingPool=0;
 combat.events.push({x:pet.x,y:pet.y,text:'Lv.'+level,color:'#b1e8e1',until:combat.elapsed+1.5});return true;
}
