# Hero 攻击 / 受击时序证据（R2 恢复审计）

审计日期：2026-10-15 UTC。范围：当前文件的只读静态证据；不是原游戏运行录像验证，也不是完整战斗等价声明。

## 结论先行

- 当前原 EXE 的 SHA-256 与受击检查脚本锁定的哈希一致；18 个历史指令锚点已用本机现有 GNU objdump 重新逐条核对，通过 18/18。
- `attack = 129 + 6*d + p`、`hurt = 225 + 3*d + p` 均找到当前 EXE 的具体运算及图索引写入地址。公式成立不等于进入动作时立即播放 p=0。
- 受击播放门控使用 actor 的 `+0x1f8c` 计数；攻击播放门控使用全局地址 `0x63f6b8`。不能把参考 JS 的 actor-local elapsed clock 当成两者的原版共同机制。
- `0x61f250` 重置计数和 phase、设置动作，但不写当前图 `+0x1f80`。受击和攻击结束分支都跳过写图。因此这些路径保留已有图，包括结束时的末图；不代表随后所有调用都不会改图。
- 参考 JS 的 hurt 入口保旧图可见；退出立即改为 idle 图。它与原 EXE 退出保图路径存在明确差异。
- 当前 `参考项目/reports/` 不存在。报告生成器中的“已通过”文字、测试代码和预设 JSON 字段均不能冒充本次执行结果。

机器可读证据：`../data/hero/timing-evidence.json`。其中含来源哈希、18 项比较、原始地址段反汇编、已核对事实和未核对边界。

## 1. 来源及证据等级

### A. 本次直接复核的原 EXE 静态事实

来源：`原版游戏/LP传奇单机版_重生.exe`

SHA-256：`21dc753d3aa828fb29dc171e595857be234833edc43a1d80833540ae7e355b84`

读取 PE 跳转表 `0x61e6a8` / `0x61e688`，得到动作 1 → `0x61c2cf`，129 → `0x61c7ee`，225 → `0x61e3a5`。本次没有运行 EXE。

本次采用系统已有 `objdump -D -Mintel --start-address=... --stop-address=...`，直接读取恢复后的 EXE。检查脚本的 anchors 通过 Python AST 读取，未执行脚本。比较只统一大小写、空白和十六/十进制表示，18 项全部匹配。无需安装、网络或 Git 操作。

### B. 当前参考实现及工具代码

- `参考项目/tools/inspect-actions.py`：读取 atlas/index，按给定 base/count 拼图，只取 direction=4。它不读 EXE、不验证计时器或动作入口。
- `参考项目/tools/inspect-hero-hurt.py`：提供哈希、18 个锚点、五段反汇编范围，另有人工填写 rules/boundaries。18 个锚点已重查；规则需要结合完整上下文，不能仅由 JSON 字段证明。
- `参考项目/src/animation.js`：可证明参考 Web 实现如何播放，不能证明原游戏也如此。
- `参考项目/tools/inspect-numerics.py`：提供攻击步长来源范围及 `8-fastAttack+frozen` 解释；其报告内容不是当前报告文件。
- `参考项目/src/combat.js`、`tools/hero-hurt-tests.mjs`：当前 Web 受击入口及测试意图，未在本轮运行。

### C. 历史声明 / 本次未复核

`参考项目/tools/report-hero-hurt.mjs` 内的通过数、截图、浏览器测试、回归、真实帧率和完整战斗效果等，缺少当前 reports 成品支撑。此次没有恢复或宣称这些历史测试结果。本次 18/18 仅指对当前 EXE 指令锚点的重新比较。

## 2. 已定位字段与共用动作切换

以下名称是根据用法赋予的解释，偏移和写入指令是直接证据：

| 字段 | 含义 / 用途 | 证据 |
|---|---|---|
| actor +0x1f78 | 方向 d | `0x61da79`, `0x61e4d2` |
| actor +0x1f7c | 当前逻辑动作 | 两个命中 gate；`0x61f2d6` 写入 |
| actor +0x1f80 | 当前图索引 | `0x61da95`, `0x61e5d5` |
| actor +0x1f84 | phase / 步进状态 | attack tail 与 hurt tail |
| actor +0x1f8c | actor 计数 | `0x618d90..0x618d9f` 自增；hurt gate 读取 |

`0x61f250..0x61f2e1` 的完整函数只重置 `+0x1f8c` 为 0、`+0x1f84` 为 0，并从参数写入 `+0x1f7c`。没有写 `+0x1f80`。所以“设置动作”与“替换已画图”是两个时点。

保图结论仅覆盖该函数及本次审查的退出分支；完整调用链、下一动作第一次写图前的准确等待时长仍需单独审查。

## 3. hurt：入口 gate、延迟、三图及退出

### 敌方命中入口 gate

- `0x5d4163` 与 `0x5d4723` 将 EBX 设为 1。
- `0x5d4460` 与 `0x5d4a20` 比较 actor 动作 `+0x1f7c` 与 BX。
- 非 1 分支跳过受击设置；符合 gate 时 `0x5d4a2d` 装入 `0xe1 = 225`，`0x5d4a35` 调用 `0x61f250`。
- 这证明这些命中路径只允许 idle(1) 进入 hurt(225)。walk/run/attack/cast/已在hurt不能通过该动作 gate，因此该路径不会反复重启已有 hurt。

不要将它简化成“HP 减少即受击”。参考脚本另列吸收、反弹、持续伤害语义；本轮只复核其指令锚点，未重新证明所有伤害数值及完整分支语义。

### 播放门控及帧公式

`0x61e3a5..0x61e3b9` 计算 actor `+0x1f8c` 对 `5 + [ebp-0x30]` 的余数，非零跳过。函数开始处 `0x618d9e` 先递增该 actor 计数。`[ebp-0x30]` 初始化为 0，所定位状态分支 `0x619a47` 把它设为 1。其“冻结”名称来自参考代码，本轮确认赋值和后续算式，不宣称所有状态切换语义已验证。

满足 gate 后，phase 小于 3 时：

1. `0x61e4d2` 读方向；`0x61e4d9` 加 75；`0x61e4dd` 乘 3。
2. `0x61e5d3` 加当前 phase；`0x61e5d5` 写当前图。
3. `0x61e605` 再增加 phase。

所以图索引为 `225 + 3*d + p`，三图 p=0,1,2。

在进入前计数被清零、期间每次执行所审查更新且额外标志固定不变的条件下：

| actor 更新 tick | 普通 | 额外标志=1 |
|---|---:|---:|
| 第一次写 p=0 | 5 | 6 |
| 写 p=1 | 10 | 12 |
| 写 p=2 | 15 | 18 |
| 退出 hurt | 20 | 24 |

首次 gate 前保留前一图；并非进入时立刻写 hurt p=0。50 Hz / 0.1 秒等换算来自参考代码，未在本次独立追到原计时器生产端，不能把 tick 表伪装为实测秒表。

### 退出仍保留末图

`0x61e4b6` 判断 phase>=3；`0x61e4c8` 设置逻辑动作 1；`0x61e4cd` 直接跳到 `0x61e5db`，绕过 `0x61e5d5` 写图。因切换函数也不写图，末张 hurt 图仍在当前图字段中。随后共用尾部还会将刚归零的 phase 加到 1（`0x61e605`）；恢复实现若要逐指令对齐，不可漏掉该细节。

## 4. attack：公式已证，首图与全局门控不能套用 JS

### 索引公式与六相位上界

`0x61da79..0x61da95` 读取方向，乘 6、加 `0x81=129`、加 phase 后写 `+0x1f80`。因此条带索引公式是 `129 + 6*d + p`；`0x61da45` 使用 6 作为退出阈值。

但是 `0x61da16` 在阈值判断和绘图之前先加 phase。对于切换函数刚清零的 phase，仅考虑该 tail 时第一次数值会变成 1，而非 0。不能凭六张图和公式断言“原版进入 attack 立刻画 p=0，之后每八个 actor tick 逐图播放”。attack 的完整入口及 p=0 是否由其他路径写入尚未追完。

### 攻击 gate 的时钟不是 hurt actor 时钟

`0x61c7ee..0x61c808` 的除数为 `8 - actor[0x2076] + [ebp-0x30]`；被除数却是全局 `DWORD [0x63f6b8]`。其余数不为零就不步进。

本次直接核实了这些地址和算式。字段的 fastAttack/frozen 解释来自参考 numerics；全局计数由谁更新、进入攻击时它处于哪个相位尚未审查。因此不能由 divisor=8 推出每次攻击必定从 0 开始精确持续 48 actor tick，或首次 step 必在进入后第 8 tick。

### 攻击结束保末图

phase 自增到>=6后，`0x61da69` 调用动作切换至 1，随后返回，绕过写图 `0x61da95`。这支持结束路径保留当前最后图，而不是同步改为 idle 图。攻击分支中另有 phase=5 条件及大量效果调用；本次未复核完整命中/释放时点，不能拿参考 releasePhase=4 当作原 EXE 统一伤害时点。

## 5. 参考 Web 实现：可借鉴的内容及已知差异

`src/animation.js` 定义 attack base129/count6/seconds0.96/releasePhase4；hurt base225/count3/seconds0.4/leadSeconds0.1。

- `setAction(hurt)` 保存当前 `animationFrame` 为 hurtStartFrame；`animationFrame()` 在 leadSeconds 前返回它，表达入口保旧图。
- 攻击没有同类入口保图处理；直接根据 elapsed 得到 p=0。
- `advanceAnimation()` 将 actionTime 耗尽后调用 `setAction(idle)`；后续 `animationFrame()` 立即返回 idle 索引。hurt 的旧图字段也会被删除。没有原版退出保末图的 latch。
- 两种动作均使用 actor-local elapsed/duration；不是原 EXE attack 的全局 modulo gate。
- `combat.js` 的敌方命中入口检查 player、非反弹、HP>0、动作idle后设置hurt。它是参考实现事实；本轮未运行其测试，也不等于原 EXE 所有伤害/状态门槛均已移植。

## 6. R2 后续验收建议（不是本轮已实现）

1. 资源索引、逻辑动作、phase 和已画图应分别建模；不能用 action 名直接强制重画第一图。
2. hurt 用受控 tick 测试验证进入旧图，5/10/15 tick 的三图，以及20 tick逻辑退出但保末图；额外标志固定1时对应6/12/18/24。
3. 明确测试 idle 可受击；walk/run/attack/cast/hurt gate不进入。伤害数值与动作反应分开测试。
4. attack 首图、全局 clock 对齐和 release 时点仍需更多原EXE调用链证据；在完成前标为 adapted/unverified。
5. 若为最小原型采用参考 JS 的 actor-local / 立即idle做法，应明确记录为适配差异，不能标成原版帧级等价。

本轮只新增此文档和 JSON 证据；没有修改 runtime、原材料、提取器、参考项目，也没有运行测试安装、网络或 Git。
