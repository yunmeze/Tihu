import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';

const dir=process.env.LP_CACHE_REPORT_DIR||'reports/audit-fixes-20261012';
await fs.mkdir(dir,{recursive:true});
const owned=await ownedTestBrowser('minimap-cache-fix'),browser=owned.browser,cases=[],errors=[];
try{
 for(const viewport of [{width:375,height:812,dpr:2},{width:430,height:932,dpr:1}]){
  const context=await browser.newContext({viewport:{width:viewport.width,height:viewport.height},deviceScaleFactor:viewport.dpr});
  context.setDefaultTimeout(60000);
  try{
   const page=await context.newPage();
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:5180');
   await page.waitForFunction(()=>globalThis.lpLegendReady);
   await enterGame(page);
   await page.evaluate(()=>{const a=lpLegend;a.platform.cancel(a.frame);a.audio.pause(true);});
   const click=async label=>{
    const point=await page.evaluate(label=>{const a=lpLegend,b=a.buttons.find(b=>b.label===label);if(!b)throw Error('Missing '+label);return {x:a.left+(b.x+b.w/2)*a.scale,y:a.top+(b.y+b.h/2)*a.scale};},label);
    await page.mouse.click(point.x,point.y);
    await page.evaluate(()=>lpLegend.render());
   };
   for(const map of ['A00','A02']){
    const cache=await page.evaluate(async map=>{
     const a=lpLegend,c=a.content;
     if(a.mapId!==map)await a.changeMap(map,null,{debug:true,unlock:true});
     a.mapOpen=false;a.render();
     const file=a.miniFile,initial=c.ready.get(file);
     if(!initial||!a.visibleArtFiles.has(file))throw Error('Original minimap missing after entering '+map);
     // Pressure must still evict unrelated art, while retaining the current
     // minimap even when it has not been rendered recently.
     const other=a.content.minimaps.maps[map==='A00'?'A02':'A00'].file;
     await c.texture(other);await c.sync();c.epoch+=100;c.textureBudget=1;
     await a.prepareVisible();
     const retained=c.ready.get(file)===initial,unrelatedEvicted=!c.textures.has(other);
     // An absent active page is acquired again through normal view loading.
     c.releaseTexture(file);await Promise.resolve();await a.prepareVisible();
     const restored=c.ready.get(file);
     a.render();
     return {file,initialOriginalReady:!!initial,protected:a.visibleArtFiles.has(file),retainedUnderPressure:retained,unrelatedEvicted,reloaded:!!restored&&restored!==initial,reloadedFile:restored?.userData.file,budget:c.textureBudget,cachedBytes:c.cachedTextureBytes};
    },map);
    assert.equal(cache.protected,true);assert.equal(cache.retainedUnderPressure,true);
    assert.equal(cache.unrelatedEvicted,true);assert.equal(cache.reloaded,true);assert.equal(cache.reloadedFile,cache.file);
    await page.screenshot({path:`${dir}/minimap-fixed-battle-${map}-${viewport.width}.png`});
    await click('地图');assert.equal(await page.evaluate(()=>lpLegend.mapOpen),true);
    const visual=await page.evaluate(()=>{
     const a=lpLegend,quad=a.batch.quad,calls=[];
     a.batch.quad=function(x,y,w,h,color,texture,uv,...rest){if(texture?.userData.file===a.miniFile)calls.push({x,y,w,h,uv});return quad.call(this,x,y,w,h,color,texture,uv,...rest);};
     try{a.render();}finally{a.batch.quad=quad;}
     // Check actual rendered color detail, not only requested image promises.
     const image=calls.find(c=>c.w>200);if(!image)throw Error('Map dialog does not draw the original image');
     const gl=a.renderer.getContext(),ratio=a.renderer.getPixelRatio();
     const x=Math.ceil((a.left+(image.x+8)*a.scale)*ratio),y=Math.ceil(gl.drawingBufferHeight-(a.top+(image.y+image.h-8)*a.scale)*ratio),w=Math.floor((image.w-16)*a.scale*ratio),h=Math.floor((image.h-16)*a.scale*ratio),pixels=new Uint8Array(w*h*4),colors=new Set();
     gl.readPixels(x,y,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
     for(let i=0;i<pixels.length;i+=4)colors.add((pixels[i]<<16)|(pixels[i+1]<<8)|pixels[i+2]);
     return {originalImageDraws:calls.length,dialogImageUV:image.uv,renderedColors:colors.size,mapOpen:a.mapOpen};
    });
    assert.equal(visual.originalImageDraws,2,'Both corner and dialog minimaps must draw native art');
    assert.ok(visual.renderedColors>256,'Map has fallen back to flat walkability blocks');
    await page.screenshot({path:`${dir}/minimap-fixed-dialog-${map}-${viewport.width}.png`});
    cases.push({viewport,map,cache,visual});await click('关闭地图');
   }
   // The original has no J30 miniature; retain its deliberate grid fallback.
   const fallback=await page.evaluate(async()=>{const a=lpLegend;await a.changeMap('J30',null,{debug:true});a.mapOpen=true;a.render();return {map:a.mapId,miniFile:a.miniFile,oldMinimapReleased:!a.content.textures.has('minimaps/A02.jpg')};});
   assert.equal(fallback.miniFile,undefined);assert.equal(fallback.oldMinimapReleased,true);
   cases.push({viewport,fallback});await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);
 await fs.writeFile(`${dir}/minimap-cache-playtest.json`,JSON.stringify({passed:true,cases,errors},null,2));
 console.log({passed:true,nativeImageCases:cases.filter(c=>c.visual).length,fallbackCases:cases.filter(c=>c.fallback).length,errors});
}finally{await owned.close();}
