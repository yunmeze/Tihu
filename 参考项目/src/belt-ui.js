import {BELT_SIZE} from './belt.js';
import {instanceItem} from './native-stats.js';
import {itemName} from './item-names.js';

export function drawBelt(app,{x=203,y=1304,size=80,gap=6,manage=false}={}){
 const entries=app.player.belt||[],h=app.hud,b=app.batch;
 for(let i=0;i<BELT_SIZE;i++){
  const left=x+i*(size+gap),entry=entries[i],item=entry&&instanceItem(app.content.items[entry.itemId],entry);
  b.quad(left+3,y+3,size-6,size-6,'#211915');
  h.slot(left,y,size,size,manage&&app.selectedBelt===i);
  if(item){app.icon(item,left,y,size);b.quad(left+3,y+size-26,size-6,24,'#100c08',b.white,[0,0,1,1],.95);h.centered('×'+entry.quantity,left+3,y+size-26,size-6,24,'#fff0cb');}
  app.region('腰带:'+i+':'+(item?itemName(item):'空'),left,y,size,size,()=>{
   if(manage){app.selectedBelt=i;app.selectedItem=null;}else if(entry)return app.useConsumable({kind:'belt',index:i});
  });
 }
}
