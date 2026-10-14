import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

// Audit output only. Do not modify runtime, assets or user saves.
const dir='reports/parity-audit-20261013';
const read=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
const probes=await read(dir+'/probes.json'),quests=await read(dir+'/quest-coverage.json'),native=await read(dir+'/native-evidence.json');
const movement=await read('reports/movement-20261013/report.json');
const before=await read('reports/movement-20261013/source-before.json');
const expected=new Map(before.files.map(r=>[r.file,r.sha256]));
for(const r of movement.sourceChanges)expected.set(r.file,r.sha256);
async function walk(path){const result=[];for(const e of await fs.readdir(path,{withFileTypes:true})){const p=path+'/'+e.name;if(e.isDirectory())result.push(...await walk(p));else result.push(p);}return result.sort();}
const source=[];for(const file of await walk('src'))source.push({file,sha256:hash(await fs.readFile(file))});
assert.equal(source.length,expected.size,'Runtime file count changed since movement completion');
for(const r of source)assert.equal(r.sha256,expected.get(r.file),'Runtime changed: '+r.file);
assert.equal(probes.findings.length,8);assert.equal(quests.summary.unsupportedProbes,0);
const evidence=(file,needle)=>({file,needle});
const findings=[
 {id:'A01',priority:'P1',status:'已确认',area:'装备 / 存档',title:'地面物品读档丢失强化水使用次数',
  detail:'使用三次强化水的装备，丢到地上后保存并读档，waterUses 字段被过滤掉；拾回装备后又能继续使用强化水。属性保留而次数重置，会破坏强化上限。',
  reproduction:'扎克 waterUses=3：读档前提示“当前武器已过量使用”；恢复地面物品后次数为空，再次使用成功。',
  probeIds:['ground-water-use-save'],evidence:[evidence('src/loot.js','export function restoreGroundItems'),evidence('src/special-consumables.js',"(old.waterUses||0)>=3")],
  next:'统一背包、装备、仓库与地面物品的实例字段恢复规则；补丢弃→保存→读档→拾取回归。'},
 {id:'A02',priority:'P1',status:'已确认',area:'难度 / BOSS',title:'切换难度覆盖明阳守卫第二阶段，复活又恢复旧难度属性',
  detail:'setDifficulty 直接用基础怪物定义重建属性，没有处理明阳守卫的 reborn / birthDefinition。二阶段标志保留，特殊攻击却被重置；下次重生会使用切换前的定义。',
  reproduction:'普通二阶段攻击类型22、攻击55；切专家后变类型0、攻击92、最大HP5200；重生恢复HP4000，玩家仍处于专家。',
  probeIds:['difficulty-rebirth-reset'],evidence:[evidence('src/game.js',' setDifficulty(mode)'),evidence('src/monster-rebirth.js','export function tryMonsterRebirth'),evidence('src/monster-rebirth.js','export function resetMonsterRebirth')],
  next:'明确战斗中能否换难度；统一基础难度定义、阶段修正和重生定义的重建顺序。'},
 {id:'A03',priority:'P2',status:'已确认',area:'剧情 / 任务UI',title:'三条已有原版支线未进入任务页，后续主线导航也未补全',
  detail:'救采药人（ET6）、清剿魔灵蜘蛛（ET3）、归还铁锤（ET4）的对话、条件和奖励脚本存在，任务页却只注册了ET2和ET10–15七条路线。主线行动按钮仅覆盖开局寺庙、村庄和甲虫王阶段。',
  reproduction:'分别携带铁锤、设置采药人获救或蜘蛛击杀状态，NPC对话正常解析，但任务列表没有相应支线。不是这三条剧情完全不可玩。',
  probeIds:['unlisted-side-quest-6','unlisted-side-quest-3','unlisted-side-quest-4'],evidence:[evidence('src/quest-journal.js','const routes='),evidence('src/first-quest-target.js','export function firstQuestTarget')],
  next:'覆盖支线可接、进行中、可交付和完成状态；补后续主线目标与跨地图指引。'},
 {id:'A04',priority:'P2',status:'已确认',area:'掉落 / 画面',title:'地面装备名称和图标忽略装备实例修改',
  detail:'背包和角色页使用实例属性，地面绘制仍取基础物品定义；拾取飘字也取基础名称。注灵、改名或改图标后的装备落地显示不一致。',
  reproduction:'原版克钦 #UpWeapon 配方产物“扎克(注灵)”应显示图标960，地面实际显示“扎克”和基础图标955。',
  probeIds:['ground-instance-display'],evidence:[evidence('src/game.js',' drawGroundItem(g)'),evidence('src/combat.js',"const name=g.kind==='gold'?")],
  next:'地面名称、图标和拾取反馈都读取同一个装备实例，保留实例颜色。'},
 {id:'A05',priority:'P2',status:'已确认',area:'刷怪 / 常驻机制',title:'符合条件击杀加速BOSS刷新计时的原版分支未接入',
  detail:'原版在死亡处理后另有选择有效BOSS计时器并随机额外减秒的分支，含挑战状态、怪物字段及“设置”项排除条件。当前只有随时间倒计时和死亡脚本自身设置BT，没有这段击杀奖励。',
  reproduction:'现实现中已有计时器100秒，击杀鸡后仍为100。原版0x5c968b–0x5c9847读取计时器并减 CInt(Rnd×10)+5 秒；该复现只证明现实现未额外减秒，不代替完整原版资格条件验证。',
  probeIds:['kill-boss-timer'],evidence:[evidence('src/combat.js',' kill(u,'),evidence(dir+'/monster-update-drop.txt','005c968b')],
  next:'补齐触发资格、选择顺序、累计值和刷新提示；不能简单对每次击杀或所有计时器统一扣秒。'},
 {id:'A06',priority:'P3',status:'已确认',area:'创角 / 难度',title:'新建角色可选地狱的全局解锁提前',
  detail:'原版帮助要求任意角色进入地狱并存档。现有modeUnlock>=2就解锁全局地狱创角，即上一难度通关但尚未进入地狱也会解锁。专家、地狱入口本身已经接入。',
  reproduction:'当前角色仍为专家 gameMode=1，只具有modeUnlock=2，保存后新角色模式已包含地狱。',
  probeIds:['hell-global-unlock'],evidence:[evidence('src/save-roster.js','this.hellUnlocked=value.hellUnlocked'),evidence('reference/LP传奇单机版-重生v1.2.2E/Help/Game_Index.htm','进入地狱难度并存档后')],
  next:'分开“当前角色允许进入地狱”与“账号已有地狱存档”的解锁标志，兼容已有合法地狱档。'},
 {id:'A07',priority:'P2',status:'已确认',area:'技能 / 特效',title:'魔法盾临近结束的闪烁提示未接入',
  detail:'展开、常驻循环、受击帧已经连接。原版渲染还检查剩余计数并按周期隐藏护盾；现在仅倒计时到期移除，缺少临近结束的视觉提示。',
  reproduction:'静态对照原版0x5c2c9f–0x5c2cc0与当前drawCombatEffect、effectFrame。此项未做本轮浏览器截图复现。',
  probeIds:[],evidence:[evidence(dir+'/shield-expiry-flash.txt','005c2c9f'),evidence('src/game.js',' drawCombatEffect(effect)'),evidence('src/combat-effects.js','if(p.magicShieldFrames>0)'),evidence('src/effect-animation.js','shield')],
  next:'核对原版计数单位后接入到期闪烁，保留展开和受击动画。'},
 {id:'A08',priority:'P2',status:'部分实现',area:'战斗 / 弹体',title:'范围命中、弹体寿命与碰撞仍有通用近似',
  detail:'26项技能已有执行路线，特殊攻击也有实现，不能列为整套技能缺失。但部分范围技能按网格批量取目标；通用弹体采用默认4秒寿命、目标距离加64像素射程和16像素命中半径，尚未逐分支证明等同原版。已还原的26/27型定向散射应保留。',
  reproduction:'代码核查，无本轮逐帧原版录像比对；尚不能断言每一种技能都存在可见偏差。',
  probeIds:[],evidence:[evidence('src/projectiles.js','export function launchProjectile'),evidence('src/projectiles.js','const target=candidates.find'),evidence('src/combat-skills.js',"name==='半月斩'")],
  next:'按技能建立原版对照场景：墙角、斜线、移动目标、大体型、多目标重叠及连续命中。'},
 {id:'A09',priority:'P2',status:'部分实现',area:'场景 / 粒子',title:'通用粒子6与10–16类型的实际入口仍未完成核对',
  detail:'类型6有粒子构造，未找到运行时发射入口；10–16没有对应实现，原版触发旗标仍待定位。已有冰冻、燃烧、中毒、恢复、暗黑光环、守卫复活、地面装备和天路/三明界/轮回云雾。',
  reproduction:'代码与既有原版粒子证据对照；尚不能把所有未映射类型认定为当前发行版可实际触发的天气内容。',
  probeIds:[],evidence:[evidence('src/native-particles.js','export function emitNativeParticle'),evidence('src/ambient-particles.js','emitAmbientParticles')],
  next:'先反查原版调用入口与地图标志，确认在发行内容中可达后再补，避免虚构天气。'},
 {id:'A10',priority:'P2',status:'待核原版条件',area:'动作 / 受击',title:'主角受击动作有帧定义，但没有运行入口',
  detail:'animation.js定义hurt帧225起的三帧动画；当前hurt只处理伤害、反馈、护盾受击和死亡，没有进入主角hurt动作。原版何种命中、硬直或状态才触发受击仍需追踪。',
  reproduction:'静态入口搜索；未证明应当每次受伤都打断移动或攻击。',
  probeIds:[],evidence:[evidence('src/animation.js','hurt:{base:225'),evidence('src/combat.js',' hurt(actor,damage')],
  next:'恢复原版受击触发与优先级；不能直接让持续伤害或每一击都重启动作。'},
 {id:'A11',priority:'P2',status:'待核原版条件',area:'掉落 / 后期数值',title:'原版条件掉落倍率分支未映射',
  detail:'原版0x5d5eaf–0x5d5fba在特定角色字段组合下把掉落分母除以2、5或10。当前直接使用物品掉落表分母。字段语义尚未确认，不能将它笼统称为“专家/地狱统一爆率”。',
  reproduction:'原版字段条件为+0x2262==83且+0x226a-2==+0x22f0；没有构造游戏中可达条件，未进行黑盒原版概率统计。',
  probeIds:[],evidence:[evidence(dir+'/conditional-drop.txt','005d5eaf'),evidence('src/loot.js','export function rollGroundDrops'),evidence('reports/native-refining-source.json','unmappedConditionalBoost')],
  next:'定位条件字段对应的物品、收集或进度含义；再核对后期特殊物品获取链与概率。'},
 {id:'A12',priority:'P2',status:'验证缺口',area:'剧情 / 完整流程',title:'解析覆盖不能代替从创角到结局的可达性验证',
  detail:'本轮155地图、851个NPC页面、146个入图脚本和80个死亡脚本扫描，35541个采样没有未支持指令。采样状态人为构造且物品充足，不验证真实道具消耗、互斥事件、跨图顺序、计时门槛和多周目接续。',
  reproduction:'quest-coverage明确只检查文本与效果解码，未完成三职业全流程原版/网页版配对通关。普通怪物固定20秒重生也仍需找到原版数值依据。',
  probeIds:[],evidence:[evidence(dir+'/quest-coverage.json','"scope"'),evidence('tools/quest-coverage.mjs','const profiles=[]'),evidence('src/combat.js','respawnSeconds:20')],
  next:'从干净测试档跑普通主线、所有支线、专家/地狱与二周目；记录每次事件与奖励快照，不改真实用户档。'},
 {id:'A13',priority:'P2',status:'验证缺口',area:'性能 / 移动',title:'复杂场景长帧尚未彻底解决或完成硬件复测',
  detail:'上一轮已做异步图像解码、AI索引和纹理释放，并有回归证据。软件WebGL下三明界仍有长帧；不能据此保证用户硬件上已完全流畅，也不能把软件GPU结果直接当硬件帧率。',
  reproduction:'引用上一轮reports/movement-20261013/report.json；本轮没有新开浏览器、没有重新测FPS。',
  probeIds:[],evidence:[evidence('reports/movement-20261013/report.json','"stutterFullyResolved"')],
  next:'在实际硬件WebGL上跑移动、密集怪物、技能与连续换图长时间场景，分离解码、绘制与模拟开销。'},
 {id:'A14',priority:'P3',status:'文档滞后',area:'交付 / 进度',title:'旧清单与README含已经解决的缺失项',
  detail:'开场剧情、专家/地狱入口等已有实现；README仍留旧限制和左走右跑等过期说明。旧审计的remaining不能直接当作当前待办。',
  reproduction:'本报告以当前90个src文件快照及已完成的移动轮次为基线，保留旧报告为历史证据。',
  probeIds:[],evidence:[evidence('README.md','')],
  next:'实现修复时同步维护当前限制和使用说明；保留历史报告，另建当前审计入口。'},
];
for(const finding of findings)for(const e of finding.evidence){const text=await fs.readFile(e.file,'utf8');e.line=e.needle?text.split(/\r?\n/).findIndex(line=>line.includes(e.needle))+1:1;assert.ok(e.line>0,`Evidence missing: ${finding.id} ${e.file} ${e.needle}`);delete e.needle;}
for(const f of findings)for(const id of f.probeIds)assert.ok(probes.findings.some(p=>p.id===id));
const implemented=[
 {area:'首页与流程',state:'已有实现',detail:'原版首页、创角/选角、开场页与对话、结局及流程存档。仍需完整路线验收。'},
 {area:'地图与画面',state:'已有实现',detail:'地图瓦片、层级、动态对象、原版小地图、装备外观/颜色及选中地环。当前未逐张地图重新人工验图。'},
 {area:'核心玩法',state:'已有实现',detail:'成长、装备属性与要求、强化/合成/套装、异常状态、召唤/产卵/随从成长存档、城镇复活、自动拾取。仍有本报告列出的实例与阶段问题。'},
 {area:'技能与音频',state:'已有实现',detail:'26项技能执行路线、技能和怪物音效、脚步与原版背景音乐已接入；范围/弹体/剩余粒子不等于完整逐帧一致。'},
 {area:'常驻系统',state:'已有实现',detail:'商店、仓库/次元箱、治疗、暗黑印记、13项心得、怪物图鉴、守卫边境、限时挑战与纪录。'},
 {area:'难度与后期',state:'已有实现',detail:'专家/地狱入口、基础怪物缩放、装备随机属性、特殊宝箱/水/蛋/技能书已接入；特殊条件与全流程仍需核查。'},
];
const adaptations=[
 '750×1624竖屏、游戏名“小小传奇”、紧凑HUD、左侧交互/右侧怪物及右上角地图弹窗。',
 '自动战斗、六个可开关主动技能、职业筛选、未学隐藏技能不显示、六格消耗品腰带。',
 '背包按战士50/法师30/道士40格，腰带不计入；负重限制已按要求取消。',
 '按路径长度自动走/跑、不可达点击取最近可达点、掉落走近自动拾取、场景点击不选NPC或怪物。',
];
const outOfScope=[
 '微信部署与资源服务器：用户明确暂时跳过。',
 '桌面版联机建房/加入、MOD“云游四海”、编辑器和桌面进程退出：不属于当前单机Web内容范围。',
 '原版发行脚本隐藏的生存挑战入口、没有找到地图/脚本引用的逐鹿分支：不直接计为本版可玩内容遗漏。',
];
const summary={confirmed:findings.filter(f=>f.status==='已确认').length,partial:findings.filter(f=>f.status==='部分实现').length,conditionsUnmapped:findings.filter(f=>f.status==='待核原版条件').length,verificationGaps:findings.filter(f=>f.status==='验证缺口').length,documentation:1,isolatedProbeCases:probes.findings.length};
const report={title:'小小传奇 · 原版对照审计',createdAt:new Date().toISOString(),auditOnly:true,fullOriginalEquivalent:false,summary,
 original:native,sourceUnchangedSinceMovementRound:true,sourceSnapshot:source,
 scope:'原版帮助、数据/脚本、指定EXE分支、当前源码和定向生产函数复现。非本轮浏览器画面验收，非全流程通关，非所有二进制分支穷举。',
 verification:{questScan:quests.summary,questScope:quests.scope,probesFile:'probes.json',probeScope:probes.scope,sourceFiles:source.length},
 findings,implemented,adaptations,outOfScope,
 order:['先修A01/A02：装备实例存档与特殊BOSS阶段，防止数值污染。','再修A03–A07：支线与导航、掉落反馈、刷新计时、创角门槛及护盾提示。','追踪A08–A11：逐技能碰撞/动画，粒子真实入口和特殊掉落条件。','用干净测试档补A12全剧情验收，实际硬件复测A13；更新A14当前说明。'],
 lifecycle:{auditBrowserStarted:false,auditServerStarted:false,auditMcpStarted:false,userSavesChanged:false,questSweep:{sessionId:28708,exitCode:0,closed:true},note:'原版提取、定向探针和报告生成均为有限命令；未触碰已有5180预览服务。'},
};
await fs.writeFile(dir+'/report.json',JSON.stringify(report,null,2));
const esc=v=>String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const link=file=>encodeURI('../../'+file);
const cards=findings.map(f=>`<article id="${f.id}"><div class="tags"><b class="${f.priority}">${f.priority}</b><span>${esc(f.status)}</span><span>${esc(f.area)}</span></div><h3>${f.id} · ${esc(f.title)}</h3><p>${esc(f.detail)}</p><p class="muted">证据与边界：${esc(f.reproduction)}</p><p><strong>后续：</strong>${esc(f.next)}</p><div class="refs">${f.evidence.map(e=>`<a href="${link(e.file)}">${esc(e.file)}:${e.line}</a>`).join(' · ')}</div></article>`).join('');
const list=rows=>'<ul>'+rows.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ul>';
const html=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${report.title}</title><style>
*{box-sizing:border-box}body{margin:0;background:#151918;color:#e6e9e2;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1100px;margin:auto;padding:40px 24px 80px}h1{font-size:34px;line-height:1.3;margin:14px 0}h2{font-size:25px;margin-top:46px}h3{font-size:20px;margin:12px 0}p{margin:10px 0}a{color:#adcfc0;overflow-wrap:anywhere}.kicker,.muted{color:#a8b6ad}.intro{font-size:19px;max-width:900px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}.stats div{background:#202823;border:1px solid #3b4b40;padding:16px;border-radius:8px}.stats b{font-size:30px;display:block;color:#e2c58c}.stats span{font-size:14px}article{border:1px solid #3c473f;border-radius:9px;padding:22px;margin:16px 0;background:#1c231f}.tags{display:flex;flex-wrap:wrap;gap:8px}.tags>*{padding:2px 10px;border-radius:4px;font-size:13px;background:#344038}.tags .P1{background:#854c3f}.tags .P2{background:#625235}.refs{font-size:12px;margin-top:16px}.note{border-left:3px solid #c5ad73;padding:12px 18px;background:#24291f}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #3b473e;padding:12px;vertical-align:top}th:first-child,td:first-child{width:150px}li{margin:8px 0}footer{margin-top:50px;color:#9ead9f;font-size:13px}@media(max-width:640px){main{padding:22px 15px}.stats{grid-template-columns:repeat(2,1fr)}h1{font-size:28px}article{padding:17px}th:first-child,td:first-child{width:95px}}
</style><main><div class="kicker">2026-10-13 · 当前源码快照 · 仅审计</div><h1>${report.title}</h1><p class="intro">主体系统已经接通，但还不能称为完整复刻。当前有明确影响装备数值、BOSS阶段和任务体验的遗漏；另有战斗细节与原版触发条件尚未核实。</p>
<div class="stats"><div><b>${summary.confirmed}</b><span>已确认差异 / 缺陷</span></div><div><b>${summary.partial+summary.conditionsUnmapped}</b><span>部分实现 / 条件待核</span></div><div><b>${quests.summary.probes.toLocaleString('en-US')}</b><span>脚本解析采样</span></div><div><b>${source.length}</b><span>运行时源文件保持不变</span></div></div>
<p class="note">本轮没有修改玩法、资产或用户存档。8个定向探针用于复现问题，不代表8项功能通过验收。脚本零未支持指令也不代表全剧情可通关。没有给出缺乏依据的整体完成百分比。</p>
<nav><a href="#findings">问题清单</a> · <a href="#implemented">已有内容</a> · <a href="#scope">设计边界</a> · <a href="#next">推进顺序</a> · <a href="report.json">完整JSON</a> · <a href="probes.json">探针结果</a> · <a href="quest-coverage.json">脚本扫描</a></nav>
<h2 id="findings">问题清单</h2><p class="muted">P1优先处理数值与状态错误；P2补齐体验和原版逻辑；P3处理门槛差异与说明。不同证据状态分别标注。</p>${cards}
<h2 id="implemented">已接入，不能继续算完全缺失</h2><table><thead><tr><th>范围</th><th>当前判断</th></tr></thead><tbody>${implemented.map(r=>`<tr><td>${esc(r.area)}</td><td>${esc(r.detail)}</td></tr>`).join('')}</tbody></table>
<h2 id="scope">按用户要求修改的设计</h2>${list(adaptations)}<h3>范围外或原版本身未开放</h3>${list(outOfScope)}
<h3>验证覆盖与局限</h3><p>${esc(report.scope)}</p><p>155张地图、851个NPC页面、146个入图脚本、80个怪物死亡脚本，共35541次采样，未支持指令0。采样使用33组人为事件/职业/等级/模式状态与充足物品，尚未验证真实路线可达性。</p><p>运行时90个文件逐一SHA-256对照上一轮完成状态，全部一致。完整原版EXE指纹与4段本轮提取的汇编见<a href="native-evidence.json">原版证据</a>。移动表现引用<a href="../movement-20261013/report.html">上一轮验证</a>，本轮未重新测帧率。</p>
<h2 id="next">建议推进顺序</h2>${list(report.order)}<footer>有限命令均在完成后退出；本轮未创建浏览器、MCP或开发服务器。未修改真实角色存档。报告保留原版不确定性，不把人为改造或原版隐藏入口算作移植遗漏。</footer></main></html>`;
await fs.writeFile(dir+'/report.html',html);
await fs.writeFile('reports/latest-parity-audit.json',JSON.stringify({date:report.createdAt,report:dir+'/report.html',data:dir+'/report.json',auditOnly:true,sourceUnchanged:true},null,2));
console.log(JSON.stringify({report:dir+'/report.html',summary,sourceFiles:source.length,sourceUnchanged:true},null,2));
