import assert from 'node:assert/strict';
import {layoutWorldLabels,overlaps,groupGroundLabels,groundLabelHit} from '../src/world-label-layout.js';
import {worldPointer,holdPointer} from '../src/continuous-movement.js';
import {floatingTextLayout} from '../src/combat-text.js';
import fs from 'node:fs/promises';

let cases=0;const results=[],test=(name,fn)=>{fn();cases++;results.push({name,passed:true});console.log('PASS',name);};
const viewport={x:10,y:12,w:730,h:1292};
const label=(id,priority=30,extra={})=>({id,kind:'actor',x:370,y:500,w:180,h:36,priority,...extra});
function separated(result,obstacles=[]){for(const [i,a]of result.placed.entries()){for(const b of result.placed.slice(i+1))assert.ok(!overlaps(a,b,3),a.id+' overlaps '+b.id);for(const b of obstacles)assert.ok(!overlaps(a,b,3),a.id+' overlaps HUD');}}
test('Target and hit remain visible when passive names crowd one point',()=>{
 const list=Array.from({length:24},(_,i)=>label('ordinary:'+i)),result=layoutWorldLabels([...list,label('selected',140,{important:true}),label('damage',120,{kind:'float',important:true,w:70,h:48})],viewport);
 assert.ok(result.placed.some(e=>e.id==='selected'));assert.ok(result.placed.some(e=>e.id==='damage'));assert.ok(result.hidden.length>0);separated(result);
});
test('Drop labels avoid minimap, both nearby columns and belt boundary',()=>{
 const hud=[{x:534,y:14,w:204,h:182},{x:14,y:900,w:168,h:416},{x:568,y:900,w:168,h:416}],list=[label('minimap',80,{kind:'drop',x:620,y:160,w:150,h:34}),label('npc column',80,{kind:'drop',x:140,y:950}),label('enemy column',80,{kind:'drop',x:620,y:990}),label('belt',80,{kind:'drop',x:375,y:1280,w:200,h:58})];
 const result=layoutWorldLabels(list,viewport,hud);assert.equal(result.placed.length,4);separated(result,hud);for(const r of result.placed)assert.ok(r.y+r.h<=1304);
});
test('Fractional camera translation preserves collision offsets',()=>{
 const state=new Map(),list=[label('selected',140),label('other',30)],first=layoutWorldLabels(list,viewport,[],state),next=layoutWorldLabels(list.map(e=>({...e,x:e.x-2.4,y:e.y+1.3})),viewport,[],state);
 for(const old of first.placed){const now=next.placed.find(e=>e.id===old.id);assert.equal(now.dx,old.dx);assert.equal(now.dy,old.dy);assert.ok(Math.abs(now.x-old.x+2.4)<1e-8);assert.ok(Math.abs(now.y-old.y-1.3)<1e-8);}separated(next);
});
test('Floating text still rises on the combat clock without a relayout snap',()=>{
 const e={text:'17',born:2,until:3.05,duration:1.05,kind:'damage'},state=new Map();
 const place=now=>{const q=floatingTextLayout(e,now,{x:370,y:700},-40,1.6);return layoutWorldLabels([{id:'damage',kind:'float',x:q.x,y:q.y,w:60,h:q.size+10,priority:120}],viewport,[],state).placed[0];};
 const first=place(2),later=place(2.5);assert.equal(first.dx,later.dx);assert.equal(first.dy,later.dy);assert.ok(Math.abs(later.y-first.y+38*.5/1.05)<1e-8);
});
test('Crowding search is bounded and does not retain departed labels',()=>{
 const state=new Map(),dense=Array.from({length:240},(_,i)=>label('name:'+i)),result=layoutWorldLabels(dense,viewport,[],state);assert.ok(result.checks<30000);separated(result);
 layoutWorldLabels([label('new')],viewport,[],state);assert.deepEqual([...state.keys()],['new']);
});
test('Offscreen labels cannot clamp across the viewport onto another actor',()=>{const r=layoutWorldLabels([label('far',30,{x:-700,y:500}),label('near',30,{x:740})],viewport);assert.equal(r.placed.length,1);assert.equal(r.placed[0].id,'near');});
test('Multi-drop grouping preserves all IDs, quantities and affixes',()=>{
 const entries=[{id:'gold',x:2,y:3,kind:'gold',quantity:125},{id:'gear',x:2,y:3,kind:'item',itemId:4,quantity:1,name:'极品木剑',fieldOverrides:{7:7}},{id:'medicine',x:2,y:3,kind:'item',itemId:8,quantity:2},{id:'elsewhere',x:4,y:3,kind:'item',itemId:9,quantity:1}],before=structuredClone(entries);
 const groups=groupGroundLabels(entries);assert.equal(groups.length,2);assert.equal(groups[0].entry.id,'gear');assert.equal(groups[0].entries.length,3);assert.deepEqual(entries,before);
});
test('Missing main-quest material outranks rare equipment in the same cell',()=>{const r=groupGroundLabels([{id:'gear',x:1,y:2,itemId:1,kind:'item',quantity:1,name:'极品'},{id:'quest',x:1,y:2,itemId:2,kind:'item',quantity:1}],{needed:new Set([2])});assert.equal(r[0].entry.id,'quest');});
test('Explicit pickup ID is retained even when it is a gold stack',()=>{const r=groupGroundLabels([{id:'gold',x:1,y:2,kind:'gold',quantity:100},{id:'quest',x:1,y:2,itemId:2,kind:'item',quantity:1}],{needed:new Set([2]),lootingId:'gold'});assert.equal(r[0].entry.id,'gold');});
test('Clicking a moved label resolves an original entry, stale hits are ignored',()=>{
 const entries=[{id:'drop',quantity:1}],layout={groundHits:[{x:100,y:500,w:180,h:58,dropId:'drop'}]};assert.equal(groundLabelHit(layout,{x:180,y:525},entries),entries[0]);assert.equal(groundLabelHit(layout,{x:180,y:525},[]),undefined);assert.equal(groundLabelHit(layout,{x:10,y:10},entries),null);
});
test('A long mouse press on a drop name cannot become continuous world movement',()=>{
 const a={screen:'game',player:{hp:10},combat:{},tab:'战斗',buttons:[],elapsed:0,worldText:{groundHits:[{x:100,y:500,w:180,h:58}]},toLogical:(x,y)=>({x,y})};assert.equal(worldPointer(a,150,520),null);holdPointer(a,'down',150,520,{pointerType:'mouse'});assert.equal(a.heldMove,undefined);assert.deepEqual(worldPointer(a,370,600),{x:370,y:600});
});
await fs.mkdir('reports/world-text-20261013',{recursive:true});await fs.writeFile('reports/world-text-20261013/targeted-tests.json',JSON.stringify({passed:true,cases,results},null,2));console.log({passed:true,cases});
