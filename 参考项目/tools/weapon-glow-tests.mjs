import fs from 'node:fs/promises';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {characterAppearance,weaponGlow,drawAvatarLayers} from '../src/appearance.js';
import {createCharacter,equip,unequip} from '../src/character.js';
import {inventoryKey,mergeItem} from '../src/inventory.js';
const read=async f=>JSON.parse(await fs.readFile(f,'utf8')),content={items:await read('public/assets/data/items.json'),skills:await read('public/assets/data/skills.json'),mapList:await read('public/assets/data/maps.json')},checks=[];
content.itemNames=new Map(content.items.map(item=>[item.name,item]));
const evidence=await read('reports/audit-fixes-20261012/native-weapon-glow.json');assert.ok(evidence.passed);assert.equal(crypto.createHash('sha256').update(await fs.readFile('reports/audit-fixes-20261012/native-weapon-glow.txt')).digest('hex'),evidence.evidenceSha256);
let alpha=0,ascending=false;const appearance={weapon:1,weaponMergeLevel:1};
for(let tick=0;tick<400;tick++){
 if(tick){if(ascending){alpha+=5;if(alpha>255)ascending=false;}else{alpha-=5;if(alpha<50)ascending=true;}}
 assert.equal(weaponGlow(appearance,5,tick/50).opacity,Math.max(0,Math.min(255,alpha))/255);
}checks.push('400 pulse ticks match the native signed-word branches, including turn overshoot');
for(let grade=1;grade<=4;grade++)for(let direction=0;direction<8;direction++){
 const glow=weaponGlow({...appearance,weaponMergeLevel:grade},direction,1.08);assert.equal(glow.color,'#'+(grade*50+55).toString(16)+'3200');assert.equal(glow.opacity,1);assert.equal(glow.offsets.length,direction===0||direction===4?2:4);
}checks.push('All four merge colors and eight directional displacement patterns match native evidence');
for(const bad of [undefined,0,-1,5,NaN])assert.equal(weaponGlow({...appearance,weaponMergeLevel:bad},5,1),null);assert.equal(weaponGlow({...appearance,weapon:null},5,1),null);checks.push('Ordinary, invalid and absent weapons cannot gain a glow');
const packs=new Map(['Weapon/1','Hero/2','Hero/Head/0'].map(id=>[id,{id}])),app={body:2,head:0,...appearance,weaponTint:'#123456'};
for(let direction=0;direction<8;direction++){
 const calls=[],batch={frame(...args){calls.push(args);}};drawAvatarLayers(batch,packs,app,{action:'attack',direction,animationElapsed:.2},100,200,1.6,{tint:'#abcdef',opacity:.45,time:1.08});
 const weapon=calls.filter(c=>c[0].id==='Weapon/1'),normal=weapon.at(-1);assert.equal(normal[5],'#123456');assert.equal(normal[7],.45);assert.ok(weapon.every(c=>c[1]===normal[1]));
 const offsets=weapon.slice(0,-1).map(c=>[+(c[2]-100).toFixed(5),+(c[3]-200).toFixed(5)]);assert.deepEqual(offsets,weaponGlow(app,direction,1.08).offsets.map(([x,y])=>[x*1.6,y*1.6]));assert.equal(calls.findIndex(c=>c===normal)<calls.findIndex(c=>c[0].id==='Hero/2'),direction===0||direction>=5);
}checks.push('Glow uses the same weapon animation frame, foot anchor, depth order and invisibility opacity as its normal pass');
const p=createCharacter(content,{}),id=p.equipment.weapon;unequip(p,'weapon');p.inventory=p.inventory.filter(e=>e.itemId!==id);mergeItem(p.inventory,id,1,{mergeLevel:3,tint:[12,34,56]});const key=inventoryKey(p.inventory.find(e=>e.itemId===id));assert.ok(equip(p,content,key));const restored=createCharacter(content,JSON.parse(JSON.stringify({version:2,player:p})));assert.equal(characterAppearance(restored,content).weaponMergeLevel,3);assert.equal(characterAppearance(restored,content).weaponTint,'#0c2238');unequip(restored,'weapon');assert.equal(weaponGlow(characterAppearance(restored,content),5,1.08),null);checks.push('Real equip/save/load/unequip preserves merge grade and tint without a phantom weapon effect');
await fs.writeFile('reports/audit-fixes-20261012/weapon-glow-tests.json',JSON.stringify({passed:true,checks},null,2));console.log({passed:true,checks:checks.length});
