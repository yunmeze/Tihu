import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';

const dir='reports/game-recheck-20261012',owned=await ownedTestBrowser('revival-resource-fix'),browser=owned.browser,cases=[],errors=[];
try{
 for(const viewport of [{width:375,height:812,dpr:2},{width:430,height:932,dpr:1}]){
  const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:viewport.dpr});context.setDefaultTimeout(60000);
  try{
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>lpLegendReady);await enterGame(page);await page.evaluate(()=>{lpLegend.platform.cancel(lpLegend.frame);lpLegend.audio.pause(true);});
   for(const town of ['A00','B00','D00','K00']){
    const result=await page.evaluate(async town=>{
     const a=lpLegend,c=a.content;await a.changeMap(town,null,{debug:true,unlock:true});
     if(town==='A00')await a.changeMap(town,{x:138,y:12},{debug:true,unlock:true});
     await a.changeMap('A02',null,{debug:true,unlock:true});c.epoch+=100;c.textureBudget=1;await a.prepareVisible();a.combat.hurt(a.player,99999,{player:true});await a.reviveAtTown();
     const missing=[],unprotected=[],draw=a.batch.frame;
     a.batch.frame=function(pack,index,...args){const f=pack?.frames[index],file=f&&pack.pages[f.page].file;if(f&&f.rect[2]>1&&f.rect[3]>1&&pack.id.startsWith('Map/')){if(!c.textureNow(file))missing.push(file);if(!a.visibleArtFiles.has(file))unprotected.push(file);}return draw.call(this,pack,index,...args);};
     try{a.render();}finally{a.batch.frame=draw;}
     const saved=a.roster.get(a.characterId).state;
     return {map:a.mapId,home:a.map.home,position:[a.hero.x,a.hero.y],hp:a.player.hp,mp:a.player.mp,maxHp:a.player.base.hp,maxMp:a.player.base.mp,returnTown:a.player.returnTown,missing:[...new Set(missing)],unprotected:[...new Set(unprotected)],minimapReady:!!c.textureNow(a.miniFile),savedMap:saved.map,savedPosition:[saved.position.x,saved.position.y],locked:a.reviving,remainingDamageText:a.combat.events.length};
    },town);
    assert.equal(result.map,town);assert.equal(result.returnTown,town);assert.deepEqual(result.position,result.home);assert.equal(result.hp,result.maxHp);assert.equal(result.mp,result.maxMp);assert.deepEqual(result.missing,[]);assert.deepEqual(result.unprotected,[]);assert.equal(result.minimapReady,true);assert.equal(result.savedMap,town);assert.deepEqual(result.savedPosition,result.home);assert.equal(result.locked,false);assert.equal(result.remainingDamageText,0);
    await page.screenshot({path:`${dir}/revival-ready-${town}-${viewport.width}.png`});cases.push({viewport,town,...result});
   }
   await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(`${dir}/revival-resource-playtest.json`,JSON.stringify({passed:true,cases,errors},null,2));console.log({passed:true,cases:cases.length,firstFrameMissingImages:0,latestTownAndSaveVerified:true,errors});
}finally{await owned.close();}
