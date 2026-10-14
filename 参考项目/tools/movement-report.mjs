import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const dir='reports/movement-20261013',read=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const [before,after,special,rules,pixels,featureCache,minimapCache,backup,verification,build]=await Promise.all([
 'profile-before.json','profile-after.json','rules.json','rule-regressions.json','pixels.json','feature-cache-playtest.json','minimap-cache-playtest.json','source-before.json'
].map(file=>read(dir+'/'+file)).concat([read('reports/verification.json'),read('reports/build.json')]));
for(const result of [special,rules,pixels,featureCache,minimapCache,verification])assert.equal(result.passed,true);
assert.deepEqual(pixels.errors,[]);assert.ok(pixels.cases.every(c=>c.differing===0&&c.maxDifference===0&&c.missing.length===0));
const hash=async file=>crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
for(const row of backup.files)assert.equal(await hash(backup.backup+'/'+row.file.split('/').at(-1)),row.sha256);
const changes=[];
for(const name of (await fs.readdir('src')).filter(n=>n.endsWith('.js')).sort()){
 const file='src/'+name,sha256=await hash(file),old=backup.files.find(row=>row.file===file)?.sha256;
 if(sha256!==old)changes.push({file,sha256,beforeSha256:old||null});
}
const lifecycle=[];
for(const purpose of ['movement-profile-before','movement-profile-after','image-decode-pixels','ui-rules','feature-cache-fix','minimap-cache-fix']){
 const record=await read('reports/audit-fixes-20261012/lifecycle/'+purpose+'.json');
 assert.ok(record.closed&&record.exitCode===0);lifecycle.push(record);
}
const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
const aiBenchmarks=special.benchmark.map(row=>{
 const before=median(row.pairs.map(p=>p.before)),after=median(row.pairs.map(p=>p.after));
 return {monsters:row.count,steps:300,alternatingPairs:row.pairs.length,beforeMs:before,afterMs:after,reductionPercent:100*(1-after/before)};
});
const measurements=after.results.map(current=>{
 const old=before.results.find(row=>row.map===current.map);assert.ok(old);
 const summary=sample=>({firstRenderMs:sample.rows[0].render,frameIntervals:sample.stats,textureUploads:sample.uploads.filter(row=>row.api==='texSubImage2D').map(row=>({frame:row.frame,width:row.width,ms:row.ms}))});
 return {map:current.map,monsters:current.units,before:summary(old),after:summary(current)};
});
const next=[
 '移动长帧仍需在硬件渲染环境复测；软件WebGL的三明界场景仍有长帧。',
 '通用粒子6、天气粒子10–16的真实入口尚未接通。',
 '范围攻击、弹体寿命和占位碰撞仍需逐分支核对。',
 '专家/地狱的条件物品与特殊掉落分支尚未全部还原。'
];
const findings=[
 {title:'减少首次显示贴图时的阻塞',detail:'浏览器先异步解码原版图集，再交给渲染器；显式保留原图方向、透明度和颜色处理。旧浏览器保留Image解码路径。'},
 {title:'减少怪物AI重复扫描',detail:'每个模拟步建立单位与阵营索引，以单次遍历选择最近目标；保留距离相等时的原始顺序，攻击触发脚本后刷新索引。追击、待机、召唤物及隐身逻辑维持原行为。'},
 {title:'回收解码后的图像内存',detail:'贴图淘汰、游戏退出及未完成加载的取消都会释放ImageBitmap，避免反复换图积累图像内存。'}
];
const report={title:'小小传奇 · 移动停顿优化与回归',date:new Date().toISOString(),passed:true,fullOriginalEquivalent:false,stutterFullyResolved:false,
 findings,next,previousContentReport:'../restoration-20261013/report.html',
 performance:{softwareWebGL:true,method:'375×812 DPR1 Chromium SwiftShader,360 frames per scene,CDP500µs sampling. Frame-interval statistics discard the first30 frames. Runs use the same start/target and random seed, but real-time frame intervals produce different simulation paths. Timings include profiling and software-GPU scheduling; they are not controlled hardware FPS benchmarks.',measurements,aiBenchmarks,aiMethod:'Isolated idle-AI CPU timing:300 calls per sample,30 warm-up calls,5 alternating before/after pairs. This measures AI only, not total game frame time.'},
 verification:{sourceBackupVerified:backup.files.length,ruleSuites:rules.count,specialChecks:special.checks.length,stateComparisonScenarios:5,stateComparisonStepsPerScenario:300,pixelCases:pixels.cases.length,pixelDifferences:0,cacheViewports:featureCache.cases.length,nativeMinimapCases:minimapCache.cases.filter(c=>c.visual).length,deliberateFallbackCases:minimapCache.cases.filter(c=>c.fallback).length,build,assetChecksPassed:verification.passed,visualReview:['bitmap-375-A02-战斗.png','bitmap-430-K24-战斗.png','bitmap-375-A00-角色.png']},
 sourceChanges:changes,lifecycle,preview:'Existing port5180 preview was reused and preserved; no preview server was started by this round.',wechat:'Skipped at user request'};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
const esc=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const ms=value=>value.toFixed(1)+' ms';
const cards=[['bitmap-375-A02-战斗.png','树林深处'],['bitmap-430-K24-战斗.png','天界三明界'],['bitmap-375-A00-角色.png','角色与原版图像']];
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(report.title)}</title><style>body{max-width:1040px;margin:32px auto;padding:0 20px;background:#f5f1e8;color:#30261e;font:16px/1.7 system-ui}h1{font-size:28px}article{border-top:1px solid #cdbfa8;padding:12px 0}table{border-collapse:collapse;width:100%}td,th{border:1px solid #cdbfa8;padding:9px;text-align:left}figure{display:inline-block;width:29%;min-width:220px;vertical-align:top;margin:14px 2% 14px 0}img{width:100%;border:1px solid #b7a285}a{color:#765214}.pass{color:#2f6c37}.pending{color:#894b12}</style><h1>${esc(report.title)}</h1><p class="pass">${rules.count}组规则回归、${pixels.cases.length}组逐像素对照、小地图与图鉴缓存压力测试通过。</p>${findings.map(f=>`<article><strong>${esc(f.title)}</strong><p>${esc(f.detail)}</p></article>`).join('')}<h2>首次渲染与贴图上传</h2><p>同一场景开始位置、目标位置及随机种子，使用软件WebGL采样。以下是本次测量值；采样开销和系统调度会影响结果，不代表所有设备的帧率。</p><table><tr><th>地图</th><th>首次渲染：之前 → 之后</th><th>单张上传范围：之前 → 之后</th></tr>${measurements.map(m=>{const a=m.before.textureUploads.map(u=>u.ms),b=m.after.textureUploads.map(u=>u.ms);return `<tr><td>${m.map}</td><td>${ms(m.before.firstRenderMs)} → ${ms(m.after.firstRenderMs)}</td><td>${ms(Math.min(...a))}–${ms(Math.max(...a))} → ${ms(Math.min(...b))}–${ms(Math.max(...b))}</td></tr>`;}).join('')}</table><h2>空闲怪物AI专项</h2><p>每个样本300步，交替运行5对样本取中位数；仅衡量AI计算，不是整帧耗时。</p><table><tr><th>怪物数量</th><th>之前</th><th>之后</th><th>耗时降低</th></tr>${aiBenchmarks.map(row=>`<tr><td>${row.monsters}</td><td>${ms(row.beforeMs)}</td><td>${ms(row.afterMs)}</td><td>${row.reductionPercent.toFixed(1)}%</td></tr>`).join('')}</table><h2>行为与画面</h2><p>追击、召唤物、隐身、战斗脚本生成新单位等5类场景各连续300步，完整状态与优化前一致。8组冻结画面对照中，图像差异像素为0。缓存压力下原版小地图、图鉴图片与延迟请求均通过检查。</p>${cards.map(([file,title])=>`<figure><a href="${file}"><img src="${file}" alt="${title}"></a><figcaption>${title}</figcaption></figure>`).join('')}<h2>继续跟进</h2><ul class="pending">${next.map(item=>`<li>${esc(item)}</li>`).join('')}</ul><p>89份修改前源码备份已核验哈希。本轮测试浏览器已关闭，原有5180预览服务保留。微信按用户要求跳过。</p><p><a href="report.json">完整结果</a> · <a href="profile-before.json">优化前采样</a> · <a href="profile-after.json">优化后采样</a> · <a href="rule-regressions.json">规则回归</a> · <a href="pixels.json">像素对照</a> · <a href="../restoration-20261013/report.html">上一轮内容补齐</a></p></html>`;
await fs.writeFile(dir+'/report.html',html);
await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next},null,2));
console.log({passed:true,changedSourceFiles:changes.map(row=>row.file),ruleSuites:rules.count,pixelCases:pixels.cases.length,allOwnedBrowsersClosed:true,report:dir+'/report.html'});
