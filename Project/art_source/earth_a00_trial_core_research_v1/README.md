# A00 首房与村长试炼：纯核心源研究

这是独立 source-only 包，不改变默认游戏入口，也不是可玩的 A00 阶段。

## 保留内容

- `source-study/`：原始只读研究报告与来源索引的冻结快照。绝对工作路径属于当时证据背景，不是本包的运行路径。
- `scripts/core/`：受测 `a00_trial_core.gd` 与显式 opt-in 的 `dialogue_vm.gd`。四个未修改核心依赖引用已 Git 的精确版本，未重复保存。
- `implementation/`：作者实现说明、独立 review 修正记录、历史失败与数值修复、两份代码差分。文中测试/日志路径属于原外部研究，不保证存在于此包。
- `VALIDATION_SUMMARY.json`：同 SHA 脚本在作者独立隔离运行完成 check exit0、539/539 行为断言、零 ERROR 的证据摘要及原证据哈希。未附测试执行器、测试源码或日志，**不能用本包直接重跑 539**。

## 可移植材料化

需要 Python 3、Pillow、Git，以及包含所列历史 commit 的完整仓库。运行：

`python materialize.py --repo /path/to/repository --output /new/external/a00-source`

入口先按 Git blob 校验原研究引用，再构造六个核心脚本、无主场景的独立 project.godot、原字节 A00.json 和物品 0/5/252 三条记录。它调用已 Git 的只读 `parse_map`，复核 A00 源字段与已提取数据、两种药品原记录字节；不运行原版 EXE、Godot、测试或 UI。大地图、物品全集和原游戏数据不会作为本研究包的新副本入库。输出中的原地图仅供这次只读解析，不能据此当作完整场景资产闭包。

调用方需把 `data/A00.json` 的原 UTF-8 文本作为 `sources.a00_text`，把 `data/records.json` 数组作为 `sources.records`。核心不拥有 I/O；可信 owner 每次传入当前 authority/context。入口没有创建角色或跳过剧情 API，仅允许已经提交的 A13→A00 到达状态。

## 已实现与限制

纯核心提供严格源准入、容量 25 的单实例库存投影、到达附着、村长/妈妈原脚本选项、同地图屋门 intent、stage 和重放 commit。村长 A5 按原文本给予 100 钱、ET0=4、三份金创药小和三份魔法药小、开启九个北口地格；妈妈可选，不是强制先决条件。药品目前仅存入库存，不启用疗效、消费或堆叠。

`commit` 仅返回离线候选值，不消费票据或自动发布 live 状态。后续可信 owner 必须准备真实 detached world/actor，原子切换 authority、地图、移动、身份侧数据和对话，并应用 movement_reset、拒绝旧回调与重入。这些接线尚未实现。资源回调在测试中是合成 true/false，未证明真实资源加载。

真实步行、屋门自动触发先后、路线取消、对话 UI、保存和实际 owner 原子发布均未接线。portal2 的自然进入受相邻 portal3 与禁止切角规则限制，合成位置测试不是实际行走通过。A01 怪物名称与 ID 的冲突仍未解决；没有战斗、怪物 AI、死亡、掉落或计时器实现。

早期类型推断失败、随后行为失败并中断的 exit130、JSON integral-float 导致门户身份比较错误均保留在历史说明。最终修正逐字段严格验证有限整数值，未放宽字符串/布尔等类型。重放原子安全、整数上限、窄模板白名单和 0.25 屋门触发距离是本重建的工程合同，原执行器的回滚与溢出行为未知。539 通过仅限该纯核心合同，不升级为原生剧情、Windows、性能或完整玩法验收。
