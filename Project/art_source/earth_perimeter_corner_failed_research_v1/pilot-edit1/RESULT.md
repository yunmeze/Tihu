# 一次整角编辑：几何未通过，停止

已按批准的四refs顺序、完整已审prompt调用一次image_gen.imagegen，transparent_background=true。实际返回1254×1254 RGBA，固定384世界窗D=3.265625。generated-raw.png保持工具原始字节。

结果：材质设计保持；没有新增灯、蓝光或封端墙。但指定的几何修正没有充分生效，不能进入注册或runtime。

独立确定的支持检验：
- 原矩形支持边界x=72/312；编辑后alpha>=128主体bbox左右约64.92/319.39，仍越出约7.08/7.39逻辑像素。
- 9个原owner矩形并集外alpha>=128仍31944像素，占全部584054高alpha像素5.47%；alpha>=250仍29747像素。上一稿38013有所减少，不等于通过。
- 原低清alpha轮廓支持外alpha>=128为37506像素。仅诊断，没有硬裁。
- 非零alpha有背景细碎杂点，a>=1 bbox=[0,103,1192,1228]；a>=8主体bbox=[211,117,1044,1149]。阈值只统计，没有清除杂点。

结构复核：
- 采用同语义“可见屋面内V终点”读取，source y约171–179，编辑图约151–159，仍不在同一范围。没有再次使用不可靠的35.83旧估计。
- 檐口下沿、墙顶仍不强行提供独立精确位移。人工点和读图歧义见STRUCTURAL_REVIEW.json。
- 顶部轮廓大体保留，墙脚右端及内V仍有位置差；不能通过只修檐口、放宽支撑或把完整raw统一fit来宣称修复。

交付：ACTUAL_CALL_CHAIN.json与prompt_actual.txt，generated-raw.png，same-coordinate-1x.png/2x.png，source-initial-edited-same-window1x.png，measurements.json每owner贡献，STRUCTURAL_REVIEW.json，EDIT_COMPARISON.json。

结论：保留本次失败，停止。未自动重试、未全局fit、未旧mask硬裁、未修改主仓、未跑Godot/碰撞或进入runtime。若要继续需新的几何实现方案与授权；当前raw只可作为材质参考。
