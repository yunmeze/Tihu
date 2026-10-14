import {monsterWalkable} from './monster-motion.js';
const DIRECTIONS=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];
const key=(x,y)=>x+','+y;
const heuristic=(x,y,target,range)=>{const dx=Math.max(0,Math.abs(x-target.x)-range),dy=Math.max(0,Math.abs(y-target.y)-range),diagonal=Math.min(dx,dy);return diagonal*Math.hypot(48,32)+(dx-diagonal)*48+(dy-diagonal)*32;};
function push(heap,node){let i=heap.length;heap.push(node);while(i){const p=(i-1)>>1;if(heap[p].f<=node.f)break;heap[i]=heap[p];i=p;}heap[i]=node;}
function pop(heap){const first=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let child=i*2+1;if(child+1<heap.length&&heap[child+1].f<heap[child].f)child++;if(heap[child].f>=last.f)break;heap[i]=heap[child];i=child;}heap[i]=last;}return first;}

// Bounded A* for many independent monsters. Terrain and occupancy are read on
// each plan; a failed plan never grants attacks or movement through obstacles.
export function findMonsterPath(map,unit,target,occupied,{range=1,canStop=()=>true,closest=false,maxVisited=4096}={}){
 const start={x:Math.round(unit.x),y:Math.round(unit.y)},height=map.height,startKey=key(start.x,start.y),costs=new Map([[startKey,0]]),parents=new Map(),heap=[];
 push(heap,{...start,k:startKey,g:0,f:heuristic(start.x,start.y,target,range)});let end=null,best=null,bestDistance=Infinity,visited=0;
 while(heap.length&&visited++<maxVisited){
  const node=pop(heap);if(node.g!==costs.get(node.k))continue;
  const distance=(node.x-target.x)**2+(node.y-target.y)**2;if(distance<bestDistance){best=node;bestDistance=distance;}
  if(Math.max(Math.abs(node.x-target.x),Math.abs(node.y-target.y))<=range&&canStop(node)){end=node;break;}
  for(const [dx,dy]of DIRECTIONS){
   const x=node.x+dx,y=node.y+dy,k=key(x,y);if(!monsterWalkable(map,x,y)||occupied.has(k)&&k!==startKey)continue;
   if(dx&&dy&&(!monsterWalkable(map,node.x+dx,node.y)||!monsterWalkable(map,node.x,node.y+dy)||occupied.has(key(node.x+dx,node.y))&&key(node.x+dx,node.y)!==startKey||occupied.has(key(node.x,node.y+dy))&&key(node.x,node.y+dy)!==startKey))continue;
   const g=node.g+Math.hypot(dx*48,dy*32);if(g>=(costs.get(k)??Infinity))continue;costs.set(k,g);parents.set(k,node);push(heap,{x,y,k,g,f:g+heuristic(x,y,target,range)});
  }
 }
 if(!end&&closest)end=best;if(!end)return null;const path=[];while(end.k!==startKey){path.push({x:end.x,y:end.y});end=parents.get(end.k);}return path.reverse();
}
