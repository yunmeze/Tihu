# 圆灌木单实例完整画布分层，父级待审

仅143–146中心(57,38)，没有接runtime、推广或新增地影。uniform density11，scale1/11，raw world左上(2695,1141)。按近似下缘叶带对位：候选raw[440,1060,1040,1120]映source-local[40,94.36,94.55,99.82]，接近源[40,94,95,100]；新手读±15raw。不是物理根或bbox底锚。

alpha>127完整主体world[2695.64,1142.36,2818.55,1243.73]。源全范围含影[2695,1143,2819,1248]；新最高叶尖只较源bbox高约0.64逻辑，底仍在原包络内；未见明显新增高树干/高障碍。原alpha不等于碰撞；细叶轮廓仍需父级审及runner前后遮挡确认。

四片全部1363×1154，同world起点/scale；像素按最近原cropped owner矩形分配，平局原draw顺序。所有RGBA包括透明RGB恰好一次，重读PNG重组逐字节相等。原143y35/flag0、144–146y38/flag-1及稳定序保持。完整canvas直接避免树crop相位差，但density11→2×实际GPU仍需测，不能预先称零差。

diagnostics/art_source/earth_round_shrub_registration_v1内source/candidate_gray_1x、_2x及alpha_overlap图从各自源直接采样；真2×不由1×放大，均不入SHA归档。overlay青源含旧影、粉新、灰重合。

父级先看registration及1×/2×套合，再交runner。运行准备须核完整4身份和PNG/hash/尺寸，同组成功抑原4（包括棋盘影），失败整组回退。保留原A*；检查143早序、144–146后序间角色关系。无新影，无物理根证据，不改flags。

build_registration.py可复现完整画布切分、校验、诊断；ARCHIVE_SHA256.json列9文件。没有第三方软件/GUI/Git操作。
