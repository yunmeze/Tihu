# G3 双细痕一次候选

严格位置/尺度合同FAIL，保留原RAW等待root单独美术评审，未重试或矫正。来源/定位纠错见SOURCE_REVIEW.md；旧证据未改。

一次内置image_gen调用，真实完整prompt+5refs见ACTUAL_TOOL_ARGUMENTS.json和INPUT_PLAN.json。参考前后SHA全部一致。RAW.png为1536×1024 RGBA，actual density按96×64重新计算x=y=16。SHA256：101415def231fd04d1aba2a9b035c02057180f57ebf41c0ca6ed584371471630。

上组α≥128 bbox（游戏1x）[4.6875,5.0625,11.5,7.5625]，质量中心(8.467,6.514)，较目标(7,5)右下约1.5px。全alpha质量4.142px²，其中允许框外质量19.13%。上组最浅alpha也未触顶，不能跨到上邻413。

下组α≥128 bbox [30.9375,51.6875,41.5,57.0625]，质量中心(35.300,54.322)，主体中心近目标(35.5,54)。全alpha质量13.800px²，允许框外质量12.70%。右下x40附近出现独立小碎痕，与本轮明确排除该处的选择不一致；不能声称精确遵循已冻结prompt。

美术观察独立于严格合同：两组保持很远的间隔，颜色为低调暗褐/红褐地表碎痕，实际1x不显著，不像大草堆或石堆。灰底真实alpha合成未看到明显大棕底。alpha1零散尾使全支持框[65,75,1386,982]远大于可见内容，不能用该框认定大污渍。阈值只为诊断，从未用于处理。

合成：整RAW统一premultiplied-alpha LANCZOS采样为96×64诊断。背景用既有AI土/草材料density2、世界周期384、G3@54,62的world(2592,1984)相位crop[576,128,768,256]再统一0.5采样。COMPOSITE_soil_1X.png和COMPOSITE_grass_1X.png为真实1x合成；SOURCE_LEFT_AI_SOIL_RIGHT_TRUE1X.png左原tile、右AI土合成。8X_INSPECT仅最近邻放大。不等同runtime实际地面混合与集成截图。

未改主runtime、未修改413已接受RAW、未生G2对象、未裁图/清alpha/独立平移缩放救框。等待root选择接受为新美术设计或拒绝，未经下一步授权不做集成。

## Root美术接受与交接
root已接受为低调高清土面细痕设计候选。严格合同FAIL、上组约1.5px偏移及下组额外x40碎痕均保留不改判。授权下一步仅完整D16原395@54,62注册预览，先替旧土底再叠新痕。minimal_asset_package已交stage_pure_soil_reuse；完整raw/refs/prompt/metrics/registration与SHA清单齐全。未修改主runtime。
