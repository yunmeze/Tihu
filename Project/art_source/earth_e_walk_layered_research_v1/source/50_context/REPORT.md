# 单50右向侧视完整上下文上裤生成：一次执行，结构失败冻结

## 结论
本次唯一一次生成确实改善腰下黑布、旧手孔和侧身裤褶，但没有按指示去除旧上裤层的双膝金银残岛。右膝最明显：raw已经保留旧银甲块并用新深色/浅金弧带连到下方冻结新胫，最终合成仍是重复甲结构。不是mask外保护把旧甲带回来，也不是后处理才产生的问题；77旧甲明确内部全部在7611可编辑union内。故本次不通过，不扩域、不重抽、不用补布覆盖甲岛。

“若成功再交六相静态板”的前提未成立，本轮没有把50列为成功候选组成六相板，也未借帧。原45/46/47/48/49研究材料完全不动。所有输出标研究失败证据，不普通晋升。

## 执行与原始材料
- 内置image_gen单次调用，三张冻结输入：完整未补上下文／原源50姿态／精确union guide。
- 实际提示词为prompt-PENDING-APPROVAL.txt，审批后原文使用；BEFORE_CONTRACT.json保存批准合同与输入hash。
- raw.png为原始1254×1254透明输出，SHA256：4ab1194ff610bdebb085eefc7287b35625e92c3d4d3aff5323584ecbe0716d48。
- 所有原层和参考只读，没有执行EXE、GUI、Git或生产操作。

## 独立锚与映射决策
非编辑头、肩、腰金属三个模板与union相交均0，独立匹配的全图uniform尺度1.000734104392641，平移[0.05520514971732382,-0.09677942909650028] HD4。拟合中心残差约0.082/0.037/0.046逻辑像素。相对47/48显著zoom，本次基本保留原构图，因此没有应用这一微小诊断fit，也没有第二次密度调整。
实际合成固定512/1254全画布映射、平移0、旋转0；直接从raw单次BICUBIC采样，output→raw affine=[2.44921875,0,0,0,2.44921875,0]。
留出两靴以global-scale模板诊断中心残差约0.051/0.060逻辑，后胫约0.047。前胫诊断模板与union有5个半透明点相交，不作为严格独立留出证据；两靴模板均0相交。局部最佳尺度只作诊断，从未用于局部变换。
测量用512 resize预览，实际合成direct affine各自明确命名；MEASUREMENTS.json保留测量，不把预览当最终采样。

## 保护与精确采样
- union7611，与审批前精确mask保持一致。
- 最终RGBA变化6457，union外0，原protected alpha255最终变化0。
- 原protected alpha1–254最终变化1894，其中alpha128–254为1530；这是新donor下的正常source-over，未伪称全部原保护域最终0差。
- 冻结输入所有hash匹配。
- 原保护层纹理/矩阵不改；旧上裤层没有在donor之上重新盖回。
- raw-sampling-safe-footprint-NOT-EDIT-MASK.png为±4原图采样足迹，仅证据，不扩编辑域；足迹外响应测试union内0。

## 手边独立审图
新手原层保留，最终未看到明显完整第二只手。raw腕/指轮廓比原图略宽且更暖，新手下缘/指侧存在红褐细边和明暗加重，不能把“原层未改”解释为raw手甲完全未被采到：union允许原半透明层下取样，边界处raw手指可能参与底色。hand-context-raw-final三底图保留这个残差。未做颜色阈值清理、手边扩mask或再次生成。即使手边将来可接受，双膝旧甲结构仍足以判本轮失败。

## 审图文件
- 50-source-context-raw-composite-{1x,2x}-{gray,light,dark}.png：源／原上下文／raw固定映射／严格合成。
- 50-joints-context-raw-composite-{gray,light,dark}.png：腰手双膝。
- hand-context-raw-final-{gray,light,dark}.png：手边。
- duplicate-right-knee-context-raw-final-{gray,light,dark}.png、duplicate-left-knee-context-raw-final-{gray,light,dark}.png：旧甲归属与残留。
- independent-anchors-diagnostic.png、MEASUREMENTS.json、PROOF.json。

已亲看完整2×灰底、全raw、三列接口浅底、手与右膝放大。腰161旧候选、71衣料失败以及原50所有历史材料均未修改。
