import {attributes} from './character.js';
import {classAllowsSkill} from './skill-classes.js';
// Native evidence and the 26 recovered skill cases: native-growth-source.json.
export const ATTRIBUTE_CHOICES=[['attack','攻击','生命上限 +1'],['tao','道术','魔法上限 +2'],['magic','魔法','魔法上限 +3'],['defense','防御','生命上限 +2'],['magicDefense','魔防','生命 +1，魔法 +2']];
const points=n=>Number.isSafeInteger(n)&&n>=0?n:0;
export function skillEligibility(player,record){
 const level=player.skills.find(s=>s.name===record?.name)?.level||0;
 if(record&&!classAllowsSkill(record,player.class))return {allowed:false,level,cost:0,reason:'仅限'+record.classes.join('、')+'学习'};
 if(!record?.pointCosts?.length){const source=record?.acquisition;return {allowed:false,level,cost:0,reason:source?(level>=source.maxLevel?'已满级':source.mapName+' · '+source.npc):'通过特殊途径获取'};}
 if(level>=record.maxLevel)return {allowed:false,level,cost:0,reason:'已满级'};
 const cost=record.pointCosts[level],missing=record.prerequisites.filter(([name,lv])=>(player.skills.find(s=>s.name===name)?.level||0)<Number(lv));
 if(missing.length)return {allowed:false,level,cost,missing,reason:'需要 '+missing.map(([name,lv])=>name+' '+lv+'级').join('、')};
 if(points(player.skillPoints)<cost)return {allowed:false,level,cost,reason:'技能点不足'};
 return {allowed:true,level,cost,reason:null};
}
export function improveSkill(player,record){
 const eligibility=skillEligibility(player,record);if(!eligibility.allowed)return eligibility;
 const learned=player.skills.find(s=>s.name===record.name);if(learned)learned.level++;else player.skills.push({name:record.name,level:1});
 player.skillPoints-=eligibility.cost;return {...eligibility,level:eligibility.level+1};
}
export function skillDescription(record,level=1){
 level=Math.max(1,level);const values={proc8:8*level,proc4:4*level,proc10:10*level,bonus10:10*level,level,refine:15*(level+1)};
 return (record.descriptionTemplate||record.description).replace(/\{(\w+)\}/g,(_,key)=>values[key]??'');
}
export function allocateAttribute(player,content,key,random=Math.random){
 if(!ATTRIBUTE_CHOICES.some(([k])=>k===key)||points(player.attributePoints)<1)return false;
 const total=attributes(player,content)[key],base=player.base[key];if(!Array.isArray(base)||!Array.isArray(total))return false;
 // Native handlers use the currently worn totals for the ratio, then add one
 // endpoint. A 0–0 legacy range raises max to avoid a zero denominator.
 const end=total[1]<=0||random()<total[0]/total[1]?1:0;
 base[end]++;player.attributePoints--;
 if(key==='attack')player.base.hp++;else if(key==='tao')player.base.mp+=2;else if(key==='magic')player.base.mp+=3;else {player.base.capacity=(player.base.capacity||0)+1;player.base.hp+=key==='defense'?2:1;if(key==='magicDefense')player.base.mp+=2;}
 return {key,end,before:total[end],after:total[end]+1};
}
export function drawAttributeDialog(app){
 const b=app.batch,h=app.hud,stats=attributes(app.player,app.content);app.buttons=[];
 b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.58);b.quad(68,405,614,819,'#211915');h.panel(68,405,614,819);b.text('分配属性',98,447,34,'#e8c887');app.button('关闭',541,431,108,64,()=>app.attributeOpen=false,false,27);b.text('属性点 '+app.player.attributePoints,100,525,29,'#dfc384');
 ATTRIBUTE_CHOICES.forEach(([key,label,bonus],i)=>{const y=590+i*112;b.text(label+' '+stats[key].join('–'),100,y+6,29,'#e5d1a7',425);b.text(bonus,100,y+48,24,'#b5a17d',425);h.button(552,y,96,78);h.centered('+',552,y+20,96,36);app.region('+',552,y,96,78,()=>{if(allocateAttribute(app.player,app.content,key))app.save();});});
 if(!app.player.attributePoints)b.text('属性点已用完',100,1175,25,'#aa9879');
}
