import {attributes} from './character.js';
import {followingPet} from './allies.js';
import {insightOn,playerStatusEntries} from './permanent-state.js';
import {labelTop,floatingTextLayout} from './combat-text.js';
import {instanceItem} from './native-stats.js';
import {itemName} from './item-names.js';
import {groundItemIcon} from './loot.js';
import {mainQuestObjective} from './main-quest.js';
import {nearbyColumn} from './nearby-layout.js';
import {groupGroundLabels,layoutWorldLabels} from './world-label-layout.js';

const PAD=5;
const inView=p=>p.x>-170&&p.x<750&&p.y>-200&&p.y<1500;
function hudObstacles(a){
 const rects=[{x:12,y:14,w:276,h:92},{x:534,y:14,w:204,h:182}];
 if(a.units.some(u=>u.alive&&followingPet(u)))rects.push({x:288,y:14,w:116,h:92});
 if(a.combat.defense||a.combat.challenge){rects.push({x:398,y:14,w:138,h:92},{x:12,y:194,w:522,h:a.combat.defense?128:76});}
 const statuses=playerStatusEntries(a.player);if(statuses.length)rects.push({x:12,y:114,w:statuses.length*61,h:69});
 a.frameNearbyEntries=a.nearbyEntries();
 if(!a.serviceView)for(const kind of ['npc','monster']){
  const list=a.frameNearbyEntries.filter(e=>e.kind===kind),selected=list.find(e=>kind==='npc'?e.index===a.pendingNpc?.index:e.monsterId===a.combat.farmType),col=nearbyColumn(list,kind,a.tab,a.nearbyPages?.[kind]||0,selected);
  rects.push(...col.rows.map(({x,y,w,h})=>({x,y,w,h})));
  if(col.pages>1)rects.push({x:col.x,y:col.pagerY,w:168,h:40});
 }
 return rects;
}

export function drawWorldText(a){
 const b=a.batch,z=a.worldScale,c=a.combat;
 if(a.worldTextMap!==a.map){a.worldTextMap=a.map;a.worldTextState=new Map();a.worldEventIds=new WeakMap();a.nextWorldEventId=0;}
 const candidates=[],rects=hudObstacles(a),viewport={x:10,y:12,w:730,h:(a.tab==='战斗'?1304:1032)-12};
 const add=(props)=>{const width=props.lines?Math.max(...props.lines.map(line=>b.textWidth(line.text,line.size))):b.textWidth(props.text,props.size),w=Math.min(props.maxWidth||380,width)+PAD*2;
  candidates.push({...props,w,h:props.h||props.size+PAD*2});};
 for(const [index,n]of a.map.npcs.entries()){
  if(n.removed)continue;const p=a.screenPoint(n.x,n.y);if(!inView(p))continue;
  const first=1+n.appearance*12,top=p.y+labelTop(a.packs.get('Npc'),first,first+11)*z;
  add({id:'npc:'+index,kind:'actor',text:n.name,size:27,color:'#f4d895',x:p.x+24*z,y:top-35-PAD,priority:index===a.pendingNpc?.index?108:95});
 }
 for(const u of a.units){
  if(!u.alive)continue;const p=a.screenPoint(u.x,u.y);if(!inView(p))continue;
  const top=p.y+labelTop(a.packs.get('Mon/'+u.definition.appearance))*z,selected=u.id===c.targetId,bar=selected||insightOn(a.player,3);
  const name=insightOn(a.player,5)&&!u.summoned?u.name+'（攻击 '+u.definition.attack+'）':u.name;
  add({id:'unit:'+u.id,kind:'actor',text:name,size:26,color:selected?'#ffe09b':u.summoned?'#b9efd0':'#e0ddba',x:p.x+24*z,y:top-(bar?44:35)-PAD,h:bar?48:36,priority:selected?140:u.summoned?50:30,important:selected,bar:bar?{kind:'monster',ratio:Math.max(0,u.hp/u.definition.hp)}:null});
  if(bar)candidates.at(-1).w=Math.max(candidates.at(-1).w,84);
 }
 const heroTop=Math.min(labelTop(a.packs.get('Hero/'+a.appearance.body)),labelTop(a.packs.get('Hero/Head/'+a.appearance.head))),hero=a.screenPoint(a.hero.x,a.hero.y);
 if(a.player.hp>0&&(insightOn(a.player,0)||insightOn(a.player,1))){
  const name=insightOn(a.player,1)?a.player.name:'',bar=insightOn(a.player,0);
  add({id:'hero',kind:'actor',text:name,size:27,color:'#ffe7b9',x:hero.x+24*z,y:hero.y+heroTop*z-(name?49:17)-PAD,h:name&&bar?52:bar?22:37,maxWidth:280,priority:130,important:true,bar:bar?{kind:'hero',ratio:a.player.hp/attributes(a.player,a.content).hp}:null});
  if(bar)candidates.at(-1).w=Math.max(candidates.at(-1).w,106);
 }
 for(const e of c.events){
  if(a.player.insights?.[2]===0&&e.kind==='damage')continue;const point=a.screenPoint(e.x,e.y);if(!inView(point)||e.until<=c.elapsed)continue;
  const top=e.actorId==='player'?heroTop:labelTop(a.packs.get('Mon/'+e.appearance)),q=floatingTextLayout(e,c.elapsed,point,top,z);
  let id=a.worldEventIds.get(e);if(!id){id='event:'+(++a.nextWorldEventId);a.worldEventIds.set(e,id);}
  add({id,kind:'float',text:e.text,size:q.size,color:e.color,x:q.x,y:q.y-PAD,opacity:q.opacity,maxWidth:360,priority:e.kind==='damage'?e.actorId==='player'?135:120:110,important:true,order:e.born||0});
 }
 const objective=mainQuestObjective(a.player,a.content),needed=new Set((objective?.missing||[]).map(name=>a.content.itemNames.get(name)?.id).filter(Number.isInteger));
 const groups=groupGroundLabels(c.groundItems.filter(g=>inView(a.screenPoint(g.x,g.y))),{lootingId:c.lootingId,needed,itemFor:g=>g.kind==='gold'?null:instanceItem(a.content.items[g.itemId],g)});
 for(const group of groups){
  const {entry:g,item}=group,p=a.screenPoint(g.x,g.y);let bottom=p.y+48;
  for(const entry of group.entries){const it=entry.kind==='gold'?null:instanceItem(a.content.items[entry.itemId],entry),f=a.packs.get('Item1')?.frames[it?it.icon:groundItemIcon(entry)];if(f)bottom=Math.max(bottom,p.y+(24-f.original[1]/2+f.crop[1]+f.rect[3])*z);}
  const text=(item?itemName(item):'金币')+(g.quantity>1?' ×'+g.quantity:''),lines=[{text,size:24,color:insightOn(a.player,4)&&Object.keys(g.fieldOverrides||{}).length?'#ffc86a':'#f0d99e'}];
  if(group.entries.length>1)lines.push({text:'等 '+group.entries.length+' 堆',size:21,color:'#cab78f'});
  add({id:'drop:'+group.key,kind:'drop',text,lines,size:24,x:p.x+24*z,y:bottom+4,h:lines.length===1?34:58,maxWidth:248,priority:g.id===c.lootingId?115:needed.has(g.itemId)?105:group.priority>=100?80:g.kind==='gold'?55:65,dropId:g.id,dropIds:group.entries.map(e=>e.id),important:g.id===c.lootingId||needed.has(g.itemId),signature:lines.map(l=>l.text).join('|')});
 }
 const layout=layoutWorldLabels(candidates,viewport,rects,a.worldTextState);a.worldText={...layout,viewport,obstacles:rects,groundHits:[]};
 // Text is drawn in logical resolution after the world composite. It stays
 // legible above map foliage and never changes map-object depth ordering.
 // The .01 width tolerance keeps fractional cursors from dropping the last
 // glyph when its measured advance exactly equals the available width.
 for(const q of layout.placed){
  const opacity=q.opacity??1;
  if(q.kind==='drop'){
   b.quad(q.x,q.y,q.w,q.h,'#17120d',b.white,[0,0,1,1],.8);let y=q.y+PAD;
   for(const line of q.lines){const width=Math.min(q.w-PAD*2,b.textWidth(line.text,line.size));b.outlinedText(line.text,q.x+(q.w-width)/2,y,line.size,line.color,q.w-PAD*2+.01);y+=line.size+2;}
   a.worldText.groundHits.push({x:q.x,y:q.y,w:q.w,h:q.h,dropId:q.dropId,dropIds:q.dropIds});
  }else{
   const width=Math.min(q.w-PAD*2,b.textWidth(q.text,q.size));if(q.text)b.outlinedText(q.text,q.x+(q.w-width)/2,q.y+PAD,q.size,q.color,q.w-PAD*2+.01,opacity);
   if(q.bar){const w=q.bar.kind==='hero'?96:74,x=q.x+(q.w-w)/2,y=q.y+q.h-(q.bar.kind==='hero'?17:11);
    if(q.bar.kind==='hero')a.hud.bar('hp',x,y,w,12,q.bar.ratio);
    else{b.quad(x-1,y-1,w+2,8,'#100c09');b.quad(x,y,w,6,'#362018');b.quad(x,y,w*q.bar.ratio,6,'#ed5544');}
   }
  }
 }
}
