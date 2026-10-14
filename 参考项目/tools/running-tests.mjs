import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {Combat,COMBAT_RULES} from '../src/combat.js';
import {createNewCharacter} from '../src/character.js';
import {ANIMATIONS,animationFrame} from '../src/animation.js';
import {applyStatus} from '../src/statuses.js';
const read=async n=>JSON.parse(await fs.readFile('public/assets/data/'+n+'.json','utf8'));
const content={items:await read('items'),monsters:await read('monsters'),skills:await read('skills'),mapList:await read('maps')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const directions=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]],checks=[],measurements=[];
const make=()=>{const p=createNewCharacter(content,{}),c=new Combat(p,content,()=>.99,{},()=>.99,()=>.99);c.enter({id:'running',width:64,height:64,cells:Array.from({length:4096},()=>[0,0,0,0]),npcs:[],spawns:[]},{x:32,y:32});return c;};
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
for(const run of [false,true])for(const frozen of [false,true])for(const fps of [30,50,60,120])for(const [dx,dy]of directions){
 const c=make(),speed=(run?3.125:1.5625)*(frozen?.5:1);if(frozen)applyStatus(c.player,'freeze');c.moveTo(32+dx*10,32+dy*10,{run});for(let i=0;i<fps;i++)c.update(1/fps);near(c.position.x,32+dx*speed);near(c.position.y,32+dy*speed);assert.equal(c.position.action,run?'run':'walk');measurements.push({run,frozen,fps,dx,dy,x:c.position.x-32,y:c.position.y-32});
}
checks.push('Eight directions at 30/50/60/120 Hz match native walking/running components; diagonal travel applies both full axes and freeze halves displacement');
let c=make();c.moveTo(42,32,{run:true});c.update(.02);const frames=new Set();for(let i=0;i<30;i++){const elapsed=c.position.animationElapsed,version=c.position.animationVersion;c.moveTo(i%2?41:42,i%3?32:33,{run:true});assert.equal(c.position.animationElapsed,elapsed);assert.equal(c.position.animationVersion,version);c.update(.02);frames.add((animationFrame(c.position)-81)%6);}assert.equal(frames.size,6);
checks.push('Repeated running commands preserve all six original run frames (81–128) and do not restart the clip');
c=make();c.moveTo(42,32,{run:false});for(let i=0;i<20;i++)c.update(.02);let phase=c.position.animationElapsed/.84;c.moveTo(42,32,{run:true});near(c.position.animationElapsed/.6,phase);c.update(.02);phase=c.position.animationElapsed/.6;c.moveTo(42,32,{run:false});near(c.position.animationElapsed/.84,phase);assert.equal(c.position.action,'walk');
checks.push('Switching walk/run preserves the normalized footstep phase while selecting the correct frame group and speed');
c=make();c.moveTo(42,32,{run:true});c.update(.02);applyStatus(c.player,'freeze');const phaseBefore=c.position.animationElapsed;for(let i=0;i<30;i++)c.update(.02);near(c.position.animationElapsed-phaseBefore,.6*5/6);applyStatus(c.player,'paralysis');const still={x:c.position.x,y:c.position.y,t:c.position.animationElapsed};c.update(.2);assert.deepEqual({x:c.position.x,y:c.position.y,t:c.position.animationElapsed},still);
checks.push('Frozen running uses five/six animation timing; paralysis pauses both movement and its animation');
c=make();c.moveTo(34,34,{run:true});for(let i=0;i<100;i++)c.update(.02);assert.deepEqual({x:c.position.x,y:c.position.y},{x:34,y:34});assert.equal(c.position.action,'idle');c.moveTo(42,32,{run:true});c.update(.02);c.stopFarming();assert.equal(c.position.action,'idle');assert.deepEqual(c.path,[]);
checks.push('Running stops exactly at the destination, and explicit cancellation ends run animation without leftover motion');
c=make();c.map.cells[34*64+33][1]=1;c.map.cells[33*64+34][1]=1;c.moveTo(35,35,{run:true});const original=c.path.map(p=>({...p}));let previous={x:32,y:32};for(const p of original){const dx=p.x-previous.x,dy=p.y-previous.y;assert.ok(c.walkable(p.x,p.y));if(dx&&dy){assert.ok(c.walkable(previous.x+dx,previous.y));assert.ok(c.walkable(previous.x,previous.y+dy));}previous=p;}c.groundItems.push({id:'running:loot:1',kind:'item',itemId:0,x:33,y:32,quantity:1});c.path=[{x:33,y:32},{x:34,y:32}];c.update(.5);assert.equal(c.player.inventory.find(e=>e.itemId===0)?.quantity,1);near(c.position.x,33.5625);
checks.push('Running uses the same legal paths and processes crossed loot waypoints while preserving unused frame time');
c=make();c.moveTo(42,32,{run:true});c.update(.02);const before={x:c.position.x,y:c.position.y};c.player.hp=0;assert.equal(c.moveTo(40,40,{run:true}),false);c.update(.2);assert.deepEqual({x:c.position.x,y:c.position.y},before);
checks.push('Dead heroes cannot start or continue running');
assert.equal(COMBAT_RULES.runTilesPerSecond,3.125);assert.equal(ANIMATIONS.hero.run.seconds,.6);
await fs.writeFile('reports/running-tests.json',JSON.stringify({passed:true,checks,measurements},null,2));console.log({passed:true,checks:checks.length,directionalCases:measurements.length});
