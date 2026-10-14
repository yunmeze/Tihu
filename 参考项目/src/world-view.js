// Keep atlas slices aligned at native resolution, then restore fractional camera motion.
export const WORLD_VIEW={scale:1.6,padding:2,width:473,height:1019};
export function worldView(camera,scale=WORLD_VIEW.scale){
 const x=375/scale-camera.x*48,y=555/scale-camera.y*32,ix=Math.round(x),iy=Math.round(y),p=WORLD_VIEW.padding;
 return {origin:{x:(ix+p)*scale,y:(iy+p)*scale},uv:[(p+ix-x)/WORLD_VIEW.width,1-(p+iy-y)/WORLD_VIEW.height,750/(WORLD_VIEW.width*scale),-1624/(WORLD_VIEW.height*scale)]};
}
