import {ANIMATIONS,setAction} from './animation.js';

export const isMoving=actor=>actor&&['walk','run'].includes(actor.action);
// Portrait controls choose pace from the legal route, including detours.
// Hysteresis avoids changing clips repeatedly when the destination is adjusted.
export const AUTO_PACE={runAt:4,walkAt:2};
export function remainingPathDistance(combat){
 let previous=combat.position,total=0;
 for(const point of combat.path){total+=Math.max(Math.abs(point.x-previous.x),Math.abs(point.y-previous.y));previous=point;}
 return total;
}
export function chooseMovementMode(combat){
 if(!combat.manualPath)return 'walk';
 if(combat.movePolicy==='walk'||combat.movePolicy==='run')return combat.movePolicy;
 const distance=remainingPathDistance(combat);
 return distance>=(isMoving(combat.position)&&combat.moveMode==='run'?AUTO_PACE.walkAt+1e-9:AUTO_PACE.runAt)?'run':'walk';
}
export function advanceMovement(combat,seconds,rules){
 let total=0;
 while(seconds>1e-10&&combat.path.length){
  const mode=chooseMovementMode(combat),speed=mode==='run'?rules.runTilesPerSecond:rules.walkTilesPerSecond;
  combat.moveMode=mode;setMovementAction(combat.position,mode);
  // Split exactly at the run/walk boundary, even when a frame crosses it.
  const duration=mode==='run'&&combat.movePolicy==='auto'?Math.min(seconds,Math.max(0,(remainingPathDistance(combat)-AUTO_PACE.walkAt)/speed)):seconds;
  if(duration<=1e-10){combat.moveMode='walk';setMovementAction(combat.position,'walk');continue;}
  total+=advanceHeroPath(combat,duration,speed);seconds-=duration;
 }
 return total;
}
export function setMovementAction(actor,action){
 if(actor.action===action)return;
 const phase=isMoving(actor)?((actor.animationElapsed||0)/ANIMATIONS.hero[actor.action].seconds)%1:0;
 setAction(actor,action);actor.animationElapsed=phase*ANIMATIONS.hero[action].seconds;
}

// Native 622e50 applies a full step to each active grid axis. Source pixels
// use 48x32 cells: horizontal = 1.5 * vertical, with no diagonal normalization.
// Consume the complete frame budget so reaching a waypoint cannot slow travel
// differently at 30/60/120 Hz. Every crossed point still processes pickup.
export function advanceHeroPath(combat,seconds,speed){
 let budget=seconds*speed,total=0,iterations=0;
 while(combat.path.length&&budget>1e-10&&iterations++<1000){
  const goal=combat.path[0],p=combat.position,dx=goal.x-p.x,dy=goal.y-p.y,distance=Math.max(Math.abs(dx),Math.abs(dy));
  if(distance<1e-10){p.x=goal.x;p.y=goal.y;combat.path.shift();combat.pickupAtFeet();continue;}
  const step=Math.min(distance,budget);p.direction=combat.direction(p,goal);p.x+=dx/distance*step;p.y+=dy/distance*step;total+=Math.hypot(dx,dy)/distance*step;budget-=step;
  if(step>=distance-1e-10){p.x=goal.x;p.y=goal.y;combat.path.shift();}
  combat.pickupAtFeet();
 }
 return total;
}
