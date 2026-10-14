import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {Combat} from '../src/combat.js';
import {createNewCharacter} from '../src/character.js';
import {ANIMATIONS,animationFrame} from '../src/animation.js';
import {findNearestPath} from '../src/pathfinding.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/data/'+file+'.json','utf8'));
const content={items:await read('items'),monsters:await read('monsters'),skills:await read('skills'),mapList:await read('maps')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const checks=[],make=(start,target,skill='基本剑术')=>{const p=createNewCharacter(content,{class:skill==='基本剑术'?'战士':'法师'});p.hp=p.base.hp=p.mp=p.base.mp=10000;p.base.accuracy=100;p.base.attack=[5,5];p.base.magic=[5,5];p.skills=[{name:skill,level:1}];p.activeSkill=skill;const c=new Combat(p,content,()=>.99,{},()=>.99,()=>.99);c.enter({id:'chase',width:40,height:40,cells:Array.from({length:1600},()=>[0,0,0,0]),npcs:[],spawns:[{...target,monsterId:4,name:'鸡'}]},start);const u=c.units[0];u.hp=10000;u.definition={...u.definition,hp:10000,speed:0,vision:0,regenFrames:0,physicalEvade:0,magicEvade:0,behavior:-1};return c;};
const step=(c,t)=>{for(let i=0;i<Math.round(t/.02);i++)c.update(.02);};
for(const skill of ['基本剑术','火球术'])for(const [dx,dy]of [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]){
 const range=skill==='基本剑术'?1:6,c=make({x:20-dx*.4,y:20-dy*.4},{x:20+dx*range,y:20+dy*range},skill),u=c.units[0];assert.equal(c.canAttackFrom(c.position,u,range),false);assert.deepEqual(c.findPath(u),[{x:20,y:20}]);assert.ok(c.startFarming(4));step(c,5.8);assert.ok(c.hitCount>=2,skill+':'+dx+','+dy);assert.ok(u.hp<10000);assert.equal(c.farmType,4);
}
checks.push('melee and fireball close the sub-tile gap and repeatedly attack at all eight range edges, instead of returning an empty path forever');
let c=make({x:8,y:8.2},{x:9,y:8.2});c.map.cells[8*c.map.height+9][1]=-2;assert.equal(c.lineOfSight(c.position,c.units[0]),true);assert.equal(c.canAttackFrom(c.position,c.units[0]),true);assert.ok(c.startFarming(4));step(c,3);assert.ok(c.hitCount>0);assert.equal(c.position.x,8);assert.equal(c.position.y,8.2);
c=make({x:8,y:8},{x:9,y:9});c.map.cells[8*c.map.height+9][1]=-2;c.map.cells[9*c.map.height+8][1]=-2;assert.equal(c.canAttackFrom(c.position,c.units[0]),false);assert.equal(c.lineOfSight(c.position,c.units[0]),false);
checks.push('fractional actors in the same map row do not invent a diagonal wall corner; truly blocked diagonals remain blocked');
c=make({x:8.6,y:8},{x:15,y:8});c.groundItems.push({id:'gap-loot',kind:'gold',quantity:7,x:9,y:8});assert.ok(c.collect('gap-loot'));assert.deepEqual(c.path,[{x:9,y:8}]);step(c,.4);assert.equal(c.groundItems.length,0);assert.equal(c.player.gold,7);assert.equal(c.position.x,9);
assert.deepEqual(findNearestPath(c.map,{x:8.6,y:8},{x:9,y:8},(x,y)=>c.walkable(x,y)),[{x:9,y:8}]);assert.deepEqual(findNearestPath(c.map,{x:9,y:8},{x:9,y:8},(x,y)=>c.walkable(x,y)),[]);
c.position.x=8.6;assert.ok(c.approach({x:10,y:8}));step(c,.3);assert.equal(c.position.x,9);assert.equal(c.canAttackFrom(c.position,{x:10,y:8}),true);
checks.push('click movement, nearby NPC approach and ground pickup finish the same physical gap without teleporting or consuming an item from a distance');
// Reproduce a target stepping away after an interrupted approach.
c=make({x:8.6,y:8},{x:10,y:8});assert.ok(c.startFarming(4));step(c,2.5);const firstHits=c.hitCount;c.units[0].x=11;assert.equal(c.canAttackFrom(c.position,c.units[0]),false);step(c,3);assert.ok(c.hitCount>firstHits);assert.ok(c.position.x>9);assert.equal(c.targetId,c.units[0].id);
checks.push('the selected moving target is chased again after it leaves reach, even when the player stopped between tile centers');
let seed=491;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};c=make({x:8.6,y:8},{x:10,y:8});Object.assign(c.units[0].definition,{speed:1,behavior:1});c.monsterRandom=random;c.units[0].hp=12;assert.ok(c.startFarming(4));for(let i=0;i<1000&&c.units[0].alive;i++)c.update(.02);assert.equal(c.units[0].alive,false);assert.ok(c.hitCount>=2);const frames=[];
checks.push('an original walking/idle chicken can be pursued and killed with its real motion rules');
for(const skill of ['基本剑术','火球术']){
 c=make({x:8.6,y:8},{x:skill==='基本剑术'?10:15,y:8},skill);const u=c.units[0],releases=[],hits=[],originalHit=c.hurt.bind(c);c.hurt=(actor,damage,options)=>{if(actor===u)hits.push({time:c.elapsed,action:c.position.action,frame:animationFrame(c.position),direction:c.position.direction,projectiles:c.projectiles.length});return originalHit(actor,damage,options);};c.startFarming(4);
 let previous=0;for(let i=0;i<250;i++){c.update(.02);if(c.projectiles.length>previous)releases.push({time:c.elapsed,action:c.position.action,phase:(animationFrame(c.position)-ANIMATIONS.hero.cast.base)%6,hits:c.hitCount});previous=c.projectiles.length;}
 assert.ok(hits.length>=2);if(skill==='基本剑术')for(const h of hits)assert.equal(h.frame,129+h.direction*6+4);else{assert.ok(releases.length>=2);for(const r of releases){assert.equal(r.action,'cast');assert.equal(r.phase,5);}assert.ok(hits[0].time>releases[0].time);assert.ok(hits[0].projectiles>0);}frames.push({skill,releases,hits});
}
checks.push('approach does not change landed-blade timing; fireballs release on the final cast phase and cause damage only after real flight contact');
const result={passed:true,checks,frames,fullNativeCombatEquivalent:false};await fs.writeFile('reports/attack-chase-tests.json',JSON.stringify(result,null,2));console.log({passed:true,checks:checks.length});
