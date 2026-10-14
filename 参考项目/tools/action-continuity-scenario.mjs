// Runs through canvas input in both browser and DOM-free WeChat smoke tests.
export async function actionContinuityScenario({native=false,width=375}={}){
 const a=native?nativeTest.gameGlobal.lpLegend:lpLegend;if(a.mapId!=='A00')await a.changeMap('A00',null,{unlock:true});a.platform.cancel(a.frame);
 const c=a.combat;c.enter(a.map,{x:86,y:52});const u=c.units.filter(u=>u.definition.id===4&&u.x>8&&u.y>4&&Array.from({length:8},(_,i)=>u.x-i).every(x=>Array.from({length:6},(_,i)=>u.y-4+i).every(y=>c.walkable(x,y)))).at(-1);if(!u)throw Error('No open native walk fixture');
 c.units=a.units=[u];u.hp=1000;u.definition={...u.definition,hp:1000,speed:0,behavior:-1,vision:0,defense:0,magicDefense:0,physicalEvade:0,magicEvade:0,regenFrames:0};Object.assign(a.player,{class:'战士',gender:0,headStyle:0,skills:[{name:'基本剑术',level:1}],activeSkill:'基本剑术',hp:1000,mp:1000});Object.assign(a.player.base,{hp:1000,mp:1000,accuracy:100,attack:[5,5]});c.battleRandom=c.monsterRandom=()=>.99;c.elapsed=c.hitCount=0;c.hitClock=.96;c.groundItems.splice(0);c.events=[];Object.assign(c.position,{x:u.x-7,y:u.y-2});a.hero=c.position;a.camera={x:u.x-4,y:u.y-2};a.tab='战斗';a.message=null;await a.updateAppearance();await a.prepareVisible();a.render();
 const input=async(x,y)=>{const p=a.screenPoint(x,y);await a.pointer(a.left+p.x*a.scale,a.top+p.y*a.scale);};
 const step=time=>{for(let i=0;i<Math.round(time/.02);i++)c.update(.02);a.hero=c.position;};
 await input(u.x-1,u.y-2);step(.2);const version=c.position.animationVersion,walk=[];
 for(let i=0;i<12;i++){
  const phase=c.position.animationElapsed;await input(u.x-1,u.y-2+(i%2)*.6);if(c.position.action!=='run'||c.position.animationVersion!==version||c.position.animationElapsed!==phase)throw Error('Scene re-click restarted running');step(.08);walk.push({time:c.elapsed,phase:c.position.animationElapsed,frame:(a.animationFrame(c.position)-81)%6,version:c.position.animationVersion});
 }
 if(new Set(walk.map(f=>f.frame)).size!==6)throw Error('Repeated-click run skipped frames');a.render();
 // Expose this state for browser screenshot capture before running combat.
 const runAttack=async skill=>{
  c.stopFarming();c.effects=[];c.projectiles=[];c.zones=[];c.events=[];c.elapsed=c.hitCount=0;c.hitClock=.96;u.hp=1000;Object.assign(c.position,{x:u.x-(skill==='基本剑术'?1:6),y:u.y});Object.assign(a.player,{class:skill==='基本剑术'?'战士':'法师',gender:skill==='基本剑术'?0:1,headStyle:skill==='基本剑术'?0:1,skills:[{name:skill,level:1}],activeSkill:skill,autoSkills:skill==='基本剑术'?[]:[{name:skill,enabled:true}],hp:1000,mp:1000});a.hero=c.position;a.camera={x:(u.x+c.position.x)/2,y:u.y};await a.updateAppearance();await a.prepareVisible();a.render();
  const button=a.buttons.find(b=>b.label==='怪物种类:4');if(!button)throw Error('Missing native monster sidebar');await a.pointer(a.left+(button.x+button.w/2)*a.scale,a.top+(button.y+button.h/2)*a.scale);
  const starts=[],hits=[],shots=[],hurt=c.hurt.bind(c);c.hurt=(actor,damage,options)=>{if(actor===u)hits.push({time:c.elapsed,frame:a.animationFrame(c.position),direction:c.position.direction,projectiles:c.projectiles.length});return hurt(actor,damage,options);};
  try{for(let i=0;i<280;i++){
   const version=c.position.animationVersion,projectiles=c.projectiles.length;c.update(.02);if(c.position.animationVersion!==version&&['attack','cast'].includes(c.position.action))starts.push({time:c.elapsed,action:c.position.action});if(c.projectiles.length>projectiles)shots.push({time:c.elapsed,phase:(a.animationFrame(c.position)-177)%6});
   if(i===34||i===60||i===95)c.enemyHit(u);if(i===56)c.select(u.id); // Incoming hits/reselection cannot shorten the second or third release.
  }}finally{c.hurt=hurt;}
  if(starts.length<4||starts[0].time>.021||starts.slice(1).some((s,i)=>Math.abs(s.time-starts[i].time-.96)>.021))throw Error('Uneven first/second attack cadence: '+JSON.stringify(starts));
  if(hits.length<3||skill==='基本剑术'&&hits.some(h=>h.frame!==129+h.direction*6+4)||skill==='火球术'&&(!shots.length||shots.some(s=>s.phase!==5)||hits[0].time<=shots[0].time))throw Error('Attack visual/release mismatch');a.hero=c.position;await a.prepareVisible();a.render();return {skill,starts,hits,shots};
 };
 // Returning functions is only used within the current evaluate call/window.
 if(native)return {nativeCanvas:true,walk,cases:[await runAttack('基本剑术'),await runAttack('火球术')]};
 a.continuityAttack=runAttack;return {width,walk,clicks:12};
}
