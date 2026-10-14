import {instanceItem} from './native-stats.js';
import {animationFrame} from './animation.js';

// Native 5c1180: HD > 1 overrides the gender head; CB selects a wing sheet.
export const HEAD_APPEARANCE_MODEL='native-hair-v1';
const valid=(value,min,max)=>Number.isInteger(value)&&value>=min&&value<=max;
function headStyle(player){
 const gender=player.gender===1?1:0,style=player.headStyle;
 if(!valid(style,0,6))return gender;
 // Earlier web profiles forced HD=2 without owning a hat. Native E00's hat
 // merchant records the purchase in HD2, so preserve legitimate old purchases.
 if(style===2&&player.headAppearanceModel!==HEAD_APPEARANCE_MODEL&&!player.appearanceUnlocks?.hd?.[2])return gender;
 return style;
}
export function normalizeAppearance(player){
 player.gender=player.gender===1?1:0;
 player.headStyle=headStyle(player);player.headAppearanceModel=HEAD_APPEARANCE_MODEL;
 player.wings=Number.isInteger(player.wings)&&player.wings>=0&&player.wings<=9?player.wings:0;
 return player;
}
export function characterAppearance(player,content){
 const gender=player.gender===1?1:0,armor=instanceItem(content.items[player.equipment?.armor],player.equipmentMeta?.armor),weapon=instanceItem(content.items[player.equipment?.weapon],player.equipmentMeta?.weapon),body=armor?.type===9?armor.appearance?.[gender]:null,blade=weapon?.type===14?weapon.appearance?.[0]:null,style=headStyle(player);
 const tint=player.equipmentMeta?.weapon?.tint,weaponTint=Array.isArray(tint)&&tint.length===3&&tint.every(v=>valid(v,0,255))?'#'+tint.map(v=>v.toString(16).padStart(2,'0')).join(''):'#ffffff';
 const mergeLevel=player.equipmentMeta?.weapon?.mergeLevel;
 return {body:valid(body,1,65)?body:gender,head:valid(style,2,6)?style:gender,weapon:valid(blade,1,102)?blade:null,wings:valid(player.wings,1,9)?player.wings:null,...(weaponTint!=='#ffffff'?{weaponTint}:{}),...(weapon?.type===14&&valid(mergeLevel,1,4)?{weaponMergeLevel:mergeLevel}:{})};
}
export function appearancePacks(appearance){return ['Hero/'+appearance.body,'Hero/Head/'+appearance.head,...(appearance.weapon?['Weapon/'+appearance.weapon]:[]),...(appearance.wings?['Hero/Cb/'+appearance.wings]:[])];}
// All sheets share the same frame and original foot anchor. Native weapon is
// behind the body in directions 0/5/6/7; wings are behind in 3/4/5.
export function avatarLayers(appearance,actor){
 const direction=((actor.direction||0)%8+8)%8,index=animationFrame({...actor,direction}),layers=[],add=(part,pack)=>layers.push({part,pack,index}),weaponBehind=direction===0||direction>=5,wingsBehind=direction>=3&&direction<=5;
 if(appearance.weapon&&weaponBehind)add('weapon','Weapon/'+appearance.weapon);
 if(appearance.wings&&wingsBehind)add('wings','Hero/Cb/'+appearance.wings);
 add('body','Hero/'+appearance.body);add('head','Hero/Head/'+appearance.head);
 if(appearance.weapon&&!weaponBehind)add('weapon','Weapon/'+appearance.weapon);
 if(appearance.wings&&!wingsBehind)add('wings','Hero/Cb/'+appearance.wings);
 return layers;
}
// Native 5c1a50 / 5c1bfa / 5c25cd: merged blades draw displaced copies
// before the ordinary tinted weapon. Directions 0 and 4 omit the x copies.
export function weaponGlow(appearance,direction,time=0){
 const grade=appearance.weaponMergeLevel;if(!appearance.weapon||!valid(grade,1,4))return null;
 const tick=Math.max(0,Math.floor(time*50+1e-8));let alpha;
 // The zero-initialized native pulse first descends to -5, then rises to
 // 260. Subsequent 86-tick cycles turn below 50 and above 255.
 if(tick===0)alpha=0;else if(tick<=54)alpha=(tick-2)*5;
 else{const phase=(tick-54)%86;alpha=phase<=43?260-phase*5:45+(phase-43)*5;}
 const d=((direction||0)%8+8)%8;
 return {color:'#'+(grade*50+55).toString(16).padStart(2,'0')+'3200',opacity:Math.min(255,Math.max(0,alpha))/255,offsets:d===0||d===4?[[0,2],[0,-2]]:[[2,0],[-2,0],[0,2],[0,-2]]};
}
export function drawAvatarLayers(batch,packs,appearance,actor,x,y,scale,{tint='#ffffff',opacity=1,time=0}={}){
 const glow=weaponGlow(appearance,actor.direction,time);
 for(const layer of avatarLayers(appearance,actor)){
  const pack=packs.get(layer.pack);if(!pack)continue;
  if(layer.part==='weapon'&&glow)for(const [dx,dy]of glow.offsets)batch.frame(pack,layer.index,x+dx*scale,y+dy*scale,scale,glow.color,true,glow.opacity*opacity);
  batch.frame(pack,layer.index,x,y,scale,['body','head'].includes(layer.part)?tint:layer.part==='weapon'?(appearance.weaponTint||'#ffffff'):'#ffffff',true,opacity);
 }
}
export function avatarBounds(packs,layers){
 let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;
 for(const layer of layers){const f=packs.get(layer.pack)?.frames[layer.index];if(!f||f.rect[2]<=0||f.rect[3]<=0)continue;const x=f.offset[0]+f.crop[0],y=f.offset[1]+f.crop[1];left=Math.min(left,x);top=Math.min(top,y);right=Math.max(right,x+f.rect[2]);bottom=Math.max(bottom,y+f.rect[3]);}
 return Number.isFinite(left)?{left,top,right,bottom,width:right-left,height:bottom-top}:null;
}
export function fitAvatar(bounds,box){
 if(!bounds||bounds.width<=0||bounds.height<=0)return null;
 const scale=Math.min(box.w/bounds.width,box.h/bounds.height,box.maxScale??Infinity);
 return {x:box.x+(box.w-bounds.width*scale)/2-bounds.left*scale,y:box.y+(box.h-bounds.height*scale)/2-bounds.top*scale,scale};
}
