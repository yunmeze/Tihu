import {spawnUnit,emptySpawnCell} from './monster-spawning.js';
import {validStatuses} from './pet-state.js';
import {nativeRound,monsterWalkable} from './monster-motion.js';
import {clearMonsterAggro} from './monster-ai.js';
import {difficultyMonster} from './difficulty.js';

const livingFlags=c=>c.units.filter(u=>u.defenseFlag&&u.alive);
export const defenseEnemies=c=>c.units.filter(u=>u.alive&&!u.summoned);
export const canContinueDefense=c=>c.defense?.status==='active'&&c.defense.waiting&&!defenseEnemies(c).length&&c.player.hp>0;
export function continueDefense(c){if(!canContinueDefense(c))return false;c.defense.waiting=false;return true;}
export function startDefense(c){
 const rules=c.content.defense;if(!rules||c.map.id!==rules.map)return false;
 c.defense={version:1,map:rules.map,status:'active',clock:rules.initialClock,remainder:0,waiting:true,wave:0,cursor:0,hpUp:0,dfUp:0,dmUp:0};
 for(const u of c.units)if(u.definition.name==='战旗'){const base=c.monsterNames.get('战旗');Object.assign(u,{definition:{...base},hp:base.hp,summoned:true,defenseFlag:true,temporary:true});}
 const saved=c.restoredDefense;c.restoredDefense=null;if(saved)restoreDefense(c,saved);
 return true;
}
export function upgradeDefense(c,e){
 const d=c.defense;if(!d||d.status!=='active')return false;
 const flags=livingFlags(c);
 if(e.kind==='defhpadd'){for(const u of flags)u.hp=Math.min(u.definition.hp,nativeRound(u.hp+Math.fround(e.fraction)*u.definition.hp));}
 else{
  const key={defhpup:'hpUp',defdfup:'dfUp',defdmup:'dmUp'}[e.kind];if(!key)return false;d[key]++;
  for(const u of flags){u.definition={...u.definition};if(key==='hpUp'){u.definition.hp+=300;u.hp+=300;}else u.definition[key==='dfUp'?'defense':'magicDefense']+=5;}
 }return true;
}
function plannedSpawns(c,event){
 if(c.units.filter(u=>u.alive||!u.temporary).length+event.spawns.length>600)return null;
 const plans=[],reserved=new Set();
 for(const spec of event.spawns){
  const candidates=[],queue=[{x:spec.x,y:spec.y}],seen=new Set([spec.x+','+spec.y]);
  for(let i=0;i<queue.length&&i<250;i++){const p=queue[i];if(!reserved.has(p.x+','+p.y))candidates.push(p);for(const [dx,dy]of [[1,0],[-1,0],[0,1],[0,-1]]){const n={x:p.x+dx,y:p.y+dy},k=n.x+','+n.y;if(!seen.has(k)&&monsterWalkable(c.map,n.x,n.y)){seen.add(k);queue.push(n);}}}
  // Candidates may be farther than one cell; use their own origin for the
  // generic occupancy check, retaining a reachable, walkable source region.
  const point=candidates.find(p=>emptySpawnCell(c,p,[p]));if(!point)return null;
  reserved.add(point.x+','+point.y);plans.push({spec,point});
 }return plans;
}
export function updateDefense(c,dt){
 const d=c.defense,r=c.content.defense;if(!d||d.status!=='active'||c.player.hp<=0)return;
 if(livingFlags(c).length<r.minimumFlags){d.status='failed';d.waiting=true;c.stopFarming();for(const u of c.units)clearMonsterAggro(u);c.defenseNotice='战旗损失过半，防守失败！';return;}
 if(d.waiting){if(d.clock>=r.endClock&&!defenseEnemies(c).length){d.status='complete';c.defenseNotice='魔物潮汐已结束，清理战场后返回吧';}return;}
 d.remainder+=dt;
 while(d.remainder>=1-1e-8&&!d.waiting){
  d.remainder=Math.max(0,d.remainder-1);d.clock++;
  const e=r.events[d.cursor];if(!e||e.time>d.clock)continue;
  const plans=plannedSpawns(c,e);if(!plans){d.clock=e.time-1;d.remainder=0;break;}
  for(const {spec,point}of plans)spawnUnit(c,c.monsterNames.get(spec.name),point,{siege:true});
  d.cursor++;d.clock=e.nextTime;d.waiting=e.waitForClear;
  if(e.messages.length){d.wave++;c.defenseNotice=e.messages.join('\n');}
 }
}
export function saveDefense(c){
 if(!c.defense)return null;
 const state={...c.defense,flags:c.units.filter(u=>u.defenseFlag).map(u=>({id:u.id,hp:u.alive?u.hp:0,alive:u.alive,statuses:validStatuses(u.statuses),regenClock:u.regenClock||0})),units:c.units.filter(u=>u.alive&&(u.siege||u.mercenary)).map(u=>({id:u.id,name:u.definition.name,x:u.x,y:u.y,hp:u.hp,mercenary:!!u.mercenary,petLevel:u.petLevel||1,petKills:u.petKills||0,statuses:validStatuses(u.statuses),regenClock:u.regenClock||0,bossFrames:u.bossFrames||0,speedBoosted:!!u.speedBoosted,attackSpeedBoosted:!!u.attackSpeedBoosted,stats:u.mercenary?Object.fromEntries(['hp','attack','defense','magicDefense','regenFrames'].map(k=>[k,u.definition[k]])):undefined}))};
 return state;
}
function restoreDefense(c,s){
 const r=c.content.defense,ints={clock:[5,2199],wave:[0,21],cursor:[0,r.events.length],hpUp:[0,5],dfUp:[0,6],dmUp:[0,6]};
 if(s?.version!==1||s.map!==c.map.id||!['active','failed','complete'].includes(s.status)||typeof s.waiting!=='boolean'||!Number.isFinite(s.remainder)||s.remainder<0||s.remainder>=1||Object.entries(ints).some(([k,[lo,hi]])=>!Number.isInteger(s[k])||s[k]<lo||s[k]>hi))return false;
 const flags=c.units.filter(u=>u.defenseFlag),allowedMercs=new Set(['稻草人','红野猪','钉耙猫','红刺蛙','天狼蜘蛛','石怪','骷髅射手','巨血魔']),allowedSiege=new Set(r.events.slice(0,s.cursor).flatMap(e=>e.spawns.map(u=>u.name)));
 if(!Array.isArray(s.flags)||s.flags.length!==flags.length||s.flags.some(f=>!f)||new Set(s.flags.map(f=>f.id)).size!==flags.length||!Array.isArray(s.units)||s.units.length>592||s.units.some(u=>!u)||c.units.length+s.units.length>600||s.units.filter(u=>u.mercenary).length>13)return false;
 if(s.units.some(u=>!/^J30:spawn:\d+$/.test(u.id)||!Number.isSafeInteger(Number(u.id.split(':').at(-1))))||new Set(s.units.map(u=>u.id)).size!==s.units.length)return false;
 const last=r.events[s.cursor-1],next=r.events[s.cursor];
 if(s.clock<(last?.nextTime||r.initialClock)||next&&s.clock>=next.time||s.wave!==r.events.slice(0,s.cursor).filter(e=>e.messages.length).length||s.waiting&&last&&!last.waitForClear||s.status==='complete'&&(s.cursor!==r.events.length||s.units.some(u=>!u.mercenary)))return false;
 const flagMax=c.monsterNames.get('战旗').hp+s.hpUp*300;
 if(s.flags.some(f=>!flags.some(u=>u.id===f.id)||!Number.isFinite(f.hp)||f.hp<0||f.hp>flagMax||typeof f.alive!=='boolean'||f.alive!==(f.hp>0)))return false;
 if(s.units.some(u=>!u||!Number.isFinite(u.x)||!Number.isFinite(u.y)||!monsterWalkable(c.map,Math.round(u.x),Math.round(u.y))||!Number.isFinite(u.hp)||u.hp<=0||!c.monsterNames.has(u.name)||!(u.mercenary?allowedMercs:allowedSiege).has(u.name)||u.mercenary&&(!Number.isInteger(u.petLevel)||u.petLevel<6||u.petLevel>10||!Number.isInteger(u.petKills)||u.petKills<0||u.petKills>275||['hp','attack','defense','magicDefense','regenFrames'].some(k=>!Number.isSafeInteger(u.stats?.[k])||u.stats[k]<0||u.stats[k]>10000000))||u.hp>(u.mercenary?u.stats.hp:difficultyMonster(c.monsterNames.get(u.name),c.player).hp)))return false;
 Object.assign(c.defense,Object.fromEntries(Object.keys(c.defense).map(k=>[k,s[k]])));
 const regen=value=>Number.isFinite(value)&&value>=0&&value<1000?value:0;
 for(const u of flags){const f=s.flags.find(f=>f.id===u.id);u.definition={...u.definition,hp:flagMax,defense:u.definition.defense+s.dfUp*5,magicDefense:u.definition.magicDefense+s.dmUp*5};Object.assign(u,{hp:f.hp,alive:f.alive,statuses:validStatuses(f.statuses),regenClock:regen(f.regenClock)});if(!f.alive){u.diedAt=c.elapsed-2;u.respawnAt=Infinity;u.refined=true;}}
 c.nextSpawnId=Math.max(c.nextSpawnId,...s.units.map(u=>Number(u.id.split(':').at(-1))));
 const ids=new Map();
 for(const u of s.units){const base=c.monsterNames.get(u.name),definition=u.mercenary?{...base,...u.stats}:base;const created=spawnUnit(c,definition,{x:u.x,y:u.y},u.mercenary?{summoned:true,mercenary:true,summonSkill:'江湖召唤',petLevel:u.petLevel,petKills:u.petKills}:{siege:true});ids.set(u.id,created.id);created.hp=u.hp;created.statuses=validStatuses(u.statuses);created.regenClock=regen(u.regenClock);created.bossFrames=Number.isSafeInteger(u.bossFrames)&&u.bossFrames>=0&&u.bossFrames<1e9?u.bossFrames:0;created.speedBoosted=!!u.speedBoosted;created.attackSpeedBoosted=!!u.attackSpeedBoosted;}
 for(const u of c.units)for(const status of Object.values(u.statuses||{}))if(ids.has(status.source))status.source=ids.get(status.source);
 return true;
}
