import fs from 'node:fs/promises';import assert from 'node:assert/strict';import {performance} from 'node:perf_hooks';
import {Combat} from '../src/combat.js';
import {updateMonsterAI} from '../src/monster-ai.js';import {updateMonsterAI as beforeAI} from '../backups/movement-20261013-before/src/monster-ai.js';
import {createCharacter} from '../src/character.js';import {spawnUnit} from '../src/monster-spawning.js';
import {Content} from '../src/content.js';import {browserImage} from '../src/browser-image.js';
// Compare the old and indexed AI against the SAME current combat rules. A
// frozen Combat snapshot also freezes unrelated subsequent restoration work
// (hurt reactions, boss timers, etc.), invalidating this AI-only comparison.
const combatUrl=new URL('../src/combat.js',import.meta.url),source=await fs.readFile(combatUrl,'utf8');
assert.ok(source.includes('import {updateMonsterAI,'));
const beforeSource=(source.replace('import {updateMonsterAI,','import {')+'\nimport {updateMonsterAI} from '+JSON.stringify(new URL('../backups/movement-20261013-before/src/monster-ai.js',import.meta.url).href)+';')
 .replace(/(from\s+['"])(\.[^'"]+)(['"])/g,(_,start,file,end)=>start+new URL(file,combatUrl).href+end);
const {Combat:BeforeCombat}=await import('data:text/javascript;base64,'+Buffer.from(beforeSource).toString('base64'));
const dir='reports/movement-20261013',read=async f=>JSON.parse(await fs.readFile('public/assets/'+f,'utf8')),checks=[];
const content={items:await read('data/items.json'),monsters:await read('data/monsters.json'),skills:await read('data/skills.json'),mapList:await read('data/maps.json')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const flat={id:'ai-compare',width:50,height:50,npcs:[],cells:Array.from({length:2500},()=>[1,0,0,0]),spawns:Array.from({length:40},(_,i)=>({name:content.monsters[[19,152,162][i%3]].name,monsterId:[19,152,162][i%3],x:10+i%8*3,y:10+Math.floor(i/8)*3}))};
function setup(Type,map,seed=123){const random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296),p=createCharacter(content,{});p.base.hp=p.hp=100000;p.autoSkills=[];const c=new Type(p,content,random,{},random,random);c.enter(structuredClone(map),{x:20,y:20});return c;}
const state=c=>JSON.stringify({player:c.player,position:c.position,units:c.units,projectiles:c.projectiles,effects:c.effects,zones:c.zones,events:c.events,particles:c.particles,path:c.path,elapsed:c.elapsed,targetId:c.targetId,farmType:c.farmType,loot:c.groundItems});
for(const fixture of ['A02','arena','friends','invisible','script-spawn']){
 const map=fixture==='A02'?await read('maps/A02.json'):flat,a=setup(BeforeCombat,map),b=setup(Combat,map);
 for(const c of [a,b]){if(fixture==='friends'){for(const [name,x]of [['召唤骷髅',19],['召唤神兽',21]])spawnUnit(c,c.monsterNames.get(name),{x,y:19},{summoned:true,summonSkill:name,petLevel:1});const u=c.units[0];u.siege=true;c.units[1].definition={...c.units[1].definition,behavior:-2};c.units[1].summoned=true;c.units[1].defenseFlag=true;}
  if(fixture==='invisible')c.player.invisible=true;
  if(fixture==='script-spawn'){const u=c.units[0];Object.assign(u,{x:19,y:20,aggro:true,aggroUntil:99,attackWindup:{remaining:.01}});let once=false;const strike=c.monsterStrike;c.monsterStrike=function(...args){strike.apply(this,args);if(!once){once=true;spawnUnit(this,this.monsterNames.get('召唤骷髅'),{x:18,y:20},{summoned:true,summonSkill:'召唤骷髅',petLevel:1});}};}
 }
 for(let i=0;i<300;i++){if(i===70){a.moveTo(24,22);b.moveTo(24,22);}if(i===170){for(const c of [a,b])c.units[2].hp=1;}a.update(.02);b.update(.02);assert.equal(state(b),state(a),`${fixture} tick${i}`);}checks.push(`300-frame original-versus-indexed full state match: ${fixture}`);
}
// Stable ties, dead targets and same-frame state changes are covered by the
// full simulation above. Measure idle crowd work separately from browser FPS.
const benchmark=[];
for(const count of [84,500]){
 const map={...flat,spawns:Array.from({length:count},(_,i)=>({name:'鸡',monsterId:4,x:i%40,y:Math.floor(i/40)}))};
 const old=setup(BeforeCombat,map),current=setup(Combat,map),measure=(fn,c)=>{for(let i=0;i<30;i++)fn(c,.02);const t=performance.now();for(let i=0;i<300;i++)fn(c,.02);return performance.now()-t;};
 const pairs=[];for(let i=0;i<5;i++){if(i%2){const after=measure(updateMonsterAI,current),before=measure(beforeAI,old);pairs.push({before,after});}else{const before=measure(beforeAI,old),after=measure(updateMonsterAI,current);pairs.push({before,after});}}
 assert.equal(state(current),state(old));benchmark.push({count,pairs});
}
checks.push('84/500-monster idle crowds preserve state in alternating paired CPU benchmark');
let closed=0;const contentCache=new Content({assetBase:'',image:async()=>({width:4,height:4,close(){closed++;}})});
const t=await contentCache.texture('sprites/Mon/1/0.png');await contentCache.sync();assert.equal(t.image.width,4);contentCache.releaseTexture('sprites/Mon/1/0.png');await Promise.resolve();assert.equal(closed,1);contentCache.dispose();await Promise.resolve();assert.equal(closed,1);
let finish;const pending=new Content({assetBase:'',image:()=>new Promise(r=>finish=r)}),request=pending.texture('pending.png');pending.dispose();finish({close(){closed++;}});await assert.rejects(request,/disposed/);assert.equal(closed,2);checks.push('Bitmap closes once on eviction, teardown and pending-load cancellation');
const previous={fetch:globalThis.fetch,bitmap:globalThis.createImageBitmap,Image:globalThis.Image};
try{let decoded=0,bitmapCalls=0;globalThis.fetch=async()=>({ok:true,blob:async()=>({})});globalThis.createImageBitmap=async(blob,options)=>{bitmapCalls++;assert.deepEqual(options,{imageOrientation:'none',premultiplyAlpha:'none',colorSpaceConversion:'none'});return {kind:'bitmap'};};assert.equal((await browserImage('image.png')).kind,'bitmap');
 globalThis.Image=class{set src(value){queueMicrotask(()=>this.onload());}async decode(){decoded++;}};globalThis.createImageBitmap=async()=>{throw Error('unsupported');};assert.ok(await browserImage('fallback.png') instanceof globalThis.Image);assert.equal(decoded,1);delete globalThis.createImageBitmap;await browserImage('legacy.png');assert.equal(decoded,2);
 globalThis.createImageBitmap=previous.bitmap||(()=>{});globalThis.fetch=async()=>({ok:false,status:404});await assert.rejects(browserImage('missing.png'),/404/);assert.equal(bitmapCalls,1);checks.push('Async bitmap decode, explicit legacy fallback, and missing-file failures');
}finally{globalThis.fetch=previous.fetch;globalThis.createImageBitmap=previous.bitmap;globalThis.Image=previous.Image;}
await fs.writeFile(dir+'/rules.json',JSON.stringify({passed:true,checks,benchmark},null,2));console.log({passed:true,checks:checks.length,benchmark});
