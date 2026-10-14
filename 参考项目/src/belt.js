import {findInventory,inventoryKey,mergeItem,sameItemStack,takeItem,validInventory} from './inventory.js';
import {instanceItem} from './native-stats.js';
import {consumableEffect} from './consumables.js';
import {bagReceiveAmount} from './bag-capacity.js';

export const BELT_SIZE=6;
export const isBeltConsumable=item=>!!consumableEffect(item);
const fail=reason=>({ok:false,reason});

export function normalizeBelt(player,content){
 const saved=Array.isArray(player.belt)?player.belt:[],belt=Array(BELT_SIZE).fill(null);
 for(let i=0;i<saved.length;i++)for(const entry of validInventory([saved[i]],content)){
  if(i<BELT_SIZE&&isBeltConsumable(instanceItem(content.items[entry.itemId],entry)))belt[i]=entry;
  else mergeItem(player.inventory,entry.itemId,entry.quantity,entry);
 }
 player.belt=belt;return player;
}

export function putInBelt(player,content,key){
 const entry=findInventory(player.inventory,key),item=entry&&instanceItem(content.items[entry.itemId],entry);
 if(!isBeltConsumable(item))return fail('仅限一次性消耗品');
 const belt=player.belt||Array(BELT_SIZE).fill(null),match=belt.findIndex(e=>sameItemStack(e,entry)),index=match>=0?match:belt.findIndex(e=>!e);
 if(index<0)return fail('腰带已满');
 if(!Number.isSafeInteger((belt[index]?.quantity||0)+entry.quantity))return fail('物品数量过多');
 const taken=takeItem(player.inventory,inventoryKey(entry),entry.quantity);if(!taken)return fail('物品数量不足');
 if(belt[index])mergeItem([belt[index]],taken.itemId,taken.quantity,taken);else belt[index]=taken;
 player.belt=belt;return {ok:true,index};
}

export function returnFromBelt(player,index){
 const entry=player.belt?.[index];if(!entry)return fail('腰带中没有物品');
 if(bagReceiveAmount(player,entry.itemId,entry.quantity,entry)!==entry.quantity)return fail('背包空间不足');
 if(!mergeItem(player.inventory,entry.itemId,entry.quantity,entry))return fail('物品数量过多');
 player.belt[index]=null;return {ok:true};
}

export function useBeltItem(combat,index){
 const entry=combat.player.belt?.[index],item=entry&&instanceItem(combat.content.items[entry.itemId],entry);
 if(!entry)return fail('腰带中没有物品');
 if(combat.player.hp<=0)return fail('死亡后无法使用药品');
 if(consumableEffect(item)?.kind!=='restore')return fail('此物品需通过道具使用流程');
 if(!combat.usePotion(item))return fail('生命和魔法已满');
 takeItem([entry],inventoryKey(entry),1);if(!entry.quantity)combat.player.belt[index]=null;
 return {ok:true};
}
