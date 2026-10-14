import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {Combat} from '../src/combat.js';
import {createCharacter} from '../src/character.js';
import {setAction,animationFrame,advanceAnimation} from '../src/animation.js';
import {applyStatus,updateStatuses} from '../src/statuses.js';
import {avatarLayers} from '../src/appearance.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8'));
const content={items:await read('data/items.json'),monsters:await read('data/monsters.json'),skills:await read('data/skills.json'),mapList:[{id:'A00'}]};
content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const results=[],test=(name,fn)=>{fn();results.push({name,passed:true});console.log('PASS',name);};
function setup(){
 const p=createCharacter(content,{});p.hp=p.base.hp=500;p.mp=p.base.mp=500;p.equipment={};
 const c=new Combat(p,content,()=>.5,{},()=>.5,()=>.5);
 c.enter({id:'hurt-fixture',width:12,height:12,cells:Array.from({length:144},()=>[0,0,0,0]),spawns:[{x:6,y:5,monsterId:4,name:'鸡'}]},{x:5,y:5});
 const u=c.units[0];u.hp=1000;u.definition={...u.definition,hp:1000,attack:10,physicalEvade:0,magicEvade:0,freeze:0,burn:0,poison:0,paralysis:0};
 return {p,c,u};
}
function quiet(c){c.units=[];c.stopFarming();}
test('landed physical and magic hits enter hurt in all eight directions, with original delayed three-frame strip',()=>{
 for(const magic of [false,true])for(let d=0;d<8;d++){
  const {p,c,u}=setup();c.position.direction=d;c.position.animationElapsed=.3;const before=animationFrame(c.position),hp=p.hp,clock=c.hitClock;
  c.enemyHit(u,null,{magic});assert.ok(p.hp<hp);assert.equal(c.position.action,'hurt');assert.equal(c.hitClock,clock);assert.equal(animationFrame(c.position),before);quiet(c);
  const samples=[];for(let i=1;i<=20;i++){c.update(.02);if(i%5===0)samples.push({action:c.position.action,frame:animationFrame(c.position)});assert.equal(c.position.x,5);assert.equal(c.position.y,5);}
  assert.deepEqual(samples.slice(0,3).map(s=>s.frame),[225+d*3,226+d*3,227+d*3]);assert.equal(samples[3].action,'idle');
 }
});
test('walk, run, attack and cast retain their action phase and pending strike when hit',()=>{
 for(const action of ['walk','run','attack','cast']){const {p,c,u}=setup();setAction(c.position,action);c.position.animationElapsed=.12;c.position.actionTime=.5;c.heroWindup={remaining:.25,targetId:u.id};const pending=c.heroWindup,position={...c.position};c.enemyHit(u);assert.ok(p.hp<500);assert.deepEqual(c.position,position);assert.equal(c.heroWindup,pending);}
});
test('a repeated hit cannot restart the reaction or extend its recovery',()=>{
 const {c,u}=setup();c.enemyHit(u);advanceAnimation(c.position,.16);const state={...c.position};c.enemyHit(u);assert.deepEqual(c.position,state);quiet(c);for(let i=0;i<12;i++)c.update(.02);assert.equal(c.position.action,'idle');
});
test('both ring slots absorb HP loss but still trigger hurt for physical and magic hits',()=>{
 for(const slot of ['ringLeft','ringRight'])for(const magic of [false,true]){const {p,c,u}=setup();p.equipment[slot]=content.itemNames.get('护身戒指').id;const hp=p.hp,mp=p.mp;c.enemyHit(u,null,{magic});assert.equal(p.hp,hp);assert.ok(p.mp<mp);assert.equal(c.position.action,'hurt');}
});
test('evaded hits produce neither damage nor reaction',()=>{
 for(const magic of [false,true]){const {p,c,u}=setup();c.playerProperties={physicalEvade:100,magicEvade:100};c.enemyHit(u,null,{magic});assert.equal(p.hp,500);assert.equal(c.position.action,'idle');}
});
test('poison, burn and direct HP deductions do not start a hit reaction',()=>{
 for(const name of ['poison','burn']){const {p,c}=setup();applyStatus(p,name,{player:true,frames:100});updateStatuses(c,p,.02,{player:true});assert.ok(p.hp<500);assert.equal(c.position.action,'idle');}const {p,c}=setup();c.hurt(p,5,{player:true});assert.equal(c.position.action,'idle');
});
test('enemy ground-damage packets still use the landed-hit gate',()=>{const {c,u}=setup();c.enemyHit(u,null,{magic:true,continuous:true});assert.equal(c.position.action,'hurt');});
test('reflection bypasses the reaction gate without changing the existing reflection calculation',()=>{const {c,u}=setup();c.playerProperties={physicalEvade:0,reflect:20};c.enemyHit(u);assert.ok(u.hp<1000);assert.equal(c.position.action,'idle');});
test('lethal hit keeps the death action and repeated hits cannot revive or restart it',()=>{const {p,c,u}=setup();p.hp=1;c.enemyHit(u);assert.equal(p.hp,0);assert.equal(c.position.action,'death');advanceAnimation(c.position,.2);const phase=c.position.animationElapsed;c.enemyHit(u);assert.equal(c.position.animationElapsed,phase);});
test('frozen hurt lasts 24 native ticks; paralysis retains the existing paused actor clock',()=>{
 const {p,c,u}=setup();applyStatus(p,'freeze',{player:true,frames:500});c.enemyHit(u);quiet(c);for(let i=0;i<23;i++)c.update(.02);assert.equal(c.position.action,'hurt');assert.equal(animationFrame(c.position),239);c.update(.02);assert.equal(c.position.action,'idle');
 const second=setup();second.c.enemyHit(second.u);quiet(second.c);applyStatus(second.p,'paralysis',{player:true,frames:100});second.c.update(.2);assert.equal(second.c.position.animationElapsed,0);delete second.p.statuses.paralysis;second.c.update(.4);assert.equal(second.c.position.action,'idle');
});
test('movement requested during hurt waits for recovery, then follows the requested route',()=>{
 const {c,u}=setup();c.enemyHit(u);quiet(c);assert.ok(c.moveTo(9,5,{run:false}));for(let i=0;i<19;i++)c.update(.02);assert.equal(c.position.x,5);c.update(.02);assert.equal(c.position.action,'walk');assert.ok(c.position.x>5);for(let i=0;i<180;i++)c.update(.02);assert.equal(c.position.x,9);assert.equal(c.position.y,5);
});
test('automatic retaliation waits until reaction recovery before starting its windup',()=>{
 const {c,u}=setup();c.enemyHit(u);u.attackClock=-100;for(let i=0;i<19;i++)c.update(.02);assert.equal(c.position.action,'hurt');assert.equal(c.heroWindup,null);c.update(.02);assert.equal(c.position.action,'attack');assert.ok(c.heroWindup);
});
test('an attack already winding up still releases once after being hit',()=>{
 const {c,u}=setup();assert.ok(c.select(u.id));c.update(.02);assert.equal(c.position.action,'attack');const pending=c.heroWindup,clock=c.hitClock;c.enemyHit(u);assert.equal(c.heroWindup,pending);assert.equal(c.hitClock,clock);u.attackClock=-100;c.targetId=null;c.counterTargetId=null;c.path=[];for(let i=0;i<36;i++)c.update(.02);assert.equal(c.hitCount,1);
});
test('body, head, weapon and wings use identical hurt indices in all directions',()=>{
 for(let direction=0;direction<8;direction++){const {c,u}=setup();c.position.direction=direction;c.enemyHit(u);for(const t of [.1,.2,.3]){c.position.animationElapsed=t;const layers=avatarLayers({body:1,head:0,weapon:1,wings:1},c.position);assert.equal(layers.length,4);assert.equal(new Set(layers.map(l=>l.index)).size,1);assert.equal(layers[0].index,225+direction*3+Math.round(t*10)-1);}}
});
test('changing map and reviving clear the transient hurt frame',()=>{const {p,c,u}=setup();c.enemyHit(u);c.enter(c.map,{x:3,y:3});assert.equal(c.position.action,'idle');assert.equal(c.position.hurtStartFrame,undefined);p.hp=0;assert.ok(c.revive({x:4,y:4}));assert.equal(animationFrame(c.position),17);});
await fs.mkdir('reports/hero-hurt-20261013',{recursive:true});await fs.writeFile('reports/hero-hurt-20261013/targeted-tests.json',JSON.stringify({passed:true,cases:results.length,results},null,2));console.log({passed:true,cases:results.length});
