import {canEnterCell} from './map-flags.js';
export function groundAt(map,x,y){if(x<0||y<0||x>=map.width||y>=map.height)return false;const cell=map.cells[x*map.height+y];if(!cell)return false;if(cell[0])return true;return (map.cells[(x-x%2)*map.height+y-y%2]?.[0]||0)<0;}
export function validLanding(map,point){if(!point||!Number.isFinite(point.x)||!Number.isFinite(point.y))return false;const x=Math.round(point.x),y=Math.round(point.y),cell=map.cells[x*map.height+y];return x>0&&y>0&&x<map.width&&y<map.height&&(groundAt(map,x,y)||cell?.[3]>0)&&canEnterCell(cell[1])&&!map.npcs?.some(n=>!n.removed&&n.x===x&&n.y===y);}
export function resolveLanding(map,player,arrivals,explicit=null){
 // Original scripted arrivals can stand on scenery over an empty floor cell
 // (for example the village house at 138,12). Preserve those legal coordinates.
 if(explicit&&Number.isFinite(explicit.x)&&Number.isFinite(explicit.y)){const x=Math.round(explicit.x),y=Math.round(explicit.y);if(x>0&&y>0&&x<map.width&&y<map.height&&canEnterCell(map.cells[x*map.height+y][1])&&!map.npcs?.some(n=>!n.removed&&n.x===x&&n.y===y))return {x:explicit.x,y:explicit.y};}
 const visit=player.mapVisits?.[map.id],home={x:map.home[0],y:map.home[1]},candidates=[explicit,...(explicit?[]:[visit?.last,visit?.entry,home,...(arrivals?.maps?.[map.id]||[])])].filter(Boolean);
 for(const p of candidates)if(validLanding(map,p))return {x:p.x,y:p.y};
 // Invalid explicit destinations are repaired locally; otherwise fall back to
 // the nearest actual ground around native arrivals rather than the map corner.
 const native=[...(arrivals?.maps?.[map.id]||[])];if(explicit)native.sort((a,b)=>Math.hypot(a.x-explicit.x,a.y-explicit.y)-Math.hypot(b.x-explicit.x,b.y-explicit.y));
 const seeds=explicit?[explicit,...native,home]:[...native,home];
 for(const seed of seeds){const x=Math.max(1,Math.min(map.width-1,Math.round(seed.x)||1)),y=Math.max(1,Math.min(map.height-1,Math.round(seed.y)||1));for(let radius=0;radius<=12;radius++)for(let dx=-radius;dx<=radius;dx++)for(let dy=-radius;dy<=radius;dy++){if(Math.max(Math.abs(dx),Math.abs(dy))!==radius)continue;const p={x:x+dx,y:y+dy};if(validLanding(map,p))return p;}}
 for(let x=1;x<map.width;x++)for(let y=1;y<map.height;y++)if(validLanding(map,{x,y}))return {x,y};
 throw Error('Map has no valid arrival ground: '+map.id);
}
export function rememberMapPosition(player,map,position,{entry=false}={}){if(!validLanding(map,position))return;player.mapVisits||={};const visit=player.mapVisits[map.id]||={};visit.last={x:position.x,y:position.y};if(entry)visit.entry={...visit.last};}
