import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {LPApp} from '../src/game.js';
import {returnTown,teleportDestination} from '../src/consumables.js';
import {Combat} from '../src/combat.js';
import {createCharacter} from '../src/character.js';
const read=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const content={mapList:await read('public/assets/data/maps.json'),items:await read('public/assets/data/items.json'),monsters:await read('public/assets/data/monsters.json'),skills:await read('public/assets/data/skills.json')};
content.itemNames=new Map(content.items.map(item=>[item.name,item]));
const checks=[];
const make=town=>{
 const player=createCharacter(content,{});player.hp=0;player.mp=0;player.returnTown=town;player.unlockedMaps=['A00',town,'K02'];
 const combat=new Combat(player,content),app={screen:'game',player,content,combat,mapId:'K02',elapsed:15,saveCount:0,loads:[],save(){this.saveCount++;this.saved={map:this.mapId,player:structuredClone(this.player),position:{...this.combat.position}};},async changeMap(id,position,options){this.loads.push({id,position,options});this.map=await read('public/assets/maps/'+id+'.json');this.mapId=id;this.player.returnTown=id;this.combat.position={action:'death'};return true;},async prepareVisible(){this.prepared={position:[this.hero.x,this.hero.y],map:this.mapId,locked:this.reviving};}};
 combat.units=[];app.reviveAtTown=LPApp.prototype.reviveAtTown;return app;
};
// Exercise the actual application transition for every original remembered town.
for(const town of content.mapList.filter(m=>/^[A-Z]00$/.test(m.id))){
 const a=make(town.id);assert.equal(await a.reviveAtTown(),true);assert.equal(a.loads.length,1);assert.equal(a.mapId,town.id);assert.deepEqual([a.hero.x,a.hero.y],town.home);assert.equal(a.player.hp,a.player.base.hp);assert.equal(a.player.mp,a.player.base.mp);assert.equal(a.saved.map,town.id);assert.equal(a.saved.player.returnTown,town.id);assert.equal(a.saved.player.hp,a.player.hp);assert.equal(a.combat.position.action,'idle');assert.deepEqual(a.camera,{x:town.home[0],y:town.home[1]});assert.equal(a.tab,'战斗');assert.equal(a.portalDelay,18);assert.equal(await a.reviveAtTown(),false);assert.equal(a.loads.length,1);assert.equal(a.saveCount,1);
 assert.equal(teleportDestination(a.player,content,{returnTown:true}).id,town.id);assert.deepEqual(a.loads[0].position,{x:town.home[0],y:town.home[1]});assert.deepEqual(a.prepared,{position:town.home,map:town.id,locked:true});
}
checks.push('all 10 native towns: revival, scroll and ring use the remembered town; original home/full HP-MP/camera/save and stale-call guards agree');
for(const map of ['A02','E30','J30']){const a=make('H00');a.mapId=map;assert.equal(await a.reviveAtTown(),true);assert.equal(a.mapId,'H00');}
checks.push('ordinary field, challenge and defense do not derive a town from the current map letter');
let a=make('H00');delete a.player.returnTown;a.player.unlockedMaps=['A00','J00','H00','K02'];assert.equal(returnTown(a.player,content).id,'H00');assert.equal(await a.reviveAtTown(),true);assert.equal(a.mapId,'H00');
a=make('bad');a.player.unlockedMaps=['A00','D00','K02'];assert.equal(await a.reviveAtTown(),true);assert.equal(a.mapId,'D00');a=make('bad');a.player.unlockedMaps=['K02'];assert.equal(await a.reviveAtTown(),true);assert.equal(a.mapId,'A00');
checks.push('missing/invalid legacy town: latest unlocked original town, then initial village fallback');
a=make('J00');let release;const load=a.changeMap;a.changeMap=async function(...args){await new Promise(r=>release=r);return load.apply(this,args);};const pending=a.reviveAtTown();assert.equal(await a.reviveAtTown(),false);assert.equal(a.saveCount,0);release();assert.equal(await pending,true);assert.equal(a.loads.length,1);
checks.push('double-click revival performs one transition and saves only its final world state');
for(const failure of ['refused','error']){a=make('D00');a.changeMap=async()=>{if(failure==='error')throw Error('offline');return false;};if(failure==='error')await assert.rejects(a.reviveAtTown(),/offline/);else assert.equal(await a.reviveAtTown(),false);assert.equal(a.player.hp,0);assert.equal(a.player.returnTown,'D00');assert.equal(a.mapId,'K02');assert.equal(a.reviving,false);}
checks.push('refused or failed map loads keep the hero dead and the town record intact; allow retry');
for(const field of ['reviving','itemBusy','changing','disposed']){a=make('D00');a[field]=true;assert.equal(await a.reviveAtTown(),false);assert.equal(a.loads.length,0);}
a=make('H00');a.screen='home';assert.equal(await a.reviveAtTown(),false);a=make('H00');a.player.hp=1;assert.equal(await a.reviveAtTown(),false);
checks.push('busy/disposed/out-of-game/living heroes cannot use revival');
const result={passed:true,checks};await fs.writeFile('reports/town-revival-tests.json',JSON.stringify(result,null,2));console.log({passed:true,checks:checks.length,nativeTowns:10});
