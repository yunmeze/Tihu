import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const dir='reports/main-quest-restoration-20261013',backup='backups/main-quest-20261013-before',read=async f=>JSON.parse(await fs.readFile(f,'utf8')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const targeted=await read(dir+'/targeted-tests.json'),rules=await read(dir+'/rule-regressions.json'),playtest=await read(dir+'/playtest.json'),verification=await read('reports/verification.json'),build=await read('reports/build.json'),lifecycle=await read(dir+'/lifecycle.json');
for(const [name,r]of Object.entries({targeted,rules,playtest,verification}))if(!r.passed)throw Error(name+' has not passed');if(!lifecycle.server.closed||!lifecycle.browser.closed)throw Error('Owned playtest processes not closed');
const before=await read(backup+'/public/assets/manifest.json'),after=await read('public/assets/manifest.json'),source=await read(backup+'/source.json'),changed=[];
for(const f of Object.keys(before.files))if(before.files[f].sha256!==after.files[f]?.sha256)throw Error('Unexpected original asset change: '+f);
for(const f of source.files){const bytes=await fs.readFile(f.file),current=sha(bytes);if(current!==f.sha256&&f.file!=='public/assets/manifest.json'&&f.file!=='reports/latest-restoration.json')changed.push({file:f.file,before:f.sha256,after:current});if(sha(await fs.readFile(path.join(backup,f.file)))!==f.sha256)throw Error('Backup mismatch: '+f.file);}
const next=[
 '普通数值新角色的主支线完整顺序通关；目标接通与分段夹具验证不能替代完整通关。',
 '密集怪物和多堆掉落的文字仍会拥挤，本轮药材实景截图可见；需继续处理标签重叠。',
 '主角受击动作的原版触发条件，以及范围攻击、弹体寿命和碰撞占位的逐分支对照。',
 '通用粒子6、10–16的原版实际发射入口与地图旗标。',
 '特殊条件掉落倍率、后期物品获取链及专家/地狱完整流程。',
 '复杂场景移动长帧的硬件WebGL复测；本轮优化导航计算和点选拾取，未作新的帧率保证。',
];
const sections=[
 {title:'28阶段主线目标',text:'依据Mstm.dat、NPC脚本和怪物死亡/掉落脚本确定目标。药材按两种材料的持有情况切换来源，灵珠按三种颜色分别检查；腰带内物品也计入。地上缺失的任务物品优先成为拾取目标。'},
 {title:'沿原版出口连续寻路',text:'从155张地图提取出口与9个无条件传送NPC，约11.7KB。一个BFS检查多个出口，处理同图房屋入口，跨图后继续路线；运行时不批量加载所有地图。NPC到达后打开原对话，剧情选择和任务完成仍由原脚本执行。'},
 {title:'点选拾取保持目的地',text:'点选地面物品会退出挂机、取消待释放攻击并沿指定路径移动。行走期间反击不会改写这段主动移动路径，到达脚下才拾取。已发出的弹体保留原结算。'},
 {title:'剧情暂停时可走向NPC',text:'原版STOP仍禁止自由移动、战斗和道具操作；任务中的方丈/凌云子交互可以接近NPC，不解除剧情锁。开局原对话的UNSTOP和取玉石返回三清观后的结局原对话已实测。'},
];
const images=[
 ['north-task-375.png','开局地图任务页：目的地按钮使用原版HUD'],
 ['opening-original-dialogue-return-375.png','方丈与凌云子原对话后，返回海曦村'],
 ['medicine-next-source-430.png','拾取老蟾酥后目标切换为野猪牙；密集标签仍拥挤'],
 ['pearls-turn-in-430.png','三色灵珠交付：原版族长剧情与500金币奖励'],
 ['native-final-transfers-430.png','经原NPC进入死亡空间和金魔大殿'],
 ['final-abbot-375.png','镇墓玉石返回三清观后，与方丈对话'],
 ['native-ending-375.png','进入原版五页结局流程'],
];
for(const [file]of images)await fs.access(dir+'/'+file);
const rulesLog=await fs.readFile(dir+'/rules.log','utf8');if(!rulesLog.includes('Owned preview stopped; port open: false'))throw Error('Final regression preview cleanup not confirmed');
await fs.copyFile('reports/verification.json',dir+'/verification.json');await fs.copyFile('reports/build.json',dir+'/build.json');
const previous=await read(backup+'/reports/latest-restoration.json');
const report={date:new Date().toISOString(),title:'原版主线目标与收尾流程还原',previous,backup,backupVerified:true,changed,
 source:{exeSha256:'21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84',originalAssetsUnchanged:Object.keys(before.files).length,addedAssets:Object.keys(after.files).filter(f=>!before.files[f]),mapsSha256:targeted.generated.mapsSha256,manifestVersion:build.manifestVersion},
 changes:sections,tests:{targeted:{passed:true,count:targeted.checks,file:'targeted-tests.json'},regressions:{passed:true,count:rules.count,file:'rule-regressions.json'},browser:{passed:true,count:playtest.results.length,widths:[...new Set(playtest.results.map(r=>r.width))],file:'playtest.json',scope:playtest.scope},build:{passed:true,file:'build.json'},verification:{passed:true,file:'verification.json'},visualReview:images.map(([file,caption])=>({file,caption,reviewed:true})),lifecycle:{file:'lifecycle.json',playtestClosed:true,finalRegressionPreviewClosed:true,regressionLog:'rules.log'}},
 limits:['高等级/高属性与阶段化独立夹具验证，未进行普通新角色全流程顺序通关。','有条件的渡船和高级传送按钮保留原脚本交互方式，未作为本轮导航捷径。','截图中的超常HP数值属于耐久夹具，不用于普通角色UI结论。','微信部署及资源重绘按用户要求暂缓。'],next};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>小小传奇 · 主线还原验证</title><style>body{margin:0;background:#17130f;color:#dfd5c2;font:16px/1.8 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:36px 22px}h1,h2,h3{color:#e1bf78;line-height:1.4}h1{font-size:30px}a{color:#c9a267}.cards{display:flex;gap:18px;flex-wrap:wrap}.cards div{padding:16px 24px;border:1px solid #665334;background:#241d16;border-radius:8px}.cards strong{display:block;font-size:30px;color:#eac47b}section{margin-top:34px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px}article,figure{margin:0;padding:18px;border:1px solid #514432;background:#211b15;border-radius:8px}figure img{width:100%;max-height:740px;object-fit:contain;background:#110e0b}figcaption{margin-top:14px;color:#c5b695}li{margin:10px 0}.note{color:#b9ab92}.links{display:flex;gap:18px;flex-wrap:wrap}</style><main><p class="note">小小传奇 · 2026-10-13 · 原版资源与玩法继续还原</p><h1>主线目标、连续寻路与收尾剧情</h1><p>任务页接通28个原版阶段的目标，并修正点选拾取被反击改路、剧情暂停误挡NPC引导的问题。</p><div class="cards"><div><strong>${targeted.checks}</strong>针对性规则通过</div><div><strong>${rules.count}</strong>回归测试组通过</div><div><strong>${playtest.results.length}</strong>浏览器流程通过</div><div><strong>0</strong>原有资源改动</div></div><p class="note">两种竖屏尺寸：375×812、430×932。原有${report.source.originalAssetsUnchanged}个资源文件哈希一致；新增一个约11.7KB的地图导航索引。浏览器使用高等级、高属性和指定阶段的独立测试存档。</p><section><h2>本轮实现</h2><div class="grid">${sections.map(s=>`<article><h3>${escape(s.title)}</h3><p>${escape(s.text)}</p></article>`).join('')}</div></section><section><h2>实景复核</h2><div class="grid">${images.map(([f,c])=>`<figure><a href="${f}"><img src="${f}" loading="lazy" alt="${escape(c)}"></a><figcaption>${escape(c)}</figcaption></figure>`).join('')}</div></section><section><h2>验证边界与后续</h2><p>本轮是实际按钮、碰撞寻路、出口传送、NPC剧情与掉落交付的分段验证，完整普通数值通关仍需独立验收。</p><ul>${next.map(s=>`<li>${escape(s)}</li>`).join('')}</ul></section><section><h2>可复核记录</h2><div class="links">${[['report.json','完整报告'],['targeted-tests.json','针对性规则'],['rule-regressions.json','52组回归'],['playtest.json','浏览器流程'],['verification.json','原版来源校验'],['lifecycle.json','测试进程清理'],['rules.log','最终回归进程记录']].map(([f,l])=>`<a href="${f}">${l}</a>`).join('')}</div><p class="note">备份：${backup}。本任务启动的临时浏览器与预览服务器已关闭，最终回归确认端口5180未监听。</p></section></main></html>`;
await fs.writeFile(dir+'/report.html',html);
await fs.writeFile('reports/latest-restoration.json',JSON.stringify({date:report.date,report:dir+'/report.json',html:dir+'/report.html',next},null,2));console.log({passed:true,targeted:targeted.checks,regressionSuites:rules.count,browserCases:playtest.results.length,report:dir+'/report.html'});
