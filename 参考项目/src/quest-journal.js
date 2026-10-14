import {taskFor} from './character.js';
import {readNpcDialogue} from './npc-dialogue.js';
import {carriedItems} from './inventory.js';
const owns=(p,c,name)=>carriedItems(p).some(e=>e.itemId===c.itemNames.get(name)?.id&&e.quantity>0);
const routes=[
 {event:2,map:'D00',name:'华月太守',title:'清剿监狱与地牢',visible:p=>p.clearCount>0&&p.events?.[2]<4},
 {event:3,map:'E00',name:'镇长',title:'清剿魔灵蜘蛛',visible:p=>(p.events?.[0]||0)>=16||(p.events?.[3]||0)>0,describe:(_p,_c,value)=>value===0?{status:'进行中',description:'苍梧镇长请你清剿镇东蜘蛛坳的毒蜘蛛。进入蜘蛛巢穴，击败魔灵蜘蛛后回镇长处领取酬谢。'}:value===1?((_p.events?.[0]||0)>=16?{status:'可交付',description:'魔灵蜘蛛已被击败。回苍梧镇与镇长对话，领取1000金币酬谢。'}:{status:'进行中',description:'魔灵蜘蛛已被击败。先与苍梧镇长继续打听恶魔谷，获得手信后再领取酬谢。'}):{status:'已完成',description:'你已清剿魔灵蜘蛛，并领取了苍梧镇长的酬谢。'}},
 {event:4,map:'F01',name:'隐士',title:'归还铁锤',describe:(p,c,value)=>value===1?{status:'已完成',description:'你已把师傅传下的铁锤归还隐士，领取银矿石与1000金币酬谢。'}:owns(p,c,'铁锤')?{status:'可交付',description:'你找到了隐士遗失的铁锤。前往大漠北，将铁锤还给隐士。'}:{status:'进行中',description:'大漠北的隐士因丢失师傅传下的铁锤而离家。找到铁锤后，将它归还隐士。'}},
 {event:6,map:'H00',name:'村大夫',title:'救采药人',resolve:(p,value)=>value===0&&p.unlockedMaps.includes('H40')?{map:'H40',name:'采药人'}:null,describe:(_p,_c,value)=>value===0?{status:'进行中',description:'栗园村大夫的兄长前往毒蛇山谷采药，至今未归。找到受困的采药人，与他对话并将其救出。'}:value===1?{status:'可交付',description:'采药人已获救。回栗园村找村大夫，领取1000金币与3瓶太阳水（小）。'}:{status:'已完成',description:'采药人已安全归家，你已领取村大夫的酬谢。'}},
 {event:10,map:'A30',name:'荣耀老者',title:'荣耀历练'},
 {event:11,map:'K00',name:'祭坛传送',title:'激活祭坛'},
 {event:12,map:'K00',name:'异族村长',title:'异族村落'},
 {event:13,map:'K25',name:'张宝',title:'张宝的委托'},
 {event:14,map:'K25',name:'刘靖',title:'刘靖的委托'},
 {event:15,map:'K22',name:'天界熔炉',title:'天界熔炉'},
];
export async function prepareQuestJournal(app){
 const p=app.player,main=taskFor(p,app.content.tasks.text),rows=main?[{title:main.title,description:main.description,main:true}]:[];
 for(const route of routes){const value=p.events?.[route.event]||0,destination=route.resolve?.(p,value),mapId=destination?.map||(route.event===2&&value>=2?'J00':route.map),name=destination?.name||(mapId==='J00'?'齐阳太守':route.name);if(!p.unlockedMaps.includes(mapId)&&!([3,6].includes(route.event)&&value>0)||route.visible&&!route.visible(p))continue;
  const map=mapId===app.mapId?app.map:await app.content.json('maps/'+mapId+'.json'),index=map.npcs.findIndex(n=>n.name===name&&!n.removed);if(index<0)continue;
  const view=readNpcDialogue(map.npcs[index].script,p,app.content,'Start',{map,random:()=>.5}),details=route.describe?.(p,app.content,value),description=details?.description||view.text.join('\n').trim();if(!description||view.unsupported.length)continue;
  rows.push({title:route.title,...details,description,event:route.event,value,mapId,index,name});
 }
 app.questJournal=rows;app.questPage=Math.min(app.questPage||0,Math.max(0,rows.length-1));return rows;
}
export function drawQuestJournal(a){
 const main=taskFor(a.player,a.content.tasks.text),rows=a.questJournal||(main?[{...main,main:true}]:[]),index=Math.min(a.questPage||0,Math.max(0,rows.length-1)),r=rows[index],b=a.batch,h=a.hud;if(!r)return;
 b.text(r.title,26,1081,32,'#e3c382');if(r.status)b.text(r.status,114,1118,23,r.status==='可交付'?'#e3c382':'#b8ab90');h.image('tasks-0',26,1140,64,64);const size=28,lines=[];let row='',used=0;for(const c of r.description){const advance=(a.content.font.glyphs[c]?.advance||32)*size/32;if(c==='\n'||used+advance>572){lines.push(row);row='';used=0;if(c==='\n')continue;}row+=c;used+=advance;}if(row)lines.push(row);const page=Math.min(a.questTextPage||0,Math.max(0,Math.ceil(lines.length/5)-1));lines.slice(page*5,page*5+5).forEach((line,i)=>b.text(line,114,1149+i*43,size));
 if(lines.length>5)a.button(page*5+5<lines.length?'继续阅读':'从头阅读',114,1370,260,49,()=>a.questTextPage=page*5+5<lines.length?page+1:0,false,24);
 if(r.main){const target=a.firstQuestTarget();if(target)a.button(target.label,114,1438,572,64,()=>a.followFirstQuest(),false,28);}
 else if(r.status!=='已完成'){if(r.mapId===a.mapId)a.button('与'+r.name+'对话',114,1438,572,64,()=>{a.tab='战斗';return a.selectNpc(r.index);},false,28);else h.centered(a.content.mapList.find(m=>m.id===r.mapId)?.name||r.mapId,114,1450,572,27);}
 if(rows.length>1){a.button('上个任务',370,1065,164,56,()=>{a.questPage=(index+rows.length-1)%rows.length;a.questTextPage=0;},false,24);a.button('下个任务',545,1065,164,56,()=>{a.questPage=(index+1)%rows.length;a.questTextPage=0;},false,24);}
}
