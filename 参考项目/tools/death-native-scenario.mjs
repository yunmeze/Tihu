// Serialized into the native-canvas browser shim; no DOM or imported helpers.
export async function nativeDeathScenario(){
 const a=nativeTest.gameGlobal.lpLegend;
 const click=async label=>{a.render();const b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing native button '+label);await a.pointer(a.left+(b.x+b.w/2)*a.scale,a.top+(b.y+b.h/2)*a.scale);a.render();};
 await a.changeMap('A00',null,{unlock:true});await a.changeMap('A02',null,{unlock:true});a.player.hp=10;a.player.mp=0;a.combat.usePotion(a.content.itemNames.get('金创药小'));a.combat.hurt(a.player,999999,{player:true});a.tab='背包';a.selectedItem=a.content.itemNames.get('金创药小').id;
 const quantity=a.player.inventory.find(e=>e.itemId===a.selectedItem)?.quantity||0;
 await click('使用');for(let i=0;i<200;i++)a.combat.update(.02);
 if(a.player.hp!==0||a.combat.recovery.length||a.hero.action!=='death'||(a.player.inventory.find(e=>e.itemId===a.selectedItem)?.quantity||0)!==quantity)throw Error('Native medicine revived or consumed after death');
 await click('战斗');await click('回城复活');
 if(a.mapId!=='A00'||a.hero.x!==86||a.hero.y!==52||a.player.hp!==a.player.base.hp||a.player.mp!==a.player.base.mp||a.platform.load().map!=='A00')throw Error('Native village revival/save failed');
 const n=a.map.npcs.find(n=>n.name==='海曦小贩');Object.assign(a.combat.position,{x:n.x+1,y:n.y});a.hero=a.combat.position;a.camera={x:n.x,y:n.y};await a.prepareVisible();a.render();
 const p=a.screenPoint(n.x,n.y),f=a.packs.get('Npc').frames[1+n.appearance*12+n.direction*4];await a.pointer(a.left+(p.x+(f.offset[0]+f.crop[0]+f.rect[2]/2)*a.worldScale)*a.scale,a.top+(p.y+(f.offset[1]+f.crop[1]+f.rect[3]/2)*a.worldScale)*a.scale);
 if(a.pendingNpc||a.npcDialogue||a.serviceView||!a.combat.manualPath)throw Error('Native scene NPC still interactive');
 const u=a.units.find(u=>u.alive&&u.definition.id===4&&a.combat.walkable(u.x-3,u.y));a.combat.stopFarming();Object.assign(a.combat.position,{x:u.x-3,y:u.y});a.hero=a.combat.position;a.camera={x:u.x,y:u.y};await a.prepareVisible();a.render();const q=a.screenPoint(u.x,u.y);await a.pointer(a.left+q.x*a.scale,a.top+(q.y-35)*a.scale);
 if(a.combat.farmType!==null||a.combat.targetId!==null||!a.combat.manualPath)throw Error('Native scene monster still interactive');
 await click('怪物种类:4');if(a.combat.farmType!==4)throw Error('Native sidebar farming lost');a.combat.stopFarming();a.units=a.combat.units=[u];a.combat.random=()=>0;a.combat.kill(u);a.combat.stopFarming();const drops=a.combat.groundItems.length;
 for(let i=0;i<65;i++)a.combat.update(.02);let models=0;const original=a.batch.frame;a.batch.frame=function(pack,...rest){if(pack.id==='Mon/'+u.definition.appearance)models++;return original.call(this,pack,...rest);};try{a.render();}finally{a.batch.frame=original;}
 if(models||u.alive||a.combat.groundItems.length!==drops)throw Error('Native dead model or drop cleanup failed');
 return {deadPotionBlocked:true,queuedRecoveryCanceled:true,rememberedTownRevival:true,savedTown:true,sceneEntityClickMoves:true,sidebarFarming:true,deathModelCleared:true,dropsPreserved:true};
}
