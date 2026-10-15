# 45 腰underlap与膝异位布桥：两步独立研究

## 亲看结果
腰89像素同位置underlap有效消除主要齿状透底。原保护层RGBA不改，在其半透明边后放已有黑布，符合正常分层合成；此前要求半透明最终像素也不变确实过强。
第二步178像素膝桥闭合所选透明口，但放大呈斜向黑布带，原裤口与胫根横向错位仍可感知。布料颜色连续性尚可，局部褶皱/明暗接界仍明显；未见足够证据判定它恢复源膝形状。建议保留两版本供父级审，腰可独立评价；膝桥只表示缺口被衣料覆盖，不能宣布姿态或材质通过。

## 两版本
- 45-HD4-WAIST-ONLY-RESEARCH.png / 45-128-WAIST-ONLY-RESEARCH.png：只加89像素腰underlap，右膝原缺口完整保留。
- 45-HD4-WAIST-KNEE-BRIDGE-RESEARCH.png / 45-128-WAIST-KNEE-BRIDGE-RESEARCH.png：在前者上加178像素膝桥。
全部固定128逻辑/root(16,64)，HD4 512/root(64,256)。未新生成、非均匀缩放、重画衣料或移动原core/胫靴/手。

## 精确来源和合成
同一已生成raw的既有mapped-whole-image-UNMASKED.png作为donor，保原512/1254全图映射，不再采样缩放。
腰donor平移(0,0)，仅冻结89像素。
膝donor平移(+5,+45)HD4、旋转0、scale不变，仅冻结178像素，包含已明确批准31像素原union外范围；来源HD4[159,228,195,241)，原raw约[389.43,558.42,477.60,590.26)。
在对应新布上source-over原protected-core-arm-shins.png，然后只从组合取批准mask内结果；mask外恢复前一版本原RGBA。原甲/手/身体纹理层本身不变，没有采用生成器的新core替换旧core。
两个mask不相交。旧原失败和所有输入未修改。

## 差分
PROOF.json：
- 腰步骤最终RGBA变化89像素，腰mask外0
- 膝步骤新增最终RGBA变化178像素，膝mask外0
- 原实色保护alpha>=128最终RGBA变化0
- 原保护纹理层RGBA变化0
- 最终原半透明保护像素共100个发生变化，分别腰89＋膝11
该100变化是正常underlap结果，不再错误报为必须0差。其余身体/腿/胫/靴保持既定状态。

## 审图
Project/diagnostics/earth_e_45_underlap_bridge_v1/
- source-before-waist-bridge-{1x,2x}-{gray,light,dark}.png：源/修前/只腰/腰＋膝桥
- waist-before-waist-bridge-{gray,light,dark}.png
- knee-before-waist-bridge-{gray,light,dark}.png
- changed-pixel-provenance.png：青腰、粉膝
已亲看完整2×灰底及腰膝放大。1×/2×为整图一次缩小后的最近邻展示，无逐相尺度变化。

## 残差
膝桥是衣料制作假设，并未改原膝代理、原固定胫根位置或靴长；错位斜接与重复衣褶风险仍在。arm45上下文手偏低约2逻辑像素、46金黄胫甲和49接头衣料痕仍需整组审。两姿势研究不是六相循环，未接生产/native/Git/GUI。
