// Isolated browser fixtures use original packs and collision. They do not
// modify resources, production saves, or the game's simulation clock.
export async function worldTextFixture(a,kind='dense'){
 a.platform.cancel(a.frame);a.audio.pause(true);a.player.events[0]=10;
 a.player.inventory=[];a.player.belt=Array(6).fill(null);a.player.hp=a.player.base.hp=10000;
 a.player.insights=[1,1,1,1,1,1];a.player.name='英雄';
 a.npcDialogue=a.serviceView=a.featureView=null;a.mapOpen=false;
 a.combat.groundByMap={};a.mapFlagsByMap={};a.scriptState={};
 await a.changeMap(kind==='village'?'A00':'C12',kind==='village'?{x:87,y:52}:{x:61,y:62},{debug:true});
 const c=a.combat;c.stopFarming();c.events=[];c.autoLoot=false;
 if(kind==='dense'){
  const near=c.units.filter(u=>Math.abs(u.x-a.hero.x)<5&&Math.abs(u.y-a.hero.y)<6);
  const boss=c.units.find(u=>u.name==='蛙统领');
  if(boss&&!near.includes(boss))near.push(boss);
  if(boss)c.targetId=boss.id;
  const landing=[];for(let y=60;y<=67;y++)for(let x=58;x<=64;x++)if(c.walkable(x,y)&&!(x===61&&y===62))landing.push({x,y});
  a.fixtureCells=landing;
  const drop=(name,cell,extra={})=>({id:'fixture:'+c.groundItems.length,kind:'item',itemId:a.content.itemNames.get(name).id,quantity:1,...cell,...extra});
  for(const [i,p]of landing.slice(0,10).entries())c.groundItems.push(drop(i===0?'老蟾酥':i%2?'金创药小':'魔法药小',p,{quantity:i+1}));
  const cell=landing[4];
  c.groundItems.push(drop('木剑',cell,{name:'极品木剑',fieldOverrides:{7:7}}));
  c.groundItems.push({id:'fixture:gold',kind:'gold',quantity:125,...cell});
  const {combatText}=await import('/src/combat-text.js');
  for(const [i,u]of near.slice(0,8).entries())combatText(c,u,17+i,{actorId:u.id,appearance:u.definition.appearance,amount:17+i});
  combatText(c,c.position,'−12',{actorId:'player',color:'#ffaaa0',amount:12});
 }
 c.lootVersion++;a.camera={...a.hero};a.tab='战斗';
 await a.prepareVisible();a.render();
 return {map:a.mapId,units:c.units.length,events:c.events.length,drops:c.groundItems.length,hero:{x:a.hero.x,y:a.hero.y}};
}
