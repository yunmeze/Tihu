import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {BELT_SIZE,isBeltConsumable,putInBelt,returnFromBelt,useBeltItem} from '../src/belt.js';
import {createCharacter,createNewCharacter,addItem} from '../src/character.js';
import {canCarry,carryAmount,carryState} from '../src/native-stats.js';
import {buyItem,transferStorage} from '../src/services.js';
import {readNpcDialogue,applyNpcEffects} from '../src/npc-dialogue.js';
import {Combat} from '../src/combat.js';
const read=async name=>JSON.parse(await fs.readFile('public/assets/data/'+name+'.json','utf8'));
const content={items:await read('items'),skills:await read('skills'),monsters:await read('monsters'),mapList:await read('maps')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const id=name=>content.itemNames.get(name).id,checks=[];
const fillBag=(p,exclude=[])=>p.inventory=content.items.filter(i=>i.name!=='0'&&!exclude.includes(i.id)).slice(0,50).map(i=>({itemId:i.id,quantity:1}));
const fresh=()=>{const p=createNewCharacter(content,{});p.base.capacity=10000;return p;};
const check=(name,run)=>{run();checks.push(name);};
check('Usable restoration, return/teleport scrolls and type-6 packages are eligible; equipment, ores and unsupported effects are rejected',()=>{
 for(const name of ['金创药小','魔法药小','太阳水(小)','鸡蛋','回城卷','海曦村符 A00','金创药小包','回城卷包'])assert.ok(isBeltConsumable(content.itemNames.get(name)));
 for(const name of ['木剑','布衣','铁矿石','人参包','回阳珠(失灵)']){const p=fresh();addItem(p,id(name));const before=JSON.stringify(p);assert.equal(putInBelt(p,content,id(name)).ok,false,name);assert.equal(JSON.stringify(p),before);}
});
check('The whole stack moves out of the bag, frees a displayed slot and preserves drop provenance; incoming matching items refill its slot',()=>{
 const p=fresh();addItem(p,0,3,{dropSources:[{mode:0,quantity:2}]});const slots=carryState(p,content).slots;assert.deepEqual(putInBelt(p,content,0),{ok:true,index:0});assert.equal(p.inventory.length,0);assert.equal(p.belt[0].quantity,3);assert.equal(carryState(p,content).slots,slots-1);assert.equal(carryState(p,content).slots,0);addItem(p,0,2,{dropSources:[{mode:0,quantity:2}]});assert.equal(p.inventory.length,0);assert.equal(p.belt[0].quantity,5);assert.deepEqual(p.belt[0].dropSources,[{mode:0,quantity:4}]);
});
check('Six full slots reject a seventh kind atomically; an existing kind can still merge while its slot remains stable',()=>{
 const p=fresh();for(const [i,name]of ['金创药小','魔法药小','太阳水(小)','鸡蛋','回城卷','金创药小包'].entries()){addItem(p,id(name));assert.equal(putInBelt(p,content,id(name)).index,i);}assert.equal(p.belt.length,BELT_SIZE);addItem(p,1);const before=JSON.stringify(p);assert.equal(putInBelt(p,content,1).ok,false);assert.equal(JSON.stringify(p),before);p.inventory.push({itemId:0,quantity:2});assert.equal(putInBelt(p,content,0).index,0);assert.equal(p.belt[0].quantity,3);
});
check('Quick-use consumes one real item, keeps native gradual/instant effects, and clears the depleted slot',()=>{
 const p=fresh(),c=new Combat(p,content);p.hp=1;p.mp=0;addItem(p,0,2);putInBelt(p,content,0);assert.ok(useBeltItem(c,0).ok);assert.equal(p.hp,1);assert.equal(p.healingPool,20);assert.equal(p.belt[0].quantity,1);assert.ok(useBeltItem(c,0).ok);assert.equal(p.belt[0],null);assert.equal(p.healingPool,40);addItem(p,id('太阳水(小)'));putInBelt(p,content,id('太阳水(小)'));assert.ok(useBeltItem(c,0).ok);assert.equal(p.hp,p.base.hp);assert.equal(p.mp,p.base.mp);assert.equal(p.belt[0],null);
});
check('Full HP/MP, dead heroes, empty slots and stale repeated clicks cannot consume or resurrect',()=>{
 const p=fresh(),c=new Combat(p,content);addItem(p,0,2);putInBelt(p,content,0);let before=JSON.stringify(p);assert.equal(useBeltItem(c,0).ok,false);assert.equal(JSON.stringify(p),before);p.hp=0;before=JSON.stringify(p);assert.equal(useBeltItem(c,0).ok,false);assert.equal(JSON.stringify(p),before);assert.equal(useBeltItem(c,3).ok,false);assert.equal(p.hp,0);
});
check('Return preserves the stack and occupies one slot, and a full backpack rejects the return without losing either container',()=>{
 const p=fresh();addItem(p,0,3);putInBelt(p,content,0);const slots=carryState(p,content).slots;assert.ok(returnFromBelt(p,0).ok);assert.equal(p.belt[0],null);assert.equal(p.inventory[0].quantity,3);assert.equal(carryState(p,content).slots,slots+1);putInBelt(p,content,0);fillBag(p,[0]);const before=JSON.stringify(p);assert.equal(returnFromBelt(p,0).ok,false);assert.equal(JSON.stringify(p),before);
});
check('Purchases, box withdrawals and pickups refill an assigned slot with all 50 backpack slots occupied, ignoring native weight',()=>{
 const p=fresh();p.gold=1000;addItem(p,0);putInBelt(p,content,0);fillBag(p,[0,1]);assert.ok(buyItem(p,content,[0],0,2).ok);assert.equal(p.belt[0].quantity,3);assert.equal(p.inventory.length,50);p.storage.items=[{itemId:0,quantity:2}];assert.ok(transferStorage(p,content,'storage',0,2,false).ok);assert.equal(p.belt[0].quantity,5);assert.deepEqual(p.storage.items,[]);p.base.capacity=0;assert.equal(carryAmount(p,content,0,10),10);assert.ok(canCarry(p,content,0,1000));assert.equal(canCarry(p,content,0,3),true);assert.equal(canCarry(p,content,1,1),false);
});
check('NPC item checks and material exchanges include belt contents and maintain atomic script execution',()=>{
 const p=fresh();addItem(p,id('鸡蛋'),3);putInBelt(p,content,id('鸡蛋'));const view=readNpcDialogue('#Sub Start\n#ItemCK 鸡蛋 >= 3\n#Take 鸡蛋 2\n#Give 金币 10\n#EndIf\n#End',p,content);assert.deepEqual(view.unsupported,[]);assert.ok(applyNpcEffects(p,view.effects,content));assert.equal(p.belt[0].quantity,1);assert.equal(p.gold,10);const before=JSON.stringify(p);assert.equal(applyNpcEffects(p,[{kind:'take',itemId:id('鸡蛋'),quantity:2}],content),false);assert.equal(JSON.stringify(p),before);
});
check('Save/reload preserves exact slot order and quantities; old saves get empty slots, malformed non-consumables return to the bag, new profiles reset',()=>{
 const p=fresh();addItem(p,5,4);putInBelt(p,content,5);addItem(p,0,2);putInBelt(p,content,0);assert.ok(returnFromBelt(p,0).ok);const q=createCharacter(content,{version:2,player:JSON.parse(JSON.stringify(p))});assert.deepEqual(q.belt,p.belt);assert.deepEqual(q.inventory,p.inventory);const old=JSON.parse(JSON.stringify(p));delete old.belt;assert.deepEqual(createCharacter(content,{version:2,player:old}).belt,Array(6).fill(null));const invalid=fresh();invalid.belt[0]={itemId:id('木剑'),quantity:1};const repaired=createCharacter(content,{version:2,player:invalid});assert.equal(repaired.belt[0],null);assert.equal(repaired.inventory[0].itemId,id('木剑'));assert.deepEqual(fresh().belt,Array(6).fill(null));
});
check('Oversized saved stacks cannot overflow safe counts through replenishment, purchases or loot pickup',()=>{
 const p=fresh();p.belt[0]={itemId:0,quantity:Number.MAX_SAFE_INTEGER};p.base.capacity=Infinity;p.gold=1000;const before=JSON.stringify(p);assert.equal(canCarry(p,content,0,1),false);assert.equal(carryAmount(p,content,0,1),0);assert.equal(buyItem(p,content,[0],0,1).ok,false);assert.equal(JSON.stringify(p),before);
});
await fs.writeFile('reports/belt-tests.json',JSON.stringify({passed:true,checks},null,2));console.log({passed:true,checks:checks.length});
