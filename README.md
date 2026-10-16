# Legend / Godot 2D

开发工程在 [Project](Project/README.md)。使用 Godot 4.6.x 导入 `Project/project.godot`。

最新可试玩入口：完整下载并解压仓库，导入工程并等待资源导入完成，然后打开 `Project/scenes/earth_first_map_review.tscn`，按 **F6（运行当前场景）**。这是出生点、南侧道路及东廊的局部美术研究稿，共 178 / 2553 个地块（既有 121 + 东廊新增 57），另新增 24 个完整植物组、81 个 owner；既有样区植被另计。水池 7 / 细枝草丛 3 个 owner 保留独立整组回退。按 1/2/3 只移动相机至东/西/南侧，L 定位水池草丛，Home 回出生点相机；角色不会传送。点击走路，B/P 对比角色/地面，E/R 对比东廊/新增植物，Q/W 对比水池/草丛。重复草纹与外围原素材边界尚未完成美术验收，Windows 未实测。**F5 仍启动原素材逻辑预览。** [启动与限制](Project/docs/first-map-review.md)

**新增可选剧情整合入口（性能未验收）：** 打开 `Project/scenes/earth_new_game_candidate.tscn` 并按 F6，可创建角色，执行原五页开场与方丈、凌云子剧情，转入 A00；A13使用上述局部重制美术。实际地表像素和自然剧情链已验证，但当前 Linux/llvmpipe 前台测试仍有明显低帧率与点击延迟，正在修复，不能视作流畅试玩或首关完整验收。默认 F5 不变，Windows 未实测。详见[整合入口及已知限制](Project/docs/earth/optional_opening.md)。

须保留整个 `Project` 文件夹，包括编辑器文件面板中隐藏的 `art_source`。这是 Godot 源工程，不是可直接双击运行的 Windows 游戏安装包；Linux / Godot 4.6.3 已做有限技术验证，Windows 尚未实测。

当前版本是重建中的分阶段预览，默认可检查原版 A13 场景、走路和遮挡。可选场景提供屋门传送和两名 NPC 的开场对话候选；完整地图加载、战斗、背包界面和科幻重制美术仍在恢复中。各入口及已验证范围以 Project/README.md 为准，数据文件存在不代表所有玩法已经接入。

原版游戏与参考项目目录保留为解析与设计参考；Godot 工程不需要运行其中的原版 EXE。

每个已验证小阶段保存在 Legend 分支历史中。测试、临时文件和引擎缓存不随工程上传。
