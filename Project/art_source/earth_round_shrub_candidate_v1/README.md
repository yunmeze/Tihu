# Earth 圆灌木第一轮raw：待审

仅143–146中心(57,38)完整主体一张，built-in image_gen一次，无第二次、无注册/切片/runtime。原40冻结资料及首树已冻结文件不改。

raw.png是生成器原文件直接复制；实际1363×1154 RGBA，不是请求的1024方形。保留原生成文件generated_images/exec-1e5633bd-2798-4262-879a-9f146e43503a.png。prompt.txt为实际提示，实际3输入/SHA在measurements.json及输入方案中。

alpha>127有效bbox[7,15,1359,1130]、1352×1115真实像素。对原124×105逻辑范围，有效像素量比约10.90/10.62，满足>=2原始密度，不是低清放大。若后续统一density11，完整raw逻辑范围约123.91×104.91；此处只是几何量级，尚未认可变换或物理根。

仍为低矮圆灌木，无新增树干/木根/花池/地影。手读下缘绿叶带大致raw[440,1060,1040,1120]，±15raw；只表示叶底支撑区域，不能当根或精确地面。原源绿叶带[40,94,95,100]继续作为近似参考。

已按原alpha合成灰/深/浅三底，未见明显独立彩色matte/根红边，不能仅凭透明预览RGB判瑕疵。仍需审：暖黄叶高光较强、左右透明留白非常窄，低alpha触左/右/底边；叶片实机尺度和四owner前后遮挡未经验证。没有为补留白自动重抽。

诊断图在Project/diagnostics/art_source/earth_round_shrub_candidate_v1/{gray,dark,light}.png，不入归档。measure_candidate.py复现原样测量和标准alpha合成，不改变raw像素。ARCHIVE_SHA256.json只列5文件，不含诊断或日志。
