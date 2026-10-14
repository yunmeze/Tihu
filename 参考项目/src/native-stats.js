import {bagState,carriedReceiveAmount} from './bag-capacity.js';
import {nativeRound} from './monster-motion.js';

// LP v1.2.2E: item words 6..27, native player 2062..208e.
export const RANGE_FIELDS={attack:6,tao:8,magic:10,defense:12,magicDefense:14};
export const PROPERTY_FIELDS={fastAttack:16,fastCast:17,physicalEvade:18,magicEvade:19,accuracy:20,freeze:21,burn:22,poison:23,paralysis:24,vampire:25,reflect:26,luck:27};
export const NUMERIC_MODEL='lp-122e-numerics-v1';
export function instanceItem(item,entry={}){
 if(!item)return null;
 const rawFields=[...(item.rawFields||[])];
 for(const [index,value]of Object.entries(entry.fieldOverrides||{}))if(Number.isInteger(+index)&&+index>=0&&+index<39&&Number.isInteger(value)&&value>=-32768&&value<=32767)rawFields[+index]=value;
 const result={...item,rawFields,name:entry.name||item.name,icon:rawFields[1]??item.icon,appearance:[rawFields[2]??item.appearance?.[0],rawFields[3]??item.appearance?.[1]],hp:rawFields[4]??item.hp,mp:rawFields[5]??item.mp};
 for(const [key,index]of Object.entries(RANGE_FIELDS))result[key]=[rawFields[index]??item[key]?.[0]??0,rawFields[index+1]??item[key]?.[1]??0];
 result.weight=rawFields[38]??item.weight??0;return result;
}
export function equipmentSet(player,content){
 const gear=slot=>instanceItem(content.items[player.equipment?.[slot]],player.equipmentMeta?.[slot]);
 const necklace=gear('necklace'),prefix=necklace?.name?.slice(0,2),match=item=>item&&item.name.length>=2&&item.name.slice(0,2)===prefix;
 const bracelets=['braceletLeft','braceletRight'].map(gear),rings=['ringLeft','ringRight'].map(gear).filter(match);
 if(!prefix||!bracelets.some(match)||!rings.length)return {level:0,key:null,bonus:0,prefix:null};
 // The native scan assigns the later matching ring (slot 7) last.
 const level=1+Number(!!match(gear('helmet')))+Number(!!match(gear('boots'))),ring=rings.at(-1),keys=['attack','tao','magic'];
 const max=Math.max(...keys.map(k=>ring[k][1])),key=keys.filter(k=>ring[k][1]===max).at(-1),value=Math.max(...rings.map(r=>r[key][1]));
 return {level,key,bonus:nativeRound(level*value/3)+level,prefix};
}
export function nativeAttributes(player,content){
 const result=JSON.parse(JSON.stringify(player.base));
 for(const [key]of Object.entries(PROPERTY_FIELDS))result[key]??=0;
 result.capacity??=0;result.setBonus=0;
 for(const [slot,id]of Object.entries(player.equipment||{})){
  const item=instanceItem(content.items[id],player.equipmentMeta?.[slot]);if(!item)continue;
  for(const key of Object.keys(RANGE_FIELDS))for(let end=0;end<2;end++)result[key][end]+=item[key][end];
  for(const [key,index]of Object.entries(PROPERTY_FIELDS))result[key]+=item.rawFields[index]||0;

 }
 const set=equipmentSet(player,content);if(set.key){result[set.key][1]+=set.bonus;result.setBonus=set.bonus;result.equipmentSet=set;}return result;
}
export function carryState(player,content){
 // Portrait inventory override: one displayed stack per slot. Native weight
 // fields remain source data, but no longer constrain carrying or purchases.
 return bagState(player);
}
export function canCarry(player,content,itemId,quantity=1,entry={}){
 return Number.isSafeInteger(quantity)&&quantity>0&&carryAmount(player,content,itemId,quantity,entry)===quantity;
}

export function carryAmount(player,content,itemId,quantity,entry={}){const item=content.items[itemId];return item&&item.name!=='0'?carriedReceiveAmount(player,itemId,quantity,entry):0;}

// Native 61cce6 / 61dbdb count sword contacts and released casts; 62524f
// adds integer count / 500 to outgoing damage, capped at 1500 uses.
export function recordWeaponUse(player,content){
 const id=player.equipment?.weapon;if(id===undefined){player.unarmedUseCount=Math.min(1500,(player.unarmedUseCount||0)+1);return;}
 const entry=player.equipmentMeta?.weapon||{},item=instanceItem(content.items[id],entry);if(!item)return;
 player.equipmentMeta||={};player.equipmentMeta.weapon={...entry,fieldOverrides:{...entry.fieldOverrides,36:Math.min(1500,(item.rawFields[36]||0)+1)}};
}
export function weaponUseBonus(player,content){const item=instanceItem(content.items[player.equipment?.weapon],player.equipmentMeta?.weapon);return Math.trunc((item?.rawFields[36]??player.unarmedUseCount??0)/500);}
