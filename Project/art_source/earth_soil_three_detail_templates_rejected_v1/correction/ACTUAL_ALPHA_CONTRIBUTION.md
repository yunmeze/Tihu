# failed raw 三槽实际贡献诊断

在root明确追加授权后，仅用Godot直接draw_texture_rect_region将D8 raw槽缩放到96×64世界尺寸，叠到同世界phase的既有AI土底。只导出board_1x.png / board_2x.png（400×296 / 800×592）；没有D2归一资产、没有修raw/alpha或runtime替换。

板三列G2/G3/413；三行分别原源、AI底材、AI底材+raw。G2取394@58,66、G3取395@54,62、413取413@54,60的世界phase。源图各格在两尺度均精确等原tile最近邻。

## 纠正与结论

原raw黑色背景展示的棕色RGB不能单独证明可见底色。实际合成中G3/413没有明显大片棕色蒙底，主要是少量稀疏暗簇；此前仅凭raw RGB的“底雾”印象不作为可见染底结论。

但两者位置仍未通过：G3下方主簇显著向右，413主簇显著向上，新增散点也可见。可直接比较第一/第三行的同局部坐标，不能通过平移拟合救回来。这个失败与右下闲置槽的微小alpha污染是两件事。

G2合成后不是不透明整块土，但加入了分散的较粗碎面/亮暗颗粒结构，而非所要求的克制低频柔斑。不能因透明混合使整体较轻，就改判原细节合同通过。

## 真实贡献数据

native-v1/ACTUAL_CONTRIBUTION.json，比较同phase的第二、三行：
- 1x G2：平均RGB绝对差4.447；1157/6144像素至少一个RGB通道改变≥8，最大139。
- 1x G3：平均差0.980；157/6144像素改变≥8，最大129。
- 1x 413：平均差1.260；167/6144像素改变≥8，最大161。
- 2x对应≥8变化像素为4766、579、678（每格24576）。没有通过少数极值宣称整片严重污染。

原raw的alpha分布/源位置粗框数据在 ../soil-detail-three-template-attempt1/ALPHA_DISTRIBUTION.json、POSITION_ALPHA_DIAGNOSTIC.json：
- G3/413平均alpha2.96/3.44，强alpha≥128为2921/3524原D8像素；绝大多数槽面积透明或低alpha。
- G3原下方粗框仅含该槽2.39%alpha总量，413主粗框只含0.086%，且后者框内无alpha≥128。粗框并非完整语义mask，这些数据只辅助同位置目视。
- unused右下槽5081像素alpha1–2独立列为严格空槽FAIL，不以它替代活跃槽的语义/位置审阅。

本次直接缩放是为实际贡献而作的渲染诊断，filter_linear不是获准生产D2归一工艺；不以本板证明缩放资产质量。alpha诊断阈值仅计数，未用于清除像素。

check/headless首次exit0，5原图实际load，自身完整scene-ready通过；planner官方native两图完成且exit0截图native-v1/terminal-exit.jpg保留。前后SHA一致，无SCRIPT ERROR/ERROR，V-Sync警告原样保留。原strictFAIL不变；不再生，不写归一美术。
