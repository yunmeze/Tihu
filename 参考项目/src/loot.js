import {rollEquipmentAffixes} from './equipment-affixes.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {recordCollectionDrop} from './permanent-state.js';
import {itemInstanceMetadata} from './inventory.js';
export function rollGroundDrops(definition,content,random,player={}){
 const rolled=new Map();
 for(const [index,rule] of (definition.dropRules||[]).entries()){
  if(rule.quantity<=0||Math.max(1,nativeRound(sampleMonsterRandom(random)*rule.denominator))!==1)continue;
  const item=rule.item==='金币'?null:content.itemNames.get(rule.item);if(rule.item!=='金币'&&!item)continue;
  if(definition.id>=4)recordCollectionDrop(player,definition.id,index);
  if(item&&item.type>=7&&item.type<=14){for(let i=0;i<rule.quantity;i++){const metadata=rollEquipmentAffixes(item,player,random),key='gear:'+item.id+':'+JSON.stringify(metadata),existing=rolled.get(key);if(existing)existing.quantity++;else rolled.set(key,{kind:'item',itemId:item.id,quantity:1,...metadata});}continue;}
  const kind=item?'item':'gold',key=item?'item:'+item.id:'gold',quantity=item?rule.quantity:Math.max(1,Math.trunc(rule.quantity/3)+nativeRound(sampleMonsterRandom(random)*(rule.quantity-Math.trunc(rule.quantity/3)))),existing=rolled.get(key);
  if(existing)existing.quantity+=quantity;else rolled.set(key,{kind,...(item?{itemId:item.id}:{}),quantity});
 }
 return [...rolled.values()];
}
export function restoreGroundItems(state,content){
 const result={};if(!state||typeof state!=='object')return result;
 for(const [mapId,entries]of Object.entries(state)){
  if(!Array.isArray(entries)||!content.mapList?.some(m=>m.id===mapId))continue;
  const ids=new Set();result[mapId]=[];
  for(const g of entries){
   if(!g||typeof g.id!=='string'||ids.has(g.id)||!Number.isInteger(g.x)||!Number.isInteger(g.y)||!Number.isSafeInteger(g.quantity)||g.quantity<=0)continue;
   if(g.kind!=='gold'&&(g.kind!=='item'||!Number.isInteger(g.itemId)||!content.items[g.itemId]||content.items[g.itemId].name==='0'))continue;
   ids.add(g.id);result[mapId].push({id:g.id,x:g.x,y:g.y,kind:g.kind,quantity:g.quantity,...(g.kind==='item'?{itemId:g.itemId,...itemInstanceMetadata(g),...(g.discarded!==undefined?{discarded:g.discarded}:{})}:{})});
  }
 }
 return result;
}
export function groundItemIcon(item){return item.kind==='gold'?Math.min(5,item.quantity>=1000?5:item.quantity>=500?4:item.quantity>=100?3:item.quantity>1?2:1):null;}
