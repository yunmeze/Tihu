export async function runningScenario({native=false}={}){
 const a=native?nativeTest.gameGlobal.lpLegend:lpLegend;a.platform.cancel(a.frame);for(const k of ['systemMenu','serviceView','npcDialogue','mapOpen','attributeOpen','gmOpen','message'])a[k]=null;
 if(a.mapId!=='A00')await a.changeMap('A00',null,{unlock:true});const c=a.combat;c.enter(a.map,{x:86,y:52});
 const fixture=c.units.filter(u=>u.definition.id===4&&u.x>8&&u.y>4&&Array.from({length:8},(_,i)=>u.x-i).every(x=>Array.from({length:6},(_,j)=>u.y-4+j).every(y=>c.walkable(x,y)))).at(-1);if(!fixture)throw Error('No open native running fixture');
 const start={x:fixture.x-7,y:fixture.y-2};c.units=a.units=[];Object.assign(c.position,start);a.hero=c.position;a.camera={x:start.x+2,y:start.y};a.tab='战斗';a.player.hp=a.player.base.hp;a.player.belt=Array(6).fill(null);await a.prepareVisible();a.render();
 const pixelFor=x=>{const p=a.screenPoint(x,start.y);return {clientX:a.left+p.x*a.scale,clientY:a.top+p.y*a.scale};},nearPixel=pixelFor(start.x+2),farPixel=pixelFor(start.x+6);
 const touch=async(point,time)=>{if(native){nativeTest.handlers.get('TouchStart')({touches:[point],timeStamp:time-20});nativeTest.handlers.get('TouchEnd')({changedTouches:[point],timeStamp:time});await new Promise(r=>setTimeout(r,0));}else await a.pointer(point.clientX,point.clientY,{button:0,pointerType:'touch',time});};
 const step=n=>{for(let i=0;i<n;i++)c.update(.02);a.hero=c.position;};
 await touch(nearPixel,1000);step(10);if(c.position.action!=='walk'||Math.abs(c.position.x-start.x-.3125)>1e-7)throw Error('Near click walk speed failed');
 const walkPhase=c.position.animationElapsed/.84%1;await touch(farPixel,2000);if(c.moveMode!=='run'||Math.abs(c.position.animationElapsed/.6-walkPhase)>1e-7)throw Error('Far click pace/phase failed');const before=c.position.x;step(15);if(Math.abs(c.position.x-before-.9375)>1e-7)throw Error('Native run displacement failed');
 const version=c.position.animationVersion,elapsed=c.position.animationElapsed;await touch(farPixel,2100);if(c.position.animationVersion!==version||c.position.animationElapsed!==elapsed)throw Error('Repeated click restarted run');const runFrame=a.animationFrame(c.position);if(runFrame<81||runFrame>128)throw Error('Wrong native run frame');
 step(50);if(c.moveMode!=='walk')throw Error('Route did not slow before destination');a.render();
 return {nativeTouch:native,nearClickWalk:true,farClickRun:true,automaticSlowdown:true,walkTilesPerSecond:1.5625,runTilesPerSecond:3.125,runFrame,normalizedPhasePreserved:true,repointingPreserved:true,start,nearPixel,farPixel};
}
