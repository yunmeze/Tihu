import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const dir='reports/hero-hurt-20261013',backup='backups/hero-hurt-20261013-before';
const read=async f=>JSON.parse(await fs.readFile(f,'utf8')),sha=async f=>crypto.createHash('sha256').update(await fs.readFile(f)).digest('hex');
const previous=await read(backup+'/reports/latest-restoration.json'),native=await read(dir+'/native-evidence.json'),targeted=await read(dir+'/targeted-tests.json'),browser=await read(dir+'/playtest.json'),rules=await read(dir+'/rule-regressions.json'),ui=await read('reports/playtest.json');
assert.ok(native.passed&&targeted.passed&&browser.passed&&ui.passed);
assert.deepEqual(rules.results.filter(r=>!r.passed).map(r=>r.file),['ui-tests.mjs']);
const retryLog=await fs.readFile(dir+'/ui-rerun.log','utf8');assert.ok(retryLog.includes('fulfilled tools/ui-tests.mjs')&&retryLog.includes('port open: false'));
const finalRules={passed:true,count:rules.count,results:rules.results.map(r=>({file:r.file,passed:r.file==='ui-tests.mjs'?ui.passed:r.passed,retried:r.file==='ui-tests.mjs'})),firstRun:'rule-regressions.json',retry:'ui-rerun.log',retryReason:'Preview was not running when the UI suite reached page.goto; rerun under owned preview succeeded.'};
await fs.writeFile(dir+'/final-regressions.json',JSON.stringify(finalRules,null,2));
const verification=await read('reports/verification.json');assert.ok(verification.passed);await fs.copyFile('reports/verification.json',dir+'/verification.json');
const lifecycle=await read(dir+'/lifecycle.json');assert.ok(lifecycle.closed);
const changed=[];for(const file of ['src/animation.js','src/combat.js','README.md','tools/appearance-tests.mjs','tools/movement-optimization-tests.mjs']){const backupFile=backup+'/'+(file.startsWith('tools/')?file.slice(6):file);changed.push({file,backupFile,before:await sha(backupFile),after:await sha(file)});}
const remaining=[
 '普通数值新角色的主支线完整顺序通关，以及专家/地狱完整流程。',
 '范围攻击、弹体寿命和碰撞占位的逐分支对照。',
 '受击音效与魔法盾反馈、反弹结算及麻痹跨状态时钟的逐帧对齐；本轮完成动作门槛和序列节奏。',
 '通用粒子6、10–16的原版实际发射入口与地图旗标。',
 '特殊条件掉落倍率与后期物品获取链。',
 '复杂场景和密集长时战斗的硬件WebGL复测；本轮使用软件渲染，不作硬件帧率结论。'
];
const report={date:new Date().toISOString(),title:'主角受击动作接入',continuedFrom:{threadId:'01a11a72-d4ed-7f13-afcf-60d252c06f47',title:'评估游戏资产提取与 Web 复刻'},previous,backup,changed,nativeEvidence:'native-evidence.json',validation:{targeted:targeted.cases,regressionSuites:finalRules.count,browserCases:browser.cases,viewportWidths:[375,430],build:true,sourceVerification:true,assetManifestVersion:'1a3a10c9f7daa194',originalAssets:2210},lifecycle,remaining,fullNativeCombatEquivalent:false};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>小小传奇 · 主角受击动作</title><style>body{margin:0;background:#17130f;color:#e1d7c7;font:16px/1.8 system-ui,sans-serif}main{max-width:1060px;margin:auto;padding:32px 24px}h1,h2{color:#e7c587;line-height:1.4}.stats{display:flex;gap:24px;flex-wrap:wrap}.stats p{padding:16px 24px;background:#292016;border:1px solid #63513b}strong{color:#f0d294}a{color:#e5bd77}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}figure{margin:0}img{width:100%}figcaption{margin:10px 0 24px}li{margin:10px 0}.note{color:#bdb09d}@media(max-width:600px){.grid{grid-template-columns:1fr}}</style><main><p class="note">小小传奇 · 2026-10-13 · 接续原版还原</p><h1>主角受击动作</h1><p>敌方命中时，待机主角会播放原版八方向受击序列。行走、跑步、攻击与施法保留当前动作，连续命中不会把动画反复重置。</p><div class="stats"><p><strong>${targeted.cases}</strong> 项针对性检查</p><p><strong>${finalRules.count}</strong> 组回归</p><p><strong>${browser.cases}</strong> 项浏览器检查</p></div><h2>本轮还原</h2><ul><li>原EXE两条命中路径都检查动作值1（待机），再进入动作225（受击）；护身戒指吸收生命伤害后仍到达该门槛。</li><li>普通时钟第5/10/15帧显示三张原受击帧，第20帧恢复；冻结分别为第6/12/18/24帧。首帧前保留原姿态，身体、头部、武器和翅膀共用索引。</li><li>闪避、反弹分支、毒与灼烧的直接扣血不启动受击；致死进入死亡。自动反击等待恢复，已经开始的攻击照常释放。</li><li>受击期间真实点击场景可以排入移动路线，恢复后继续；系统菜单暂停受击时钟。</li></ul><h2>原场景截图</h2><div class="grid">${[0,1,2].map(i=>`<figure><a href="hurt-430-${i}.png"><img src="hurt-430-${i}.png" alt="第${i+1}张受击帧"></a><figcaption>第${i+1}张受击帧 · ${(i+1)*.1}秒</figcaption></figure>`).join('')}</div><h2>验证与边界</h2><p>原EXE校验18个指令锚点；两种竖屏尺寸为375×812与430×932。测试使用独立浏览器上下文、受控敌人与高HP夹具，不更改用户存档。构建和原版来源检查通过，资源清单版本保持一致。</p><p>移动优化回归改为在同一套当前战斗规则中比较优化前后的AI，继续逐帧核对完整状态。首次UI回归因缺少预览服务失败，已由受控服务单独重跑通过，原失败记录保留。</p><p class="note">音效和护盾仍在Web命中时点反馈；反弹结算、麻痹跨状态时钟和恢复后的待机换帧仍有原版逐帧差异。此轮完成受击动作入口及序列节奏，完整战斗等价标记保持false。浏览器为软件WebGL，未验证微信真机。</p><h2>仍待继续</h2><ul>${remaining.map(s=>`<li>${s}</li>`).join('')}</ul><h2>可复核记录</h2><p><a href="native-evidence.json">原版证据</a> · <a href="targeted-tests.json">专项检查</a> · <a href="final-regressions.json">最终回归</a> · <a href="playtest.json">浏览器验证</a> · <a href="verification.json">资源校验</a> · <a href="lifecycle.json">进程关闭记录</a> · <a href="report.json">完整记录</a></p><p class="note">备份：${backup}。测试浏览器与临时预览服务均已结束。</p></main></html>`;
await fs.writeFile(dir+'/report.html',html);
await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next:remaining},null,2));
console.log({passed:true,targeted:targeted.cases,regressions:finalRules.count,browser:browser.cases,report:dir+'/report.html'});
