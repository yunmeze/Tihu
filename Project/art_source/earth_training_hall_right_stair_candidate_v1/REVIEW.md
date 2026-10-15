# 右阶局部候选 v1

2026-10-15：一次已批准的内置 imagegen 局部编辑，实际1254×1254 RGBA。

- raw SHA256：`02c406984828c636887fc64d82e7292cede74581e2056b12e2d14c5a1ed34495`。
- 实际 prompt 和调用前输入hash已保存在 `prompt.txt`、`generation-input.json`。
- 唯一归位为 `raw_v2 = local*(512/1254)+[850,635]`，未做bbox/控制点重拟合。
- 7个明确原支撑脚点仍是实阶/平台，4个外侧源草地脚点在完整读数圆内透明。

## 右下草地代理点的正确结论

(74,37)第二脚中心在局部原始输出 alpha=84，±2 source px读数圆中47.2%像素alpha>128。它没有达到“完全透明”。但这不足以认定超预算越界：固定映射下，距新台阶 alpha>128外轮廓的带符号距离仅约 **+0.112 source px**（正为外侧，边界采样误差约±0.10 source px），落在最低阶竖直前沿的外边界附近，而非明显深入踏面。

父审要求区分低清原图的±2px读数预算与实际可走支撑。故记录为**边缘不确定，允许候选联合审**，不再为了消除抗锯齿追加生成。此结论没有改变原flags、可达路径或owner。注册/原生联合审仍须复核明确支撑悬空、踩侧颊和明显扩大阻挡。

复现：`python Project/art_source/earth_training_hall_local_stair_plan_v1/measure_local_candidates.py`。透明分层合成证据在 `../earth_training_hall_local_assembly_review_v1/`。没有改runtime，没有生成外部地影。
