# A00 整村预览 v10

这是尚未整体验收的阶段预览。

## 打开方式

用 Godot 4.6.x 打开 `Project/project.godot`，再打开 `res://scenes/earth_overall_village_preview_v10.tscn`，按 F6 运行当前场景。

F5 仍启动原来的 `earth_new_game_candidate.tscn`。已发布的 v9 场景保留，可继续单独打开。

## 本次变化

- 修正三处混层鱼架的 9 个 layer1 切片引用，复用已有 partition 纹理；原有 1013 layer2 切片保持不变。
- 补充原地图 FloorBig10 的两块土地，坐标为 (38,60) 与 (46,106)，复用已有土地纹理。
- 保持其余场景条目和 v9 的 328 项建筑纹理裁切逻辑，不新增 PNG。

岸线、围栏和动作仍未整体验收。这个预览不代表完整第一关完成，也不代表通过 Windows 新检出运行或导出验收。
