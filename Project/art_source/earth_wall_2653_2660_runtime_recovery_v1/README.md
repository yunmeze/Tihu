# A13 围墙八 owner：恢复后的独立 runtime 候选归档

这是从已发布的完整美术源重新构建并接线的候选，不是找回的旧 runtime 二进制。归档建议位置为 `Project/art_source/earth_wall_2653_2660_runtime_recovery_v1/`。根 `.gdignore` 隔离整个归档；仅保存这里不会启用候选、修改默认场景，或改写父类 pins。

## 精确内容

- `runtime/Project/` 恰好 13 个文件：8 张 owner PNG、1 个 registration、3 个独立脚本、1 个独立 scene。
- `RUNTIME_FILES_MANIFEST.json` 保留 freeze-v1 的逐文件 SHA256。路径相对于 `runtime/`。
- `ORIGINAL_SOURCE_REFERENCE.json` 引用已有 `art_source/earth_wall_2653_2660_candidate_v1`，列出原源包文件及 35 项输入闭包；不重复复制原始生图、原图集或完整仓库。
- `VALIDATION_STATUS.json` 区分已完成的 CPU/静态检查与尚未执行的 engine/native 检查。
- `ARCHIVE_MANIFEST.json` 明确列出本归档所有内容；仅自身不做自引用 hash。
- 不含测试脚本、截图、运行日志、临时文件、Godot 导入缓存或历史失效源副本。

## 固定边界

仅 A13 中以 18,17 为根的原八 owner：2653@18,17、2654@17,18、2655@18,18、2656@16,19、2657@17,19、2658@15,20、2659@16,20、2660@15,21。左侧 14,21 同族、右侧墙角以及前景 Plant274 不替换。四个 flag0 尾片全部保留，源 alpha、碰撞、排序、投影及阴影不变。

继承现有 upright_51_70 / TreeWorld 控制器链；八片在原 `_draw_frame` 调用位置替换。prefilter early_source 仍经 `_source_entry` 的虚调用进入该位置，无需改潜在 owner 集。准备期固定源/资产 SHA，绘制期分别检查 live map/frame、raw objects 和实际 ordered/cache 流的八 owner 精确身份与唯一性。任一不符，全组回退父类原帧。owner-origin 检查也拒绝不同 order/layer/y、动态 index 和数值转换产生的别名。

PNG 直接 decode → RGBA8 → ImageTexture → CanvasTexture，nearest、禁 repeat、无 mip，D2 以 0.5 显示。资源改变按 generation 撤权。2654 原 original-height222 / crop_y1，对应世界左上 y387。调制为 Color.WHITE，不触发既有 house 特殊颜色路径。没有新增 candidate_item 或 NPC-hit 分支；NPC 遮挡继续使用原源整数像素 alpha >= 0.1。

## 已验证与待验证

原 35 项输入 SHA、声明 D2 PNG/RGBA SHA、八片重组、全部 alpha 和 1978 个原生尾片非零像素均匹配。24000 点 CPU nearest 采样零差异；144 项独立 Python 路由模型及静态核查通过。这些 CPU/静态结果不作为引擎证据。2026-10-17 已另外使用官方 Godot 4.6.3 完成最小 check-only 解析：三脚本及候选 scene 通过，exit 0，5.61 秒，无 ERROR/WARNING，进程已回收；原始 shadow 与13个新增文件字节均未变化。行为、native 图像及 hit-test 尚未运行。

原 Wall 导入仍有 `process/fix_alpha_border=true`，并非未经导入的 CPU PNG。同一继承控制器最终以 LINEAR TextureRect 呈现 D2 viewport，这个边界没有改动，也尚未核验。候选只保证自己的 CanvasTexture 是 nearest，不将最终屏幕称为全链 nearest。

顶部周期亮带/面板调制与缺少精确下沿接触暗部是已接受的有界美术偏差；完整 cap 的旧失败仍是失败。没有重新生图、补阴影、扩展全墙或宣称现场融合完成。

后续由唯一 engine 协调者执行行为、native D2 图/NPC-hit 和原场景回归，最后看 A13 同机位 D2 截图，重点包括顶部亮带、面板缝、左右旧墙交界及 Plant274 遮挡。测试夹具另行保留，不进入此用户源归档。

## 候选启用方式（已安装到独立副本并完成最小解析，尚未实际运行）

在拥有完整且运行字节未改变的已恢复 Project 的独立测试副本中，将 `runtime/Project/` 的这 13 个新文件按 manifest 放到对应 Project 路径，保留原父脚本和默认 main_scene。显式运行 `res://scenes/earth_wall_2653_2660_candidate.tscn`。其它地图继续使用父工厂。

此增量不构成独立完整工程或已闭合的导出 PCK。直接 FileAccess 读取的源 PNG/JSON 与 pinned 脚本必须由后续导出闭包显式包含；不能假设既有 export allowlist 已收录新资产。

## 可重建性

使用原已发布源包 `rebuild.py --project-root PATH_TO_COMPLETE_Project --out FRESH_NONEXISTENT_OUTPUT`。固定验证环境为 Python3.12.14、NumPy2.3.5、Pillow12.3.0。重建所需依赖来自原源闭包，无网络/生图步骤。期望 body PNG SHA256：`4815aed4c9c0eaec20107010fd0cd6759e739c0a77acb2794d080aa005142587`。

源重建与本次 staging 均拒绝路径任意祖先的 symlink，使用 fresh 输出/独占创建，不覆盖既有证据；恢复主仓未被本工作改写。
