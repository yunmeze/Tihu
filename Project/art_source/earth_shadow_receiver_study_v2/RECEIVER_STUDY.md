# Earth 阴影接收面归因与 v2 CPU 候选

2026-10-15。只读CPU研究；v1源档、现SE/Fangzhang gate、runtime、身体PNG、flags、相位、坐标全部未修改。没有GPU、生图或Git。本研究生成的是诊断mask与覆盖统计，不是已批准运行接收面。

## 结论

- 凌云四相共同包络的233个旧禁区格，全由新楼upper3969的一枚远离材料主体、alpha恒1的独立texel扩张而来；不是平台、台阶、屋顶或真实斜撑。
- 首树旧禁区1804格来自源草裙以及新楼远隔alpha1小连通块。其直接命中的源layer0像素并非真正台阶。当前新楼真实support未被首树完整保守包络触及。
- 不存在可借用“画完楼后全不透明遮住影”的区域：所有冲突格的新楼完整不透明覆盖数均为0。噪点透明度1/255，绝不能当遮挡保证。
- 根据父级明确语义，CPU构建了**仅精确新楼有效时可用**的独立v2候选：保留新楼12support全部alpha>0及18upper所有材料，只在实体占据mask排除15个已逐一证明的远隔alpha恒1连通块，共28texel；身体仍原样绘制。实体mask外扩仍4逻辑。
- 该候选下凌云四相及共同包络、首树完整包络均0禁区交叠。没有截影、缩影、改变cast/脚线或修改旧gate。通过只限现固定输入和CPU面积验证，不是GPU通过，也不是3D平面证明。

## 精确归因

mask density2；每格0.5×0.5逻辑。以下贡献会互相重叠，不可把逐owner计数相加当并集。

### 凌云子

113/114/115/116旧冲突分别233/224/211/211格，共同并集233。唯一贡献 `new Building:3969@63,34`，layer1。源30owner与新12support贡献全0。

- 全图raw `(0,908)`；owner3969局部 `(0,746)`；texel world左上 `(3007.409332733406,1170.731770737911)`，单texel边长 `.484129314897`。
- alpha准确为1；以整个新楼alpha>0作8连通分析，该块id96，大小1texel，bbox `[0,908,1,909]`，max/min alpha均1。没有连接到任何真实半透明轮廓。
- 到全楼alpha≥128材料核心的texel中心距离110.847642逻辑。此阈值仅用于报告距离，**不是删除规则**。
- 四个直接覆盖mask格(world xywh)：`[3007,1170.5,.5,.5]`、`[3007.5,1170.5,.5,.5]`、`[3007,1171,.5,.5]`、`[3007.5,1171,.5,.5]`。其余229格只有4px扩张，直接alpha≥128/255覆盖为0。
- 四相共同线仍取冻结v1注册代理；阴影alpha>0完整面积、双线性半texel、blur+余量1.8与足代理保持不变。

### 首树

旧冲突并集1804格：新upper贡献1336、源support扩张贡献226、源upper扩张贡献290，彼此可重叠。

1. `source Building:3985@66,37` layer0：直接11mask格，来自5个源texel `[(0,11),(1,11),(0,12),(1,12),(1,13)]`，world左上x3168–3169/y1195–1197，alpha255。4px扩张种子100texel，bbox局部 `[0,7,48,32]`，扩张相交226格。已放大查看：这些点为绿草裙，不是浅石踏面。既存 `earth_training_hall_edit_plan_v1/edit-plan.json` 的3985两脚证据明确记为 `source_grass_apron`、新图透明、`must_restore_support=false`。不能把“layer0 owner”一概解释为整块台阶。
2. `source Building:3988@67,38` layer1：直接105mask格，来自30个texel，局部x0–5/y528–533，world x3216–3221/y1217–1222，alpha255；扩张122种子、290格。已放大核看全部直接点和扩张种子位于下部草裙，不是上方屋顶/柱/栏杆。layer1也不能自动解释为高处材质。
3. `new Building:3969@63,34` layer1：6个种子全alpha1，6个彼此独立的1texel连通块；直接24格，外扩878格；离全图alpha≥128核心67.02–110.85逻辑。
4. `new Building:3973@64,35` layer1：22个种子全alpha1，9个独立连通块，大小依次5/1/1/1/9/2/1/1/1；直接2格，外扩458格；离alpha≥128核心37.81–92.25逻辑。

15块的全部whole-raw坐标、连通块bbox/大小/max alpha、逐owner原身份/层级和非可加贡献均见 `attribution.json` 与 `receiver-candidate.json`。component id只对绑定PNG/SHA及8连通算法成立，不能当未来版本通用ID。

## 地图与真正接收面

研究使用源A13 `cells[x*100+y]` 与 `movement.gd`：flags -1/-2/-3阻塞；从(61,39)无对角穿角静态连通搜索。像素映射报告为nearest actor-origin cell，即round(world/(48,32))，不是将格子当成地板高度图。

- 凌云冲突落最近actor cell `(63,37)`：原记录 `[0,0,0,0]`，walkable且静态可达。
- 首树冲突最近cells `(63,36),(63,37),(64,36),(64,38),(66,37),(67,38),(68,39)` 均原flags可走且静态可达；(66,37)是flag1的3985草裙owner，(67,38)是flag0的3988草裙部分。
- 这是通行证据，不是支持高度证据。草裙材质来自实际源图复核和已有脚点分类；新support来自已批准新楼的实际landing/treads/narrow-risers material partition。原台阶12owner并非12个实心平面矩形。
- 当前受测完整影包络与新楼12support全部alpha>0及4px外扩均不交叠。全包络到support覆盖栅格中心最近距离：凌云共同64.63745、首树18.02776逻辑。半逻辑格之间连续面积的保守下界需减sqrt(2)/2，分别≥63.93034、≥17.32065。
- 真正台阶/平台依旧禁止平地影；若以后改变树根/投影后跨阶，必须新增有实际支撑几何与高度分段的platform receiver。把楼影块裁掉不会构成物理解。

## v2 候选mask的明示规则

候选PNG在忽略目录 `diagnostics/earth-shadow-receiver-v2/`，1536×1024二值L，world域 `[2496,960,768,512]`；样区外禁止。`receiver-candidate.json`记录SHA、全30owner几何计数与输入SHA闭包。

1. 仅T正在绘制已批准新楼，且其30owner精确身份、所有非空纹理、显式空项、注册、map/flags与SHAs均有效时可启用。仅检查`prefer_hall=true`不足。
2. 保留每个新layer0像素，无论alpha是否低；保留全部upper结构、边缘、半透明材料与连到主体的alpha1。只将上述15个经过独立8连通和距离/材料检查的完整alpha1小块从**实体占据**排除。
3. PNG/raw/owner身体仍完全不变。mask修改不等于美术擦除，也不允许全图alpha阈值去噪。没被审的噪点继续留在mask里。
4. 新实体面积保守栅格化并外扩4逻辑，allowed是样区内补集。新楼的真实台阶、窄立面、侧颊、柱、墙和其他upper仍禁止。没有“所有upper都放开”。
5. 此时源楼不绘制，其旧草裙不应冒充当前平台。一旦T切源、hall验证失败、身份不符、manifest/图像hash变更，新v2 receiver即失效，依赖它的新NPC/环境影整份关闭；不能悄悄退回源楼上继续画影。现SE/Fang gate原封不动，继续自身规则。
6. 每对象自己的完整alpha包络必须全在allowed，既不借用hero offset/包络，也不剪掉相交部分。楼toggle变化和每次加载失败都要有fail-closed验证。
7. 最终层序仍是地面→独立落影→原对象/人物排序。新楼后画并不是本方案的安全依据；这里依靠实际实体/支持面排除，且没有声称覆盖人物或墙面的接收能力。

## 全包络结果与余量

- 凌云四相、共同包络与候选4px forbidden相交均0；距候选forbidden栅格中心39.80264，连续面积保守下界≥39.09553逻辑。新alpha≥128核心最近64.40497。
- 首树相交0，但距候选禁区格中心仅0.5逻辑，**不能保证正的连续面积余量**。这是固定参数/位置的CPU通过，不能自行扩大木根误差预算、移动、换参数后仍声称通过。
- 首树离alpha≥128核心栅格中心8.5，连续面积下界≥7.79289；距真实support更远，如上。将margin仅作敏感性研究增到6会碰58格，bbox `[3071,1148.5,3076.5,1156.5]`；原因是3973内两个**仍保留**的alpha1点whole raw `(144,857)/(150,865)`。本次没有为增加余量继续删它们，也没有改变正式4px候选规则。不能把这58格说成台阶相交。
- 首树固定木根与水平接触线仍是2D近似，1254²/density4还需要独立shadow-only透明补边接口处理。receiver通过不会自动批准树影几何、透明补边或GPU视觉。

## 审图、复现与下一步

运行 `python Project/art_source/earth_shadow_receiver_study_v2/analyze_receiver.py`，需numpy/Pillow/scipy。只读正式输入与冻结v1，输出诊断目录；不会自动更新本源档中的冻结JSON，不生成运行资产。脚本先精确重建旧30+30owner alpha+4 forbidden并断言与现mask逐格相等，再逐相重现v1冲突计数。

诊断图片：
- `lingyunzi_all-source-new-context.png` / `first_tree-source-new-context.png`：同world旧/新楼CPU背景，洋红标旧冲突；不是native实机截图。
- `source-3985-seed-detail.png` / `source-3988-seed-detail.png`：源像素nearest8x；洋红直接种子、黄扩张种子，可读为草裙。
- `*-attribution.png`：原禁区贡献类别及源flags网格；只作算法示意。
- `*-candidate-receiver.png`：灰完整alpha包络、红新实体+4、绿新support+4、黄已归因旧冲突。没有绘制候选美术或投影视觉效果。
- `allowed-candidate.png` / `forbidden-candidate.png`：二值候选mask，均未安装。

建议父级先审凌云单点噪声与新楼条件绑定，再决定是否授权只凌云GPU诊断；首树仍独立审脚根假设、接口补边及紧余量。GPU前不得默认启影。本次未做运行验证、未修改原walkflags，未声称3D遮挡或平台接收完成。

## 追加：父级要求的只diag接口与树技术纹理

父级已要求准备CPU/技术纹理，GPU仍待其看图授权。运行归因工具后执行：

`python Project/art_source/earth_shadow_receiver_study_v2/prepare_diagnostic_interfaces.py`

输出仍只在ignored diagnostics，源身体/正式资源不写：

- `lingyunzi-diagnostic-interface.json`：精确record1/source113–116/四个raw512×640区域、固定共同足线、17tick时钟、cast(1.2,.55)/opacity.25/logical blur.8、receiver/参数/资源SHA与新楼失效条件。
- `first_tree-diagnostic-interface.json`：固定七owner身份/根world(2761,1090)、单whole影、不动身体排序；shadow-only图及独立补边契约SHA。
- `first-tree-shadow-padded-1256.png` / `tree-shadow-padding-contract.json`：原1254²逐RGBA保持原位，右/下各2px全RGBA=0，raw root(523,1224)、density4与world origin不变；logical region314²。重新解码逐像素验证通过。原边界夹紧变为插值透明的差异仍需GPU审，不声称采样完全相同。
- `receiver-material-review.png`：当前地表/新楼CPU上下文，红色为保留实体+4。仅接收面审图。
- `lingyunzi-phase0-cpu-alpha-overlay.png` / `first-tree-cpu-alpha-overlay.png` / `both-phase0-cpu-alpha-overlay.png`：以固定投影逆矩阵、双线性alpha、归一化3×3核采样，在现地表后、楼前叠影，无身体sprite。不是native实机截图，颜色合成为CPU sRGB近似，不能替代最终shader/sRGB验证。

receiver契约包含28texel完整坐标列表、15个完整8连通块记录、全部新support保留证明、30owner几何计数、源map/新楼/参数SHA及失效条件；参数SHA是其parameter_records按sort_keys与紧凑JSON编码的SHA256。两接口只给诊断runner，不授权安装到普通入口。

### 多caster叠暗

`multi-caster-overlap.json` 记录全部四相。凌云4相完整保守包络均包含于首树保守包络内，union交集5779个density2格。CPU实际正alpha采样交集逐相3062/2930/2852/2917格，集中world约x2970.5–3088.5/y1169–1205.5。两个独立blend_mix叠加时最大opacity约.4334–.4335；两张全不透明alpha各.25的理论上限.4375。相对较强单影最大额外暗度约.1857。

后续GPU必须分别看树-only、凌云-only、两者同时和原样身体/遮挡，确认叠暗是否过重及四相边缘变化。此次不加union compositor、不自动降opacity、不扩通用阴影系统。若实机叠暗不接受，再单独提出有界合成决策。
