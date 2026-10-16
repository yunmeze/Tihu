# 可选入口：原版自然开场 + 局部 Earth 美术

此入口使用同一套 R6 权威剧情状态与 Earth 显示适配。第一关完整验收尚未完成。

## 启动与操作

在 Godot 打开 `res://scenes/earth_new_game_candidate.tscn`，运行当前场景；或从 Project 执行 `godot --path . res://scenes/earth_new_game_candidate.tscn`。默认 F5/main_scene 仍为 `res://scenes/game.tscn`，原 R6 和美术 review 入口行为不变。

创建角色后阅读五页开场，左键点击 NPC 和选项推进原剧情，ESC 关闭对话。STOP 时不能移动；允许移动后左键选择可达位置，Shift 使用原跑动逻辑。窗口保持比例，黑边点击忽略。逻辑画面1024×768，渲染密度2×。正式入口没有评审相机快捷键，不固定彩蛋随机种子。

## 范围与显示合同

- 同一个 R6 控制器、VM、库存、RNG、50Hz逻辑与原子地图事务。初访自然剧情到 A00，A00 使用原显示。
- A13 已登记121+57=178个地面 owner、24植物实例/81 owner、pool7/clump3，以及各自合格的建筑、NPC、植被、18相位和E六相。未覆盖或失去资格的内容显示源图。
- 原 source/atlas/owner/receiver 门禁不放宽；鸡额外图集仅允许完整预检的精确闭包。资源丢失仍依原规则实时回退。植物与虚云没有新增影子；E方向没有已验收的新投影阴影。
- 可选入口合并同一显示帧内视觉请求；每次实际flush仍完整验证，发布、重新准备和必要的NPC点击同步flush。两次flush间短暂坏又恢复且未显示的状态不承诺旧逐physics视觉撤回行为。直接refresh仍即时。默认R6不采用此调度。
- 地面裁剪保持数据、资格和源顺序，仅跳过视口外绘制。投影quad覆盖完整逻辑viewport，保持原光照、receiver和max-alpha规则。

## 排序与 owner 预筛

A13 factory 使用 `snapshot_prefilter_world.gd`，继承 `snapshot_sorted_world.gd` 与原 snapshot world。`sort_reuse_enabled`、`owner_prefilter_enabled` 默认均启用，可独立关闭。

排序复用前检查完整对象流与独立基线的类型敏感一致性；未知值、非有限值、排序键平局回原路径。hero每帧按原键插入，动态NPC保持原路由。完整父refresh验证后建立保守候选owner集合，包含空owner；集合内继续执行全部原helper优先级，集合外才直接走原source fallback。资源prepare前后使预筛失效，不缓存跨帧正资格。

保留 first_map 绘制前 `refresh_xuyun()` 即时验证。受保护源方法SHA变化会关闭优化并使用原路径；维护时必须重新审计实际父方法，不能只更新常量。

## 2026-10-16 本轮实际验收

同一冻结组合完成真实创建、五页开场、STOP地面拒绝、ET1提前凌云A1→ESC、方丈A1–A5、凌云B1–B5、ET3/UNSTOP到A00(138,12)、黑边忽略及实际走到(138,13)。自然进程exit0，54/54语义检查、21里程碑匹配，23张实际窗口截图。五项故障/单tick CPU探针不当作自然链等价。本轮已补提前凌云，旧52/53阶段记录保持历史原样。

当前原路径与优化路径各52张实际framebuffer，全52对RGBA和slot一致，184项检查通过，两进程exit0。涵盖1×/2×、resize、出生/东/西/南视图、E45–50、材质撤回恢复及影子正反控制。出生影子on/off实际变化44,507/177,922像素，其中17,688/70,709位于旧768×512quad之外。缺148声明或receiver与影关图完全相同，恢复后与影开图完全相同。

虚云body在refresh之后、draw之前移除且不再refresh，实际回源并与独立源控制相同；恢复后重新显示，1×/2×变化1,532/6,156像素。pool主材质撤回与源控制一致，恢复精确还原；57正向控制在相应视野有非零像素变化。ready计数不能替代上述实际像素证据。

独立headless覆盖原R6逻辑、rare、receiver、生命周期/回滚、严格类型、资源失效、默认入口、当前显示描述和调度；13套继承矩阵1183项，另调度17、排序32、owner165项通过。测试、日志和截图不随发行工程打包。

## 性能读法

本轮同状态ABBA使用Linux llvmpipe软件渲染、相同seed208/出生相机/fullquad/2×密度、1024×768窗口；3秒预热后约20秒真实墙钟计数。唯一变量为联合排序与owner预筛：

- 正序：基线187帧/20.053673秒 = 9.325 FPS；优化211帧/20.017112秒 = 10.541 FPS，提升13.04%。
- 反序：优化220帧/20.087116秒 = 10.952 FPS；基线192帧/20.055226秒 = 9.574 FPS，提升14.40%。
- 四例均exit0，累计权威49.87–49.98 ticks/s，每显示帧1次flush。焦点只观测起止，实际VSync为0。

自然观察开场五页期间滚动FPS中位22，此时原逻辑暂停权威推进和视觉tick请求；开场后A13实际游玩中位11。把两者混算得到21不能用作收益基线。只有上述同状态ABBA用于本次收益判断。旧独立原型的增益不能相加。

画面仍约10.5–11 FPS，未达到50FPS；完整验证、剩余对象分支、地面遍历与2×像素成本仍在。上述软件渲染结果不能推断用户Windows硬件表现。首次准备/失效重建成本仍存在，不把稳态收益当作最坏帧保证。

## 构建、导出与未完成项

`tools/earth/build_snapshot_registration.py --project . --output ../snapshot-rebuilt` 从tracked输入重建声明，输出须在Project之外。148项runtime SHA为 `d5fe14f49f71e6b2d1b4d7b22d6010ea0619ab8e50043c7eb3bf4422de1d5dd4`，receiver SHA为 `0292fcd96402ec0b26cd4b2d6d99cd069aa7e77a973e434f39fa6f15e1ce3534`。JSON内待测文字保留生成时历史状态，当前验收范围以绑定代码版本报告为准，不改受测资源SHA。

两个新脚本由明确preload代码链进入导出闭包，不属于148项资源/契约清单的新增数据条目。新发行须另建代码SHA闭包，纳入两脚本及UID；旧冻结export policy保持原样。被FileAccess核SHA的源GD必须保留原字节，不能仅以编译GDC替代。receiver中的单一Python依赖为显式hash-only叶子，相关来源注册为明确raw-only叶子。新代码组合的发行包闭包与Windows运行仍待独立验收。

snapshot构造必须显式调用父构造并保留正确floor绑定；后续回归需看framebuffer。虚云目前仅静态身体与命中显示，原服务未实现；开场交互限制仍有原数组索引局限。整张A13完整美术、草地严格无缝与外围边界、完整动作循环、E影子、其余NPC服务、战斗/怪物AI、保存和完整游戏流程均未验收。
