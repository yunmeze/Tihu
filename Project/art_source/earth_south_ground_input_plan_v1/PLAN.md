# 南侧地表扩展：源布局与冻结接缝输入方案

2026-10-15 UTC。待审制作方案，不是生成结果。仅本目录源证据、技术裁图和说明；无生图、无最终艺术拼接/混合/修色、无生产修改、无Godot/Git/GUI操作。

## 1 精确范围和57个新增owner

新观察窗world半开[2400,1408,3168,1920]，768×512逻辑。完整绘制bounds恰好对应64个96×64 FloorBig owner：cell x50..64、y44..58，均step2。不是64个48×32逻辑格。窗口中无FloorSmall，也无半个被截断的floor owner。

已有v4覆盖world[2496,960,3264,1472]。交集[2496,1408,3168,1472]为672×64逻辑，即7个完整owner：
- y44，x52、54、56、58、60、62、64。
- 它们继续使用原7个v4 tile PNG，SHA、RGB、alpha、world原点均冻结；原完整64-owner v4组也不拆解/重注册。
- 新增只有57个精确实例：x50,y44及全部x50..64/y46..58 step2。

64块均为负floorID对应FloorBig，source RGBA alpha均255。新增57块的12种signed ID及数量：-406×36、-577×1、-608×2、-594×2、-581×4、-597×1、-604×5、-385×1、-598×2、-386×1、-586×1、-388×1。

源类别：36草基底、15窄石路缘、3土/砂路基底、3草土过渡。不是允许把整窗口涂成同一草地。所有source_cell四字段、负号、flag、原裁切/完整画布、map byte offset、排序和完整world rect逐片保存在 `source_owner_evidence.json`。

每片引用对应原RGBA/alpha SHA与未改像素的源frame PNG；重复frame只有一份PNG，共12份。重复frame的新地面RGB必须来自各自世界位置母版，不得把某个新tile按frameID铺到其他实例。FloorBig不缩成一个cell，不按flag猜高度。

## 2 实际输入与像素来源

纯源布局：
- `source_floor_layout_native.png`，768×512，只拼接原floor图，不含树、NPC、建筑、池或其影。所有原像素不重采样、不改色。
- `source_alpha_native.png`，原alpha全255；不得把草/道路语义当alpha。
- `source_owner_index_native.png`，16bit索引1..64，按证据owners顺序，0代表无owner但本窗口无0。
- `source_owner_layout_reference.png`，带owner边框与signed ID标注的参考板；仅用于识别，不当成生成纹理。独立纯源图未被标注修改。
- `source_frames/`，12个原floor RGBA精确裁图，每个owner通过源证据指向其frame。

当前已过v4的实际生成像素，直接从普通 `assets/earth/environment/ground_plate_v4/plate.png` 裁取，原SHA a44d861c4485cb8596fb42681441675d1b9cefb3d8c48261113325c14492ae2f：
- `approved_overlap_2x.png`：world[2496,1408,3168,1472]，1344×128原生texel。
- `approved_north_seam_band_2x.png`：world[2496,1440,3168,1472]，1344×64。
- `approved_west_seam_band_2x.png`：world[2496,1408,2528,1472]，64×128。
- `approved_material_context_2x.png`：world[2496,1344,3264,1472]，1536×256，包含真实草、板缝、路缘与小排水细节。
- `approved_grass_scale_patch_2x.png`：world[3072,1408,3136,1472]，128×128。
- `approved_slab_scale_patch_2x.png`：world[2704,1408,2768,1472]，128×128。

这些裁图均只做整数crop，无缩放、混合、修色、重画或改alpha。7个现用tile按原位置重组与overlap裁图RGBA逐字节相同。裁图是输入证据，不是新的可平铺材质库。详细raw坐标见 `approved_reference_crops.json`。

## 3 接缝锚点：固定的是旧像素和世界坐标

旧新直接相接构成一个L：
- 北边：world y1472，x2496..3168，共7段，每段96逻辑。
- 西边：world x2496，y1408..1472，共1段64逻辑。

共8条冻结→新增接触；窗口内部另98条新增→新增接触、6条冻结→冻结接触，总112。全部线段、两侧exact key在 `seam_contact_ledger.json`。向观察窗外有32个源floor接触，部分北侧邻居是现有v4，其余仍source；不能把外边源/新风格差异当作整图已完成。

北边旧侧32逻辑宽、左侧旧侧32逻辑宽均已保存真实2×裁图；全重叠提供64逻辑高的条件，比32更充分。精确锚点包括L角(2496,1472)、北边每96逻辑分割点至(3168,1472)、西边顶点(2496,1408)。`generation_proposal.json`给出其在旧母版及新候选canvas中的texel-edge坐标。这些是坐标锚，不伪称为路缘中心或物理高度点。

道路/草边应由纯源layout决定，原斜路走向、转折、左边缘短竖段与草土过渡不能直线化。旧v4的相邻视觉落点则直接以冻结2×像素复核。材料外观与原低密度纹理不同，不能按颜色阈值自动测“精确道路mask”；本方案未生成任何伪精确语义mask。生成前人工复核原路缘中心窄带及旧/源对应关系；若确有超出原不确定带的形状冲突，先列差异，不能移动旧像素或源道路去消缝。

## 4 完整池结构：不填、不开新洞、不烘焙进地板

窗口右下可见原Debris55/56，实际同组为55–61七owner，cell依次(64,60)、(65,61)、(66,62)、(67,63)、(68,63)、(69,63)、(70,63)。完整源bounds world[3086,1800,3406,2048]，320×248逻辑。原图可见暗绿池面和石砌边缘，这不是floor材质或普通草斑。

`debris_pool_complete_source_native.png`仅复合完整7个原Debris owner，保其原layer/Y/order；`debris_pool_source_context_native.png`另给原floor+池的上下文，未加入其他物件。它们只是独立对象边界/排除输入，禁止生成器把池复制到地面RGB。详细原flags、source_cell、draw bounds、RGBA SHA在 `debris_pool_evidence.json`。

这处池的上下文地表全部是FloorBig，不是旧全图研究中另一处FloorSmall粗石楼梯井。池下原本有floor覆盖，所以新地表应仍保完整原floor，不把池轮廓打洞；池自身继续按原7owner遮住其下地板。所谓“不填平”指保留独立池对象和通行结构，绝非把地表owner删除。不要画新池沿、护栏、台阶，勿把flag1/-2推为真实水位/岸高。池只露两片也不能裁断组或替换成小装饰。

## 5 一次连续母版生成的待审方案

目标一次1536×1024原生有效像素母版，world原点(2400,1408)，density2，统一俯视斜向镜头。保持源道路/草边几何，材料、草密度、混凝土大分格、路缘细节与实际v4接缝裁图连续。风格仍是现实绿色草坪、近未来训练基地中性灰路面；统一暖左上日光和冷填光，无新太阳方向、无新增玄幻元素。

输入优先级：
1. 原floor纯layout和exact-owner证据决定几何与范围。
2. 当前真实v4重叠/两条接缝带决定边缘像素参考；已过grass/slab裁图决定尺度、颜色与材料细节。
3. 已认可Earth concept只辅助共同日光/材料，不可按概念重排道路。
4. 池对象图明确标注“独立对象，仅排除提示，禁止出现在输出地板”。

v4原prompt以144实际像素高的角色作2×尺度尺、希望草尖通常1–3像素；这是历史制作目标，不是这次对所有像素已做尺寸测量。这里优先延续真实v4裁图的观感和有效density2，不凭新prompt把草重画得更密、更亮或改材料。原concept和v4 prompt已列只读依赖，无旧庭院素材混入。

新母版中冻结重叠对应pixel rect[192,0,1536,128]，新增L形为[0,0,192,128]及[0,128,1536,1024]。生成可使用完整canvas上下文，但最终必须舍弃生成的7块重叠，不覆盖旧资产；只能为57新增owner取图。当前未制作带混合RGB的“最终拼接母版”，也未把源图与已过v4在一张图中混合。

提示词草案：
“在原始南侧地表布局上制作一张原生1536×1024连续纯2D地表。原图只确定道路、草地、窄路缘、转折及过渡位置，不保留低分辨率草纹。以提供的已过v4重叠和草/板材裁图保持同一世界尺度、中性灰路面、现实绿色草坪、暖左上光和冷填光；避免重复草斑、小砖网格和逐格纹理重置。路面保原宽度、斜向、左侧转折和窄路缘，不新增路口、高花池、台阶或沟槽。上方及左上提供的冻结重叠是接续参考，不能通过改它的颜色、位置或结构来救新图。只输出地面，不含人物、建筑、树灌木、池体/池水、文字或大面积投影；池是另层独立对象。不得镜像、旋转或循环已过纹理。”

生成返回尺寸、构图、道路对位、冻结接缝比较和重复图案检查全部通过后，才进入分片待审。若新旧接缝明显，不自动拼接/羽化/渐变/修色：先重新生成，或另提“仅新增侧”的有限修订方案等待批准。旧7块始终不能变；此阶段不提前处理最终艺术。

## 6 后续57片导出与安全接口建议

新world到raw采样：world=[2400,1408]+(texel_index+0.5)/2。每个96×64原owner对应192×128 direct crop，证据已有 `proposed_whole_canvas_region_px`。同frameID不同位置取不同raw区域；不重复tile、不回绕UV、不镜像草地或转带光材料。

建议新增57-owner原子组，与现有64-owner组独立。只有57的全部注册、真实PNG字节SHA、源cell/flag/order、密度、尺寸、原点和alpha通过后才publish。失败全部57恢复source，现有64组不受影响。新键与旧64键集合交集须为空；重叠7块完全由现有组绘制。保持原floor原遍历顺序，不能额外画一整张768×512背景覆盖旧图，也不能注册64新片再靠alpha混合遮住旧7片。

原选区alpha全部255，导出仍使用逐owner原alpha的精确2×扩展；生成图的草mask不能改它。不绘制观察窗外；不移除池下floor。若保持当前nearest采样，用直接切片先验证与整母版一致；任何linear/gutter改变须单独验收，不能自行加透明边或重复edgetexel来掩盖裂缝。

接缝检查：8条旧→新contact两侧至少±4实际texel带，98条新→新边同母版像素对照，6条旧→旧保持字节不变；检查整个L角不出现透明缺口/双绘、旧7重组等于原plate、全部64覆盖恰好一次。旧原64每个PNG保持SHA不变。窗口外source接缝明确标注，不为遮缝扩大owner范围。

独立native验收须保原角色起点、实际路径、对象深度、池结构、现有植物组和NPC时钟。新地板不烘焙树/楼/人物影；新增地面也不自动扩大任何旧影receiver/gate的批准范围。修改实际renderer若影响SHA绑定，必须由唯一runner单独重建/复查；本准备不改门。

## 7 交付与复核

运行 `python Project/art_source/earth_south_ground_input_plan_v1/prepare_inputs.py` 只重建本目录源输入与JSON。`INPUT_SHA256.json`逐项绑定读取源、真实v4、12源frame所用atlas和规则依据。每个owner有可复核源RGBA/alpha SHA、sourceframe文件、source_cell及切片坐标。

`UPLOAD_MANIFEST.json`仅列必要研究输入PNG、证据JSON、脚本、方案和生成提案；没有diagnostics PNG、运行截图、日志、缓存或导入文件。所有技术PNG都明确标注source/reference，不能当新美术成果展示。原生产raw/plate/tiles和concept仅列既有只读依赖，不复制重复上传。本阶段未生成或注册任何新地表。
