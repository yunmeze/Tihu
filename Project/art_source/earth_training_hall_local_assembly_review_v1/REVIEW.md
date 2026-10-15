# 双阶透明分层联合审

输入为保留的全栋v2及两张局部imagegen原始输出。仅用全画幅固定缩放（512/1254）、原裁片平移及透明材料选择；没有warp、RGB补绘、程序画阶、模糊遮缝。

`full-building-candidate-review.png` 为1372×1147整栋透明候选。`full-building-native-gray.png` 仅换底便于实看；左右 `*-native-seam-review.png` 均按原raw尺寸对照。

`build_review.py` 可复现全部透明分层，`partition-contract.json` 记录每条材料选择/旧阶退役边界。旧左主斜撑保留域从原v2逐RGBA精确复制，而非采用候选缩短的主脚。旧楼梯在替换域退役，避免叠留旧颊。楼体其它像素保持原v2。

24脚样点复测：14个清楚支撑点仍在阶/平台；8个清楚源草地点读数圆全透明；1个原边界不确定点；右侧1个草地代理点在±2 source px内的前沿边界不确定。没有新发现的明确可走支撑悬空。原生行走与排序尚未验证。

父于2026-10-15 08:53 UTC实看原尺寸整楼及左右接缝后，同意保留左上口细线、原主脚压新侧颊的小拐口作为可见残差，进入独立Earth入口候选联合审。该批准不是最终美术/原生验收。后续原30owner候选注册在 `../earth_training_hall_registration_v1/`，不得用整栋单sprite覆盖角色。
