import {instanceItem} from './native-stats.js';
// Native item columns: see reports/native-item-fields.json. Keep field values
// literal: displaying a property does not apply unimplemented combat effects.
export const EQUIPMENT_PROPERTIES=[
 [16,'快攻'],[17,'快法'],[18,'物避'],[19,'魔避'],[20,'准确'],
 [21,'冰封'],[22,'引燃'],[23,'中毒'],[24,'麻痹'],[25,'吸血'],[26,'伤反'],[27,'幸运'],
 [31,'等级需求'],[32,'攻击需求'],[33,'道术需求'],[34,'魔法需求'],
];
export const isEquipment=item=>!!item&&item.type>=7&&item.type<=14;
export function itemPropertyRows(item,{weight=false,entry={}}={}){
 if(!item)return [];item=instanceItem(item,entry);
 const rows=[];if(item.rawFields[35]||entry.forgeLevel)rows.push('锻造 +'+(item.rawFields[35]||entry.forgeLevel));if(entry.mergeLevel)rows.push('合成 '+entry.mergeLevel+'级');
 for(const [key,label]of [['attack','攻击'],['tao','道术'],['magic','魔法'],['defense','防御'],['magicDefense','魔防']]){
  const value=item[key];if(Array.isArray(value)&&value.some(n=>n!==0))rows.push(label+' '+value.join('–'));
 }
 if(isEquipment(item))for(const [index,label]of EQUIPMENT_PROPERTIES){const value=item.rawFields?.[index];if(Number.isFinite(value)&&value!==0)rows.push(label+' '+value);}
 const attached=({18:'雷电术',19:'火墙',20:'冰咆哮'})[item.rawFields?.[30]];if(attached)rows.push('附加技能 '+attached);
 if(item.hp)rows.push('恢复 HP '+item.hp);if(item.mp)rows.push('恢复 MP '+item.mp);
 if(weight)rows.push('重量 '+item.weight);
 return rows;
}

// Fixed-height details keep long equipment records above the action buttons.
// Each surface owns its pagination so changing selection always starts at page 1.
export function drawItemProperties(app,item,{x,y,w,h,size=25,line=32,state,scope,weight=false,entry={}}){
 const rows=itemPropertyRows(item,{weight,entry}),capacity=Math.max(1,Math.floor(h/line)),paged=rows.length>capacity,perPage=paged?Math.max(1,Math.floor((h-48)/line)):capacity;
 const pages=Math.max(1,Math.ceil(rows.length/perPage)),selectionKey=entry.instanceId??item?.id;if(state.selectionKey!==selectionKey){state.itemId=item?.id;state.selectionKey=selectionKey;state.page=0;}state.page=Math.min(state.page||0,pages-1);
 rows.slice(state.page*perPage,state.page*perPage+perPage).forEach((text,index)=>{const fit=Math.min(size,size*w/Math.max(1,app.batch.textWidth(text,size)));app.batch.text(text,x,y+index*line,fit,'#dccdad',w);});
 if(pages>1)app.button('属性 '+(state.page+1)+' / '+pages,x,y+h-42,w,42,()=>state.page=(state.page+1)%pages,false,22);
 app.itemDetailsViews||={};app.itemDetailsViews[scope]={itemId:item?.id,rows,page:state.page,pages,x,y,w,h};
}
