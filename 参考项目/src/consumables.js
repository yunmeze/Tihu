import {findInventory,inventoryKey,mergeCarriedItem,takeItem} from './inventory.js';
import {carryState,instanceItem} from './native-stats.js';
import {specialConsumableEffect,specialDescription,applySpecialConsumable} from './special-consumables.js';
import {placePendingLoot} from './permanent-state.js';

const fail=reason=>({ok:false,reason});
const clone=value=>Array.isArray(value)?value.map(clone):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([k,v])=>[k,clone(v)])):value;
export function consumableEffect(item){
 if(!item)return null;
 const special=specialConsumableEffect(item);if(special)return special;
 if(item.type===5){
  if(item.name==='回城卷')return {kind:'teleport',returnTown:true};
  const id=item.name.match(/\s+([A-Z]\d\d)$/)?.[1],x=item.rawFields?.[2],y=item.rawFields?.[3];
  return id&&Number.isInteger(x)&&Number.isInteger(y)?{kind:'teleport',id,position:{x,y}}:null;
 }
 if(item.type===6&&item.name.endsWith('包'))return {kind:'package',name:item.name.slice(0,-1),quantity:6};
 return [3,4].includes(item.type)&&(item.hp>0||item.mp>0)?{kind:'restore'}:null;
}

// Native map loader 59e03b: entering an xx00 map remembers its town prefix.
// Older Web saves have no explicit prefix; use their latest unlocked town.
export function returnTown(player,content){
 const towns=content.mapList.filter(m=>/^[A-Z]00$/.test(m.id));
 return towns.find(m=>m.id===player.returnTown)||[...(player.unlockedMaps||[])].reverse().map(id=>towns.find(m=>m.id===id)).find(Boolean)||towns.find(m=>m.id==='A00');
}
export function teleportDestination(player,content,effect){
 const map=effect.returnTown?returnTown(player,content):content.mapList.find(m=>m.id===effect.id);
 if(!map)return fail('传送地点不存在');
 if(!effect.returnTown&&!player.unlockedMaps.includes(map.id))return fail('无法传送到未到过的地图');
 // Native single-player branch 5e768a checks Event(0) before 三清观符.
 if(!effect.returnTown&&map.id==='A13'&&(player.events?.[0]||0)<3)return fail('当前任务状态无法使用该道具');
 const position=effect.returnTown?{x:map.home[0],y:map.home[1]}:effect.position;
 if(position.x<0||position.y<0||position.x>=map.width||position.y>=map.height)return fail('传送坐标无效');
 return {ok:true,id:map.id,position:{...position},name:map.name};
}
export function consumableDescription(player,content,item){
 const effect=consumableEffect(item);if(!effect)return [];
 if(effect.kind==='special')return specialDescription(effect.name);
 if(effect.kind==='restore')return ['恢复 HP '+item.hp,'恢复 MP '+item.mp];
 if(effect.kind==='package')return ['拆出 '+effect.quantity+' 个',effect.name];
 const map=effect.returnTown?returnTown(player,content):content.mapList.find(m=>m.id===effect.id);
 return [effect.returnTown?'回到主城镇':'传送到',map?.name||'未知地点'];
}

function takeSource(player,source){
 if(source.kind==='bag')return takeItem(player.inventory,source.key,1);
 const entry=player.belt?.[source.index],taken=entry&&takeItem([entry],inventoryKey(entry),1);
 if(taken&&!entry.quantity)player.belt[source.index]=null;return taken;
}
const worldFields=['appearance','featureView','visibleArtFiles','worldArtFiles','map','mapId','hero','camera','units','pendingNpc','npcDialogue','nearbyPages','serviceView','attributeOpen','mapSpriteExtents','miniFile','lastMoveTap','selectedItem','selectedBelt','selectedEquipment','page','lastPreparedCell','lastWorldScriptRevision','portalDelay'];
export function captureWorld(app){return {fields:Object.fromEntries(worldFields.map(k=>[k,app[k]])),combat:{...app.combat,position:clone(app.combat.position),threats:new Map(app.combat.threats||[]),groundByMap:clone(app.combat.groundByMap)},scriptState:clone(app.scriptState),mapFlagsByMap:clone(app.mapFlagsByMap)};}
export function restoreWorld(app,state){
 for(const k of Object.keys(app.combat))if(!(k in state.combat))delete app.combat[k];
 Object.assign(app.combat,state.combat);Object.assign(app,state.fields,{scriptState:state.scriptState,mapFlagsByMap:state.mapFlagsByMap});
 app.hero=app.combat.position;app.combat.groundItems=app.combat.groundByMap[app.mapId];app.combat.scriptState=app.scriptState;app.combat.mapFlagsByMap=app.mapFlagsByMap;
}
export function restorePlayer(player,saved){for(const k of Object.keys(player))delete player[k];Object.assign(player,saved);}

// The UI and periodic saves are suspended while an asynchronous use is pending.
// Stage the cost before map entry scripts, then commit both cost and destination
// together; loading failures restore the old world and the exact item stack.
export async function useCarriedConsumable(app,source){
 if(app.itemBusy||app.changing||app.entering||app.resetting||app.reviving||app.disposed)return fail('操作正在进行');
 const player=app.player,combat=app.combat,entry=source.kind==='bag'?findInventory(player.inventory,source.key):player.belt?.[source.index];
 if(!entry||entry.quantity<=0)return fail('物品数量不足');
 if(player.hp<=0)return fail('死亡后无法使用消耗品');
 if(app.combat.scriptLocked)return fail('剧情进行中');
 const item=instanceItem(app.content.items[entry.itemId],entry),effect=consumableEffect(item);
 if(!effect)return fail('此物品无法直接使用');
 if(effect.kind==='restore'){
  if(!combat.usePotion(item))return fail('生命和魔法已满');
  takeSource(player,source);app.save();return {ok:true};
 }
 const saved=clone(player),world=['teleport','special'].includes(effect.kind)?captureWorld(app):null;
 app.itemBusy=true;let committed=false;
 const current=()=>!app.disposed&&app.player===player&&app.combat===combat&&player.hp>0;
 try{
  if(effect.kind==='special'){
   const staged=clone(player);if(!takeSource(staged,source))return fail('物品数量不足');const result=applySpecialConsumable(staged,app.content,effect.name,combat.random);if(!result.ok)return result;
   if(result.drops.length)staged.pendingGroundItems=[...(staged.pendingGroundItems||[]),...result.drops];
   restorePlayer(player,staged);if(!placePendingLoot(combat))return fail('附近没有可放置物品的地面');
   if(result.appearance)await app.updateAppearance();await app.prepareOwned();await app.prepareVisible();if(!current())return fail('操作已取消');
   if(result.drops.length){combat.autoLoot=true;combat.lootAfter=combat.elapsed;}
   app.audio?.ui('道具-其它');if(result.message)app.notify(result.message);
  }else if(effect.kind==='package'){
   const child=app.content.itemNames.get(effect.name);if(!child)return fail('包内道具不存在');
   const staged=clone(player),taken=takeSource(staged,source);
   const metadata=taken.dropSources?{dropSources:taken.dropSources.map(s=>({...s,quantity:s.quantity*effect.quantity}))}:{};
   if(!mergeCarriedItem(staged,child.id,effect.quantity,metadata))return fail('物品数量过多');
   const load=carryState(staged,app.content);
   if(load.slots>Math.max(load.capacity,carryState(player,app.content).slots))return fail('背包没有足够的空间用来解包');
   if(app.content.frame){await app.content.frame('Item1',child.icon);await app.content.sync();}
   if(!current())return fail('操作已取消');
   player.inventory=staged.inventory;player.belt=staged.belt;app.audio?.ui('按键2');
  }else{
   const destination=teleportDestination(player,app.content,effect);if(!destination.ok)return destination;
   if(!takeSource(player,source))return fail('物品数量不足');
   if(destination.id===app.mapId){
    combat.stopFarming();Object.assign(combat.position,destination.position);app.hero=combat.position;app.camera={...destination.position};app.pendingNpc=null;
    await app.prepareVisible();
   }else if(!await app.changeMap(destination.id,destination.position,{unlock:effect.returnTown,consumable:true}))throw Error('Map transition failed');
   if(!current())throw Error('Item use cancelled');
   app.audio?.ui('传送2');app.portalDelay=app.elapsed+3;
  }
  committed=true;return {ok:true};
 }catch(error){return fail(app.disposed?'操作已取消':'使用未完成，请重试');}
 finally{
  if(!committed&&app.player===player&&app.combat===combat){restorePlayer(player,saved);if(world)restoreWorld(app,world);}
  app.itemBusy=false;
  if(!app.disposed&&app.player===player&&app.combat===combat)app.save();
 }
}
