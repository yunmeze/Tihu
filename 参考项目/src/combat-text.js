export function combatText(combat,point,text,{kind='damage',color='#ffe5a2',actorId,appearance,duration=1.05,aggregate=false,amount=0,prefix=''}={}){
 if(aggregate){const previous=combat.events.find(e=>e.aggregate&&e.actorId===actorId&&combat.elapsed-e.lastHit<.3);if(previous){previous.amount+=amount;previous.text=prefix+previous.amount;previous.lastHit=combat.elapsed;previous.until=combat.elapsed+duration;previous.x=point.x;previous.y=point.y;return previous;}}
 const recent=combat.events.filter(e=>e.actorId===actorId&&combat.elapsed-(e.aggregate?e.lastHit:e.born??0)<.15).length;
 const event={x:point.x,y:point.y,text:String(text),kind,color,actorId,appearance,born:combat.elapsed,duration,until:combat.elapsed+duration,lane:recent%3,aggregate,amount,lastHit:combat.elapsed};
 combat.events.push(event);return event;
}
const boundsCache=new WeakMap();
// Labels use a stable idle silhouette, so attacking / dying / shadows do not
// make the name or HP bar jump. Sprite offsets already include the foot anchor.
export function labelTop(pack,first=1,last=32){
 if(!pack)return -48;let cache=boundsCache.get(pack);if(!cache)boundsCache.set(pack,cache=new Map());const key=first+':'+last;
 if(!cache.has(key)){const tops=pack.frames.slice(first,last+1).filter(f=>f.rect[2]>0&&f.rect[3]>0).map(f=>f.offset[1]+f.crop[1]);cache.set(key,tops.length?Math.min(...tops):-48);}
 return cache.get(key);
}
export function floatingTextLayout(event,now,point,top,scale){
 const duration=event.duration??1.05,age=Math.max(0,now-(event.aggregate?event.lastHit:event.born??event.until-duration)),progress=Math.min(1,age/duration),lane=event.lane||0;
 return {x:point.x+24*scale+(lane===1?-24:lane===2?24:0),y:point.y+top*scale-76-38*progress-lane*16,size:event.kind==='loot'?29:event.kind==='level'?36:38,opacity:Math.min(1,(1-progress)/.18)};
}
