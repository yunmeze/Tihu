import {NUMERIC_MODEL} from './native-stats.js';
import {nativeRound} from './monster-motion.js';
export const MAX_LEVEL=130;
// 61f63e..61f819: CLng(piecewise cubic + level) + 9; native XP resets on promotion.
export function experienceNeeded(level){level=Math.max(1,Math.min(MAX_LEVEL,Math.trunc(level)||1));return nativeRound(level**3/(level<100?6:level<110?3:2)+level)+9;}
export function experienceProgress(player){const needed=experienceNeeded(player.level),current=Math.max(0,Math.min(needed,Math.trunc(player.experience)||0)),maxLevel=player.level>=MAX_LEVEL;return {current,needed,remaining:maxLevel?0:needed-current,ratio:maxLevel?1:current/needed,maxLevel};}
function promote(player){
 player.level++;player.attributePoints=(player.attributePoints||0)+1;if(player.level%2===0)player.skillPoints=(player.skillPoints||0)+1;
 if(player.base){player.base.hp+=player.class==='战士'?5:player.class==='法师'&&player.level%2===0?1:2;player.base.capacity=(player.base.capacity??(player.class==='战士'?25:player.class==='道士'?22:20))+(player.class==='战士'?3:2);player.base.mp+=player.class==='战士'?2:player.class==='法师'?6:4;
  if(player.level%10===0){if(player.class==='战士'){player.base.defense[1]++;player.base.capacity++;}else player.base.mp+=5;}
  // A late poison/reflect kill or old-save migration can promote a dead hero.
  // Award growth and points without turning that promotion into a revival.
  if(player.hp>0){player.hp=player.base.hp;player.mp=player.base.mp;}
 }
}
export function normalizeProgress(player){
 player.level=Math.max(1,Math.min(MAX_LEVEL,Math.trunc(player.level)||1));player.experience=Math.max(0,Math.trunc(player.experience)||0);
 for(const key of ['skillPoints','attributePoints'])player[key]=Number.isSafeInteger(player[key])&&player[key]>=0?player[key]:0;
 if(player.creationProfile&&player.numericModel!==NUMERIC_MODEL){
  // Migrate the pre-existing levels before replaying legacy accumulated XP,
  // so native promotions are not corrected a second time.
  player.numericMigrationBaseline={level:player.level,base:JSON.parse(JSON.stringify(player.base)),skillPoints:player.skillPoints,attributePoints:player.attributePoints};
  const oddPromotions=Math.ceil((player.level-1)/2);player.attributePoints+=oddPromotions+1;player.base.defense[1]=Math.max(player.base.defense[0],player.base.defense[1]-1);player.skillPoints=Math.max(0,player.skillPoints-oddPromotions);
  if(player.class==='法师')player.base.hp+=Math.floor((player.level-1)/2);
  player.base.capacity=(player.base.capacity||0)+(player.class==='战士'?25:player.class==='道士'?22:20)+(player.level-1)*(player.class==='战士'?3:2)+(player.class==='战士'?Math.floor(player.level/10):0);
  player.numericModel=NUMERIC_MODEL;
 }
 if(player.experienceModel!=='native-level-v1'){
  // Older web saves accumulated XP without promotions. Preserve it during this one-time migration.
  while(player.level<MAX_LEVEL&&player.experience>=experienceNeeded(player.level)){player.experience-=experienceNeeded(player.level);promote(player);}
  player.experienceModel='native-level-v1';
 }
 player.experience=Math.min(player.experience,experienceNeeded(player.level));
return player;
}
export function gainExperience(player,amount){normalizeProgress(player);player.experience+=Math.max(0,Math.trunc(amount)||0);if(player.experience<experienceNeeded(player.level))return false;if(player.level>=MAX_LEVEL){player.experience=experienceNeeded(player.level);return false;}player.experience=0;promote(player);return true;}
