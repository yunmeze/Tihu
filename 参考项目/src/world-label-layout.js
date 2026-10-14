const GAP=3,CELL_X=128,CELL_Y=64;
export const overlaps=(a,b,gap=0)=>a.x<b.x+b.w+gap&&a.x+a.w+gap>b.x&&a.y<b.y+b.h+gap&&a.y+a.h+gap>b.y;
export const containsPoint=(r,p)=>p.x>=r.x&&p.x<=r.x+r.w&&p.y>=r.y&&p.y<=r.y+r.h;
const fits=(r,v)=>r.x>=v.x&&r.y>=v.y&&r.x+r.w<=v.x+v.w&&r.y+r.h<=v.y+v.h;

// Only the overlay is displaced. The actor/loot anchor, sprite and simulation
// coordinates stay unchanged. A small spatial grid bounds dense-frame work.
class Occupancy {
 constructor(){this.cells=new Map();this.checks=0;}
 keys(r,gap=0){const keys=[];for(let y=Math.floor((r.y-gap)/CELL_Y);y<=Math.floor((r.y+r.h+gap)/CELL_Y);y++)for(let x=Math.floor((r.x-gap)/CELL_X);x<=Math.floor((r.x+r.w+gap)/CELL_X);x++)keys.push(x+','+y);return keys;}
 add(rect){for(const key of this.keys(rect)){let list=this.cells.get(key);if(!list)this.cells.set(key,list=[]);list.push(rect);}}
 blocked(rect){const seen=new Set();for(const key of this.keys(rect,GAP))for(const other of this.cells.get(key)||[]){if(seen.has(other))continue;seen.add(other);this.checks++;if(overlaps(rect,other,GAP))return true;}return false;}
}

function offsets(c){
 const step=c.h+GAP*2,up=c.kind==='drop'?1:-1,out=[[0,0]];
 for(let i=1;i<=3;i++)out.push([0,up*step*i]);
 for(const dx of [-(c.w/2+12),c.w/2+12])for(const dy of [0,up*step,up*step*2])out.push([dx,dy]);
 if(c.kind!=='actor')for(let i=1;i<=3;i++)out.push([0,-up*step*i]);
 // High-priority hit/target information gets a wider last-resort search.
 if(c.important||c.kind==='drop')for(const dx of [-c.w-12,c.w+12])for(const dy of [0,-step,step,-step*2,step*2])out.push([dx,dy]);
 return out;
}

export function layoutWorldLabels(candidates,viewport,obstacles=[],state=new Map()){
 const grid=new Occupancy(),placed=[],hidden=[],active=new Set();
 for(const r of obstacles)grid.add(r);
 const sorted=[...candidates].sort((a,b)=>(b.priority||0)-(a.priority||0)||(a.order||0)-(b.order||0)||String(a.id).localeCompare(String(b.id)));
 for(const c of sorted){
  active.add(c.id);const signature=c.signature??c.w+':'+c.h,old=state.get(c.id);
  const choices=old?.signature===signature?[[old.dx,old.dy],...offsets(c)]:offsets(c);
  let chosen;
  for(const [dx,dy]of choices){
   const rect={x:c.x-c.w/2+dx,y:c.y+dy,w:c.w,h:c.h};
   // Avoid clamping a distant label onto the screen edge. Near-edge labels
   // may shift horizontally, but retain their world-relative vertical anchor.
   if(rect.x<viewport.x&&rect.x+rect.w>viewport.x)rect.x=viewport.x;
   if(rect.x+rect.w>viewport.x+viewport.w&&rect.x<viewport.x+viewport.w)rect.x=viewport.x+viewport.w-rect.w;
   if(!fits(rect,viewport)||grid.blocked(rect))continue;
   chosen={...c,...rect,dx:rect.x-(c.x-c.w/2),dy};break;
  }
  if(chosen){grid.add(chosen);placed.push(chosen);state.set(c.id,{dx:chosen.dx,dy:chosen.dy,signature});}
  else hidden.push(c);
 }
 for(const id of state.keys())if(!active.has(id))state.delete(id);
 return {placed,hidden,checks:grid.checks};
}

// Grouping is presentation only: retain every original drop ID/instance.
// A selected pickup or missing main-quest item represents its cell first.
export function groupGroundLabels(entries,{lootingId=null,needed=new Set(),itemFor=()=>null}={}){
 const cells=new Map(),rank=g=>g.id===lootingId?1000:needed.has(g.itemId)?500:g.kind==='gold'?0:Object.keys(g.fieldOverrides||{}).length||g.name?100:50;
 for(const g of entries){if(g.quantity<=0)continue;const key=g.x+','+g.y;let list=cells.get(key);if(!list)cells.set(key,list=[]);list.push(g);}
 return [...cells].map(([key,list])=>{const sorted=[...list].sort((a,b)=>rank(b)-rank(a)||String(a.id).localeCompare(String(b.id))),entry=sorted[0];return {key,entry,entries:list,item:itemFor(entry),priority:rank(entry)};});
}

export function groundLabelHit(layout,point,entries){
 const hit=layout?.groundHits?.find(r=>containsPoint(r,point));
 return hit?entries.find(g=>g.id===hit.dropId&&g.quantity>0):null;
}
