import {findInventory,inventoryKey} from './inventory.js';
import {instanceItem} from './native-stats.js';
import {drawItemProperties} from './item-details.js';
import {forgeQuote,forgeEquipment,mergeQuote,mergeEquipment,ORES} from './equipment-refining.js';

export async function refiningAction(app){
 const d=app.serviceView;if(!d||!['forge','merge'].includes(d.kind)||app.serviceBusy)return;
 app.serviceBusy=true;
 try{
  const result=d.kind==='forge'?forgeEquipment(app.player,app.content,d.selections?.[0],app.combat.random):mergeEquipment(app.player,app.content,d.selections,app.combat.random);
  d.feedback=!result.ok?result.reason:result.destroyed?'锻造失败':result.success?(d.kind==='forge'?'锻造成功':'合成成功'):'合成失败';
  if(result.ok){d.selections=[];app.audio?.ui(result.success?'按键2':'回收');await app.prepareOwned();app.save();}
 }finally{app.serviceBusy=false;}
}
export function drawRefining(app){
 const d=app.serviceView,b=app.batch,h=app.hud,forge=d.kind==='forge';d.selections||=[];
 app.buttons=app.buttons.filter(button=>button.y>=1040||button.label==='地图');
 b.quad(20,204,710,810,'#211915');h.panel(20,204,710,810);
 b.text(forge?'装备锻造':'装备合成',48,246,32,'#e8c887',480);
 app.button('关闭窗口',564,234,136,58,()=>app.serviceView=null,false,24);
 b.text(d.name,48,306,26,'#d8c493');
 const labels=forge?['武器']:['武器一','武器二','矿石一','矿石二','属性一','属性二'];
 const bag=findInventory(app.player.inventory,app.selectedItem)||app.player.inventory[0];
 for(let i=0;i<labels.length;i++){
  const x=72+i%2*170,y=390+Math.floor(i/2)*170,e=findInventory(app.player.inventory,d.selections[i]);
  h.centered(labels[i],x,y-26,116,24);h.slot(x,y,116,116,!!e);
  if(e)app.icon(instanceItem(app.content.items[e.itemId],e),x,y,116);
  app.region('炼制栏:'+i,x,y,116,116,()=>{if(!bag){d.feedback='请在背包中选择物品';return;}d.selections[i]=inventoryKey(bag);d.feedback=null;});
  if(e)app.button('移除',x,y+118,116,24,()=>{d.selections[i]=null;d.feedback=null;},false,18);
 }
 const selected=findInventory(app.player.inventory,d.selections[0]),item=selected&&instanceItem(app.content.items[selected.itemId],selected);
 if(item){b.paragraph(item.name,414,358,282,28,36,2);d.itemDetails||={};drawItemProperties(app,item,{x:414,y:443,w:282,h:275,size:25,line:31,state:d.itemDetails,scope:'refining',entry:selected});}
 const quote=forge?forgeQuote(app.player,app.content,d.selections[0]):mergeQuote(app.player,app.content,d.selections);
 if(quote.ok){b.text('金币 '+quote.gold,414,750,25);b.text('成功率 '+quote.successPercent+'%',414,788,25);
  if(forge){let y=550;quote.ores.forEach((n,i)=>{if(n){b.text(ORES[i]+' '+n,72,y,24);y+=34;}});b.text('失败武器消失',72,744,24,'#ddaa89');}
 }else if(d.selections.some(v=>v!==null&&v!==undefined))b.paragraph(quote.reason,414,750,282,24,31,3);
 if(d.feedback)b.paragraph(d.feedback,48,855,652,25,32,2);
 app.button(forge?'锻造':'合成',414,918,282,58,()=>refiningAction(app),false,28);
 if(bag)b.paragraph('选择：'+instanceItem(app.content.items[bag.itemId],bag).name,48,918,338,24,31,2);
}
