import {instanceItem} from './native-stats.js';
import {findInventory,inventoryKey,takeItem,mergeItem} from './inventory.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';
import {bagState} from './bag-capacity.js';

// Shipped EXE: 583d80 / 5e5230 (forge), 563040 / 566e30 / 566fe0 (merge).
export const FORGE_COSTS=[
 [200,1,0,0,0],[500,2,0,0,0],[800,1,1,0,0],
 [1000,2,1,0,0],[1200,3,1,0,0],[1500,4,1,0,0],
 [1800,4,1,1,0],[2000,4,2,1,0],[2500,4,1,1,1],
];
export const ORES=['铁矿石','铜矿石','银矿石','金矿石'];
const fail=reason=>({ok:false,reason}),clone=x=>JSON.parse(JSON.stringify(x));
const word=x=>((x+32768)&65535)-32768;
const named=(p,c,name)=>p.inventory.filter(e=>instanceItem(c.items[e.itemId],e)?.name===name);
const count=(p,c,name)=>named(p,c,name).reduce((n,e)=>n+e.quantity,0);
function takeNamed(p,c,name,quantity){for(const e of named(p,c,name)){const n=Math.min(quantity,e.quantity);takeItem(p.inventory,inventoryKey(e),n);quantity-=n;if(!quantity)break;}return quantity===0;}
const field=(item,index)=>item.rawFields[index]||0;
export function forgeQuote(player,content,selector){
 const entry=findInventory(player.inventory,selector),item=entry&&instanceItem(content.items[entry.itemId],entry);
 if(!item||item.type!==14)return fail('请先选择一件武器');
 if((entry.mergeLevel||0)>0||entry.fused)return fail('不能锻造合成过的装备');
 const level=field(item,35)||entry.forgeLevel||0;
 if(level<0||level>=9)return fail('已达最高锻造等级');
 const [gold,...ores]=FORGE_COSTS[level];
 return {ok:true,level,gold,ores,successPercent:100-level*10,item,entry};
}
export function forgeEquipment(player,content,selector,random=Math.random){
 const q=forgeQuote(player,content,selector);if(!q.ok)return q;
 if(player.gold<q.gold)return fail('携带金币不足');
 if(q.ores.some((n,i)=>count(player,content,ORES[i])<n))return fail('矿石不足');
 const next=clone(player),taken=clone(takeItem(next.inventory,selector));
 next.gold-=q.gold;q.ores.forEach((n,i)=>{if(n)takeNamed(next,content,ORES[i],n);});
 const destroyed=sampleMonsterRandom(random)*100<q.level*10;
 if(!destroyed){
  const raw=[...q.item.rawFields],index=raw[7]>=raw[11]&&raw[7]>=raw[9]?7:raw[11]>=raw[9]?11:9;
  raw[index]=word(raw[index]+(nativeRound(raw[index]/20)||1));raw[35]=q.level+1;
  let priceBonus=taken.priceBonus??raw[37]??0;
  // Sixth and subsequent successful forges roll five independent capped attributes.
  if(raw[35]>5)for(const [i,denominator]of [[20,15],[21,35],[22,25],[23,25],[25,40]]){const hit=sampleMonsterRandom(random)*denominator<1;if(hit&&raw[i]<2){raw[i]++;priceBonus+=2;}}
  taken.fieldOverrides={...taken.fieldOverrides,[index]:raw[index],35:raw[35]};
  for(let i=16;i<=27;i++)if(raw[i]!==q.item.rawFields[i])taken.fieldOverrides[i]=raw[i];
  taken.forgeLevel=raw[35];taken.priceBonus=priceBonus;taken.fieldOverrides[37]=priceBonus;delete taken.instanceId;
  if(!mergeItem(next.inventory,taken.itemId,1,taken))return fail('物品数量过多');
 }
 if(bagState(next).slots>Math.max(bagState(player).capacity,bagState(player).slots))return fail('背包空间不足');
 Object.assign(player,next);return {ok:true,success:!destroyed,destroyed,level:destroyed?q.level:q.level+1,gold:q.gold};
}

export function mergeQuote(player,content,selections=[]){
 const entries=selections.map(k=>k===null||k===undefined?null:findInventory(player.inventory,k)),items=entries.map(e=>e&&instanceItem(content.items[e.itemId],e));
 const [a,b]=items;if(!a||!b||a.type!==14||b.type!==14||a.name!==b.name||(entries[0].mergeLevel||0)!==(entries[1].mergeLevel||0))return fail('需要两件名称、合成等级相同的武器');
 const used=new Map();for(const e of entries.filter(Boolean)){const key=inventoryKey(e);used.set(key,(used.get(key)||0)+1);if(used.get(key)>e.quantity)return fail('物品数量不足');}
 const level=entries[0].mergeLevel||0;if(level<0||level>=4)return fail('神器级的装备无法再次合成');
 for(const i of [2,3])if(items[i]&&!ORES.includes(items[i].name))return fail('矿石栏只能放矿石');
 for(const i of [4,5])if(items[i]&&(items[i].type<7||items[i].type>14))return fail('属性栏只能放装备');
 const oreBonus=[2,3].reduce((n,i)=>n+(items[i]?[4,6,9,12][ORES.indexOf(items[i].name)]:0),0);
 return {ok:true,level,gold:[2000,5000,8000,10000][level],successPercent:Math.min(100,[70,50,30,10][level]+oreBonus),entries,items};
}
export function mergeEquipment(player,content,selections,random=Math.random){
 const q=mergeQuote(player,content,selections);if(!q.ok)return q;if(player.gold<q.gold)return fail('携带金币不足');
 const next=clone(player);next.gold-=q.gold;
 const inputs=q.entries.map(e=>e&&clone(takeItem(next.inventory,inventoryKey(e)))),selected=nativeRound(sampleMonsterRandom(random)*100)<50?0:1;
 const output=inputs[selected],raw=[...q.items[selected].rawFields],success=nativeRound(sampleMonsterRandom(random)*100)<q.successPercent;
 if(success){const newLevel=q.level+1;for(let i=6;i<=26;i++){raw[i]=nativeRound(word(field(q.items[0],i)+field(q.items[1],i))/2);if(i>=16&&raw[i]===0&&(field(q.items[0],i)===1||field(q.items[1],i)===1))raw[i]=1;}
  for(let i=6;i<=14;i+=2){if(raw[i]>0)raw[i]=word(raw[i]+1);if(raw[i+1]>0)raw[i+1]=word(raw[i+1]+newLevel);}
 }
 const oreChance=[2,3].reduce((n,i)=>n+(q.items[i]?[3,5,8,12][ORES.indexOf(q.items[i].name)]:0),0);
 const rolled={};for(const i of [23,25,16,17,20,24]){const amount=[4,5].reduce((n,j)=>n+(q.items[j]?field(q.items[j],i):0),0)*12;rolled[i]=nativeRound(sampleMonsterRandom(random)*100)<amount+(amount>0?oreChance:0);}
 const lower=i=>{if(raw[i]>0)raw[i]--;};
 if(rolled[25]&&raw[25]<2){raw[25]++;lower(23);}if(rolled[23]&&raw[23]<2){raw[23]++;lower(25);}
 if(rolled[16]&&raw[16]<1){raw[16]++;[21,20,24,25,17].forEach(lower);}
 if(rolled[17]&&raw[17]<1){raw[17]++;[21,20,16].forEach(lower);}
 if(rolled[20]&&raw[20]<2){raw[20]++;if(raw[20]>=2&&raw[16]>=2)raw[16]=1;}
 if(rolled[24]&&raw[24]<1){raw[24]++;if(raw[24]>=2&&raw[20]>=2)raw[20]=1;[21,22,23,25].forEach(lower);if(raw[7]>5)raw[7]-=5;}
 for(const [a,b]of [[23,25],[21,22],[16,17]])if(raw[a]>0&&raw[b]>0)lower(nativeRound(sampleMonsterRandom(random)*100)<50?a:b);
 // Preserve the shipped final physical/magic-evade branch, including its asymmetry.
 if(raw[18]>0)raw[nativeRound(sampleMonsterRandom(random)*100)<50?18:19]--;
 if(raw[24]>0&&raw[18]>0)raw[nativeRound(sampleMonsterRandom(random)*100)<50?18:19]--;
 output.fieldOverrides={...output.fieldOverrides};for(let i=6;i<=26;i++)if(raw[i]!==q.items[selected].rawFields[i])output.fieldOverrides[i]=raw[i];
 output.mergeLevel=q.level+Number(success);output.fused=output.mergeLevel>0;delete output.instanceId;if(!mergeItem(next.inventory,output.itemId,1,output))return fail('物品数量过多');
 if(bagState(next).slots>Math.max(bagState(player).capacity,bagState(player).slots))return fail('背包空间不足');
 Object.assign(player,next);return {ok:true,success,level:output.mergeLevel,gold:q.gold};
}
