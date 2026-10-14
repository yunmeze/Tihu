import * as T from 'three';
import {itemName} from './item-names.js';
const disposeTexture=texture=>{texture.dispose();texture.image?.close?.();};
export class Content {
 constructor(platform){this.platform=platform;this.base=platform.assetBase;this.packs=new Map();this.textures=new Map();this.lastUsed=new Map();this.epoch=0;this.textureBudget=192*1024*1024;this.disposed=false;}
 json(file){return this.platform.json(this.base+file);}
 async init(){[this.items,this.monsters,this.mapList,this.skills,this.tasks,this.font,this.minimaps,this.sounds,this.audioRules,this.permanent,this.defense,this.story,this.arrivals,this.questNavigation]=await Promise.all(['data/items.json','data/monsters.json','data/maps.json','data/skills.json','data/tasks.json','fonts/index.json','data/minimaps.json','data/sounds.json','data/audio.json','data/permanent.json','data/defense.json','data/story.json','data/map-arrivals.json','data/quest-navigation.json'].map(f=>this.json(f)));this.atlas=await this.json('ui/portrait-atlas.json');this.itemNames=new Map(this.items.filter(i=>i.name!=='0').map(i=>[i.name,i]));for(const item of this.items)if(item.type===5&&!this.itemNames.has(itemName(item)))this.itemNames.set(itemName(item),item);this.monsterNames=new Map(this.monsters.filter(i=>i.name!=='0').map(i=>[i.name,i]));await Promise.all(this.font.pages.map(p=>this.texture(p.file)));return this;}
 async texture(file){file=this.atlas?.regions[file]?this.atlas.file:file;if(!this.textures.has(file)){const pending=(async()=>{const image=await this.platform.image(this.base+file);const texture=new T.Texture(image);texture.flipY=false;const nativeSprite=file.startsWith('sprites/');texture.magFilter=nativeSprite?T.NearestFilter:T.LinearFilter;texture.minFilter=nativeSprite?T.NearestFilter:T.LinearFilter;texture.generateMipmaps=false;texture.colorSpace=T.SRGBColorSpace;texture.needsUpdate=true;texture.userData.file=file;if(this.disposed){disposeTexture(texture);throw Error('Content disposed');}return texture;})().catch(error=>{if(this.textures.get(file)===pending)this.textures.delete(file);throw error;});this.textures.set(file,pending);}return this.textures.get(file);}
 async pack(id){if(!this.packs.has(id))this.packs.set(id,this.json('sprites/'+id+'/index.json'));return this.packs.get(id);}
 async frame(id,index){const pack=await this.pack(id),frame=pack.frames[index];if(!frame)return null;const page=pack.pages[frame.page];await this.texture(page.file);return {frame,page};}
 beginFrame(){this.epoch++;}
 textureNow(file){file=this.atlas?.regions[file]?this.atlas.file:file;const t=this.ready?.get(file);if(t)this.lastUsed.set(file,this.epoch);return t;}
 uv(file,x,y,w,h,width,height){const r=this.atlas?.regions[file];return r?[(r.x+x)/this.atlas.width,(r.y+y)/this.atlas.height,w/this.atlas.width,h/this.atlas.height]:[x/width,y/height,w/width,h/height];}
 rectUV(source,page){
  // Imported sprite and glyph rectangles are immutable. Reuse their atlas
  // coordinates across animation/render frames instead of allocating arrays
  // for every tile and every outlined-text pass. Weak keys retain no old pack.
  if(this.uvAtlas!==this.atlas){this.uvAtlas=this.atlas;this.rectUVCache=new WeakMap();}
  this.rectUVCache||=new WeakMap();let cached=this.rectUVCache.get(source);
  if(!cached||cached.page!==page||cached.rect!==source.rect){cached={page,rect:source.rect,value:this.uv(page.file,...source.rect,page.width,page.height)};this.rectUVCache.set(source,cached);}
  return cached.value;
 }
 releaseTexture(file){const pending=this.textures.get(file);this.textures.delete(file);this.ready?.delete(file);this.lastUsed.delete(file);pending?.then(disposeTexture).catch(()=>{});}
 trimTextures(protectedFiles=new Set()){
  const pages=[...(this.ready||[])].map(([file,t])=>({file,bytes:(t.image?.width||0)*(t.image?.height||0)*4,used:this.lastUsed.get(file)||0}));let bytes=pages.reduce((n,p)=>n+p.bytes,0);
  // UI sheets remain available when switching tabs. Evict only old world art;
  // protect both the next visible view and textures sampled by recent frames.
  for(const p of pages.sort((a,b)=>a.used-b.used)){if(bytes<=this.textureBudget)break;if(protectedFiles.has(p.file)||p.used>=this.epoch-2||!/^(sprites\/(Map\/|Mon\/|Hero\/|Weapon\/|Mgc\/)|minimaps\/)/.test(p.file))continue;this.releaseTexture(p.file);bytes-=p.bytes;}
  this.cachedTextureBytes=bytes;return bytes;
 }
 async sync(){this.ready||=new Map();await Promise.all([...this.textures].filter(([k])=>!this.ready.has(k)).map(async([k,v])=>{const t=await v;if(this.textures.get(k)===v&&!this.disposed)this.ready.set(k,t);}));}
 dispose(){this.disposed=true;for(const v of this.textures.values())v.then(disposeTexture).catch(()=>{});this.textures.clear();this.ready?.clear();this.lastUsed.clear();}
}
