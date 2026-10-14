import {carriedItems} from './inventory.js';

// Mstm.dat ET0=1..28, matched to the shipped NPC/death/drop scripts. Stage 6
// reaches the cemetery test first; its native death event advances ET0 to 7.
export const MAIN_QUEST_GOALS={
 1:['npc','A13','方丈'],2:['npc','A13','凌云子'],3:['npc','A00','海曦村长'],
 4:['monster','A02','甲虫王'],5:['npc','A00','海曦村长'],6:['monster','A04','墓地尸王'],
 7:['npc','B00','英雄雕像'],8:['npc','B00','村长'],9:['npc','C00','大夫'],
 11:['npc','C00','临海镇长'],12:['npc','D00','华月太守'],13:['monster','D11','狼王'],
 14:['npc','D00','华月太守'],15:['npc','E00','镇长'],16:['npc','F00','村长'],
 17:['monster','F12','鼠王'],18:['npc','F00','村长'],19:['npc','G00','族长'],
 21:['npc','H00','村长'],22:['monster','H32','邪恶虫王'],23:['npc','H00','村长'],
 24:['monster','H24','虎威将军'],25:['npc','H00','村长'],26:['monster','H85','金魔霸王'],
 27:['npc','H85','镇墓玉石'],28:['npc','A13','方丈'],
};
export const QUEST_COLLECTIONS={
 10:{items:['老蟾酥','野猪牙'],sources:[['monster','C12','蛙统领'],['monster','B12','野猪王']],turnIn:['npc','C00','大夫']},
 20:{items:['红色灵珠','绿色灵珠','蓝色灵珠'],sources:[['monster','G10','未知怪']],turnIn:['npc','G00','族长']},
};
const goal=([kind,mapId,name])=>({kind,mapId,name});
export function mainQuestObjective(player,content){
 const event=player.events?.[0],collection=QUEST_COLLECTIONS[event];
 if(collection){
  const held=new Set(carriedItems(player).filter(e=>e.quantity>0).map(e=>e.itemId));
  const missing=collection.items.filter(name=>!held.has(content?.itemNames?.get(name)?.id));
  if(!missing.length)return {...goal(collection.turnIn),event,turnIn:true};
  const index=event===10?collection.items.indexOf(missing[0]):0;
  return {...goal(collection.sources[index]),event,missing,label:event===10?'寻找'+missing[0]:'寻找三色灵珠'};
 }
 return MAIN_QUEST_GOALS[event]?{...goal(MAIN_QUEST_GOALS[event]),event}:null;
}
