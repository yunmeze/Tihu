# 张天师单202最小实验：身份可延续，稳定微动未通过

仅一次授权完整202生成。201身份ref选择明确的(-5,+1)版本，源202已按真实offset(0,-44)贴入共同96世界窗，未再次叠加+1。输出只做整窗均匀密度换算，完全没有独立bboxfit/缩放身体/平移修正。

## 查看
201-202-pair-1x.png / -2x.png / -4x.png：左已选201，右202。
201-202-toggle-1x.gif / -2x.gif / -4x.gif：340ms逐相来回，仅两相诊断，不代表完整四相loop。
static-alpha-rgb-difference-4x.png：青=201强alpha独有，橙=202强alpha独有，共同强alpha区域显示3倍RGB绝对差；不是动作骨架图。

## 结论和误差
同一成熟脸/短发、灰短拉链夹克、浅肩拼片、蓝内层、裤鞋整体可认作同身份；没有新增武器/长袍，原高低手势仍在。但身体略变宽、脚/躯干整体往右下移动，不是仅细表面变化。
8区局部patch诊断（logical、202减201）：脸(+1.5,+0.5)，左肩(+1.25,+0.75)，右肩(+1.5,+1)，高手(+0.25,+0.75)，低手(+1.75,+1.25)，腰(+1.5,+1.25)，后鞋(+1.25,+1.75)，前鞋(+1,+1.5)。RMSE约16.5–35.1，纹理重绘会偏移最佳点；误差约1–2logical，不声称这些小数是真骨骼精度。多点同向且鞋位变化需要保留，不能都归于噪声。
强alpha面积从1320.6875增至1420.3125logical²（+7.5434%）。面积并不等价统一scale，但与可见略增体量一致，需要拒绝“尺度完全锁住”的说法。未通过提案保守稳定性门槛；不以脸相似或不同hash宣称动画成功。
原201高手(-6,+1)源残差仍存在，本202实验没有修复或洗掉它。202源offset+1已注册并大致抵消帧内变化，不能用该metadata替新整体右下漂移辩护。未追加203/204，也不根据本次漂移重新拟合202。

## 实际链与确定复现
contract-before-generation.json：actualrefs仅source202-fixed-world.png、identity201-fixed-world.png，顺序如文件；prompt_actual.txt为完整实际文本。身份ref SHA为2b2069213836341aab4518728a27d4f472bae78591f5237c9bc19187c3c89597。
原返回 /workspace/scratch/22c897619190/generated_images/exec-6ddf2b7d-791e-458d-8372-5ee6eea7ae96.png。
generated-raw.png SHA680577f73a3915132dc75e964e831e3c332fd7b19c77d02cfacd0133ab018ac9；1254square/96logical=13.0625真实密度。
review.py整raw RGBa LANCZOS→384square；candidate202-complete-density4.png SHA18660490c2e0305a3cbd1de26b6152d6a2b4b133a903c29b4fbd6d35753abc2c。worldorigin1668,1032不变，无额外transform、alpha清理或肢体修改，10112个raw alpha1–2保留。
track.py只测量，不移动图。无Godot、runtime、生产或Git操作。
