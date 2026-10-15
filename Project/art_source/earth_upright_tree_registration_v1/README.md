# Upright两实例全画布分层：仅诊断候选

只左根(50,41)及底根(61,51)，分别registration_left_50_41.json和registration_bottom_61_51.json。共享同一组6张1162×1353PNG，不镜像/旋转，不推广其它树。density4.5、统一scale2/9；底origin(2839.555556,1350.666667)，左减(528,320)。每片同origin/size，避免crop择邻相位差。没有运行时安装或生成新图。

299–303按最近原cropped矩形归属（平局原序），所有raw像素包括alpha0RGB各分一次，完整PNG重读后逐RGBA重组相同。304旧纯影显式empty、全尺寸透明仍占原身份抑源，不塞新冠。根区原302木足续边保留归属，validation单列原木足区域各owner计数，未把全根都塞299。

小量扩展像素不裁：validation给出alpha>127超原6owner矩形并集数量/比例/bbox，所有都按最近非影owner归属。低alpha远点另记并全保留。原flags/source_cell/layer/sort_y/stable order逐当前map验证。两组分别整组成功/失败，不半旧半新；无新树影。

Runner先各实例whole/fullcanvas真实GPU1×/2×对照（density4.5为非整数，不能假定CPU等价就无GPU差），再原A*绕各树后/干前/全前，检查原299早行与其余后行之间角色遮挡，特别302根续边。源world/collision/NPC/路径都不改，不因当前视口裁边省owner。结果只覆盖这两株，普通晋升另等父级。

instances.json列两注册精确SHA。build_registration.py复现，ARCHIVE_SHA256.json列13文件，诊断owner色图单放Project/diagnostics/art_source/earth_upright_tree_registration_v1不入档。raw和先前冻结清单不改。
