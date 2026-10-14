import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {createCharacter,createNewCharacter,addItem,equip,unequip} from '../src/character.js';
import {HEAD_APPEARANCE_MODEL,normalizeAppearance,characterAppearance} from '../src/appearance.js';
import {readNpcDialogue,applyNpcEffects} from '../src/npc-dialogue.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8'));
const content={items:await read('data/items.json'),skills:await read('data/skills.json'),mapList:await read('data/maps.json')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const checks=[];
for(const job of ['战士','道士','法师'])for(const gender of [0,1]){
 const p=createNewCharacter(content,{class:job,gender});assert.equal(p.equipment.helmet,undefined);assert.equal(p.headStyle,gender);assert.equal(characterAppearance(p,content).head,gender);assert.equal(p.headAppearanceModel,HEAD_APPEARANCE_MODEL);
 for(const value of [undefined,2]){
  const old=JSON.parse(JSON.stringify(p));delete old.headAppearanceModel;if(value===undefined)delete old.headStyle;else old.headStyle=value;
  old.gold=1234;old.experience=3;const before=JSON.parse(JSON.stringify(old));assert.equal(characterAppearance(old,content).head,gender);
  const migrated=createCharacter(content,{version:2,player:old});assert.equal(migrated.headStyle,gender);assert.equal(characterAppearance(migrated,content).head,gender);assert.equal(migrated.gold,before.gold);assert.equal(migrated.experience,before.experience);assert.deepEqual(migrated.equipment,before.equipment);assert.deepEqual(migrated.inventory,before.inventory);assert.deepEqual(migrated.skills,before.skills);
  const once=JSON.stringify(migrated);normalizeAppearance(migrated);assert.equal(JSON.stringify(migrated),once);assert.deepEqual(old,before);
 }
}
checks.push('all three classes and both genders use original hair; raw save previews and missing/forced-HD2 legacy saves migrate without changing progress');
const p=createNewCharacter(content,{class:'法师'}),merchant=(await read('maps/E00.json')).npcs.find(n=>n.name==='斗笠商');
let view=readNpcDialogue(merchant.script,p,content,'A1');assert.equal(p.headStyle,0);assert.ok(view.choices.some(c=>c.action.toUpperCase()==='A1D'));
for(const name of ['鹿茸','鹤仙草','鹿肉'])addItem(p,content.itemNames.get(name).id,3);
view=readNpcDialogue(merchant.script,p,content,'A1D');assert.deepEqual(view.unsupported,[]);assert.ok(applyNpcEffects(p,view.effects,content));assert.equal(p.headStyle,2);assert.equal(p.appearanceUnlocks.hd[2],1);assert.equal(characterAppearance(p,content).head,2);
for(const name of ['鹿茸','鹤仙草','鹿肉'])assert.equal(p.inventory.some(e=>e.itemId===content.itemNames.get(name).id),false);
const owned=JSON.parse(JSON.stringify(p));delete owned.headAppearanceModel;assert.equal(createCharacter(content,{version:2,player:owned}).headStyle,2);
view=readNpcDialogue(merchant.script,p,content,'ZZ');assert.ok(applyNpcEffects(p,view.effects,content));assert.equal(characterAppearance(p,content).head,0);
view=readNpcDialogue(merchant.script,p,content,'A1');assert.ok(applyNpcEffects(p,view.effects,content));assert.equal(characterAppearance(p,content).head,2);
checks.push('native hat purchase consumes its real materials and sets HD2 ownership; old owned hats persist, removal and free rewear still work');
const explicit=createNewCharacter(content,{});view=readNpcDialogue('#CHANGE HD = 2\n#END',explicit,content);assert.ok(applyNpcEffects(explicit,view.effects,content));assert.equal(createCharacter(content,{version:2,player:explicit}).headStyle,2);
for(const gender of [0,1])for(const style of [3,4,5,6]){const old=createNewCharacter(content,{gender});delete old.headAppearanceModel;old.headStyle=style;assert.equal(createCharacter(content,{version:2,player:old}).headStyle,style);}
checks.push('explicit script-selected hats and other old cosmetic styles remain intact');
const bare=createNewCharacter(content,{}),helmet=content.itemNames.get('红樱头盔');bare.level=130;bare.base.attack=[999,999];addItem(bare,helmet.id);assert.ok(equip(bare,content,helmet.id));assert.equal(characterAppearance(bare,content).head,0);assert.ok(unequip(bare,'helmet'));assert.equal(characterAppearance(bare,content).head,0);
checks.push('helmet equipment transfers preserve native stats and never synthesize the unrelated straw-hat sheet');
const result={passed:true,checks,classes:3,genders:2};await fs.writeFile('reports/head-appearance-tests.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
