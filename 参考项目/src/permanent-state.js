import {applyNpcEffects} from './npc-dialogue.js';

export const insightOn=(player,id)=>player.insights?.[id]===1;
export function normalizePermanent(player,content){
 const old=player.insights||[];player.insights=Array.from({length:13},(_,i)=>[-1,0,1].includes(old[i])?old[i]:-1);
 player.insightFreeCount=Math.max(0,Math.min(2,Math.trunc(player.insightFreeCount)||0));
 player.autoHpPercent=Math.max(10,Math.min(90,Math.trunc(player.autoHpPercent)||40));player.autoMpPercent=Math.max(10,Math.min(90,Math.trunc(player.autoMpPercent)||20));
 player.collection||={};player.collection.monsters||={};player.collection.drops||={};
 // Historical kills / origins cannot be inferred from inventory contents.
 const pool=content.permanent?.collectionPool||[];for(const key of Object.keys(player.collection.monsters))if(!pool.some(m=>m.id===Number(key)))delete player.collection.monsters[key];
 for(const key of Object.keys(player.collection.drops)){const [id,index]=key.split(':').map(Number),m=pool.find(m=>m.id===id);if(!m?.drops[index])delete player.collection.drops[key];}
 return player;
}
export function recordCollectionMonster(player,id){player.collection||={};player.collection.monsters||={};player.collection.monsters[id]=true;}
export function recordCollectionDrop(player,id,index){player.collection||={};player.collection.drops||={};player.collection.drops[id+':'+index]=true;}
export function collectionProgress(player,content){
 const pool=content.permanent.collectionPool,m=player.collection?.monsters||{},d=player.collection?.drops||{};
 const monsters=pool.filter(r=>m[r.id]).length,totalDrops=pool.reduce((n,r)=>n+r.drops.length,0),drops=pool.reduce((n,r)=>n+r.drops.filter((_,i)=>d[r.id+':'+i]).length,0);
 return {monsters:{current:monsters,total:pool.length,ratio:monsters/Math.max(1,pool.length),stage:player.monsterRewardStage||0},drops:{current:drops,total:totalDrops,ratio:drops/Math.max(1,totalDrops),stage:player.collectionRewardStage||0}};
}
// Keep the recovered reward table intact; its weight-only tier is inactive
// under the fixed class backpack rule.
export const collectionRewards=(content,kind)=>content.permanent.rewards[kind].filter(r=>!r.capacity||r.gold||r.attributes||r.items||r.defense||r.magicDefense||r.offense||r.affixBonus);
export function claimCollection(player,content,kind){
 if(!['monsters','drops'].includes(kind))return false;const progress=collectionProgress(player,content)[kind],ready=collectionRewards(content,kind).filter(r=>r.stage>progress.stage&&progress.current*10>=r.stage*progress.total);
 if(!ready.length)return false;const effects=[];
 const change=(field,value)=>effects.push({kind:'change',field,operator:'+',value});
 for(const row of ready){if(row.gold)change('money',row.gold);if(row.attributes)change('属性点',row.attributes);if(row.defense)change('dfmax',row.defense);if(row.magicDefense)change('dmmax',row.magicDefense);if(row.offense)for(const field of ['dcmax','scmax','mcmax'])change(field,row.offense);
  for(const [name,quantity]of row.items||[]){const item=content.itemNames.get(name);if(!item)return false;effects.push({kind:'give',itemId:item.id,quantity});}
 }
 if(!applyNpcEffects(player,effects,content))return false;player[kind==='monsters'?'monsterRewardStage':'collectionRewardStage']=ready.at(-1).stage;return true;
}
export function playerStatusEntries(player){
 const labels={burn:'灼烧',freeze:'冰冻',poison:'中毒',corrosion:'侵蚀',paralysis:'麻痹'},frames={burn:1,freeze:3,poison:5,corrosion:7,paralysis:9};
 const result=Object.entries(player.statuses||{}).filter(([name,s])=>labels[name]&&s.frames>0).map(([name,s])=>({name:labels[name],frame:frames[name],seconds:Math.ceil(s.frames/50)}));
 if(player.invisible&&player.invisibleFrames>0)result.push({name:'隐身',skill:'隐身术',seconds:Math.ceil(player.invisibleFrames/50)});
 if(player.magicShieldFrames>0)result.push({name:'魔法盾',skill:'魔法盾',seconds:Math.ceil(player.magicShieldFrames/50)});
 if(player.aura===2)result.push({name:'暗黑印记',pack:'Data4',frame:69,persistent:true,seconds:null});
 return result;
}
export function placePendingLoot(combat){
 const pending=combat.player.pendingGroundItems;if(!pending?.length)return true;
 const p=combat.position,cells=[];for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){const x=Math.round(p.x)+dx,y=Math.round(p.y)+dy;if(combat.walkable(x,y)&&combat.findPath({x,y},0)!==null)cells.push({x,y});}
 if(!cells.length)return false;
 for(const drop of pending){const cell=cells.find(c=>Math.hypot(c.x-p.x,c.y-p.y)>.1)||cells[0];combat.groundItems.push({...drop,...cell,id:combat.map.id+':loot:'+(++combat.nextDropId)});combat.lootVersion++;}
 delete combat.player.pendingGroundItems;return true;
}
