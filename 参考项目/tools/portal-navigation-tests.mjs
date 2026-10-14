import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {findNearestPath} from '../src/pathfinding.js';
import {canEnterCell,MAP_FLAG} from '../src/map-flags.js';

const checks=[],fixture=(width,walls)=>({id:'test',width,height:7,cells:Array.from({length:width*7},(_,i)=>[1,walls.includes(Math.floor(i/7))?MAP_FLAG.GROUND_BLOCKED:0,0,0]),portals:[]});
const search=(map,start,target,throughPortals=true)=>findNearestPath(map,start,target,(x,y)=>x>=0&&x<map.width&&y>=0&&y<map.height&&canEnterCell(map.cells[x*map.height+y][1]),{range:1,throughPortals});
const m=fixture(12,[4,8]);m.portals=[{x:2,y:2,targetX:5,targetY:2,target:'当前地图'},{x:6,y:2,targetX:9,targetY:2,target:'test'}];
const routed=search(m,{x:1,y:2},{x:10,y:3});assert.equal(routed.filter(p=>p.viaPortal).length,2);assert.ok(Math.max(Math.abs(routed.at(-1).x-10),Math.abs(routed.at(-1).y-3))<=1);checks.push('Two separate rooms are crossed through the original same-map portal edges');
const ordinary=search(m,{x:1,y:2},{x:10,y:3},false);assert.ok(ordinary.every(p=>p.x<4&&!p.viaPortal));checks.push('Normal map clicks still stop in the closest reachable local area');
const blocked=structuredClone(m);blocked.cells[5*blocked.height+2][1]=MAP_FLAG.GROUND_BLOCKED;assert.ok(search(blocked,{x:1,y:2},{x:10,y:3}).every(p=>!p.viaPortal));checks.push('A blocked arrival cannot be used as a navigation shortcut');
const other=structuredClone(m);other.portals[0].target='B00 elsewhere';assert.ok(search(other,{x:1,y:2},{x:10,y:3}).every(p=>!p.viaPortal));checks.push('NPC navigation does not use other maps or bypass map unlocks');
const invalid=structuredClone(m);invalid.portals[0].targetX=99;assert.ok(search(invalid,{x:1,y:2},{x:10,y:3}).every(p=>!p.viaPortal));checks.push('Out-of-map portal coordinates are ignored');
const village=JSON.parse(await fs.readFile('public/assets/maps/A00.json','utf8')),npc=village.npcs.find(n=>n.name==='海曦村长'),route=search(village,{x:138,y:12},npc),jump=route.find(p=>p.viaPortal)?.viaPortal;
assert.ok(jump);assert.equal(jump.target,'当前地图');assert.deepEqual([jump.targetX,jump.targetY],[64,72]);assert.ok(Math.max(Math.abs(route.at(-1).x-npc.x),Math.abs(route.at(-1).y-npc.y))<=1);checks.push('The real opening house reaches the village chief through its native exit');
await fs.writeFile('reports/game-recheck-20261012/portal-navigation-tests.json',JSON.stringify({passed:true,checks},null,2));console.log({passed:true,checks:checks.length});
