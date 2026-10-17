# A01 普通怪物动画契约 v1

这是原版静态研究阶段存档，不是 Godot 实现或运行验收。没有运行原 EXE、Godot，没有修改主仓或执行 Git 提交/推送。

## 已恢复的关键规则

- A01 普通外观为 Mon/5（鹿类，36 个）和 Mon/7（甲壳虫，9 个）；姓名/定义绑定沿用独立完成并按 SHA256 引用的 `a01-source-contract-v1`。外观 888 不在本阶段范围。
- 两包各有 217 个有效 BMP 表记录，普通布局是 native frame 1..216。记录 0 的 BMP 字节与记录 1 相同，但解码前缀是 `[216,0]`，不能当成普通注册偏移。原版资源表使用 `nativeFrame * 8 + 13` 的 VB Seek；native frame 不减 1。只有表项内的 VB 文件指针转文件偏移时减 1。
- 方向为 0=N、1=NE、2=E、3=SE、4=S、5=SW、6=W、7=NW；对应地图 x 右增、y 下增。指令与方向跳表均已存档。
- idle：`4*d+p`，稳定相位 1..4，每 12 个 clock tick 先加相位、达到 5 改成 1；普通 idle 尾部每次到达都写帧。
- walk：布局每方向分配 6 张，但该循环实际发出 `33+6*d+p` 的相位 1..5。先把旧相位 >=5 清 0，再加 1。不能写成六帧循环。q=0/1 时帧周期分别为 4/5 tick。
- attack：`81+6*d+旧相位`，依次 0..5。旧相位 4 进入主要攻击分派；旧相位 5 显示末帧，同时改成 idle、clock=-1、phase=0。特殊攻击种类的额外效果与完整伤害逻辑不在此契约里。
- hurt：`129+2*d+旧相位`，两帧，每 5 tick；若入口 clock=0、phase=0，则发帧 clock 为 5、10。外部受伤入口尚未穷举，不能把这个条件时间线声称为全部伤害场景。
- death：普通死亡入口优先于当前状态，入口重置 clock=0、phase=0，并在同一次 update 发出 `145+9*d`。随后 clock=4..32 发出后 8 帧。终点清占位，存入尸体网格；尸体终帧为 `153+9*d`。本路径不支持“1.2 秒自动消失”的说法。
- 追击移动入口与闲逛入口不同：追击通常 clock=-1、phase=0、保留旧帧；闲逛 clock=-1、phase=1，并落入 idle 尾部写 `4*d+1`。若未被其他逻辑打断，下一次 walk 门限分别从相位 1 / 2 开始。

状态、phase、stored_frame 必须分开保存。原版不总是在改变状态的同一次调用更新显示帧。移动函数也可能在 walk 调用中先改回 idle，而这一调用仍继续走 walk 写帧逻辑。

## 交付文件

- `A01_ANIMATION_CONTRACT.json`：机器可读状态、帧布局、时序门限、入口与边界
- `SOURCE_FRAME_INDEX.json`：两包全部 434 个表项、文件位置、VB Seek、原始前缀、BMP 尺寸及图像字节 SHA256；不转换或重绘像素
- `SOURCE_PINS.json`：原 EXE 和两包原始资源的完整长度/SHA256
- `evidence/EXE_EVIDENCE.json` 与必要反汇编片段：指令锚点、PE 映射、状态/方向跳表、来源范围
- `tools/replay.py`：只读原始来源的可重放生成器
- `DELIVERY_MANIFEST.json`：明确列出归档文件；交付集是 `archive_files` 加 manifest 自身

`local/` 是本地研究、模型验证和日志，全部排除归档。模型验证不是原版执行或引擎行为测试。

## 重放

依赖 Python 3 标准库和 GNU objdump。脚本不导入主仓模块，不安装软件，不执行 EXE/Godot。

```sh
python -B tools/replay.py --repo /absolute/path/to/tihu-legend-recovered --out /absolute/path/outside-source-repo
```

输出必须在来源仓之外，且不能是其祖先；拒绝路径中的符号链接。已审阅的预期指令字节是脚本常量，不会由本次来源重新生成期望值。脚本比较固定来源 SHA256、指令字节、跳表和 BMP 结构，随后生成契约与反汇编。README 与 delivery manifest 是交付包装，不由研究重放脚本复制。

## 明确未证明

- 原版 update 的真实 Hz / 秒数。不能把当前实现的 50Hz 当原版证据
- 完整 AI、完整战斗、受伤入口穷举、复活和命名特殊分支、所有尸体清理机制
- 运行时表现、渲染缓存正确性、Godot 集成与原生 GUI 结果

只把本阶段已证明的字节身份、索引、布局和限定路径规则用于下一步；不要据此一次性接入完整战斗系统。
