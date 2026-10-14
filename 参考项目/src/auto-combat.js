import {autoSkillAllowed} from './auto-skill-config.js';
import {explicitSkill,attackRange,corpseTarget} from './combat-skills.js';
import {SUMMON_SKILLS} from './skill-roles.js';
import {followingPet} from './allies.js';
import {attributes} from './character.js';
import {emptySpawnCell} from './monster-spawning.js';
import {skillLevel,spellPower} from './native-damage.js';
const BASIC={name:'基本剑术',action:'attack',mpCost:0},UTILITY=new Set(['回生术','治愈术','隐身术','魔法盾','炼尸咒',...SUMMON_SKILLS]);
const distance=(a,b)=>Math.max(Math.abs(a.x-b.x),Math.abs(a.y-b.y));
function enabledSkills(c){return (c.player.autoSkills||[]).filter(e=>e.enabled&&autoSkillAllowed(c.player,c.content,e.name)).map(e=>explicitSkill(c,e.name)).filter(Boolean);}
const affected=(c,u)=>u.alive&&!u.summoned&&!u.removed&&c.lineOfSight(c.position,u);
// Estimate with the same learned levels, equipment and native spell formulas.
// This selects an action; it never consumes a damage RNG roll or changes power.
export function expectedAttackDamage(c,s,t){
 const stats=attributes(c.player,c.content),mean=k=>(stats[k][0]+stats[k][1])/2+(stats.setBonus||0),l=skillLevel(c.player,s.name),m=mean('magic'),a=mean('attack');let power=spellPower(s.name,l,m),repeats=1;
 if(power===null){power=({'灵魂火符':mean('tao')*.9+3*(l-1),'雷电术':m+5*l+3,'冰咆哮':m+5*l+(c.player.class==='道士'?mean('tao')/4:0),'地狱雷光':m/2.5+6*l+(c.player.class==='道士'?mean('tao')/4:0),'烈火斩':stats.attack[1]+a*l*.1,'冰封斩':a+a*.1*l+l,'半月斩':a+a*(l-1)*.1+l})[s.name]??a;}
 const defense=s.action==='cast'?t.definition.magicDefense:t.definition.defense,hit=Math.max(1,power-(defense||0));
 // Lightning's L-1 native aftershocks also contribute to a surviving target.
 if(s.name==='雷电术')repeats+=(Math.max(0,l-1)*Math.max(1,m/10+2*l-(defense||0)))/hit;
 return hit*repeats;
}
function offenseScore(c,s,t){
 const name=s.name,d=distance(c.position,t);if(UTILITY.has(name))return null;
 if(name==='施毒术'||name==='侵蚀术')return t.statuses?.[name==='施毒术'?'poison':'corrosion']?.frames>0?null:700;
 if(name==='火墙')return c.zones.some(z=>z.source==='player'&&z.type===19&&z.frames>0&&Math.round(z.x)===Math.round(t.x)&&Math.round(z.y)===Math.round(t.y))?null:600;
 if(name==='诱惑之光')return t.definition.attackKind===0&&t.definition.hp<60*skillLevel(c.player,name)&&c.elapsed>=(c.nextAutoTemptAt||0)?650:null;
 if(name==='地狱雷光')return c.units.filter(u=>distance(c.position,u)<=2&&affected(c,u)&&Math.abs(Math.round(u.x)-Math.round(c.position.x))+Math.abs(Math.round(u.y)-Math.round(c.position.y))<4).length>=2?550:10;
 const around=c.units.filter(u=>distance(u,t)<=1&&affected(c,u)).length,line=c.units.filter(u=>distance(c.position,u)<=6&&c.direction(c.position,u)===c.direction(c.position,t)&&affected(c,u)).length;
 const aoe=['冰咆哮','爆裂火球','强冰术','半月斩','冰封斩'].includes(name),base=aoe&&around>=2?500:name==='烈火斩'&&line>=2?500:100;
 const damage=Math.min(t.hp,expectedAttackDamage(c,s,t)),mpFraction=c.player.mp/Math.max(1,attributes(c.player,c.content).mp);
 // At low MP conserve resources. For a nearly defeated enemy, equal lethal
 // spells prefer the cheaper one; against a strong enemy prefer actual power.
 const efficiency=damage/(1+s.mpCost*(mpFraction<.25?.4:.015));
 return base+(d>1&&s.action==='cast'?250:d<=1&&s.action==='attack'?250:0)+(aoe&&around<2?-30:0)+100*efficiency/(efficiency+30)-s.mpCost*.2;
}
export function automaticAttackSkill(c,target){
 if(!target)return BASIC;let best=null;
 for(const skill of enabledSkills(c)){const score=offenseScore(c,skill,target);if(score===null)continue;const range=attackRange(c,skill),reachable=c.canAttackFrom(c.position,target,range,skill.name)&&c.lineOfSight(c.position,target),candidate={skill,range,reachable,score};
  if(!best||Number(reachable)>Number(best.reachable)||reachable===best.reachable&&(reachable?score>best.score:range>best.range||range===best.range&&score>best.score))best=candidate;
 }
 return best?.skill||BASIC;
}
export function automaticUtilitySkill(c){
 if(c.manualPath||c.autoLoot||c.lootingId)return null;
 const p=c.player,stats=attributes(p,c.content),friends=[...c.units,...(c.waitingPets||[])].filter(u=>u.alive&&followingPet(u)),hurt=p.hp<stats.hp*.65&&!p.healingPool,critical=p.hp<stats.hp*.35&&!p.healingPool,petHurt=c.units.some(u=>u.alive&&followingPet(u)&&u.hp<u.definition.hp*.65&&!u.healingPool&&distance(u,c.position)<=1),choices=[];
 for(const skill of enabledSkills(c)){
  const name=skill.name;let score=0,target=null;
  if(SUMMON_SKILLS.has(name)){
   const limit=name==='召唤骷髅'&&skillLevel(p,name)>=2?2:1,point={x:Math.round(c.position.x),y:Math.round(c.position.y)},offsets=[[-1,0],[1,0],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[1,1]];
   if(friends.length<3&&friends.filter(u=>u.summonSkill===name).length<limit&&c.monsterNames.has(name)&&c.units.filter(u=>u.alive||!u.temporary).length<600&&emptySpawnCell(c,point,offsets.map(([dx,dy])=>({x:point.x+dx,y:point.y+dy}))))score=9000;
  }else if(name==='回生术'&&hurt||name==='治愈术'&&(hurt||petHurt))score=critical?10000:7000;
  else if(name==='魔法盾'&&!p.magicShieldFrames)score=8500;
  else if(name==='隐身术'&&!p.invisible&&!c.target()&&!c.threats?.size)score=1000;
  else if(name==='炼尸咒'&&!c.target()){target=corpseTarget(c);if(target)score=6000;}
  if(score)choices.push({skill,target,score});
 }
 return choices.sort((a,b)=>b.score-a.score)[0]||null;
}
export function recordAutomaticCast(c,skill){if(skill.name==='诱惑之光')c.nextAutoTemptAt=c.elapsed+2;c.lastAutoCast={name:skill.name,at:c.elapsed};}
