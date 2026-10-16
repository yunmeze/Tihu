# E 步行研究稿对照入口

这是可选的美术查看场景，界面持续标注“研究预览，未完成实机验收”。它不接入普通玩法，不代表动作、美术或原生窗口验收通过。

## 使用

Godot 4.6.3 导入 `Project/project.godot`，单独打开 `scenes/earth_walk_review.tscn` 后按 F6。也可在仓库根目录执行：

    godot --path Project res://scenes/earth_walk_review.tscn

空格暂停/继续，S 切正常/四分之一速度，右箭头暂停并前进一帧；也可点击按钮。六帧顺序为 45–50；正常每帧 7 个 physics tick，使用项目现有 50 Hz，故 0.14 秒/帧、0.84 秒/轮。慢速每帧 28 tick，只改变这个查看器。切速度或单步重置帧内计数，暂停保留计数。此节奏来自现有/reference clip 元数据，不是独立 EXE 时序或运动连续性证明。

两边都完整显示 128×128 逻辑画布，固定三倍显示。左侧来自 `art_source/hero_e_walk_source_r8/source-45.png` 至 `source-50.png`，已含原始 body/head 合成及偏移；不另加头部。右侧 HD4 512×512 映射回相同逻辑画布，root (64,256) 对应逻辑 root (16,64)。十字只标根点，不代表脚底接触。无裁剪、自动居中、逐帧缩放拟合或移动修正；两边用相同最近邻采样。窗口伸缩统一缩放整页并保持比例。

当前研究选择固定为：
- 45：`earth_e45_vertical_leg_research_v1/45-HD4-CLOTH-CLEANED-RESEARCH.png`
- 48：`earth_e48_vertical_leg_research_v1/48-HD4-BOUNDED-DONOR-DIAGNOSTIC.png`
- 46、47、49、50：`earth_e_walk_layered_research_v1/<ID>-HD4-RESEARCH.png`

这些是 `art_source/` 下的原文件，未修改像素。48 仍是 bounded-donor diagnostic，保留研究限定，不代表正式选用。各相位仍需检查材质、边缘及跨帧连续性。加载前检查全部十二张原图/研究图和尺寸；任一缺失、解码失败或尺寸不符时，两边全部停用并明确显示错误文件，无部分播放或旧版回退。

此入口按源工程方式直接读 PNG，无需这些研究图的导入缓存；独立导出包须另行配置包含所需原始 PNG，尚未验证。中文字体沿用工程 SystemFont 方法，优先 Noto Sans CJK SC，亦列 Microsoft YaHei/SimHei/PingFang SC；本次 Linux 环境已确认 Noto Sans CJK SC 存在，未捆绑字体，其他机器须有可用中文字库。

默认 F5、现有 `earth_sample_preview.tscn`、玩法代码、项目时序、原版游戏及参考项目均不变。本次仅可进行 headless 解析和逻辑检查，未完成原生窗口视觉验收或 Windows 验证。
