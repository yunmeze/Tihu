# 三材料同密度审核：没有贴墙

可审图：`THREE_MATERIAL_SAME_DENSITY_REVIEW.png`。三份原图都为1254×1254 RGB；显示色样为全图等比缩至231px，拟议屏幕周期P=230.7553，对应统一密度5.434328 texels/逻辑像素。下面的重复条没有混边/镜像/调色，右侧是100%原生接缝条。

|材料|形态|周期筛查|当前判定|
|---|---|---|---|
|M1石墨金属|平面拉丝，无对象|FAIL：边跳3.434倍内部，8px均色偏差最高21.572/255|不准入，左亮右暗导致明显接续台阶；保留原FAIL|
|M2混凝土墙|平面细孔混凝土|小WARN：边跳1.074倍，blue边带3.136/255|root已接受为微纹理候选，WARN保留，不混边/重生|
|M3中灰基础|平面较粗骨料，无台阶|数值筛查PASS：边跳1.155倍，边带最高2.575/255|比M2暗，颗粒较粗，等待root审图|

原raw路径分别为：

- `../a13-wall-m1-material-pilot-v1/generated-raw.png`，SHA `d1da199db346ac41b54374ba92b82f02096de047cf7eaf4dfcc123928ce83a3b`。
- `../a13-wall-m2-material-pilot-v1/generated-raw.png`，SHA `6f48ff889bd98646fed0923ba3d3d8e12e57a453c3b95bb4b7926cf6c0d00ebc`。
- `../a13-wall-m3-material-pilot-v1/generated-raw.png`，SHA `c46919ecc4595ccc0620d576ad80b5ab461d7b86d2775e40eb1dd62acefbe5d8`。

每份一次built-in调用，分别保存调用前完整prompt/args/输入SHA与工具输出路径。三份raw各只有一份物理数据，保留工具原文件并在owned目录硬链接；本汇总没有复制raw。小屋参考未改变。先前两次整墙FAIL保留且未重启。

这些是材料色样；并未做2D墙域采样、UV注册、几何alpha/D4过滤、8-owner层序或植物/角色引擎验证。金属脊条/折边/结构板缝/檐下明暗/角段仍要单独设计。不可称三材质已构成可用整墙。

本阶段到此：交root审核M1FAIL与M3颗粒感，等待进一步明确指示；不自动新增生成、颜色处理、混边或贴墙测试。
