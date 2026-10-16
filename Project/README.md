> 最新局部试玩入口（2026-10-16）：导入 `project.godot` 并等待资源导入完成，打开 `scenes/earth_first_map_review.tscn`，按 **F6**。出生点、南侧道路与东廊共 178 / 2553 地块使用草地研究稿（既有 121 + 新增 57），另新增 24 个完整植物组、81 个 owner；既有样区植被另计。E 方向步行保留六帧，水池 7 / 细枝草丛 3 个 owner 保留独立整组回退。1/2/3 只移动相机至东/西/南侧，L 定位水池草丛，Home 回出生点相机，不传送角色。E/R 对比东廊/新增植物，Q/W 对比水池/草丛；其他区域仍为原素材或既有样稿。重复草纹与外围原素材边界尚未完成美术验收。**F5 仍启动原素材逻辑预览。** 详见 [局部试玩说明](docs/first-map-review.md)。Windows 尚未实测。


# Legend：Godot 2D 重建工程

目标版本：Godot 4.6.x。原素材入口验证玩法与数据，独立 Earth 入口验证重新生成的纯 2D 科幻美术。旧工作环境的源码和生成图未找回；本目录是依据原始材料重新实现并分阶段存档的版本。

## 最新局部试玩

1. 完整下载并解压整个仓库，用 Godot 4.6.x 导入本目录的 `project.godot`，等待资源导入完成。
2. 打开 `scenes/earth_first_map_review.tscn`，按 **F6（运行当前场景）**。
3. 点击走路，Shift 跑步，空格停止，F 切跟随，B/P 对比角色/地面。沿东向走路可查看 E 方向最新六帧。

这是局部美术研究稿，可走动但不是全图美术替换或完整游戏。保留整个 `Project`，尤其 `art_source`；其 `.gdignore` 使它不显示在编辑器文件面板，但运行时仍直接读取其中 PNG，不能删除或只复制 scenes/assets。当前交付为源工程，未验证导出的 Windows EXE/PCK。

命令行（在仓库根目录执行，Godot 须在 PATH 中）：`godot --path Project res://scenes/earth_first_map_review.tscn`。Windows 使用下载的 Godot 4.6.x 编辑器打开工程即可，不需要运行任何原版 EXE。

## 既有地球区样区入口

1. 导入本目录的 `project.godot`，等待 Godot 完成资源导入。
2. 在文件面板双击 `scenes/earth_sample_preview.tscn`，按 **F6（运行当前场景）**。
3. 左键走路，空格停止；F 切固定/跟随镜头，H 隐藏说明。跟随走出样区后仍会看到未重制的外围原素材。

命令行也可启动：`godot --path Project res://scenes/earth_sample_preview.tscn`（在仓库根目录执行；Godot 程序需在 PATH 中）。

当前固定样区为 768×512 逻辑单位，直接渲染为 1536×1024。初始站位保持原 `(61,39)`：64 个地表块、30 个建筑 owner（含 2 个显式空项）、35 个植被 owner（3 树、3 灌木、2 草丛）和 2 个 NPC 已接入重制资产。初始画面已核查没有未替原素材的非透明像素进入这个矩形；**这不等于完整 A13 地图重制完成**。

主角目前正式接入 SE 朝向 4 帧待机、6 帧步行，以及 E、S 朝向各 4 帧待机，共 18 个新动作相位；E/S 步行、其他方向及跑步仍完整回退原素材。已核平地区域内接入主角（SE 待机/步行、S 待机）、方丈、凌云子、首棵树及左侧直立树（50,41）的新投影，五个有效投影取最大遮蔽并只合成一次，避免同一主光源的重叠影过黑。各自资格独立；凌云子和首树需新楼及对应接收面有效；左树使用独立世界接收区域，路缘按二维共面装饰近似，底部直立树仍不开影。S 待机使用独立主体与靴底接触近似，脚后仍有较细过渡，不宣称真实物理光照。E 方向及其他未覆盖动作不启用新主角影；其余植被、建筑及台阶投影尚未完成。此入口不执行完整剧情/战斗，R6 新游戏候选仍独立保留。

初始样区之外，南侧已接入另外 3 株直立树和 1 株圆灌木（22 个 owner），复用已审重制资产，保留各实例原位置、遮挡顺序和碰撞。当前合计 6 树、4 灌木、2 草丛；南侧地表仍为原素材，新增四株尚无新投影。

对照键：B 主角、N 两个 NPC、P 地表、T 主楼、V 六株树、J 四株灌木、K 两组草丛；各键在新/原资产间切换。S 控制新投影，G 显示原碰撞格。资源组校验失败时整组回原素材，不混画半组。

已验证 Linux / Godot 4.6.3 的干净资源导入与运行；Windows 尚未实测。不要把 Linux 验证当作 Windows 兼容性保证。

## 启动与当前范围

使用 Godot 编辑器导入本目录的 `project.godot`，等待资源导入完成。

- **F5 默认入口：** `scenes/game.tscn`。A13 原版场景走动预览；左键走路，按住 Shift 跑步，空格停止，G 显示碰撞格。
- **屋门预览：** 打开 `scenes/portal_preview.tscn` 后按 F6。A00 房间出门、返门的原传送点可用。
- **地图加载诊断：** 打开 `scenes/map_load_candidate.tscn` 后按 F6，以 F1–F9 检查原脚本的 NPC 隐藏、门禁开闭和固定姿态彩蛋鸡。随机值为显式诊断输入，无 AI/战斗。
- **NPC 剧情候选：** 打开 `scenes/opening_candidate.tscn` 后按 F6。点击方丈、凌云子，沿原按钮对话，可到 A00 房间。此入口显式预设 ET1/STOP；尚未执行完整地图加载脚本，不能等同完整新游戏。

目前没有完整战斗、背包界面或完整游戏存档。新美术仅限上述独立样区。A01/A02、原动作和物品数据已提取存档，但数据存在不代表玩法已接入。Windows 尚未实测；已验证平台为 Linux / Godot 4.6.3。

## 已验证的小阶段

- R1：原 A13 地表、物件与 NPC 绘制；原角色128移动相位；寻路、阻挡及树前后遮挡。
- R2：独立 A00 屋门往返；九处原门禁保持关闭。
- R3：独立两 NPC 对话链 ET1→2→3；换图前先检查全部候选事件和目标资源，失败不提交一半进度。
- 纯对话内核：原脚本分支、按钮、ET/BT、候选事件及失败回滚；尚未支持所有原脚本指令。

范围和已知适配差异见 `docs/R1_SOURCE_PREVIEW.md`、`docs/R2_HOUSE_PORTAL_PREVIEW.md`、`docs/R3_NPC_OPENING_CANDIDATE.md`。

## 文件与存档规则

原版游戏和参考项目位于仓库上一级的同名目录，保持不变。生产资产、实际代码、可复现提取工具及必要设计说明纳入 Git；测试夹具、诊断截图、临时文件、引擎缓存和游戏存档不上传。

每个小阶段验证后提交至 Legend，并核对远端提交与文件树。工作目录内的副本不作为独立备份。详见 `docs/RECOVERY_PLAN.md`。

## 可选普通战士新游戏候选（R6）

在 Godot 4.6.3 打开 `scenes/new_game_candidate.tscn`，按 F6，点击“踏入江湖 · 创建角色”。阅读原五页，再依次与方丈、凌云子交谈，可到 A00 首房。默认 F5 仍是 R1 原图预览。

此入口已有单一实例库存初始布衣、真实原地图加载脚本、STOP 与原 NPC 剧情。界面明确标记兼容 RNG，其算法并非原 VB 随机流；彩蛋鸡仅静态显示，无 AI。当前无保存、战斗或后续任务，Windows 未验证。完整事务边界见 `docs/R6_NATURAL_OPENING_CANDIDATE.md`。

## 历史庭院技术入口（非当前美术方向）

下面的 `art_preview.tscn` 及其 E/SE/S 美术来自已被否定的庭院探索，仅保留技术对照。请勿把它们当作上方 Earth 入口的画面或动作覆盖范围。

Temple art preview: in `scenes/art_preview.tscn`, T toggles the selected A13 main-temple v2 cutouts and F5 shows its stair with the source hero. Only 30 source Building owners are replaced; no new building cast shadow or platform receiver is claimed. See `docs/A13_TEMPLE_ART_PREVIEW.md`.


The same optional art preview also has G for the reviewed first A13 golden tree and F6 for its trunk-front source-hero view. Only seven exact owners change; nearest sampling and original depth order remain. G now switches the selected tree with one whole-alpha ground cast; H toggles that cast for comparison. Failed cast preparation restores the whole source tree. See `docs/A13_FIRST_TREE_ART_PREVIEW.md`.


The optional art preview has30 selected phases: E/SE/S each four idle plus six walking. Select1/2/3, C cycles idle, P advances all poses, and M for that direction's verified two-cell route. All three share fixed86 single-shadow sampling; each returns to its own idle. B switches to original body/head, S toggles hero shadow. Other directions and run remain outside this optional preview. See `docs/ADJACENT_IDLE_ART_PREVIEW.md` for bounded movement/depth review and retained pose differences.

The optional art preview also offers **J** to switch the two exact A13 NPC records
(方丈 / 凌云子) together, **K** for their single ground shadows, and **F7** to view
them. Their shared four-phase clock is17 updates/phase. This is an art-only preview;
R1 and R6 NPC dialogue/gameplay remain source. See `docs/A13_NPC_ART_PREVIEW.md`.
