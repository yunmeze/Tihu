import {DIFFICULTIES,availableCharacterModes} from './difficulty.js';
import {CHARACTER_CLASSES,createNewCharacter} from './character.js';
import {characterAppearance,avatarLayers,avatarBounds,fitAvatar,drawAvatarLayers} from './appearance.js';
export class EntryScreens{
 constructor(app){this.app=app;this.page=0;this.selectedId=app.roster.activeId;this.error=null;}
 async init(){const a=this.app;for(const id of ['Data1','Data2']){const pack=await a.loadPack(id);await Promise.all(pack.pages.map(p=>a.content.texture(p.file)));}await a.content.sync();}
 async show(screen){const a=this.app;this.error=null;this.confirmDelete=null;this.page=0;a.screen=screen;if(screen==='create'){this.draft={name:a.roster.defaultName(),class:'战士',gender:0,gameMode:0};await this.preview(createNewCharacter(a.content,this.draft));}else if(screen==='characters'||screen==='delete'){this.selectedId=a.roster.get(this.selectedId)?.id||a.roster.activeId;this.page=Math.max(0,Math.floor(a.roster.characters.findIndex(r=>r.id===this.selectedId)/3));await this.previewSelected();}}
 async previewSelected(){const state=this.app.roster.get(this.selectedId)?.state;this.previewPlayer=state?.player||null;if(state)await this.preview(state.player);}
 async preview(player){const a=this.app,request=this.previewRequest=(this.previewRequest||0)+1,appearance=characterAppearance(player,a.content),layers=avatarLayers(appearance,{action:'idle',direction:5});this.previewLoading=true;try{await Promise.all(layers.map(async l=>{await a.loadPack(l.pack);await a.content.frame(l.pack,l.index);}));await a.content.sync();if(request===this.previewRequest){this.previewAppearance=appearance;this.previewPlayer=player;}}finally{if(request===this.previewRequest)this.previewLoading=false;}}
 sprite(packName,index,x,y,w,h,region=null,color='#ffffff'){
  const a=this.app,pack=a.packs.get(packName),f=pack?.frames[index];if(!f)return;const p=pack.pages[f.page],t=a.content.textureNow(p.file);if(!t)return;
  if(region){const [sx,sy,sw,sh]=region;a.batch.quad(x,y,w,h,color,t,[(f.rect[0]-f.crop[0]+sx)/p.width,(f.rect[1]-f.crop[1]+sy)/p.height,sw/p.width,sh/p.height]);return;}
  const zx=w/f.original[0],zy=h/f.original[1];a.batch.quad(x+f.crop[0]*zx,y+f.crop[1]*zy,f.rect[2]*zx,f.rect[3]*zy,color,t,[f.rect[0]/p.width,f.rect[1]/p.height,f.rect[2]/p.width,f.rect[3]/p.height]);
 }
 button(index,label,x,y,w=400,h=118,action,enabled=true){this.sprite('Data2',index,x,y,w,h,null,enabled?'#ffffff':'#716553');if(enabled)this.app.region(label,x,y,w,h,action);}
 choice(label,x,y,w,h,action,selected){const a=this.app;a.button(label,x,y,w,h,action,selected,30);if(selected){a.batch.quad(x+7,y+5,w-14,2,'#c2984e');a.batch.quad(x+7,y+h-7,w-14,2,'#c2984e');}}
 background(){const a=this.app,b=a.batch;b.quad(0,0,750,1624,'#251d16');this.sprite('Data1',8,0,42,750,1538,[290,50,235,420]);this.sprite('Data1',3,0,0,750,42);this.sprite('Data1',4,0,1582,750,42);}
 panel(x,y,w,h){this.app.batch.quad(x,y,w,h,'#2b201a');this.app.hud.panel(x,y,w,h);}
 title(text,y=190,size=72){this.app.hud.centered(text,55,y,640,size,'#3c2414');}
 portrait(x,y,w,h){const a=this.app;if(!this.previewAppearance||!this.previewPlayer)return;const actor={action:'idle',direction:5},layers=avatarLayers(this.previewAppearance,actor),fit=fitAvatar(avatarBounds(a.packs,layers),{x,y,w,h,maxScale:4});if(fit)drawAvatarLayers(a.batch,a.packs,this.previewAppearance,actor,fit.x,fit.y,fit.scale,{time:a.elapsed});}
 async editName(){const a=this.app;if(this.editing)return;this.editing=true;try{const name=await a.platform.editName?.({value:this.draft.name,maxLength:12});if(name!==null&&name!==undefined)this.draft.name=name.trim();this.error=null;}finally{this.editing=false;}}
 async choose(field,value){this.draft[field]=value;this.error=null;await this.preview(createNewCharacter(this.app.content,this.draft));}
 async create(){const a=this.app,name=this.draft.name.trim();if(!name||[...name].length>12){this.error='姓名请输入一至十二个字';return;}if(/[\u0000-\u001f\\/:*?"<>|]/.test(name)){this.error='姓名包含不能使用的字符';return;}if([...name].some(c=>!a.content.font.glyphs[c])){this.error='请换一个姓名';return;}if(a.roster.nameExists(name)){this.error='这个姓名已有存档';return;}
  if(!availableCharacterModes(a.roster).includes(this.draft.gameMode)){this.error='该模式尚未解锁';return;}const player=createNewCharacter(a.content,{...this.draft,name});await a.createGame(player);
 }
 draw(){const a=this.app,b=a.batch,h=a.hud;this.background();
  if(a.screen==='home'){a.button('声音',18,60,124,62,()=>a.systemMenu=true,false,27);this.title('小小传奇',315,100);this.button(1,'踏入江湖',175,985,400,112,()=>this.show('create'));this.button(9,'再续前缘',175,1133,400,118,()=>this.show('characters'),a.roster.characters.length>0);this.button(11,'自废武功',175,1283,400,118,()=>this.show('delete'),a.roster.characters.length>0);return;}
  if(a.screen==='loading'){this.title('小小传奇',315,100);h.centered('进入江湖中',120,1000,510,36,'#4c321e');return;}
  if(a.screen==='create'){
   this.sprite('Data1',11,255,160,240,86);this.portrait(240,325,270,280);this.panel(36,649,678,744);const p=CHARACTER_CLASSES[this.draft.class];
   b.text('姓名',69,710,33,'#ddc48c');h.button(182,689,460,73);h.centered(this.draft.name||'点击输入姓名',194,710,436,32);a.region('姓名',182,689,460,73,()=>this.editName());
   b.text('职业',69,824,33,'#ddc48c');Object.keys(CHARACTER_CLASSES).forEach((job,i)=>this.choice(job,182+i*155,803,145,74,()=>this.choose('class',job),this.draft.class===job));
   b.text('性别',69,938,33,'#ddc48c');for(const [label,gender,i]of [['男',0,0],['女',1,1]])this.choice(label,182+i*235,917,225,74,()=>this.choose('gender',gender),this.draft.gender===gender);
   b.text('模式',69,1052,33,'#ddc48c');const modes=availableCharacterModes(a.roster),mw=460/modes.length;for(const mode of modes)this.choice(DIFFICULTIES[mode],182+mode*mw,1031,mw-6,74,()=>this.choose('gameMode',mode),this.draft.gameMode===mode);
   h.centered(p.description,70,1155,610,32,'#ddcba7');h.centered('生命 '+p.hp+'   魔法 '+p.mp,70,1230,610,30,'#ddcba7');if(this.error)h.centered(this.error,66,1320,618,28,'#edac84');
   this.button(17,'返回',45,1439,300,89,()=>this.show('home'));this.button(15,'创建角色',405,1439,300,89,()=>this.create());return;
  }
  const deleting=a.screen==='delete',selected=a.roster.get(this.selectedId),list=a.roster.characters,pages=Math.max(1,Math.ceil(list.length/3));this.page=Math.min(this.page,pages-1);
  this.sprite('Data1',10,255,160,240,86);this.portrait(240,320,270,260);if(selected){const p=selected.state.player;h.centered(p.name+'  '+p.class+'  Lv.'+p.level,74,601,602,33,'#3e2815');}
  this.panel(36,704,678,645);for(let i=0;i<3;i++){const record=list[this.page*3+i];if(!record)continue;const p=record.state.player,y=760+i*147;h.button(70,y,610,122,this.selectedId===record.id);if(this.selectedId===record.id){b.quad(78,y+6,594,2,'#c2984e');b.quad(78,y+114,594,2,'#c2984e');}b.text(p.name,95,y+18,36,'#e6c991',565);b.text(p.class+'  '+(p.gender?'女':'男')+'  Lv.'+p.level,95,y+70,28,'#c7b598',555);a.region('存档:'+record.id,70,y,610,122,async()=>{this.selectedId=record.id;await this.previewSelected();});}
  if(pages>1){a.button('上一页',70,1216,184,68,()=>this.page=Math.max(0,this.page-1),false,26);h.centered((this.page+1)+' / '+pages,285,1238,180,26);a.button('下一页',496,1216,184,68,()=>this.page=Math.min(pages-1,this.page+1),false,26);}
  if(this.error)h.centered(this.error,66,1302,618,27,'#edac84');
  this.button(17,'返回',45,1439,300,89,()=>this.show('home'));if(selected)this.button(deleting?11:9,deleting?'自废武功':'再续前缘',405,1439,300,89,()=>deleting?this.confirmDelete=selected.id:a.startGame(selected.state,{characterId:selected.id}));
  if(this.confirmDelete){const record=a.roster.get(this.confirmDelete);a.buttons=[];b.quad(0,0,750,1624,'#080604',b.white,[0,0,1,1],.62);this.panel(65,615,620,366);h.centered('删除 '+record.state.player.name+' 的存档？',86,701,578,34);this.button(17,'取消删除',107,841,240,72,()=>this.confirmDelete=null);this.button(23,'确认删除',404,841,240,72,async()=>{a.roster.remove(record.id);a.platform.save(a.roster.serialize());if(a.characterId===record.id)a.sessionLoaded=false;this.confirmDelete=null;this.selectedId=a.roster.activeId;await this.previewSelected();});}
 }
}
