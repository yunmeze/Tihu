// Runs in the DOM-free WeChat bundle through the existing native API shim.
export async function nativeHeadScenario(){
 const a=nativeTest.gameGlobal.lpLegend;
 await a.entry.show('create');if(a.entry.previewAppearance.head!==0)throw Error('Native creation preview has a default hat');await a.entry.choose('gender',1);if(a.entry.previewAppearance.head!==1)throw Error('Native female preview has a default hat');a.screen='game';
 a.save();const saved=a.platform.load(),gold=saved.player.gold,equipment=JSON.stringify(saved.player.equipment),inventory=JSON.stringify(saved.player.inventory);saved.player.headStyle=2;delete saved.player.headAppearanceModel;if(saved.player.appearanceUnlocks?.hd)delete saved.player.appearanceUnlocks.hd[2];
 await a.startGame(saved,{characterId:a.characterId});const gender=a.player.gender===1?1:0;if(a.appearance.head!==gender||a.player.headStyle!==gender||a.player.gold!==gold||JSON.stringify(a.player.equipment)!==equipment||JSON.stringify(a.player.inventory)!==inventory)throw Error('Native old hat migration lost appearance/progress');
 a.tab='角色';const heads=[],original=a.batch.frame;a.batch.frame=function(pack,index,x,y,scale,...rest){if(pack.id.startsWith('Hero/Head/'))heads.push({pack:pack.id,scale});return original.call(this,pack,index,x,y,scale,...rest);};try{a.render();}finally{a.batch.frame=original;}
 if(heads.length!==2||heads.some(h=>h.pack!=='Hero/Head/'+gender)||!heads.some(h=>h.scale===a.worldScale)||!heads.some(h=>h.scale!==a.worldScale))throw Error('Native hair differs between scene and character panel');
 a.save();if(a.platform.load().player.headStyle!==gender||a.platform.load().player.headAppearanceModel!=='native-hair-v1')throw Error('Native migrated hair was not saved');
 return {nativeMaleFemalePreviews:true,legacyForcedHatRemoved:true,worldAndPortraitHair:true,progressPreserved:true,migrationSaved:true};
}
