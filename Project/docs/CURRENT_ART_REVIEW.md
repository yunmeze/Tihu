# 当前美术检视（F6，单树阶段候选）

在编辑器打开 `scenes/earth_current_art_review.tscn`，按 F6 运行当前场景。此入口使用固定原始 A13，不执行剧情、NPC 服务、随机地图脚本、奖励、跳关、传送或存档。默认 F5 仍由本阶段 TreeController 运行自然开场；此更新不把 F5 切换为未验证的 A00 组合。

- 版本标签：`tree-stage-shared-south-v3-candidate`，对应已验证的 (51,70) 单树及 shared-south-v3 执行闭包，不冒用未知 Git 提交号。
- 固定参考 A13 SHA-256：`d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27`。保留原 NPC，没有执行地图加载脚本，因此不是自然开场存档状态。
- 渲染入口：`upright_51_70_world.gd`，开启原 S 步行接地影和该单树贡献。70 个可达 GD 脚本、7 个 shader 与 A13 逐 SHA 校验；继承纹理、原图集、静态身份和 receiver 门全部保留。
- 左键原格 A* 寻路，Shift 跑步，空格停；原 Movement 50Hz 时序/方向/相位/阻挡不变，未覆盖动作继续使用原角色图。
- 四按钮只移动相机：出生区左上角 (2496,960)、南侧 (2112,1664)、南右 (2450,1465)、小屋 (738,400)。F 跟随主角、Home 出生相机；相机不传送角色或改地图。
- F8 在 C24 / 草907 / 既有39 / 原版保留1583 与既有121+57通道间对照。关闭现代地面时撤销新树影 raw sampler、receiver 与 compositor 绑定，仍显示同一组树体 owner；恢复现代地面时重新 prepare 并通过实际树影正门。F8 不是全图纯原版模式。
- 任何必需正门缺失会明确显示“检视不完整，移动已停止”，不把整组回退称为新版。相机仍可查看。角色走出原接地影区域是正常行为，不被误判资源损坏。

## 验证边界

本次 F6 兼容入口已独立通过 check、37 项 headless contract 与 35 项官方 Linux native 检查，正常退出并回收。挂载后先核五个有效资源路径 SHA，再动态加载 F6；默认 F5 仍核对为正式 TreeController。F8 两轮 off/on、树体 owner/RID 不变、新影 raw/receiver/材质绑定撤销与恢复、缺 raw 负例明确停机、固定 A13 与原移动路径均通过。

本轮原生验证使用 Godot 4.6.3、OpenGL 4.5 Compatibility、Mesa llvmpipe（软件渲染）。按钮、F8、跟随、点格、Shift 与停步走实际 Godot 输入路由；这是 `Input.parse_input_event`，没有声称本轮做了 OS 鼠标补验。南侧 on/off/on 三张实际画面均检查，中文状态可读、树体保留、恢复正门成立。原生窗口1180×812，内容截图1082×812，内部 SubViewport2048×1536，逻辑1024×768，不能混称。

单树及 shared-south-v3 另有独立 source/PCK 48 项绘制读回验证，该树开关影子、正常与半像素偏移画面已人工审阅。前版 F6 的31项headless、59项native与实际OS三操作仅为旧3e基线历史记录，不计入上述本轮37/35项，也不替代本次验证。

Windows、音频未测；不是全图 HD 或所有动作逐帧验收。旧 NPC、墙、竹林、棋盘影等未替换部分仍可见。A00 组合变更不在本阶段范围。

## 发布范围

本 F6 小更新只需 controller 与本说明，scene 字节不变；测试 fixture、runner、PCK、图像证据不进入发布。必须与已验证单树阶段 runtime 同时匹配，不能在旧3e资源下假报成功。后续 A00 或其他 runtime 改动须重新核对执行闭包、pin 与 F6 正门。
