import {parseItemUpgrade,upgradeItems} from './item-upgrades.js';
import {rollEquipmentAffixes} from './equipment-affixes.js';
import {instanceItem,carryAmount} from './native-stats.js';
import {inventoryKey,carriedItems} from './inventory.js';
import {addItem,removeItem} from './character.js';
import {CHALLENGE_RULES} from './challenges.js';
import {scriptValue,changeScriptValue} from './npc-fields.js';
import {resolveItem,itemName} from './item-names.js';
const matchesItemName=(item,name)=>item?.name===name||itemName(item)===name;
const clean=line=>line.replace(/[\ue000-\uf8ff]/g,'').trim(),capabilities=new WeakMap();
export function scriptLines(script){
 let text=String(script||'').replace(/(#change\s+bt25\s*=\s*3600)@3change(\s+ET9\s*=\s*1)/gi,'$1\n#change$2');
 // Shipped 牛岛屠夫 B1 says #good2 instead of #goto GOOD2. Only repair
 // this precise renew branch with its own GH2/500-gold destination.
 if(/#Sub\s+GOOD2\s*\r?\n\s*#take\s+金币\s+500\s*\r?\n\s*#change\s+gh2\s*=\s*1\s*\r?\n\s*#change\s+gh\s*=\s*2/i.test(text))text=text.replace(/(#Sub\s+B1\s*\r?\n\s*#ITEMCK\s+金币\s*>\s*499\s*\r?\n\s*)#good2(?=\s*\r?\n\s*#endif)/i,'$1#goto GOOD2');
 return text.replace(/@(?=#)/g,'\n').replace(/(#end)(?=#)/gi,'$1\n').split(/\r?\n/).map(clean);
}
export function hasNpcDialogue(npc){if(capabilities.has(npc))return capabilities.get(npc);let shop=false;const available=scriptLines(npc.script).some(line=>{if(/^#buy\b/i.test(line)){shop=true;return false;}if(/^#endbuy\b/i.test(line)){shop=false;return false;}return /^#passmap\b/i.test(line)||!shop&&line&&!line.startsWith('#')&&!line.startsWith('//');});capabilities.set(npc,available);return available;}
export function hasNpcInteraction(npc){return !npc.removed&&(hasNpcDialogue(npc)||/#\s*(?:kwlr|itembox|cybox|buy|sell|move|tomap|button|change|give|take|setmapflag|setmapdata)\b/i.test(npc.script||''));}
function condition(expression,player,content,command,context){
 const m=expression.match(/^(.+?)\s*(>=|<=|<>|!=|==|=|>|<)\s*(-?\d+)$/);if(!m)return null;const name=m[1].trim();let left;
 if(command==='itemck')left=name==='金币'?player.gold:carriedItems(player).filter(i=>matchesItemName(instanceItem(content.items[i.itemId],i),name)).reduce((n,i)=>n+i.quantity,0);
 else if(command==='monck')left=context.units?context.units.filter(u=>u.alive&&!u.removed&&u.definition.name===name).length:undefined;
 else left=scriptValue(name,player,content,context);
 if(left===undefined)return null;const right=Number(m[3]);return ({'>=':()=>left>=right,'<=':()=>left<=right,'<>':()=>left!==right,'!=':()=>left!==right,'==':()=>left===right,'=':()=>left===right,'>':()=>left>right,'<':()=>left<right})[m[2]]();
}
export function applyNpcEffects(player,effects,content){
 const next=JSON.parse(JSON.stringify(player));for(const e of effects){
  if(e.kind==='give'){if(!content.items[e.itemId]||!Number.isSafeInteger(e.quantity)||e.quantity<1)return false;
   const grants=e.instances?e.instances.map(metadata=>({quantity:1,metadata})):[{quantity:e.quantity,metadata:{}}];if(e.instances&&e.instances.length!==e.quantity)return false;
   for(const grant of grants){const amount=carryAmount(next,content,e.itemId,grant.quantity,grant.metadata);if(amount&&!addItem(next,e.itemId,amount,grant.metadata))return false;if(amount<grant.quantity){next.pendingGroundItems||=[];next.pendingGroundItems.push({kind:'item',itemId:e.itemId,quantity:grant.quantity-amount,...grant.metadata});}}
  }
  else if(e.kind==='take'){let remaining=e.quantity;if(!Number.isSafeInteger(remaining)||remaining<=0)return false;for(const entry of carriedItems(next).filter(i=>e.name?matchesItemName(instanceItem(content.items[i.itemId],i),e.name):i.itemId===e.itemId)){const quantity=Math.min(remaining,entry.quantity);if(quantity&&!removeItem(next,inventoryKey(entry),quantity))return false;remaining-=quantity;if(!remaining)break;}if(remaining)return false;}
  else if(e.kind==='upgradeItem'){if(!upgradeItems(next,content,e))return false;}
  else if(e.kind==='change'){if(!changeScriptValue(next,e,content))return false;}
  else return false;
 }Object.assign(player,next);return true;
}
// Preview every effect before committing. Unsupported active commands and an
// exhausted jump budget invalidate the entire exchange, including world edits.
export function readNpcDialogue(script,player,content,page='Start',context={}){
 if(/#kwlr\b/i.test(script)&&content.permanent?.insightScript)script=content.permanent.insightScript;
 const source=scriptLines(script),sections=new Map([['START',[]]]);let current='START';
 for(const line of source){const sub=line.match(/^#(?:sub|label)\s+(\S+)/i);if(sub){current=sub[1].toUpperCase();if(!sections.has(current))sections.set(current,[]);}else sections.get(current).push(line);}
 const view={page:page.toUpperCase(),text:[],choices:[],effects:[],mapFlags:[],worldEffects:[],passMap:false,move:null,shopItems:[],shop:false,sell:false,storage:null,close:false,silent:source.some(l=>/^#notui\b/i.test(l)),unsupported:[]},preview=JSON.parse(JSON.stringify(player));
 const finish=()=>{if(view.unsupported.length){view.effects=[];view.mapFlags=[];view.worldEffects=[];view.move=null;view.passMap=false;view.shop=false;view.sell=false;view.storage=null;view.refining=null;view.close=false;view.text=['暂时无法完成这项操作。'];view.choices=[{label:'关闭',action:'OVER'}];}return view;};
 for(let jumps=0;jumps<32;jumps++){
  const lines=sections.get(view.page);if(!lines){view.unsupported.push('missing page '+view.page);return finish();}const stack=[];let active=true,shop=false,jump=null;
  for(const line of lines){if(!line||line.startsWith('//'))continue;const m=line.match(/^#(\S+)\s*(.*)$/),command=m?.[1].toLowerCase(),args=m?.[2]||'';
   if(['if','itemck','monck'].includes(command)){const matched=active?condition(args,preview,content,command,context):false;if(active&&matched===null)view.unsupported.push(line);stack.push({parent:active,matched,used:matched===true});active=active&&matched===true;continue;}
   if(command==='else'){const state=stack.at(-1);if(state){active=state.parent&&state.matched!==null&&!state.used;state.used=true;}continue;}
   if(command==='elseif'){const state=stack.at(-1);if(state){const matched=state.parent&&!state.used?condition(args,preview,content,'if',context):false;if(matched===null)view.unsupported.push(line);active=state.parent&&!state.used&&matched===true;state.used||=matched===true;}continue;}
   if(command==='endif'){const state=stack.pop();if(state)active=state.parent;continue;}
   if(!active)continue;
   if(command==='buy'){view.shop=true;shop=true;continue;}if(command==='endbuy'){shop=false;continue;}if(shop){const item=resolveItem(content,line);if(item)view.shopItems.push(item.id);else if(!m)view.unsupported.push(line);continue;}
   if(!m){view.text.push(line);continue;}
   if(command==='end')return finish();
   if(command==='goto'){jump=args.trim().toUpperCase();break;}
   if(command==='button'){const button=args.match(/^(.*?)\s+-?\d+\s+-?\d+\s+\S+\s+(.+)$/);if(button){const action=button[2].trim(),target=action.split(/\s+/)[0].toUpperCase();if(target==='OVER'||target==='TOMAP'||sections.has(target))view.choices.push({label:button[1],action});}continue;}
   if(command==='passmap'){view.passMap=true;continue;}
   if(command==='notui')continue;
   if(['close','closeall','closewindow'].includes(command)){view.close=true;continue;}
   if(command==='gameover'&&!args){view.worldEffects.push({kind:'gameover'});view.close=true;continue;}
   if(['reme','repet','stop','unstop'].includes(command)&&!args){view.worldEffects.push({kind:command});continue;}
   if(['defstart','defhpup','defdfup','defdmup'].includes(command)&&!args){view.worldEffects.push({kind:command});continue;}
   if(['时间挑战','生存挑战'].includes(command)&&!args){const mode=command==='时间挑战'?'time':'survival',rule=CHALLENGE_RULES[mode];view.worldEffects.push({kind:'challenge',mode});view.move={id:rule.map,x:rule.entry[0],y:rule.entry[1]};continue;}
   if(command==='defhpadd'){if(/^(?:0?\.1|0?\.2)$/.test(args))view.worldEffects.push({kind:command,fraction:Number(args)});else view.unsupported.push(line);continue;}
   if(command==='addfriendhero'||command==='addfriendheron'||command==='addmonhero'){
    const m=args.match(command!=='addmonhero'?/^(.+?)\s+(\d+)$/:/^(.+)$/),name=m?.[1],level=command!=='addmonhero'?Number(m?.[2]):1;
    if(m&&level>=1&&level<=10&&content.monsterNames?.has(name))view.worldEffects.push({kind:command,name,level});else view.unsupported.push(line);continue;
   }
   if(command==='itembox'||command==='cybox'){view.storage=command==='itembox'?'storage':'dimension';continue;}
   if(command==='sell'){view.sell=true;continue;}
   if(command==='forge'||command==='merge'){view.refining=command;continue;}
   if(['setmapflag','setmapdata','movenpc','delnpc','delallmon','addmon'].includes(command)){
    const words=args.split(/\s+/),numbers=words.map(Number);let effect;
    if(command==='setmapflag'&&[2,3].includes(numbers.length)&&numbers.every(Number.isInteger)){view.mapFlags.push([numbers[0],numbers[1],numbers[2]||0]);continue;}
    if(command==='setmapdata'&&[3,4].includes(numbers.length)&&numbers.every(Number.isInteger))effect={kind:command,x:numbers[0],y:numbers[1],type:numbers[2],index:numbers[3]||0};
    else if(command==='movenpc'&&numbers.length===4&&numbers.every(Number.isInteger))effect={kind:command,x:numbers[0],y:numbers[1],toX:numbers[2],toY:numbers[3]};
    else if(command==='delnpc'&&numbers.length===2&&numbers.every(Number.isInteger))effect={kind:command,x:numbers[0],y:numbers[1]};
    else if(command==='delallmon'&&!args)effect={kind:command};
    else if(command==='addmon'&&words.length>=3&&numbers.slice(0,2).every(Number.isInteger)&&content.monsterNames?.has(words.slice(2).join(' ')))effect={kind:command,x:numbers[0],y:numbers[1],name:words.slice(2).join(' ')};
    else view.unsupported.push(line);
    if(effect)view.worldEffects.push(effect);continue;
   }
   if(command==='move'||command==='tomap'){const m=args.match(/^(?:(\S+)\s+)?(\d+)\s+(\d+)$/);if(m)view.move={id:m[1]?.toUpperCase()||context.map?.id,x:Number(m[2]),y:Number(m[3])};else view.unsupported.push(line);continue;}
   if(command==='upweapon'){const effect=parseItemUpgrade(args);if(effect&&applyNpcEffects(preview,[effect],content))view.effects.push(effect);else view.unsupported.push(line);continue;}
   if(['give','take','change'].includes(command)){
    let effect;if(command==='change'){const valueArgs=args.replace(/^(游戏模式\s*=\s*)(普通模式|专家模式|地狱模式)$/,(all,prefix,mode)=>prefix+['普通模式','专家模式','地狱模式'].indexOf(mode));const m=valueArgs.match(/^(.+?)\s*([=+-])\s*(-?\d+)$/);if(m)effect={kind:'change',field:m[1].trim(),operator:m[2],value:Number(m[3])};}
    else {const m=args.match(/^(.+?)(?:\s+(\d+))?$/),name=m?.[1],quantity=Number(m?.[2]||1);if(name==='金币')effect={kind:'change',field:'money',operator:command==='give'?'+':'-',value:quantity};else{const item=resolveItem(content,name)||command==='take'&&carriedItems(preview).map(e=>instanceItem(content.items[e.itemId],e)).find(i=>i?.name===name);if(item&&quantity>0)effect={kind:command,itemId:item.id,name,quantity};}}
    if(effect?.kind==='give'&&content.items[effect.itemId].type>=7&&content.items[effect.itemId].type<=14)effect.instances=Array.from({length:effect.quantity},()=>rollEquipmentAffixes(content.items[effect.itemId],preview,context.random||Math.random));
    if(effect&&applyNpcEffects(preview,[effect],content))view.effects.push(effect);else view.unsupported.push(line);continue;
   }
   view.unsupported.push(line);
  }
  if(!jump)return finish();view.page=jump;
 }
 view.unsupported.push('jump budget exceeded');return finish();
}
export function nearbyNpcs(map,position){return map.npcs.flatMap((npc,index)=>hasNpcInteraction(npc)&&Math.abs(npc.x-position.x)<=12&&Math.abs(npc.y-position.y)<=15?[{...npc,index,kind:'npc'}]:[]).sort((a,b)=>Math.hypot(a.x-position.x,a.y-position.y)-Math.hypot(b.x-position.x,b.y-position.y));}
