# A13 老药师原版服务最小方案与容量补证

日期：2026-10-16。基线任务：a08a204 / runtime c6ebde3。只读研究原游戏与当前实现；仅在本仓外目录写报告/证据，不修改 Project、不运行原 EXE/Godot、不操作 Git、不开放服务。

## 当前结论（补证后，优先于初次建议）

原 EXE 静态购买链已经证实：先检查42物理背包槽是否有空位，再检查原剩余负重能否容纳单件商品，然后检查金币、扣单价并通过 GIVE 分配一件独立实例。本链没有查询同名已有物品、增加堆叠数量、quantity乘单价或“全部”逻辑。药包是独立模板，购买不拆包。

因此更正初报“真实购买必须先扩堆叠/腰带库存”的建议：不需要为了复刻原版而先移植 Web 堆叠；现42实例核心更接近已验证原购买路径。仍须做审定12药目录、单件原子交易、稳定身份和对话revision绑定；不能因商店可用就宣称治疗和宠物系统完整。

Web 的 +/−/全部、50/30/40堆叠格、腰带优先合并是 portrait override，应作为明确不同的参考实现保留，不得冒充原版。原完整商店面板布局、网格行列、15个非背包实例位置的逐项语义还未证实。不为此无限逆向全EXE；最小购买范围限制为当前初始战士、已验证布衣装备和背包物品，其他装备/腰带输入继续拒绝。

## 1. 原NPC与脚本

Project/data/maps/A13.json:70113：sourceNPC[2]，老药师，x=20/y=26，appearance=2，direction=2。完整脚本UTF-8 SHA256（保留CRLF）：78fdc3d3044ef40d2d7de1cb36804de64349131d22e3c9036391b723db3ae2ad。

本目录 pharmacist-script.txt 是逐字节UTF-8副本；SOURCE_INDEX.json保存源文件行号、文件SHA、脚本SHA、商品原记录SHA。源审计 a13-service-audit/REPORT.md 已说明原LP/项目JSON/Web JSON的NPC相等；本次重新比较药师两个JSON记录。

脚本无剧情门槛。START含BUY12、介绍、三个按钮：角色治疗(2,9,绿,M1)，宠物治疗(12,9,青,M2)，关闭(34,9,黄,OVER)。M1说明1000文，确认到M1G；M2说明2000文，确认到M2G；每页有原关闭按钮。保留全部原文与坐标，不添加出售、兑换或商店剧情条件。

药师自身没有orphan ENDIF；ITEMCK按IF入栈后两个ELSE/ENDIF全部配平。不修改其他NPC源脚本，不允许全局忽略孤立ENDIF，不允许未知命令默认成功或只编译当前页绕过错误。

Help Mod_4_6.htm:717–722说明BUY/ENDBUY每行一商品；878–882说明TAKE金币；910–914说明ITEMCK像IF且可嵌套。Game_Index.htm:141–150说明背包使用/丢弃/快捷栏/装备/仓库存取操作，但不是完整容量规格。

## 2. BUY12目录（保持原顺序）

|序|ID|名称|价格|原weight|type|
|---|---:|---|---:|---:|---:|
|1|3|强效金创药|35|1|3|
|2|4|绝强金创药|60|1|3|
|3|42|精炼金创药|120|2|3|
|4|8|强效魔法药|30|1|3|
|5|9|绝强魔法药|55|1|3|
|6|44|精炼魔法药|110|2|3|
|7|13|强效金创药包|210|7|6|
|8|14|绝强金创药包|360|7|6|
|9|18|强效魔法药包|180|7|6|
|10|19|绝强魔法药包|330|7|6|
|11|43|精炼金创药包|760|12|6|
|12|45|精炼魔法药包|660|12|6|

Project/data/items/catalogue.json.records与参考项目/public/assets/data/items.json逐项名称/ID/price/weight/type相同。原模板来自Item0.lpRes，SHA 1b19b738c9c66492aa1aaee0c5218d84e0f67a567de9391794edc9fd75f260fe。原Help/Mod_2_1.htm:227–239明确weight为道具重量、price为商店购买价格。不能把药包买入替换为多瓶药，精炼包价格尤其不能据单药推算。

## 3. 新增原EXE静态证据：槽位、重量、单件购买

二进制：原版游戏/LP传奇单机版_重生.exe；2502656 bytes；SHA256 21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84。只用Python读取PE字节与系统objdump静态反汇编。NATIVE_EVIDENCE.json含节区、VA→文件offset、每段原bytes SHA/hex与证据解释；*.asm为真实反汇编。

### 3.1 42槽有独立原版证据，不是从Godot倒推

- Help Mod_4_6.htm:526–528：PKCOUNT=角色背包剩余空间。
- native-query.asm，0x608477比较字符串PKCOUNT（0x4177c0），0x608482调用0x5fc4f0。
- native-bag-helpers.asm，0x5fc4f0..0x5fc52d：从实例数组base+0x834开始，步长0x8c，循环0x2a=42次；每条+0x2c字符串长度>1算占用；返回42减占用数。IAT0x40104c经objdump导入表确认为__vbaLenBstr。
- 0x834/0x8c=15。0x5fc660..0x5fc6a7独立验证空槽扫描index15..56 inclusive，找到第一个名称长度<=1的位置即返回；全满返回-1。
- 该证据证明42条物理实例槽和扫描区间，不能证明UI一定6×7或7×6，不从差值15外推装备/腰带逐项映射。

### 3.2 原重量计算与容量源

- 0x5fc530..0x5fc574：实例index0..56，共57条，名称长度>1才累加实例+0x80重量，返回低16位。
- 0x5fc5f0..0x5fc65f：同样遍历57条，返回角色record+0x2080减重量总和（16位算术）。不能仿制原溢出漏洞；候选用范围检查拒绝越界。
- 原创建战士0x59308b设ESI=25，0x593105写入角色+0x2080；已有Project/data/items/native-static-evidence.json范围warrior_create可核对，本目录另存原字节区段。道士/法师创建该字段分别22/20，当前最小候选不开放这些职业。
- Help Game_Index.htm:185/191升级负重基础+2、战士额外+1；237/242防御/魔防加点负重+1。参考inspect-numerics.py另报告战士每十级额外+1，属于参考静态结论，本任务未重新追完整成长路径。首个药师候选不加等级成长系统。
- 当前Profile已固定初始战士capacity25，POLICY为bag+equipment；原重量函数覆盖前15条加42包槽，故不可普遍宣称现10个命名装备槽完整映射了原15位置。本候选只容许当前已审定布衣与背包，其他位置/装备输入拒绝，不能用Web“忽略装备腰带重量”补齐。

### 3.3 购买实际调用上述helper

native-trade-capacity.asm完整函数范围0x582c50..0x583000：
1. 0x582e5b调用0x5fc4f0；无空槽则字串0x40ff08“背包剩余空间不足”。
2. 0x582ead调用0x5fc5f0，0x582eb2再减选中商品实例+0x80；结果负数则0x40ff20“人物负重能力不足”；等于0允许。
3. 0x582ee8读取商品+0x84价格，0x582ef7比较角色+0x1fe0金币；不足则0x40ff38“携带金币不足”。
4. 0x582f27扣单价；0x582f29压入原字串0x40ff4c“#give ”，拼接选中商品名，0x582f98调用0x603e10。
5. native-buy-grant.asm：0x603ec4..0x603ecf将省略/非正数量归1；0x603ef6循环给物，每份0x603f04调用空槽helper；0x603f47..0x603f64将新0x8c实例复制到选中空槽。

该购买链没有同名库存查询或数量字段递增，重复购买同一药会另占槽。它只用单价、单件重量，没有Web批量数量UI的行为。只声明此已追踪购买链；不宣称所有其他原游戏操作均无合并。GIVE模板构造内部还可能做装备随机属性，这不是药物购买需开放的装备路径。

误命名排除：native-purchase-check.asm是初始搜索“携带金币不足”命中的0x563230片段，实际附近有武器type14/合成级别检查，不能用作药师购买证据。保留它仅记录搜索误命中，NATIVE_EVIDENCE将其标excluded。

## 4. 治疗确切条件和未完成部分

M1G：ITEMCK金币>999，成功TAKE1000、REME；999不足且不变，1000剩0，1001剩1。原脚本没有满血免收费条件。
M2G：ITEMCK金币>1999，成功TAKE2000、REPET；1999不足，2000剩0，2001剩1。
关闭/取消以及进入报价页均不扣钱。

参考npc-dialogue.js:64生成事件；script-services.js:27要求玩家存活，47 REME将HP/MP补至attributes上限、清healingPool/mpRecoveryPool/combat.recovery；48 REPET遍历存活followingPet（units加waitingPets，定义见11行），恢复definition.hp并清healingPool，不复活死亡宠物。Web无宠物时仍可扣钱并空循环成功。原EXE对REME/REPET细节本任务未独立追踪，Help亦未找到说明，不把Web行为写成已证原EXE。

当前无完整恢复池、宠物权威模型；REPET保持可解析原菜单，但执行不支持必须整体回滚，不能扣2000后显示假成功。REME需独立受限状态适配，不能写死hp25/mp5冒充全角色上限；不借药师任务发明宠物模型。

## 5. Web参考与原版的明确差异

参考services.js:13校验库存包含ID、正整数数量、目录价格、容量和金币；先合并carried再扣price×quantity。inventory.js:9–10的carried包含bag+belt；匹配腰带优先合并。service-ui.js:7–43显示5×5、数量+/−/全部、价格、反馈和关闭；“全部”按金币可买量，容量不够失败不截断。

但native-stats.js:39明确“Portrait inventory override”，取消原重量限制；bag-capacity.js:3为战士50/法师30/道士40堆叠格；inspect-growth.py明确这是user-requested override。旧inspect-npc-quests.py仍残留“42 physical inventory slots and worn/bag carry weight”文字，与当前Web代码不一致，应保留版本差异，不据旧说明冒称当前Web执行重量检查。

结论：可借用Web的事务校验、失败反馈和不重入思想；原版候选先单件购买，不引入Web批量/全部和堆叠库存。若将来确需这些交互，应明确标为参考Web扩展并单独确定契约。

## 6. UI资产证据与界限

本目录Data1/2/3/4/6/7/8-contact.png为现有原图atlas逐帧裁切缩略联系表，不是新设计。已人工看图：Data1:9原对话面板，Data2主要创建/返回/确认按钮，Data3格言，Data4血条数字与特效，Data6男女角色像，Data7状态图标，Data8天空/特效。所查帧没有完整背包/商店格网，可疑空白区域不能推导槽数。

参考public/assets/ui/native/index.json给出原资产来源：dialog=Data1 frame9，原尺寸523×216；button=Data2 frame7，101×30（图文为“新的开始”，不能直接当购买按钮）；Data1 frame27–30是383像素边框线，不是完整商店控件。原图sourceSha/sourceOffset/sourceBytes可核查；native UI index本身记录design750×1624与nine-slice adaptation，不能当原屏幕布局。

原Help数字1–6自定义恢复道具快捷键、点击快捷栏目标格“设置快捷道具”。这只证明6个快捷键和设置行为，不证明Web腰带作为独立库存。当前不追加腰带存储。

当前opening_candidate.render_dialog按原BUTTON x/y和颜色，可复用；保留原菜单/价格/关闭，不擅加新UI风格。完整商店网格行列与数量控件尚未确定，已验证链按单件即可满足最小行为；界面复刻仍需原绘制/命中函数证据后才能称原版完整UI。

## 7. 最小方案与改动接缝（尚未实施）

1. 独立earth_apothecary_candidate scene/controller继承Earth候选；不改main，不开放所有NPC。
2. 复用NpcIdentity.sidecar/resolve；药师能力固定A13/source2、六字段记录与脚本SHA、world instance/npc_epoch/revision。source0/1原链保持。不得用当前压缩数组index或名字授权。
3. 页面白名单START/M1/M1G/M2/M2G/OVER；单件购买意图只传itemID，不接受客户端价格、金币差值、随意目标页或数量。
4. 每回调绑定world/epoch/conversation revision/source2/script hash/inventory revision/catalogue hash；提交重新查当前NPC和authority。关闭、换图、重开、成功购买后陈旧回调无效。
5. authority.character.gold和authority.inventory继续唯一来源；在detached authority上验证单件空槽/总重/金币，Inventory.stage+commit取得新快照，重新Profile校验，最后一次发布钱和库存。失败不改任何serial/revision/RNG/对话状态。不能照原EXE先扣款后生成的执行顺序暴露部分失败。
6. 专用目录仅布衣252+上述12药；默认战士其他限制不放宽。购买药包只acquire原药包模板。购买药物不暗自消费或拆包；consumable分类须有受限源适配，不能让generic consume接口在无药效时吞物。
7. VM窄扩展BUY/ENDBUY、ITEMCK金币、TAKE金币、REME/REPET事件。条件结构按ITEMCK入栈，不开放未知物品条件，不放宽orphanENDIF。其他服务事件拒绝。
8. REME、REPET与购买分开验收，不以菜单显示等同治疗完成。

建议最小文件：新增core/apothecary_service.gd、core/apothecary_profile.gd、ui/apothecary_shop.gd、earth/apothecary_candidate_controller.gd、scenes/earth_apothecary_candidate.tscn；dialogue_vm.gd作窄扩展；共用controller仅必要分派钩子。补证后不再要求inventory_state增加堆叠/腰带；已有42实例stage/commit可复用，先验证无需schema变更。codec如现模板通用无需为购买改动，但新profile保存许可应另核，不默认持久化已完成。不改源A13.json、LP二进制、project.godot main。

## 8. 验收矩阵

|类别|最低验收|
|---|---|
|源|12项顺序/ID/price/weight一致；脚本/目录SHA漂移拒绝|
|身份|删除凌云后runtime1解析source2；其他NPC不可借索引获服务；source3–10仍禁|
|流程|START/M1/M1G/M2/M2G/OVER全覆盖；进入/取消不扣款；保留原按钮|
|金币|999/1000/1001、1999/2000/2001；每药单价−1/单价/单价+1|
|单件|一次扣一份价格/得一个实例；连续买同药增加独立ID和槽；药包不拆|
|槽位|0/1空槽、全满、同名已有物品但全满仍拒绝；明确无堆叠|
|重量|当前布衣2+药物总重；等于25允许，超过25拒绝；精炼药2/药包7或12；前15未知位置输入不获默认支持|
|事务|满包、负重不足、钱不足、未知ID、溢出、库存先变、Profile校验失败均全部回滚|
|重放|重复点击、旧页、关闭后、切图返回、目录改变、库存revision改变拒绝；RNG失败不推进|
|治疗|满/缺血蓝、恢复池、死亡等单独测；未实现宠物不扣钱；不能假成功|
|结构|药师ITEMCK配平；其他orphanENDIF旧失败保持|
|回归|原主链54项、map load、source identity、inventory/codec；自然鼠标路线另验，调试直调不冒充用户路径|

优先级：现画面继续优先，药师资料已足以排“初始战士单件购买”的受限纯事务候选；完整UI布局与未知携带位置不靠猜。没有新运行通过数，不报告已开放/已可买。

## 9. GIVE失败与原子安全差异（最终补充）

原购买handler在0x582f27/0x582f2e已经扣款，随后才调用GIVE。0x582f98调用返回后直接清理临时字符串并刷新，没有检测成功标志或恢复金币的分支。GIVE本身先查空槽，若无空槽走0x603f6f后至0x604010的地面生成路径。模板查找/构造出错、脚本解析错误或分配异常是否能触发VB错误处理、会否保留扣款，本任务未运行EXE，不能宣称已复现原bug；静态调用者未见退款分支是明确事实。

候选故意采用更安全的原子发布：正常可购买输入保持原单件结果与空槽→重量→金币失败优先级；内部失败、目录漂移、陈旧revision一律不扣款/不给物，不声称这一额外保障是原EXE逐指令一致。这是保全用户状态的实现约束，不是改价格/数量规则。

UI触发界限：已定位0x582c50所属COM事件handler、选中商品index全局0x63c76a及商品数组0x63edc0。函数消费当前选择并完成单件交易；本次未解析VB控件事件注册，不能从ret0x14推定左键/双击/右键或具体按钮文字。先把纯purchase_selected_one契约定下来，原点击方式和网格布局另以该handler事件表/绘制函数补证，禁止凭Web UI补造“原版购买数量”控件。

停止条件：本报告已形成可实现受限单件购买的来源契约；没有扩展逆向到全库存/全部NPC/全部UI。剩余前15位置映射、原窗口控件事件、治疗恢复池与宠物模型明确列为边界。下一实施仍由root审查排序。
