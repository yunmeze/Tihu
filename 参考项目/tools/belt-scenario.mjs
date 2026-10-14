// Real HUD coordinates through browser/native canvas input, independent of DOM.
export async function beltScenario({native=false}={}){
 const a=native?nativeTest.gameGlobal.lpLegend:lpLegend;a.platform.cancel(a.frame);
 if(a.mapId!=='A00')await a.changeMap('A00',null,{unlock:true});
 a.systemMenu=false;a.serviceView=null;a.npcDialogue=null;a.attributeOpen=false;a.mapOpen=false;a.gmOpen=false;
 const p=a.player,c=a.combat;c.stopFarming();p.base.capacity=1000;p.hp=7;p.mp=1;p.healingPool=p.mpRecoveryPool=0;
 p.inventory=[{itemId:0,quantity:3},{itemId:5,quantity:2},{itemId:24,quantity:1},{itemId:20,quantity:2},{itemId:1,quantity:1},{itemId:298,quantity:1},{itemId:140,quantity:1},{itemId:59,quantity:2},{itemId:10,quantity:1}];p.belt=[null,null,null,null,null,null];a.selectedBelt=null;a.selectedItem=null;a.page=0;a.tab='背包';await a.prepareOwned();a.render();
 const click=async label=>{
  const b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing belt control '+label);
  const point={clientX:a.left+(b.x+b.w/2)*a.scale,clientY:a.top+(b.y+b.h/2)*a.scale};
  if(native){nativeTest.handlers.get('TouchStart')({touches:[point]});nativeTest.handlers.get('TouchEnd')({changedTouches:[point]});await new Promise(r=>setTimeout(r,0));}
  else await a.pointer(point.clientX,point.clientY);
  a.render();
 };
 for(const name of ['木剑','铁矿石']){await click(name);if(a.buttons.some(b=>b.label==='放入腰带'))throw Error('Non-consumable exposed belt action');}
 for(const name of ['金创药小','魔法药小','太阳水(小)','鸡蛋','回城卷','金创药小包']){await click(name);await click('放入腰带');}
 if(p.inventory.some(e=>[0,5,24,20].includes(e.itemId))||p.belt.map(e=>e.itemId).join(',')!=='0,5,24,20,59,10')throw Error('Belt transfer did not remove bag items/order changed');
 await click('金创药中');await click('放入腰带');if(p.inventory.find(e=>e.itemId===1)?.quantity!==1||p.belt.filter(Boolean).length!==6)throw Error('Full belt lost an item');a.message=null;
 await click('战斗');const row=a.buttons.filter(b=>b.label.startsWith('腰带:'));if(row.length!==6||row.some(b=>b.y!==1312)||a.buttons.filter(b=>b.label.startsWith('技能:')).some(b=>b.y<1380))throw Error('Belt/skill rows overlap');
 c.farmType=4;const feet=JSON.stringify(c.position);await click('腰带:0:金创药小');if(p.belt[0].quantity!==2||p.healingPool!==20||JSON.stringify(c.position)!==feet||c.farmType!==4)throw Error('Quick potion canceled farming/moved or used wrong quantity');c.stopFarming();
 const instant=a.content.items[24],instantHp=Math.min(p.base.hp,p.hp+instant.hp),instantMp=Math.min(p.base.mp,p.mp+instant.mp);await click('腰带:2:太阳水(小)');if(p.belt[2]!==null||p.hp!==instantHp||p.mp!==instantMp)throw Error('Instant item/depleted slot failed');
 p.hp=0;const quantity=p.belt[0].quantity;await click('腰带:0:金创药小');if(p.hp!==0||p.belt[0].quantity!==quantity)throw Error('Belt potion resurrected dead hero');p.hp=p.base.hp;a.message=null;
 const emptyFeet=JSON.stringify(c.position);await click('腰带:2:空');if(JSON.stringify(c.position)!==emptyFeet)throw Error('Empty belt clicked through to map');
 await click('背包');await click('腰带:0:金创药小');await click('移回背包');if(p.belt[0]!==null||p.inventory.find(e=>e.itemId===0)?.quantity!==2)throw Error('Belt return failed');await click('金创药小');await click('放入腰带');
 const belt=JSON.stringify(p.belt);a.save();if(JSON.stringify(a.platform.load().player.belt)!==belt)throw Error('Belt slot order/quantity not saved');
 await a.startGame(a.platform.load(),{characterId:a.characterId});a.platform.cancel(a.frame);if(JSON.stringify(a.player.belt)!==belt||a.player.inventory.some(e=>[0,5,20].includes(e.itemId)))throw Error('Belt reload duplicated/lost items');a.tab='战斗';a.message=null;a.render();
 return {nativeTouch:native,slots:6,oneShotOnly:true,wholeStacksHidden:true,fullBeltAtomic:true,instantAndGradual:true,noFarmingInterruption:true,deadUseBlocked:true,noMapClickThrough:true,returnToBag:true,slotOrderAndCountsSaved:true,belt:JSON.parse(belt)};
}
