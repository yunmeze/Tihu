import {insightOn} from './permanent-state.js';
import {consumableEffect,useCarriedConsumable} from './consumables.js';
import {inventoryKey,carriedItems} from './inventory.js';
export function updateInsightAutomation(app){
 const p=app.player,c=app.combat;if(p.hp<=0||app.itemBusy||app.autoItemBusy||app.elapsed<(app.nextAutoItem||0))return;
 app.nextAutoItem=app.elapsed+.5;
 const carried=carriedItems(p),source=e=>{const index=p.belt.indexOf(e);return index>=0?{kind:'belt',index}:{kind:'bag',key:inventoryKey(e)};};
 let selected;
 for(const [id,key,threshold,pool]of [[11,'hp',p.autoHpPercent,'healingPool'],[12,'mp',p.autoMpPercent,'mpRecoveryPool']]){
  if(!insightOn(p,id)||p[key]*100>=p.base[key]*threshold||p[pool]>0)continue;
  selected=carried.find(e=>{const item=app.content.items[e.itemId];return consumableEffect(item)?.kind==='restore'&&item[key]>0;});if(selected)break;
 }
 if(!selected&&insightOn(p,9))selected=carried.find(e=>{const effect=consumableEffect(app.content.items[e.itemId]),child=effect?.kind==='package'&&app.content.itemNames.get(effect.name);return consumableEffect(child)?.kind==='restore'&&!carried.some(i=>i.itemId===child.id);});
 if(selected){app.autoItemBusy=true;useCarriedConsumable(app,source(selected)).then(r=>{if(r.ok)app.prepareOwned().catch(e=>console.error(e));}).catch(e=>console.error(e)).finally(()=>app.autoItemBusy=false);return;}
 if(insightOn(p,10)&&!c.targetId&&!c.path.length&&c.position.actionTime<=0){const g=c.groundItems.find(g=>g.kind==='gold'&&Math.max(Math.abs(g.x-c.position.x),Math.abs(g.y-c.position.y))<=1);if(g)c.collect(g.id);}
}
