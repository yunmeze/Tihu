import {SPECIAL_BOX_RULES} from './special-box-rules.js';
import {LEGACY_BOX_RULES} from './legacy-box-rules.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {rollEquipmentAffixes} from './equipment-affixes.js';
import {instanceItem} from './native-stats.js';
const waters=new Set(['剧毒水','战神水','仙尊水','天魔水','金刚水','消毒水','消色水']);
const advancedBooks={'高级雷电术':'雷电术','高级魔法盾':'魔法盾'};
export function specialConsumableEffect(item){return item.name==='彩蛋'||item.name==='箱子'||SPECIAL_BOX_RULES[item.name]||advancedBooks[item.name]||waters.has(item.name)?{kind:'special',name:item.name}:null;}
export function specialDescription(name){return advancedBooks[name]?[advancedBooks[name]+'达到5级后学习','提升为6级']:name==='箱子'||SPECIAL_BOX_RULES[name]?['打开后获得原版随机奖励']:name==='彩蛋'?['随机获得恢复效果或物品']:name==='金刚水'?['强化手持盾牌']:['作用于手持武器'];}
// Native use 5e9234..5ea15b, 5ea83c..5ec561 and 5ec63e..5ece5c.
// Stage changes on a player clone. All random outcomes are consumed once.
export function applySpecialConsumable(p,content,name,random=Math.random){
 const rnd=()=>sampleMonsterRandom(random),drops=[],itemDrop=name=>{const item=content.itemNames.get(name);if(!item)throw Error('Missing native reward '+name);drops.push({kind:'item',itemId:item.id,quantity:1,...rollEquipmentAffixes(item,p,random)});};
 const advanced=advancedBooks[name];if(advanced){const skill=p.skills.find(s=>s.name===advanced);if(!skill||skill.level<5)return {ok:false,reason:advanced+'低于5级无法学习'};if(skill.level>5)return {ok:false,reason:'已学习'+name};skill.level=6;return {ok:true,drops};}
 if(name==='箱子'){const roll=nativeRound(rnd()*LEGACY_BOX_RULES.scale),entry=LEGACY_BOX_RULES.ranges.find(e=>roll>=e.min&&roll<=e.max);if(entry?.item==='金币'){if(!Number.isSafeInteger(p.gold+entry.quantity))return {ok:false,reason:'金币数量过多'};p.gold+=entry.quantity;}else if(entry)itemDrop(entry.item);return {ok:true,drops,message:entry?null:'箱子里什么都没有'};}
 const box=SPECIAL_BOX_RULES[name];if(box){const roll=nativeRound(rnd()*box.scale),entry=box.ranges.find(e=>roll>=e.min&&roll<=e.max);if(entry)itemDrop(entry.item);else{const gold=box.gold.add+nativeRound(rnd()*box.gold.scale);if(!Number.isSafeInteger(p.gold+gold))return {ok:false,reason:'金币数量过多'};p.gold+=gold;}return {ok:true,drops};}
 if(name==='彩蛋'){
  const roll=nativeRound(rnd()*600),level=p.level;if(roll<100)p.healingPool=(p.healingPool||0)+nativeRound(level*.2);else if(roll<200)p.mpRecoveryPool=(p.mpRecoveryPool||0)+nativeRound(level*.2);else if(roll<300){p.healingPool=(p.healingPool||0)+nativeRound(level*.3);p.mpRecoveryPool=(p.mpRecoveryPool||0)+nativeRound(level*.3);}
  else if(roll<500){const hp=roll<400,tier=level<50?0:level<100?1:level<200?2:level<500?3:4,names=hp?[['金创药小','金创药小'],['金创药小','金创药中'],['金创药中','金创药大'],['金创药大','强效金创药'],['强效金创药','绝强金创药']]:[['魔法药小','魔法药小'],['魔法药小','魔法药中'],['魔法药中','魔法药大'],['魔法药大','强效魔法药'],['强效魔法药','绝强魔法药']];for(const reward of names[tier])itemDrop(reward);}else itemDrop('一捧鲜花');return {ok:true,drops};
 }
 const slot=name==='金刚水'?'shield':'weapon',item=instanceItem(content.items[p.equipment[slot]],p.equipmentMeta?.[slot]);if(!item)return {ok:false,reason:slot==='shield'?'未手持盾牌':'未手持武器'};
 const old=p.equipmentMeta?.[slot]||{},meta={...old,fieldOverrides:{...old.fieldOverrides}},change=(field,amount)=>meta.fieldOverrides[field]=(item.rawFields[field]||0)+amount;
 if(name==='消色水'){delete meta.tint;p.equipmentMeta||={};p.equipmentMeta[slot]=meta;return {ok:true,drops,appearance:true};}
 if(name==='剧毒水'&&item.rawFields[23]>=3)return {ok:false,reason:'毒性似乎很难提升了'};
 if(!['剧毒水','消毒水'].includes(name)&&(old.waterUses||0)>=3)return {ok:false,reason:slot==='shield'?'当前盾牌已过量使用':'当前武器已过量使用'};
 if(rnd()>.3)return {ok:true,drops,message:'似乎没有什么效果'};
 if(name==='剧毒水')change(23,1);else if(name==='消毒水'){if(item.rawFields[23]>0)change(23,-1);}
 else if(name==='金刚水'){change(rnd()>.5?13:15,1);meta.waterUses=(old.waterUses||0)+1;}
 else{change(({战神水:7,仙尊水:9,天魔水:11})[name],1);meta.waterUses=(old.waterUses||0)+1;}
 p.equipmentMeta||={};p.equipmentMeta[slot]=meta;return {ok:true,drops};
}
