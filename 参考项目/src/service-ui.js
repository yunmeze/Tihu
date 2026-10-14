import {drawRefining} from './refining-ui.js';
import {instanceItem} from './native-stats.js';
import {itemName} from './item-names.js';
import {drawItemProperties} from './item-details.js';
import {buyItem,sellItem,sellPrice,transferStorage,transferBankGold} from './services.js';
import {droppedCount,dropSources,inventoryKey,findInventory} from './inventory.js';
export function serviceItems(app){const d=app.serviceView;if(!d)return [];return d.kind==='storage'?app.player.storage.items:d.kind==='dimension'?app.player.dimensionBox.items.filter(e=>droppedCount(e,app.player.gameMode||0)>0).map(e=>({...e,quantity:droppedCount(e,app.player.gameMode||0),dropSources:dropSources(e).filter(s=>s.mode===(app.player.gameMode||0))})):d.kind==='shop'?d.dialogue.shopItems.map(itemId=>({itemId,quantity:null})):[];}
export async function prepareService(app){if(!app.serviceView)return;const d=app.serviceView,list=serviceItems(app),pages=Math.max(1,Math.ceil(list.length/25));d.page=Math.min(d.page,pages-1);await Promise.all(list.slice(d.page*25,d.page*25+25).map(e=>app.content.frame('Item1',instanceItem(app.content.items[e.itemId],e).icon)));await app.content.sync();}
export async function serviceAction(app,action){
 const d=app.serviceView;if(!d||app.serviceBusy)return;app.serviceBusy=true;
 try{const p=app.player,c=app.content,list=serviceItems(app),stock=findInventory(list,d.selectedItem)||list[0],bag=findInventory(p.inventory,app.selectedItem)||p.inventory[0],entry=action==='withdraw'||action==='buy'?stock:bag;let quantity=d.quantity,result;
  if(quantity==='all'){if(action==='depositGold')quantity=p.gold;else if(action==='withdrawGold')quantity=p.storage.gold;else if(action==='buy')quantity=c.items[entry?.itemId]?.price>0?Math.floor(p.gold/c.items[entry.itemId].price):1;else quantity=d.kind==='dimension'?entry&&droppedCount(entry,p.gameMode||0):entry?.quantity||0;}
  if(action==='depositGold'||action==='withdrawGold')result=transferBankGold(p,quantity,action==='depositGold');
  else if(!entry)result={ok:false,reason:'没有可用的物品'};
  else if(action==='buy')result=buyItem(p,c,d.dialogue.shopItems,entry.itemId,quantity);
  else if(action==='sell')result=sellItem(p,c,inventoryKey(entry),quantity);
  else result=transferStorage(p,c,d.kind,inventoryKey(entry),quantity,action==='deposit');
  d.feedback=result.ok?null:result.reason;if(result.ok){if(action==='buy')app.audio?.pickup(c.items[entry.itemId],false,{ui:true});else app.audio?.ui(action==='sell'?'回收':action.endsWith('Gold')?'道具-钱':'道具-其它');await app.prepareOwned();await prepareService(app);app.save();}
 }finally{app.serviceBusy=false;}
}
export function drawService(app){
 if(['forge','merge'].includes(app.serviceView?.kind)){drawRefining(app);return;}
 const d=app.serviceView,b=app.batch,h=app.hud,list=serviceItems(app),storage=['storage','dimension'].includes(d.kind),trading=['shop','sell'].includes(d.kind),pages=Math.max(1,Math.ceil(list.length/25));d.page=Math.min(d.page,pages-1);
 // Retain lower inventory/nav and the mini-map; suppress world input regions.
 app.buttons=app.buttons.filter(button=>button.y>=1040||button.label==='地图');b.quad(20,204,710,810,'#211915');h.panel(20,204,710,810);b.text(d.name+(d.kind==='dimension'?'（共享）':''),48,245,32,'#e8c887',486);app.button('关闭窗口',564,234,136,58,()=>app.serviceView=null,false,24);
 if(d.kind==='storage')b.text('金币 '+app.player.storage.gold,48,305,25,'#d8c493');else if(d.dialogue.text.length&&d.kind!=='dialogue'&&(!trading||!d.feedback))b.paragraph(d.dialogue.text.join('\n'),48,305,654,24,29,2);
 const bag=findInventory(app.player.inventory,app.selectedItem)||app.player.inventory[0],stock=findInventory(list,d.selectedItem)||list[0],entry=d.kind==='sell'?bag:stock,item=entry&&instanceItem(app.content.items[entry.itemId],entry);
 if(storage||d.kind==='shop'){for(let i=0;i<25;i++){const x=48+i%5*82,y=368+Math.floor(i/5)*82,e=list[d.page*25+i];h.slot(x,y,78,78,!!e&&inventoryKey(e)===inventoryKey(entry));if(e){const definition=instanceItem(app.content.items[e.itemId],e);app.icon(definition,x,y,78);if(e.quantity!==null)b.text(e.quantity,x+43,y+52,22,'#fff0cb');app.region('窗口物品:'+e.itemId,x,y,78,78,()=>{d.selectedItem=inventoryKey(e);d.quantity=1;d.feedback=null;},{rightClick:storage?()=>{d.selectedItem=inventoryKey(e);d.quantity=1;return serviceAction(app,'withdraw');}:undefined});}}}
 else if(d.kind==='sell'&&item){app.icon(item,161,414,184);h.centered(itemName(item),70,620,360,30,'#e9d096');}
 else if(d.kind==='dialogue')b.paragraph(d.dialogue.text.join('\n'),48,354,654,28,37,12);
 if(d.kind!=='dialogue'){
  if(item){b.paragraph(itemName(item),486,355,218,28,36,2);b.text(d.kind==='shop'?'价格 '+item.price:'数量 '+entry.quantity,486,438,25);if(d.kind==='sell')b.text('回收价 '+(sellPrice(item,entry)??'—'),486,478,25);if(trading){d.itemDetails||={};drawItemProperties(app,item,{x:486,y:524,w:218,h:236,size:25,line:31,state:d.itemDetails,scope:'service',entry});}}
  if(storage&&bag&&!d.feedback)b.paragraph('背包：'+itemName(app.content.items[bag.itemId]),486,546,218,24,32,2);
  if(d.feedback)b.paragraph(d.feedback,trading?48:486,trading?305:546,trading?654:218,24,trading?29:31,trading?2:3);
  h.centered('数量 '+(d.quantity==='all'?'全部':d.quantity),486,trading?778:616,218,26);
  app.button('-',486,trading?818:655,68,50,()=>d.quantity=typeof d.quantity==='number'?Math.max(1,d.quantity-1):1,false,26);app.button('+',559,trading?818:655,68,50,()=>d.quantity=typeof d.quantity==='number'?Math.min(Number.MAX_SAFE_INTEGER,d.quantity+1):1,false,26);app.button('全部',632,trading?818:655,72,50,()=>d.quantity='all',false,23);
  if(storage){app.button('取出',486,724,218,52,()=>serviceAction(app,'withdraw'),false,26);app.button('存入',486,786,218,52,()=>serviceAction(app,'deposit'),false,26);}else app.button(d.kind==='shop'?'购买':'出售',486,898,218,52,()=>serviceAction(app,d.kind==='shop'?'buy':'sell'),false,26);
  if(d.kind==='storage'){app.button('存金币',486,850,105,52,()=>serviceAction(app,'depositGold'),false,23);app.button('取金币',599,850,105,52,()=>serviceAction(app,'withdrawGold'),false,23);}
 }
 if(pages>1){app.button('上页',48,800,126,48,async()=>{d.page=Math.max(0,d.page-1);await prepareService(app);},false,25);h.centered((d.page+1)+' / '+pages,188,811,126,25);app.button('下页',328,800,126,48,async()=>{d.page=Math.min(pages-1,d.page+1);await prepareService(app);},false,25);}
 const choices=d.dialogue.choices.filter(choice=>choice.action.toUpperCase()!=='OVER'),choicePages=Math.max(1,Math.ceil(choices.length/2));d.choicePage=Math.min(d.choicePage||0,choicePages-1);
 choices.slice(d.choicePage*2,d.choicePage*2+2).forEach((choice,i)=>{const y=858+i*62;const width=trading||storage?406:654;h.button(48,y,width,52);h.centered(choice.label,60,y+13,width-24,26,'#e2c98e');app.region(choice.label,48,y,width,52,()=>app.npcChoice(choice.action,d));});
 if(choicePages>1)app.button('选项 '+(d.choicePage+1)+'/'+choicePages,530,298,172,48,()=>d.choicePage=(d.choicePage+1)%choicePages,false,23);
}
