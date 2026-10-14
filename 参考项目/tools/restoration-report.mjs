import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const dir='reports/restoration-20261013',read=async f=>JSON.parse(await fs.readFile(f,'utf8'));
const [native,rules,special,visual,screens,movement,backup,build]=await Promise.all(['native-source.json','rule-regressions.json','rules.json','playtest.json','screens/runtime.json','movement-performance-after.json','source-before.json'].map(f=>read(dir+'/'+f)).concat([read('reports/build.json')]));
assert.ok(native.passed&&rules.passed&&special.passed&&visual.passed);
const missingImages=screens.steps.flatMap(s=>s.missingImages),missingGlyphs=screens.steps.flatMap(s=>s.missingGlyphs),truncated=screens.steps.flatMap(s=>s.truncated);
assert.deepEqual([...screens.errors,...screens.requests,...missingImages,...missingGlyphs,...truncated],[]);
const hash=async file=>crypto.createHash('sha256').update(await fs.readFile(file)).digest('hex');
for(const row of backup.files)assert.equal(await hash(backup.backup+'/'+row.file.split('/').at(-1)),row.sha256);
const changes=[];
for(const name of (await fs.readdir('src')).filter(n=>n.endsWith('.js')).sort()){
 const file='src/'+name,sha256=await hash(file),before=backup.files.find(f=>f.file===file)?.sha256;
 if(sha256!==before)changes.push({file,sha256,beforeSha256:before||null});
}
const lifecycle=[];
for(const purpose of ['restoration-20261013','restoration-movement','whole-game-recheck','ui-rules']){
 const record=await read('reports/audit-fixes-20261012/lifecycle/'+purpose+'.json');assert.ok(record.closed&&record.exitCode===0);lifecycle.push(record);
}
const findings=[
 {title:'天界地图雾效',change:'按原版地图名分支接入天路、三明界、轮回的两类雾效，保留生成节奏、缩放、淡入淡出和地图坐标。',evidence:'native-weather-emission.txt'},
 {title:'地面装备特效',change:'窥世之眼Ⅲ生效后，按装备实例属性显示普通极品星光、高级极品彩色旋转星光及异常属性粒子；拾取后停止生成。',evidence:'native-ground-glow.txt'},
 {title:'明阳守卫第二阶段',change:'仅原名明阳守卫首次生命归零时恢复30%，获得70%的持续回血池，每个50Hz刻度恢复3点；保留生命上限，切换攻击种类22并调整速度和攻防，播放原版复活特效及声音。最后一次死亡才结算事件、经验、宠物击杀和掉落；重新刷新恢复第一阶段。',evidence:'native-guard-rebirth.txt'},
 {title:'高难度挑战与守城存档',change:'存档合法血量按当前难度及通关轮次校验，避免专家/地狱敌人的正常血量导致整场重置；守城友方战旗使用原始模板，不受敌方难度加成影响。',evidence:'rules.json'},
 {title:'资源初始化与第二阶段换招',change:'修复进入地图前尚无掉落列表时的启动异常；守卫第二阶段会触发招式资源预加载，新增特效资源随地图和掉落按需准备。',evidence:'playtest.json'}
];
const next=['通用粒子6、天气粒子10–16的真实入口尚未接通。','范围攻击、弹体寿命和占位碰撞仍需逐分支核对。','专家/地狱的条件物品与特殊掉落分支尚未全部还原。','移动长帧仍存在：需进一步采样定位，并在硬件渲染环境复测。'];
const report={title:'小小传奇 · 2026-10-13 内容补齐与回归',date:new Date().toISOString(),passed:true,fullOriginalEquivalent:false,findings,next,
 verification:{sourceBackupVerified:backup.files.length,sourceFilesChanged:changes.length,ruleSuites:rules.count,specialChecks:special.checks.length,visualCases:visual.results.length,wholeGameScreens:screens.steps.length,missingImages:missingImages.length,missingGlyphs:missingGlyphs.length,truncatedTexts:truncated.length,errors:screens.errors,failedRequests:screens.requests,build,manualVisualReview:['375-K23-fog.png','375-K24-fog.png','430-ground-glow.png','430-guard-rebirth.png','screens/375-09-character.png','screens/430-15-shop.png']},
 movement:{stutterFullyResolved:false,softwareWebGL:true,method:'Each scene measured alone for180 frames with render, simulation, resource-preparation and drawing counters. Single runs include first-visible resource work; these are not controlled hardware FPS benchmarks.',cases:movement.cases.map(c=>({map:c.map,frame:c.frame,cost:c.cost,longTasks:c.longTasks,geometryGroups:c.geometryGroups})),conclusion:'Movement/action continuity checks pass; long frames remain, especially in A02 and K24. No new movement-performance improvement is claimed for this patch.'},
 recoveryNote:'An initial visual/UI run failed before map entry because groundItems did not yet exist. That was fixed and rebuilt; the subsequent UI,10 visual cases,51 screen sweep and all49 rule suites passed.',
 sourceChanges:changes,sourceEvidence:'native-source.json',lifecycle,preview:'Existing port5180 preview was reused and preserved. This round created no new preview server.',wechat:'Skipped at user request'};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next},null,2));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const cards=[['375-K23-fog.png','天路雾效'],['375-K24-fog.png','三明界雾效'],['430-ground-glow.png','地面装备属性特效'],['430-guard-rebirth.png','明阳守卫复活阶段']];
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(report.title)}</title><style>body{max-width:1060px;margin:32px auto;padding:0 20px;background:#f5f1e8;color:#30261e;font:16px/1.7 system-ui}h1{font-size:28px}article{border-top:1px solid #cdbfa8;padding:12px 0}table{border-collapse:collapse;width:100%}td,th{border:1px solid #cdbfa8;padding:9px;text-align:left}figure{display:inline-block;width:23%;min-width:210px;vertical-align:top;margin:14px 1% 14px 0}img{width:100%;border:1px solid #b7a285}figcaption{font-size:14px}a{color:#765214}.pass{color:#2f6c37}.pending{color:#894b12}</style><h1>${esc(report.title)}</h1><p class="pass">构建、${rules.count}组规则检查、${visual.results.length}个专项画面场景、${screens.steps.length}个整体验收画面通过。无缺图、缺字、文字截断、脚本错误或资源请求失败。</p>${findings.map(f=>`<article><strong>${esc(f.title)}</strong><p>${esc(f.change)} <a href="${f.evidence}">证据</a></p></article>`).join('')}<div>${cards.map(([file,label])=>`<figure><a href="${file}"><img src="${file}"></a><figcaption>${label}</figcaption></figure>`).join('')}</div><h2>移动测量</h2><p class="pending">仍有长帧，本轮没有宣称卡顿已解决。下列为单次软件WebGL测量，不能代表硬件设备表现或作为改进比例。</p><table><tr><th>地图</th><th>帧间隔中位数</th><th>P95</th><th>最长帧</th><th>长任务数量</th></tr>${movement.cases.map(c=>`<tr><td>${c.map}</td><td>${c.frame.p50.toFixed(1)}ms</td><td>${c.frame.p95.toFixed(1)}ms</td><td>${c.frame.max.toFixed(1)}ms</td><td>${c.longTasks.length}</td></tr>`).join('')}</table><h2>尚未完成</h2><ul>${next.map(s=>`<li>${esc(s)}</li>`).join('')}</ul><p>原版素材未改动；86份本轮修改前源码备份哈希通过。测试浏览器已确认关闭，复用的5180预览服务保留。微信继续按要求跳过。</p><p><a href="report.json">完整结果与源码哈希</a> · <a href="rule-regressions.json">49组回归</a> · <a href="screens/runtime.json">51个画面记录</a> · <a href="native-source.json">原版入口与常量证据</a></p></html>`;
await fs.writeFile(dir+'/report.html',html);console.log({passed:true,sourceChanges:changes.length,rules:rules.count,visualCases:visual.results.length,screens:screens.steps.length,allRecordedBrowsersClosed:true,report:dir+'/report.html'});
