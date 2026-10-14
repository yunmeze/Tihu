import {ANIMATIONS} from './animation.js';

const cache=new WeakMap();
// Native actor art is positioned relative to a 48 x 32 map cell. Keep a
// single footprint across all directions / walking frames, rather than
// resizing the ground marker with each animation frame or weapon swing.
export function selectionRingBounds(pack){
 if(cache.has(pack))return cache.get(pack);
 const x=24,y=32,padding=10;let left=x,right=x,bottom=y;
 for(const action of ['idle','walk','attack']){
  const clip=ANIMATIONS.monster[action];
  for(let i=clip.base;i<clip.base+clip.count*8;i++){
   const f=pack.frames[i];if(!f||f.rect[2]<=0||f.rect[3]<=0)continue;
   const fx=f.offset[0]+f.crop[0],fy=f.offset[1]+f.crop[1];
   if(action!=='attack'){left=Math.min(left,fx);right=Math.max(right,fx+f.rect[2]);}
   bottom=Math.max(bottom,fy+f.rect[3]);
  }
 }
 const radiusX=Math.max(30,x-left+padding,right-x+padding);
 // The front arc stays below even a large creature's lowest attack frame.
 // Its rear half can be covered naturally by the creature and scenery.
 const bounds={x,y,radiusX,radiusY:Math.max(radiusX*.5,bottom-y+padding)};
 cache.set(pack,bounds);return bounds;
}

export function drawSelectionRing(batch,pack,x,y,scale){
 const r=selectionRingBounds(pack),cx=x+r.x*scale,cy=y+r.y*scale;
 const stroke=(expand,width,color,opacity=1)=>batch.ellipseRing(cx,cy,(r.radiusX+expand)*scale,(r.radiusY+expand)*scale,width*scale,color,opacity);
 stroke(2,6,'#24130b',.95);
 stroke(0,3,'#ed783e');
 stroke(-1,1,'#ffe5aa');
}
