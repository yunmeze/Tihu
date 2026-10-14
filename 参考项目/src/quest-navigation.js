import {mainQuestObjective} from './main-quest.js';

const directions=[[0,-1],[1,0],[0,1],[-1,0],[1,-1],[1,1],[-1,1],[-1,-1]],distances=new WeakMap();
function mapDistances(data,destination){
 let cache=distances.get(data);if(!cache){cache=new Map();distances.set(data,cache);}if(cache.has(destination))return cache.get(destination);
 const reverse=new Map();for(const [id,m]of Object.entries(data.maps))for(const to of [...m.exits,...m.transfers.map(t=>t.target)]){if(!reverse.has(to))reverse.set(to,[]);reverse.get(to).push(id);}
 const result=new Map([[destination,0]]),queue=[destination];for(let i=0;i<queue.length;i++)for(const from of reverse.get(queue[i])||[])if(!result.has(from)){result.set(from,result.get(queue[i])+1);queue.push(from);}cache.set(destination,result);return result;
}
export function questTarget(player,map,units,content,groundItems=[]){
 let objective=mainQuestObjective(player,content);if(!objective)return null;
 if(objective.missing){const ids=new Set(objective.missing.map(n=>content?.itemNames?.get(n)?.id)),drop=groundItems.find(g=>g.kind==='item'&&ids.has(g.itemId));if(drop)return {kind:'loot',dropId:drop.id,point:drop,event:objective.event,label:'拾取'+content.items[drop.itemId].name,objective};}
 // The jade's native page normally performs this return immediately. Old
 // saves already at ET0=28 may instead use Lingyunzi's original travel choice.
 if(objective.event===28&&map.id==='H85')objective={...objective,mapId:'H85',name:'凌云子'};
 if(map.id===objective.mapId){
  if(objective.kind==='npc'){const index=map.npcs.findIndex(n=>n.name===objective.name&&!n.removed);return index<0?null:{kind:'npc',index,event:objective.event,objective,label:'与'+objective.name+'对话'};}
  const matches=units.filter(u=>!u.summoned&&!u.removed&&u.definition.name===objective.name),alive=matches.find(u=>u.alive),unit=alive||matches[0],point=unit||content?.questNavigation?.targets?.[map.id]?.[objective.name];
  return point?{kind:'monster',unitId:alive?.id,monsterId:unit?.definition.id||content?.monsterNames?.get(objective.name)?.id,point,event:objective.event,objective,label:objective.label||(!alive?'等待'+objective.name+'刷新':'寻找'+objective.name)}:null;
 }
 const data=content?.questNavigation;if(!data?.maps[map.id])return null;const distance=mapDistances(data,objective.mapId),current=distance.get(map.id);if(!current)return null;
 const exits=map.portals.filter(p=>{const id=p.target.split(' ')[0].toUpperCase();return distance.get(id)===current-1;});
 const transfers=data.maps[map.id].transfers.filter(t=>distance.get(t.target)===current-1&&map.npcs[t.index]?.name===t.name&&!map.npcs[t.index].removed);
 return exits.length||transfers.length?{kind:'route',portals:exits,transfers,event:objective.event,objective,label:objective.label||'前往'+(data.maps[objective.mapId]?.name||objective.mapId)}:null;
}

// One BFS handles all tiles of an exit, same-map house jumps and native move
// NPCs. Other map exits end the search instead of becoming walking shortcuts.
export function findQuestRoute(map,position,goals,walkable,canStop=()=>true){
 const {width,height}=map,sx=Math.round(position.x),sy=Math.round(position.y);if(sx<0||sy<0||sx>=width||sy>=height||!goals.length)return null;
 const start=sx*height+sy,parents=new Int32Array(width*height),queue=new Int32Array(width*height),jumps=new Map(),portals=new Map(),stops=new Map();parents.fill(-2);parents[start]=-1;queue[0]=start;let tail=1,best=start,bestGoal=goals[0],bestDistance=Infinity,found=null;
 for(const p of map.portals||[]){const key=p.x*height+p.y;if(!portals.has(key))portals.set(key,p);}
 for(const g of goals)for(let dx=-g.range;dx<=g.range;dx++)for(let dy=-g.range;dy<=g.range;dy++){const x=Math.round(g.point.x)+dx,y=Math.round(g.point.y)+dy;if(x<0||y<0||x>=width||y>=height||!canStop({x,y},g))continue;const key=x*height+y;if(!stops.has(key))stops.set(key,g);}
 for(let head=0;head<tail;head++){
  const index=queue[head],x=Math.floor(index/height),y=index%height;if(walkable(x,y)){for(const g of goals){const d=(x-g.point.x)**2+(y-g.point.y)**2;if(d<bestDistance){best=index;bestGoal=g;bestDistance=d;}}const g=stops.get(index);if(g){found={index,goal:g};break;}}
  const portal=portals.get(index);if(portal){const id=portal.target==='当前地图'?map.id:portal.target.split(' ')[0].toUpperCase();if(id.toUpperCase()===map.id.toUpperCase()){const {targetX:nx,targetY:ny}=portal;if(!Number.isInteger(nx)||!Number.isInteger(ny)||nx<0||ny<0||nx>=width||ny>=height||!walkable(nx,ny))continue;const next=nx*height+ny;if(parents[next]===-2){parents[next]=index;jumps.set(next,portal);queue[tail++]=next;}continue;}if(index!==start)continue;}
  for(const [dx,dy]of directions){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=width||ny>=height||!walkable(nx,ny)||dx&&dy&&(!walkable(x+dx,y)||!walkable(x,y+dy)))continue;const next=nx*height+ny;if(parents[next]!==-2)continue;parents[next]=index;queue[tail++]=next;}
 }
 const end=found?.index??best,path=[];for(let i=end;parents[i]!==-1;i=parents[i]){const p={x:Math.floor(i/height),y:i%height};if(jumps.has(i))p.viaPortal=jumps.get(i);path.push(p);}path.reverse();if(!path.length&&Math.hypot(position.x-sx,position.y-sy)>1e-8&&walkable(sx,sy))path.push({x:sx,y:sy});
 const jump=path.findIndex(p=>p.viaPortal),portal=jump>=0?path[jump].viaPortal:null;
 return {goal:found?.goal||bestGoal,reached:!!found,path:jump>=0?path.slice(0,jump):path,portal};
}

export async function followQuestTarget(a,target){
 const c=a.combat;if(!target||a.player.hp<=0||a.changing||a.itemBusy||a.npcBusy||c.story||c.scriptLocked&&target.kind!=='npc')return false;
 a.questTravel=null;a.tab='战斗';a.lastMoveTap=null;a.pendingNpc=null;
 let goals=target.kind==='route'?[...target.portals.map(portal=>({kind:'portal',point:portal,portal,range:0,destination:portal.target.split(' ')[0].toUpperCase()})),...target.transfers.map(t=>({kind:'transfer',point:a.map.npcs[t.index],index:t.index,range:1,destination:t.target}))]:[{...target,point:target.kind==='npc'?a.map.npcs[target.index]:target.point,range:target.kind==='loot'?0:1}];
 if(target.kind==='monster'){const units=a.units.filter(u=>u.alive&&!u.summoned&&!u.removed&&u.definition.name===target.objective.name);if(units.length)goals=units.map(u=>({...target,point:u,unitId:u.id,range:1}));}
 const route=findQuestRoute(a.map,a.hero,goals,(x,y)=>c.walkable(x,y),(p,g)=>g.range===0||c.canAttackFrom(p,g.point));if(!route)return false;
 if(route.portal){a.questTravel={event:target.event,kind:'portal',mapId:a.mapId,destination:a.mapId,portal:route.portal};return c.moveAlong(route.path);}
 const g=route.goal;
 if(!route.reached)return c.moveAlong(route.path);
 if(g.kind==='portal'){a.questTravel={event:target.event,kind:'portal',mapId:a.mapId,destination:g.destination,portal:g.portal};return c.moveAlong(route.path);}
 if(g.kind==='npc'||g.kind==='transfer'){
  if(g.kind==='transfer')a.questTravel={event:target.event,kind:'transfer',mapId:a.mapId,destination:g.destination,index:g.index};
  await a.selectNpc(g.index,{quest:true});return true;
 }
 if(g.kind==='loot')return c.collect(g.dropId);
 a.questTravel={event:target.event,kind:'monster',mapId:a.mapId,monsterId:target.monsterId,unitId:g.unitId};if(!c.moveAlong(route.path)){a.questTravel=null;return false;}updateQuestTravel(a);return true;
}
export function questTransfer(a,index,destination){const q=a.questTravel;return q?.kind==='transfer'&&q.index===index&&q.mapId===a.mapId&&q.destination===destination&&q.event===a.player.events?.[0];}
export function questPortal(a,p){const q=a.questTravel;return q?.kind==='portal'&&q.mapId===a.mapId&&q.portal.x===p.x&&q.portal.y===p.y&&q.portal.target===p.target&&q.event===a.player.events?.[0];}
export function updateQuestTravel(a){
 const q=a.questTravel,c=a.combat;if(!q)return;
 if(a.player.hp<=0||a.screen!=='game'||a.disposed||c.story||c.scriptLocked||a.player.events?.[0]!==q.event){a.questTravel=null;return;}
 if(a.changing||a.npcBusy||a.itemBusy||a.serviceView||a.npcDialogue||a.systemMenu||a.mapOpen||a.gmOpen||a.featureView||a.attributeOpen)return;
 if(q.arrived){a.questTravel=null;a.followFirstQuest().catch(e=>console.error(e));return;}
 if(q.mapId!==a.mapId){a.questTravel=null;return;}
 if(q.kind==='monster'&&!c.path.length&&!c.autoLoot&&!c.lootingId){a.questTravel=null;if(a.units.some(u=>!u.summoned&&!u.removed&&u.definition.id===q.monsterId))c.startFarming(q.monsterId,q.unitId);}
}
