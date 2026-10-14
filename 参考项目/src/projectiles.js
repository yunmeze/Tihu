import {MAP_FLAG} from './map-flags.js';
import {emitNativeParticle} from './native-particles.js';

// Native effect IDs -> original Mgc resources, read from the effect renderer.
export const EFFECT_PACKS={1:'1-1',2:'2-1',3:'3-1',4:'4',5:'5',6:'18',7:'20',8:'21',9:'28',10:'23',11:'24',12:'25',13:'26',14:'6',15:'8',16:'10',17:'12',18:'14',19:'15',20:'16',21:'17',22:'30',23:'0',24:'7',25:'9',26:'11',27:'13',28:'19',30:'31',31:'32',32:'33',33:'34',34:'35',36:'36',37:'37',38:'38',39:'38',40:'40',41:'51',42:'52',43:'53',44:'54',45:'55',46:'6',47:'8',48:'10',49:'12',56:'56',72:'71',80:'80',90:'90',91:'29'};
export const MONSTER_EFFECTS={1:30,2:31,3:32,4:33,6:31,7:36,11:41,12:42,13:43,14:44,15:45,16:46,17:47,18:48,19:49,20:20};
export const EFFECT_VARIANTS={lightningWide:'14-2'};
export const effectPack=(type,variant)=>EFFECT_PACKS[type]&&'Mgc/'+(EFFECT_VARIANTS[variant]||EFFECT_PACKS[type]);
export const impactType=type=>({6:28,14:24,15:25,16:26,17:27,46:24,47:25,48:26,49:27})[type]||type;
export function addVisual(combat,type,point,{duration=.48,direction=4,loop=false,owner=null,follow=null,variant=null,clipFrames,hitAt,onHit,onComplete}={}){
 if(type===73||type===74)return emitNativeParticle(combat,type===73?3:8,point);
 if(!effectPack(type))return;combat.audio?.effect(type,point);
 const effect={id:++combat.nextEffectId,type,x:point.x,y:point.y,direction,age:0,duration,loop,owner,follow,variant,clipFrames,hitAt,onHit,onComplete,animationVersion:owner?.animationVersion};combat.effects.push(effect);combat.effectVersion++;return effect;
}
export function launchProjectile(combat,{from,to,type=6,source='player',onHit,area=false,velocity,duration=4,maxTravel}){
 combat.audio?.effect(type,from);
 const dx=(to.x-from.x)*48,dy=(to.y-from.y)*32,distance=Math.hypot(dx,dy);
 if(!velocity&&distance<1e-6){onHit(to);addVisual(combat,impactType(type),to);return;}
 // 7 source pixels per native tick. Web collision uses short swept segments;
 // heading is captured when released, allowing the victim to move away.
 const p={id:++combat.nextEffectId,type,x:from.x,y:from.y,vx:velocity?.vx??dx/distance*350/48,vy:velocity?.vy??dy/distance*350/32,direction:combat.direction(from,to),age:0,duration,loop:true,source,onHit,area,travel:0,maxTravel:maxTravel??distance+64};
 combat.projectiles.push(p);combat.effectVersion++;
 if(type===44)p.spin=0;
 return p;
}
// Native 38/39 initializer receives an angle and source pixels per 50-Hz tick.
// Angles increase counterclockwise from up. Keep velocity in projected pixels,
// not a normalized 48x32 grid diagonal; radial shots do not retarget the player.
export function launchDirectedProjectile(combat,{from,angle,speed,...options}){
 const radians=angle*Math.PI/180,vx=-Math.sin(radians)*speed*50/48,vy=-Math.cos(radians)*speed*50/32;
 return launchProjectile(combat,{...options,from,to:{x:from.x+vx,y:from.y+vy},velocity:{vx,vy},maxTravel:speed*50*(options.duration||4)});
}
const blocked=(map,x,y)=>{const c=x>=0&&y>=0&&x<map.width&&y<map.height&&map.cells[x*map.height+y];return !c||[MAP_FLAG.GROUND_BLOCKED,MAP_FLAG.MIDDLE_BLOCKED].includes(c[1]);};
export function updateProjectiles(combat,dt){
 for(const e of [...combat.effects]){e.age+=dt;const follow=e.owner||e.follow;if(follow){e.x=follow.x;e.y=follow.y;if(e.owner)e.direction=follow.direction;}if(!e.hit&&e.hitAt!==undefined&&e.age+1e-8>=e.hitAt){e.hit=true;if(combat.player.hp>0)e.onHit?.(e);}if(!e.finished&&e.age+1e-8>=e.duration){e.finished=true;if(combat.player.hp>0)e.onComplete?.(e);}}
 combat.effects=combat.effects.filter(e=>e.owner?e.owner.animationVersion===e.animationVersion&&e.owner.actionTime>0:!e.finished);
 for(const p of combat.projectiles){
  if(p.type===44){p.spinRemainder=(p.spinRemainder||0)+dt*50;for(let ticks=Math.floor(p.spinRemainder+1e-8);ticks>0;ticks--){p.spinRemainder--;p.spin=combat.battleRandom()*Math.PI*2;}}
  p.age+=dt;
  const source=p.source==='player'?combat.player:combat.units.find(u=>u.id===p.source);
  if(!source||source.hp<=0){p.dead=true;continue;}
  const speed=Math.hypot(p.vx*48,p.vy*32),steps=Math.max(1,Math.ceil(dt*speed/8));
  const friendly=p.source==='player'||source.summoned;
  const candidates=friendly?combat.units.filter(u=>u.alive&&!u.summoned):[{...combat.position,id:'player',hp:combat.player.hp},...combat.units.filter(u=>u.alive&&u.summoned)];
  for(let i=0;i<steps&&!p.dead;i++){
   const old={x:Math.round(p.x),y:Math.round(p.y)};p.x+=p.vx*dt/steps;p.y+=p.vy*dt/steps;p.travel+=speed*dt/steps;
   const x=Math.round(p.x),y=Math.round(p.y);
   if(blocked(combat.map,x,y)||x!==old.x&&y!==old.y&&(blocked(combat.map,x,old.y)||blocked(combat.map,old.x,y))){p.dead=true;break;}
   const target=candidates.find(u=>u.hp>0&&Math.hypot((u.x-p.x)*48,(u.y-p.y)*32)<16);
   if(target){p.dead=true;p.onHit(target);addVisual(combat,impactType(p.type),p,{direction:p.direction});}
   if(p.travel>p.maxTravel||p.age>=p.duration)p.dead=true;
  }
 }
 combat.projectiles=combat.projectiles.filter(p=>!p.dead);
}
