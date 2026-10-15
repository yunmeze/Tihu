# 南侧连续道路：四组植物纯平移候选计划

2026-10-15 UTC。仅准备，未接入 ordinary runtime、未生成图片、未复制PNG、未改现有注册。遵循现有地球基地绿化风格。本目录的 registration 是候选数据，不是现有 loader 已支持它们的证明；当前 loader 的范围和固定 SHA 应继续拒绝这些新实例，直至唯一 runner 在独立试验入口实现和验收。

## 1 范围：7组交窗，4组新增

观察窗 world xyxy [2400,1408,3168,1920]。以原完整源绘制 bounds 相交选组，再保全组，不以 root 是否在窗内决定。

新增共22 owner：
- 直立树(47,66)，299–304 六片；源 bounds[2167,1832,2448,2130]。只有右上边缘进入窗，仍保6 owner。
- 直立树(55,57)，299–304 六片；源 bounds[2551,1544,2832,1842]。
- 直立树(59,61)，299–304 六片；源 bounds[2743,1672,3024,1970]。下边越窗，仍保6 owner。
- 圆灌木中心(58,51)，143–146 四片；源 bounds[2743,1559,2867,1664]。

已有普通实例仅作上下文，不重复注册、不重绑键：树(61,51)，灌木(51,44)/(64,45)。不能用这4组候选掩盖该窗口未做地表、新密草248–250、Debris结构和窗口边缘其他源内容；这不是完整南侧高清验收。

## 2 精确源比对与复用

`source_equivalence_proof.json` 对每个目标owner逐一记录基线/目标：原完整画布、crop、被忽略的offset、实际裁切RGBA SHA、裁切尺寸、源绘制bounds、frame、flag、layer、原cell四字段和byte offset。逐项断言相同RGBA/crop/布局/flags/layer；不是仅拿相同frame ID当许可。

- 三棵树基线为已用(61,51)，新world平移依次(-672,+480)、(-288,+192)、(-96,+320)。
- 灌木基线为已用中心(57,38)，平移(+48,+416)。
- 树(55,57)/(59,61)连完整source_cell都与树基线一致。
- 树(47,66)和灌木(58,51)部分source_cell的地面字段不同，保持实际目标值；不改变地表、碰撞或层级。
- 目标flag均与各自基线一致。这只证明通行/层级数据的对应，不证明真实高度、地面接触、周围遮挡或阴影接收等价。

候选共同原点：
- tree47,66 → (2167.5555555555557,1830.6666666666667)
- tree55,57 → (2551.5555555555557,1542.6666666666667)
- tree59,61 → (2743.5555555555557,1670.6666666666667)
- shrub58,51 → (2743,1557)

树保持density4.5、scale2/9、1162×1353整画布、原raw根(560,1329)和同一根点误差；只平移world根。灌木保持density11、scale1/11、1363×1154整画布和原可见叶支撑带，physical_root仍为null，不擅自把bbox底当根。两类均不裁切、缩放修形、镜像、旋转、改变分片归属或单片归一化。

## 3 资源只引用一次

4个候选JSON共同引用已存在的10个owner PNG：6个树owner（含全空304）和4个灌木owner。非空实际绘制PNG只有9个。三棵树使用同6个文件，不生成三份atlas或重复资产。

原raw与owner-labels仅作可核对的基线来源；它们已在assets/earth里。`shared_asset_dependencies.json`列10个owner文件的实际SHA、size及所有引用者。实际PNG与baseline注册声明SHA一致，源原图来自manifest/atlas。源与候选像素、统一根/支撑线都没有修改。每个目标的22个owner位置与标识在 `trusted_expected_scope.json`；该文件由固定目标SPECS和权威A13直接生成，不能从待验证的candidate注册反推“可信范围”。

## 4 阴影边界与现有基线差异

新增四组全部无新投影，不加载receiver、gate、cast mask，也不加入现有shadow compositor槽。不继承首树或左树world-fixed patch；切S不应使这些新树/灌木突然出现cast。源切换时原始棋盘影作为整组source正常恢复；新组激活时完整源组（含304旧影）被抑制，这与“新组无cast”不矛盾。

本次父任务提及普通4caster，但读取的 sample_world.gd 已有以下5槽：hero、fangzhang、lingyunzi、first_tree、left_upright。`candidate_ledger.json`记录实际代码SHA和configure行。此计划不修改这项基线；唯一runner应先冻结当前有效场景，明确保留它的现有4/5槽行为，再做本候选。不得为了凑4槽回滚现有功能，也不得把既有左树许可泛化给三棵新树。

## 5 给唯一runner的候选接口（建议契约，未实现）

独立诊断入口优先，不把现有 ordinary PATHS/CELLS 范围放宽。

1. prepare_south_group(id, registration_path, live_map) → 一个完整group，或空group。id只接受本计划四个固定ID；路径、注册SHA、源mapSHA由独立可信expected表绑定。错误Variant、额外ID、缺键、重复owner、错order、错source_cell、错flag、错layer、错sort_y、错world原点、错scale、错empty、错PNG bytes/尺寸均应失败。
2. 所有依赖须检查真实loose文件存在且SHA匹配，不能只信已导入cache。整组先stage，全部通过才publish；失败清空该组。304必须有精确空项和source抑制身份，不得删去，也不能画源304造成双影。
3. source/candidate preference是每组独立bool，默认候选只限独立诊断；可提供总开关但不覆盖现有V/J语义。每组切source后该组所有源owner恢复；其余候选和现有组保持状态。
4. 精确匹配entry时检查kind2、Plant pack、frame、cell×(48,32) origin、layer、y、stable_source_order。按原对象遍历位置画同分片的整画布，不能用root处单sprite替代6/4 owner，也不能修改原排序。
5. candidate_item(entry)只在当前完整group准备成功、该entry精确匹配、该组prefer_new为true时返回override。否则原始draw路径继续。三棵树各自独立dictionary，不能按frameIndex覆盖别的相同frame实例。
6. setup必须清空四组prepared状态及临时绑定，保留用户preference也不能遗留上张图像。重新prepare成功后才恢复候选。新组shadow descriptor永远不存在；既有影组原行为保持。
7. 共享texture cache可按path+实际SHA+尺寸缓存引用；group状态不能共用一个“成功”bool。任何一个共享树PNG失效时，所有依赖它的三个树组分别整体fallback，灌木可独立保持；仅一个registration失效时只回退该组。

`trusted_expected_scope.json`给出固定完整输入期望。候选status=detached不能换成accepted；先完成以下验收才可另外提出普通入口推广。

## 6 原路径与遮挡验收点

`route_acceptance_points.json`保存每段完整cell路径、实际目标source_cell、各owner与actor的sort关系。起点均是原(61,39)，由原flags进行8邻接禁止切角BFS。它是只读可达性提案，未执行Godot A*、tick或截图验收。runner必须真正请求原路径行走，不能teleport角色当路线通过。

树(47,66)：后(46,65)→左(44,67)→中间分层(47,68)→树冠同Y(48,70)→前(47,71)。
树(55,57)：后(54,56)→左(52,58)→中间分层(55,59)→树冠同Y(56,61)→前(55,62)。
树(59,61)：后(58,60)→左(56,62)→中间分层(59,63)→树冠同Y(60,65)→前(59,66)。
灌木(58,51)：后(58,47)→中间分层(57,50)→左(56,51)→同Y右侧(60,51)→前(58,52)。

所提树后方原同X点、灌木中心/旁片阻挡点不可站，已选择原可达点，没有修改flag。树299在root Y，其余300–304在root Y+4；灌木143在中心Y−3，其余在中心Y。中间点专门验证actor在两组owner之间；同Y时actor稳定order晚于静态owner。排序关系不能独立证明alpha遮挡，需要截图确认人体/树冠真正相交；可再加原可达侧翼点，但不能挪树/角色锚点以制造通过。

所有点对照同tick、同source South17姿势，避免主角新旧方向覆盖差异干扰。跟随镜头或明确标注审图机位可使完整人物和相关整组可见；(47,66)/(59,61)跨窗不能用固定窗裁断人物后声称遮挡检查通过。其他源植物遮挡不得隐藏。实际相位和运行步数由runner记录，不把本BFS步数当native tick证据。

## 7 必做验收矩阵

- 全22 trusted identities/source_cell/world translation逐项相符；原A13、碰撞、NPC、门户、路径和绘制顺序未改。
- 每组fullcanvas组合与原整张候选raw的既有分区重组关系保持；不因平移引入额外scale、UV裁切、alpha缝或重复画源。
- 四组独立source/new开关；对每组分别缺registration、错SHA、错Variant、错源cell、重复/漏owner、错empty、依赖PNG缺失且保留旧import cache，验证整组source fallback。
- 所有树组共享依赖坏时三组同时安全fallback；仅一组registration坏时其他组保持；灌木完全独立。
- fallback→修复→reprepare恢复；setup/map切换清理；不支持地图/错尺寸全部source。原有三组上下文不被重复/关闭。
- 每组上述前中后路线真正行走并A/B；记录裁剪失败证据并补拍，不将源植物遮挡删除。
- 新4组投影始终0；现有compositor和各slot行为与冻结基线一致。源棋盘影不能在候选打开后残留。
- ordinary entry尚未改变。未来若改实际sample_world，会影响SHA绑定，必须由唯一runner重建/复查相关现有gate；本次不会提前更新任何门。

## 8 文件与上传

重建：python Project/art_source/earth_south_vegetation_reuse_plan_v1/build_plan.py。
此命令只读source/ordinary依赖，写本研究目录JSON；不生成图片、不修改注册原件或脚本。

`UPLOAD_MANIFEST.json`仅列本阶段必要的说明、工具、候选注册、源证据/可信范围、依赖清单、路径验收及SHA清单。已经存在的source map/atlas、生成raw/owner PNG、基线代码另列只读repo dependencies，按SHA核对，勿重复复制上传。没有diagnostics PNG、截图、日志、Godot import或缓存。输出不宣称可直接交给当前两实例loader运行。
