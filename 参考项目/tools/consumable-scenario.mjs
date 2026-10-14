export async function consumableScenario({native=false}={}){
 const a=native?nativeTest.gameGlobal.lpLegend:lpLegend;
 a.platform.cancel(a.frame);a.systemMenu=false;a.serviceView=null;a.npcDialogue=null;a.mapOpen=false;a.attributeOpen=false;a.gmOpen=false;
 const click=async label=>{
  a.render();const b=a.buttons.find(b=>b.label===label||label.endsWith(':')&&b.label.startsWith(label));if(!b)throw Error('Missing consumable control '+label);
  const x=a.left+(b.x+b.w/2)*a.scale,y=a.top+(b.y+b.h/2)*a.scale;
  if(native){nativeTest.handlers.get('TouchStart')({touches:[{clientX:x,clientY:y}]});nativeTest.handlers.get('TouchEnd')({changedTouches:[{clientX:x,clientY:y}]});
   for(let i=0;i<3000&&(a.itemBusy||a.changing);i++)await new Promise(r=>setTimeout(r,10));if(a.itemBusy||a.changing)throw Error('Native consumable action timed out');await new Promise(r=>setTimeout(r,0));
  }else await a.pointer(x,y);
  if(a.preparing)await a.preparing;a.render();
 };
 await a.changeMap('H00',{x:40,y:78},{unlock:true});await a.changeMap('A02',{x:86,y:51},{unlock:true});
 a.player.inventory=[{itemId:59,quantity:3},{itemId:55,quantity:2},{itemId:60,quantity:1},{itemId:10,quantity:1}];a.player.belt=[null,null,null,null,null,null];a.player.base.capacity=10000;a.player.hp=a.player.base.hp;a.player.mp=a.player.base.mp;a.player.events[0]=3;a.tab='背包';a.selectedItem=59;a.selectedBelt=null;await a.prepareOwned();
 for(const name of ['回城卷','海曦村符','回城卷包','金创药小包']){await click(name);await click('放入腰带');}
 if(a.player.inventory.length||a.player.belt.filter(Boolean).length!==4)throw Error('Consumable stacks remained in bag');
 await click('战斗');await click('腰带:0:');
 if(a.mapId!=='H00'||a.hero.x!==40||a.hero.y!==78||a.player.belt[0].quantity!==2)throw Error('Return scroll did not return to remembered town');
 const nativeReturn={map:a.mapId,x:a.hero.x,y:a.hero.y};await click('腰带:1:');
 if(a.mapId!=='A00'||a.hero.x!==86||a.hero.y!==53||a.player.returnTown!=='A00'||a.player.belt[1].quantity!==1)throw Error('Named scroll ignored native item coordinates');
 await click('腰带:2:');if(a.player.belt[2]!==null||a.player.belt[0].quantity!==8||a.player.inventory.length)throw Error('Six return scrolls did not refill assigned belt');
 await click('腰带:3:');if(a.player.belt[3]!==null||a.player.inventory.find(e=>e.itemId===0)?.quantity!==6)throw Error('Native medicine package unpack failed');
 // Real LPApp.changeMap fails after entering the destination, before art is ready.
 a.player.returnTown='H00';const before=JSON.stringify(a.player),position={x:a.hero.x,y:a.hero.y},visible=a.prepareVisible;
 a.prepareVisible=async()=>{throw Error('Intentional late map-art failure');};try{await click('腰带:0:');}finally{a.prepareVisible=visible;}
 if(a.mapId!=='A00'||a.hero.x!==position.x||a.hero.y!==position.y||JSON.stringify(a.player)!==before||a.platform.load().map!=='A00')throw Error('Failed teleport changed world or consumed scroll');
 a.player.returnTown='A00';await click('背包');await click('腰带:0:');await click('移回背包');
 await click('回城卷');await click('使用');if(a.hero.x!==86||a.hero.y!==52||a.player.inventory.find(e=>e.itemId===59)?.quantity!==7)throw Error('Backpack return scroll use failed');
 await click('放入腰带');await click('战斗');a.save();const saved=a.platform.load();
 if(saved.player.belt[0]?.quantity!==7||saved.player.inventory.find(e=>e.itemId===0)?.quantity!==6||saved.player.returnTown!=='A00')throw Error('Consumable transaction not persisted');
 a.message=null;a.render();return {nativeReturn,namedDestination:{map:'A00',x:86,y:53},scrollsAndPackagesInBelt:true,sixChildrenRefillBelt:true,medicinePackageSixChildren:true,lateMapFailureAtomic:true,bagAndBeltUse:true,returnTownSaved:true,belt:JSON.parse(JSON.stringify(a.player.belt)),inventory:JSON.parse(JSON.stringify(a.player.inventory))};
}
