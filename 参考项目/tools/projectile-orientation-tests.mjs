import assert from 'node:assert/strict';import fs from 'node:fs/promises';
import {effectRotation,effectFrame,ROTATED_PROJECTILE_TYPES,EFFECT_DIRECTIONS} from '../src/effect-animation.js';
import {launchProjectile,effectPack,impactType} from '../src/projectiles.js';
import {Combat} from '../src/combat.js';import {LPApp} from '../src/game.js';import {Batch} from '../src/batch.js';
const read=async path=>JSON.parse(await fs.readFile(path,'utf8')),source=await read('reports/native-projectile-orientation-source.json'),checks=[],close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
assert.deepEqual([...ROTATED_PROJECTILE_TYPES].sort((a,b)=>a-b),source.rules.rotatedProjectileTypes);
const vectors=[[0,-4],[4,-4],[4,0],[4,4],[0,4],[-4,4],[-4,0],[-4,-4],[5,-2],[2,5],[-5,2],[-2,-5]],packs=new Map();
for(const type of ROTATED_PROJECTILE_TYPES){const id=effectPack(type),pack=await read('public/assets/sprites/'+id+'/index.json');packs.set(id,pack);
 for(const [dx,dy]of vectors){const c={nextEffectId:0,effectVersion:0,projectiles:[],direction:Combat.prototype.direction};launchProjectile(c,{from:{x:8,y:8},to:{x:8+dx,y:8+dy},type,onHit(){}});const p=c.projectiles[0],angle=effectRotation(p),speed=Math.hypot(p.vx*48,p.vy*32);close(speed,350);close(Math.sin(angle),dx*48/Math.hypot(dx*48,dy*32));close(-Math.cos(angle),dy*32/Math.hypot(dx*48,dy*32));assert.equal(p.direction,c.direction({x:8,y:8},{x:8+dx,y:8+dy}));assert.equal(p.travel,0);assert.equal(p.source,'player');assert.ok(effectFrame(p,pack)>=1&&effectFrame(p,pack)<pack.frames.length);}
}
checks.push('all 15 native heading-driven flight types align their forward vector to screen-space velocity for eight directions and four oblique headings; flight speed/frame groups are preserved');
close(effectRotation({type:14,vx:1,vy:-1}),Math.atan2(48,32));assert.ok(Math.abs(effectRotation({type:14,vx:1,vy:-1})-Math.PI/4)>.1);
checks.push('48:32 grid diagonal is projected to 56.31 degrees from up instead of 45 degrees');
for(const type of Object.keys(EFFECT_DIRECTIONS).map(Number))assert.equal(effectRotation({type,vx:2,vy:3}),null);
for(const type of ROTATED_PROJECTILE_TYPES)assert.equal(effectRotation({type:impactType(type),direction:3,age:0}),null);
for(const velocity of [{},{vx:0,vy:0},{vx:NaN,vy:1},{vx:1,vy:Infinity}])assert.equal(effectRotation({type:14,...velocity}),null);
checks.push('eight-direction knife/monster sheets, stationary impact visuals and missing/invalid headings never rotate');
// Exercise actual app rendering and atlas vertex generation, including crop
// placement around the original canvas rather than the cropped rectangle.
const batch=new Batch({textureNow:()=>batch.white}),pack=packs.get('Mgc/6'),app={packs,mapPoint:()=>({x:200,y:300}),worldScale:1.6,batch};
for(let frame=1;frame<pack.frames.length;frame++)for(const [dx,dy]of vectors){const angle=Math.atan2(dx*48,-dy*32),effect={type:14,vx:dx,vy:dy,age:(frame-1)*.08,duration:4,loop:true};batch.begin();LPApp.prototype.drawCombatEffect.call(app,effect);assert.equal(effectFrame(effect,pack),frame);const positions=batch.layers[0].p,f=pack.frames[frame],cx=238.4,cy=268,ox=f.crop[0]-f.original[0]/2,oy=f.crop[1]-f.original[1]/2;close(positions[0],cx+(ox*Math.cos(angle)-oy*Math.sin(angle))*1.6);close(positions[1],1624-cy-(ox*Math.sin(angle)+oy*Math.cos(angle))*1.6);assert.equal(positions.length,18);}
batch.dispose();checks.push('real application draw and atlas geometry rotate all cropped fire frames around the original canvas center without displacement');
let rotated=0,plain=0;const spy={...app,batch:{rotatedFrame(){rotated++;},frame(){plain++;}}};LPApp.prototype.drawCombatEffect.call(spy,{type:14,vx:2,vy:1,age:0,duration:4,loop:true});LPApp.prototype.drawCombatEffect.call(spy,{type:24,age:0,duration:.48});assert.equal(rotated,1);assert.equal(plain,0); // Impact pack deliberately absent from the first map.
spy.packs=new Map([...packs,['Mgc/7',await read('public/assets/sprites/Mgc/7/index.json')],['Mgc/1-1',await read('public/assets/sprites/Mgc/1-1/index.json')]]);LPApp.prototype.drawCombatEffect.call(spy,{type:24,age:0,duration:.48});LPApp.prototype.drawCombatEffect.call(spy,{type:1,direction:3,age:0,duration:.96});assert.equal(rotated,1);assert.equal(plain,2);checks.push('actual app chooses rotation for flight and original anchored drawing for impact and directional sword light');
const result={passed:true,checks,types:ROTATED_PROJECTILE_TYPES.length,headingCases:vectors.length};await fs.writeFile('reports/projectile-orientation-tests.json',JSON.stringify(result,null,2));console.log({passed:true,checks:checks.length,flightTypes:result.types,headingCases:result.headingCases});
