import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {MAIN_QUEST_GOALS,QUEST_COLLECTIONS} from '../src/main-quest.js';

// Only unconditional native #MOVE NPCs join the portal graph. Conditional
// travel buttons (ferries, teleport stones, ending pages) retain their scripts.
export function nativeTransfers(map){
 return map.npcs.flatMap((n,index)=>{
  const lines=n.script.replace(/\/\/[^\r\n]*/g,'').replace(/(#end)(#notui)/ig,'$1\n$2').split(/[\r\n]+/).map(s=>s.trim()).filter(Boolean);
  const moves=lines.map(s=>s.match(/^#(?:move|tomap)\s+([a-z]\d{2})\s+(\d+)\s+(\d+)\s*$/i)).filter(Boolean);
  if(moves.length!==1||!lines.every(s=>/^#(?:move|tomap|end|notui|sub\s+start)\b/i.test(s)))return [];
  return [{index,name:n.name,target:moves[0][1].toUpperCase()}];
 });
}
export async function buildQuestNavigation(root=process.cwd()){
 const base=path.join(root,'public/assets'),list=JSON.parse(await fs.readFile(path.join(base,'data/maps.json'),'utf8'));
 const maps={},originals=new Map(),digest=crypto.createHash('sha256');
 for(const meta of list){const bytes=await fs.readFile(path.join(base,'maps/'+meta.id+'.json')),m=JSON.parse(bytes);originals.set(m.id,m);digest.update(meta.id).update(bytes);maps[m.id]={name:m.name,exits:[...new Set(m.portals.map(p=>p.target==='当前地图'?m.id:p.target.split(' ')[0].toUpperCase()))].filter(id=>id!==m.id),transfers:nativeTransfers(m)};}
 const targets={};
 const goals=[...Object.values(MAIN_QUEST_GOALS),...Object.values(QUEST_COLLECTIONS).flatMap(c=>[...c.sources,c.turnIn])];
 for(const [kind,mapId,name]of goals){const map=originals.get(mapId),actor=(kind==='npc'?map.npcs:map.spawns).find(n=>n.name===name);if(!actor)throw Error(`Native quest target absent: ${mapId}/${name}`);targets[mapId]||={};targets[mapId][name]={kind,x:actor.x,y:actor.y};}
 for(const [id,m]of Object.entries(maps))for(const dest of [...m.exits,...m.transfers.map(t=>t.target)])if(!maps[dest])throw Error(`Native quest exit absent: ${id}/${dest}`);
 const data={version:1,source:'LP传奇单机版-重生v1.2.2E: extracted maps, Mstm.dat and NPC/monster scripts',mapsSha256:digest.digest('hex'),maps,targets};
 const bytes=JSON.stringify(data);await fs.writeFile(path.join(base,'data/quest-navigation.json'),bytes);return {maps:list.length,targets:Object.values(targets).reduce((n,t)=>n+Object.keys(t).length,0),transfers:Object.values(maps).reduce((n,m)=>n+m.transfers.length,0),bytes:Buffer.byteLength(bytes),mapsSha256:data.mapsSha256};
}
