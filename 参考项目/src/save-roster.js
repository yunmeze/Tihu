import {mergeItem,validInventory} from './inventory.js';
const clone=value=>JSON.parse(JSON.stringify(value));
export function characterSave(value){
 if(value?.version!==2||!value.player?.base||!value.player.equipment||!Array.isArray(value.player.inventory))return null;
 // Retired mode saves already contain the original map and position.
 const {rosterVersion,hellUnlocked,activeCharacterId,characters,dimensionBoxVersion,sharedDimensionBox,playStyle,sideAdventure,...state}=value;
 const saved=clone(state);delete saved.player.sideSupplies;return saved;
}
// Keep the active v2 save at the root for compatibility with existing clients.
// Each roster entry is a plain v2 save, so nested rosters cannot accumulate.
export class SaveRoster{
 constructor(value={},content=null){
  if(!value||typeof value!=='object')value={};this.characters=[];for(const record of Array.isArray(value.characters)?value.characters:[]){const state=characterSave(record?.state);if(typeof record?.id==='string'&&state&&!this.characters.some(r=>r.id===record.id))this.characters.push({id:record.id,state});}
  this.activeId=this.characters.some(r=>r.id===value.activeCharacterId)?value.activeCharacterId:this.characters[0]?.id||null;
  const active=characterSave(value);if(active){if(this.activeId)this.set(this.activeId,active);else{this.activeId='character-1';this.characters.push({id:this.activeId,state:active});}}
  this.hellUnlocked=value.hellUnlocked===true||this.characters.some(r=>r.state.player.gameMode===2);this.dimensionBox={items:[]};const sources=value.dimensionBoxVersion===1?[value.sharedDimensionBox?.items||[]]:this.characters.map(r=>r.state.player.dimensionBox?.items||[]);
  for(const list of sources)for(const entry of content?validInventory(list,content):Array.isArray(list)?list:[]){if(!entry||!Number.isInteger(entry.itemId)||!Number.isSafeInteger(entry.quantity)||entry.quantity<=0)continue;if(!mergeItem(this.dimensionBox.items,entry.itemId,entry.quantity,clone(entry)))throw Error('Shared dimension quantity overflow');}
 }
 get(id=this.activeId){return this.characters.find(r=>r.id===id);}
 nextId(){let i=1;while(this.get('character-'+i))i++;return 'character-'+i;}
 add(state){const save=characterSave(state);if(!save)throw Error('Invalid character save');const id=this.nextId();this.characters.push({id,state:save});return id;}
 set(id,state){const entry=this.get(id),save=characterSave(state);if(!save)return false;if(entry)entry.state=save;else this.characters.push({id,state:save});this.activeId=id;if(save.player.gameMode===2)this.hellUnlocked=true;return true;}
 remove(id){const index=this.characters.findIndex(r=>r.id===id);if(index<0)return false;this.characters.splice(index,1);if(this.activeId===id)this.activeId=this.characters[0]?.id||null;return true;}
 bindDimension(player,content){if(content)this.dimensionBox.items=validInventory(this.dimensionBox.items,content);player.dimensionBox=this.dimensionBox;}
 commitDimension(player){if(player.dimensionBox!==this.dimensionBox)this.dimensionBox.items=clone(player.dimensionBox?.items||[]);player.dimensionBox=this.dimensionBox;}
 serialize(){const characters=clone(this.characters);for(const r of characters)r.state.player.dimensionBox=clone(this.dimensionBox);const state=characters.find(r=>r.id===this.activeId)?.state;return {...(state||{}),rosterVersion:1,hellUnlocked:this.hellUnlocked,activeCharacterId:this.activeId,characters,dimensionBoxVersion:1,sharedDimensionBox:clone(this.dimensionBox)};}
 nameExists(name){return this.characters.some(r=>r.state.player.name.toLocaleLowerCase()===name.toLocaleLowerCase());}
 defaultName(){let name='英雄',i=2;while(this.nameExists(name))name='英雄'+i++;return name;}
}
