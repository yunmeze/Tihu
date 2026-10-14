// Explicit original sheet groups, rather than inferring directions from the
// number of frames (the 16-frame shield is not an eight-direction sheet).
export const EFFECT_DIRECTIONS={1:6,2:6,3:6,4:17,5:17,30:6,31:6,32:7,33:6,34:8,36:6};
// Native single-strip flights pass effect +0x18 to the rotated sprite draw.
// Eight-direction sword/monster sheets already encode their orientation.
export const ROTATED_PROJECTILE_TYPES=[6,14,15,16,17,38,39,41,42,43,45,46,47,48,49];
export function effectRotation(effect){
 if(effect.type===44&&Number.isFinite(effect.spin))return effect.spin;
 if(!ROTATED_PROJECTILE_TYPES.includes(effect.type)||!Number.isFinite(effect.vx)||!Number.isFinite(effect.vy))return null;
 const dx=effect.vx*48,dy=effect.vy*32;
 // Original flight sheets face up. Rotate in screen space, where a grid
 // diagonal projects to 48:32 rather than a 45-degree sprite rotation.
 return Math.hypot(dx,dy)>1e-6?Math.atan2(dx,-dy):null;
}
export function effectFrame(effect,pack){
 const available=pack.frames.length-1,count=effect.clipFrames||EFFECT_DIRECTIONS[effect.type]||available;
 if(count<=0)return null;
 if(effect.shield){
  if(effect.shieldFrame!==undefined)return effect.shieldFrame;
  // Native 5c2b4e: five ticks per frame; 1..10 unfold, 11..13 hold,
  // 13..16 react to a hit, then return to the holding loop.
  const pulse=effect.shieldHitAt===undefined?Infinity:effect.age-effect.shieldHitAt;
  if(pulse<.4)return Math.min(16,13+Math.floor((pulse+1e-8)/.1));
  return effect.age<1?Math.min(10,1+Math.floor((effect.age+1e-8)/.1)):11+Math.floor((effect.age-1+1e-8)/.1)%3;
 }
 const time=effect.owner?effect.owner.animationElapsed:effect.age;
 const duration=effect.owner?(effect.owner.animationDuration||effect.duration):effect.duration;
 const phase=effect.loop?Math.floor((time+1e-8)/(effect.frameSeconds||.08))%count:Math.min(count-1,Math.floor((Math.max(0,time)+1e-8)/duration*count));
 return 1+(EFFECT_DIRECTIONS[effect.type]?((effect.direction||0)%8)*count:0)+phase;
}
