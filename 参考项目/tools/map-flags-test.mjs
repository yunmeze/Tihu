import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {MAP_FLAG,mapLayer,canEnterCell,compareWorldObjects} from '../src/map-flags.js';
import {Combat} from '../src/combat.js';
const native=JSON.parse(await fs.readFile('reports/native-map-flags.json','utf8'));
assert.equal(native.passed,true);
for(const m of native.mapping){const layer=m.caption==='底端禁行'||m.caption==='底端'?0:m.caption==='顶端'?2:1;assert.equal(mapLayer(m.flag),layer,m.caption);}

for(const f of [-2,1])assert.equal(mapLayer(f),0);
for(const f of [-1,-3,-4,0,10,28])assert.equal(mapLayer(f),1);
assert.equal(mapLayer(2),2);
for(const f of [-1,-2,-3])assert.equal(canEnterCell(f),false);
for(const f of [-4,0,1,2,10,28])assert.equal(canEnterCell(f),true);
assert.equal(canEnterCell(-3,'monster'),true);assert.equal(canEnterCell(-4,'monster'),false);
assert.equal(canEnterCell(-1,'monster'),false);assert.equal(canEnterCell(-2,'monster'),false);
const sorted=[{name:'front',layer:2,y:0},{name:'actor',layer:1,y:4.25},
 {name:'floor',layer:0,y:100},{name:'wall-behind',layer:1,y:3},
 {name:'wall-ahead',layer:1,y:5}].sort(compareWorldObjects);
assert.deepEqual(sorted.map(o=>o.name),['floor','wall-behind','actor','wall-ahead','front']);
const map=JSON.parse(await fs.readFile('public/assets/maps/A00.json','utf8'));
const c=new Combat({hp:25},{monsters:[]});c.enter({...map,spawns:[]},{x:86,y:52});
const cell=(x,y)=>map.cells[x*map.height+y];
// Original building #86: steps are ground; the roof edge is foreground.
assert.equal(cell(74,62)[1],MAP_FLAG.GROUND);assert.equal(c.walkable(74,62),true);
assert.equal(cell(74,48)[1],MAP_FLAG.FOREGROUND);assert.equal(c.walkable(74,48),true);
assert.equal(cell(74,59)[1],MAP_FLAG.MIDDLE_BLOCKED);assert.equal(c.walkable(74,59),false);
assert.equal(cell(80,61)[1],MAP_FLAG.GROUND_BLOCKED);assert.equal(c.walkable(80,61),false);
assert.equal(cell(93,63)[1],MAP_FLAG.GROUND_BLOCKED);assert.equal(mapLayer(cell(93,63)[1]),0);
assert.equal(c.moveTo(74,59),false);assert.equal(c.moveTo(80,61),false);
assert.equal(c.moveTo(74,62),true);assert.ok(c.path.length>0);
for(const p of c.path)assert.ok(c.walkable(p.x,p.y),'auto path enters a blocked cell');
for(const p of map.portals)assert.equal(c.walkable(p.x,p.y),true);
const result={passed:true,checks:['ground / foot-sorted middle / foreground order','signed player and monster collision','native steps and roof flags','blocked house and railing cells','auto path avoids blocked cells','portals remain traversable']};
await fs.writeFile('reports/map-flags-tests.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
