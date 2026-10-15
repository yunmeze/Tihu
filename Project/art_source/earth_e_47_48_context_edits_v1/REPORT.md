# 47/48 独立完整上下文局部编辑：两次各一调用，均失败

## 结果
两个相位各独立执行一次批准的局部编辑，没有孤立裤sheet，没有重试。raw可见黑布补全了原缺口，但工具把整个角色显著放大，因此不能按预定原画布坐标取裤料。固定合同回贴在裤域采到了错位手/护甲和躯干部位，均不通过。没有通过重新缩放内容或移动接口隐藏失败。

## before contract
47/48各子目录保存：
- input-context.png：共core＋合法臂＋本相固定胫靴＋旧上裤/旧手孔上下文
- input-source.png：各自原源完整128同4×
- input-union-guide.png：精细局部上裤union
- fixed-union-mask.png / old-remove-support-mask.png / new-support-mask.png
- protected-original-layers.png：原始共core/臂/胫纹理层
- BEFORE_CONTRACT.json：调用前实际腰端、两胫根、隐藏2–3逻辑搭接假设、源图SHA、范围与合成规则
- prompt.txt / request.json：实际短约束，明确右向侧视、真实补齐两胫根透明断口，47窄经过、48相反纵序短展步，不能镜像45
47 union6317像素，含400原半透明保护位置；48 union6648，含402。实色alpha>=128保护交集均0。所有输入均调用前亲看。

## 原输出及映射
47 raw1254² SHA ce6c4a56e0a7f8dbb54c6246d04301cb8e7528b5daa7df612729056e7a938613。
48 raw1254² SHA 26ddaeebfc4a5b79f9a2a35276c82fb8640ef61a541412a01a97f78dfd51611a。
两者均按预定全画布512/1254=0.4082934609250399映射，平移0、旋转0，没有内容fit。
47原实色bbox(106,59,209,358)→映射raw(91,58,228,432)，高299→374HD4。
48原实色bbox(71,63,246,345)→映射raw(53,56,308,452)，高282→396HD4。
bbox仅量化明显整体漂移，不证明纯统一缩放，更不能据此自行调整素材密度。raw的姿态表面可能同时改变。true transparent alpha0分别1392532/1343852像素。

## 回贴与保护
仅union内使用mapped donor，并将原protected-original-layers正常source-over在其上；其余恢复原上下文。
47最终变化5576像素、48变化5358；二者union外最终RGBA变化0、原实色保护最终变化0、原纹理层RGBA变化0。
47/48分别386/340原半透明最终像素改变，诚实记录为正常over结果，不误称0差。
mapped raw在union外24917/37359像素变化均丢弃。但固定裤域内因全人尺度漂移误采衣甲/手，恢复域外像素不能救这个根本问题。此回贴仅保存失败证据，不是可用艺术。
文件mapped-UNMASKED.png保持实际映射；47/48-HD4-FIXED-CONTRACT-RESEARCH.png及128版标研究，不交普通运行。

## 亲看诊断
Project/diagnostics/earth_e_47_48_context_edits_v1/
- 47/48-source-context-raw-composite-{1x,2x}-{gray,light,dark}.png：各自源/原上下文/全图映射raw/固定合同合成
- 47/48-joints-{gray,light,dark}.png：腰手膝接口
已亲看两raw及完整2×灰底，未掩盖错误。保持45/46/49研究候选和50独立worker目录不变；不再单点扩mask或自动重抽。本轮到失败冻结为止。
