# 独立原商店 UI 参考候选

授权范围：仓外 owned，原资源局部布局与单件交易交互。不是 Project 已接入服务，不是最终 HD 皮肤。主树未改。

## 文件和资源
- owned/shop.tscn、scripts/shop.gd：329×147 原面板、16格8×2、原67×21购买钮；原局部格(26+35c,27+35r)、按钮(236,105)。全局(24,90)仅诊断承载位置。
- owned/scripts/session_adapter.gd：独立 authority、可信 source2 context、原脚本 BUY 顺序核验、prepare/commit、关闭/重开/成功交易 revision 失效。
- owned/scripts/core 三文件：已测核心与原 Inventory/Profile 逐字副本，未重写业务；未来接主树需复用主依赖。
- owned/data/source.json：从 Project/data/maps/A13.json 原 npcs[2] 完整提取，源文件 SHA 随同记录。map/source 索引由 adapter 固定核验，script SHA/full record 由 core 核验。不是游戏存档/外部 UI 传入 context。
- owned/data/records.json：既有精确13模板 fixture，仅独立候选；不是主 profile 白名单扩展。
- assets/panel.png：原 EXE 嵌入 ScriptBuy.gif 无损解码；assets/buy.png：原 Data/Button/Buy.gif 无损解码。
- assets/item_ID.png：原 Data/Item1.lpRes 对应 icon GIF 直接取字节、无损解码；Web index 只用已校验相同原包 SHA 的 offset/length，不用 Web portrait 配方。逐项来源见 data/resource_sources.json。
- tests/ui_test.gd：实际 core 路由、选空、关闭重开/成功购买旧 ticket 失效、布局节点检查。

## 诚实边界
原面板/按钮/格子用源像素。不确定的选择框颜色没有自创；价格与选择名称暂在明确诊断区显示，原价格 label 的准确几何/字体未证。悬停只给已证名称/价格，注明非原 Tooltip 复刻。外围 Godot 诊断字体/按钮不是原皮肤证据。
仅等级1普通初始战士、布衣、容量25；测试金币2000，初始值为测试设置，不声称原开局钱数。完整库存/装备去重计重；药包独立模板，不拆、不堆叠。治疗菜单只显示原文本，不可点击、无确认成功页/扣钱。
全部状态仅候选 session 持有，无主存档/主NPC入口/真实服务接线。价格核心失败无状态变更；关窗/重开属于独立 UI 生命周期，主动推进 revision。

## 引擎状态
planner批准短headless窗口后，实际Godot4.6.3复测exit0，23检查通过，ERROR/WARNING 0。检查包含原尺寸/16格/购买节点、实际core扣单价/单实例、空格无修改、成功购买/关闭/重开旧ticket失效。首轮因JSON source_index浮点与core整数契约不符导致测试未保护ticket访问，timeout124；首败日志保留。修复为先严格确认源索引等于2，再由可信adapter构造固定整数2（不截断任意输入），测试加fail-fast。窗口已释放。未运行GPU、未视觉截图，因此只能宣称节点与交互数据验收通过，不能宣称画面审阅已通过。


## 实际图形与鼠标验收
已完成一次官方鼠标验收，细节见 GPU_REVIEW.md / GPU_RESULTS.json。exit0，ERROR0，1条V-Sync驱动警告；原资源面板原尺寸，12药清晰。原文两枚私用字符缺字已记录。仅一张实际窗口截图，不是最终HD皮肤。

源私用码显示兼容：仅Label展示层将U+E810映射为空白，沿现opening_candidate先例；不是已证原引擎语义。原A13/record.script/VM文本/脚本SHA未改。


最终显示兼容复验：glyph-headless.exit=0，23/23通过，无ERROR/WARNING；actual-glyph-window.jpg已由官方桌面截图并独立目视确认段首不再方块，gpu-glyph.exit=0，ERROR0，仍有1条相同V-Sync驱动警告。未重复交易链，旧actual-purchase-window.jpg与gpu.log保持原交易证据。source2脚本SHA再次核对不变。
