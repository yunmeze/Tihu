const inside=(p,b)=>p.x>=b.x&&p.y>=b.y&&p.x<=b.x+b.w&&p.y<=b.y+b.h;
const blocked=a=>a.screen!=='game'||a.hidden||a.disposed||a.player?.hp<=0||a.combat?.scriptLocked||a.combat?.story||['itemBusy','changing','entering','reviving','resetting','growthBusy','gmBusy','npcBusy','serviceBusy','systemMenu','featureView','mapOpen','attributeOpen','npcDialogue','serviceView','gmOpen'].some(k=>a[k]);
export function worldPointer(a,x,y){const p=a.toLogical(x,y);return p.x>=0&&p.x<=750&&p.y>=0&&p.y<=(a.tab==='战斗'?1535:1040)&&!a.buttons.some(b=>inside(p,b))&&!a.worldText?.groundHits?.some(b=>inside(p,b))?p:null;}
export function rememberPointer(a,x,y){const p=worldPointer(a,x,y);if(p)a.lastWorldPointer=p;}
export function cancelContinuous(a){const active=a.autoRun||a.heldMove;a.autoRun=false;a.heldMove=null;if(active&&a.combat?.manualPath)a.combat.stopFarming();}
export function holdPointer(a,phase,x,y,input={}){
 if(phase==='cancel'){const active=!!a.heldUsed;cancelContinuous(a);a.heldUsed=false;return active;}
 if(phase==='up'){const active=!!(a.heldUsed||a.heldMove&&input.dragged);if(active)cancelContinuous(a);else a.heldMove=null;a.heldUsed=false;return active;}
 if(phase==='move'){if(a.heldMove){a.heldMove.point=worldPointer(a,x,y);if(a.heldMove.point)a.lastWorldPointer=a.heldMove.point;}return false;}
 a.heldUsed=false;if(input.pointerType==='mouse'&&!blocked(a)){const point=worldPointer(a,x,y);if(point){a.questTravel=null;cancelContinuous(a);a.lastWorldPointer=point;a.heldMove={point,started:a.elapsed,active:false};a.nextContinuous=0;a.continuousTarget=null;}}
 return false;
}
export function toggleAutoRun(a){if(blocked(a))return false;a.questTravel=null;if(a.autoRun){cancelContinuous(a);return false;}a.heldMove=null;a.autoRun=true;a.nextContinuous=0;a.continuousTarget=null;return true;}
export function updateContinuousMovement(a){
 if(blocked(a)){cancelContinuous(a);return;}
 const held=a.heldMove;if(held&&!held.active&&a.elapsed-held.started>=.18){held.active=true;a.heldUsed=true;a.continuousTarget=null;a.nextContinuous=0;}
 if(!a.autoRun&&!held)return;a.questTravel=null;if(a.elapsed<(a.nextContinuous||0))return;a.nextContinuous=a.elapsed+.12;
 const p=held?held.point:a.lastWorldPointer,c=a.combat;
 if(!p){if(held){a.continuousTarget=null;if(c.manualPath)c.stopFarming();return;}const [dx,dy]=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]][c.position.direction||0];a.lastWorldPointer={x:375+dx*192,y:555+dy*128};return;}
 const x=Math.round(a.camera.x+(p.x-375)/(48*a.worldScale)),y=Math.round(a.camera.y+(p.y-555)/(32*a.worldScale)),key=x+','+y+','+(c.scriptRevision||0);
 if(key===a.continuousTarget)return;a.continuousTarget=key;a.pendingNpc=null;c.moveTo(x,y);
}
