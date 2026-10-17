# A01 来源契约 v1：独立恢复、静态核验

状态：可存档的来源/绑定研究阶段；未接入运行时。2026-10-17 重新核验实际原始二进制与已发布数据，未把上轮提示当作结论。工作目录位于发布仓库外；没有运行原版 EXE、Godot，没有推送 Git，也没有修改发布仓库文件。

## 结论与实施入口

A01「海曦村北」为 150×150，x-major 共 22500 格，48 条 kind6 来源记录、16 条传送门、0 条 NPC。怪物名称必须从地图记录读出，再在原版定义表中顺序查询；地图里的旧数字 ID 不是权威身份。

| 地图旧数字 | 名称 | 提取定义 ID（0-based） | native 定义 ID（1-based） | appearance | 条数 |
|---:|---|---:|---:|---:|---:|
| 4 | 鹿 | 6 | 7 | 5 | 29 |
| 5 | 鹿-精英 | 7 | 8 | 5 | 5 |
| 6 | 鹿-剧毒 | 8 | 9 | 5 | 1 |
| 7 | 鹿-幻影 | 9 | 10 | 5 | 1 |
| 9 | 甲壳虫 | 10 | 11 | 7 | 9 |
| 215 | 假人 | 3 | 4 | 888 | 3 |

45 条来源记录使用普通 appearance 5/7。另三条假人位于 (49,72)、(93,50)、(108,86)，必须保留特殊初始化类别。48 是来源记录数，不是“最终必有 48 个普通活体实例”的保证。

供后续实现读取：

- `A01_SOURCE_CONTRACT.json`：可机读契约、分组、边界、未决事项
- `A01_SPAWN_BINDINGS.json`：全部 48 条，含原始格序号/字节偏移/编码字节/旧数字/名称/提取 ID/native ID/appearance
- `A01_DEFINITION_SOURCE_RECORDS.json`：六个相关定义完整原始字段、字节偏移、编码字节；不为未知字段发明战斗语义
- `SOURCE_PINS.json`：15 个来源文件的路径、大小与 SHA-256；包含仓库提交背景
- `VALIDATION.json`：本轮实际重放检查结果，仅本地验证记录，不随 Git 交付
- `evidence/EXE_EVIDENCE.json`：PE 布局、37 个指令锚点、6 个完整片段的原始 bytes/hash、IAT 与 BSTR 常量
- `evidence/*.asm.txt`：GNU objdump 实际反汇编文本
- `evidence/LOOKUP_MODEL_TESTS.json`：模型边界测试，仅本地验证记录，不随 Git 交付；明确不是 native 执行测试

## 可重放命令

只需 Python 3 标准库与 GNU objdump，不需要 capstone、Pillow、Godot、Wine。脚本不导入仓库里的 Python 模块，不会在来源树生成 `__pycache__`。

```sh
python legend-recovery-work/a01-source-contract-v1/tools/replay.py \
  --repo /workspace/scratch/22c897619190/tihu-legend-recovered
```

默认只覆写本独立产物目录中的生成报告，也可指定仓库外另一输出目录：

```sh
python legend-recovery-work/a01-source-contract-v1/tools/replay.py \
  --repo /path/to/repository --out /tmp/a01-contract-replay
```

脚本先后核对所有 15 个来源 pins。任意来源字节变更直接失败；输出若位于来源仓库内也直接拒绝。默认读脚本相邻的 `SOURCE_PINS.json`，不会从当前任意来源重建基准来掩盖差异。

## 证据链

### 1. 原始地图与定义数据

`原版游戏/Data/Map/A01.lpMap` 从 byte 10 解码，key = header[3] XOR 3。地图短整型逐字段 XOR（不是对文件整体逐字节解密），字符串为 XOR 长度 + 按字节 XOR 的 GB18030。22500 格按 x 外循环、y 内循环读；每格四个 short；kind6 格紧跟一个名称字符串。脚本重新读取原文件，与生产 A01 JSON 16 个字段、参考地图字段及生产 entity index 比较。

定义文件 `原版游戏/Data/Mon/0.lpRes` 从 byte 10、key = header[3] XOR 6 读取 600 条，每条 32 个字段；float32 原样读取，不 XOR。每条原始字段与生产 definitions 逐项比对，600×32 = 19200 个字段；名字、appearance、偏移等也与参考 definitions 比对。原始记录拼接回文件前缀完全一致。这里的 extracted `id` 是顺序零基索引，不是文件里另一个显式 ID 字段。

六组的绑定是本次从地图原始名称对定义原始名称重新得出的，不是直接复制参考 JavaScript 的 runtime 策略。`Project/tools/extract_a13_original.py`、`extract_original_monster_pilot.py`、`lp_original.py` 作为可追溯格式资料被 hash-pin，但不会执行它们的写入主函数。

### 2. native ID = extracted ID + 1

原版 EXE SHA-256：`21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84`。

- PE32/i386，image base `0x400000`
- `.text` RVA/raw offset 均为 `0x1000`，所以本产物的 `.text` VA 可用 `VA - 0x400000` 定位。此简式不推广到 `.rsrc` 等其它 section
- 定义加载器 `0x5a8ee0`：`0x5a9032` 将记录循环索引设为 1；`0x5a9037` 上界 600
- `0x5a904a` 每条处理 32 字段，jump table `0x5a988c` 首目标 `0x5a906f`，调用字符串读取器作为第一个 name 字段
- `0x5a9082..0x5a908c` 将 name 写到 `*[0x640214] + nativeIndex * 124`
- `0x5a9818..0x5a981f` 索引加 1 后顺序继续，没有从文件读取显式数字 ID 的槽位
- 此表地址与 name lookup 读取的 `0x640214` 完全相同，因此原文件顺序第 0 条对应 native slot 1

### 3. 名称查询：顺序、first match、sentinel 终止

完整范围 `0x5a0330..0x5a0447` 已保留。

- `0x5a0359` 取 IAT `0x40110c`；PE import table 将其明确命名为 `MSVBVM60.__vbaStrCmp`
- `0x5a0367` 从 1 开始，`0x5a036f` 最大 600，步长一；定义 stride 124
- 比较当前数据库 name 与 BSTR `0x40edb8`（确认为字面量 "0"）和 `0x40bae0`（确认为空字符串）
- 任一 sentinel 相等时 `0x5a03bb → 0x5a03e2` 立即返回整数 0。重要：这是停止扫描，不是跳过空定义后继续找
- `0x5a03cd` 比较查询名称，`0x5a03d1 → 0x5a03eb` 在首个相等时返回当前索引
- 当前 600 条来源中首次 sentinel 为 native 579，579..600 为 22 个 "0"；A01 所有名称在此之前唯一匹配
- 当前来源中的空查询、"0" 查询或不存在名称最终得到 0。不得 trim、改名、用旧数字补救
- 超过 600 的无匹配路径保留初始 Empty Variant；Python 模型将其对调用方的 I4 转换结果表示为 0，但没有运行 VB6 进行动态验证。当前真实来源在 579 已走显式整数 0 的路径

`LOOKUP_MODEL_TESTS.json` 验证 first duplicate、两种 sentinel 提前终止、不 trim、大小写不改写、未找到、600 上限。模型的文本相等适用于这里已解码名称；不是对 VB6 全部字符串/区域行为的独立仿真保证。

### 4. 地图绑定无旧数字 fallback

完整范围 `0x59e5cc..0x59e855` 已保留。

1. `0x59e5df` 检查 kind == 6
2. `0x59e5e9` 读取该格后面的字符串
3. `0x59e604` 调 `0x5a0330` 名称查询
4. `0x59e610` 通过明确命名的 `__vbaI4Var` 转为整数
5. `0x59e62d` 无条件覆盖地图运行缓存的数字 index
6. `0x59e65e..0x59e660` 结果 <= 0 转失败分支；`0x59e82e` 清 kind，未尝试旧数字 ID
7. 正值 `0x59e71b` 写入实体 `+0x8c`
8. `0x59e7e0` 调初始化 `0x5a0960`；其 `0x5a099d` 从 `+0x8c` 读 native 定义索引；`0x5a0a91..0x5a0a95` 把定义 `+8` appearance 写至实体 `+8`

后续移植应保留原始地图 `monsterId` 原值作为来源字段，另存 `native_definition_id` 与 `extracted_definition_id`，避免破坏原始数据与 provenance。

### 5. appearance 888 的硬边界

`0x5a0eb5/0x5a0ec7` 明确检查 888（0x378），与普通 appearance 分支不同。特殊前缀中 `0x5a0ef2` 调运行库 import ordinal 593；现存 RNG 研究将该 import 解释为 Rnd，本阶段直接验证的是 ordinal/IAT/调用字节，不把未随包提供的 DLL export 名称当作已重新验证。`0x5a0f38` 可以减实体数量，`0x5a0f5f` 可以清占位；因此不可把三条特殊输入当作普通确定性生成。

`Mon/5.lpRes`、`Mon/7.lpRes`、`Mon/888.lpRes` 都真实存在，均验证了 native animated image table 的全部范围与文件签名。这里未做图像像素解码、动作切片、显示评审或使用它们作为运行时资源。888 的存在不代表它可以跳过特殊初始化逻辑按普通怪渲染。

## 刻意保留的不确定项

- appearance888 完整生成概率、全部 RNG 消耗、后续变体/属性覆写/生命周期/最终占位，没有在本阶段建立可执行等价实现
- 普通45条的动作时序、移动、AI、仇恨、攻击、受击、掉落、死亡与重生仍属于后续战斗契约
- A01 解析后剩余 68 bytes，定义文件 600 条后剩余 9020 bytes，均保留且不解释
- loadScript 原文仍为注释 + `#end` + `#NotUI`。本阶段只保存及比对文本，不为脚本执行顺序添加新推断
- 未运行原版程序、Windows/VB6、Godot，未做 native 操作或运行时测试
- 所有检查是来源/结构/反汇编/重建模型层；不能称为完整玩法恢复验收

## 存档范围

仅按 `DELIVERY_MANIFEST.json` 的 `archive_files` 清单加 manifest 本身归档。保留其中的重放脚本、来源 pins、逐条绑定和必要反汇编证据；`local_only_do_not_commit` 中的测试报告及边界测试工具只留在独立研究目录，不进入 Git。来源仓库不是本脚本输出目录；后续若决定把契约安装到主项目，应另开明确的实现变更及验证阶段。

### 建议归档到主项目的位置（由主控后续执行）

建议目的：`Project/art_source/earth_a01_source_contract_v1/`，附带 `.gdignore`，不让 Godot 把研究证据当运行时资源导入。`DELIVERY_MANIFEST.json` 明确列出可归档文件及本地专用验证输出；只复制 `archive_files` 加 manifest 本身。`VALIDATION.json`、`REPLAY_DETERMINISM.json`、`WRITE_BOUNDARY_TESTS.json`、模型测试输出与边界测试工具留在独立研究目录，不进入 Git。

归档后的 verifier 必须使用仓库外 `--out`（脚本会拒绝默认写入来源仓库）：

```sh
python Project/art_source/earth_a01_source_contract_v1/tools/replay.py \
  --repo /path/to/repository --out /tmp/a01-contract-replay
```

必要反汇编片段与 EXE byte anchors 属于项目来源依据，可以归档；测试执行报告不属于运行时或来源资产。本阶段已做二次独立目录重放逐字节一致检查，以及“拒绝仓库内输出”“篡改预期 hash 提前失败”的负例测试。发布仓库在检查前后 Git status 均为空；此目录没有执行复制、提交或推送。
