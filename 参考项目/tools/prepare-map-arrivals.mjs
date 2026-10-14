// Arrival candidates from original portals and literal MOVE scripts. No source maps rewritten.
import fs from 'node:fs/promises';
const maps=JSON.parse(await fs.readFile('public/assets/data/maps.json','utf8')),byMap=new Map(maps.map(m=>[m.id,m])),arrivals={};
function add(id,x,y,source){const map=byMap.get(id);if(!map||!Number.isInteger(x)||!Number.isInteger(y)||x<=0||y<=0||x>=map.width||y>=map.height)return;const list=arrivals[id]||=[];if(!list.some(p=>p.x===x&&p.y===y))list.push({x,y,source});}
for(const meta of maps){const m=JSON.parse(await fs.readFile('public/assets/maps/'+meta.id+'.json','utf8'));for(const p of m.portals){const id=p.target==='当前地图'?m.id:p.target.split(' ')[0];add(id,p.targetX,p.targetY,'portal:'+m.id);}for(const n of m.npcs)for(const match of n.script.matchAll(/#(?:move|tomap)\s+([A-Z]\d\d)\s+(\d+)\s+(\d+)/gi))add(match[1],+match[2],+match[3],'npc:'+m.id+':'+n.name);}
await fs.writeFile('public/assets/data/map-arrivals.json',JSON.stringify({source:'immutable original maps/portals/NPC literal destinations',maps:arrivals}));console.log({arrivalMaps:Object.keys(arrivals).length,points:Object.values(arrivals).flat().length});
