# 一阳837：单画布设计候选，未验收

保留第一次完整生成的原raw、实际prompt和按顺序提交的两张来源图。第二张带来源landmark标注的图是实际模型输入，必须保留；其他review图/诊断代码不进入本包。历史contract原路径作为来源记录，ARCHIVE.json给包内映射。

Root认为脸、双手、坐姿有研究价值，但灰色下身仍有袍毯感，右椅/基座比源扩张约7–12逻辑像素；现代服装和源支撑合同未通过。未native验收、未启用、未进行局部回贴或二次编辑。

整1254方图以预乘alpha LANCZOS统一缩至640方，160逻辑像素固定窗，世界原点(2592,2200)，density4。没有按bbox配准、清alpha、变形或复制四相。源837–840的RGBA、offset与crop相同只证明原版是单静态body映射四源ID，不是四张新动画。本包不把源等价改写为候选艺术验收。

重放：python reproduce.py --project /path/to/Project --out /path/to/new-output
需Python/Pillow；从tracked A13、original manifest和Npc atlas重建源图、核四ID等价、逐字节重建实际primary ref和固定候选PNG，并验证RGBA。第二张实际标注ref原字节保存并验hash，其人工源点读数保存于source-visible-landmarks.json；不以标注替代精确人体真值。无需recovery目录、Godot或联网。图像生成本身不可确定性重放。
