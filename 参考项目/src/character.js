import {nativeAttributes,NUMERIC_MODEL,instanceItem} from './native-stats.js';
export const EQUIPMENT=[['helmet','头盔',7],['necklace','项链',8],['armor','衣服',9],['boots','鞋',10],['braceletLeft','手镯',11],['braceletRight','手镯',11],['ringLeft','戒指',12],['ringRight','戒指',12],['shield','盾牌',13],['weapon','武器',14]];
import {mergeCarriedItem,takeCarriedItem,takeItem,validInventory,findInventory} from './inventory.js';
import {normalizeBelt,BELT_SIZE} from './belt.js';
import {normalizeProgress} from './progression.js';
import {normalizeAppearance} from './appearance.js';
import {bagState,bagReceiveAmount} from './bag-capacity.js';
export const SKILL_ORDER=['基本剑术','剑气斩','火龙斩','半月斩','烈火斩','冰封斩','自然之力','灵魂火符','回生术','治愈术','隐身术','召唤骷髅','召唤神兽','施毒术','侵蚀术','火球术','爆裂火球','雷电术','火墙','魔法盾','御冰术','地狱雷光','强冰术','冰咆哮','诱惑之光','炼尸咒'];
// Legacy regression fixture. Production creation uses the native template below.
export function createCharacter(content,saved){
 if(saved?.version===2&&saved.player){const p=structuredCloneSafe(saved.player);p.inventory=validInventory(p.inventory,content);p.storage={items:validInventory(p.storage?.items,content),gold:Number.isSafeInteger(p.storage?.gold)&&p.storage.gold>=0?p.storage.gold:0};p.dimensionBox={items:validInventory(p.dimensionBox?.items,content)};p.equipmentMeta||={};p.skills=(p.skills||[]).filter(s=>content.skills.records.some(r=>r.name===s.name)&&s.level>0);p.unlockedMaps=(p.unlockedMaps||['A00']).filter(id=>content.mapList.some(m=>m.id===id));return normalizeProgress(normalizeAppearance(normalizeBelt(p,content)));}
 const item=name=>content.itemNames.get(name)?.id,player={name:'英雄',class:'战士',gender:0,level:1,experience:0,gold:0,hp:25,mp:15,base:{hp:25,mp:15,attack:[1,2],tao:[0,0],magic:[0,0],defense:[0,0],magicDefense:[0,0]},inventory:[{itemId:item('金创药小'),quantity:5},{itemId:item('魔法药小'),quantity:3}],equipment:{weapon:item('木剑'),armor:item('布衣')},skills:[{name:'基本剑术',level:1}],unlockedMaps:['A00'],events:[3],activeSkill:'基本剑术'};
 player.belt=Array(BELT_SIZE).fill(null);player.storage={items:[],gold:0};player.dimensionBox={items:[]};player.equipmentMeta={};return normalizeProgress(normalizeAppearance(player));
}
function structuredCloneSafe(value){return JSON.parse(JSON.stringify(value));}
// HP/MP verified in native creation function 591980, branches 593085/5932b4/5934e3.
export const CHARACTER_CLASSES={
 '战士':{hp:25,mp:5,attack:[1,3],tao:[0,1],magic:[0,1],defense:[0,3],magicDefense:[0,1],accuracy:7,capacity:25,skill:'基本剑术',description:'近身攻击，擅长剑法。'},
 '道士':{hp:22,mp:15,attack:[0,2],tao:[1,2],magic:[0,2],defense:[0,2],magicDefense:[0,2],accuracy:7,capacity:22,skill:'灵魂火符',description:'符咒与召唤，攻守兼备。'},
 '法师':{hp:17,mp:15,attack:[0,1],tao:[0,1],magic:[1,3],defense:[0,1],magicDefense:[0,3],accuracy:6,capacity:20,skill:'火球术',description:'远程法术，魔法攻击。'},
};
export function createNewCharacter(content,{name='英雄',class:job='战士',gender=0,gameMode=0}={}){
 const profile=CHARACTER_CLASSES[job];if(!profile)throw Error('Unknown character class');const p=createCharacter(content,{}),{skill,description,...base}=profile;
 Object.assign(p,{name,class:job,gender:gender===1?1:0,headStyle:gender===1?1:0,hp:base.hp,mp:base.mp,base:structuredCloneSafe(base),inventory:[],equipment:{armor:content.itemNames.get('布衣').id},equipmentMeta:{},skills:[],skillPoints:1,attributePoints:1,activeSkill:null,gameMode:0,clearCount:0,creationProfile:'native-classes-v2',numericModel:NUMERIC_MODEL});
 // Native creation caches the starter cloth's defense in the displayed total.
 p.gameMode=[0,1,2].includes(gameMode)?gameMode:0;const cloth=content.itemNames.get('布衣');for(const key of ['attack','tao','magic','defense','magicDefense'])for(let i=0;i<2;i++)p.base[key][i]-=cloth[key][i];return p;
}
export const attributes=nativeAttributes;
export function addItem(player,id,quantity=1,metadata={}){return mergeCarriedItem(player,id,quantity,metadata);}
export function removeItem(player,id,quantity=1){return !!takeCarriedItem(player,id,quantity);}
export function equipmentEligibility(player,content,id,entry={}){
 const item=instanceItem(content.items[id],entry);if(!EQUIPMENT.some(s=>s[2]===item?.type))return {allowed:false,reason:'无法穿戴'};
 const stats=attributes(player,content),requirements=[[31,player.level,'人物等级不够！'],[32,stats.attack[1],'人物攻击不够！'],[33,stats.tao[1],'人物道术不够！'],[34,stats.magic[1],'人物魔法不够！']];
 for(const [field,current,reason]of requirements)if((item.rawFields?.[field]||0)>current)return {allowed:false,reason,required:item.rawFields[field],current,field};
 return {allowed:true,reason:null};
}
export function equip(player,content,selector){
 const selected=findInventory(player.inventory,selector),id=selected?.itemId;if(!selected||!equipmentEligibility(player,content,id,selected).allowed)return false;
 const item=content.items[id],slots=EQUIPMENT.filter(s=>s[2]===item.type),slot=slots.find(s=>player.equipment[s[0]]===undefined)||slots[0],staged={...player,inventory:structuredCloneSafe(player.inventory),belt:structuredCloneSafe(player.belt||[])},taken=takeItem(staged.inventory,selector);if(!taken)return false;
 const old=player.equipment[slot[0]];if(old!==undefined&&!addItem(staged,old,1,player.equipmentMeta?.[slot[0]]||{}))return false;
 // Preserve legacy overflow while rearranging owned gear, without growing it.
 if(bagState(staged).slots>Math.max(bagState(player).capacity,bagState(player).slots))return false;
 player.inventory=staged.inventory;player.belt=staged.belt;player.equipmentMeta||={};player.equipment[slot[0]]=id;player.equipmentMeta[slot[0]]=taken;if(slot[0]==='weapon')delete player.unarmedUseCount;return true;
}
export function unequip(player,slot){const id=player.equipment[slot],meta=player.equipmentMeta?.[slot]||{};if(id===undefined||bagReceiveAmount(player,id,1,meta)!==1||!addItem(player,id,1,meta))return false;delete player.equipment[slot];if(slot==='weapon')delete player.unarmedUseCount;if(player.equipmentMeta)delete player.equipmentMeta[slot];return true;}
export function taskFor(player,text){const lines=text.split(/\r?\n/),count=Number(lines[0]),index=Math.max(1,player.events?.[0]||3);return index<=count?{index,title:lines[1+(index-1)*2],description:lines[2+(index-1)*2]}:null;}
