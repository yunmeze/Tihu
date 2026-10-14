// Native map-object dispatch: 5c59e4; animation clock: 5b55df..5b5644.
// Type 7 is an NPC index, rendered through the NPC list, not another effect.
export const MAP_GROUPS={1:'Debris',2:'Plant',3:'Wall',4:'Building',5:'Dynamic'};
export const MAP_EFFECT_RULES=Object.freeze({sourceFps:50,frameTicks:8,dynamicFrames:5,pillarPack:'Data4',pillarFirst:55,pillarFrames:5,pillarTop:-52,npcFrameTicks:17});
const frameCache=new WeakMap();
function objectFrame(type,index,packs){
 const pack=packs.get(type===8?MAP_EFFECT_RULES.pillarPack:MAP_GROUPS[type]&&'Map/Res/'+MAP_GROUPS[type]);
 const frame=pack?.frames[index];if(!frame)return null;
 let cached=frameCache.get(pack);if(!cached)frameCache.set(pack,cached=new Map());let result=cached.get(index);const top=type===8?MAP_EFFECT_RULES.pillarTop:32-frame.original[1];
 if(!result||result.frame!==frame||result.top!==top){result={pack,index,frame,top};cached.set(index,result);}return result;
}
export function mapObjectFrames(cell,packs){
 const type=cell[2],base=cell[3];if(base<=0||!MAP_GROUPS[type]&&type!==8)return [];
 const count=type===5?MAP_EFFECT_RULES.dynamicFrames:type===8?MAP_EFFECT_RULES.pillarFrames:1,first=type===8?MAP_EFFECT_RULES.pillarFirst:base;
 return Array.from({length:count},(_,phase)=>objectFrame(type,first+phase,packs)).filter(Boolean);
}
export function mapObjectFrame(cell,packs,seconds){
 const type=cell[2],base=cell[3];if(base<=0||!MAP_GROUPS[type]&&type!==8)return null;
 const tick=Math.floor((Math.max(0,seconds)+1e-8)*MAP_EFFECT_RULES.sourceFps/MAP_EFFECT_RULES.frameTicks),phase=tick%5;
 const index=type===5?base+phase:type===8?MAP_EFFECT_RULES.pillarFirst+(Math.floor(tick/5)%2?4-phase:phase):base;
 return objectFrame(type,index,packs);
}
