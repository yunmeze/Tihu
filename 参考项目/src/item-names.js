// Native type-5 records embed the destination after their displayed name.
// Retain the full exported name while resolving scripts by the displayed name.
export function itemName(item){return item?.type===5?item.name.replace(/\s+\S+$/,''):item?.name||'';}
export function resolveItem(content,name){return content.itemNames.get(name)||content.items.find(i=>i.type===5&&itemName(i)===name);}
