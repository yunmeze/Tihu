# 最终汇总交付

## 当前结论

- 固定原几何/8-owner/四flag0尾片的二维分区方案已完成并经root审阅：Q267/Q322为人工二维候选，纯旋转统一屏幕密度UV只用于微纹理研究。**没有实现映射/引擎或正式几何替换。**
- M2墙混凝土、M3基础混凝土均由root接受为微纹理候选；M2保留blue边带3.136/255的小WARN，不称数学无缝，两份raw不改。
- M1原生成及唯一定向编辑均周期FAIL。原边带最高21.572/255，编辑后仍7.045/255；接缝/内部跳变比3.434→2.473，残余单调梯度仍存在。**金属生图路线按约冻结，无更多调用。**
- 原整墙两次几何FAIL及档案继续保留。任何阶段都不能把两张混凝土贴上当成整墙新美术；屋脊、折边、板缝、檐下明暗、角段及真实遮挡验证都未实现。

## 优先审图/报告路径

1. `../a13-wall-m1-material-edit-v2/EDIT_COMPARISON_SAME_DENSITY.png`：M1原/编辑最终FAIL对照。
2. `THREE_MATERIAL_SAME_DENSITY_REVIEW.png`：同密度三材料板，展示的是原M1FAIL、M2与M3；M3后已被root接受，初版图中文字“review pending”是审阅前状态。
3. `FUTURE_STRUCTURED_METAL_2D_CONTRACT.md`：以后若改为有明确结构板缝的独立金属板，须先确定的二维尺寸、方向、相位和上下/两端接口。仅建议，未实施。
4. `../a13-wall-material-uv-plan-v1/README.md`、两张REVIEW图及完整SURFACE_UV_REVIEW.json：原源支持/owner/分区与UV方案。

## 原raw索引

|角色|相对recovery-work路径|SHA256|
|---|---|---|
|M1初稿FAIL|a13-wall-m1-material-pilot-v1/generated-raw.png|d1da199db346ac41b54374ba92b82f02096de047cf7eaf4dfcc123928ce83a3b|
|M1编辑FAIL|a13-wall-m1-material-edit-v2/generated-raw.png|cc2dad7c59f58a3d611529e7e52ffa876eb2e8f2a07fe368b13c153bad691ea7|
|M2候选接受，WARN保留|a13-wall-m2-material-pilot-v1/generated-raw.png|6f48ff889bd98646fed0923ba3d3d8e12e57a453c3b95bb4b7926cf6c0d00ebc|
|M3候选接受|a13-wall-m3-material-pilot-v1/generated-raw.png|c46919ecc4595ccc0620d576ad80b5ab461d7b86d2775e40eb1dd62acefbe5d8|

四份均1254×1254 RGB；每份保留工具原文件与owned硬链接，仅一份物理数据。每个目录都有调用前prompt/args/实际输入SHA、输出路径/metadata、统计/报告和manifest。材料阶段共3次新图＋1次M1编辑，逐次获得root批准，无自动重试、CLI或API替代。

## 停止状态

不再生图、不程序混边/调色、不贴墙、不生成正式mesh/shader、不运行引擎、不改main/Git。root是唯一publisher。若以后继续结构金属板，必须先批准二维模块合同，不能自动推进。
