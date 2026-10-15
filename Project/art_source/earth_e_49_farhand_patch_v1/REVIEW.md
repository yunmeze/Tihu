# 49远手极小补片研究
一次raw已保存，SHA0328a213234a9b420bda0a5bb4f6c30ea6a0251c4b30f89128b7515aae113d45。只输入批准context[435,460,500,530]。原尺寸请求65:70，实际raw1302×1208，比例不符。

未非等比硬fit：仅宽度确定s=65/1302，顶部/左侧对齐，映射高度60.307，底部余9.693像素透明。冻结替换mask位于crop y16–55，全部被该映射覆盖，因此可完成有限mask研究。外围金属位置/衣料纹理有漂移，未用其重fit，不采纳mask外输出。

按冻结粉mask合成，内缘1rawpx半权重，mask外RGBA变化0，raw y>515变化0，现rigid肩解/core/arm层完全不变，脚部HD4 y>=248变化0。保存实际mask、raw、同尺度映射、合成、来源与PROOF.json。此文件是合成研究，不是生成器原生完整人物。

亲看三底与接头：旧裸指和前凸尖突明显去除，未变成新大侧甲或整手大小裤筒。最上缘仍有小黑袖口状边缘/扣状残形，部分来自固定mask之外及1px边缘混合；没有擅自扩大mask。新细布纹与旧低密度裤料存在接缝差，当前只给父级审，不自行通过。先前近手补片左侧鼓包问题仍在，本次不处理。

诊断Project/diagnostics/earth_e_49_farhand_patch_v1/：
- input-versus-width-only-map.png：比例漂移与等比留白
- farhand-before-after-{gray,light,dark}.png：局部三底
- joints-before-after-{gray,light,dark}.png：完整肩腰接头
- source-before-after-{gray,light,dark}.png：源、前稿、本次49
- pixel-provenance.png：粉色本次mask支持，绿色前稿像素

不自动追加生图，不runtime/Git/GUI。
