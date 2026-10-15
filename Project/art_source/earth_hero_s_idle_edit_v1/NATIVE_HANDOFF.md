# S idle 独立native验收候选

父级已实看编辑raw/同尺度服装对照，并认可作为S idle原生验收候选。不是普通world生产晋升。

独立资源：art_source/earth_hero_s_idle_edit_v1/candidate/body.png 与 candidate/manifest.json。

- direction S/index4；source17、18、19、20，依次12ticks，原顺序/时长不变。
- 完整头身合成，无额外原head覆盖。HD4 texture2048×512，4×512方格；logical frame128、root(16,64)、draw offset(-16,-64)、sprite scale0.25。
- body直接复制已审body-density4-CANDIDATE.png，SHA完全一致；四相RGBA哈希在manifest，各不相同。raw是2172×724，四个543×724格，先前公共scale及逐格刚性translation冻结，未refit、warp或归一化。
- S影未完成，必须关闭候选全部cast/contact影；不能借SE影图、SE shader参数或把旧棋盘影带回。候选本身无影。
- 只由唯一runner做独立native验证；不自行改普通world。候选任一校验不通过时整组恢复原body+head，不能半套新图。

测量边界：主体raw密度最低8.083/逻辑高单位；冠/靴端相对首张raw最大改变0.644逻辑px，受保护头手靴mask距离≤0.722逻辑px。这是可见面，不是骨骼/接地。服装编辑有ROI外纹理重绘，不能宣称逐像素锁定。静态同尺度/20→17已看，native仍需检查真实尺寸、4相顺序、至少两圈、20→17、启停和原资源fallback，不改状态机去适应图。

灰底/对照在 diagnostics/earth_hero_s_idle_edit_v1；最小归档显式清单不包括diagnostics、.import或运行文件。旧raw/登记/计划均保留，未覆盖旧版本。
