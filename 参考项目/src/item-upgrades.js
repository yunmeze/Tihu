import {instanceItem} from './native-stats.js';
import {inventoryKey,takeItem,mergeItem} from './inventory.js';

// Fields used by the unchanged #UpWeapon recipes in G00, H00 and K00.
const fields={dc:6,dcmax:7,sc:8,scmax:9,mc:10,mcmax:11,df:12,dfmax:13,dm:14,dmmax:15,'准确':20,'燃烧':22,'引燃':22,'中毒':23,'冰封':21,'麻痹':24,'吸血':25,'伤害反弹':26,'幸运':27,'图标':1,'外观':2};
export function parseItemUpgrade(args){
 const m=args.match(/^(.+?)\s+(\S+)\s*([=+-])\s*(.+)$/);if(!m)return null;
 const [name,field,operator,value]=m.slice(1),key=field.toLowerCase();
 if(key==='name'&&operator==='='&&value.trim())return {kind:'upgradeItem',name,field:'name',operator,value:value.trim()};
 if(fields[key]===undefined||!/^\d+$/.test(value))return null;
 return {kind:'upgradeItem',name,field:fields[key],operator,value:Number(value)};
}
export function upgradeItems(player,content,effect){
 const matching=player.inventory.filter(e=>instanceItem(content.items[e.itemId],e)?.name===effect.name);if(!matching.length)return false;
 const upgrades=[];
 for(const entry of matching){const item=instanceItem(content.items[entry.itemId],entry),metadata={...entry};
  if(effect.field==='name')metadata.name=effect.value;
  else {const old=item.rawFields[effect.field]||0,n=effect.operator==='='?effect.value:effect.operator==='+'?old+effect.value:old-effect.value;if(!Number.isInteger(n)||n< -32768||n>32767)return false;metadata.fieldOverrides={...entry.fieldOverrides,[effect.field]:n};}
  upgrades.push({key:inventoryKey(entry),quantity:entry.quantity,metadata});
 }
 for(const {key,quantity,metadata}of upgrades){const entry=takeItem(player.inventory,key,quantity);if(!entry)return false;mergeItem(player.inventory,entry.itemId,quantity,metadata);}return true;
}
