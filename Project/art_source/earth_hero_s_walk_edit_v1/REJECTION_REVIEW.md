# S六walk局部动作/衣甲编辑：失败并冻结

一次获批编辑已执行，无自动重试。raw-edit-v1.png保留工具完整原输出，不擦背景、不扣图、不替换alpha、不拼旧肢体。普通S walk保持原source，未送此编辑结果native，未晋升runtime。

## 直接失败

输出仍1536×1024，但alpha范围4–253，透明像素总数为0。旧raw原有1,344,644个完全透明像素，在新图中全部变为非零alpha，其中410,008个≥128。灰底可见大面积棕黑块状背景污染，不是查看器显示棋盘，也不是单纯边缘色晕。候选无法作为透明角色资产。

新银腰侧带基本保留，外腿细长片仍见；暗靴材质有局部变化，但无法宣布身份回归通过。动作几何外观看不出足以批准的61/62改善；不能以此模糊视觉判断编造新骨骼结论。

## 登记和测量诚实边界

已原样复制旧registration-v1.json为frozen-registration.json，SHA与实际请求冻结值匹配。复用旧scale0.2002896386与逐相translation，直接生成body-density4-REJECTED-DIAGNOSTIC.png及源/旧/编辑/idle同逻辑板；没有重新fit或逐相归一化。该诊断保留所有污染，不是运行候选。

初尝试alpha254读取固定头/靴ROI，以避开背景污染，但角色自身也没有alpha254像素，测量无法成立。已明确记录这次失败并将新轮廓/相差数值设为null，而不是降低阈值把背景读成脚，也不偷偷借旧mask清洗结果。旧raw/source六相原读数完整保留于EDIT_REVIEW.json。没有可靠新身体alpha边界，不能用全画布非透明bbox估计主体密度或声称新相位已修好。

## 复核文件

- raw-edit-v1.png、prompt-v1.txt、request-v1.json：真实生成记录和输入SHA
- frozen-registration.json：旧登记逐字冻结
- EDIT_REVIEW.json：透明污染定量、旧相位测量、新测量不可用原因
- review_edit.py：可复现原登记诊断与透明统计，无清洗
- MINIMAL_SHA_MANIFEST.json：显式归档清单，排除diagnostics

灰底/对照位于Project/diagnostics/earth_hero_s_walk_edit_v1：raw-edit-gray.png、source-old-edit-idle-same-logical-1x.png及2x、FAILED-loop-and-idle-2x.png。

父级指示本轮之后暂停S生图，等源实际身体边界/去旧衣纹理的输入研究证据再决定；本包不开展该研究或自动继续生成。没有Git、GUI或普通world更改。
