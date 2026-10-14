import {MAP_GROUPS,mapObjectFrames} from './map-effects.js';
export {MAP_GROUPS} from './map-effects.js';
function rectangle(frame,object=false){
 if(!frame||frame.rect[2]<=0||frame.rect[3]<=0)return null;
 const left=frame.crop[0],top=frame.crop[1]+(object?32-frame.original[1]:0);
 return {left,top,right:left+frame.rect[2],bottom:top+frame.rect[3]};
}
const rectangleCache=new WeakMap();
const resourceKeys=Object.entries(MAP_GROUPS).map(([type,name])=>[type,'Map/Res/'+name]).concat([[8,'Data4']]);
function mapResources(packs){
 // Resolve source identities once per scan, rather than building resource
 // keys for every candidate tile. Late map-pack loads still invalidate tiles.
 const objects=[];for(const [type,key]of resourceKeys)objects[type]=packs.get(key);
 return {small:packs.get('Map/Res/FloorSmall'),big:packs.get('Map/Res/FloorBig'),objects};
}
function cellRectangles(cell,packs,resources){
 const floorPack=cell[0]<0?resources.big:resources.small,objectPack=resources.objects[cell[2]];
 const cached=rectangleCache.get(cell);if(cached&&cached.floorPack===floorPack&&cached.objectPack===objectPack&&cached.floor===cell[0]&&cached.type===cell[2]&&cached.index===cell[3])return cached.rectangles;
 const floor=cell[0],frames=mapObjectFrames(cell,packs),rects=frames.map(({frame,top})=>({left:frame.crop[0],top:frame.crop[1]+top,right:frame.crop[0]+frame.rect[2],bottom:frame.crop[1]+top+frame.rect[3]}));
 const object=rects.length?{left:Math.min(...rects.map(r=>r.left)),top:Math.min(...rects.map(r=>r.top)),right:Math.max(...rects.map(r=>r.right)),bottom:Math.max(...rects.map(r=>r.bottom))}:null;
 const rectangles={floor:rectangle(floor&&floorPack?.frames[Math.abs(floor)]),object};rectangleCache.set(cell,{floorPack,objectPack,floor:cell[0],type:cell[2],index:cell[3],rectangles});return rectangles;
}
// A tree/roof is anchored at its bottom cell. Its visible crown can extend many
// rows above that cell, including when the anchor itself is below the screen.
export function mapSpriteExtents(map,packs){
 const extents={left:0,top:0,right:48,bottom:32},resources=mapResources(packs);
 for(const cell of map.cells)for(const rect of Object.values(cellRectangles(cell,packs,resources)))if(rect){extents.left=Math.min(extents.left,rect.left);extents.top=Math.min(extents.top,rect.top);extents.right=Math.max(extents.right,rect.right);extents.bottom=Math.max(extents.bottom,rect.bottom);}
 return extents;
}
export function visibleMapCells(map,packs,view,extents,{padding=1}={}){
 const minX=Math.max(0,Math.floor((-padding-view.x-extents.right)/48)),maxX=Math.min(map.width-1,Math.ceil((view.width+padding-view.x-extents.left)/48)),minY=Math.max(0,Math.floor((-padding-view.y-extents.bottom)/32)),maxY=Math.min(map.height-1,Math.ceil((view.height+padding-view.y-extents.top)/32)),cells=[],resources=mapResources(packs);
 const intersects=(rect,x,y)=>!!rect&&view.x+x*48+rect.right>-padding&&view.y+y*32+rect.bottom>-padding&&view.x+x*48+rect.left<view.width+padding&&view.y+y*32+rect.top<view.height+padding;
 for(let x=minX;x<=maxX;x++)for(let y=minY;y<=maxY;y++){
  const cell=map.cells[x*map.height+y],rects=cellRectangles(cell,packs,resources),floorVisible=intersects(rects.floor,x,y),objectVisible=intersects(rects.object,x,y);
  if(floorVisible||objectVisible)cells.push({x,y,cell,floorVisible,objectVisible});
 }
 return cells;
}
