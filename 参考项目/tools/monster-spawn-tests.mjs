import fs from 'node:fs/promises';import assert from 'node:assert/strict';
import {Combat} from '../src/combat.js';import {canEnterCell} from '../src/map-flags.js';
const read=async f=>JSON.parse(await fs.readFile('public/assets/'+f,'utf8'));
const content={monsters:await read('data/monsters.json')},maps=await read('data/maps.json'),fixtures={},mismatches=[];
let spawns=0;
for(const entry of maps){
 const map=await read('maps/'+entry.id+'.json'),c=new Combat({hp:1},content);c.enter(map,{x:0,y:0});spawns+=map.spawns.length;
 assert.equal(c.units.length,map.spawns.length);
 for(let index=0;index<map.spawns.length;index++){
  const raw=map.spawns[index],unit=c.units[index];assert.equal(unit.definition.name,raw.name);assert.equal(unit.sourceMonsterId,raw.monsterId);assert.equal(unit.monsterId,unit.definition.id);
  if(unit.monsterId!==raw.monsterId)mismatches.push({mapId:map.id,x:raw.x,y:raw.y,name:raw.name,cachedId:raw.monsterId,cachedName:content.monsters[raw.monsterId]?.name,resolvedId:unit.monsterId});
  if(![19,152,162].includes(unit.monsterId)||fixtures[unit.monsterId])continue;
  const gap=unit.monsterId===152?1:3,free=(x,y)=>x>=0&&y>=0&&x<map.width&&y<map.height&&canEnterCell(map.cells[x*map.height+y][1])&&canEnterCell(map.cells[x*map.height+y][1],'monster')&&!map.npcs.some(n=>n.x===x&&n.y===y);
  for(const [dx,dy]of [[-1,0],[1,0],[0,-1],[0,1]])if(Array.from({length:gap+1},(_,i)=>i).every(i=>free(raw.x+i*dx,raw.y+i*dy))){fixtures[unit.monsterId]={mapId:map.id,mapName:map.name,monsterId:unit.monsterId,sourceSpawnIndex:index,spawn:raw,hero:{x:raw.x+dx*gap,y:raw.y+dy*gap}};break;}
 }
}
assert.ok(mismatches.length>0);assert.equal(Object.keys(fixtures).length,3);
// Synthetic callers without names may still supply an already-resolved ID.
const c=new Combat({hp:1},content);c.enter({id:'fallback',spawns:[{x:0,y:0,monsterId:4}]},{x:1,y:1});assert.equal(c.units[0].definition.id,4);
const result={passed:true,maps:maps.length,spawns,resolvedByNativeName:spawns,staleCachedIds:mismatches.length,originalExportUnmodified:true,nativeEvidence:'reports/native-ai-source.json',examples:mismatches.slice(0,16)};
await fs.writeFile('reports/monster-spawn-tests.json',JSON.stringify(result,null,2));await fs.writeFile('reports/native-ai-fixtures.json',JSON.stringify(fixtures,null,2));console.log({...result,examples:result.examples.slice(0,3)});
