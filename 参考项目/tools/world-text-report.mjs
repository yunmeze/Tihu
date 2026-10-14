import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const dir='reports/world-text-20261013',backup='backups/world-text-20261013-before';
const read=async f=>JSON.parse(await fs.readFile(f,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const targeted=await read(dir+'/targeted-tests.json'),rules=await read(dir+'/rule-regressions.json'),browser=await read(dir+'/playtest.json'),verification=await read('reports/verification.json'),build=await read('reports/build.json');
for(const [name,value]of Object.entries({targeted,rules,browser,verification}))if(!value.passed)throw Error(name+' not passed');
const before=await read(backup+'/public/assets/manifest.json'),after=await read('public/assets/manifest.json'),source=await read(backup+'/source.json'),changed=[];
if(Object.keys(before.files).length!==Object.keys(after.files).length)throw Error('Asset count changed');
for(const [file,entry]of Object.entries(before.files))if(entry.sha256!==after.files[file]?.sha256)throw Error('Asset changed: '+file);
for(const entry of source.files){if(sha(await fs.readFile(path.join(backup,entry.file)))!==entry.sha256)throw Error('Backup mismatch: '+entry.file);const current=sha(await fs.readFile(entry.file));if(current!==entry.sha256&&entry.file!=='reports/latest-restoration.json')changed.push({file:entry.file,before:entry.sha256,after:current});}
const lifecycle={browser:await read('reports/audit-fixes-20261012/lifecycle/world-text-after-20261013.json'),baseline:await read('reports/audit-fixes-20261012/lifecycle/world-text-before-20261013.json'),logs:['final-tests.log','final-regressions.log']};
if(!lifecycle.browser.closed||!lifecycle.baseline.closed)throw Error('Browser cleanup not confirmed');
for(const file of lifecycle.logs){const log=await fs.readFile(dir+'/'+file,'utf8');if(!log.includes('Owned preview stopped; port open: false'))throw Error('Preview cleanup not confirmed: '+file);}
await fs.writeFile(dir+'/lifecycle.json',JSON.stringify(lifecycle,null,2));
await fs.copyFile('reports/verification.json',dir+'/verification.json');await fs.copyFile('reports/build.json',dir+'/build.json');
const changes=[
 {title:'场景文字共同避让',text:'怪物/NPC名称、可选血条、飘字和掉落标签共用占位与优先级，避开小地图、左右交互列表、状态按钮及底部栏。当前目标的名称与血条一起移动，原版开悟的显隐开关继续生效。'},
 {title:'镜头与战斗时钟',text:'文字保留相对世界锚点的可用偏移，小数位镜头移动保持连续。伤害飘字仍由实际命中时刻、原有持续时间和透明度驱动；角色/怪物/弹体的坐标与伤害公式未改。文字宽度容差修正末字在小数游标下漏绘。'},
 {title:'多堆掉落可读',text:'同一格的掉落显示一个代表物品名和“等N堆”，任务材料、当前拾取目标及装备实例优先。原有物品ID、数量、图标和强化信息全部保留。标签在场景合成后以逻辑分辨率绘制，树木不再挡住掉落名称。'},
 {title:'名称点击与部分拾取',text:'挪动后的掉落名称对应原掉落ID，可以点名称走过去拾取；长按名称不会转成持续移动。背包满时未捡的物品留在地上，已拾取堆数与名称及时更新。注灵武器的原图标和完整名称跨显示层与拾取仍一致。'},
];
const next=[
 '普通数值新角色的主支线完整顺序通关；分段夹具不能替代完整通关。',
 '主角受击动作的原版触发条件，以及范围攻击、弹体寿命和碰撞占位的逐分支对照。',
 '通用粒子6、10–16的原版实际发射入口与地图旗标。',
 '特殊条件掉落倍率、后期物品获取链及专家/地狱完整流程。',
 '复杂场景与极密长时战斗的硬件WebGL复测，包含文字层和移动长帧；本轮不作硬件帧率结论。',
];
const limits=[
 '屏幕空间不足时，部分低优先级普通名称或掉落标签暂不显示；地面图标、掉落数据和左右交互入口仍保留。',
 '浏览器使用高HP、全部开悟和受控掉落的独立夹具，验证两种竖屏尺寸及真实点击/移动/拾取；不是普通角色完整通关。',
 '九个同时伤害飘字的密集原场景已验证，超出该密度的长时性能与硬件GPU仍待测试。',
 '微信部署与资源重绘按用户要求暂缓。完整战斗/数值逐分支等价标记继续保持false。',
];
const images=[
 ['before-dense-430.png','修改前：蛙统领周围的掉落、名字和伤害叠在一起'],
 ['after-dense-430.png','修改后：同一原场景，目标、伤害与掉落避让'],
 ['picked-group-430.png','点击挪动后的装备名，走到原落点拾取三堆物品'],
 ['after-village-430.png','海曦村：箱子、NPC名称与小地图及交互列避让'],
 ['bag-view-375.png','背包页：场景文字避开系统界面边界'],
 ];for(const [file]of images)await fs.access(dir+'/'+file);
const report={date:new Date().toISOString(),title:'场景文字与多堆掉落交互修复',backup,backupVerified:true,previous:await read(backup+'/reports/latest-restoration.json'),changed,
 addedRuntime:['src/world-label-layout.js','src/world-text-renderer.js'],updatedTests:['tools/parity-restoration-tests.mjs'],source:{existingAssetsUnchanged:Object.keys(before.files).length,manifestVersion:build.manifestVersion,sourceHashVerification:verification.passed},changes,
 tests:{targeted:{passed:true,count:targeted.cases,file:'targeted-tests.json'},regressions:{passed:true,count:rules.count,file:'rule-regressions.json'},browser:{passed:true,count:browser.results.length,widths:[...new Set(browser.results.map(r=>r.width))],file:'playtest.json',scope:browser.scope},build:{passed:true,file:'build.json'},verification:{passed:true,file:'verification.json'},visualReview:images.map(([file,caption])=>({file,caption,reviewed:true})),lifecycle:{closed:true,file:'lifecycle.json'}},limits,next};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>小小传奇 · 场景文字验证</title><style>body{margin:0;background:#17130f;color:#dfd5c2;font:16px/1.8 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:36px 22px}h1,h2,h3{color:#e1bf78;line-height:1.4}h1{font-size:30px}a{color:#dbb674}.cards{display:flex;gap:18px;flex-wrap:wrap}.cards div{padding:16px 24px;border:1px solid #665334;background:#241d16;border-radius:8px}.cards strong{display:block;font-size:30px;color:#eac47b}section{margin-top:34px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px}article,figure{margin:0;padding:18px;border:1px solid #514432;background:#211b15;border-radius:8px}figure img{width:100%;max-height:750px;object-fit:contain;background:#110e0b}figcaption{margin-top:14px;color:#c5b695}li{margin:10px 0}.note{color:#b9ab92}.links{display:flex;gap:18px;flex-wrap:wrap}</style><main><p class="note">小小传奇 · 2026-10-13 · 原版还原继续</p><h1>密集场景文字与掉落名称</h1><p>目标、伤害数字和掉落名称共同避让；同格多堆显示堆数，并支持点击移动后的名称走近拾取。</p><div class="cards"><div><strong>${targeted.cases}</strong>针对性规则通过</div><div><strong>${rules.count}</strong>回归测试组通过</div><div><strong>${browser.results.length}</strong>浏览器检查通过</div><div><strong>0</strong>原有资源修改</div></div><p class="note">375×812、430×932；原有${report.source.existingAssetsUnchanged}个资源文件哈希一致。测试使用独立夹具和高HP，未改变用户存档。</p><section><h2>本轮实现</h2><div class="grid">${changes.map(s=>`<article><h3>${escape(s.title)}</h3><p>${escape(s.text)}</p></article>`).join('')}</div></section><section><h2>实景前后与交互复核</h2><div class="grid">${images.map(([f,c])=>`<figure><a href="${f}"><img src="${f}" loading="lazy" alt="${escape(c)}"></a><figcaption>${escape(c)}</figcaption></figure>`).join('')}</div></section><section><h2>验证边界</h2><ul>${limits.map(s=>`<li>${escape(s)}</li>`).join('')}</ul></section><section><h2>仍待还原与验收</h2><ul>${next.map(s=>`<li>${escape(s)}</li>`).join('')}</ul></section><section><h2>可复核记录</h2><div class="links">${[['report.json','完整报告'],['targeted-tests.json','针对性规则'],['rule-regressions.json','53组回归'],['playtest.json','浏览器检查'],['verification.json','原版来源校验'],['lifecycle.json','进程关闭记录'],['final-regressions.log','最终回归日志']].map(([f,l])=>`<a href="${f}">${l}</a>`).join('')}</div><p class="note">备份：${backup}。测试创建的浏览器与预览服务器已关闭，回归结束确认5180端口未监听。</p></section></main></html>`;
await fs.writeFile(dir+'/report.html',html);await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next},null,2));
console.log({passed:true,targeted:targeted.cases,regressionSuites:rules.count,browserCases:browser.results.length,report:dir+'/report.html'});
