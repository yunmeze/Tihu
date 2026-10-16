# Legend / Godot 2D

开发工程在 [Project](Project/README.md)。使用 Godot 4.6.x 导入 `Project/project.godot`。

最新可试玩入口：完整下载并解压仓库，导入工程并等待资源导入完成，然后打开 `Project/scenes/earth_first_map_review.tscn`，按 **F6（运行当前场景）**。这是出生点和南侧道路的局部美术研究稿，仅替换 121 / 2553 个地块；水池和细枝草丛研究稿已接入此局部试玩；按 L 定位查看，Q/W 分别切换原版对照。点击走路，B/P 对比角色/地面。**F5 仍启动原素材逻辑预览。** [启动与限制](Project/docs/first-map-review.md)

须保留整个 `Project` 文件夹，包括编辑器文件面板中隐藏的 `art_source`。这是 Godot 源工程，不是可直接双击运行的 Windows 游戏安装包；Linux / Godot 4.6.3 已做有限技术验证，Windows 尚未实测。

当前版本是重建中的分阶段预览，默认可检查原版 A13 场景、走路和遮挡。可选场景提供屋门传送和两名 NPC 的开场对话候选；完整地图加载、战斗、背包界面和科幻重制美术仍在恢复中。各入口及已验证范围以 Project/README.md 为准，数据文件存在不代表所有玩法已经接入。

原版游戏与参考项目目录保留为解析与设计参考；Godot 工程不需要运行其中的原版 EXE。

每个已验证小阶段保存在 Legend 分支历史中。测试、临时文件和引擎缓存不随工程上传。
