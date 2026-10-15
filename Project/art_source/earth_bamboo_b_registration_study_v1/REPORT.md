# 首组 (78,53) AC 七 owner 注册研究

## 结论与冻结
研究候选，未安装生产、未开 GUI，未运行 GPU。AC 原图与全部原始生成/编辑输入、prompt、mask 的 SHA 见 FROZEN_ART_LINEAGE.json。raw_frozen.png 是 AC 字节副本，SHA256 为 36731fe0e2ffad2ee8c6772ff8433b14d60fb66f4ae1b5a4455251815eb858c2。原生1254×1254；density=3.066360594075836，统一scale=0.3261195052962738，world origin=(3412.8449703437527,1435.9874544212582)。无再拟合、拉伸或擦低 alpha。顶梢12.34逻辑像素缺高与右缘内收仍为已知自然轮廓残差。

## 分片依据与源字段
直接原 LP 解码/crop、实际 A13 cell 四个 short、atlas RGBA 与源合同核对。身体6片在源图是真实横向不重叠条带，左至右317,319,321,322,320,318；源组x边界31,79,127,175,223，对应world3504,3552,3600,3648,3696。因此分片沿原条带，不猜frame顺序、不制造统一根。原六端仍保持既定深度。

316是烘焙影，只在完整7-owner整体替换成功时空置；任一字段/纹理失败必须原7-owner整体fallback。该事务规则只是研究合同，尚未接入加载器。source_guards.json保留cell/sourcecell/flag/layer/sort_y/order/offset/crop/尺寸及源SHA。guard_failure_cases.json是独立Python守卫模拟：合法组通过、15种破坏均拒绝，不能代替运行时守卫验收。

6个身体纹理均为1254全canvas；分片整数切点280,427,574,721,868，以像素中心归属。所有像素含alpha0的隐藏RGB恰归属一次，整数RGBA重建完全一致。原生CPU source-over的alpha和可见RGBA一致；3598个alpha0但RGB非零的像素在合成器被丢弃，因此不能宣称source-over全RGBA逐字节相等。这些隐藏RGB仍原样保存在raw/owner文件中。

## 非整数采样风险，必须交给runner
全canvas避免crop边沿取样，但预切alpha在线性过滤后分别source-over仍可能出现接缝。五条实际连续边界为279.5141908897309、426.699499405371、573.8848079210111、721.0701164366512、868.2554249522914 raw像素。boundary_sampling_risks.json列出每条边4列及每300行区间低alpha分布、取样位置和理论缺口。最大半texel理论alpha缺口分别约62.26/62.75/62.75/62.75/62.51个8-bit单位，并非实测GPU。

427和868附近穿过可见厚竿；其余边也穿叶/细枝，不是透明安全通道。见独立diagnostics中actual-partition-boundaries.png及原生不拉伸seam-material-native-y240-1120.png。不得用手擦缝或阈值删除低alpha掩盖问题。

## 候选方案2：完整纹理采样后归属discard
post_sample_ownership.gdshader 与 post_sample_ownership_contract.json 是独立研究代码，未编译/运行。每片用同一个完整raw_frozen.png，同全canvas UV、原点、scale、四边形；线性采样完整纹理后，根据UV.x*1254的连续raw坐标作[begin,end)硬归属。左至右六区间分别为[0,e1)、[e1,e2)、[e2,e3)、[e3,e4)、[e4,e5)、[e5,1254)，边界归右片。316无绘制。每个owner单独ShaderMaterial参数，但同纹理资源。白modulate、无region/atlas/flip、centered=false，滤波/重复/mipmap/import设置与whole对照一致。shader明确unshaded/blend_mix；whole也用相同shader与[0,1254)全区间。

预切方案在边界混合两片被削弱的alpha；后采样方案在理想同UV位置只让一个owner提交完整采样值，可避免这项缺口，但不能据此宣称GPU已通过。六个draw的UV浮点插值、不同transform/snap、renderer精度、屏幕像素中心、MSAA及capture缩放都可能改变实际归属。硬边界无额外抗锯齿；它保证的是分类规则，不保证移动遮挡的视觉自然。透明纹理隐藏RGB过滤带来的边色也需与whole同资源对照，不能改raw。

连续源边界与预切整数边界略不同；为了独立诊断，应额外用[0,280,427,574,721,868,1254]后采样控制组，仅改uniform，不改艺术。这样可区分几何取整差与alpha过滤差。

## 六层sort与可达路点
仍用原layer1，sort54:317(order7254),318(7754)；sort55:319(7355),320(7655)；sort56:321(7456),322(7556)。源316 sort53/order7853在完整组时为空。玩家同y因原order在景物后，因此y54时在317/318之后、319/320/321/322之前；y55时在319/320之后、321/322之前；y56时在全部身体后。不得把六片合成单一排序根。

同一raw像素只属于一片，但玩家穿插后，该片与玩家的遮挡按其原sort发生。厚竿跨边处可能随玩家y出现不同深度，这来自源条带排序，不意味着真实新竹竿已被解剖成独立物体。需要场景实测，不能只比较无遮挡静帧。

routes_and_draw_order.json记录原碰撞8邻域不切角BFS。可达点包括(71,53),(72,54),(72,55),(72,56),(75,56),(75,57),(77,54),(78,53)；(73,54),(73,55),(74,55),(74,56),(75,54),(75,55)不可达，不能为测试改碰撞。路点通过不等于玩家精灵遮挡已正确。

## Runner验收建议
1. 当前标准768×512逻辑→1536×1024物理，whole / 预切 / 后采样同相机、sprite和native分辨率分别比对；额外大视口注明诊断。
2. 无玩家先对完整raw同变换渲染，在整数及亚像素相机位置取native RGBA差、alpha差、五边界局部；screen展示图不能替代native像素差。
3. 连续边界后采样与整数边界控制组分开记录，记录import、filter、mipmaps、pixel snap及实际renderer；不要为过测改艺术或改变运行采样设置。
4. 按可达路点移动，并在y53.99/54/54.01、54.99/55/55.01、55.99/56/56.01核排序与跨厚竿遮挡。断层可能来自sort而非alpha，应分别报告。
5. 运行时落实7字段/纹理完整组守卫和失败全源fallback后才能谈晋升；本包未改生产，20组扩展未授权。
