// The shipped miniature canvas is 200x200 cells, each rendered as 7x5 pixels.
export function mapViewport(map,position,local=false){
 const width=local?Math.min(36,map.width):map.width,height=local?Math.min(36,map.height):map.height;
 const x=local?Math.max(0,Math.min(map.width-width,position.x+.5-width/2)):0;
 const y=local?Math.max(0,Math.min(map.height-height,position.y+.5-height/2)):0;
 return {x,y,width,height};
}
export function mapMarker(view,position,rect){return {x:rect.x+(position.x+.5-view.x)/view.width*rect.w,y:rect.y+(position.y+.5-view.y)/view.height*rect.h};}
export function fitMinimap(view,x,y,w,h){const ratio=view.width*7/(view.height*5),fw=Math.min(w,h*ratio),fh=fw/ratio;return {x:x+(w-fw)/2,y:y+(h-fh)/2,w:fw,h:fh};}
export function minimapCoverage(view,mini){const x=Math.max(0,view.x),y=Math.max(0,view.y),right=Math.min(view.x+view.width,mini.width/7),bottom=Math.min(view.y+view.height,mini.height/5);return {x,y,width:Math.max(0,right-x),height:Math.max(0,bottom-y)};}
