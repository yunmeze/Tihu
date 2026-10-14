import fs from 'node:fs/promises';import assert from 'node:assert/strict';
import {characterAppearance,normalizeAppearance,appearancePacks,avatarLayers,avatarBounds,fitAvatar} from '../src/appearance.js';
import {ANIMATIONS,animationFrame} from '../src/animation.js';
import {createCharacter,equip,unequip} from '../src/character.js';
import {readNpcDialogue,applyNpcEffects} from '../src/npc-dialogue.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8'));
const content={items:await read('data/items.json'),skills:await read('data/skills.json'),mapList:await read('data/maps.json')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const packs=new Map(),load=async id=>{if(!packs.has(id))packs.set(id,await read('sprites/'+id+'/index.json'));return packs.get(id);},player=createCharacter(content,{}),starting=characterAppearance(player,content);
assert.deepEqual(starting,{body:2,head:0,weapon:1,wings:null});
let armorChecks=0,weaponChecks=0,frameChecks=0;const emptyFrames=[];
for(const item of content.items.filter(i=>i.type===9&&i.name!=='0'))for(const gender of [0,1]){const a=characterAppearance({...player,gender,equipment:{armor:item.id}},content);assert.equal(a.body,item.appearance[gender]);await load('Hero/'+a.body);armorChecks++;}
for(const item of content.items.filter(i=>i.type===14&&i.name!=='0'))for(const gender of [0,1]){const a=characterAppearance({...player,gender,equipment:{weapon:item.id}},content);assert.equal(a.weapon,item.appearance[0]);await load('Weapon/'+a.weapon);weaponChecks++;}
for(const id of [0,1])await load('Hero/'+id);for(let id=0;id<=6;id++)await load('Hero/Head/'+id);for(let id=1;id<=9;id++)await load('Hero/Cb/'+id);
for(const [id,pack]of packs)for(const [action,clip]of Object.entries(ANIMATIONS.hero))for(let direction=0;direction<8;direction++)for(let phase=0;phase<clip.count;phase++){
 const lead=clip.leadSeconds||0,index=animationFrame({action,direction,animationElapsed:lead+(phase+.01)*(clip.seconds-lead)/clip.count});assert.equal(index,clip.base+direction*clip.count+phase);assert.ok(index<pack.frames.length,id+'/'+index);const f=pack.frames[index];if(!f){emptyFrames.push(id+'/'+index);continue;}assert.ok(pack.pages[f.page],id+'/'+index);assert.ok([...f.rect,...f.offset,...f.crop].every(Number.isFinite),id+'/'+index);frameChecks++;
}
assert.deepEqual(emptyFrames,[]);
const a={...starting,wings:1};for(let direction=0;direction<8;direction++){
 const layers=avatarLayers(a,{action:'idle',direction}),parts=layers.map(l=>l.part),weapon=parts.indexOf('weapon'),wings=parts.indexOf('wings'),body=parts.indexOf('body'),head=parts.indexOf('head');assert.equal(weapon<body,direction===0||direction>=5);assert.equal(wings<body,direction>=3&&direction<=5);assert.ok(head>body);assert.equal(new Set(layers.map(l=>l.index)).size,1);
 const bounds=avatarBounds(packs,layers),box={x:104,y:1138,w:192,h:344,maxScale:4},fit=fitAvatar(bounds,box);assert.ok(bounds.width>0&&bounds.height>0);assert.ok(fit.x+bounds.left*fit.scale>=box.x-1e-7);assert.ok(fit.x+bounds.right*fit.scale<=box.x+box.w+1e-7);assert.ok(fit.y+bounds.top*fit.scale>=box.y-1e-7);assert.ok(fit.y+bounds.bottom*fit.scale<=box.y+box.h+1e-7);
}
// Native hair is sex-dependent, even when HD=0/1; absent armor uses correct sex.
for(const gender of [0,1])for(const headStyle of [0,1])assert.deepEqual(characterAppearance({...player,gender,headStyle,equipment:{}},content),{body:gender,head:gender,weapon:null,wings:null});
for(const gender of [0,1]){const p={...player,gender,headStyle:999,wings:10,equipment:{armor:298,weapon:252}};normalizeAppearance(p);assert.deepEqual(characterAppearance(p,content),{body:gender,head:gender,weapon:null,wings:null});}
for(const type of [7,10,13])for(const item of content.items.filter(i=>i.type===type&&i.name!=='0'))assert.deepEqual(item.appearance,[0,0]);
// Real item transfers and save migration preserve visual state and inventory.
unequip(player,'weapon');assert.equal(characterAppearance(player,content).weapon,null);assert.ok(equip(player,content,298));unequip(player,'armor');assert.equal(characterAppearance(player,content).body,0);assert.ok(equip(player,content,252));player.headStyle=5;player.wings=3;const saved={version:2,player};assert.equal(createCharacter(content,saved).headStyle,5);assert.equal(createCharacter(content,saved).wings,3);delete saved.player.headStyle;delete saved.player.wings;const old=createCharacter(content,saved);assert.equal(old.headStyle,0);assert.equal(old.wings,0);assert.deepEqual(old.equipment,player.equipment);
const script='#CHANGE HD = 4\n#CHANGE CB = 2\n#END',view=readNpcDialogue(script,old,content);assert.deepEqual(view.unsupported,[]);assert.ok(applyNpcEffects(old,view.effects,content));assert.equal(characterAppearance(old,content).head,4);assert.equal(characterAppearance(old,content).wings,2);const before=JSON.stringify(old);assert.equal(applyNpcEffects(old,[{kind:'change',field:'HD',operator:'=',value:8}],content),false);assert.equal(applyNpcEffects(old,[{kind:'change',field:'CB',operator:'+',value:1}],content),false);assert.equal(JSON.stringify(old),before);
assert.equal(appearancePacks(starting).length,3);
const result={passed:true,armorChecks,weaponChecks,packs:packs.size,frameChecks,emptyFrames,directions:8,headStyles:7,wings:9,equipmentRoundtrip:true,genderFallback:true,oldSaveMigration:true,visualStatePersists:true,nativeScriptAssignments:true,unsupportedEquipmentAppearanceTypes:[7,10,13]};await fs.writeFile('reports/appearance-tests.json',JSON.stringify(result,null,2));console.log(result);
