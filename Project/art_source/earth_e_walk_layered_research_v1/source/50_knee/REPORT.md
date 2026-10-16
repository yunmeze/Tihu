# 50右膝残甲单次局部编辑及六相研究状态板

## 本轮判断
右膝旧上裤银岛和大金凸片已明显消除，改为同光照黑布裤脚连到原固定新胫。保留为局部结构改善的研究候选，不宣称整体或循环通过。
最终接口仍有浅金/银细边，裤脚呈较尖折线，左膝旧甲残片未在本次许可内改变；新手红褐细边也照留。因此六相板明确标研究状态，不是六相验收。

## 冻结域与一次调用
使用上一轮50实际合成作为输入，原生96×96方形crop=[136,232,232,328] HD4，不放大当新密度。input-native96-context.png、input-native96-guide.png、protected-native96-reference.png三张供唯一一次内置image_gen。
冻结mask457像素，全部在先前7611 union内。手绘多边形与既有union裁交，37点排除：32当前全透明、5原保护opaque；没有应移除残甲位于这些排除点，因此无需扩域。
原保护opaque交集0，原半透明交集15。BEFORE_CONTRACT.json保存多边形、crop、精确mask计数、所有输入hash和合成约定。

raw.png原始1254×1254，SHA256 ebddbf840f63a83322f0bced96a83688ff8920a090bb667baa037357c8889363。
提示词prompt.txt明确只删除上方旧膝残银/金甲，下方固定新银胫保留，不泛称保留所有甲。

## 唯一映射与合成
输出整张crop唯一等比回映96/1254=0.07655502392344497到原生96，再放回[136,232]。没有内容fit、局部拉伸、非均匀缩放或追随raw新胫位置。
raw对裁图其他部位有位置/表面漂移，尤其新胫轮廓和对侧靴，但这些修改全部在采用mask外被丢弃。没有把raw新胫作为底层替换原新胫。
只在457像素mask内取raw布料，原protected层source-over；mask外恢复上一轮50最终RGBA。
- 实际变化449；mask外0；原alpha255保护最终变化0。
- 原半透明最终变化15，正常over，不虚报全保护最终0差。
- 冻结输入hash全部匹配。
- 旧右甲被替换，不再叠旧upper层；保留原新胫。未程序填黑、未重抽。

## 六相研究状态板
six-phase-RESEARCH-STATE-{1x,2x}-{gray,light,dark}.png，六列45/46/47/48/49/50，上原源、下真实当前研究图。每格完整128逻辑；2×仅最近邻展示，不按相位fit。
SIX_PHASE_LINEAGE.json逐相列实际文件SHA256，没有缺相、借帧或镜像。
- 45使用腰only候选，不采用失败斜布桥；原膝缺口明确保留。
- 46真实静态候选，金黄胫甲色差/姿态待审。
- 47密度登记裤候选，裤脚接缝仍待整组审。
- 48密度登记裤候选，膝根凹口/硬边待审。
- 49真实静态候选，臂/布接头痕待审。
- 50本次局部右膝候选，左膝旧甲、新手细边、裤脚折线与既有源姿态残差仍在。

整体身份/动作判断仍须下一轮：六相看得到手摆幅、金属色温和裤形体积不完全一致；本次没有运行循环，也不把静态板当循环通过证据。

## 关键证据
- knee-before-raw-final-{gray,light,dark}.png：原局部／raw回映／固定域最终。
- source-before-final-{1x,2x}-{gray,light,dark}.png：原50／前一失败／本次局部研究。
- frozen-full512-mask.png、input-native96-mask.png、clipped-native512-donor.png。
- BEFORE_CONTRACT.json、PROOF.json、prepare.py、composite.py、six_phase_board.py。

已亲看浅底局部三列、完整六相2×灰底；原参考、既有47/48冻结目录、原纹理文件、生产、GUI、EXE和Git不动。
