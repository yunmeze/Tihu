# Earth 首树7owner静态分层候选

仅根owner(57,34)的Plant292–298这一个实例。父级已批准原owner矩形外约0.78%新冠边像素作为待审扩展。本包准备静态切片与registration给runner，不修改运行时、地图、flags或碰撞，不推广其他株。不生新图、不追加树影。

## 固定坐标与身份

raw来自earth_first_tree_boundary_repair_v2/raw.png，1254×1254；统一density4、scale0.25、world左上(2630.25,784)。木根raw(523,1224)→world(2761,1090)，人工新读点±8raw，原点±4逻辑。无局部warp/拉伸/逐片配准。

保持完整7个key/source_cell/flag/layer/sort_y/stable_source_order。292为y34；293–298为y37。292 flag=-1，其他flag0。顺序不改，原A*不改，扩大的是纹理canvas，不是collision。

298原为纯烘焙影外缘。本候选无新树影，298明示empty、保留其身份并抑制原图。其余6片承担所有新raw像素；绝不利用298放大块新树冠。

## 每像素分层规则

在固定world空间，以像素中心到原292–297六个cropped world矩形的欧氏距离选最近owner；原矩形内距离0保持原owner，扩张冠边分到最近/相邻原owner，精确平局按原draw顺序。所有raw像素（包括alpha0背后的RGB）分配恰好一次，不按颜色去边、不阈值裁掉新叶、不更改raw。owner-labels.png中1..6对应292..297，298空。

每片从原raw按标签复制RGBA，局部未分配区域为透明0，纹理使用标签全域bbox；因此会保留远处低alpha杂点及透明RGB，不偷裁主体。registration的world_top_left由同一raw_rect和固定scale推导。其texture字段当前指向art_source，只是待审资源；尚未进生产asset路径。

validation.json验证每raw像素coverage恰好1、内存及重新读盘后所有RGBA字节重组完全相等。该重组测试包括透明RGB，不仅alpha合成视觉近似。切片间alpha非重叠，因此正常alpha合成在像素格上与原raw等效；GPU过滤/采样缝仍须runner核验，不能以离线相等代替。

低alpha远点另列统计：alpha1..16且距alpha>16主体超过16raw像素（4逻辑单位），全部保留；不删除明亮叶缘。定义只是便于审图，不声称这些点全是视觉瑕疵。

## Runner交接

入口registration.json包含7个原身份、各PNG/SHA/尺寸、共同scale与world位置、显式空298和7个suppress_source_keys。只在全部资源/可信源身份匹配后原子抑制7个source；任何空项身份丢失、PNG/hash/尺寸/scale异常应整组回退原7片，不能半树新半树旧。empty298不是漏资源，透明1×1占位PNG仍可验hash。

先同world矩形[2496,960,768,512]、同角色相位切源/新、独立1×及真2×截图。继而按原flags可走路线围绕树、穿过y34与y37前后排序线，检查292与其余6身份间角色遮挡，不挪根/角色救图。可从原first-tree source contract的recommended_static_route复用路点，但需以当前map/NPC再次核验。不可承诺未实际走的路线通过。

关切点：叶簇形状变化、右枝扩展、原可走格上方冠遮挡、切片过滤接缝、根接触、source棋盘影是否全消失、298是否确实不留旧影、B/P及现有建筑主角是否受影响。没有新增树影是本阶段明确限制，不可宣称光影完成。

交接给runner即可，不在本包自行接runtime或GUI。父级决定样区可否保留；全图其他树仍source。

## 复现/归档

`python Project/art_source/earth_first_tree_registration_v1/build_registration.py`，依赖Python/Pillow/numpy/scipy。仅写本目录及Project/diagnostics/art_source/earth_first_tree_registration_v1。ARCHIVE_SHA256.json显式列12个文件，不含诊断图/清单自身。输入raw与source契约SHA记录于registration；原地图SHA记录于registration和validation。
