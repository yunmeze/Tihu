import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {consumableEffect,returnTown,teleportDestination,useCarriedConsumable} from '../src/consumables.js';
import {putInBelt} from '../src/belt.js';
import {createCharacter,createNewCharacter,addItem} from '../src/character.js';
import {Combat} from '../src/combat.js';
import {LPApp} from '../src/game.js';
const read=async file=>JSON.parse(await fs.readFile('public/assets/'+file,'utf8'));
const content={items:await read('data/items.json'),skills:await read('data/skills.json'),monsters:await read('data/monsters.json'),mapList:await read('data/maps.json')};content.itemNames=new Map(content.items.map(i=>[i.name,i]));
const checks=[],check=async(name,fn)=>{await fn();checks.push(name);},id=name=>content.itemNames.get(name).id;
async function fixture(){
 const p=createNewCharacter(content,{});p.base.capacity=10000;const c=new Combat(p,content),map=await read('maps/A00.json');c.enter(map,{x:90,y:50});
 const app={player:p,combat:c,content:{...content},map,mapId:map.id,hero:c.position,camera:{x:90,y:50},units:c.units,elapsed:7,scriptState:{},mapFlagsByMap:{},audio:{ui(){}},saved:[],save(){if(!this.itemBusy)this.saved.push({player:JSON.parse(JSON.stringify(this.player)),map:this.mapId,position:{x:this.hero.x,y:this.hero.y}});},async prepareVisible(){},async changeMap(mapId,position){this.map=await read('maps/'+mapId+'.json');this.mapId=mapId;c.enter(this.map,position);this.hero=c.position;this.units=c.units;this.camera={...position};if(mapId.endsWith('00'))p.returnTown=mapId;return true;}};
 return {p,c,app};
}
await check('All 12 original scrolls accept belt transfer and retain configured destinations/coordinates',async()=>{
 for(const item of content.items.filter(i=>i.type===5)){
  const {p,app}=await fixture();p.unlockedMaps=content.mapList.map(m=>m.id);p.events=[3];addItem(p,item.id,2);assert.ok(putInBelt(p,content,item.id).ok);
  const effect=consumableEffect(item),plan=teleportDestination(p,content,effect);assert.ok(plan.ok,item.name);
  if(item.name!=='回城卷')assert.deepEqual(plan.position,{x:item.rawFields[2],y:item.rawFields[3]});
  assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,item.name);assert.equal(p.belt[0].quantity,1);assert.equal(app.mapId,plan.id);assert.equal(app.hero.x,plan.position.x);assert.equal(app.hero.y,plan.position.y);assert.equal(app.saved.at(-1).player.belt[0].quantity,1);
 }
});
await check('Return scroll targets the last entered town; saved town and legacy unlocked-town fallback survive loading',async()=>{
 const {p,app}=await fixture();p.returnTown='H00';p.unlockedMaps.push('H00');addItem(p,59,2);assert.ok((await useCarriedConsumable(app,{kind:'bag',key:59})).ok);assert.equal(app.mapId,'H00');assert.deepEqual({x:app.hero.x,y:app.hero.y},{x:40,y:78});assert.equal(p.inventory.find(e=>e.itemId===59).quantity,1);
 const q=createCharacter(content,{version:2,player:JSON.parse(JSON.stringify(p))});assert.equal(returnTown(q,content).id,'H00');delete q.returnTown;q.unlockedMaps=['A00','H00','H12'];assert.equal(returnTown(q,content).id,'H00');q.unlockedMaps=[];assert.equal(returnTown(q,content).id,'A00');
});
await check('Unvisited target, unfinished 三清观 quest, dead hero and invalid destination consume nothing and never revive',async()=>{
 const {p,app}=await fixture();addItem(p,51,2);putInBelt(p,content,51);let before=JSON.stringify(p);assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(JSON.stringify(p),before);p.unlockedMaps.push('A13');p.events=[2];before=JSON.stringify(p);assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(JSON.stringify(p),before);
 p.hp=0;addItem(p,59);before=JSON.stringify(p);assert.equal((await useCarriedConsumable(app,{kind:'bag',key:59})).ok,false);assert.equal(JSON.stringify(p),before);assert.equal(p.hp,0);
 assert.equal(teleportDestination(p,content,{id:'A00',position:{x:-1,y:0}}).ok,false);
});
await check('A late map-loading failure rolls back map, position, farming, pets, quest mutations and exact item provenance',async()=>{
 const {p,c,app}=await fixture();p.unlockedMaps.push('H00');addItem(p,59,2,{dropSources:[{mode:0,quantity:2}]});putInBelt(p,content,59);p.returnTown='H00';Object.assign(c.position,{x:86,y:52});c.groundItems.push({id:'A00:loot:1',kind:'item',itemId:0,quantity:1,x:86,y:52});c.farmType=4;c.threats.set('A00:0',90);const before=JSON.stringify(p),originalMap=app.map,originalUnits=c.units,position={...c.position};
 app.changeMap=async()=>{const m=await read('maps/H00.json');app.map=m;app.mapId='H00';c.enter(m,{x:40,y:78});app.hero=c.position;app.units=c.units;p.gold+=999;p.events[0]=99;app.scriptState.H00={test:true};c.groundByMap.H00=[{id:'bad'}];app.save();throw Error('late texture error');};
 assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(JSON.stringify(p),before);assert.equal(app.map,originalMap);assert.equal(app.mapId,'A00');assert.deepEqual(c.position,position);assert.equal(app.hero,c.position);assert.equal(c.units,originalUnits);assert.equal(c.farmType,4);assert.equal(c.threats.get('A00:0'),90);assert.deepEqual(app.scriptState,{});assert.ok(!c.groundByMap.H00);assert.equal(app.saved.length,1);assert.equal(app.saved[0].map,'A00');assert.equal(app.itemBusy,false);assert.equal(c.groundItems,c.groundByMap.A00);c.pickupAtFeet();assert.equal(p.inventory.find(e=>e.itemId===0).quantity,1);assert.equal(c.groundByMap.A00.length,0);
});
await check('Same-map teleport does not respawn monsters; preparation failure restores the old position and item',async()=>{
 const {p,c,app}=await fixture();addItem(p,55,2);putInBelt(p,content,55);const units=c.units,before={...c.position};app.prepareVisible=async()=>{throw Error('failed art');};assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.deepEqual(c.position,before);assert.equal(p.belt[0].quantity,2);
 app.prepareVisible=async()=>{};assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok);assert.equal(c.units,units);assert.equal(p.belt[0].quantity,1);assert.equal(c.farmType,null);assert.equal(c.position.x,86);assert.equal(c.position.y,53);
});
await check('Repeated clicks during asynchronous travel are rejected; save and other map/session/GM changes wait for completion',async()=>{
 const {p,app}=await fixture();p.returnTown='H00';p.unlockedMaps.push('H00');addItem(p,59,2);putInBelt(p,content,59);let resolve;const pending=new Promise(r=>resolve=r),change=app.changeMap;app.changeMap=async(...args)=>{await pending;return change.apply(app,args);};
 const first=useCarriedConsumable(app,{kind:'belt',index:0});assert.equal(app.itemBusy,true);assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);app.save();assert.equal(app.saved.length,0);
 assert.equal(await LPApp.prototype.startGame.call(app),false);assert.equal(await LPApp.prototype.changeMap.call(app,'A00'),false);assert.equal(await LPApp.prototype.gmCommand.call({...app,screen:'game'},'清档'),undefined);
 resolve();assert.ok((await first).ok);assert.equal(p.belt[0].quantity,1);assert.equal(app.saved.length,1);assert.equal(app.itemBusy,false);
});
await check('All 17 native type-6 packages produce six correct children, consume one package and preserve dropped-item provenance',async()=>{
 for(const item of content.items.filter(i=>i.type===6&&i.name!=='0')){
  const {p,app}=await fixture();addItem(p,item.id,2,{dropSources:[{mode:0,quantity:2}]});putInBelt(p,content,item.id);assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,item.name);assert.equal(p.belt[0].quantity,1);const child=p.inventory.find(e=>e.itemId===id(item.name.slice(0,-1)));assert.equal(child.quantity,6);assert.deepEqual(child.dropSources,[{mode:0,quantity:6}]);
 }
});
await check('Package slot failures are atomic; consuming the last package or filling an assigned child belt works at the class limit',async()=>{
 const {p,app}=await fixture();const fill=exclude=>p.inventory=content.items.filter(i=>i.name!=='0'&&!exclude.includes(i.id)).slice(0,50).map(i=>({itemId:i.id,quantity:1}));addItem(p,60);putInBelt(p,content,60);fill([59,60]);let before=JSON.stringify(p);assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(JSON.stringify(p),before);
 fill([59,60]);p.inventory[0]={itemId:60,quantity:1};p.belt.fill(null);assert.ok((await useCarriedConsumable(app,{kind:'bag',key:60})).ok);assert.equal(p.inventory.find(e=>e.itemId===59).quantity,6);assert.equal(p.inventory.length,50);
 fill([59,60]);p.belt=[{itemId:60,quantity:1},{itemId:59,quantity:1},null,null];assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok);assert.equal(p.belt[0],null);assert.equal(p.belt[1].quantity,7);assert.equal(p.inventory.length,50);
 p.inventory=[];p.belt=[{itemId:10,quantity:1},null,null,null];p.base.capacity=0;assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok);
});
await check('Dead package use and disposal during asset loading preserve contents; depleted packages clear their belt slot',async()=>{
 const {p,app}=await fixture();addItem(p,60);putInBelt(p,content,60);p.hp=0;assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(p.belt[0].quantity,1);p.hp=1;
 app.content.frame=async()=>{app.disposed=true;};app.content.sync=async()=>{};assert.equal((await useCarriedConsumable(app,{kind:'belt',index:0})).ok,false);assert.equal(p.belt[0].quantity,1);assert.equal(p.inventory.length,0);assert.equal(app.itemBusy,false);app.disposed=false;delete app.content.frame;
 assert.ok((await useCarriedConsumable(app,{kind:'belt',index:0})).ok);assert.equal(p.belt[0],null);assert.equal(p.inventory[0].itemId,59);assert.equal(p.inventory[0].quantity,6);
});
await fs.writeFile('reports/consumable-tests.json',JSON.stringify({passed:true,checks,scrolls:12,packages:17},null,2));console.log({passed:true,checks:checks.length,scrolls:12,packages:17});
