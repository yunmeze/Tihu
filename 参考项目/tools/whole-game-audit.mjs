// Read-only gameplay audit. All fixtures live in an isolated browser profile.
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const out='reports/whole-game-audit-20261012';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const report={date:new Date().toISOString(),method:'isolated Playwright, current dist/browser, software WebGL; fixtures are not a natural campaign playthrough',steps:[],errors:[],requests:[],ownedBrowserPid:browser._browserProcess?.process?.pid??null};
try{
 for(const width of [375,430]){
  const context=await browser.newContext({viewport:{width,height:width===375?812:932},deviceScaleFactor:1});
  const page=await context.newPage();page.setDefaultTimeout(90000);
  page.on('pageerror',e=>report.errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)report.requests.push({url:r.url(),status:r.status()});});
  const settle=async()=>page.evaluate(async()=>{const a=lpLegend;for(let i=0;i<900&&(a.preparing||a.changing||a.entering||a.npcBusy||a.appearanceLoading||a.itemBusy);i++)await new Promise(r=>setTimeout(r,20));await Promise.all([...a.content.packs.values()]);await a.content.sync();a.platform.cancel(a.frame);a.render();});
  const shot=async(name)=>{await settle();await page.screenshot({path:`${out}/${width}-${name}.png`});const state=await page.evaluate(()=>{const a=lpLegend,textures=[...(a.content.ready||[])].map(([file,t])=>({file,width:t.image?.width||0,height:t.image?.height||0}));return {screen:a.screen,map:a.mapId,position:a.hero&&{x:a.hero.x,y:a.hero.y},class:a.player?.class,story:a.combat?.story||null,taskEvent:a.player?.events?.[0],buttons:a.buttons.map(b=>({label:b.label,x:b.x,y:b.y,w:b.w,h:b.h})),texturePages:textures.length,rgbaBytes:textures.reduce((s,t)=>s+t.width*t.height*4,0),gpuTextureCount:a.renderer.info.memory.textures};});report.steps.push({width,name,file:`${width}-${name}.png`,...state});console.log('audit',width,name,'textures',state.texturePages,'RGBA MiB',Math.round(state.rgbaBytes/1048576));};
  const tap=async(label)=>{const pt=await page.evaluate(label=>{const a=lpLegend;a.render();const b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);await page.mouse.click(pt.x,pt.y);await settle();};
  try{
   await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await shot('01-home');
   await tap('踏入江湖');await shot('02-create-warrior');await tap('法师');await shot('03-create-mage');await tap('道士');await shot('04-create-taoist');await tap('创建角色');await shot('05-new-game');
   await tap('任务');await shot('06-first-task');
   await page.evaluate(async()=>{const a=lpLegend;a.player.events[0]=9;a.player.questLog='审计夹具：支线应有可查看记录';a.player.questFlags=Array(30).fill(0);a.player.questFlags[1]=1;a.render();});await shot('07-later-task');
   await page.evaluate(async()=>{const a=lpLegend;a.player.level=30;a.player.base.hp=1200;a.player.base.mp=1200;a.player.hp=1200;a.player.mp=1200;a.player.gold=123456;a.player.inventory=['木剑','草帽','草鞋','金创药小','魔法药小','回城卷','祝福油','战神油','剧毒水'].map(name=>({itemId:a.content.itemNames.get(name)?.id,quantity:6})).filter(e=>e.itemId!==undefined);a.player.skills=a.content.skills.records.map(r=>({name:r.name,level:1}));a.player.autoSkills=['召唤骷髅','回生术','施毒术','灵魂火符','治愈术','隐身术'].map(name=>({name,enabled:true}));a.player.belt=['金创药小','魔法药小','回城卷','金创药中','魔法药中','太阳水(小)'].map(name=>({itemId:a.content.itemNames.get(name).id,quantity:9}));a.player.equipment.weapon=a.content.itemNames.get('木剑').id;await a.updateAppearance();await a.prepareOwned();});
   await tap('背包');await shot('08-bag-special-item');await tap('角色');await shot('09-character');await tap('技能');await shot('10-skills');await tap('战斗');await shot('11-six-slot-hud');
   await tap('地图');await shot('12-map-modal');await tap('关闭地图');
   await tap('开悟');await shot('13-insights');await tap('关闭窗口');await tap('图鉴');await shot('14-collection');await tap('关闭窗口');
   await page.evaluate(async()=>{const a=lpLegend;const i=a.map.npcs.findIndex(n=>n.name==='海曦小贩');const n=a.map.npcs[i];Object.assign(a.hero,{x:n.x-1,y:n.y});a.camera={x:a.hero.x,y:a.hero.y};await a.prepareVisible();await a.openNpcPage(i);});await shot('15-shop');
   await page.evaluate(()=>{lpLegend.serviceView=null;lpLegend.npcDialogue=null;lpLegend.tab='战斗';});
   if(width===375){
    for(const id of ['A00','A02','B10','C00','D02','A13','A23','E30','J30']){await page.evaluate(async id=>{const a=lpLegend;await a.changeMap(id,null,{debug:true,unlock:true});a.combat.scriptLocked=false;a.player.hp=1200;a.player.mp=1200;},id);await shot('scene-'+id);}
    await page.evaluate(async()=>{const a=lpLegend;await a.changeMap('A02',null,{debug:true,unlock:true});a.player.class='法师';a.player.skills=a.content.skills.records.map(r=>({name:r.name,level:1}));a.player.autoSkills=['火球术','雷电术','御冰术','强冰术','爆裂火球','冰咆哮'].map(name=>({name,enabled:true}));await a.prepareOwned();const target=a.units.find(u=>u.alive&&!u.summoned);const p=[[-3,0],[0,-3],[3,0],[0,3]].map(([dx,dy])=>({x:Math.round(target.x)+dx,y:Math.round(target.y)+dy})).find(p=>a.combat.walkable(p.x,p.y));Object.assign(a.hero,p);a.camera={...p};a.combat.targetId=target.id;auditTargetId=target.id;await a.prepareVisible();});
    const policy=await page.evaluate(()=>{const a=lpLegend,c=a.combat,t=c.units.find(u=>u.id===auditTargetId);return {enabled:a.player.autoSkills,atDistance:Math.max(Math.abs(t.x-c.position.x),Math.abs(t.y-c.position.y)),selected:c.automaticAttackSkill(t),target:t.name};});report.autoPolicy=policy;
    await shot('16-ranged-policy');
    const trace=[];for(let i=0;i<6;i++){const event=await page.evaluate(()=>{const a=lpLegend,c=a.combat;for(let j=0;j<8;j++)c.update(.05);a.hero=c.position;a.units=c.units;a.render();return {elapsed:c.elapsed,action:c.position.action,animation:c.position.animationElapsed,windup:c.heroWindup&&{name:c.heroWindup.skill?.name,at:c.heroWindup.at},effects:c.effects.map(e=>({type:e.type,age:e.age})),projectiles:c.projectiles.map(p=>({type:p.type,age:p.age})),events:c.events.map(e=>({text:e.text,born:e.born,kind:e.kind})),lastAutoCast:c.lastAutoCast};});trace.push(event);if(i===1||i===3)await shot('combat-'+i);}report.combatTrace=trace;
   }
   await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
}finally{await browser.close();await fs.writeFile(`${out}/runtime.json`,JSON.stringify(report,null,2));console.log('audit browser closed');}
