import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const dir='reports/game-recheck-20261012',read=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const before=await read(dir+'/runtime.json'),after=await read(dir+'/after/runtime.json');
const rules=await read(dir+'/rule-regressions.json'),critical=await read(dir+'/critical-flows.json');
const gallery=await read(dir+'/feature-cache-playtest.json'),galleryBefore=await read(dir+'/feature-cache-before.json');
const revival=await read(dir+'/revival-resource-playtest.json'),revivalBefore=await read(dir+'/revival-resource-before.json');
const portal=await read(dir+'/portal-navigation-tests.json'),questBefore=await read(dir+'/quest-house-before.json');
const mini=await read('reports/audit-fixes-20261012/minimap-cache-playtest.json');
const verify=await read('reports/verification.json'),visibility=await read('reports/map-visibility-tests.json');
const progress=await read('reports/audit-fixes-20261012/progress.json');
for(const result of [rules,critical,gallery,revival,portal,mini,verify,visibility])assert.equal(result.passed,true);
const snapshotCounts=a=>({snapshots:a.steps.length,pageErrors:a.errors.length,failedRequests:a.requests.length,missingImages:a.steps.reduce((n,s)=>n+s.missingImages.length,0),missingGlyphs:a.steps.reduce((n,s)=>n+s.missingGlyphs.length,0),truncatedTexts:a.steps.reduce((n,s)=>n+s.truncated.length,0)});
const afterCounts=snapshotCounts(after);for(const [key,value]of Object.entries(afterCounts))if(key!=='snapshots')assert.equal(value,0,key);

// Keep both the original audit and this round's source snapshot immutable.
const baselineFile='reports/whole-game-audit-20261012/findings.json',baselineSha=sha(await fs.readFile(baselineFile));
assert.equal(baselineSha,progress.baselineSha256);
const sourceBefore=await read(dir+'/source-before.json'),sourceChanges=[];
for(const row of sourceBefore.files){
 const name=row.file.replace(/^src\//,'');assert.equal(sha(await fs.readFile(sourceBefore.backup+'/'+name)),row.sha256);
 const current=sha(await fs.readFile(row.file));if(current!==row.sha256)sourceChanges.push({file:row.file,beforeSha256:row.sha256,afterSha256:current});
}

const findings=[
 {id:'R01',status:'已修复',title:'角色属性漏掉最后两项',before:'23 项属性每页显示 7 项，但页数固定为 3，时间挑战记录和通关次数无法看到。',change:'根据实际属性数计算页数，当前显示 4 页，翻页循环正常。',files:['src/game.js'],evidence:['after/375-09-attributes-4.png','character-last-stats-375.png','critical-flows.json']},
 {id:'R02',status:'已修复',title:'开场回到屋内后，任务找村长会丢失目标',before:'原版开场把玩家送到海曦村屋内 (138,12)。导航到门口后，同地图传送将玩家放到 (64,72)，但目标被清空，不能继续走到村长。',change:'NPC 导航识别原版同地图门户，经过出口后继续原 NPC 目标。玩家主动移动可以取消，其他地图门户和非法落点不作为捷径。',files:['src/pathfinding.js','src/game.js'],evidence:['quest-house-before.json','quest-house-before.png','portal-navigation-tests.json','chief-after-house-375.png','critical-flows.json']},
 {id:'R03',status:'已修复',title:'图鉴翻页积累贴图，并会回收当前预览',before:'连续查看第 1、21、41、61、81、101 页，估算 RGBA 贴图数据从约 223 MiB 增至 435 MiB。缓存压力下当前 5 个模型全部被回收。',change:'将当前图鉴、宠物和守城单位预览纳入加载与保留集合，翻页回收闲置贴图；返回列表补加载，旧页异步加载完成后不能覆盖新页。',files:['src/permanent-ui.js','src/game.js','src/consumables.js'],evidence:['feature-cache-before.json','collection-cache-before.png','feature-cache-playtest.json','collection-cache-fixed-375.png']},
 {id:'R04',status:'已修复',title:'回城复活首帧缺建筑和植物',before:'先加载上次在城里的位置，再移动到原版复活点。在缓存压力下首帧缺失 5 个地图贴图页。',change:'按记住的主城和原版复活点加载，在最终位置的场景准备完成后恢复操作并保存。',files:['src/game.js'],evidence:['revival-resource-before.json','revival-resource-before.png','revival-resource-playtest.json','revival-ready-A00-375.png','revival-ready-K00-430.png']},
 {id:'R05',status:'已修复',title:'换图和复活后残留旧场景伤害数字',before:'伤害飘字按寿命保留，换图和复活没有清空，会短暂出现在新场景的错误坐标。',change:'切换地图、同图传送和复活清空旧飘字；新场景的伤害数字仍按实际受击位置显示。',files:['src/combat.js'],evidence:['revival-ready-A00-375.png','revival-resource-playtest.json','../death-tests.json']}
 ];

const lifecycleDir='reports/audit-fixes-20261012/lifecycle',lifecycle=[];
for(const file of await fs.readdir(lifecycleDir)){if(!file.endsWith('.json'))continue;const state=await read(lifecycleDir+'/'+file);assert.equal(state.closed,true,file);assert.equal(state.exitCode,0,file);lifecycle.push(state);}
const report={
 title:'小小传奇：整体复查与查漏补缺',updatedAt:new Date().toISOString(),passed:true,fullOriginalEquivalent:false,
 scope:{design:[750,1624],browserViewports:[{width:375,height:812},{width:430,height:932}],surfaces:['首页、三职业创角、原版开场','背包、角色四页属性、技能、任务和战斗 HUD','原版小地图和二级地图弹窗','开悟、图鉴、商店和仓库','10 个代表场景、远程施法画面、死亡与主城复活'],method:after.method,naturalOpeningAndFirstQuestPassed:true,entireCampaignManuallyCompleted:false,wechatSkippedAtUserRequest:true},
 findings,
 verification:{buildPassed:true,assetsAndExeHashesVerified:verify.passed,ruleSuites:rules.count,ruleSuitesPassed:rules.passed,ruleReport:dir+'/rule-regressions.json',before:snapshotCounts(before),after:afterCounts,criticalFlowViewports:critical.checks.length,criticalFlowReport:dir+'/critical-flows.json',portalChecks:portal.checks.length,collectionCacheViewports:gallery.cases.length,revivalFirstFrameCases:revival.cases.length,revivalMissingTexturePages:revival.cases.reduce((n,c)=>n+c.missing.length,0),revivalRemainingDamageText:revival.cases.reduce((n,c)=>n+c.remainingDamageText,0),nativeMinimapPressureCases:mini.cases.filter(c=>c.visual).length,intentionalMinimapFallbackCases:mini.cases.filter(c=>c.fallback).length,mapVisibilityMaps:visibility.maps,mapVisibilityViews:visibility.checkedViews},
 observations:{openingHouseBefore:questBefore,collectionBeforeRgbaBytes:galleryBefore.rows.map(r=>({page:r.page,bytes:r.bytes})),collectionAfterRgbaBytes:gallery.cases[0].rows.map(r=>({page:r.page,bytes:r.bytes})),cacheBudgetIsNotHardProcessMemoryLimit:true,revivalBeforeMissingTexturePages:revivalBefore.missing.length},
 remaining:progress.findings.filter(f=>f.status==='部分完成').map(f=>({id:f.id,title:f.title,detail:f.detail})),
 limits:['整条剧情尚未人工从头通关；脚本采样和规则检查不能证明所有剧情条件组合都完成。','其余通用粒子、天气及死亡/传送特效仍需逐入口对照。','部分特殊攻击的弹体寿命、碰撞和范围剑法仍未证明逐帧原版等价。','专家/地狱的条件物品和掉落分支仍需补齐。','移动长帧仍需继续定位；本轮软件 WebGL 画面检查不能证明硬件实机稳定 60 FPS。'],
 preservation:{originalAudit:baselineFile,originalAuditSha256:baselineSha,originalAuditUnchanged:true,sourceBackup:sourceBefore.backup,sourceBackupFiles:sourceBefore.files.length,sourceBackupUnchanged:true,sourceChanges},
 processLifecycle:{allRecordedOwnedBrowsersClosed:true,records:lifecycle,existingPreview:'127.0.0.1:5180 was already running, reused and preserved; no new development server was left running.'}
};
await fs.writeFile(dir+'/findings.json',JSON.stringify(report,null,2));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const cards=findings.map(f=>`<article><h2>${esc(f.title)} <span>已修复</span></h2><p>${esc(f.before)}</p><p>${esc(f.change)}</p><p>${f.evidence.map(file=>`<a href="${esc(file)}">${esc(file.split('/').at(-1))}</a>`).join(' · ')}</p></article>`).join('');
const limits=report.limits.map(s=>`<li>${esc(s)}</li>`).join('');
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(report.title)}</title><style>body{max-width:1080px;margin:32px auto;padding:0 22px;background:#f5f1e8;color:#30261e;font:16px/1.65 system-ui}h1{font-size:28px}h2{font-size:20px}article{border-top:1px solid #d6c8b2;padding:12px 0}h2 span{font-size:14px;color:#386d3b}a{color:#765426}figure{display:inline-block;vertical-align:top;margin:20px 14px 12px 0;width:30%;min-width:240px}img{width:100%;border:1px solid #b7a285}figcaption{font-size:14px}li{margin:8px 0}.metrics{padding:18px;background:#e9dfcd}</style><h1>${esc(report.title)}</h1><p>更新于 ${esc(report.updatedAt)}。本轮修复 5 项实际问题；原版完整等价尚未成立，微信按用户要求跳过。</p><p class="metrics">构建、素材与 EXE 哈希核对通过。${rules.count} 组规则检查全部通过；修复后 ${afterCounts.snapshots} 个画面检查缺图、缺字、文字裁切和浏览器错误均为 0。开场恢复、找村长、北门出村、买卖和仓库存取通过两种尺寸验证；四个主城共 ${revival.cases.length} 组复活首帧检查通过。</p><p>图鉴连续翻页的估算 RGBA 数据由约 435 MiB 降到 278 MiB，并验证当前预览在缓存压力下保留。该数值是贴图数据估算，不等于浏览器进程总内存；缓存预算也不是硬上限。</p>${cards}<figure><img src="character-last-stats-375.png"><figcaption>角色属性第 4 页</figcaption></figure><figure><img src="chief-after-house-375.png"><figcaption>从开场屋内自动找村长</figcaption></figure><figure><img src="revival-ready-A00-375.png"><figcaption>按原版地点复活，场景与飘字检查</figcaption></figure><h2>仍待继续还原</h2><ul>${limits}</ul><p>本轮已关闭全部自建测试浏览器；保留原有 5180 预览服务。原始审计报告与本轮 86 文件源码备份均已核对未改动。</p><p><a href="findings.json">完整记录</a> · <a href="after/runtime.json">修复后画面检查</a> · <a href="rule-regressions.json">规则回归</a> · <a href="../audit-fixes-20261012/progress.html">累计修复进度</a></p></html>`;
await fs.writeFile(dir+'/findings.html',html);
console.log({passed:true,fixed:findings.length,snapshots:afterCounts.snapshots,ruleSuites:rules.count,sourceChanges:sourceChanges.map(c=>c.file),allRecordedOwnedBrowsersClosed:true,originalAuditUnchanged:true});
