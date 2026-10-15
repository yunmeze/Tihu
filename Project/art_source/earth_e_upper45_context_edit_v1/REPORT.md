# 单45完整侧身上下文局部编辑：侧向改善，接头仍未通过

仅执行批准的一次imagegen。raw.png 1254×1254，SHA256 3c705ac0bb9db5c457fff432a578f838e25416708fb866cbda805c6181e06b5a。
实际短prompt及三个输入SHA已在调用前保存request.json。父级批准5743像素union保持原样。

## 结果
亲看raw、腰膝三列及完整源/旧/新2×：这次没有变成正面商品裤，右向侧身与旧短展步保持，旧大侧片已替换为黑布。但工具主要重画裤面，没有自然连到右胫根；原raw中右膝下仍有透明缺口，不只是后处理裁切造成。最终回贴后右膝仍断，腰边还出现细齿状接痕。当前失败，不晋升、不扩mask、不重抽。
黑布形状仍接近旧上裤，不能因侧视正确就宣称源膝/腿相位已通过。

## 映射与保护
全图单一等比512/1254=0.4082934609250399，平移(0,0)，旋转0。未重新fit人物或局部。
原alpha>=128 bbox(69,63,247,350)，全图映射raw为(68,61,249,351)：有约1–2HD4px边界漂移及表面改动，未自行修正。这只是轮廓范围，不能据bbox认定为精确统一缩放。
原图外修改全部丢弃：映射raw在union外17352像素RGBA不同，其中原保护区16576不同；它们均未采用。
最终：
- union5743像素，其中4055实际RGBA变化
- union外RGBA变化0
- core/手/胫靴alpha>0保护域RGBA变化0
- actual-fixed-union-mask.png与预先批准mask一致
最终从原上下文开始，仅union内替换生成RGBA，没有旧裤叠影。保护层所有RGBA恢复，但保护边的旧抗锯齿与新衣料不完全连续，腰口细齿状痕迹照留，没有羽化扩域。
raw alpha0像素1445584，真实透明；未颜色阈值清理暖边。

## 文件
- raw.png：实际完整工具输出，包含所有被丢弃上下文修改。
- mapped-whole-image-UNMASKED.png：预定映射，不隐藏工具漂移。
- 45-HD4-CONTEXT-EDIT-RESEARCH.png / 45-128-CONTEXT-EDIT-RESEARCH.png：严格固定union研究回贴。
- PROOF.json：RGBA差分/原保护/映射记录。
- actual-fixed-union-mask.png：原5743像素mask副本。

诊断 Project/diagnostics/earth_e_upper45_context_edit_v1/
- source-context-new-{1x,2x,4x}-{gray,light,dark}.png：完整源/旧上下文/新。
- waist-knees-context-raw-new-{gray,light,dark}.png：左旧、中映射raw、右最终。明确显示raw已经未闭右膝口。
- actual-RGBA-diff.png：只有union内变化。

源膝是表面代理，现胫靴原长度残差、上下文arm45偏低约2逻辑px、46金黄胫甲及49接头痕仍保留。没有修改这些历史资产或任何普通运行/Git/GUI。单次失败到此冻结。
