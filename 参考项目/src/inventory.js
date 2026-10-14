let instanceSequence=0;
// Persist the same instance fields whether gear is carried or on the ground.
export const ITEM_INSTANCE_FIELDS=Object.freeze(['instanceId','name','fieldOverrides','forgeLevel','fused','mergeLevel','priceBonus','tint','affixModel','waterUses','dropSources']);
export const itemInstanceMetadata=entry=>Object.fromEntries(ITEM_INSTANCE_FIELDS.filter(k=>entry?.[k]!==undefined).map(k=>[k,entry[k]]));
export const inventoryKey=entry=>entry?.instanceId??entry?.itemId;
export const findInventory=(list,key)=>list.find(e=>inventoryKey(e)===key)||(typeof key==='number'?list.find(e=>e.itemId===key):undefined);
const variant=e=>JSON.stringify([e.forgeLevel||0,!!e.fused,e.name||null,e.fieldOverrides||{},e.priceBonus||0,e.mergeLevel||0,e.tint||null,e.waterUses||0]);
export const sameItemStack=(a,b)=>!!a&&!!b&&a.itemId===b.itemId&&variant(a)===variant(b);
export const carriedItems=player=>[...(player.inventory||[]),...(player.belt||[]).filter(Boolean)];
export const matchingBeltItem=(player,itemId,metadata={})=>(player.belt||[]).find(e=>sameItemStack(e,{...metadata,itemId}));
export function mergeCarriedItem(player,itemId,quantity,metadata={}){const entry=matchingBeltItem(player,itemId,metadata);return mergeItem(entry?[entry]:player.inventory,itemId,quantity,metadata);}
export function takeCarriedItem(player,key,quantity=1){
 if(findInventory(player.inventory,key))return takeItem(player.inventory,key,quantity);
 const entry=findInventory((player.belt||[]).filter(Boolean),key);if(!entry)return null;
 const index=player.belt.indexOf(entry),taken=takeItem([entry],inventoryKey(entry),quantity);if(taken&&!entry.quantity)player.belt[index]=null;return taken;
}
export function dropSources(entry){let remaining=entry.quantity;const result=[];for(const source of entry.dropSources||[]){if(!Number.isInteger(source.mode)||source.mode<0||!Number.isSafeInteger(source.quantity)||source.quantity<=0)continue;const quantity=Math.min(source.quantity,remaining);if(quantity)result.push({mode:source.mode,quantity});remaining-=quantity;}return result;}
export function droppedCount(entry,mode){return dropSources(entry).filter(s=>mode===undefined||s.mode===mode).reduce((n,s)=>n+s.quantity,0);}
export function mergeItem(list,itemId,quantity,metadata={}){
 if(!Number.isSafeInteger(quantity)||quantity<=0)return false;let entry=list.find(e=>e.itemId===itemId&&variant(e)===variant(metadata));if(entry&&!Number.isSafeInteger(entry.quantity+quantity))return false;
 const sources=dropSources({quantity,dropSources:metadata.dropSources||[]});if(!entry){entry={...metadata,itemId,quantity:0};delete entry.dropSources;if(metadata.forgeLevel||metadata.fused||metadata.fieldOverrides||metadata.name||metadata.priceBonus||metadata.tint||metadata.mergeLevel){entry.instanceId||='gear:'+itemId+':'+(++instanceSequence);while(list.some(e=>e.instanceId===entry.instanceId))entry.instanceId='gear:'+itemId+':'+(++instanceSequence);}list.push(entry);}const existing=dropSources(entry);entry.quantity+=quantity;for(const source of sources){const old=existing.find(s=>s.mode===source.mode);if(old)old.quantity+=source.quantity;else existing.push({...source});}if(existing.length)entry.dropSources=existing;else delete entry.dropSources;return true;
}
export function takeItem(list,itemId,quantity=1,{preferDropped=false,mode}={}){
 const index=list.indexOf(findInventory(list,itemId)),entry=list[index];if(!entry||!Number.isSafeInteger(quantity)||quantity<=0||entry.quantity<quantity)return null;const sources=dropSources(entry);
 if(preferDropped&&sources.filter(s=>mode===undefined||s.mode===mode).reduce((n,s)=>n+s.quantity,0)<quantity)return null;
 let remaining=preferDropped?quantity:Math.max(0,quantity-(entry.quantity-sources.reduce((n,s)=>n+s.quantity,0)));const taken=[];for(const source of sources){if(preferDropped&&mode!==undefined&&source.mode!==mode)continue;const count=Math.min(remaining,source.quantity);if(count){taken.push({mode:source.mode,quantity:count});source.quantity-=count;remaining-=count;}}
 const result={...entry,quantity};if(taken.length)result.dropSources=taken;else delete result.dropSources;entry.quantity-=quantity;if(!entry.quantity)list.splice(index,1);else{const kept=sources.filter(s=>s.quantity>0);if(kept.length)entry.dropSources=kept;else delete entry.dropSources;}return result;
}
export function validInventory(entries,content){const result=[];for(const entry of Array.isArray(entries)?entries:[]){if(!entry||!Number.isInteger(entry.itemId)||!content.items[entry.itemId]||content.items[entry.itemId].name==='0'||!Number.isSafeInteger(entry.quantity)||entry.quantity<=0)continue;mergeItem(result,entry.itemId,entry.quantity,{...entry,dropSources:dropSources(entry)});}return result;}
