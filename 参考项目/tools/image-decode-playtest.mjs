import fs from 'node:fs/promises';import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';import {enterGame} from './enter-game.mjs';
const dir='reports/movement-20261013',owned=await ownedTestBrowser('image-decode-pixels'),cases=[],errors=[];
try{for(const width of [375,430]){
 const context=await owned.browser.newContext({viewport:{width,height:width===375?812:932},deviceScaleFactor:width===375?1:2});
 try{const page=await context.newPage();page.setDefaultTimeout(90000);page.on('pageerror',e=>errors.push(e.message));await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady);await enterGame(page);
  for(const [map,tab]of [['A00','战斗'],['A00','角色'],['A02','战斗'],['K24','战斗']]){
   const result=await page.evaluate(async({map,tab})=>{const a=lpLegend;a.platform.cancel(a.frame);a.audio.pause(true);if(a.mapId!==map)await a.changeMap(map,null,{debug:true,unlock:true});a.tab=tab;await a.prepareVisible();await a.prepareOwned();a.render();const gl=a.renderer.getContext(),read=()=>{const bytes=new Uint8Array(gl.drawingBufferWidth*gl.drawingBufferHeight*4);gl.readPixels(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight,gl.RGBA,gl.UNSIGNED_BYTE,bytes);return bytes;};
    const bitmapPixels=read(),pairs=[],missing=[];let differing=0,maxDifference=0;
    try{for(const [file,texture]of a.content.ready){if(!(texture.image instanceof ImageBitmap))continue;const image=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=a.content.base+file;});await image.decode();pairs.push({texture,bitmap:texture.image,image});}for(const p of pairs){p.texture.image=p.image;p.texture.needsUpdate=true;}a.render();const htmlPixels=read();for(let i=0;i<htmlPixels.length;i+=4){let max=0;for(let k=0;k<4;k++)max=Math.max(max,Math.abs(htmlPixels[i+k]-bitmapPixels[i+k]));maxDifference=Math.max(maxDifference,max);if(max>1)differing++;}
    }finally{for(const p of pairs){p.texture.image=p.bitmap;p.texture.needsUpdate=true;}}
    for(const file of a.visibleArtFiles||[])if(!a.content.textureNow(file))missing.push(file);a.render();return {map,tab,differing,maxDifference,bitmapTextures:pairs.length,missing};
   },{map,tab});assert.ok(result.bitmapTextures>0);assert.equal(result.differing,0);assert.deepEqual(result.missing,[]);cases.push({width,...result});await page.screenshot({path:`${dir}/bitmap-${width}-${map}-${tab}.png`});console.log({width,...result});
  }
  await page.evaluate(()=>lpLegend.dispose());
 }finally{await context.close();}
}assert.deepEqual(errors,[]);await fs.writeFile(dir+'/pixels.json',JSON.stringify({passed:true,cases,errors,oracle:'Same frozen scene rendered with predecoded ImageBitmap and original HTMLImageElement sources; RGB/alpha tolerance1.'},null,2));
}finally{await owned.close();}
