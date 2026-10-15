# 四 caster 最大遮蔽：样区限定诊断方案

2026-10-15。只读研究与CPU合同；未改生产renderer/helper/gate/美术，未运行GUI/GPU。原生v2结果来自唯一runner，后续实现只由runner在独立诊断执行。

## 建议

使用一张独立Node2D+四个显式sampler的CanvasItem shader，只处理SE英雄、方丈record0、凌云record1、首树root57,34。每slot保持自己的资格门、原始变换、原9tap alpha采样和blur；得到每slot最终alpha后取max，原tint只blend一次。不要把独立影继续混到背景后再尝试提取黑色，也不要构建泛化引擎或低分辨率Viewport。

`a_i = 原本的gate ? clamp(9tap(alpha_i)/16,0,1) * opacity_i : 0`

`A = max(a_SE,a_Fang,a_Ling,a_tree)`

这里max在**各自blur与opacity之后**。不把max放到各caster blur之前，也不再对合成结果blur。当前统一cast(1.2,.55)、tint(.035,.045,.055)、opacity .25、logical blur .8、density4/raw blur3.2不变。它是单一主光源的有界最大遮蔽近似；半透明树叶与半影实际光学相关性未恢复，不能声称精确物理阴影并集。

Godot 4.6 CanvasItem公开blend modes没有独立`blend_max`模式，因此不建议把现节点换一个混合枚举；采用shader中显式max后`unshaded, blend_mix`一次输出。依据：[Godot 4.6 CanvasItem shader reference](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/canvas_item_shader.html)。

## 最小实现范围

1. 一个独立诊断组合Node2D，一个固定四sampler shader，诊断driver绑定四份已有helper配置；不编辑原helper/gate代码。
2. 坐标使用同一个逻辑父CanvasItem平面。合成节点identity transform；该点乘每helper的body_to_parent逆变换得到raw投影坐标，再用该slot原inverse projection采样。camera translation已经在原transform内，绝不再次乘density或重复加camera。
3. 四slot各保留实际raw atlas、raw region、atlas size、frame边界先reject后texel中心clamp、LOD0、filter_linear/repeat_disable、原padding。draw quad覆盖所有有效slot已有shadow_bounds变换后的并集，不用body bbox。
4. 原helpers继续configure与gate计算，取有效配置后仅关闭旧draw，防止重复阴影。隐藏后不得把visible当下帧资格来源。新合成失败时整次合成关闭，不暗中叠回四个旧draw。
5. 单slot资格失败只令该slot为0；要在读取无效uniform/采样前分支返回0，不能做`0*NaN`。新楼/T失效只影响依赖v2的凌云/树，SE/Fang仍由原独立gate决定。共同shader/tint合同失败才整次组合关闭。
6. 不把v2mask应用到整个合成结果。每caster先完成自己的完整包络资格，随后合成；不能把旧SE/Fang改用新receiver，也不能剪掉跨阶部分。所有地面→一次合成→原support/对象/人物排序保持不变。

## 可复核数值

原生v2 `gpu-difference.json` 报告可见双影重叠2150像素、比单影额外暗最多40RGB；两个单影与both在禁区>2RGB差分均0。已查看ling-contact/tree-contact/overlap：局部没有明确脚根/木根分离，叠暗带可见；这不替代连续移动验收。RGB差分不是alpha反演。

CPU采用当前相同逆投影、纹理alpha、3×3核、2samples/逻辑；统计阈值为最终单影alpha>1/255，**不等同原生RGB>2统计**：

- 凌云phase0与首树重叠2557采样点；方丈与首树也重叠375；方丈与凌云为0。因此仅合并Ling/tree再把Fang画第二次仍不能完整解决样区叠暗。
- 三个静态caster：独立blend最大alpha .433411102；max方案最大 .248416470，最大移除的额外遮蔽 .185667832。
- SE idle13在(61,39)：原gate允许，阈值下与三静态影均无重叠；max全图最大 .248463559。非重叠处应保持原样。
- SE idle13在(61,37)：原gate允许，与树重叠5343采样点；独立blend最大 .434327569，max最大 .248463559。
- SE idle13/walk51在(63,38)、idle13在(62,36)：虽然源flag0可走，原十相gate拒绝，必须贡献0。不能为了演示四影交叠绕gate。
- 这些5个明确actor状态没有三/四重叠，不是全移动穷举。另用synthetic alpha向量验证四输入合成规则：全部.25时，独立两次/三次/四次blend分别.4375/.578125/.68359375，max始终.25。

`measure.py`可复现上述CPU数据，输出只到ignored `diagnostics/earth-max-shadow-study/measurements.json`；冻结报告与输入SHA在本目录。CPU读真实body，不改身体或alpha。不执行现renderer或GPU。

## 验证合同与风险

- 数学不变量：单caster等价；非重叠等价；重复同caster幂等；slot顺序不影响；全slot关闭透明；任何当前组合alpha≤.25。这些数值已CPU验证。
- GPU先做每个单caster与原节点同帧同机位对照，预算每RGB通道≤2；任何超过预算的像素列count/max/bbox并解释，禁区>2差分必须0。body像素/位置和相位时钟不变。不要把“合成更浅”当成单caster采样改变的借口。
- 各slot入口/退出、N/T/G切换、hero离开SE/进入run、v2失败、单caster纹理/身份错误、camera移动须保持独立资格与立即清影。小数移动仍使用原gate完整面积逻辑。
- 原source_color/sRGB路径必须与旧shader相同；不得为了匹配CPU预览而改gamma。max比较alpha而非RGB或亮度。
- max可在两个软影等强交界产生梯度折线；不是opacity相加，但运动时边界交换仍需观察。相同太阳下不叠加过暗是本次美术选择，树冠透明度并非真实体积透射模型。
- 4slot×9tap最多36纹理读取/fragment；全1536×1024 quad最坏56,623,104读取/帧，是理论上界，不是耗时测量。disabled slot和已padding的slot AABB先剔除。Compatibility/llvmpipe需实测；不先引入静态缓存/额外Viewport/多轮合成体系。
- 必须包含四caster同画面的原样路径验证，不能只测Ling/tree或仍让SE/Fang旧draw叠在max结果上。组合验证期间禁止生产晋升；父级看结果后再决定。

冻结机器合同：`numeric-contract.json`。输入/报告/工具SHA：`ARCHIVE_SHA256.json`。原v1、receiver v2源档保持不变。
