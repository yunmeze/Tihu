import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {Combat} from '../src/combat.js';
import {createCharacter} from '../src/character.js';
import {difficultyMonster} from '../src/difficulty.js';
import {emitNativeParticle,updateNativeParticles,drawNativeParticles} from '../src/native-particles.js';
import {emitAmbientParticles,AMBIENT_PARTICLES} from '../src/ambient-particles.js';
import {emitGroundParticles} from '../src/ground-particles.js';
import {updateMonsterRebirth} from '../src/monster-rebirth.js';
import {spawnUnit} from '../src/monster-spawning.js';
import {continueDefense,updateDefense} from '../src/defense.js';
import {Batch} from '../src/batch.js';

const dir='reports/restoration-20261013',read=async f=>JSON.parse(await fs.readFile(f,'utf8')),checks=[],check=(name,fn)=>{fn();checks.push(name);},near=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const content={};for(const name of ['items','monsters','skills','permanent','defense'])content[name]=await read('public/assets/data/'+name+'.json');content.mapList=await read('public/assets/data/maps.json');
content.itemNames=new Map(content.items.map(i=>[i.name,i]));content.monsterNames=new Map(content.monsters.map(i=>[i.name,i]));
const evidence=await read(dir+'/native-source.json');assert.ok(evidence.passed);
for(const row of [{file:evidence.source,sha256:evidence.sourceSha256},...evidence.evidenceFiles])assert.equal(crypto.createHash('sha256').update(await fs.readFile(row.file)).digest('hex'),row.sha256);
checks.push('Original executable and all six aligned native evidence dumps retain their hashes');
const makeParticles=()=>({player:{hp:100,insights:[]},position:{x:20,y:20},particleView:{x:0,y:0},particles:[],ruleFrame:1,visualRandom:()=>.5,random:()=>{throw Error('Visual consumed gameplay RNG');},content});
check('Native particle lifetimes, cloud phase increments and offscreen pre-aging',()=>{
 for(const [type,ticks]of [[5,48],[6,42],[7,51],[9,282],[20,511],[21,50],[22,26]]){const c=makeParticles();const p=emitNativeParticle(c,type,{x:0,y:0});for(let i=0;i<ticks-1;i++)updateNativeParticles(c);assert.equal(c.particles.length,1,`type${type}`);updateNativeParticles(c);assert.equal(c.particles.length,0,`expired${type}`);}
 const c=makeParticles(),p=emitNativeParticle(c,20,{x:40,y:0});assert.deepEqual([p.stage,p.alpha,p.size],[2,255,3]);for(let i=0;i<270;i++)updateNativeParticles(c);assert.equal(c.particles.length,1);updateNativeParticles(c);assert.equal(c.particles.length,0);
});
check('Native cloud maps and cadence, no generic weather, bounded visual-only pool',()=>{
 assert.deepEqual(AMBIENT_PARTICLES,evidence.ambient);
 for(const [name,n,type]of [['天界-天路',150,9],['天界-三明界',100,20],['天界-轮回',100,20],['海曦村',0,0]]){const c=makeParticles();c.map={name};for(let i=1;i<=300;i++){c.ruleFrame=i;emitAmbientParticles(c);}assert.equal(c.particles.length,n);assert.ok(c.particles.every(p=>p.type===type));}
 const c=makeParticles();for(let i=0;i<1100;i++)emitNativeParticle(c,21,c.position);assert.equal(c.particles.length,1024);
});
check('Equipment ground effects require insight, proper rarity and immutable instance attributes',()=>{
 const weapon=content.itemNames.get('木剑'),c=makeParticles();c.groundItems=[{id:'a',kind:'item',x:20,y:20,itemId:weapon.id,quantity:1,fieldOverrides:{37:12}},{id:'b',kind:'item',x:22,y:20,itemId:weapon.id,quantity:1,fieldOverrides:{37:17,24:2}}];const before=JSON.stringify(c.groundItems);
 for(let i=0;i<60;i++)emitGroundParticles(c);assert.equal(c.particles.length,0);c.player.insights[4]=1;
 for(let i=0;i<60;i++)emitGroundParticles(c);assert.equal(c.particles.filter(p=>p.type===5).length,3);assert.equal(c.particles.filter(p=>p.type===21).length,6);assert.equal(c.particles.filter(p=>p.type===22).length,1);
 const glyph=c.particles.find(p=>p.type===22);near(glyph.x,22.5);near(glyph.y,20+25/32);near(glyph.angle,180);near(glyph.dx,-10);
 assert.equal(JSON.stringify(c.groundItems),before);c.groundItems.splice(0,2);c.particles=[];for(let i=0;i<100;i++)emitGroundParticles(c);assert.equal(c.particles.length,0);
});
const data1=await read('public/assets/sprites/Data1/index.json'),data8=await read('public/assets/sprites/Data8/index.json');
check('Source frames, rotation pivots, cloud crop offsets, tint and opacity draw correctly',()=>{
 const c=makeParticles();for(const type of [5,7,9,20,21,22])emitNativeParticle(c,type,{x:0,y:0});const calls=[];
 drawNativeParticles({combat:c,camera:{x:0,y:0},packs:new Map([['Data1',data1],['Data8',data8]]),mapPoint:()=>({x:300,y:400}),worldScale:1,batch:{frame(...args){calls.push(['frame',...args]);},rotatedFrame(...args){calls.push(['rotated',...args]);}}});
 assert.deepEqual(calls.map(r=>r[2]),[34,36,7,8,34,11]);near(calls[2][3],210);near(calls[2][4],340);near(calls[3][3],120);near(calls[3][4],220);assert.deepEqual(calls[0].at(-1),[0,0]);assert.equal(calls.at(-1).at(-1),null);
 const texture={},b=new Batch({textureNow:()=>texture});b.begin();b.rotatedFrame(data1,34,100,200,1,1,0,.5,'#ff0000',[0,0]);const l=b.layers[0];near(l.p[0],100+data1.frames[34].crop[0]);assert.deepEqual(l.color.slice(0,3),[1,0,0]);assert.equal(l.alpha[0],.5);b.dispose();
});
const flat={id:'A00',name:'test',width:80,height:80,npcs:[],spawns:[{name:'明阳守卫',monsterId:349,x:40,y:40}],cells:Array.from({length:6400},()=>[1,0,0,0])};
function makeCombat(mode=0,map=flat,options={}){const p=options.player||createCharacter(content,{});p.gameMode=mode;p.base.hp=p.hp=100000;const c=new Combat(p,content,()=>.99,{},()=>.99,()=>.99,options.pets||[],options.defense||null,options.challenge||null);c.enter(structuredClone(map),{x:42,y:40});return c;}
check('Guard rebirth is exact-name, once per spawn, with original 30% HP and 70% restoration pool',()=>{
 for(const mode of [0,1,2]){const c=makeCombat(mode),u=c.units[0],base=u.definition;u.statuses={poison:{frames:100,power:1,source:'player'}};c.targetId=u.id;c.hurt(u,u.hp);assert.ok(u.alive);assert.ok(u.reborn);assert.equal(u.hp,Math.round(base.hp*.3));assert.equal(u.rebirthRecovery,Math.round(base.hp*.7));assert.equal(u.definition.hp,base.hp);assert.equal(u.definition.attackKind,22);assert.equal(u.definition.vision,5);near(u.definition.speed,base.speed+.2);assert.equal(u.definition.defense,base.defense+10);assert.equal(u.definition.magicDefense,base.magicDefense+5);assert.equal(u.definition.attack,base.attack-15);assert.equal(c.player.experience,0);assert.equal(c.groundItems.length,0);assert.ok(!c.player.bossTimers?.[20]);assert.equal(c.targetId,u.id);assert.equal(c.particles[0].frame,36);assert.ok(u.statuses.poison);assert.equal(c.artRevision,1);
  const hp=u.hp;for(let i=0;i<50;i++)updateMonsterRebirth(u);assert.equal(u.hp,hp+150);assert.equal(u.rebirthRecovery,Math.round(base.hp*.7)-150);c.monsterStrike(u);assert.ok(c.projectiles.some(p=>[47,49].includes(p.type)));
  c.hurt(u,u.hp);assert.equal(u.alive,false);assert.equal(c.player.bossTimers[20],2600);assert.equal(u.action,'death');const rewards=JSON.stringify([c.player.experience,c.groundItems,c.player.bossTimers]);c.kill(u);assert.equal(JSON.stringify([c.player.experience,c.groundItems,c.player.bossTimers]),rewards);
  c.player.bossTimers[20]=0;u.respawnAt=c.elapsed;c.update(.02);assert.ok(u.alive);assert.equal(u.reborn,false);assert.equal(u.definition,base);assert.equal(u.hp,base.hp);assert.equal(u.rebirthRecovery,undefined);
 }
 for(const name of ['明阳守卫『终极』','明阳守卫-攻城']){const map=structuredClone(flat);map.spawns[0].name=name;const c=makeCombat(0,map);c.hurt(c.units[0],c.units[0].hp);assert.equal(c.units[0].alive,false);assert.equal(c.units[0].reborn,undefined);}
});
check('Guard restoration respects 50Hz across browser frame rates; pet kill credit only on final death',()=>{
 for(const hz of [30,50,60,120]){const c=makeCombat(),u=c.units[0];c.hurt(u,u.hp);u.definition={...u.definition,regenFrames:0,vision:0,speed:0};const hp=u.hp;for(let i=0;i<hz;i++)c.update(1/hz);assert.equal(u.hp,hp+150);}
 const c=makeCombat(),u=c.units[0],pet=spawnUnit(c,content.monsterNames.get('召唤骷髅'),{x:35,y:40},{summoned:true,summonSkill:'召唤骷髅',petLevel:1,petKills:0});c.hurt(u,u.hp,{source:pet.id});assert.equal(pet.petKills,0);c.hurt(u,u.hp,{source:pet.id});assert.equal(pet.petKills,1);
});
const arena=await read('public/assets/maps/E30.json'),defenseMap=await read('public/assets/maps/J30.json');
check('All difficulty and cleared-cycle challenge saves keep scaled full/damaged/dead enemies',()=>{
 for(const mode of [0,1,2])for(const clearCount of [0,1]){const p=createCharacter(content,{});p.gameMode=mode;p.clearCount=clearCount;const c=new Combat(p,content,()=>.99);c.pendingChallenge={kind:'time',origin:{map:'A00',x:40,y:40}};c.enter(structuredClone(arena),{x:15,y:25});c.challenge.frames=999;c.units[1].hp--;c.kill(c.units[2],{reward:false});const saved=c.saveChallenge(),next=makeCombat(mode,arena,{challenge:saved,player:structuredClone(p)});assert.equal(next.challenge.frames,999);assert.equal(next.units[0].hp,c.units[0].hp);assert.equal(next.units[1].hp,c.units[1].hp);assert.equal(next.units[2].alive,false);
  const invalid=structuredClone(saved);invalid.originals[0].hp=difficultyMonster(content.monsterNames.get(arena.spawns[0].name),p).hp+1;assert.equal(makeCombat(mode,arena,{challenge:invalid,player:structuredClone(p)}).challenge.frames,0);
 }
});
check('High-difficulty defense reload retains wave, enemy HP and unscaled friendly flags',()=>{
 for(const mode of [0,1,2]){const c=makeCombat(mode,defenseMap);assert.ok(c.runScript(c.map.loadScript).applied);assert.ok(continueDefense(c));for(let i=0;i<150&&!c.units.some(u=>u.siege);i++)updateDefense(c,1);const enemy=c.units.find(u=>u.siege);assert.ok(enemy);const flag=c.units.find(u=>u.defenseFlag);assert.equal(flag.definition.hp,content.monsterNames.get('战旗').hp);flag.hp-=25;const saved=c.saveDefense(),next=makeCombat(mode,defenseMap,{defense:saved,player:structuredClone(c.player)});assert.ok(next.runScript(next.map.loadScript).applied);assert.equal(next.defense.cursor,c.defense.cursor);assert.equal(next.units.find(u=>u.siege).hp,enemy.hp);assert.equal(next.units.find(u=>u.id===flag.id).hp,flag.hp);assert.equal(next.units.find(u=>u.siege).definition.hp,enemy.definition.hp);}
});
await fs.writeFile(dir+'/rules.json',JSON.stringify({passed:true,checks},null,2));console.log({passed:true,checks:checks.length});
