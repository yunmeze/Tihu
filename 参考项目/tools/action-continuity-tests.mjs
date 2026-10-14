import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {Combat,COMBAT_RULES} from '../src/combat.js';
import {createNewCharacter} from '../src/character.js';
import {ANIMATIONS,animationFrame} from '../src/animation.js';
const read=async name=>JSON.parse(await fs.readFile('public/assets/data/'+name+'.json','utf8'));
const content={items:await read('items'),monsters:await read('monsters'),skills:await read('skills'),mapList:await read('maps')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const make=(skill='基本剑术')=>{
 const p=createNewCharacter(content,{});p.hp=p.base.hp=p.mp=p.base.mp=10000;p.base.accuracy=100;p.base.attack=p.base.magic=[5,5];p.skills=[{name:skill,level:1},{name:'回生术',level:1}];p.activeSkill=skill;
 const c=new Combat(p,content,()=>.99,{},()=>.99,()=>.99);c.enter({id:'continuity',width:40,height:40,cells:Array.from({length:1600},()=>[0,0,0,0]),npcs:[],spawns:[{x:11,y:10,monsterId:4,name:'鸡'},{x:10,y:11,monsterId:4,name:'鸡'}]},{x:10,y:10});
 for(const u of c.units){u.hp=10000;u.definition={...u.definition,hp:10000,speed:0,behavior:-1,vision:0,defense:0,magicDefense:0,physicalEvade:0,magicEvade:0,regenFrames:0};}
 const starts=[],hits=[],hurt=c.hurt.bind(c);c.hurt=(actor,damage,options)=>{if(c.units.includes(actor))hits.push({time:c.elapsed,id:actor.id,frame:animationFrame(c.position),direction:c.position.direction});return hurt(actor,damage,options);};
 const update=c.update.bind(c);c.update=dt=>{const version=c.position.animationVersion;update(dt);if(c.position.animationVersion!==version&&['attack','cast'].includes(c.position.action))starts.push({time:c.elapsed,action:c.position.action,skill:c.position.skill});};return {c,starts,hits};
};
const step=(c,t)=>{for(let i=0;i<Math.round(t/.02);i++)c.update(.02);};
const checks=[],traces=[],near=(a,b,e=.021)=>assert.ok(Math.abs(a-b)<=e,`${a} != ${b}`);
let {c}=make();c.moveTo(25,10,{run:false});step(c,.3);const phase=c.position.animationElapsed,version=c.position.animationVersion;c.moveTo(23,12,{run:false});assert.equal(c.position.action,'walk');assert.equal(c.position.animationElapsed,phase);assert.equal(c.position.animationVersion,version);step(c,.1);near(c.position.animationElapsed,phase+.1,1e-8);
const frames=new Set();for(let i=0;i<30;i++){const elapsed=c.position.animationElapsed;c.moveTo(i%2?24:22,i%3?12:14,{run:false});assert.equal(c.position.animationElapsed,elapsed);step(c,.06);frames.add((animationFrame(c.position)-ANIMATIONS.hero.walk.base)%6);}assert.equal(frames.size,6);
checks.push('repeated movement clicks change only the route and facing; the same walk cycle reaches all six frames without restarting');
const approachPhase=c.position.animationElapsed/.84%1;c.approach({x:30,y:30});assert.equal(c.position.action,'run');near(c.position.animationElapsed/.6,approachPhase,1e-8);assert.ok(c.startFarming(4));assert.equal(c.position.action,'run');c.stopFarming();assert.equal(c.position.action,'idle');
checks.push('NPC approach selects automatic running without resetting footstep phase; farming preserves movement and an explicit stop switches to idle');
for(const skill of ['基本剑术','火球术']){
 const fixture=make(skill);({c}=fixture);c.startFarming(4);c.update(.02);assert.equal(c.position.action,skill==='基本剑术'?'attack':'cast');assert.equal(c.position.animationElapsed,0);assert.equal(c.hitCount,0);step(c,6.2);assert.ok(fixture.starts.length>=4);for(let i=1;i<fixture.starts.length;i++)near(fixture.starts[i].time-fixture.starts[i-1].time,COMBAT_RULES.playerAttackSeconds);traces.push({skill,starts:fixture.starts,hits:fixture.hits});
}
checks.push('a ready hero starts the first melee/cast immediately in reach; every following attack starts at the same native .96-second interval');
let fixture=make();({c}=fixture);c.startFarming(4);step(c,.68);assert.equal(c.hitCount,1);const clock=c.hitClock;c.enemyHit(c.units[0]);assert.equal(c.hitClock,clock);step(c,1.1);near(fixture.starts[1].time-fixture.starts[0].time,COMBAT_RULES.playerAttackSeconds);
for(let i=0;i<120;i++){if(i%5===0)c.enemyHit(c.units[i%2]);c.update(.02);}for(let i=1;i<fixture.starts.length;i++)near(fixture.starts[i].time-fixture.starts[i-1].time,COMBAT_RULES.playerAttackSeconds);traces.push({retaliation:true,starts:fixture.starts});
checks.push('incoming attacks and multiple retaliating targets cannot prime, shorten or restore an old hero attack clock');
fixture=make();({c}=fixture);c.startFarming(4);step(c,.68);c.select(c.units[1].id);step(c,.16);c.stopFarming();c.startFarming(4,c.units[1].id);step(c,.2);assert.equal(fixture.starts.length,2);near(fixture.starts[1].time-fixture.starts[0].time,COMBAT_RULES.playerAttackSeconds);
checks.push('changing target or toggling farming during recovery neither delays the next attack nor bypasses its cooldown');
fixture=make();({c}=fixture);c.startFarming(4);step(c,.2);c.moveTo(20,10,{run:false});assert.equal(c.heroWindup,null);assert.equal(c.position.action,'idle');c.update(.02);assert.equal(c.position.action,'walk');step(c,1.8);assert.equal(c.hitCount,0);Object.assign(c.position,{x:10,y:10});c.startFarming(4);c.update(.02);assert.equal(c.position.action,'attack');assert.equal(c.position.animationElapsed,0);
checks.push('manual movement interrupts the pending swing immediately; cooldown recovers during travel and the next ready attack does not wait again');
fixture=make();({c}=fixture);c.startFarming(4);step(c,.68);c.stopFarming();c.requestSkill('回生术');step(c,.2);assert.equal(c.pendingSkill,'回生术');assert.equal(c.position.action,'idle');step(c,.3);assert.equal(c.pendingSkill,null);assert.equal(c.position.action,'cast');near(fixture.starts[1].time-fixture.starts[0].time,COMBAT_RULES.playerAttackSeconds);
checks.push('queued recovery/summoning casts share the same cooldown as offensive attacks');
fixture=make();({c}=fixture);c.startFarming(4);c.update(.02);c.enter(c.map,{x:10,y:10});for(const u of c.units){u.hp=10000;u.definition={...u.definition,hp:10000,speed:0,behavior:-1,vision:0,regenFrames:0};}c.startFarming(4);c.update(.1);assert.equal(c.position.action,'idle');c.update(10);assert.equal(c.position.action,'attack');assert.equal(c.hitClock,0);step(c,.94);assert.equal(fixture.starts.length,2);step(c,.02);assert.equal(fixture.starts.length,3);near(fixture.starts[2].time-fixture.starts[1].time,COMBAT_RULES.playerAttackSeconds);
checks.push('map entry preserves recent cooldown; a delayed update cannot accumulate extra attacks or trigger a short follow-up burst');
await fs.writeFile('reports/action-continuity-tests.json',JSON.stringify({passed:true,checks,traces},null,2));console.log({passed:true,checks:checks.length});
