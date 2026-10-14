import {canContinueDefense,continueDefense,defenseEnemies} from './defense.js';

export function drawDefenseHud(a){
 const c=a.combat,d=c.defense;if(!d)return;
 const flags=c.units.filter(u=>u.defenseFlag&&u.alive).length;
 a.button('防守',404,20,126,80,()=>a.openFeature('defense'),false,27);
 a.hud.button(18,200,510,50);a.hud.centered('第 '+d.wave+'/21 波  战旗 '+flags+'/8  敌军 '+defenseEnemies(c).length,28,213,490,24,'#e7d4a1');
 if(canContinueDefense(c))a.button(d.wave?'继续防守':'开始进攻',18,260,220,56,()=>continueDefense(c),false,27);
 if(d.status!=='active')a.button(d.status==='failed'?'防守失败':'防守完成',18,260,220,56,()=>a.openFeature('defense'),false,27);
}
export function drawDefenseDialog(a,v){
 const c=a.combat,d=c.defense,h=a.hud,b=a.batch;if(!d)return;
 const mercs=c.units.filter(u=>u.alive&&u.mercenary),flags=c.units.filter(u=>u.defenseFlag),sub=v.sub==='mercs'?'mercs':'flags';v.sub=sub;
 for(const [i,[key,label]]of [['flags','战旗'],['mercs','佣兵']].entries())a.button(label,68+i*310,344,300,58,()=>{v.sub=key;v.page=0;},sub===key,29);
 h.centered(d.status==='failed'?'战旗损失过半，防守失败！':d.status==='complete'?'魔物潮汐已结束，清理战场后返回吧':'第 '+d.wave+'/21 波 · 敌军 '+defenseEnemies(c).length,68,426,614,27);
 if(sub==='flags'){
  h.centered('生命升级 '+d.hpUp+'/5  物防 '+d.dfUp+'/6  魔防 '+d.dmUp+'/6',68,480,614,25);
  flags.forEach((u,i)=>{const y=540+i*77;h.button(68,y,614,67);b.text('战旗 '+(i+1),85,y+13,26,u.alive?'#dfc384':'#907d63');h.bar('hp',238,y+17,420,30,u.alive?u.hp/u.definition.hp:0);h.centered(u.alive?u.hp+'/'+u.definition.hp:'已损毁',238,y+20,420,25);});
 }else{
  const pages=Math.max(1,Math.ceil(mercs.length/4));v.page=Math.min(v.page||0,pages-1);
  mercs.slice(v.page*4,v.page*4+4).forEach((u,i)=>{const y=494+i*168,pack=a.packs.get('Mon/'+u.definition.appearance),f=pack?.frames[17];h.button(68,y,614,154);if(f){const z=Math.min(110/f.original[0],110/f.original[1]);b.frame(pack,17,82,y+12,z,'#ffffff',false);}b.text(u.name+'  Lv.'+u.petLevel,223,y+12,29,'#dfc384',420);h.bar('hp',223,y+56,436,25,u.hp/u.definition.hp);h.centered(u.hp+'/'+u.definition.hp,223,y+57,436,23);b.text('攻击 '+u.definition.attack+'  防御 '+u.definition.defense+'  魔防 '+u.definition.magicDefense,223,y+101,23,'#d9cbb0',437);});
  if(!mercs.length)h.centered('暂无佣兵',68,600,614,30);
  a.button('上一页',68,1178,180,52,()=>v.page=Math.max(0,v.page-1),false,24);h.centered((v.page+1)+' / '+pages,258,1190,225,24);a.button('下一页',502,1178,180,52,()=>v.page=Math.min(pages-1,v.page+1),false,24);
 }
 if(d.status==='active'){
  if(canContinueDefense(c))a.button(d.wave?'继续防守':'开始进攻',68,1250,295,58,()=>{continueDefense(c);a.closeFeature();},false,26);
  const index=a.map.npcs.findIndex(n=>n.name==='守卫升级');a.button('守卫升级',382,1250,300,58,async()=>{a.closeFeature();await a.selectNpc(index);},false,26);
 }
 a.button('返回齐阳城',182,1323,386,52,async()=>{if(a.player.hp<=0)return;await a.changeMap('J00',{x:126,y:74},{unlock:true});a.save();},false,26);
}
