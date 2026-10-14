// Frame groups checked against the original Hero/Weapon and Mon sprite strips.
// Native hero frame steps: idle 12, walk 7, run 5, attack/cast 8 ticks at 50 Hz.
export const ANIMATIONS={
 hero:{idle:{base:1,count:4,seconds:.96,loop:true},walk:{base:33,count:6,seconds:.84,loop:true},run:{base:81,count:6,seconds:.6,loop:true},attack:{base:129,count:6,seconds:.96,releasePhase:4},cast:{base:177,count:6,seconds:.96,releasePhase:5},hurt:{base:225,count:3,seconds:.4,leadSeconds:.1},death:{base:249,count:4,seconds:1}},
 monster:{idle:{base:1,count:4,seconds:.96,loop:true},walk:{base:33,count:6,seconds:.48,loop:true},attack:{base:81,count:6,seconds:.48},death:{base:129,count:10,seconds:1.2}},
};
export function setAction(actor,action,{restart=false,family='hero'}={}){
 if(actor.action===action&&!restart)return;
 // Native 61f250 resets the action clock without replacing the drawn frame;
 // 61e3a5 first draws hurt phase 0 at tick 5 and returns to idle at tick 20.
 if(family==='hero'&&action==='hurt')actor.hurtStartFrame=animationFrame(actor,family);
 else if(actor.hurtStartFrame!==undefined)delete actor.hurtStartFrame;
 actor.action=action;actor.animationVersion=(actor.animationVersion||0)+1;actor.animationElapsed=0;actor.animationDuration=null;
 actor.actionTime=ANIMATIONS[family][action]?.loop?0:ANIMATIONS[family][action]?.seconds||0;
}
// Sprite contact uses the same clock as the numeric action period.
export function releaseTime(actor,family='hero'){
 const clip=ANIMATIONS[family][actor.action];return (actor.animationDuration||clip.seconds)*(clip.releasePhase??5)/clip.count;
}
export function advanceAnimation(actor,dt,family='hero'){
 actor.animationElapsed=(actor.animationElapsed||0)+dt;
 if(actor.actionTime>0){actor.actionTime=Math.max(0,actor.actionTime-dt);if(actor.actionTime<1e-8&&actor.action!=='death')setAction(actor,'idle',{family});}
}
export function animationFrame(actor,family='hero'){
 const clip=ANIMATIONS[family][actor.action]||ANIMATIONS[family].idle,t=Math.max(0,actor.animationElapsed||0);
 if(clip.leadSeconds&&t+1e-8<clip.leadSeconds&&Number.isInteger(actor.hurtStartFrame))return actor.hurtStartFrame;
 if(family==='monster'&&actor.action==='death'&&t>=clip.seconds)return 209+((actor.direction||0)%8);
 const seconds=actor.animationDuration||clip.seconds,lead=clip.leadSeconds||0,time=lead?Math.max(0,t-lead)+1e-8:t,phase=clip.loop?Math.floor(t/seconds*clip.count)%clip.count:Math.min(clip.count-1,Math.floor(time/(seconds-lead)*clip.count));
 return clip.base+((actor.direction||0)%8)*clip.count+phase;
}
// Keep the logical corpse for refining and respawn, but stop drawing it once
// the death animation has finished.
export function monsterModelVisible(actor){return !actor.removed&&(actor.alive||!actor.refined&&actor.action==='death'&&(actor.animationElapsed||0)<ANIMATIONS.monster.death.seconds-1e-8);}
const MELEE=new Set(['基本剑术','剑气斩','火龙斩','半月斩','烈火斩','冰封斩','自然之力']);
export function skillAction(player,content){
 const name=player.activeSkill,learned=player.skills.some(s=>s.name===name&&s.level>0),record=content.skills.records.find(s=>s.name===name);
 if(!learned||!record||player.mp<(record.mpCost||0))return {action:'attack',name:'基本剑术',mpCost:0};
 return {action:MELEE.has(name)?'attack':'cast',name,mpCost:record.mpCost||0};
}
