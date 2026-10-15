# 竹组 C右外叶扇：一次局部修订，AC候选

仅候选研究，B暂缓。以已保留A合成图为艺术基底，原source为同尺度几何参照；一次image_gen调用，无自动重试、owner分片、生产或source/flag/影更改。A和V2原文件不变。

## 冻结方案与实际合成

调用前冻结raw[354,100,1254,1000]的900×900正方形窗口，含C区域外足够上下文。使用既定C editable扣除guard/hold、先前A区域；另加四接点圆：(946,325)半径14，(884,420)半径16，(790,470)半径14，(862,895)半径16。12px羽化完全在editable内部。固定最终mask SHA102f8a0c63cb2a69a01e95ae3c27a42645093940371e76b2050159ab3c5da452。

原生模型输出1254×1254，兼容900方窗；唯一均匀换算900/1254，不自由fit内容，不改变已有density3.0663605941或世界原点，不非均匀变形。经过预乘RGBA固定mask回贴，所有weight0像素直接恢复A基底原字节。模型原始donor的对应保护区有265560像素不同，因此不能直接使用donor或称模型遵守像素锁。

## 结果

C范围alpha128覆盖由46228降至34624，减少25.10%；源同区28966，候选为其1.195倍。整组近似覆盖比由A的1.373降至1.338。右缘由raw1058收至999，对应从源外扩13.88逻辑px变为内收5.36px。主要右倾竿仍锁定，侧叶扇更轻、更接近源的外缘走势；5.36px残差仅作明确自然轮廓差异供root判断，不据此自动否决或另抽。

A区域逐RGBA0差，冠顶+12.34逻辑px的已知小顶梢自然残差完全未变，未追加追尖。B左侧仍沿原基底保留，没有跨范围减密。

## 保护/端点/接枝

以下区域改变像素数均为0：C最终mask以外、主竿fixed_guard、no_cut_hold、四连接保护圆、先前A最终编辑区。六个半径20px端点保护圆内RGBA均严格不变，冻结六端坐标不变，无重新fit。

注意区分圆与外包方框：第6端(862,903)的41×41包围方框有20个角落像素发生批准范围内变化，因此它的方框比较为false；这些像素在半径20保护圆外。实际保护圆变化数为0。没有把较宽诊断框的false隐去，也没有把它误称为端点移动。

四接点局部前后图已实看。未见整根断裂或齐底，右外上梢的侧枝更短/更疏，叶扇仍沿倾斜竹竿相接；局部枝叶细节是生成替换，不是源绘制像素复制。固定数据0差不替代根的接缝视觉认可。未知交叉hold区域未切空，也未从其它竿复制木段填洞。

## 三底与审图

C窗口白/灰/暗三底已查看，未见新地面或落影。A外原有极低alpha尾迹照旧保留；本次未进行整图alpha阈值清理。可见侧叶没有硬裁成源阶梯轮廓。

Project/diagnostics/art_source/earth-bamboo-b-right-fans-edit-v1/
- source-v2-A-AC-full-same-logical.png：四组完整同2px/逻辑单位，固定坐标，不重新fit。
- source-A-AC-native-window.png：源/A/AC同900原生窗口。
- connections-before-after-2x-analysis.png：四个连接点前后；末尾空栏只是复用诊断画布，非第五接点。
- C-window-on-white.png、C-window-on-gray.png、C-window-on-dark.png：C窗口三底。
- composite-on-white/gray/dark.png：完整AC叠底供额外查看。

均为额外诊断，不是768×512→1536×1024运行时截图。路径/遮挡/owner切片尚未验收。

## 保留文件

generated_crop_raw.png SHA4b2a863865bce1746f9c2880cc01fe0509249b669a67418fd88e0af5c5f5f0f9。
composite_candidate.png SHA36731fe0e2ffad2ee8c6772ff8433b14d60fb66f4ae1b5a4455251815eb858c2。
实际prompt、输入SHA、原生输入/源裁图、事前契约、固定mask/连接保护、测量和再现脚本均保留。UPLOAD_MANIFEST明确列必要项目文件，不包含diagnostics/cache/temp，也不表示已上传或晋升。等待root决定保留AC或回退；不自动启动B或其它生成。
