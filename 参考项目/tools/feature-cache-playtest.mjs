import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';

const dir=process.env.LP_CACHE_REPORT_DIR||'reports/game-recheck-20261012';
await fs.mkdir(dir,{recursive:true});
const owned=await ownedTestBrowser('feature-cache-fix'),browser=owned.browser,cases=[],errors=[];
try{
 for(const viewport of [{width:375,height:812,dpr:2},{width:430,height:932,dpr:1}]){
  const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:viewport.dpr});context.setDefaultTimeout(60000);
  try{
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>lpLegendReady);await enterGame(page);
   const result=await page.evaluate(async()=>{
    const a=lpLegend,c=a.content;a.platform.cancel(a.frame);a.audio.pause(true);const rows=[],visited=new Set();
    const active=()=>a.content.permanent.collectionPool.slice(a.featureView.page*5,a.featureView.page*5+5).map(r=>{const pack=a.packs.get('Mon/'+a.content.monsters[r.id].appearance),file=pack.pages[pack.frames[17].page].file;return {id:r.id,file,ready:!!c.textureNow(file),protected:a.visibleArtFiles.has(file)};});
    for(const page of [0,20,40,60,80,100]){c.epoch+=5;await a.openFeature('collection',{page});a.render();const current=active();for(const r of current)visited.add(r.file);rows.push({page,bytes:c.cachedTextureBytes,active:current});}
    const latest=active(),evictable=[...visited].filter(f=>!a.worldArtFiles.has(f)&&!latest.some(r=>r.file===f));
    c.epoch+=100;c.textureBudget=1;await a.prepareVisible();a.render();
    return {rows,current:active(),unusedGalleryEvicted:evictable.length>0&&evictable.every(f=>!c.textures.has(f)),minimapReady:!!c.textureNow(a.miniFile),firstId:latest[0].id};
   });
   assert.ok(result.rows.every(r=>r.active.every(a=>a.ready&&a.protected)));assert.ok(result.current.every(r=>r.ready&&r.protected));assert.equal(result.unusedGalleryEvicted,true);assert.equal(result.minimapReady,true);
   const click=async label=>{const p=await page.evaluate(label=>{const a=lpLegend,b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);await page.mouse.click(p.x,p.y);await page.waitForFunction(()=>!lpLegend.preparing);await page.evaluate(async()=>{await lpLegend.content.sync();lpLegend.render();});};
   await page.screenshot({path:`${dir}/collection-cache-fixed-${viewport.width}.png`});
   await click('图鉴怪物:'+result.firstId);
   await page.evaluate(async()=>{const a=lpLegend;a.content.epoch+=100;await a.prepareVisible();a.render();});
   await click('返回列表');
   const returned=await page.evaluate(()=>{const a=lpLegend;return a.content.permanent.collectionPool.slice(500,505).map(r=>{const p=a.packs.get('Mon/'+a.content.monsters[r.id].appearance);return !!a.content.textureNow(p.pages[p.frames[17].page].file);});});assert.ok(returned.every(Boolean));
   // Complete an older page load after another page has been selected.
   const race=await page.evaluate(async()=>{
    const a=lpLegend,c=a.content,target=a.content.permanent.collectionPool[100],packId='Mon/'+a.content.monsters[target.id].appearance,pack=await a.loadPack(packId),file=pack.pages[pack.frames[17].page].file,image=c.platform.image;c.releaseTexture(file);await Promise.resolve();let release;
    c.platform.image=async function(url){if(url.endsWith(file))await new Promise(r=>release=r);return image.call(this,url);};
    try{
     const first=a.openFeature('collection',{page:20});for(let i=0;i<200&&!release;i++)await new Promise(r=>setTimeout(r,5));if(!release)throw Error('Delayed image fixture was not requested');
     const second=a.openFeature('collection',{page:100});release();await Promise.all([first,second]);a.render();
     const rows=a.content.permanent.collectionPool.slice(500,505).map(r=>{const p=a.packs.get('Mon/'+a.content.monsters[r.id].appearance),f=p.pages[p.frames[17].page].file;return {file:f,ready:!!c.textureNow(f),protected:a.visibleArtFiles.has(f)};});return {page:a.featureView.page,rows};
    }finally{release?.();c.platform.image=image;}
   });assert.equal(race.page,100);assert.ok(race.rows.every(r=>r.ready&&r.protected));
   cases.push({viewport,...result,returnListReloadedAllPreviews:true,race});await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(`${dir}/feature-cache-playtest.json`,JSON.stringify({passed:true,cases,errors},null,2));console.log({passed:true,viewports:cases.length,activeImagesProtected:true,unusedGalleryEvicted:true,latePageLoadSafe:true,errors});
}finally{await owned.close();}
