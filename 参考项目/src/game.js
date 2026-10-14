import {setMonsterDifficulty} from './monster-rebirth.js';
import {magicShieldVisible} from './magic-shield.js';
import {drawNativeParticles} from './native-particles.js';
import {ambientParticlePack} from './ambient-particles.js';
import {prepareQuestJournal,drawQuestJournal} from './quest-journal.js';
import {neededEffectPacks} from './effect-resources.js';
import {openingDestination,restoreOpening} from './opening.js';
import {resolveLanding,rememberMapPosition} from './map-landing.js';
import {AUTO_SKILL_LIMIT,normalizeAutoSkills,activateAutoSkill,toggleAutoSkill,removeAutoSkill} from './auto-skill-config.js';
import {PASSIVE_SKILLS} from './skill-roles.js';
import {normalizeEndingPlayer,restoreEnding,advanceEnding} from './ending.js';
import {drawEnding} from './ending-ui.js';
import {challengeTime,isChallengeMap,challengeDestinationAllowed} from './challenges.js';
import {drawAura,auraVictim,DARK_AURA} from './dark-aura.js';
import {ringRule,ringRemaining,normalizeRings,activateRing} from './ring-items.js';
import {holdPointer,rememberPointer,cancelContinuous,toggleAutoRun,updateContinuousMovement} from './continuous-movement.js';
import {isBeltConsumable,putInBelt,returnFromBelt} from './belt.js';
import {useCarriedConsumable,consumableDescription,returnTown,captureWorld,restoreWorld,restorePlayer} from './consumables.js';
import {drawBelt} from './belt-ui.js';
import {firstQuestTarget} from './first-quest-target.js';
import {followQuestTarget,updateQuestTravel,questPortal,questTransfer} from './quest-navigation.js';
import {findNearestPath} from './pathfinding.js';
import {inventoryKey,findInventory,takeItem,mergeItem,sameItemStack} from './inventory.js';
import {classAllowsSkill,visibleSkillRecords,learnedClassSkills,normalizeActiveClassSkill} from './skill-classes.js';
import {carryState,instanceItem} from './native-stats.js';
import {AudioBus} from './audio.js';
import {itemName} from './item-names.js';
import {effectPack,EFFECT_PACKS,EFFECT_VARIANTS} from './projectiles.js';
import {effectFrame,effectRotation} from './effect-animation.js';
import {labelTop} from './combat-text.js';
import {drawWorldText} from './world-text-renderer.js';
import {groundLabelHit} from './world-label-layout.js';
import {statusTint,actorOpacity} from './statuses.js';
import {drawAttributeDialog,skillEligibility,improveSkill,skillDescription} from './growth.js';
import {experienceProgress} from './progression.js';
import {drawItemProperties} from './item-details.js';
import * as T from 'three';
import {WORLD_VIEW,worldView} from './world-view.js';
import {mapLayer,compareWorldObjects} from './map-flags.js';
import {MAP_GROUPS as GROUPS,mapSpriteExtents,visibleMapCells} from './map-visibility.js';
import {mapObjectFrame,mapObjectFrames,MAP_EFFECT_RULES} from './map-effects.js';
import {animationFrame,monsterModelVisible} from './animation.js';
import {drawSelectionRing} from './selection-ring.js';
import {normalizePermanent,insightOn,placePendingLoot} from './permanent-state.js';
import {drawPermanentHud,drawFeatureDialog,prepareFeature,featureSpriteRequests} from './permanent-ui.js';
import {updateInsightAutomation} from './insight-automation.js';
import {characterAppearance,appearancePacks,avatarLayers,avatarBounds,fitAvatar,drawAvatarLayers} from './appearance.js';
import {groundItemIcon} from './loot.js';
import {mapViewport,mapMarker,fitMinimap,minimapCoverage} from './minimap.js';
import {canEnterCell} from './map-flags.js';
import {nearbyColumn} from './nearby-layout.js';
import {drawService,prepareService,serviceAction} from './service-ui.js';
import {nearbyNpcs,hasNpcInteraction,readNpcDialogue} from './npc-dialogue.js';
import {restoreScriptWorld,executeScriptView} from './npc-world.js';
import {Content} from './content.js';import {Batch} from './batch.js';import {Hud} from './hud.js';
import {SaveRoster} from './save-roster.js';import {EntryScreens} from './entry-screens.js';
import {createCharacter,equipmentEligibility,createNewCharacter,attributes,EQUIPMENT,SKILL_ORDER,equip,unequip,taskFor} from './character.js';import {Combat,COMBAT_RULES} from './combat.js';
const GM_SECTORS=[['解锁全技能',Math.PI*5/6,Math.PI*1.5,245,700],['清档',-Math.PI/2,Math.PI/6,505,700],['获得100技能点',Math.PI/6,Math.PI*5/6,375,930]];
export class LPApp {
 constructor(platform){Object.assign(this,{platform,content:new Content(platform),elapsed:0,previous:0,loading:true,tab:'战斗',page:0,buttons:[],packs:new Map(),worldScale:1.6,combatReady:true,nextSave:5});}
 async init(){
  const p=this.platform,context=p.canvas.getContext('webgl2',{alpha:false,antialias:false});if(!context)throw Error('WebGL2 is required');
  this.renderer=new T.WebGLRenderer({canvas:p.canvas,context,antialias:false});this.renderer.setClearColor('#14130f');this.renderer.outputColorSpace=T.SRGBColorSpace;this.batch=new Batch(this.content);this.worldTarget=new T.WebGLRenderTarget(WORLD_VIEW.width,WORLD_VIEW.height,{minFilter:T.LinearFilter,magFilter:T.LinearFilter,depthBuffer:false,stencilBuffer:false});this.worldTarget.texture.colorSpace=T.SRGBColorSpace;
  await this.content.init();this.audio=new AudioBus(p,this.content.sounds,this.content.audioRules);this.audio.position=()=>this.combat?.position;this.audio.combat=()=>this.combat;this.hud=new Hud(this.content,this.batch);await this.hud.init();this.batch.skin=this.hud;this.roster=new SaveRoster(p.load(),this.content);this.entry=new EntryScreens(this);await this.entry.init();this.screen='home';
  p.pointer((x,y,input)=>this.pointer(x,y,input),()=>{},(phase,x,y,input)=>holdPointer(this,phase,x,y,input));p.key?.((down,cancel)=>this.gmKey(down,cancel));p.shortcut?.(code=>this.shortcut(code).catch(e=>console.error(e)));p.hover?.((x,y)=>{rememberPointer(this,x,y);if(this.gmOpen)this.gmSelection=this.gmChoice(x,y);});p.resize(()=>this.resize());p.hide(()=>{cancelContinuous(this);this.hidden=true;this.audio.pause(true);this.gmKey(false,true);this.save();});p.show(()=>{this.hidden=false;this.audio.pause(false);this.previous=0;});this.resize();this.loading=false;this.tick=this.tick.bind(this);this.render();this.frame=p.frame(this.tick);return this;
 }
 async createGame(player){
  const previous=this.roster.serialize(),d=openingDestination(this.content);if(!d)throw Error('Missing native opening destination');player.events[0]=1;if(!player.unlockedMaps.includes(d.id))player.unlockedMaps.push(d.id);
  const state={version:2,map:d.id,position:{x:d.x,y:d.y},story:{version:1,kind:'opening',phase:'reading',page:0},player,groundItems:{},pets:[],mapFlagsByMap:{}},id=this.roster.add(state);
  try{await this.startGame(state,{characterId:id});}catch(e){this.roster=new SaveRoster(previous,this.content);throw e;}
 }
 async startGame(saved={}, {characterId=null}={}){
  if(this.entering||this.itemBusy||this.disposed)return false;cancelContinuous(this);this.lastWorldPointer=null;this.lastItemTap=null;this.entering=true;this.screen='loading';this.systemMenu=false;
  try{if(this.preparing)await this.preparing;this.sessionLoaded=false;this.map=null;this.mapId=null;this.player=normalizePermanent(normalizeActiveClassSkill(createCharacter(this.content,saved),this.content),this.content);normalizeRings(this.player);normalizeEndingPlayer(this.player);this.roster.bindDimension(this.player,this.content);normalizeAutoSkills(this.player,this.content);this.heroClass=this.player.class;this.mapFlagsByMap=saved.mapFlagsByMap||{};this.scriptState=saved.scriptState||{};this.combat=new Combat(this.player,this.content,Math.random,saved.groundItems,Math.random,Math.random,saved.pets,saved.map==='J30'?saved.defense:null,['E30','C30'].includes(saved.map)?saved.challenge:null);this.combat.story=restoreOpening(this.content,saved.story)||restoreEnding(this.player,this.content,saved.story);this.combat.audio=this.audio;this.characterId=characterId||this.roster.activeId||this.roster.nextId();
   this.featureView=null;this.selectedSkill=null;this.selectedEquipment=null;this.skillPage=0;this.serviceView=null;this.npcDialogue=null;this.pendingNpc=null;this.attributeOpen=false;this.mapOpen=false;this.tab='战斗';this.message=null;this.portalDelay=0;this.lastPreparedCell=null;
   await Promise.all(['Npc','Item1','Data7'].map(id=>this.loadPack(id)));await Promise.all(Array.from({length:10},(_,i)=>this.content.frame('Data7',i+1)));await this.updateAppearance();await this.prepareCombatArt();const map=saved.version===2&&this.player.unlockedMaps.includes(saved.map)&&challengeDestinationAllowed(this.combat,saved.map)?saved.map:'A00';await this.changeMap(map,saved.version===2&&map===saved.map?saved.position:null);if(this.disposed)return false;this.sessionLoaded=true;this.entry.selectedId=this.characterId;this.screen='game';this.nextSave=this.elapsed+5;this.entering=false;this.save();this.render();return true;
  }catch(e){this.screen=this.roster.characters.length?'characters':'home';this.entry.error='进入游戏失败，请重试';throw e;}finally{this.entering=false;}
 }
 // Revival is one guarded transition; save only after map and hero agree.
 async reviveAtTown(){
  if(this.screen!=='game'||this.player.hp>0||this.reviving||this.itemBusy||this.changing||this.disposed)return false;
  const town=returnTown(this.player,this.content);if(!town)return false;
  this.reviving=true;
  try{
   // Native 588d74 reads the town prefix remembered by map loader 59e0a0.
   // Its #move <prefix>00 0 0 returns to that town's original home point.
   if(!await this.changeMap(town.id,{x:town.home[0],y:town.home[1]},{unlock:true}))return false;
   if(this.disposed)return false;
   this.combat.revive({x:this.map.home[0],y:this.map.home[1]});this.hero=this.combat.position;this.camera={x:this.hero.x,y:this.hero.y};this.pendingNpc=null;this.tab='战斗';this.mapOpen=false;this.portalDelay=this.elapsed+3;this.lastPreparedCell=null;await this.prepareVisible();return true;
  }finally{this.reviving=false;this.save();}
 }
 async returnHome({save=true}={}){this.questTravel=null;cancelContinuous(this);if(this.itemBusy)return;this.audio.battle(false);if(save)this.save();else this.roster=new SaveRoster(this.platform.load(),this.content);this.featureView=null;this.combat?.stopFarming();this.systemMenu=false;this.gmOpen=false;this.serviceView=null;this.npcDialogue=null;this.attributeOpen=false;this.mapOpen=false;await this.entry.show('home');}
 async loadPack(id){if(!this.packs.has(id))this.packs.set(id,await this.content.pack(id));return this.packs.get(id);}
 setDifficulty(mode){const p=this.player;if(!Number.isInteger(mode)||mode<0||mode>2||mode>Math.max(p.gameMode||0,p.modeUnlock||0)){this.notify('通关上一模式后解锁');return false;}if(mode===p.gameMode)return true;p.gameMode=mode;for(const u of this.units)setMonsterDifficulty(u,this.content.monsters[u.definition.id],p);this.save();return true;}
 async openFeature(kind,options={}){if(kind==='hotkeys')return;if(this.screen!=='game'||this.combat?.story||this.itemBusy||this.changing||this.reviving)return;this.systemMenu=false;this.gmOpen=false;this.lastMoveTap=null;this.featureView={kind,page:0,sub:'monsters',...options};await prepareFeature(this);}
 closeFeature(){const exit=this.featureView?.kind==='exit';this.featureView=null;if(exit)this.systemMenu=true;}
 async shortcut(code){
  if(this.screen!=='game'||this.itemBusy||this.entering||this.changing||this.reviving||this.resetting||this.npcBusy||this.growthBusy||this.serviceBusy||this.gmBusy||this.entry.editing)return;
  if(this.combat.story){if(['Space','Enter','ArrowRight'].includes(code))await advanceEnding(this);if(code==='ArrowLeft')await advanceEnding(this,-1);return;}
  if(code==='Escape'){this.questTravel=null;if(this.featureView)this.closeFeature();else if(this.systemMenu)this.systemMenu=false;else if(this.mapOpen)this.mapOpen=false;else if(this.attributeOpen)this.attributeOpen=false;else if(this.npcDialogue)this.npcDialogue=null;else if(this.serviceView)this.serviceView=null;else this.systemMenu=true;return;}
  if(this.systemMenu||this.featureView||this.mapOpen||this.attributeOpen||this.npcDialogue||this.serviceView||this.gmOpen||this.player.hp<=0||this.combat.scriptLocked)return;
  if(code==='Space'){toggleAutoRun(this);return;}
  if(code==='KeyY'){await this.useRing('隐身戒指',{keyboard:true});return;}
  if(code==='KeyM'){await this.openFeature('pets');return;}
  this.save();
 }
 async discardSelected(){
  if(this.player.hp<=0||this.itemBusy||this.changing)return;const list=this.player.inventory,e=findInventory(list,this.selectedItem);if(!e)return;const before=JSON.parse(JSON.stringify(list)),oldPending=this.player.pendingGroundItems,drop=takeItem(list,this.selectedItem,e.quantity);
  this.player.pendingGroundItems=[...(oldPending||[]),{...drop,kind:'item',discarded:true}];
  if(!placePendingLoot(this.combat)){this.player.inventory=before;this.player.pendingGroundItems=oldPending;return;}
  this.combat.stopFarming();this.featureView=null;this.selectedItem=null;await this.prepareOwned();await this.prepareVisible();this.save();
 }
 sortBag(){const selected=findInventory(this.player.inventory,this.selectedItem),sorted=[];for(const entry of [...this.player.inventory].sort((a,b)=>a.itemId-b.itemId))if(!mergeItem(sorted,entry.itemId,entry.quantity,entry))return false;this.player.inventory=sorted;this.selectedItem=inventoryKey(selected&&sorted.find(e=>sameItemStack(e,selected)));return true;}
 async equipBagItem(entry){const item=instanceItem(this.content.items[entry.itemId],entry),check=equipmentEligibility(this.player,this.content,item.id,entry);if(!check.allowed){this.notify(check.reason);return;}if(equip(this.player,this.content,inventoryKey(entry))){this.audio.ui('按键2');await this.updateAppearance();await this.prepareOwned();}else this.notify('背包空间不足');}
 async bagQuickAction(entry,{right=false,shift=false}={}){this.selectedItem=inventoryKey(entry);this.selectedBelt=null;const item=instanceItem(this.content.items[entry.itemId],entry),kind=this.serviceView?.kind;if(shift)return this.discardSelected();if(right&&['storage','dimension'].includes(kind)){this.serviceView.quantity=1;return serviceAction(this,'deposit');}if(kind==='sell'){this.serviceView.quantity=1;return serviceAction(this,'sell');}if(ringRule(item))return this.useRing(item.name);if(isBeltConsumable(item))return this.useBagItem(inventoryKey(entry));if(EQUIPMENT.some(e=>e[2]===item.type))return this.equipBagItem(entry);}
 async updateAppearance(){
  const appearance=characterAppearance(this.player,this.content),request=this.appearanceRequest=(this.appearanceRequest||0)+1;
  this.appearanceLoading=true;
  try{const preload=async id=>{const pack=await this.loadPack(id);await Promise.all(pack.frames.slice(1,281).map((_,index)=>this.content.frame(id,index+1)));};await Promise.all(appearancePacks(appearance).map(preload));await this.content.sync();if(request!==this.appearanceRequest||this.disposed)return;this.appearance=appearance;this.heroAppearance=appearance.body;this.weaponAppearance=appearance.weapon;if(this.map)await this.prepareVisible();}
  finally{if(request===this.appearanceRequest)this.appearanceLoading=false;}
 }

 async changeMap(id,position=null,{unlock=false,debug=false,consumable=false,quest=false}={}){if(!quest)this.questTravel=null;cancelContinuous(this);if(this.changing||this.itemBusy&&!consumable)return false;if(!debug&&!challengeDestinationAllowed(this.combat,id))return false;if(!debug&&!unlock&&(this.combat.scriptLocked||!this.player.unlockedMaps.includes(id)))return false;const rollback=this.map?captureWorld(this):null,savedPlayer=JSON.parse(JSON.stringify(this.player));this.changing=true;const transporting=this.sessionLoaded;this.audio.stopEffects();try{if(this.preparing)await this.preparing;if(this.map&&this.hero)rememberMapPosition(this.player,this.map,this.hero);const map=await this.content.json('maps/'+id+'.json');if(unlock&&!this.player.unlockedMaps.includes(id))this.player.unlockedMaps.push(id);this.featureView=null;this.attributeOpen=false;this.map=map;this.mapId=id;this.pendingNpc=null;this.npcDialogue=null;this.nearbyPages={npc:0,monster:0};this.serviceView=null;for(const [x,y,flag]of this.mapFlagsByMap?.[id]||[])if(Number.isInteger(x)&&Number.isInteger(y)&&Number.isInteger(flag)&&x>=0&&y>=0&&x<map.width&&y<map.height)map.cells[x*map.height+y][1]=flag;restoreScriptWorld(map,this.scriptState?.[id]);const spawn=resolveLanding(map,this.player,this.content.arrivals,position||(id==='J30'?{x:30,y:19}:null));this.combat.scriptState=this.scriptState||={};this.combat.mapFlagsByMap=this.mapFlagsByMap||={};this.combat.enter(map,spawn);const entry=this.combat.runScript(map.loadScript);if(entry.applied&&entry.move?.id===id)Object.assign(this.combat.position,{x:entry.move.x,y:entry.move.y});this.hero=this.combat.position;rememberMapPosition(this.player,map,this.hero,{entry:true});this.camera={x:this.hero.x,y:this.hero.y};this.units=this.combat.units;this.lastMoveTap=null;this.selectedItem=null;this.selectedBelt=null;this.selectedEquipment=null;this.page=0;await Promise.all([...['FloorBig','FloorSmall',...Object.values(GROUPS)].map(g=>this.loadPack('Map/Res/'+g)),this.loadPack('Data4')]);this.mapSpriteExtents=mapSpriteExtents(map,this.packs);const mini=this.content.minimaps.maps[id];const previousMini=this.miniFile;this.miniFile=mini?.file;if(mini)await this.content.texture(mini.file);await this.prepareVisible();await this.prepareOwned();this.audio.prepare(this.combat);if(previousMini&&previousMini!==mini?.file)this.content.releaseTexture(previousMini);if(/^[A-Z]00$/.test(id))this.player.returnTown=id;if(transporting&&!consumable)this.audio.ui('传送1');if(quest&&this.questTravel?.destination===id)this.questTravel.arrived=true;this.save();return true;}catch(error){this.questTravel=null;restorePlayer(this.player,savedPlayer);if(rollback)restoreWorld(this,rollback);throw error;}finally{this.changing=false;}}
 visibleCells({preload=false}={}){const z=this.worldScale,origin=worldView(this.camera,z).origin;return visibleMapCells(this.map,this.packs,{x:origin.x/z,y:origin.y/z,width:WORLD_VIEW.width,height:WORLD_VIEW.height},this.mapSpriteExtents,{padding:preload?49:1});}
 // The active minimap is always visible HUD art. Protect and reload it with
 // the world view, including before its first draw under texture pressure.
 async prepareVisible(){if(this.preparing)return this.preparing;this.audio?.prepare(this.combat);this.preparing=(async()=>{const files=new Set(this.miniFile?[this.miniFile]:[]),addFrame=(id,index)=>{const pack=this.packs.get(id),f=pack?.frames[index];if(f)files.add(pack.pages[f.page].file);},packFrames=async(id,max)=>{const pack=await this.loadPack(id);for(let i=1;i<Math.min(max,pack.frames.length);i++)addFrame(id,i);};for(const {cell,floorVisible,objectVisible}of this.visibleCells({preload:true})){const [floor,,type,index]=cell;if(floor&&floorVisible)addFrame('Map/Res/'+(floor<0?'FloorBig':'FloorSmall'),Math.abs(floor));if(objectVisible)for(const object of mapObjectFrames(cell,this.packs))addFrame(object.pack.id,object.index);}const nearby=this.units.filter(u=>monsterModelVisible(u)&&Math.abs(u.x-this.camera.x)<17&&Math.abs(u.y-this.camera.y)<26);await Promise.all([...new Set(nearby.map(u=>'Mon/'+u.definition.appearance))].map(id=>packFrames(id,217)));for(const n of this.map.npcs.filter(n=>!n.removed&&Math.abs(n.x-this.camera.x)<17&&Math.abs(n.y-this.camera.y)<26))for(let phase=0;phase<4;phase++)addFrame('Npc',1+n.appearance*12+n.direction*4+phase);for(const g of this.combat.groundItems||[])if(Math.abs(g.x-this.camera.x)<17&&Math.abs(g.y-this.camera.y)<26)addFrame('Item1',g.kind==='gold'?groundItemIcon(g):instanceItem(this.content.items[g.itemId],g).icon);await Promise.all(appearancePacks(this.appearance).map(id=>packFrames(id,281)));const effects=await this.prepareCombatArt(nearby);for(const file of effects)files.add(file);this.worldArtFiles=new Set(files);for(const [id,index]of featureSpriteRequests(this)){await this.loadPack(id);addFrame(id,index);}this.visibleArtFiles=files;await Promise.all([...files].filter(f=>!this.content.textureNow(f)).map(f=>this.content.texture(f)));await this.content.sync();this.content.trimTextures(files);})().finally(()=>this.preparing=null);return this.preparing;}
 async prepareCombatArt(units=[]){const files=new Set();const packs=neededEffectPacks(this.player,units,[...(this.combat?.effects||[]),...(this.combat?.projectiles||[])],this.content);const particlePacks=new Set([ambientParticlePack(this.combat),(this.combat?.groundItems||[]).some(g=>g.kind==='item'&&insightOn(this.player,4)&&((g.fieldOverrides?.[24]??this.content.items[g.itemId]?.rawFields[24]??0)>0))?'Data8':null].filter(Boolean));for(const id of particlePacks){const p=await this.loadPack(id);for(const page of p.pages)files.add(page.file);}await this.loadPack('Data4');for(const i of DARK_AURA.frames){const p=this.packs.get('Data4'),f=p.frames[i];if(f)files.add(p.pages[f.page].file);}await Promise.all([...packs].map(async id=>{const p=await this.loadPack(id);for(const page of p.pages)files.add(page.file);}));await Promise.all([...files].filter(f=>!this.content.textureNow(f)).map(f=>this.content.texture(f)));await this.content.sync();return files;}
 async useRing(name,options){const result=await activateRing(this,name,options);if(!result.ok)this.notify(result.reason);return result;}
 async activateSkill(name){if(this.combat.scriptLocked)return {ok:false};const result=activateAutoSkill(this.player,this.content,name);if(!result.ok)this.notify(result.reason);else {await this.prepareOwned();this.audio.prepare(this.combat);this.save();}return result;}
 toggleSkill(name){if(this.combat.scriptLocked)return;toggleAutoSkill(this.player,name);this.save();}
 removeSkill(name){if(this.combat.scriptLocked)return;removeAutoSkill(this.player,name);this.save();}
 drawCombatEffect(effect){if(effect.shield&&!magicShieldVisible(this.combat))return;const pack=this.packs.get(effectPack(effect.type,effect.variant));if(!pack)return;const index=effectFrame(effect,pack);if(index===null)return;const p=this.mapPoint(effect.x,effect.y),f=pack.frames[index],z=this.worldScale;
  const rotation=effectRotation(effect);if(rotation!==null){this.batch.rotatedFrame(pack,index,p.x+24*z,p.y-20*z,z,z,rotation);return;}
  // Zero-offset effect sheets use a centered canvas; cropped borders must not
  // move the visible projectile away from its collision point.
  if(f.offset[0]===0&&f.offset[1]===0)this.batch.frame(pack,index,p.x+(24-f.original[0]/2)*z,p.y-(20+f.original[1]/2)*z,z,'#ffffff',false);
  else this.batch.frame(pack,index,p.x,p.y,z);
 }
 drawWorldLabels(){drawWorldText(this);}
 async prepareOwned(){normalizeAutoSkills(this.player,this.content);await this.prepareCombatArt();await Promise.all([...[...this.player.inventory,...(this.player.belt||[]).filter(Boolean)].map(e=>instanceItem(this.content.items[e.itemId],e)),...Object.entries(this.player.equipment).map(([slot,id])=>instanceItem(this.content.items[id],this.player.equipmentMeta?.[slot]))].map(item=>this.content.frame('Item1',item.icon)));for(const s of this.player.skills){const a=this.hud.index.assets['skill-'+(1+this.content.skills.records.find(r=>r.name===s.name).nativeIndex*3)];if(a)await this.content.texture(a.file);}await this.content.sync();}
 resize(){const {width,height,dpr}=this.platform.size();Object.assign(this,{width,height,scale:Math.min(width/750,height/1624)});this.left=(width-750*this.scale)/2;this.top=(height-1624*this.scale)/2;this.batch.pixelGrid={scale:this.scale*dpr,left:this.left*dpr,top:this.top*dpr};this.renderer.setPixelRatio(dpr);this.renderer.setSize(width,height,false);}
 toLogical(x,y){return {x:(x-this.left)/this.scale,y:(y-this.top)/this.scale};}
 notify(message){this.message=message;this.messageUntil=this.elapsed+2.5;}
 async pointer(x,y,input={}){const firstSoundGesture=!this.audio.unlocked;this.audio.unlock();if(firstSoundGesture)this.audio.prepare(this.combat);const p=this.toLogical(x,y);if(this.itemBusy||this.reviving||this.resetting||this.growthBusy||this.gmBusy||this.npcBusy||this.serviceBusy||this.changing||this.entering||this.entry?.editing)return;this.questTravel=null;cancelContinuous(this);if(this.gmOpen){if(input.button===2)return;const choice=this.gmChoice(x,y);if(choice)await this.gmCommand(choice);return;}for(const b of [...this.buttons].reverse())if(p.x>=b.x&&p.y>=b.y&&p.x<=b.x+b.w&&p.y<=b.y+b.h){this.lastMoveTap=null;if(input.button===2&&!b.rightClick)return;try{const menuControl=this.systemMenu||this.featureView?.kind==='exit'||b.label==='菜单';this.audio.ui(/物品|存档:/.test(b.label)?'选取':'按键1');const now=input.time??Date.now(),key=b.label+':'+b.x+':'+b.y,old=this.lastItemTap;let action=b.action;if(input.longPress&&b.longPress){action=b.longPress;this.lastItemTap=null;}else if(input.button===2){action=b.rightClick;this.lastItemTap=null;}else if(input.shiftKey&&b.shiftClick){action=b.shiftClick;this.lastItemTap=null;}else if(b.doubleClick&&old?.key===key&&now-old.time>=0&&now-old.time<=350){action=b.doubleClick;this.lastItemTap=null;}else this.lastItemTap=b.doubleClick?{key,time:now}:null;await action();if(!menuControl)this.save();}catch(e){console.error(e);this.notify('操作未完成');}return;}if(this.screen!=='game'||this.combat?.story||this.systemMenu)return;if(this.featureView){if(p.x<38||p.x>712||p.y<228||p.y>1394)this.closeFeature();return;}if(this.serviceView)return;if(this.npcDialogue){if(p.x<38||p.x>712||p.y<356||p.y>1286)this.npcDialogue=null;return;}if(this.attributeOpen){if(p.x<68||p.x>682||p.y<405||p.y>1224)this.attributeOpen=false;return;}if(this.mapOpen){if(p.x<38||p.x>712||p.y<238||p.y>1343)this.mapOpen=false;return;}if(p.x<0||p.x>750||p.y<0||p.y>(this.tab==='战斗'?1535:1040))return;if(this.player.hp<=0)return;const loot=groundLabelHit(this.worldText,p,this.combat.groundItems)||this.combat.groundItems.find(g=>{const q=this.screenPoint(g.x,g.y);return Math.hypot(p.x-q.x-24*this.worldScale,p.y-q.y-24*this.worldScale)<35;});if(loot){this.lastMoveTap=null;this.pendingNpc=null;if(this.combat.collect(loot.id))await this.prepareVisible();return;}this.pendingNpc=null;const nx=Math.round(this.camera.x+(p.x-375)/(48*this.worldScale)),ny=Math.round(this.camera.y+(p.y-555)/(32*this.worldScale));this.combat.moveTo(nx,ny);}
 button(label,x,y,w,h,action,selected=false,font=28){this.hud.button(x,y,w,h,selected);this.batch.text(label,x+12,y+(h-font)/2,font,selected?'#ffe0a0':'#d5c49f',w-24);this.region(label,x,y,w,h,action);}
 region(label,x,y,w,h,action,shortcuts={}){this.buttons.push({label,x,y,w,h,action,...shortcuts});}
 mapPoint(x,y){const z=this.worldScale,o=worldView(this.camera,z).origin;return {x:o.x+x*48*z,y:o.y+y*32*z};}
 screenPoint(x,y){return {x:375+(x-this.camera.x)*48*this.worldScale,y:555+(y-this.camera.y)*32*this.worldScale};}
 animationFrame(actor,family='hero'){return animationFrame(actor,family);}
 drawGroundItem(g){const pack=this.packs.get('Item1'),item=g.kind==='gold'?null:instanceItem(this.content.items[g.itemId],g),index=item?item.icon:groundItemIcon(g),f=pack.frames[index],p=this.mapPoint(g.x,g.y),z=this.worldScale;if(!f)return;this.batch.frame(pack,index,p.x+(24-f.original[0]/2)*z,p.y+(24-f.original[1]/2)*z,z,'#ffffff',false);}
 drawWorld(){const b=this.batch;b.quad(0,0,WORLD_VIEW.width*this.worldScale,WORLD_VIEW.height*this.worldScale,'#292d23');const cells=this.visibleCells();for(const {x,y,cell,floorVisible}of cells){const floor=cell[0];if(!floor||!floorVisible)continue;const pack=this.packs.get('Map/Res/'+(floor<0?'FloorBig':'FloorSmall')),p=this.mapPoint(x,y);if(pack)b.frame(pack,Math.abs(floor),p.x,p.y,this.worldScale,'#ffffff',false);}const objects=[];for(const {x,y,cell,objectVisible}of cells){const flag=cell[1];if(!objectVisible)continue;const object=mapObjectFrame(cell,this.packs,this.elapsed);if(object)objects.push({layer:mapLayer(flag),y,draw:()=>{const p=this.mapPoint(x,y);b.frame(object.pack,object.index,p.x,p.y+object.top*this.worldScale,this.worldScale,'#ffffff',false);}});}for(const g of this.combat.groundItems){if(Math.abs(g.x-this.camera.x)>16||Math.abs(g.y-this.camera.y)>25)continue;objects.push({layer:.5,y:g.y,draw:()=>this.drawGroundItem(g)});}const phase=Math.floor((this.elapsed+1e-8)*MAP_EFFECT_RULES.sourceFps/MAP_EFFECT_RULES.npcFrameTicks)%4;for(const n of this.map.npcs){if(n.removed)continue;if(Math.abs(n.x-this.camera.x)>16||Math.abs(n.y-this.camera.y)>25)continue;objects.push({layer:1,y:n.y,draw:()=>{const p=this.mapPoint(n.x,n.y);b.frame(this.packs.get('Npc'),1+n.appearance*12+n.direction*4+phase,p.x,p.y,this.worldScale);}});}for(const u of this.units){if(!monsterModelVisible(u)||Math.abs(u.x-this.camera.x)>16||Math.abs(u.y-this.camera.y)>25)continue;const pack=this.packs.get('Mon/'+u.definition.appearance);if(!pack)continue;if(u.alive&&u.id===this.combat.targetId)objects.push({layer:.7,y:u.y,draw:()=>{const p=this.mapPoint(u.x,u.y);drawSelectionRing(b,pack,p.x,p.y,this.worldScale);}});objects.push({layer:u.alive?1:.6,y:u.y,draw:()=>{const p=this.mapPoint(u.x,u.y);b.frame(pack,this.animationFrame(u,'monster'),p.x,p.y,this.worldScale,statusTint(u),true,actorOpacity(u));}});}if(this.player.aura===2&&this.player.hp>0){objects.push({layer:.72,y:this.hero.y,draw:()=>drawAura(this,this.hero)});for(const u of this.units)if(auraVictim(this.combat,u)&&this.combat.inRange(u))objects.push({layer:.72,y:u.y,draw:()=>drawAura(this,u,{enemy:true})});}objects.push({layer:1,y:this.hero.y,draw:()=>{const p=this.mapPoint(this.hero.x,this.hero.y);this.drawAvatar(this.hero,p.x,p.y,this.worldScale,{tint:statusTint(this.player),opacity:this.player.invisible?.45:1});}});for(const effect of [...this.combat.effects,...this.combat.projectiles])if(Math.abs(effect.x-this.camera.x)<17&&Math.abs(effect.y-this.camera.y)<26)objects.push({layer:[19,40].includes(effect.type)?.75:1,y:effect.y,draw:()=>this.drawCombatEffect(effect)});objects.sort(compareWorldObjects);for(const o of objects)o.draw();drawNativeParticles(this);}
 drawChrome(){drawPermanentHud(this);const x=540,y=20;this.hud.button(x,y,192,170);this.drawMinimap(x+7,y+7,178,127,true);this.hud.centered(this.map.name,x+7,y+140,178,24,'#e2cf9f');this.region('地图',x,y,192,170,()=>{this.mapOpen=true;this.mapPage=0;});if(this.tab!=='战斗'){this.batch.quad(0,1040,750,584,'#211915');this.hud.base(1040,584);}if(!this.serviceView)this.drawNearby();else this.sidebarVisible=[];}
 drawMinimap(x,y,w,h,local=false){
  const b=this.batch,view=mapViewport(this.map,this.hero,local),rect=fitMinimap(view,x,y,w,h),mini=this.content.minimaps.maps[this.mapId],texture=mini&&this.content.textureNow(mini.file);b.quad(rect.x,rect.y,rect.w,rect.h,'#171910');
  const coverage=texture&&minimapCoverage(view,mini),step=Math.max(1,Math.ceil(Math.max(view.width,view.height)/80));
  for(let gx=Math.floor(view.x);gx<view.x+view.width;gx+=step)for(let gy=Math.floor(view.y);gy<view.y+view.height;gy+=step){if(texture&&gx+step<=mini.width/7&&gy+step<=mini.height/5)continue;const cell=this.map.cells[gx*this.map.height+gy];if(cell&&canEnterCell(cell[1])){const left=Math.max(view.x,gx),top=Math.max(view.y,gy),right=Math.min(view.x+view.width,gx+step),bottom=Math.min(view.y+view.height,gy+step);b.quad(rect.x+(left-view.x)/view.width*rect.w,rect.y+(top-view.y)/view.height*rect.h,(right-left)/view.width*rect.w,(bottom-top)/view.height*rect.h,'#7b7655');}}
  if(coverage?.width&&coverage.height)b.quad(rect.x+(coverage.x-view.x)/view.width*rect.w,rect.y+(coverage.y-view.y)/view.height*rect.h,coverage.width/view.width*rect.w,coverage.height/view.height*rect.h,'#ffffff',texture,[coverage.x*7/mini.width,coverage.y*5/mini.height,coverage.width*7/mini.width,coverage.height*5/mini.height]);
  const p=mapMarker(view,this.hero,rect),mx=Math.max(rect.x+4,Math.min(rect.x+rect.w-5,p.x)),my=Math.max(rect.y+4,Math.min(rect.y+rect.h-5,p.y));b.quad(mx-4,my-4,9,9,'#efe8c3');b.quad(mx-2,my-2,5,5,'#e73722');
 }
 drawMapDialog(){
  const b=this.batch,h=this.hud,list=this.player.unlockedMaps.filter(id=>!isChallengeMap(id)).map(id=>this.content.mapList.find(m=>m.id===id)).filter(Boolean),pages=Math.max(1,Math.ceil(list.length/4));this.mapPage=Math.min(this.mapPage||0,pages-1);this.buttons=[];
  b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.58);b.quad(38,238,674,1105,'#211915');h.panel(38,238,674,1105);b.text(this.map.name,70,272,34,'#e8c887',446);this.button('关闭地图',548,260,134,70,()=>this.mapOpen=false,false,27);this.drawMinimap(70,362,610,440);b.text('已解锁地图',70,825,30,'#d9bd88');
  list.slice(this.mapPage*4,this.mapPage*4+4).forEach((m,i)=>this.button(m.name,70,878+i*84,610,72,async()=>{if(this.player.hp<=0)return;if(m.id!==this.mapId)await this.changeMap(m.id);this.attributeOpen=false;this.mapOpen=false;this.tab='战斗';},m.id===this.mapId,28));
  if(pages>1){this.button('上一页',70,1244,172,66,()=>this.mapPage=Math.max(0,this.mapPage-1),false,27);h.centered((this.mapPage+1)+' / '+pages,292,1265,166,26);this.button('下一页',508,1244,172,66,()=>this.mapPage=Math.min(pages-1,this.mapPage+1),false,27);}
 }
 async selectTarget(id){const unit=this.units.find(u=>u.id===id&&u.alive);if(!unit)return;this.pendingNpc=null;if(!this.combat.startFarming(unit.definition.id,id))return;await this.prepareVisible();}
 async selectMonsterType(id){this.pendingNpc=null;if(this.combat.farmType===id){this.combat.stopFarming();return;}if(this.combat.startFarming(id))await this.prepareVisible();}
 nearbyEntries(){return [...nearbyNpcs(this.map,this.hero).sort((a,b)=>a.index-b.index),...this.combat.nearbyTypes().sort((a,b)=>a.monsterId-b.monsterId)];}
 drawNearby(){
  const entries=this.frameNearbyEntries||this.nearbyEntries();this.nearbyPages||={npc:0,monster:0};this.sidebarVisible=[];
  for(const kind of ['npc','monster']){const list=entries.filter(e=>e.kind===kind),selected=list.find(e=>kind==='npc'?e.index===this.pendingNpc?.index:e.monsterId===this.combat.farmType),column=nearbyColumn(list,kind,this.tab,this.nearbyPages[kind],selected);this.nearbyPages[kind]=column.page;this.sidebarVisible.push(...column.visible);
   for(const {entry,x,y,w,h}of column.rows){const npc=kind==='npc',active=entry===selected,name=npc?entry.name:entry.definition.name;this.batch.quad(x+3,y+6,w-6,h-12,'#17120d',this.batch.white,[0,0,1,1],active?.78:.58);if(active){if(npc)this.hud.outlineSlot(x,y+3,w,h-6,true);else this.hud.flowFrame(x,y+3,w,h-6,this.elapsed);}this.hud.centered(name,x+8,y+17,w-16,26,active?'#ffe3a0':npc?'#ead193':'#ded2b5');this.region(npc?'NPC:'+entry.index:'怪物种类:'+entry.monsterId,x,y,w,h,()=>npc?this.selectNpc(entry.index):this.selectMonsterType(entry.monsterId));}
   if(column.pages>1){this.button('‹',column.x,column.pagerY,80,40,()=>this.nearbyPages[kind]=(column.page+column.pages-1)%column.pages,false,24);this.button('›',column.x+88,column.pagerY,80,40,()=>this.nearbyPages[kind]=(column.page+1)%column.pages,false,24);}
  }
 }
 hitNpc(point,npc){const p=this.screenPoint(npc.x,npc.y),pack=this.packs.get('Npc'),first=1+npc.appearance*12,f=pack?.frames[first+npc.direction*4];if(!f)return false;const z=this.worldScale,x=p.x+(f.offset[0]+f.crop[0])*z,y=p.y+(f.offset[1]+f.crop[1])*z,labelY=p.y+labelTop(pack,first,first+11)*z-35,w=Math.min(280,this.batch.textWidth(npc.name,27)),labelX=p.x+24*z-w/2;return point.x>=x-6&&point.x<=x+f.rect[2]*z+6&&point.y>=y-6&&point.y<=y+f.rect[3]*z+6||point.x>=labelX-6&&point.x<=labelX+w+6&&point.y>=labelY-6&&point.y<=labelY+33;}
 async selectNpc(index,{quest=false}={}){if(!quest)this.questTravel=null;const npc=this.map.npcs[index];if(!npc||!hasNpcInteraction(npc)||this.player.hp<=0)return;this.pendingNpc=null;const route=findNearestPath(this.map,this.hero,npc,(x,y)=>this.combat.walkable(x,y),{range:1,canStop:p=>this.combat.canAttackFrom(p,npc),throughPortals:true}),portal=route?.find(p=>p.viaPortal)?.viaPortal;if(portal){if(!this.combat.moveTo(portal.x,portal.y))return;this.pendingNpc={index,mapId:this.mapId,portal};}else{if(!this.combat.approach(npc))return;this.pendingNpc={index,mapId:this.mapId};}await this.prepareVisible();await this.checkNpcInteraction();}
 async checkNpcInteraction(){const pending=this.pendingNpc;if(!pending||pending.mapId!==this.mapId||pending.portal||this.combat.path.length||this.player.hp<=0)return;const npc=this.map.npcs[pending.index];if(!this.combat.canAttackFrom(this.hero,npc)){this.pendingNpc=null;return;}this.pendingNpc=null;this.combat.stopFarming();this.hero.direction=this.combat.direction(this.hero,npc);await this.openNpcPage(pending.index);}
 async openNpcPage(index,page='Start'){
  const npc=this.map.npcs[index];if(!npc||npc.removed||this.combat?.story||this.npcBusy)return;this.npcBusy=true;
  try{
   let view=readNpcDialogue(npc.script,this.player,this.content,page,{map:this.map,units:this.units,waitingPets:this.combat.waitingPets,defense:this.combat.defense,random:this.combat.random});
   let destination=this.map;if(view.move&&view.move.id!==this.mapId)destination=this.content.mapList.some(m=>m.id===view.move.id)?await this.content.json('maps/'+view.move.id+'.json'):null;
   if(!executeScriptView(this.combat,view,this.scriptState,this.mapFlagsByMap,destination))view={...view,effects:[],mapFlags:[],worldEffects:[],move:null,passMap:false,shop:false,sell:false,storage:null,close:false,silent:false,text:['暂时无法完成这项操作。'],choices:[{label:'关闭',action:'OVER'}]};
   this.mapSpriteExtents=mapSpriteExtents(this.map,this.packs);this.lastPreparedCell=null;
   const service=view.close?null:view.refining||view.storage||(view.shop?'shop':view.sell?'sell':this.serviceView?'dialogue':null);
   if(view.close||view.silent){this.serviceView=null;this.npcDialogue=null;}
   else if(service){this.serviceView={kind:service,index,name:npc.name,dialogue:view,page:0,quantity:1,selectedItem:null,choicePage:0,feedback:null};this.npcDialogue=null;this.tab='背包';this.page=0;await prepareService(this);}
   else{this.serviceView=null;this.npcDialogue={...view,index,name:npc.name,textPage:0,choicePage:0};}
   if(view.passMap){this.npcDialogue=null;this.serviceView=null;this.mapOpen=true;this.mapPage=0;}
   if(view.move){this.npcDialogue=null;this.serviceView=null;if(view.move.id===this.mapId){this.audio.stopEffects();this.audio.ui('传送2');this.combat.stopFarming();Object.assign(this.hero,{x:view.move.x,y:view.move.y});this.camera={x:view.move.x,y:view.move.y};}else await this.changeMap(view.move.id,{x:view.move.x,y:view.move.y},{unlock:true,quest:questTransfer(this,index,view.move.id)});}
   if(view.effects.some(e=>e.kind==='give'))this.audio.ui('道具-其它');if(view.effects.some(e=>e.kind==='change'&&/^money$/i.test(e.field)&&e.operator==='+'&&e.value>0))this.audio.ui('道具-钱');if(view.effects.some(e=>e.kind==='change'&&/^(hd|cb)$/i.test(e.field)))await this.updateAppearance();
   await this.prepareVisible();await this.prepareOwned();this.audio.prepare(this.combat);this.save();
  }finally{this.npcBusy=false;}
 }
 async npcChoice(action,source=this.npcDialogue||this.serviceView){
  if(!source||source!==(this.npcDialogue||this.serviceView)||this.npcBusy)return;
  const choices=source.choices||source.dialogue?.choices||[];if(!choices.some(c=>c.action===action))return;
  const index=source.index,parts=action.trim().split(/\s+/),command=parts[0].toUpperCase();
  if(command==='OVER'){this.npcDialogue=null;this.serviceView=null;return;}
  if(command==='TOMAP'){
   this.npcBusy=true;
   try{const id=parts[1]?.toUpperCase(),x=Number(parts[2]),y=Number(parts[3]);
    if(this.content.mapList.some(m=>m.id===id)&&Number.isInteger(x)&&Number.isInteger(y)){
     const map=id===this.mapId?this.map:await this.content.json('maps/'+id+'.json');
     if(x<0||y<0||x>=map.width||y>=map.height||source!==(this.npcDialogue||this.serviceView))return;
     this.npcDialogue=null;this.serviceView=null;await this.changeMap(id,{x,y},{unlock:true});
    }
   }finally{this.npcBusy=false;}return;
  }
  if(index!==undefined)await this.openNpcPage(index,command);
 }
 drawNpcDialog(){
  const d=this.npcDialogue,b=this.batch;this.buttons=[];b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.58);b.quad(38,356,674,930,'#211915');this.hud.panel(38,356,674,930);b.text(d.name,70,395,34,'#e8c887',446);this.button('关闭对话',548,382,134,70,()=>this.npcDialogue=null,false,27);
  const lines=[];for(const paragraph of d.text){let row='';for(const ch of paragraph){if(row&&b.textWidth(row+ch,28)>610){lines.push(row);row='';}row+=ch;}if(row)lines.push(row);}const textPages=Math.max(1,Math.ceil(lines.length/9));d.textPage=Math.min(d.textPage,textPages-1);lines.slice(d.textPage*9,d.textPage*9+9).forEach((line,i)=>b.text(line,70,496+i*40,28,'#e6d4af',610));
  if(d.textPage===textPages-1)d.choices.slice(d.choicePage*4,d.choicePage*4+4).forEach((choice,i)=>{const y=894+i*75;this.hud.button(70,y,610,64);this.hud.centered(choice.label,82,y+17,586,27,'#e2c98e');this.region(choice.label,70,y,610,64,()=>this.npcChoice(choice.action,d));});
  if(textPages>1&&d.textPage===textPages-1&&d.choices.length>4)this.button('选项 '+(d.choicePage+1)+'/'+Math.ceil(d.choices.length/4),496,842,184,40,()=>d.choicePage=(d.choicePage+1)%Math.ceil(d.choices.length/4),false,22);
  if(textPages>1){this.button('上一页',70,1214,172,48,()=>d.textPage=Math.max(0,d.textPage-1),false,25);this.hud.centered((d.textPage+1)+' / '+textPages,292,1224,166,25);this.button('下一页',508,1214,172,48,()=>d.textPage=Math.min(textPages-1,d.textPage+1),false,25);}else if(d.choices.length>4){this.button('上一页',70,1214,172,48,()=>d.choicePage=Math.max(0,d.choicePage-1),false,25);this.button('下一页',508,1214,172,48,()=>d.choicePage=Math.min(Math.ceil(d.choices.length/4)-1,d.choicePage+1),false,25);}
 }
 icon(item,x,y,size){const pack=this.packs.get('Item1'),f=pack?.frames[item.icon];if(!f)return;const s=Math.min((size-12)/f.original[0],(size-12)/f.original[1]);this.batch.frame(pack,item.icon,x+(size-f.original[0]*s)/2,y+(size-f.original[1]*s)/2,s,'#ffffff',false);}
 thumbnail(pack,index,x,y,w,h){const f=pack.frames[index];if(!f)return;const p=pack.pages[f.page],t=this.content.textureNow(p.file);if(!t)return;const [sx,sy,fw,fh]=f.rect,s=Math.min(w/fw,h/fh);this.batch.quad(x+(w-fw*s)/2,y+(h-fh*s)/2,fw*s,fh*s,'#ffffff',t,[sx/p.width,sy/p.height,fw/p.width,fh/p.height]);}
 async useConsumable(source){
  const result=await useCarriedConsumable(this,source);if(!result.ok)this.notify(result.reason);return result;
 }
 useBagItem(key){return this.useConsumable({kind:'bag',key});}
 drawBag(){
  const b=this.batch,list=this.player.inventory,perPage=15,load=carryState(this.player,this.content),totalSlots=Math.max(load.capacity,load.slots),pages=Math.ceil(totalSlots/perPage);
  this.page=Math.max(0,Math.min(this.page,pages-1));
  const entries=list.slice(this.page*perPage,this.page*perPage+perPage);
  b.text('金币 '+this.player.gold,26,1081,28,'#dfc384');
  this.button('整理',348,1072,106,48,()=>this.sortBag(),false,25);
  b.text('背包 '+load.slots+'/'+load.capacity,477,1081,25,load.freeSlots<=0?'#efbc80':'#dfc384');
  drawBelt(this,{x:26,y:1135,size:65,gap:5,manage:true});
  for(let i=0;i<perPage;i++){
   if(this.page*perPage+i>=totalSlots)continue;
   const x=26+(i%5)*85,y=1220+Math.floor(i/5)*85,e=entries[i];this.hud.slot(x,y,78,78,inventoryKey(e)===this.selectedItem);
   if(e){const item=instanceItem(this.content.items[e.itemId],e);this.icon(item,x,y,78);b.text(e.quantity,x+43,y+52,23,'#fff0cb');
    this.region(itemName(item),x,y,78,78,()=>{this.selectedItem=inventoryKey(e);this.selectedBelt=null;if(this.serviceView){this.serviceView.quantity=1;this.serviceView.feedback=null;}},{doubleClick:()=>this.bagQuickAction(e),rightClick:['storage','dimension'].includes(this.serviceView?.kind)?()=>this.bagQuickAction(e,{right:true}):undefined,shiftClick:!this.serviceView?()=>this.bagQuickAction(e,{shift:true}):undefined});
   }
  }
  const beltEntry=Number.isInteger(this.selectedBelt)&&this.player.belt[this.selectedBelt],e=beltEntry||findInventory(list,this.selectedItem)||list[0],item=e&&instanceItem(this.content.items[e.itemId],e);
  if(item){
   b.paragraph(itemName(item),477,1138,239,29,36,2);b.text('数量 '+e.quantity,477,1220,26);
   if(isBeltConsumable(item)){
    consumableDescription(this.player,this.content,item).forEach((text,i)=>b.text(text,477,1300+i*34,26));
    this.button('使用',477,1380,237,46,()=>beltEntry?this.useConsumable({kind:'belt',index:this.selectedBelt}):this.useBagItem(inventoryKey(e)));
    if(beltEntry)this.button('移回背包',477,1440,237,42,()=>{const result=returnFromBelt(this.player,this.selectedBelt);if(!result.ok)this.notify(result.reason);else{this.selectedBelt=null;this.selectedItem=inventoryKey(e);}});
    else this.button('放入腰带',477,1440,237,42,()=>{const result=putInBelt(this.player,this.content,inventoryKey(e));if(!result.ok)this.notify(result.reason);else{this.selectedItem=null;this.selectedBelt=result.index;}});
   }else if(EQUIPMENT.some(e=>e[2]===item.type)){
    this.bagItemDetails||={};drawItemProperties(this,item,{x:477,y:1254,w:239,h:160,size:25,line:30,state:this.bagItemDetails,scope:'bag',entry:e});
    this.button('穿戴',477,1430,ringRule(item)?114:237,56,()=>this.equipBagItem(e));if(ringRule(item))this.button(ringRemaining(this.player,item.name)?ringRemaining(this.player,item.name)+'秒':'使用',600,1430,114,56,()=>this.useRing(item.name),false,25);
   }
  }
  if(e&&!beltEntry&&!this.serviceView)this.button('丢弃',477,1488,237,42,()=>{this.selectedItem=inventoryKey(e);return this.openFeature('discard');},false,24);
  if(pages>1){this.button('上一页',26,1484,145,46,()=>this.page=Math.max(0,this.page-1));this.hud.centered((this.page+1)+' / '+pages,172,1492,112,23);this.button('下一页',285,1484,145,46,()=>this.page=Math.min(pages-1,this.page+1));}
 }
 drawAvatar(actor,x,y,scale,{tint='#ffffff',opacity=1}={}){
  drawAvatarLayers(this.batch,this.packs,this.appearance,actor,x,y,scale,{tint,opacity,time:this.elapsed});
 }
 drawCharacterAvatar(){
  const actor={action:'idle',direction:5,animationElapsed:0},layers=avatarLayers(this.appearance,actor),bounds=avatarBounds(this.packs,layers),box={x:104,y:1138,w:192,h:344,maxScale:4},fit=fitAvatar(bounds,box);
  this.characterPortrait={layers,bounds,box,fit};if(fit)this.drawAvatar(actor,fit.x,fit.y,fit.scale);
 }
 drawCharacter(){
  const b=this.batch,s=attributes(this.player,this.content),active=this.selectedEquipment??(this.player.equipment.weapon!==undefined?'weapon':EQUIPMENT.find(([slot])=>this.player.equipment[slot]!==undefined)?.[0]);
  b.text(this.player.name+'  '+this.player.class+'  Lv.'+this.player.level,26,1081,28,'#dfc384');this.drawCharacterAvatar();
  EQUIPMENT.forEach(([slot,label],i)=>{const x=i<5?26:302,y=1135+(i%5)*72,item=instanceItem(this.content.items[this.player.equipment[slot]],this.player.equipmentMeta?.[slot]);this.hud.slot(x,y,68,68,active===slot);if(item)this.icon(item,x,y,68);else b.text(label,x+6,y+21,27,'#8f8067');this.region(label,x,y,68,68,()=>{this.selectedEquipment=slot;},{doubleClick:ringRule(item)?()=>this.useRing(item.name):undefined,rightClick:item?async()=>{if(unequip(this.player,slot))this.audio.ui('按键2');await this.updateAppearance();await this.prepareOwned();}:undefined});});
  const rows=['生命 '+this.player.hp+'/'+s.hp,'魔法 '+this.player.mp+'/'+s.mp,'攻击 '+s.attack.join('–'),'道术 '+s.tao.join('–'),'魔法 '+s.magic.join('–'),'防御 '+s.defense.join('–'),'魔防 '+s.magicDefense.join('–'),'快攻 '+s.fastAttack,'快法 '+s.fastCast,'准确 '+s.accuracy,'物避 '+s.physicalEvade,'魔避 '+s.magicEvade,'背包 '+carryState(this.player,this.content).slots+'/'+carryState(this.player,this.content).capacity,'套装加成 '+s.setBonus,'冰封 '+s.freeze,'引燃 '+s.burn,'中毒 '+s.poison,'麻痹 '+s.paralysis,'吸血 '+s.vampire,'伤反 '+s.reflect,'幸运 '+s.luck,'时间挑战 '+(this.player.challengeRecords.timeFrames?challengeTime(this.player.challengeRecords.timeFrames):'未完成'),'通关次数 '+(this.player.clearCount||0)],statsPages=Math.ceil(rows.length/7),statsPage=Math.max(0,Math.min(this.characterStatsPage||0,statsPages-1));this.characterStatsPage=statsPage;rows.slice(statsPage*7,statsPage*7+7).forEach((text,i)=>b.text(text,396,1140+i*40,Math.min(25,25*158/Math.max(1,b.textWidth(text,25))),'#d9cbb0',158));
  this.button('属性 '+(statsPage+1)+'/'+statsPages,396,1414,158,36,()=>this.characterStatsPage=(statsPage+1)%statsPages,false,22);
  this.button('属性点 '+this.player.attributePoints,396,1458,158,66,()=>this.attributeOpen=true,false,24);
  const item=instanceItem(this.content.items[this.player.equipment[active]],this.player.equipmentMeta?.[active]);
  if(item){b.paragraph(itemName(item),576,1138,146,25,33,2);this.characterItemDetails||={};drawItemProperties(this,item,{x:576,y:1220,w:146,h:ringRule(item)?156:252,size:24,line:31,state:this.characterItemDetails,scope:'character',entry:this.player.equipmentMeta?.[active]});if(ringRule(item)){b.text('冷却 '+ringRemaining(this.player,item.name)+' 秒',576,1388,23,'#c7b58c',146);this.button('使用',576,1423,146,50,()=>this.useRing(item.name),false,24);}this.button('卸下',576,1483,146,46,async()=>{if(unequip(this.player,active))this.audio.ui('按键2');else this.notify('背包空间不足');await this.updateAppearance();await this.prepareOwned();},false,24);}else if(this.itemDetailsViews)delete this.itemDetailsViews.character;
 }

 drawBattle(){
  const b=this.batch,h=this.hud,stats=attributes(this.player,this.content);
  for(const [kind,x,value,max]of [['hp',12,this.player.hp,stats.hp],['mp',578,this.player.mp,stats.mp]]){
   h.orb(kind,x,1333,160,value/max);h.centered(kind.toUpperCase(),x+24,1390,112,24,'#f0dfbd');h.centered(value+'/'+max,x+24,1420,112,25,'#fff0ca');
  }
  drawBelt(this,{x:181,y:1312,size:61,gap:4});
  for(let i=0;i<AUTO_SKILL_LIMIT;i++){
   const x=181+i*65,y=1380,entry=this.player.autoSkills?.[i],learned=entry&&this.player.skills.find(s=>s.name===entry.name);h.outlineSlot(x,y,61,61,!!entry?.enabled);
   if(entry&&learned){h.skill(entry.name,x+5,y+5,51,entry.enabled);b.quad(x+3,y+37,55,23,'#100c08',b.white,[0,0,1,1],.95);h.centered(entry.enabled?'Lv.'+learned.level:'关闭',x+3,y+37,55,23,entry.enabled?'#fff0cb':'#a59c8c');this.region('技能:'+entry.name,x,y,61,61,()=>this.toggleSkill(entry.name),{longPress:()=>this.openFeature('skillInfo',{name:entry.name}),rightClick:()=>this.openFeature('skillInfo',{name:entry.name})});}
   else this.region('自动技能空位:'+i,x,y,61,61,()=>{this.tab='技能';this.page=0;this.selectedSkill=null;});
  }

  const xp=experienceProgress(this.player);b.quad(12,1497,726,36,'#100c08',b.white,[0,0,1,1],.92);h.bar('experience',16,1501,718,27,xp.ratio);h.centered('Lv.'+this.player.level+'  经验 '+xp.current+'/'+xp.needed+(xp.maxLevel?'  满级':'  还差 '+xp.remaining),24,1501,702,26,'#fff0cb');
  if(this.player.hp===0)this.button('回城复活',236,1214,278,62,()=>this.reviveAtTown());
 }

 gmChoice(x,y){const p=this.toLogical(x,y),r=Math.hypot(p.x-375,p.y-780);if(r<76||r>240)return null;const angle=(Math.atan2(p.y-780,p.x-375)+Math.PI*2.5)%(Math.PI*2)-Math.PI/2;return GM_SECTORS.find(([,start,end])=>angle>=start&&angle<end)?.[0]||null;}
 gmKey(down,cancel=false){if(this.screen!=='game'||this.combat?.story||this.systemMenu||this.disposed||this.loading||this.itemBusy||this.changing||this.serviceView||this.npcDialogue||this.attributeOpen||this.featureView||this.mapOpen||this.resetting||this.gmBusy)return;if(down){cancelContinuous(this);this.gmOpen=true;this.gmSelection=null;}else if(this.gmOpen){const selection=cancel?null:this.gmSelection;this.gmOpen=false;this.gmSelection=null;if(selection)this.gmCommand(selection).catch(e=>console.error(e));}}
 async gmCommand(command){
  if(this.screen!=='game'||this.combat?.story||this.gmBusy||this.disposed||this.loading||this.itemBusy||this.changing)return;this.gmBusy=true;this.gmOpen=false;this.gmSelection=null;
  try{if(command==='解锁全技能'){
   const previous=new Map(this.player.skills.map(s=>[s.name,s.level]));this.player.skills=SKILL_ORDER.filter(name=>this.content.skills.records.some(r=>r.name===name)).map(name=>({name,level:Math.max(1,previous.get(name)||0)}));normalizeActiveClassSkill(this.player,this.content);await this.prepareOwned();this.audio.prepare(this.combat);this.save();this.notify('已解锁全技能');
  }else if(command==='获得100技能点'){
   this.player.skillPoints=(this.player.skillPoints||0)+100;this.save();this.notify('获得100技能点');
  }else if(command==='清档'){
   this.resetting=true;if(this.preparing)await this.preparing;const identity={name:this.player.name,class:this.player.class,gender:this.player.gender};this.player=this.player.creationProfile?.startsWith('native-classes-')?createNewCharacter(this.content,identity):Object.assign(createCharacter(this.content,{}),identity);normalizePermanent(this.player,this.content);normalizeRings(this.player);this.roster.bindDimension(this.player,this.content);this.heroClass=this.player.class;this.combat=new Combat(this.player,this.content);this.combat.audio=this.audio;this.audio.stopEffects();this.featureView=null;this.selectedSkill=null;this.selectedEquipment=null;this.skillPage=0;this.mapFlagsByMap={};this.scriptState={};this.serviceView=null;this.npcDialogue=null;this.pendingNpc=null;this.attributeOpen=false;this.mapOpen=false;this.tab='战斗';this.message=null;this.portalDelay=0;this.lastPreparedCell=null;await this.updateAppearance();await this.changeMap('A00');this.resetting=false;this.nextSave=this.elapsed+5;this.save();this.notify('已清档');
  }}finally{this.resetting=false;this.gmBusy=false;}
 }
 drawGM(){
  const b=this.batch,h=this.hud;b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.5);
  for(const [label,start,end,x,y]of GM_SECTORS){const selected=this.gmSelection===label;b.ring(375,780,72,240,start+.02,end-.02,selected?'#c3a364':'#8b6940');b.ring(375,780,77,234,start+.02,end-.02,selected?'#59412b':'#2a211b');h.centered(label,x-95,y+24,190,27,selected?'#ffdfa0':'#d4bf96');if(label==='解锁全技能')h.skill('基本剑术',x-29,y-48,58);else if(label==='清档')h.image('system-0',x-25,y-44,50,50);else h.centered('+100',x-60,y-38,120,36,'#e6c382');}
  h.centered('GM',331,763,88,38,'#e6c382');
 }
 async learnSkill(record){
  if(this.growthBusy)return;this.growthBusy=true;
  try{const result=improveSkill(this.player,record);if(!result.allowed){this.notify(result.reason);return;}this.audio.ui('升级');this.save();await this.prepareOwned();this.audio.prepare(this.combat);}finally{this.growthBusy=false;}
 }
 drawSkills(){
  this.batch.text('自动技能 '+(this.player.autoSkills?.length||0)+' / 6',503,1081,25,'#dfc384');
  const b=this.batch,records=visibleSkillRecords(this.player,this.content),learned=name=>this.player.skills.find(s=>s.name===name&&s.level>0);this.page=Math.max(0,Math.min(this.page,Math.max(0,Math.ceil(records.length/4)-1)));const selected=records.find(r=>r.name===this.selectedSkill)||records[this.page*4]||records[0];this.selectedSkill=selected?.name||null;b.text('技能点 '+this.player.skillPoints,26,1081,28,'#dfc384');
  records.slice(this.page*4,this.page*4+4).forEach((r,i)=>{const x=26,y=1137+i*82,s=learned(r.name);this.hud.slot(x,y,72,72,r.name===selected.name);this.hud.skill(r.name,x+8,y+8,56,!!s);b.text(r.name,111,y+8,28,s?'#dfc795':'#928976',245);b.text(s?'Lv.'+s.level:'未解锁',111,y+44,24,s?'#b7a277':'#776f60');this.region(r.name,x,y,320,72,()=>this.selectedSkill=r.name);});
  if(selected){const s=learned(selected.name),check=skillEligibility(this.player,selected);b.text(selected.name,397,1138,30,'#e6c27b',319);b.text(s?'Lv.'+s.level:'未解锁',397,1190,27,s?'#d0bd98':'#928976');if(PASSIVE_SKILLS.has(selected.name))b.text('被动生效',579,1200,24,'#bba475');else if(s){const configured=this.player.autoSkills?.some(e=>e.name===s.name);this.button(configured?'移出':'激活',579,1182,138,50,async()=>{if(configured)this.removeSkill(s.name);else if((await this.activateSkill(s.name)).ok)this.tab='战斗';},false,24);}
   b.paragraph(skillDescription(selected,s?.level||1).replace(/[，,]?MP消耗[：:]\d+/g,''),397,1240,314,25,32,4);if(selected.mpCost)b.text('消耗 MP '+selected.mpCost,397,1380,24);b.paragraph(check.missing?check.reason:!check.cost?check.reason:'',397,1420,314,23,27,2);
   if(check.cost)this.button((s?'升级':'学习')+' · '+check.cost+'点',397,1476,319,50,()=>this.learnSkill(selected),check.allowed,25);
  }
  this.button('上一页',26,1476,145,50,()=>{this.page=Math.max(0,this.page-1);this.selectedSkill=records[this.page*4].name;},false,25);b.text((this.page+1)+' / '+Math.ceil(records.length/4),191,1489,24,'#a7997c');this.button('下一页',275,1476,105,50,()=>{this.page=Math.min(Math.ceil(records.length/4)-1,this.page+1);this.selectedSkill=records[this.page*4].name;},false,25);
 }
 async followFirstQuest(){return followQuestTarget(this,this.firstQuestTarget());}
 firstQuestTarget(){return firstQuestTarget(this.player,this.map,this.units,this.content,this.combat.groundItems);}
 drawTasks(){const key=JSON.stringify([this.player.events,this.player.unlockedMaps,this.player.clearCount,this.mapId,this.combat.scriptRevision,this.player.inventory.map(e=>[e.itemId,e.quantity])]);if(this.questKey!==key&&!this.questPreparing){this.questKey=key;this.questPreparing=prepareQuestJournal(this).catch(e=>console.error(e)).finally(()=>this.questPreparing=null);}drawQuestJournal(this);}
 drawSystem(){const methods={背包:'drawBag',角色:'drawCharacter',战斗:'drawBattle',技能:'drawSkills',任务:'drawTasks'};this[methods[this.tab]||'drawBattle']();['背包','角色','战斗','技能','任务'].forEach((tab,i)=>{const x=12+i*148;this.hud.nav(tab,x,1535,134,80,this.tab===tab);this.region(tab,x,1535,134,80,async()=>{if(tab!=='背包')this.serviceView=null;this.tab=tab;this.page=0;if(tab==='任务'){this.questTextPage=0;await prepareQuestJournal(this);}await this.prepareOwned();});const points=tab==='角色'?this.player.attributePoints:tab==='技能'?this.player.skillPoints:0;if(points>0){this.batch.quad(x+91,1538,39,25,'#742817');this.hud.centered(points>99?'99+':String(points),x+91,1538,39,22,'#ffe6af');}});if(this.message&&this.elapsed<this.messageUntil){this.hud.button(125,940,500,68);this.batch.text(this.message,145,960,29,'#ead3a5',460);}}
 render(){
  this.content.beginFrame();
 if(this.screen==='game'&&(!this.sessionLoaded||this.resetting||this.changing||this.reviving))return;
 this.buttons=[];const b=this.batch,c=b.camera,r=this.renderer;if(this.combat?.story&&this.screen==='game'){r.setRenderTarget(null);c.right=750;c.bottom=0;c.updateProjectionMatrix();b.begin();drawEnding(this);b.finish();r.setViewport(0,0,this.width,this.height);r.clear();r.setViewport(this.left,this.height-this.top-1624*this.scale,750*this.scale,1624*this.scale);r.render(b.scene,c);return;}if(this.screen!=='game'){r.setRenderTarget(null);c.right=750;c.bottom=0;c.updateProjectionMatrix();b.begin();this.entry.draw();if(this.systemMenu)this.drawSystemMenu();if(this.featureView)drawFeatureDialog(this);b.finish();r.setViewport(0,0,this.width,this.height);r.clear();r.setViewport(this.left,this.height-this.top-1624*this.scale,750*this.scale,1624*this.scale);r.render(b.scene,c);return;}b.pixelGrid={scale:1/this.worldScale,left:0,top:0};b.begin('world');this.drawWorld();b.finish();c.right=WORLD_VIEW.width*this.worldScale;c.bottom=1624-WORLD_VIEW.height*this.worldScale;c.updateProjectionMatrix();r.setRenderTarget(this.worldTarget);r.clear();r.render(b.scene,c);
 r.setRenderTarget(null);c.right=750;c.bottom=0;c.updateProjectionMatrix();b.begin();b.quad(0,0,750,1624,'#ffffff',this.worldTarget.texture,worldView(this.camera,this.worldScale).uv);this.drawWorldLabels();this.drawChrome();this.drawSystem();if(this.serviceView)drawService(this);if(this.npcDialogue)this.drawNpcDialog();if(this.mapOpen)this.drawMapDialog();if(this.attributeOpen)drawAttributeDialog(this);if(this.gmOpen)this.drawGM();if(this.systemMenu)this.drawSystemMenu();if(this.featureView)drawFeatureDialog(this);b.finish();r.setViewport(0,0,this.width,this.height);r.clear();r.setViewport(this.left,this.height-this.top-1624*this.scale,750*this.scale,1624*this.scale);r.render(b.scene,c);
 }
 drawSystemMenu(){
  const b=this.batch,h=this.hud,s=this.audio.settings,playing=this.screen==='game',top=playing?228:350,height=playing?1166:780;
  this.buttons=[];b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.6);b.quad(110,top,530,height,'#2b201a');h.panel(110,top,530,height);h.centered(playing?'系统':'声音',145,top+62,460,38);
  this.button(playing?'继续游戏':'关闭',173,playing?366:494,404,64,()=>this.systemMenu=false);
  if(playing){this.button('保存继续',173,444,404,64,()=>{this.save();this.systemMenu=false;});this.button('保存退出',173,522,404,64,()=>this.returnHome());this.button('操作帮助',173,600,404,64,()=>this.openFeature('help'));this.button('游戏模式',173,1127,404,56,()=>this.openFeature('difficulty'));}
  for(const [label,key,y]of [['音乐','music',playing?697:635],['音效','effects',playing?925:865]]){
   b.text(label,157,y+16,33,'#e2cf9f');this.button(s[key+'Enabled']?'开启':'关闭',422,y,172,64,()=>this.audio.set(key+'Enabled',!s[key+'Enabled']),s[key+'Enabled'],28);const value=s[key+'Volume'];h.centered(Math.round(value*100)+'%',288,y+97,174,30);this.button('-',157,y+89,95,64,()=>this.audio.set(key+'Volume',Math.round((value-.1)*100)/100),false,33);this.button('+',499,y+89,95,64,()=>this.audio.set(key+'Volume',Math.round((value+.1)*100)/100),false,33);b.quad(157,y+174,437,10,'#100d09');b.quad(157,y+174,437*value,10,'#ad8440');
  }
  if(playing)this.button('放弃退出',173,1190,404,64,()=>{this.systemMenu=false;this.featureView={kind:'exit'};});
 }
 tick(time){
  if(this.disposed)return;const dt=this.previous?Math.min((time-this.previous)/1000,.1):0;this.previous=time;
  if(!this.hidden){this.audio.battle(this.screen==='game'&&!this.combat?.story&&!this.itemBusy&&!this.changing&&!this.reviving&&!this.resetting&&!this.systemMenu&&!this.serviceView&&!this.npcDialogue&&!this.attributeOpen&&!this.featureView&&!this.mapOpen&&!this.gmOpen&&!this.gmBusy);this.elapsed+=dt;if(this.screen==='game'&&!this.combat?.story&&!this.itemBusy&&!this.changing&&!this.reviving&&!this.resetting){
   if(!this.combat.story&&!this.systemMenu&&!this.serviceView&&!this.npcDialogue&&!this.attributeOpen&&!this.featureView&&!this.mapOpen&&!this.gmOpen&&!this.gmBusy){updateContinuousMovement(this);this.combat.particleView={x:this.camera.x-375/(48*this.worldScale),y:this.camera.y-555/(32*this.worldScale)};for(let remaining=dt;remaining>1e-8;){const step=Math.min(.02,remaining);this.combat.update(step);remaining-=step;}if(this.combat.challengeNotice){this.combat.challengeNotice=false;this.save();this.openFeature('challenge').catch(e=>console.error(e));}if(this.combat.defenseNotice){this.notify(this.combat.defenseNotice);this.combat.defenseNotice=null;}updateInsightAutomation(this);this.audio.idle(this.combat);this.audio.ambient(this.combat.zones.some(z=>[19,40].includes(z.type)&&this.audio.attenuation(z)>0));this.hero=this.combat.position;updateQuestTravel(this);this.checkNpcInteraction().catch(e=>console.error(e));}
   if(this.lastWorldScriptRevision!==this.combat.scriptRevision){this.lastWorldScriptRevision=this.combat.scriptRevision;this.mapSpriteExtents=mapSpriteExtents(this.map,this.packs);}
   this.hero=this.combat.position;const follow=1-Math.exp(60*Math.log(.85)*dt);this.camera.x=T.MathUtils.lerp(this.camera.x,this.hero.x,follow);this.camera.y=T.MathUtils.lerp(this.camera.y,this.hero.y,follow);const monsterPacks=[...new Set(this.units.filter(u=>u.alive&&Math.abs(u.x-this.camera.x)<17&&Math.abs(u.y-this.camera.y)<26).map(u=>u.definition.appearance))].sort((a,b)=>a-b).join(',');const key=this.combat.artRevision+'|'+this.combat.scriptRevision+'|'+Math.floor(this.camera.x)+','+Math.floor(this.camera.y)+','+this.combat.lootVersion+'|'+monsterPacks;if(key!==this.lastPreparedCell&&!this.preparing){this.lastPreparedCell=key;this.prepareVisible().catch(e=>console.error(e));}this.checkPortal();if(this.elapsed>this.nextSave&&!this.systemMenu&&!this.featureView){this.save();this.nextSave=this.elapsed+5;}
  }this.render();}this.frame=this.platform.frame(this.tick);
 }
 checkPortal(){if(this.screen!=='game'||this.combat.story||this.combat.scriptLocked||this.player.hp<=0||this.itemBusy||this.reviving||this.systemMenu||this.serviceView||this.npcDialogue||this.pendingNpc&&!this.pendingNpc.portal||this.combat.farmType!==null&&this.combat.farmType!==undefined||this.attributeOpen||this.featureView||this.mapOpen||this.gmOpen||this.gmBusy||this.resetting||this.combat.autoLoot||this.combat.lootingId)return;if(this.elapsed<(this.portalDelay||0)||this.combat.targetId)return;const p=this.map.portals.find(p=>Math.hypot(p.x-this.hero.x,p.y-this.hero.y)<.25);if(!p||this.pendingNpc?.portal&&(p.x!==this.pendingNpc.portal.x||p.y!==this.pendingNpc.portal.y))return;const id=p.target==='当前地图'?this.mapId:p.target.split(' ')[0];if(!this.content.mapList.some(m=>m.id===id))return;this.portalDelay=this.elapsed+3;const resume=this.pendingNpc?.portal?this.pendingNpc:null;this.changeMap(id,{x:p.targetX,y:p.targetY},{unlock:true,quest:questPortal(this,p)}).then(changed=>{if(changed&&resume&&resume.mapId===this.mapId&&!this.disposed)return this.selectNpc(resume.index);}).catch(e=>console.error(e));}
 save(){if(this.screen!=='game'||!this.sessionLoaded||!this.mapId||this.itemBusy||this.resetting||this.entering||this.reviving)return;rememberMapPosition(this.player,this.map,this.hero);const state={version:2,map:this.mapId,position:{x:this.hero.x,y:this.hero.y},player:this.player,groundItems:this.combat.groundByMap,pets:this.combat.savePets(),defense:this.combat.saveDefense(),challenge:this.combat.saveChallenge(),story:this.combat.story||null,mapFlagsByMap:this.mapFlagsByMap,scriptState:this.scriptState};this.roster.commitDimension(this.player);this.roster.set(this.characterId,state);this.platform.save(this.roster.serialize());}
 snapshot(){return {audio:this.audio.snapshot(),design:{width:750,height:1624},screen:this.screen,characters:this.roster.characters.map(r=>({id:r.id,name:r.state.player.name,class:r.state.player.class,level:r.state.player.level})),battleAt:'top',systemsAt:'bottom',map:this.mapId||null,mapName:this.map?.name||null,items:this.content.items.length,monsters:this.content.monsters.length,spawns:this.units?.length||0,npcs:this.map?.npcs.length||0,tab:this.tab,combatReady:true,combatFormulaVerified:COMBAT_RULES.damageFormulaVerified,hud:this.hud.snapshot(),player:this.player?JSON.parse(JSON.stringify(this.player)):null,appearance:this.appearance,portrait:this.characterPortrait,attributeDialog:!!this.attributeOpen,mapDialog:!!this.mapOpen,npcDialogue:this.npcDialogue?.name||null,service:this.serviceView?.kind||null,farmType:this.combat?.farmType??null,groundItems:this.combat?.groundItems.length||0,target:this.combat?.targetId,hitCount:this.combat?.hitCount||0,texturePages:this.content.textures.size,drawCalls:this.renderer.info.render.calls,disposed:this.disposed};}
 dispose(){if(this.disposed)return;cancelContinuous(this);this.disposed=true;this.platform.cancel(this.frame);this.save();this.audio?.dispose();this.batch?.dispose();this.content.dispose();this.platform.dispose();this.worldTarget?.dispose();this.renderer?.dispose();}
}
