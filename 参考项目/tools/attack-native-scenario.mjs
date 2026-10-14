// Serialized into the native canvas/IO test environment, without DOM access.
export async function nativeAttackChaseScenario(){
 const a=nativeTest.gameGlobal.lpLegend;await a.changeMap('A00',null,{unlock:true});const cases=[];
 for(const skill of ['基本剑术','火球术']){
  const c=a.combat;c.enter(a.map,{x:86,y:52});const u=c.units.find(u=>u.definition.id===4&&u.x>8&&u.y>4&&Array.from({length:8},(_,i)=>u.x-i).every(x=>c.walkable(x,u.y)));if(!u)throw Error('No native chase fixture');const range=skill==='基本剑术'?1:6;
  c.units=a.units=[u];u.hp=1000;u.definition={...u.definition,hp:1000,speed:0,behavior:-1,defense:0,magicDefense:0,physicalEvade:0,magicEvade:0,regenFrames:0};Object.assign(a.player,{hp:1000,mp:1000,skills:[{name:skill,level:1}],activeSkill:skill,autoSkills:skill==='基本剑术'?[]:[{name:skill,enabled:true}]});Object.assign(a.player.base,{hp:1000,mp:1000,accuracy:100,attack:[5,5],magic:[5,5]});c.battleRandom=c.monsterRandom=()=>.99;c.elapsed=c.hitCount=0;c.events=[];c.groundItems.splice(0);Object.assign(c.position,{x:u.x-range-.4,y:u.y});a.hero=c.position;a.camera={x:(a.hero.x+u.x)/2,y:u.y};a.tab='战斗';await a.prepareVisible();a.render();
  if(c.findPath(u).length!==1)throw Error('Native fractional path omitted its final step');const button=a.buttons.find(b=>b.label==='怪物种类:4');await a.pointer(a.left+(button.x+button.w/2)*a.scale,a.top+(button.y+button.h/2)*a.scale);
  const start=c.position.x,hits=[],shots=[],hurt=c.hurt.bind(c);c.hurt=(actor,damage,options)=>{if(actor===u)hits.push({time:c.elapsed,frame:a.animationFrame(c.position),direction:c.position.direction,projectiles:c.projectiles.length});return hurt(actor,damage,options);};
  try{for(let i=0;i<290;i++){const old=c.projectiles.length;c.update(.02);if(c.projectiles.length>old)shots.push({time:c.elapsed,action:c.position.action,phase:(a.animationFrame(c.position)-177)%6});}}finally{c.hurt=hurt;}
  if(c.hitCount<2||c.position.x<=start||c.farmType!==4)throw Error('Native range-edge attack stalled');
  if(skill==='基本剑术'&&hits.some(h=>h.frame!==129+h.direction*6+4)||skill==='火球术'&&(!shots.length||shots.some(s=>s.action!=='cast'||s.phase!==5)||hits[0].time<=shots[0].time))throw Error('Native attack contact timing changed');
  a.hero=c.position;a.render();cases.push({skill,hits:c.hitCount,moved:c.position.x-start,contactTiming:true});
 }
 return {meleeAndFireballEdges:true,sidebarInput:true,nativeCanvas:true,cases};
}
