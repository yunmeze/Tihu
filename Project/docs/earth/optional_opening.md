# 可选入口：原版自然开场 + 局部 Earth 美术

此入口把同一套 R6 权威剧情状态与 Earth 显示适配组合起来，不是第一关完整验收。

## 启动与操作

在 Godot 打开 `res://scenes/earth_new_game_candidate.tscn`，运行当前场景。也可从项目目录执行 `godot --path . res://scenes/earth_new_game_candidate.tscn`。

默认 F5/main_scene 仍是 `res://scenes/game.tscn`。原 R6 场景及 `earth_first_map_review.tscn` 保留各自用途；本次不重设默认入口。

创建角色后逐页阅读五页开场；点击 NPC 对话，点击选项推进原脚本。ESC 关闭对话；STOP 生效时不能移动，但允许符合原规则的 NPC 交互。允许移动时，左键选择可达位置，Shift 使用原跑动逻辑。窗口可缩放，画面保持比例；黑边点击忽略。输入映射采用1024×768逻辑画面和2×渲染密度。

正式入口没有外部评审脚本的 F1–F8 相机/姿态快捷键，也不会固定彩蛋随机种子。

## 当前范围

- 同一个 R6 控制器、VM、库存、RNG 和原子地图事务；不维护第二套游戏状态。自然开场包含原五页及两名开场 NPC 的实际剧情，目的地 A00 使用原显示回退。
- A13 的121+57=178个已登记地面 owner；24个完整植物复用实例、81个 owner；pool7/clump3。其余已登记建筑、NPC、植被、18相位和E向六相按各自资格启用；未覆盖内容继续显示源图。
- 每组仍验证原来源、所有者与资源。未知几何、未知图集扩展或依赖问题按原规则回退；彩蛋鸡额外图集仅接受完整预检后的精确闭包。24植物实例不增加新影子。
- 已审影子仍走原 hero slot、原 receiver/light 与 max-alpha 合成。E向六相没有已验收的新投影阴影；不能把这个缺口写成已解决。

## 证据与限制

构造链修复已通过真正原生 SubViewport 像素对照：四个相机、all/121-only/source三态，published review与snapshot同态RGBA一致；121、57各有对应owner ROI内非零变化，ROI外零变化。此前仅有ready数量却绑定旧floor pass的版本保留为失败证据。

当前修正版全套 headless 逻辑、回滚、生命周期、稀有分支、类型/别名、资源故障与逐组回退检查通过。同一修正版已通过真实点击自然链：五页开场、STOP、NPC透明边缘与身体命中、提前凌云子与ESC、方丈A1–A5及凌云子B1–B5，进入ET3/A00(138,12)，随后走到(138,13)，黑边点击未移动角色。自然日志54项语义检查零失败，21个自然里程碑匹配；5个故障或确定性单tick探针不声称原生等价。本版seed208彩蛋人工组合已实窗检查121+57地面、24实例/81植物owner、pool/clump、四相机及E45–50；角色保持(61,39)，相机检查没有传送角色。该分支对话到ET2/凌云B1后停止重复流程，不声称再次完成A00；未做本版rare原生依赖注入，已有headless故障检查与framebuffer证据分别保留。人工模式依据外部启动器和日志标定，屏幕人工提示面板未成功显示。

性能尚未验收：最近200次稳定 CPU refresh p50/p95约22.005/26.959ms，超过50Hz的20ms预算；故障回退更慢。这不等同于原生FPS或GPU耗时。原生前台与后台节流样本必须分开。此次原生自然日志全部样本报告前台焦点，A13秒级FPS样本中位2、p95 24，A00中位5；不能用旧版后台节流解释本次结果。渲染器为llvmpipe软件图形，未测硬件GPU耗时。Windows未验收。

整张A13美术、全部动作循环、E影子、其他NPC服务、战斗、怪物AI、保存及完整游戏流程仍有未完成项。不要把可选局部美术开场视作首关或全游戏验收完成。

## 构建与维护约束

`tools/earth/build_snapshot_registration.py` 可从tracked源数据及已发布注册重建 snapshot receiver/runtime JSON；输出必须指定到Project之外，再核SHA后采用。运行时不依赖诊断工作目录或原版EXE。

运行时JSON中的status/provenance保留生成时的“组合未测、native待验”历史文字，它不是当前验收结论。为保持受测资源SHA稳定，不随测试进展改写该JSON。当前验收应查看同批归档、绑定实际代码SHA的测试报告；本修正版18文件代码清单SHA为 `cd87702d33aa92851fb1531c49ae641953cbebe827484edaae880ab247cc767d`。

运行时声明包含145项。旧receiver pins中的单一Python文件是显式hash-only叶子，不属于通用v1资源类型；SE来源注册JSON也按明确raw-only叶子处理。导出时需显式解析两份新地面/植物注册、receiver闭包及真R6/A00/原UI导入资源，不能只打包JSON或放宽所有未知文件。

snapshot构造函数必须显式调用父类 `super()`，保留 `first_map_floor_pass.gd`。后续回归必须检查实际floor脚本绑定和Framebuffer，不可只看ready计数或纹理资源SHA。默认strict source/atlas门以及旧receiver AND门不得放宽。
