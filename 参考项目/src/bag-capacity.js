import {matchingBeltItem,sameItemStack} from './inventory.js';

export const BAG_CAPACITIES=Object.freeze({'战士':50,'法师':30,'道士':40});
export function bagState(player){
 const capacity=BAG_CAPACITIES[player.class]||BAG_CAPACITIES['战士'],slots=(player.inventory||[]).filter(e=>e?.quantity>0).length;
 return {capacity,slots,freeSlots:capacity-slots};
}
const validQuantity=quantity=>Number.isSafeInteger(quantity)&&quantity>0;
const stackRoom=entry=>Math.max(0,Number.MAX_SAFE_INTEGER-entry.quantity);
export function bagReceiveAmount(player,itemId,quantity,metadata={}){
 if(!validQuantity(quantity))return 0;
 const stack=(player.inventory||[]).find(e=>sameItemStack(e,{...metadata,itemId}));
 return Math.min(quantity,stack?stackRoom(stack):bagState(player).freeSlots>0?Number.MAX_SAFE_INTEGER:0);
}
export function carriedReceiveAmount(player,itemId,quantity,metadata={}){
 if(!validQuantity(quantity))return 0;
 const belt=matchingBeltItem(player,itemId,metadata);
 return belt?Math.min(quantity,stackRoom(belt)):bagReceiveAmount(player,itemId,quantity,metadata);
}
