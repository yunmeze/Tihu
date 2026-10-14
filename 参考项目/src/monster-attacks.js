import {launchProjectile,launchDirectedProjectile,addVisual,MONSTER_EFFECTS} from './projectiles.js';
import {addZone,firewall} from './combat-effects.js';
import {nativeRound,sampleMonsterRandom} from './monster-motion.js';

export function monsterStrike(combat,unit,target){
 if(!unit.alive||combat.player.hp<=0)return;
 const kind=unit.definition.attackKind,point=target||{...combat.position,id:'player',hp:combat.player.hp};
 if([8,9,10].includes(kind)||kind<0||kind>28)return;combat.audio?.monster(unit,2);
 const hit=(t,magic=false)=>combat.enemyHit(unit,t.id==='player'?null:combat.units.find(u=>u.id===t.id),{magic});
 const impact=type=>t=>{
  const victims=[47,49].includes(type)?(unit.summoned?combat.units.filter(u=>u.alive&&!u.summoned):[{...combat.position,id:'player',hp:combat.player.hp},...combat.units.filter(u=>u.alive&&u.summoned)]).filter(u=>Math.abs(Math.round(u.x)-Math.round(t.x))+Math.abs(Math.round(u.y)-Math.round(t.y))<=1):[t];
  for(const victim of victims)hit(victim,[46,47,48,49].includes(type));
 };
 const flight=(type,from=unit,to=point)=>launchProjectile(combat,{from,to,type,source:unit.id,onHit:impact(type)});
 // Projectiles store the foot-space coordinate of the renderer's +24/-20
 // pivot. Convert the original screen-space muzzle locations exactly once.
 const muzzle=(x,y)=>({x:unit.x+(x-24)/48,y:unit.y+(y+20)/32});
 const burst=(type,angle,speed)=>launchDirectedProjectile(combat,{from:muzzle(0,-32),type,source:unit.id,angle,speed,onHit:impact(type)});
 if(kind<=7){hit(point);const type=MONSTER_EFFECTS[kind];if(type)addVisual(combat,type,point,{direction:unit.direction});return;}
 if(kind<=19){flight(MONSTER_EFFECTS[kind]);return;}
 if(kind===20){addVisual(combat,20,point,{duration:1.2});for(const t of [{...combat.position,id:'player',hp:combat.player.hp},...combat.units.filter(u=>u.alive&&u.summoned)])if(Math.max(Math.abs(Math.round(t.x)-Math.round(point.x)),Math.abs(Math.round(t.y)-Math.round(point.y)))<=1)hit(t,true);return;}
 if(kind===21||kind===22){flight(nativeRound(sampleMonsterRandom(combat.battleRandom)*100)<50?(kind===21?46:47):(kind===21?48:49));return;}
 if(kind===23){for(const x of [-26,74])flight(48,muzzle(x,-62));return;}
 if(kind===24){flight(47,muzzle(24,-32));for(const x of [-26,74])flight(46,muzzle(x,-72));return;}
 if(kind===25){addZone(combat,{point,type:37,frames:60,source:unit.id,hitFrame:36,hit:t=>hit(t)});return;}
 if(kind===26){
  // 5cbd98: five angles (-3,0,+3,-30,+30), speeds 5.6/6.5/5.6/5/5.
  // Aim uses monster (x*48-20,y*32-37), player (x*48+24,y*32-16).
  const angle=-Math.atan2((point.x-unit.x)*48+44,-((point.y-unit.y)*32+21))*180/Math.PI;
  for(const [offset,speed]of [[-3,5.6],[0,6.5],[3,5.6],[-30,5],[30,5]])burst(38,angle+offset,speed);return;
 }
 if(kind===27){
  // 5cbfce: twin explosive fire before 500 actor ticks, then twelve evenly
  // spaced 5-pixel/tick shots from the monster, resetting its +3a timer.
  if((unit.bossFrames||0)<500){for(const x of [-26,74])flight(47,muzzle(x,-62));return;}
  unit.bossFrames=0;for(let angle=0;angle<360;angle+=30)burst(39,angle,5);return;
 }
 // 5cc2e4: a fresh 50% branch chooses twin fire/ice or one stationary hazard.
 // At 500 actor ticks, lay three cells with separate 25% orientation rolls.
 if((unit.bossFrames||0)<500){if(sampleMonsterRandom(combat.battleRandom)<.5){flight(47,muzzle(-26,-62));flight(49,muzzle(74,-62));}else firewall(combat,point,1,{source:unit.id,type:40,frames:4000});return;}
 unit.bossFrames=0;let offsets;if(sampleMonsterRandom(combat.battleRandom)<.25)offsets=[[0,0],[-1,0],[1,0]];else if(sampleMonsterRandom(combat.battleRandom)<.25)offsets=[[0,0],[0,-1],[0,1]];else if(sampleMonsterRandom(combat.battleRandom)<.25)offsets=[[0,0],[-1,-1],[1,1]];else offsets=[[0,0],[-1,1],[1,-1]];
 for(const [dx,dy]of offsets)firewall(combat,{x:Math.round(point.x)+dx,y:Math.round(point.y)+dy},1,{source:unit.id,type:40,frames:4000});
}
