import {enterGame} from './enter-game.mjs';
import {chromium} from 'playwright';import fs from 'node:fs/promises';import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true,executablePath:process.env.LP_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const errors=[],checks=[];
try{
 for(const config of [{width:375,height:812,dpr:2},{width:430,height:916,dpr:1}]){
  const p=await browser.newPage({viewport:{width:config.width,height:config.height},deviceScaleFactor:config.dpr});p.on('pageerror',e=>errors.push(e.message));
  await p.goto('http://127.0.0.1:5180');await p.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(p);assert.equal(await p.evaluate(()=>globalThis.lpLegendError),undefined);
  const point=async(x,y)=>p.evaluate(({x,y})=>({x:lpLegend.left+x*lpLegend.scale,y:lpLegend.top+y*lpLegend.scale}),{x,y});
  const move=async(x,y)=>{const q=await point(x,y);await p.mouse.move(q.x,q.y);};
  await p.keyboard.down('g');assert.equal(await p.evaluate(()=>lpLegend.gmOpen),true);await p.waitForTimeout(80);await p.screenshot({path:`reports/gm-wheel-${config.width}.png`});
  await p.keyboard.up('g');assert.equal(await p.evaluate(()=>lpLegend.gmOpen),false);assert.equal(await p.evaluate(()=>lpLegend.player.skills.length),1);
  await p.keyboard.down('g');await move(240,780);await p.keyboard.up('g');await p.waitForFunction(()=>!lpLegend.gmBusy);assert.equal(await p.evaluate(()=>lpLegend.player.skills.length),26);await p.evaluate(()=>lpLegend.message=null);
  const paging=await p.evaluate(()=>{const a=lpLegend;a.render();const q=a.buttons.find(b=>b.label==='1 / 3');return {x:a.left+(q.x+q.w/2)*a.scale,y:a.top+(q.y+q.h/2)*a.scale};});await p.mouse.click(paging.x,paging.y);assert.equal(await p.evaluate(()=>lpLegend.skillPage),1);
  await move(260,1430);await p.mouse.down();await move(490,1430);await p.mouse.up();assert.equal(await p.evaluate(()=>lpLegend.skillPage),0);
  await move(490,1430);await p.mouse.down();await move(260,1430);await p.mouse.up();assert.equal(await p.evaluate(()=>lpLegend.skillPage),1);
  await p.waitForTimeout(80);await p.screenshot({path:`reports/battle-compact-${config.width}.png`});
  const visible=await p.evaluate(()=>lpLegend.buttons.filter(b=>b.label.startsWith('技能:')).map(b=>b.label));assert.ok(visible.includes('技能:火球术'));
  const spell=await p.evaluate(()=>{const a=lpLegend,q=a.buttons.find(b=>b.label==='技能:火球术');return {x:a.left+(q.x+q.w/2)*a.scale,y:a.top+(q.y+q.h/2)*a.scale};});await p.mouse.click(spell.x,spell.y);assert.equal(await p.evaluate(()=>lpLegend.player.activeSkill),'火球术');
  await p.evaluate(()=>{const a=lpLegend;a.platform.cancel(a.frame);const u=a.combat.nearby()[0];a.combat.position={x:u.x-1,y:u.y,direction:2,action:'idle',animationElapsed:0,actionTime:0};a.hero=a.combat.position;a.camera={x:a.hero.x,y:a.hero.y};a.combat.select(u.id);a.combat.hitClock=1.5;a.combat.update(.001);a.hero=a.combat.position;a.render();});
  assert.equal(await p.evaluate(()=>lpLegend.hero.action),'cast');await p.screenshot({path:`reports/casting-${config.width}.png`});
  await p.evaluate(()=>{lpLegend.player.gold=123;lpLegend.player.experience=7;lpLegend.player.skills[0].level=3;lpLegend.save();localStorage.setItem('gm-test-unrelated','keep');});
  await p.reload();await p.waitForFunction(()=>globalThis.lpLegendReady);await enterGame(p);assert.equal(await p.evaluate(()=>lpLegend.player.skills.length),26);assert.equal(await p.evaluate(()=>lpLegend.player.experience),7);
  // Click a sector while holding G; keyup must not run the command twice.
  await p.keyboard.down('g');const clear=await point(515,780);await p.mouse.click(clear.x,clear.y);await p.keyboard.up('g');await p.waitForFunction(()=>!lpLegend.gmBusy);
  const fresh=await p.evaluate(()=>({skills:lpLegend.player.skills.length,gold:lpLegend.player.gold,xp:lpLegend.player.experience,map:lpLegend.mapId,tab:lpLegend.tab,unrelated:localStorage.getItem('gm-test-unrelated')}));assert.deepEqual(fresh,{skills:1,gold:0,xp:0,map:'A00',tab:'战斗',unrelated:'keep'});
  await p.reload();await p.waitForFunction(()=>globalThis.lpLegendReady);await enterGame(p);assert.equal(await p.evaluate(()=>lpLegend.player.skills.length),1);assert.equal(await p.evaluate(()=>lpLegend.player.experience),0);
  await p.keyboard.down('g');await move(515,780);await p.evaluate(()=>dispatchEvent(new Event('blur')));assert.equal(await p.evaluate(()=>lpLegend.gmOpen),false);await p.keyboard.up('g');
  await p.evaluate(()=>lpLegend.dispose());await p.keyboard.down('g');assert.equal(await p.evaluate(()=>lpLegend.gmOpen),false);await p.keyboard.up('g');
  checks.push({config,gmHoldCancel:true,unlockAll26:true,skillsPaged:true,spellUsesCastFrames:true,saveReload:true,clearOnlyGameSave:true,blurCancels:true,keyboardDisposed:true});await p.close();
 }
 assert.deepEqual(errors,[]);await fs.writeFile('reports/gm-hud-playtest.json',JSON.stringify({passed:true,checks,errors},null,2));console.log(JSON.stringify({passed:true,checks,errors}));
}finally{await browser.close();}
