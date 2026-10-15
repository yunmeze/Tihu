# 46冻结刚体矩阵 + 单次主膝下接头：接头失败，保留几何研究

## 结果先行
两段胫靴刚体按已批准矩阵执行，density不改；后根被固定裤面自然盖住，未生成后根。主根只生成一次黑布接头。固定mask过窄，未覆盖顶部完整弧形缺口，合成后仍有细透明缝；当前接头不通过。没有扩大mask、第二次生图、生产/native接入。
同尺度源/旧/新完整图显示后胫横伸和踝趾位置改善，这是几何研究结果；不能把接头缺陷忽略或宣称46原动作通过。

## 生成与固定范围
raw1298×1212，SHA86724222ab21e3c276b779608a874d180b1b87849e29dd8300a097fe3da012bb。唯一输入HD4 context[128,244,188,300]，60×56。单一等比60/1298，映射高度56.02465，仅底部裁0.02465px，无非等比fit。
实际主根支持为事先保存多边形fixed-main-gap-mask.png，而非最大11×9逻辑盒。实际采用进一步限制到原刚体图alpha<128的缺口/抗锯齿边，共358个HD4像素。规则仅依赖生成前图与固定polygon，不根据生成结果扩大。
新布放在旧半透明边后方，所有原alpha>=128表面逐字节保护。现原膝布、银甲、踝靴无需重画；生成器修改的所有上下文像素均未采用。

## 保护证据
PROOF.json：实际mask外RGBA变化0；所有生成前alpha>=128表面RGBA变化0；HD4 y>292与刚体前补片版本差0；旧静态到新图HD4 y<228保护区RGBA变化0。后根没有生成mask。core/arm输入及层级保持，49文件未改。
刚体分割仍沿earth_e_46_leg_rigid_plan_v1的互斥mask、原density；程序不画衣料、不重复拉伸纹理。

## 残余继续保留
后/主踝候选(26,72)/(40,84)，趾(31.492,77.492)/(48.749,87.281)。这些点驱动了候选刚体方向，不能视为独立验证。
固定裤膝布仍为后(34.148,62.902)、主(40.132,66.622)，对源(32,65)/(43,65)偏差未消。后/主靴踝趾可见长度7.766/9.344，对源7.071/8.544，分别多0.695/0.800逻辑像素。没有缩放追点。
主近端切口约(40.571,69.720)，是接头位置，不是新膝关节。主根新布纹理/边缘还有可见切接；后根附近一条细旧边/半透明拖尾仍在，没有以清理为名扩域。

## 文件与审图
- rigid46-BEFORE-JOIN.png：两块原像素刚体拼接未补布
- 46-HD4-RIGID-JOIN-RESEARCH.png / 46-128-RIGID-JOIN-RESEARCH.png：失败接缝静态候选
- layer-{rear,main,fixed}-HD4.png：所有已登记部件
- fixed-main-gap-mask.png / actual-gap-only-replacement-mask.png：支持域与实际采用域
诊断Project/diagnostics/earth_e_46_knee_join_v1/
- seam-old-rigid-joined-{gray,light,dark}.png
- source-old-new-{1x,2x}-{gray,light,dark}.png
- patch-diff-support.png / patch-pixel-provenance.png
这些均研究资料，不构成循环、不替换普通E walk sourcefallback。
