import {carriedItems} from './inventory.js';
import {instanceItem} from './native-stats.js';
import {returnTown,captureWorld,restoreWorld,restorePlayer} from './consumables.js';
import {addVisual} from './projectiles.js';
import {clearMonsterAggro} from './monster-ai.js';

export const RING_RULES={'传送戒指':{key:'teleport',seconds:60},'隐身戒指':{key:'invisibility',seconds:120,frames:1000}};
export const ringRule=item=>RING_RULES[item?.name]||null;
export function normalizeRings(player){const old=player.ringCooldowns||{};player.ringCooldowns=Object.fromEntries(Object.values(RING_RULES).map(r=>[r.key,Math.max(0,Math.min(r.seconds,Math.ceil(Number(old[r.key])||0)))]));return player;}
export function hasRing(player,content,name){return [...carriedItems(player).map(e=>instanceItem(content.items[e.itemId],e)),...Object.entries(player.equipment).map(([slot,id])=>instanceItem(content.items[id],player.equipmentMeta?.[slot]))].some(i=>i?.name===name);}
export function ringRemaining(player,name){return Math.ceil(player.ringCooldowns?.[RING_RULES[name]?.key]||0);}
export function updateRingCooldowns(player,seconds){if(player.ringCooldowns)for(const key of ['teleport','invisibility'])player.ringCooldowns[key]=Math.max(0,(player.ringCooldowns[key]||0)-seconds);}
export async function activateRing(app,name,{keyboard=false}={}){
 const p=app.player,c=app.combat,r=RING_RULES[name],fail=reason=>({ok:false,reason});
 if(!r||!hasRing(p,app.content,name))return fail('没有该戒指');
 if(p.hp<=0)return fail('死亡后无法使用戒指');
 if(c.scriptLocked)return fail('剧情进行中');
 if(app.itemBusy||app.changing||app.entering||app.resetting||app.reviving||app.disposed)return fail('操作正在进行');
 if(ringRemaining(p,name)>0)return fail('戒指尚在冷却');
 normalizeRings(p);
 if(r.key==='invisibility'){
  if(!keyboard&&p.invisibleFrames>0)return fail('已经处于隐身状态');
  p.ringCooldowns[r.key]=r.seconds;p.invisible=true;p.invisibleFrames=r.frames;
  addVisual(c,9,c.position,{duration:1.2,follow:c.position});for(const u of c.units.filter(u=>u.alive&&!u.summoned))clearMonsterAggro(u);app.save();return {ok:true};
 }
 const town=returnTown(p,app.content);if(!town)return fail('传送地点不存在');
 const saved=JSON.parse(JSON.stringify(p)),world=captureWorld(app);let committed=false;app.itemBusy=true;
 try{
  p.ringCooldowns[r.key]=r.seconds;
  if(town.id===app.mapId){c.stopFarming();Object.assign(c.position,{x:town.home[0],y:town.home[1]});app.hero=c.position;app.camera={x:c.position.x,y:c.position.y};app.pendingNpc=null;await app.prepareVisible();}
  else if(!await app.changeMap(town.id,{x:town.home[0],y:town.home[1]},{unlock:true,consumable:true}))throw Error('Ring transition failed');
  if(app.disposed||app.player!==p||app.combat!==c||p.hp<=0)throw Error('Ring use cancelled');
  app.audio?.ui('传送2');app.portalDelay=app.elapsed+3;committed=true;return {ok:true};
 }catch{return fail(app.disposed?'操作已取消':'使用未完成，请重试');}
 finally{if(!committed&&app.player===p&&app.combat===c){restorePlayer(p,saved);restoreWorld(app,world);}app.itemBusy=false;if(!app.disposed&&app.player===p&&app.combat===c)app.save();}
}
