import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {findNearestPath} from '../src/pathfinding.js';
import {Combat} from '../src/combat.js';

const makeMap=(width=12,height=12)=>({id:'path-test',width,height,cells:Array.from({length:width*height},()=>[0,0,0,0]),spawns:[]});
const block=(map,x,y)=>map.cells[x*map.height+y][1]=-2;
const combat=(map,start)=>{const c=new Combat({hp:25,mp:5,class:'战士',level:1,skills:[],equipment:{},inventory:[],gold:0,base:{hp:25,mp:5,capacity:25,attack:[0,0],tao:[0,0],magic:[0,0],defense:[0,0],magicDefense:[0,0]}},{monsters:[],items:[],skills:{records:[]},itemNames:new Map()});c.enter(map,start);return c;};
function assertRoute(c,start,target){
 const path=findNearestPath(c.map,start,target,(x,y)=>c.walkable(x,y));assert.notEqual(path,null);let previous=start;
 for(const p of path){assert.ok(c.walkable(p.x,p.y));const dx=p.x-previous.x,dy=p.y-previous.y;assert.ok(Math.max(Math.abs(dx),Math.abs(dy))===1);if(dx&&dy){assert.ok(c.walkable(previous.x+dx,previous.y));assert.ok(c.walkable(previous.x,previous.y+dy));}previous=p;}
 // Independent flood fill proves that no tile in this connected area is closer.
 const queue=[start],seen=new Set([start.x+','+start.y]);let minimum=Infinity;
 for(let i=0;i<queue.length;i++){const p=queue[i];minimum=Math.min(minimum,(p.x-target.x)**2+(p.y-target.y)**2);for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++){if(!dx&&!dy)continue;const n={x:p.x+dx,y:p.y+dy},key=n.x+','+n.y;if(seen.has(key)||!c.walkable(n.x,n.y))continue;if(dx&&dy&&(!c.walkable(p.x+dx,p.y)||!c.walkable(p.x,p.y+dy)))continue;seen.add(key);queue.push(n);}}
 assert.equal((previous.x-target.x)**2+(previous.y-target.y)**2,minimum);return {end:previous,steps:path.length};
}
const checks=[];
let map=makeMap(),c=combat(map,{x:1,y:6});for(let x=4;x<=8;x++)for(let y=4;y<=8;y++)block(map,x,y);
assert.deepEqual(assertRoute(c,{x:1,y:6},{x:6,y:6}).end,{x:3,y:6});checks.push('blocked destination moves to its closest reachable boundary');
map=makeMap();for(let y=0;y<map.height;y++)block(map,4,y);c=combat(map,{x:2,y:5});assert.equal(c.findPath({x:8,y:5},0),null);assert.deepEqual(assertRoute(c,{x:2,y:5},{x:8,y:5}).end,{x:3,y:5});assert.ok(c.moveTo(8,5));while(c.path.length)c.update(.05);assert.deepEqual({x:c.position.x,y:c.position.y},{x:3,y:5});checks.push('walkable but disconnected destination stops on the player side of a wall');
map=makeMap();for(const [x,y]of [[6,5],[5,6],[7,6],[6,7]])block(map,x,y);c=combat(map,{x:2,y:6});assert.equal(c.findPath({x:6,y:6},0),null);assertRoute(c,{x:2,y:6},{x:6,y:6});assertRoute(c,{x:2,y:6},{x:-6,y:30});checks.push('sealed islands, diagonal corners and out-of-map clicks use reachable tiles');
map=makeMap(150,150);c=combat(map,{x:0,y:0});assert.ok(c.moveTo(149,149));assert.equal(c.path.length,149);assert.deepEqual(c.path.at(-1),{x:149,y:149});checks.push('reachable routes beyond the old 8000-node cutoff still reach the destination');
map=makeMap(9,9);for(let y=0;y<9;y++)block(map,4,y);c=combat(map,{x:2,y:4});assert.ok(c.moveTo(6,4));assert.deepEqual(c.path.at(-1),{x:3,y:4});map.cells[4*9+4][1]=0;assert.ok(c.moveTo(6,4));assert.deepEqual(c.path.at(-1),{x:6,y:4});checks.push('NPC map gate changes immediately affect new routes');
map=makeMap(4,4);for(const cell of map.cells)cell[1]=-2;map.cells[1*4+1][1]=0;map.cells[2*4+2][1]=0;c=combat(map,{x:1,y:1});assert.ok(c.moveTo(2,2));assert.deepEqual(c.path,[]);assert.ok(c.approach({x:2,y:2}));assert.deepEqual(c.path,[]);assert.equal(c.canAttackFrom(c.position,{x:2,y:2}),false);assert.equal(c.findPath({x:2,y:2},0),null);checks.push('already at the closest tile stays still and cannot interact across blocked corners');
c.farmType=4;c.targetId='fake';c.autoLoot=true;assert.ok(c.moveTo(-10,-10));assert.equal(c.farmType,null);assert.equal(c.targetId,null);assert.equal(c.autoLoot,false);assert.equal(c.moveTo(NaN,1),false);checks.push('manual fallback cancels farming and invalid coordinates do not create paths');
const result={passed:true,checks};await fs.writeFile('reports/pathfinding-tests.json',JSON.stringify(result,null,2));console.log(result);
