import {drawDefenseHud,drawDefenseDialog} from './defense-ui.js';
import {drawChallengeHud,drawChallengeDialog} from './challenge-ui.js';
import {followingPet} from './allies.js';
import {attributes} from './character.js';
import {statusTint,actorOpacity} from './statuses.js';
import {skillDescription} from './growth.js';
import {DIFFICULTIES} from './difficulty.js';
import {collectionProgress,collectionRewards,claimCollection,playerStatusEntries,placePendingLoot} from './permanent-state.js';

export function featureSpriteRequests(app){
 const v=app.featureView;if(!v)return [];
 if(v.kind==='pets'||v.kind==='defense')return app.units.filter(u=>u.alive&&(v.kind==='defense'?u.mercenary:followingPet(u))).map(u=>['Mon/'+u.definition.appearance,17]);
 if(v.kind!=='collection'||v.sub==='rewards')return [];
 const pool=app.content.permanent.collectionPool,ids=v.monsterId===undefined?pool.slice((v.page||0)*5,(v.page||0)*5+5).map(m=>m.id):[v.monsterId];
 return ids.map(id=>['Mon/'+app.content.monsters[id].appearance,17]);
}
export async function prepareFeature(app){
 const view=app.featureView;if(!view)return;const requests=featureSpriteRequests(app),key=JSON.stringify(requests),files=new Set();
 await Promise.all(requests.map(async([id,index])=>{await app.loadPack(id);const prepared=await app.content.frame(id,index);if(prepared)files.add(prepared.page.file);}));await app.content.sync();
 // An older page load may finish after the player selected another page.
 // Only the current window can choose which preview images to retain.
 if(app.featureView!==view||JSON.stringify(featureSpriteRequests(app))!==key)return;
 app.visibleArtFiles=new Set([...(app.worldArtFiles||app.visibleArtFiles||[]),...files]);app.content.trimTextures(app.visibleArtFiles);
}
export function drawPermanentHud(app){
 const b=app.batch,h=app.hud,p=app.player;
 for(const [key,label,x,action]of [['system-0','菜单',18,()=>app.systemMenu=true],['insight-0','开悟',110,()=>app.openFeature('insight')],['collection-0','图鉴',202,()=>app.openFeature('collection')]]){h.image(key,x,20,80,80);app.region(label,x,20,80,80,action);}
 const pets=app.units.filter(u=>followingPet(u)&&u.alive);if(pets.length)app.button('宠物',294,20,104,80,()=>app.openFeature('pets'),false,27);
 drawDefenseHud(app);
 drawChallengeHud(app);
 const statuses=playerStatusEntries(p);for(const [i,s]of statuses.entries()){
  const x=18+i*61,y=120;h.button(x,y,55,57);if(s.pack)icon(app,app.packs.get(s.pack),s.frame,x+6,y+6,43);else if(s.frame)b.frame(app.packs.get('Data7'),s.frame,x+9,y+4,2.2,'#ffffff',false);else h.skill(s.skill,x+9,y+4,36);if(s.seconds!==null)h.centered(String(s.seconds),x+3,y+36,49,20,'#fff0ca');app.region('状态:'+s.name,x,y,55,57,()=>app.openFeature('status'));
 }
}
const titles={difficulty:'游戏模式',skillInfo:'技能信息',challenge:'极限挑战',defense:'守卫边境',insight:'开悟',collection:'图鉴',pets:'宠物',status:'状态',help:'操作帮助',discard:'丢弃物品',exit:'放弃退出'};
const icon=(a,pack,index,x,y,size,definition)=>{const f=pack?.frames[index];if(!f)return;const scale=Math.min(size/f.original[0],size/f.original[1]),actor={definition};a.batch.frame(pack,index,x+(size-f.original[0]*scale)/2,y+(size-f.original[1]*scale)/2,scale,definition?statusTint(actor):'#ffffff',false,definition?actorOpacity(actor):1);};
export function drawFeatureDialog(a){
 const v=a.featureView;if(!v)return;const b=a.batch,h=a.hud;a.buttons=[];
 b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.62);b.quad(38,228,674,1166,'#211915');h.panel(38,228,674,1166);b.text(titles[v.kind]||'功能',68,278,36,'#e6c78d');a.button('关闭窗口',547,266,135,55,()=>a.closeFeature(),false,25);
 if(v.kind==='insight')drawInsights(a,v);
 if(v.kind==='collection')drawCollection(a,v);
 if(v.kind==='pets')drawPets(a,v);
 if(v.kind==='defense')drawDefenseDialog(a,v);
 if(v.kind==='challenge')drawChallengeDialog(a);
 if(v.kind==='status')drawStatuses(a);
 if(v.kind==='help')drawHelp(a,v);
 if(v.kind==='difficulty'){
  const p=a.player,max=Math.min(2,Math.max(p.gameMode||0,p.modeUnlock||0));h.centered('通关 '+(p.clearCount||0)+' 次',70,400,610,30);
  DIFFICULTIES.forEach((name,i)=>{const y=530+i*185;a.button(name,120,y,510,85,()=>a.setDifficulty(i),i===p.gameMode,32);h.centered(i>max?'通关上一模式后解锁':i===p.gameMode?'当前模式':'已解锁',120,y+105,510,27,i>max?'#8f806c':'#d4bf92');});
 }
 if(v.kind==='skillInfo'){
  const r=a.content.skills.records.find(r=>r.name===v.name),s=a.player.skills.find(s=>s.name===v.name),entry=a.player.autoSkills.find(e=>e.name===v.name);if(!r||!s)return;
  h.slot(80,375,106,106);h.skill(r.name,92,387,82);b.text(r.name,216,386,34,'#f0d59e');b.text('Lv.'+s.level+'  消耗 MP '+r.mpCost,216,438,28);
  b.paragraph(skillDescription(r,s.level),80,532,590,30,45,12);
  a.button(entry?.enabled?'关闭自动释放':'开启自动释放',140,1140,470,72,()=>a.toggleSkill(r.name),!!entry?.enabled,29);
 }
 if(v.kind==='discard'){b.paragraph('将所选物品丢到脚边，走过去可重新拾取。',78,400,594,30,44,3);a.button('确定丢弃',94,610,250,70,()=>a.discardSelected());a.button('取消',402,610,250,70,()=>a.featureView=null);}
 if(v.kind==='exit'){b.paragraph('放弃尚未保存的进度，返回首页？',78,400,594,30,44,3);a.button('放弃退出',94,610,250,70,()=>a.returnHome({save:false}));a.button('取消',402,610,250,70,()=>{a.featureView=null;a.systemMenu=true;});}
}
function drawInsights(a,v){
 const b=a.batch,h=a.hud,p=a.player,records=a.content.permanent.insights,page=v.page||0,rows=records.slice(page*4,page*4+4);
 h.centered('已获得 '+p.insights.filter(n=>n!==-1).length+'/13',70,349,610,28);
 rows.forEach((r,i)=>{const y=409+i*193,state=p.insights[r.id],label=state===-1?'未获得':state?'开启':'关闭';h.button(64,y,620,177);b.text(r.name,82,y+18,29,'#dfc384');b.paragraph(r.description,82,y+60,415,26,34,3);
  a.button(label,528,y+47,135,64,()=>{if(state!==-1){p.insights[r.id]=state?0:1;a.save();}},state===1,26);
  if(state===-1)b.text(p.insightFreeCount<2?'可免费开悟':r.price+'金币',527,y+121,22,'#c7b58c',138);
 });
 a.button('上一页',64,1203,151,56,()=>v.page=Math.max(0,page-1),false,25);h.centered((page+1)+' / 4',252,1218,246,26);a.button('下一页',533,1203,151,56,()=>v.page=Math.min(3,page+1),false,25);
 const index=a.map.npcs.findIndex(n=>n.name==='开悟老人'&&!n.removed);if(index>=0)a.button('前往开悟老人',181,1304,388,56,async()=>{a.featureView=null;a.systemMenu=false;await a.selectNpc(index);},false,26);else h.centered('在海曦村向开悟老人求教',68,1314,614,26);
 if(page===3){const y=1050;for(const [label,key,x]of [['HP','autoHpPercent',80],['MP','autoMpPercent',388]]){b.text(label+' '+p[key]+'%',x,y,27,'#e5d09b');a.button('−',x,y+44,77,58,()=>p[key]=Math.max(10,p[key]-10),false,30);a.button('+',x+173,y+44,77,58,()=>p[key]=Math.min(90,p[key]+10),false,30);}}
}
function drawCollection(a,v){
 const b=a.batch,h=a.hud,p=a.player,progress=collectionProgress(p,a.content),sub=v.sub||'monsters';
 for(const [i,[key,label]]of [['monsters','怪物'],['drops','战利品'],['rewards','奖励']].entries())a.button(label,64+i*208,344,202,56,async()=>{v.sub=key;v.page=0;delete v.monsterId;await prepareFeature(a);},sub===key,27);
 if(sub==='rewards'){
  for(const [j,[key,label]]of [['monsters','怪物'],['drops','战利品']].entries()){
   const x=66+j*316,pr=progress[key];h.centered(label+' '+pr.current+'/'+pr.total,x,425,304,27);h.bar('experience',x,465,298,24,pr.ratio);
   for(const [i,r]of collectionRewards(a.content,key).entries()){const y=518+i*126,claim=pr.stage>=r.stage,ready=pr.current*10>=r.stage*pr.total;h.button(x,y,298,115);h.centered(r.stage*10+'%  '+rewardLabel(r),x+12,y+16,274,27,'#dfc384');a.button(claim?'已领取':ready?'领取':'未达成',x+65,y+55,168,48,async()=>{if(!claim&&ready&&claimCollection(p,a.content,key)){placePendingLoot(a.combat);await a.prepareOwned();await a.prepareVisible();a.save();}},ready&&!claim,27);}
  }return;
 }
 if(v.monsterId!==undefined){drawCollectionDetails(a,v);return;}
 const pr=progress[sub];h.bar('experience',68,432,612,26,pr.ratio);h.centered(pr.current+' / '+pr.total+'  '+(pr.ratio*100).toFixed(1)+'%',68,468,612,26);
 const pool=a.content.permanent.collectionPool,pages=Math.ceil(pool.length/5);v.page=Math.min(v.page||0,pages-1);
 pool.slice(v.page*5,v.page*5+5).forEach((r,i)=>{const d=a.content.monsters[r.id],known=p.collection.monsters[r.id],y=520+i*145;h.button(64,y,620,133);icon(a,a.packs.get('Mon/'+d.appearance),17,80,y+13,105,d);b.text(known?d.name:'未发现',206,y+24,29,known?'#e6cf98':'#8f806c',455);const found=r.drops.filter((_,index)=>p.collection.drops[r.id+':'+index]).length;b.text('战利品 '+found+'/'+r.drops.length,206,y+73,26,'#c6b58f');a.region('图鉴怪物:'+r.id,64,y,620,133,async()=>{v.monsterId=r.id;v.dropPage=0;await prepareFeature(a);});});
 a.button('上一页',64,1304,151,56,async()=>{v.page=Math.max(0,v.page-1);await prepareFeature(a);},false,25);h.centered((v.page+1)+' / '+pages,252,1318,246,26);a.button('下一页',533,1304,151,56,async()=>{v.page=Math.min(pages-1,v.page+1);await prepareFeature(a);},false,25);
}
function rewardLabel(r){return r.gold?'金币+'+r.gold:r.items?r.stage===6?'栗子组合':'矿石组合':r.defense?'防御+1':r.magicDefense?'魔防+1':r.offense?'攻道魔+1':r.attributes?'属性点+1':'极品率提升';}
function drawCollectionDetails(a,v){
 const b=a.batch,h=a.hud,p=a.player,r=a.content.permanent.collectionPool.find(m=>m.id===v.monsterId),d=a.content.monsters[v.monsterId],known=p.collection.monsters[d.id];
 icon(a,a.packs.get('Mon/'+d.appearance),17,80,437,150,d);b.text(known?d.name:'未发现',260,447,32,'#e5c98e');b.text('生命 '+d.hp+'  攻击 '+d.attack,260,501,27);b.text('防御 '+d.defense+'  魔防 '+d.magicDefense,260,545,27);
 const pages=Math.max(1,Math.ceil(r.drops.length/9));v.dropPage=Math.min(v.dropPage||0,pages-1);
 r.drops.slice(v.dropPage*9,v.dropPage*9+9).forEach((drop,i)=>{const x=68+(i%3)*206,y=638+Math.floor(i/3)*175,index=v.dropPage*9+i,found=p.collection.drops[d.id+':'+index],item=a.content.itemNames.get(drop.item);h.slot(x,y,74,74);if(item)a.icon(item,x,y,74);else if(drop.item==='金币')icon(a,a.packs.get('Item1'),5,x+4,y+4,64);h.centered(found?drop.item:'未收集',x,y+85,190,25,found?'#dfc384':'#8f8067');if(found)h.centered(drop.quantity+' / '+drop.denominator,x,y+119,190,22,'#bba475');});
 a.button('返回列表',64,1216,183,56,async()=>{delete v.monsterId;await prepareFeature(a);},false,25);a.button('上一页',270,1216,183,56,()=>v.dropPage=Math.max(0,v.dropPage-1),false,25);a.button('下一页',476,1216,208,56,()=>v.dropPage=Math.min(pages-1,v.dropPage+1),false,25);h.centered((v.dropPage+1)+' / '+pages,80,1320,584,26);
}
function drawPets(a,v){
 const b=a.batch,h=a.hud,pets=a.units.filter(u=>followingPet(u)&&u.alive);if(!pets.length){h.centered('暂无宠物',68,525,614,32);return;}
 pets.forEach((u,i)=>a.button(u.definition.name,68+i*206,346,197,56,()=>v.petId=u.id,u.id===(v.petId||pets[0].id),25));const pet=pets.find(u=>u.id===v.petId)||pets[0],d=pet.definition;
 icon(a,a.packs.get('Mon/'+d.appearance),17,258,448,220,d);h.centered(d.name,80,700,594,34);h.bar('hp',108,758,534,30,pet.hp/d.hp);h.centered(pet.hp+' / '+d.hp,108,792,534,27);
 const level=pet.petLevel||1,threshold=(level+1)*25,lines=['成长等级 '+level+' / 10',level>=10?'已达最高等级':'击败怪物 '+(pet.petKills||0)+' / '+threshold,'攻击 '+d.attack+'  防御 '+d.defense+'  魔防 '+d.magicDefense,'物避 '+d.physicalEvade+'  魔避 '+d.magicEvade,'移动速度 '+Number(d.speed.toFixed(2))];lines.forEach((t,i)=>h.centered(t,76,862+i*66,598,28));
}
function drawStatuses(a){const h=a.hud,b=a.batch,rows=playerStatusEntries(a.player);if(!rows.length){h.centered('无异常状态',68,505,614,32);return;}rows.forEach((s,i)=>{const y=377+i*132;h.slot(72,y,76,76);if(s.pack)icon(a,a.packs.get(s.pack),s.frame,80,y+8,60);else if(s.frame)b.frame(a.packs.get('Data7'),s.frame,86,y+14,3,'#ffffff',false);else h.skill(s.skill,82,y+10,56);b.text(s.name,180,y+14,30,'#dfc384');b.text(s.persistent?'持续生效':'剩余 '+s.seconds+' 秒',180,y+60,27);});}
function drawHelp(a,v){
 const b=a.batch,h=a.hud,rows=[['移动','点击地面按路径长短自动走跑，临近终点转为走路。鼠标和触屏操作相同。'],['战斗','右侧选择怪物种类，持续搜索与攻击；主动移动或再次点选取消挂机。'],['交互','左侧选择人物或箱子，自动走近后操作。'],['拾取','击败怪物后自动走近拾取；也可点地面物品。'],['腰带','背包选择消耗品放入六格腰带，点击使用；腰带不占背包格子。'],['自动技能','技能页激活最多六个主动技能，战斗栏点击开关；被动技能学会后自动生效。'],['宠物','宠物入口或 M 键查看存活宠物属性。'],['特殊戒指','双击持有的戒指，或点使用按钮。Y 使用隐身戒指；回城冷却60秒，隐身冷却120秒。'],['背包操作','双击物品使用、穿戴或出售；右键存取仓库物品、卸下装备；Shift 点击丢弃。']];
 const pages=Math.ceil(rows.length/5);v.page=Math.min(v.page||0,pages-1);rows.slice(v.page*5,v.page*5+5).forEach(([name,text],i)=>{const y=372+i*161;b.text(name,78,y,29,'#dfc384');b.paragraph(text,78,y+40,594,26,35,3);});
 a.button('上一页',68,1214,180,56,()=>v.page=Math.max(0,v.page-1),false,25);h.centered((v.page+1)+' / '+pages,258,1228,225,25);a.button('下一页',502,1214,180,56,()=>v.page=Math.min(pages-1,v.page+1),false,25);
}
