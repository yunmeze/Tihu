import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {ownedTestBrowser} from './owned-test-browser.mjs';
import {enterGame} from './enter-game.mjs';

const dir='reports/world-text-20261013',baseline=process.env.LP_TEXT_BASELINE==='1';
await fs.mkdir(dir,{recursive:true});const owned=await ownedTestBrowser('world-text-'+(baseline?'before':'after')+'-20261013'),results=[],errors=[];
const timer=setTimeout(()=>owned.close().catch(()=>{}),180000);
try{
 for(const width of [375,430]){
  const context=await owned.browser.newContext({viewport:{width,height:width===375?812:932}}),page=await context.newPage();page.setDefaultTimeout(60000);
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url());});
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  try{
   await page.goto('http://127.0.0.1:5180');await page.waitForFunction(()=>globalThis.lpLegendReady||globalThis.lpLegendError);await enterGame(page);
   for(const kind of ['dense','village']){
    const fixture=await page.evaluate(async kind=>{const {worldTextFixture}=await import('/tools/world-text-fixtures.js');return worldTextFixture(lpLegend,kind);},kind);
    await page.screenshot({path:dir+'/'+(baseline?'before':'after')+'-'+kind+'-'+width+'.png'});
    results.push({width,kind,...fixture});
    if(!baseline){
     const check=await page.evaluate(async()=>{
      const a=lpLegend,{overlaps}=await import('/src/world-label-layout.js'),w=a.worldText;
      const collisions=[];for(const [i,q]of w.placed.entries()){
       for(const next of w.placed.slice(i+1))if(overlaps(q,next,3))collisions.push([q.id,next.id]);
       for(const h of w.obstacles)if(overlaps(q,h,3))collisions.push([q.id,'hud']);
      }
      const selected=w.placed.find(q=>q.id==='unit:'+a.combat.targetId),hero=w.placed.find(q=>q.id==='hero');
      return {collisions,selected:!!selected?.bar,hero:!!hero?.bar,floatCount:w.placed.filter(q=>q.kind==='float').length,events:a.combat.events.length,group:w.placed.find(q=>q.kind==='drop'&&q.dropIds.length>1),checks:w.checks,hidden:w.hidden.map(q=>({id:q.id,kind:q.kind}))};
     });
     assert.deepEqual(check.collisions,[]);assert.ok(check.hero);if(kind==='dense'){assert.ok(check.selected);assert.equal(check.floatCount,fixture.events);assert.equal(check.group.text,'极品木剑');assert.equal(check.group.dropIds.length,3);}results.push({width,kind:kind+'-overlay-collision-and-info',...check});
     if(kind==='dense'){
      const motion=await page.evaluate(()=>{
       const a=lpLegend,c=a.combat,before=a.worldText.placed.filter(q=>q.kind==='float').map(q=>({id:q.id,x:q.x,y:q.y,dx:q.dx,dy:q.dy})),events=JSON.stringify(c.events);
       a.camera.x+=.01;a.camera.y+=.01;a.render();const camera=a.worldText.placed.filter(q=>q.kind==='float');
       const translated=before.every(q=>{const n=camera.find(n=>n.id===q.id);return n&&Math.abs(n.x-q.x+.768)<1e-7&&Math.abs(n.y-q.y+.512)<1e-7;});
       const unchanged=JSON.stringify(c.events)===events;c.elapsed+=.16;a.render();
       const rising=camera.every(q=>{const n=a.worldText.placed.find(n=>n.id===q.id);return n&&Math.abs(n.y-q.y+38*.16/1.05)<1e-7;});
       return {translated,unchanged,rising};
      });
      assert.ok(motion.translated);assert.ok(motion.unchanged);assert.ok(motion.rising);results.push({width,kind:'fractional-camera-and-floating-clock',...motion});
      const hit=await page.evaluate(()=>{const a=lpLegend,c=a.combat,u=c.units.find(u=>u.id===c.targetId),hp=u.hp;c.hurt(u,17);const e=c.events.at(-1);a.render();const shown=a.worldText.placed.some(q=>q.kind==='float'&&q.text==='17');a.player.insights[2]=0;a.render();const disabled=a.worldText.placed.filter(q=>q.kind==='float').length;a.player.insights[2]=1;a.render();return {damage:hp-u.hp,born:e.born,now:c.elapsed,shown,disabled};});
      assert.equal(hit.damage,17);assert.equal(hit.born,hit.now);assert.ok(hit.shown);assert.equal(hit.disabled,0);results.push({width,kind:'landed-damage-and-native-insight-switch',...hit});
      const picked=await page.evaluate(()=>{const a=lpLegend,c=a.combat,u=c.units.find(u=>u.id===c.targetId);c.startFarming(u.definition.id,u.id);a.render();const q=a.worldText.groundHits.find(q=>q.dropIds.length===3),g=c.groundItems.find(g=>g.id===q.dropId),p=a.screenPoint(g.x,g.y);return {ids:q.dropIds,id:q.dropId,logical:{x:q.x+q.w/2,y:q.y+q.h-7},original:{x:p.x+24*a.worldScale,y:p.y+24*a.worldScale},x:a.left+(q.x+q.w/2)*a.scale,y:a.top+(q.y+q.h-7)*a.scale};});
      assert.ok(Math.hypot(picked.logical.x-picked.original.x,picked.logical.y-picked.original.y)>35,'Click must exercise the moved label instead of the original icon hit area');
      await page.mouse.move(picked.x,picked.y);await page.mouse.down();await page.waitForTimeout(220);assert.ok(!await page.evaluate(()=>lpLegend.heldMove));await page.mouse.up();await page.waitForFunction(id=>lpLegend.combat.lootingId===id,picked.id);
      const pickup=await page.evaluate(async picked=>{const a=lpLegend,c=a.combat,manual=c.manualPath,farm=c.farmType;for(let i=0;i<1800&&!a.player.inventory.some(e=>e.name==='极品木剑');i++){c.update(.02);a.hero=c.position;}await a.prepareVisible();a.render();return {manual,farm,gear:a.player.inventory.find(e=>e.name==='极品木剑'),remainingIds:c.groundItems.filter(g=>picked.ids.includes(g.id)).map(g=>g.id)};},picked);
      assert.ok(pickup.manual);assert.equal(pickup.farm,null);assert.equal(pickup.gear?.fieldOverrides[7],7);assert.deepEqual(pickup.remainingIds,[]);await page.screenshot({path:dir+'/picked-group-'+width+'.png'});results.push({width,kind:'moved-group-label-click-and-walk-pickup',...pickup});
      const glyphs=await page.evaluate(()=>{
       const a=lpLegend,b=a.batch,original=b.outlinedText,checked=[],clipped=[];b.outlinedText=function(text,x,y,size,color,max,opacity){const actual=original.call(this,text,x,y,size,color,max,opacity),expected=b.textWidth(text,size);if(expected<=max){checked.push(text);if(Math.abs(actual-expected)>1e-6)clipped.push({text,actual,expected});}return actual;};try{a.render();}finally{b.outlinedText=original;}return {checked:checked.length,clipped};
      });assert.ok(glyphs.checked>0);assert.deepEqual(glyphs.clipped,[]);results.push({width,kind:'outlined-label-last-glyph-visible',...glyphs});
      const partial=await page.evaluate(async()=>{
       const a=lpLegend,c=a.combat,{addItem}=await import('/src/character.js'),{bagState}=await import('/src/bag-capacity.js');c.stopFarming();c.events=[];a.player.inventory=[];
       const capacity=bagState(a.player).capacity;for(const item of a.content.items.filter(i=>i.name!=='0'&&i.type>=7&&i.type<=14).slice(0,capacity))addItem(a.player,item.id,1);
       const at={x:Math.round(c.position.x),y:Math.round(c.position.y)},quest=a.content.itemNames.get('老蟾酥').id;c.groundItems.splice(0,c.groundItems.length,{id:'partial:quest',kind:'item',itemId:quest,quantity:1,...at},{id:'partial:gold',kind:'gold',quantity:125,...at});c.lootVersion++;const gold=a.player.gold;c.pickupAtFeet();await a.prepareVisible();a.render();
       const result={capacity,used:bagState(a.player).slots,goldGain:a.player.gold-gold,remaining:c.groundItems.map(g=>g.id),label:a.worldText.placed.find(q=>q.kind==='drop')?.text,groupSize:a.worldText.groundHits[0]?.dropIds.length};
       a.player.inventory.pop();c.pickupAtFeet();a.render();result.afterSpace=c.groundItems.length;result.hitsAfterSpace=a.worldText.groundHits.length;return result;
      });
      assert.equal(partial.used,partial.capacity);assert.equal(partial.goldGain,125);assert.deepEqual(partial.remaining,['partial:quest']);assert.equal(partial.label,'老蟾酥');assert.equal(partial.groupSize,1);assert.equal(partial.afterSpace,0);assert.equal(partial.hitsAfterSpace,0);results.push({width,kind:'partial-pickup-refreshes-group',...partial});
      const panel=await page.evaluate(()=>{const a=lpLegend;a.tab='背包';a.render();return {bottom:a.worldText.viewport.y+a.worldText.viewport.h,within:a.worldText.placed.every(q=>q.y+q.h<=1032)};});assert.equal(panel.bottom,1032);assert.ok(panel.within);await page.screenshot({path:dir+'/bag-view-'+width+'.png'});results.push({width,kind:'labels-respect-system-panel-boundary',...panel});
     }
    }
   }
   await page.evaluate(()=>lpLegend.dispose());
  }finally{await context.close();}
 }
 assert.deepEqual(errors,[]);await fs.writeFile(dir+'/'+(baseline?'baseline':'playtest')+'.json',JSON.stringify({passed:true,results,errors,scope:'Two isolated portrait browser contexts with original C12/A00 packs and collision. Dense-drop/damage fixtures, actual moved-label clicks, walking/pickup, partial capacity, native insight switch, fractional camera and glyph rendering. Elevated HP and all insights for visibility; not a normal campaign or hardware FPS benchmark.'},null,2));console.log({passed:true,cases:results.length,baseline});
}catch(error){await fs.writeFile(dir+'/playtest-attempt.json',JSON.stringify({passed:false,results,errors,error:String(error)},null,2));throw error;}
finally{clearTimeout(timer);await owned.close();}
