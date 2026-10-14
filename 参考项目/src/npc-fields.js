import {followingPet} from './allies.js';
import {PROPERTY_FIELDS} from './native-stats.js';
import {attributes} from './character.js';
import {gainExperience} from './progression.js';
import {HEAD_APPEARANCE_MODEL} from './appearance.js';
const ranges={dc:['attack',0],dcmax:['attack',1],sc:['tao',0],scmax:['tao',1],mc:['magic',0],mcmax:['magic',1],df:['defense',0],dfmax:['defense',1],dm:['magicDefense',0],dmmax:['magicDefense',1]};
const scalars={money:'gold',gold:'gold','金币':'gold',ex:'experience',experience:'experience',hp:'hp',mp:'mp',level:'level',lv:'level',sex:'gender',hd:'headStyle',cb:'wings','属性点':'attributePoints','技能点':'skillPoints','通关次数':'clearCount','游戏模式':'gameMode'};
const propertyNames={'快速打击':'fastAttack','快速施法':'fastCast','快攻':'fastAttack','快法':'fastCast','物理躲避':'physicalEvade','魔法躲避':'magicEvade','准确':'accuracy','冰封':'freeze','引燃':'burn','燃烧':'burn','中毒':'poison','麻痹':'paralysis','吸血':'vampire','伤害反弹':'reflect','幸运':'luck','负重':'capacity'};
const indexed=name=>/^(et|bt|hd|cb|gh)(\d*)$/i.exec(name);
const skill=(name,content)=>content.skills.records.find(r=>r.name===name);
// Native query 606de0 and change 608b20; scripted skill rewards have their own
// acquisition rules, independent of the ordinary skill-point panel.
export function scriptValue(name,player,content,{random=Math.random,units,waitingPets=[],defense}={},base=false){
 const key=name.toLowerCase(),index=indexed(key);
 if(key==='gh')return player.aura||0;
 if(index?.[1]==='gh'&&index[2])return Number(index[2])<10?player.auraUnlocks?.[Number(index[2])]||0:undefined;
 if(key==='kwzt')return player.insightFreeCount||0;
 if(['defhpup','defdfup','defdmup'].includes(key))return defense?.[{defhpup:'hpUp',defdfup:'dfUp',defdmup:'dmUp'}[key]]||0;
 if(key==='friend'||key==='friendcount')return units?[...units,...waitingPets].filter(u=>u.alive&&u.summoned&&(key==='friend'?followingPet(u):!u.defenseFlag)).length:undefined;
 if(/^kw\d+$/.test(key)){const id=Number(key.slice(2));return id<13?player.insights?.[id]??-1:undefined;}
 if(index&&index[2]){const i=Number(index[2]),kind=index[1];if(kind==='et'||kind==='bt')return i<30?(player[kind==='et'?'events':'bossTimers']?.[i]??(kind==='bt'?-1:0)):undefined;if(i<1||i>(kind==='hd'?6:9))return undefined;return player.appearanceUnlocks?.[kind]?.[i]||0;}
 if(key==='et'||key==='bt')return player[key==='et'?'events':'bossTimers']?.[0]??(key==='bt'?-1:0);
 if(skill(name,content))return player.skills.find(s=>s.name===name)?.level||0;
 if(propertyNames[key])return (base?player.base:attributes(player,content))[propertyNames[key]]||0;
 if(ranges[key]){const [field,end]=ranges[key];return (base?player.base:attributes(player,content))[field]?.[end];}
 if(key==='hpmax'||key==='mpmax')return player.base[key==='hpmax'?'hp':'mp'];
 if(key==='bank')return player.storage?.gold||0;
 if(key==='职业')return ['战士','道士','法师'].indexOf(player.class);
 if(key==='rnd')return Math.min(100,Math.floor(random()*100)+1);
 return scalars[key]?player[scalars[key]]||0:undefined;
}
export function changeScriptValue(player,effect,content){
 const {field,operator,value}=effect,key=field.toLowerCase(),old=scriptValue(field,player,content,{},true);
 if(old===undefined||!['=','+','-'].includes(operator)||!Number.isSafeInteger(value))return false;
 const n=operator==='='?value:operator==='+'?old+value:old-value,index=indexed(key);if(!Number.isSafeInteger(n))return false;
 if(key==='gh'){if(operator!=='='||![0,2].includes(n))return false;player.aura=n;return true;}
 if(index?.[1]==='gh'){if(operator!=='='||![0,1].includes(n))return false;player.auraUnlocks||=Array(10).fill(0);player.auraUnlocks[Number(index[2])]=n;return true;}
 if(key==='kwzt'){if(n<0||n>2)return false;player.insightFreeCount=n;return true;}
 if(/^kw\d+$/.test(key)){if(![-1,0,1].includes(n))return false;player.insights||=Array(13).fill(-1);player.insights[Number(key.slice(2))]=n;return true;}
 if(index&&(index[1]==='et'||index[1]==='bt')){if(n< -32768||n>32767)return false;const target=index[1]==='et'?'events':'bossTimers';player[target]||=[];player[target][Number(index[2]||0)]=n;return true;}
 if(propertyNames[key]){if(n< -32768||n>32767)return false;player.base[propertyNames[key]]=n;return true;}
 if(n<0)return false;
 if(index&&index[2]){if(n>32767)return false;player.appearanceUnlocks||={};player.appearanceUnlocks[index[1]]||=[];player.appearanceUnlocks[index[1]][Number(index[2])]=n;return true;}
 if(skill(field,content)){if(n>32767)return false;const learned=player.skills.find(s=>s.name===field);if(n===0)player.skills=player.skills.filter(s=>s.name!==field);else if(learned)learned.level=n;else player.skills.push({name:field,level:n});if(!player.skills.some(s=>s.name===player.activeSkill))player.activeSkill=player.skills[0]?.name||null;return true;}
 if(ranges[key]){const [stat,end]=ranges[key];player.base[stat][end]=n;return true;}
 if(key==='hpmax'||key==='mpmax'){const stat=key==='hpmax'?'hp':'mp';if(n>32767)return false;player.base[stat]=n;player[stat]=Math.min(player[stat],n);return true;}
 if(key==='bank'){player.storage||={items:[],gold:0};player.storage.gold=n;return true;}
 const target=scalars[key];if(target==='gameMode'){if(operator!=='='||n>2||n>old)return false;player.gameMode=n;return true;}if(!target||['level','gender','clearCount'].includes(target))return false;
 if(target==='headStyle'&&(operator!=='='||n>6)||target==='wings'&&(operator!=='='||n>9))return false;
 if(target==='experience'){if(n>old)gainExperience(player,n-old);else player.experience=n;return true;}
 player[target]=target==='hp'||target==='mp'?Math.min(player.base[target],n):n;if(target==='headStyle')player.headAppearanceModel=HEAD_APPEARANCE_MODEL;return true;
}
