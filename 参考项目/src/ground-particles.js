import {instanceItem} from './native-stats.js';
import {insightOn} from './permanent-state.js';
import {emitNativeParticle} from './native-particles.js';

const states=new WeakMap();
const color=rgb=>'#'+rgb.map(n=>Math.max(0,Math.min(255,n)).toString(16).padStart(2,'0')).join('');
// The native dropped-item clock is visual state, not inventory metadata.
export function emitGroundParticles(c){
 if(!insightOn(c.player,4)||!c.groundItems?.length)return;
 let table=states.get(c);if(!table)states.set(c,table=new Map());
 const ids=new Set(c.groundItems.map(g=>g.id));for(const id of table.keys())if(!ids.has(id))table.delete(id);
 for(const g of c.groundItems){
  if(g.kind!=='item'||Math.abs(g.x-c.position.x)>17||Math.abs(g.y-c.position.y)>26)continue;
  let s=table.get(g.id);if(!s||s.entry!==g){const item=instanceItem(c.content.items[g.itemId],g);if(!item||item.type<7||item.type>14)continue;const price=item.rawFields[37]||0;if(price<=0&&!(g.mergeLevel>0))continue;s={entry:g,raw:item.rawFields,price,grade:g.mergeLevel||0,clock:0,phase:0,rgb:[0,0,0]};table.set(g.id,s);}
  s.clock++;if(s.clock>20000)s.clock=0;
  if(s.price>10&&s.price<15&&!s.grade){if(s.clock%20===0)emitNativeParticle(c,5,{x:g.x+.5,y:g.y+20/32});}
  else if(s.price>=15||s.grade){
   const rgb=s.rgb;
   if(s.phase===0){rgb[2]=255;s.phase=1;}
   else if(s.phase===1){rgb[1]+=30;if(rgb[1]>=255){rgb[1]=255;s.phase=2;}}
   else if(s.phase===2){rgb[2]-=50;rgb[0]+=50;if(rgb[2]<=0){rgb[2]=0;rgb[0]=255;s.phase=3;}}
   else if(s.phase===3){rgb[1]-=5;if(rgb[1]<=0){rgb[1]=0;s.phase=4;}}
   else{rgb[2]+=50;rgb[0]-=20;if(rgb[2]>=255){rgb[2]=255;rgb[0]=0;s.phase=1;}}
   if(s.clock%10===0)emitNativeParticle(c,21,{x:g.x+.5,y:g.y+20/32},{color:color(rgb)});
  }
  for(const [field,type,period,x]of [[21,0,(5-s.raw[21])*10,5],[22,1,(5-s.raw[22])*15,0],[23,2,65-s.raw[23]*15,5],[25,3,55-s.raw[25]*15,0],[27,8,55-s.raw[27]*15,0],[24,22,(5-s.raw[24])*20,24]])if(s.raw[field]>0&&period>0&&s.clock%period===0)emitNativeParticle(c,type,{x:g.x+x/48,y:g.y+25/32});
 }
}
