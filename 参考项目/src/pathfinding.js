const DIRECTIONS=[[0,-1],[1,0],[0,1],[-1,0],[1,-1],[1,1],[-1,1],[-1,-1]];

// BFS starts on a rounded tile. An empty route must still finish the short
// remaining step when the actor is physically between tile centers.
export function finishEmptyPath(path,position,walkable){
 if(path?.length!==0)return path;
 const start={x:Math.round(position.x),y:Math.round(position.y)};
 return Math.hypot(position.x-start.x,position.y-start.y)>1e-8&&walkable(start.x,start.y)?[start]:path;
}

// Search the player's connected area. If the requested destination is blocked
// or disconnected, choose its closest reachable tile; BFS breaks ties by steps.
export function findNearestPath(map,position,target,walkable,{range=0,canStop=()=>true,throughPortals=false}={}){
 const {width,height}=map,sx=Math.round(position.x),sy=Math.round(position.y);
 if(!Number.isFinite(target.x)||!Number.isFinite(target.y)||sx<0||sy<0||sx>=width||sy>=height)return null;
 const start=sx*height+sy,parents=new Int32Array(width*height),queue=new Int32Array(width*height),portals=throughPortals?new Map():null,jumps=throughPortals?new Map():null;
 // NPC navigation may cross the original same-map house entrances. These
 // edges are route metadata; they must never become ordinary walking steps.
 const seenPortals=throughPortals?new Set():null;
 if(throughPortals)for(const portal of map.portals||[]){
  const key=portal.x*height+portal.y;if(seenPortals.has(key))continue;seenPortals.add(key);
  const id=portal.target==='当前地图'?map.id:portal.target?.split(' ')[0];
  if(id!==map.id||![portal.x,portal.y,portal.targetX,portal.targetY].every(Number.isInteger)||portal.x<0||portal.x>=width||portal.y<0||portal.y>=height||portal.targetX<0||portal.targetX>=width||portal.targetY<0||portal.targetY>=height||!walkable(portal.x,portal.y)||!walkable(portal.targetX,portal.targetY))continue;
  portals.set(key,[portal]);
 }
 parents.fill(-2);parents[start]=-1;queue[0]=start;let tail=1,end=-1,best=-1,bestDistance=Infinity;
 const distance=(x,y)=>(x-target.x)**2+(y-target.y)**2;
 const directions=[...DIRECTIONS].sort((a,b)=>distance(sx+a[0],sy+a[1])-distance(sx+b[0],sy+b[1]));
 for(let head=0;head<tail;head++){
  const index=queue[head],x=Math.floor(index/height),y=index%height;
  if(walkable(x,y)){
   const d=distance(x,y);if(d<bestDistance){best=index;bestDistance=d;}
   if(Math.max(Math.abs(x-target.x),Math.abs(y-target.y))<=range&&canStop({x,y})){end=index;break;}
  }
  const exits=portals?.get(index);
  if(exits){for(const portal of exits){const next=portal.targetX*height+portal.targetY;if(parents[next]!==-2)continue;parents[next]=index;jumps.set(next,portal);queue[tail++]=next;}continue;}
  for(const [dx,dy]of directions){
   const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=width||ny>=height)continue;
   const next=nx*height+ny;if(parents[next]!==-2||!walkable(nx,ny))continue;
   if(dx&&dy&&(!walkable(x+dx,y)||!walkable(x,y+dy)))continue;
   parents[next]=index;queue[tail++]=next;
  }
 }
 if(end===-1)end=best;if(end===-1)return null;
 const path=[];for(let index=end;parents[index]!==-1;index=parents[index]){const point={x:Math.floor(index/height),y:index%height};if(jumps?.has(index))point.viaPortal=jumps.get(index);path.push(point);}
 return finishEmptyPath(path.reverse(),position,walkable);
}
