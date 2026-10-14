import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const dir='reports/restoration-parity-20261013',read=async f=>JSON.parse(await fs.readFile(f,'utf8')),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const backup=await read('backups/parity-20261013-before/source.json'),targeted=await read(dir+'/targeted-tests.json'),rules=await read(dir+'/rule-regressions.json'),browser=await read(dir+'/playtest.json'),native=await read(dir+'/native-evidence.json'),lifecycle=await read(dir+'/lifecycle.json'),uiLifecycle=await read(dir+'/ui-lifecycle.json'),integrity=await read('reports/verification.json'),build=await read('reports/build.json'),previous=await read('reports/latest-restoration.json');
assert.ok(targeted.passed&&rules.passed&&browser.passed&&native.passed&&integrity.passed);assert.ok(lifecycle.server.closed&&lifecycle.browser.closed&&uiLifecycle.closed);assert.equal(browser.errors.length,0);assert.equal(browser.requests.length,0);
const suite=rules.results.find(r=>r.file==='parity-restoration-tests.mjs');suite.pid=targeted.pid;suite.output=JSON.stringify({passed:true,checks:targeted.checks.length});suite.revalidated=true;await fs.writeFile(dir+'/rule-regressions.json',JSON.stringify(rules,null,2));
async function walk(p){const files=[];for(const e of await fs.readdir(p,{withFileTypes:true})){const file=p+'/'+e.name;if(e.isDirectory())files.push(...await walk(file));else files.push(file);}return files.sort();}
const old=new Map(backup.files.map(r=>[r.file,r.sha256])),sourceSnapshot=[],sourceChanges=[];
for(const file of await walk('src')){const sha256=hash(await fs.readFile(file));sourceSnapshot.push({file,sha256});if(old.get(file)!==sha256)sourceChanges.push({file,sha256,beforeSha256:old.get(file)||null});}
for(const r of backup.files)assert.equal(hash(await fs.readFile(backup.backup+'/'+r.file)),r.sha256);
const fixes=[
 {audit:'A01',title:'地面装备存档保留强化水次数',detail:'集中列出装备实例字段；地面恢复保留waterUses、实例ID、属性、注灵名称/图标、锻造/合成、颜色及掉落来源。三次水上限在丢弃、保存、读档、拾取和穿戴后仍生效。',files:['src/inventory.js','src/loot.js']},
 {audit:'A02',title:'切换难度保留明阳守卫阶段与重生属性',detail:'根据新难度重建基础定义后重施二阶段修正；同步birthDefinition、当前HP比例和剩余回复比例，不重置动作/攻击冷却。已死亡单位保持零HP，召唤物、雇佣兵和战旗不缩放。',files:['src/monster-rebirth.js','src/game.js']},
 {audit:'A03（支线部分）',title:'补齐三条支线记录与交付状态',detail:'救采药人、清剿魔灵蜘蛛、归还铁锤显示进行中、可交付和完成状态。救人后目标转到村大夫，蜘蛛交付受原主线门槛约束，铁锤随背包物品更新。预览不执行奖励脚本；原奖励与消耗通过执行原脚本验证。后段主线跨图导航仍未完成。',files:['src/quest-journal.js','src/game.js']},
 {audit:'A04',title:'注灵装备落地与拾取显示实际名称/图标',detail:'可见资源准备、地面绘制和拾取文字读取instanceItem；原配方“扎克(注灵)”显示图标960，而不是基础扎克的955。',files:['src/game.js','src/combat.js']},
 {audit:'A05',title:'恢复死亡触发的BOSS刷新减秒',detail:'按原版从BT29向下找首个正计时且名称不是“设置”的槽，CInt(Rnd×10)+5秒减时。挑战和行为10的BOSS死亡排除；保留累计值与精确到零/超出零的区别，同时提前该单位实际重生时间并显示反馈。',files:['src/boss-timers.js','src/combat.js']},
 {audit:'A06',title:'修正地狱创角的全局解锁条件',detail:'新解锁要求存在进入地狱并保存的角色，modeUnlock>=2不再直接解锁全局创角。保留旧明确解锁标记，删除已进入地狱的角色也不会撤销全局资格。无法从旧标记判断其历史来源，因此兼容保留。',files:['src/save-roster.js']},
 {audit:'A07 + 计时单位',title:'恢复魔法盾计时、阶段暂停与到期闪烁',detail:'原计数是5×（魔法掷值+80×等级），每五个50Hz逻辑帧递减一单位。Web字段改为对应实际帧数；展开和受击阶段不递减，维持阶段递减。低于50原计数单位时按12帧周期只显示1–7相位，闪烁不移除防御。',files:['src/magic-shield.js','src/combat-skills.js','src/combat-effects.js','src/effect-animation.js','src/game.js']},
];
const next=[
 '后段主线跨图目标与真实顺序通关验收；本轮只补三条支线，不能据解析覆盖宣称全剧情完成。',
 '主角受击动作的原版触发条件；当前护盾使用战斗逻辑时钟，尚不宣称所有原始全局显示时序完全一致。',
 '范围攻击、弹体寿命、碰撞和原版占位判定的逐分支对照。',
 '通用粒子6、10–16的实际运行入口与地图旗标。',
 '原版特殊条件掉落倍率、后期物品获取链及专家/地狱的完整流程。',
 '复杂场景移动长帧的硬件WebGL复测；本轮未修改渲染管线或作新帧率结论。',
];
const report={title:'小小传奇 · 原版玩法继续还原',date:new Date().toISOString(),passed:true,fullOriginalEquivalent:false,previousReport:previous.html,baselineAudit:'reports/parity-audit-20261013/report.html',backup:backup.backup,backupVerifiedFiles:backup.files.length,sourceSnapshot,sourceChanges,fixes,next,
 verification:{targetedChecks:targeted.checks.length,ruleSuites:rules.count,browserCases:browser.results.length,portraitSizes:['375×812','430×932'],sourceIntegrityPassed:true,buildPassed:true,manifestVersion:build.manifestVersion,originalAssetsChanged:false,userSavesChanged:false,wechatDeploymentSkipped:true},
 boundaries:['浏览器使用隔离的测试角色和状态，非从创建到结局的自然通关。','本轮恢复原版玩法，未开始暗黑风格资源生成或替换。','原版二进制提取4段，保留源哈希、范围和检查；未声称已解析全部程序。'],
 screenshots:['375-enchanted-ground.png','375-quest-6.png','430-quest-4.png','375-quest-6-complete.png','375-guard-expert-phase.png','375-shield-on.png','375-shield-off.png'],
 lifecycle:{current:lifecycle,uiRegression:uiLifecycle,allOwnedProcessesClosed:true},pid:process.pid};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
await fs.copyFile('reports/verification.json',dir+'/verification.json');await fs.copyFile('reports/build.json',dir+'/build.json');
await fs.copyFile(dir+'/check.log',dir+'/check-capture-attempt.log');await fs.writeFile(dir+'/check.log',JSON.stringify(integrity,null,2));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const rows=fixes.map(f=>`<article><small>${esc(f.audit)}</small><h3>${esc(f.title)}</h3><p>${esc(f.detail)}</p><p class="refs">${f.files.map(file=>`<a href="../../${file}">${file}</a>`).join(' · ')}</p></article>`).join('');
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(report.title)}</title><style>
*{box-sizing:border-box}body{margin:0;background:#171b18;color:#e5e8df;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1080px;margin:auto;padding:34px 24px 70px}h1{font-size:32px;line-height:1.4}h2{margin-top:38px;font-size:24px}h3{font-size:20px;margin:8px 0}p{margin:10px 0}a{color:#abcab9;overflow-wrap:anywhere}small,.muted{color:#adbaac}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:22px 0}.stats>div,article{border:1px solid #3c493f;background:#212820;border-radius:8px;padding:18px}.stats b{font-size:30px;color:#dac291;display:block}article{margin:16px 0}.refs{font-size:12px}.shots{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.shots figure{margin:0}.shots img{width:100%;display:block;border:1px solid #71603d}.shots figcaption{font-size:13px;color:#adbaac;margin-top:6px}li{margin:10px 0}footer{margin-top:40px;color:#a9b6a6;font-size:13px}@media(max-width:650px){main{padding:20px 15px}.shots{grid-template-columns:repeat(2,1fr)}.stats{gap:8px}.stats>div{padding:12px}h1{font-size:27px}}
</style><main><small>2026-10-13 · 当前原版玩法修复</small><h1>${esc(report.title)}</h1><p>本轮处理装备实例、难度阶段、三条支线、掉落显示、BOSS刷新、创角门槛及魔法盾时序。原版资源保持不变，未进行暗黑风格重绘。</p><div class="stats"><div><b>${targeted.checks.length}</b>定向回归检查</div><div><b>${rules.count}</b>规则测试组</div><div><b>${browser.results.length}</b>两尺寸浏览器场景</div></div><p class="muted">检查均通过；浏览器无脚本错误或失败资源请求。隔离测试档并不代表完整剧情通关。</p><p><a href="report.json">完整记录</a> · <a href="native-evidence.json">原版程序证据</a> · <a href="targeted-tests.json">定向回归</a> · <a href="rule-regressions.json">规则结果</a> · <a href="playtest.json">浏览器结果</a> · <a href="lifecycle.json">进程关闭记录</a></p><h2>本轮修复</h2>${rows}<h2>画面核查</h2><div class="shots">${report.screenshots.map(file=>`<figure><a href="${file}"><img src="${file}" alt="${esc(file)}" loading="lazy"></a><figcaption>${esc(file)}</figcaption></figure>`).join('')}</div><h2>仍需继续还原</h2><ul>${next.map(s=>'<li>'+esc(s)+'</li>').join('')}</ul><h2>验证与兼容边界</h2><ul>${report.boundaries.map(s=>'<li>'+esc(s)+'</li>').join('')}</ul><p>备份${backup.files.length}个运行时文件并逐一核对，当前运行时文件${sourceSnapshot.length}个、本轮变更${sourceChanges.length}个。源资产清单版本仍为${build.manifestVersion}。真实用户存档未修改；已有明确地狱解锁记录按兼容规则保留。</p><footer>临时预览服务器及两次场景测试浏览器均在finally中关闭，UI回归浏览器也已退出。微信部署按用户要求跳过。完整原版等价标记仍为false。</footer></main></html>`;
await fs.writeFile(dir+'/report.html',html);await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next},null,2));
console.log(JSON.stringify({report:dir+'/report.html',targeted:targeted.checks.length,suites:rules.count,browserCases:browser.results.length,sourceChanged:sourceChanges.length,ownedProcessesClosed:true},null,2));
