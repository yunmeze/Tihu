export const NEARBY_ROW=60,NEARBY_WIDTH=168;
export function nearbyColumn(entries,kind,tab,page=0,selected=null){
 const slots=tab==='战斗'?8:6,pages=Math.max(1,Math.ceil(entries.length/slots));page=Math.max(0,Math.min(page,pages-1));const visible=entries.slice(page*slots,(page+1)*slots);
 if(selected&&!visible.includes(selected)){if(visible.length===slots)visible.pop();visible.push(selected);}const bottom=tab==='战斗'?1316:1020,pager=pages>1?44:0,start=bottom-pager-visible.length*NEARBY_ROW;
 return {page,pages,x:kind==='npc'?14:568,bottom,visible,rows:visible.map((entry,i)=>({entry,x:kind==='npc'?14:568,y:start+i*NEARBY_ROW,w:NEARBY_WIDTH,h:NEARBY_ROW})),pagerY:bottom-40};
}
