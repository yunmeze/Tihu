# 小楼280–289：阶段接入与局部视觉资格

本阶段接入的是完整10-owner高清小楼身体，不代表整关美术、性能无损或完整玩法验收。原10个source身份、flags、绘制顺序、碰撞与门坐标不变；空285仍参与完整组资格且不回画原建筑。9个非空owner使用同一master与最近邻ID数据mask，颜色显式LINEAR，保持原owner层序。所有新真实边缘保留，未按原含影alpha硬裁。

## 资格与回退

小楼逐draw及需要其遮挡判断的query重新核验10个完整source/runtime身份、Building完整header、page列表及280–289完整descriptor。自己的任一身份、body、mask、bounds或注册依赖失效，整组回原版；恢复后重新验证。原reload阶段所有map/manifest/page/body等SHA保护保留。

这是明确的新局部依赖合同：无关pack或Mon220绑定错误单独发生时，不要求小楼一起消失。其他NPC、草地和投影的全局guard保持原样，仍各自拒绝不合法上下文；小楼通过不表示整个世界通过。原全局atlas面对非Dictionary pack的类型异常列为遗留项，本阶段没有混改；新小楼对int/null/bool/string/array均安全拒绝。

移除的是refresh阶段重复的小楼校验，draw/query即时校验不缓存跨帧布尔值。实验性屏外shader脱离和uniform去重均默认关闭，保留已测代码、不做额外重构。当前排序、owner预筛及Xuyun draw前资格保留，proof pins、builder和receiver声明pin同步。稳定NPC原source身份规则见[开场说明](optional_opening.md)，不回退到数组索引授权。

## 当前正确性证据

原61资格断言、11query组和141局部scope例通过；5类无关变化保持小楼并验证其他相关全局guard拒绝。212新实际渲染采样与44冻结历史正确oracle逐RGBA摘要/尺寸一致；26fresh query、仅queue_redraw的晚body失效、空285变异、恢复与地图重入通过。完整当前矩阵402新样本、164ca55源oracle对照及74直接同态比较通过，24实际到达和12原阻挡拒绝保持；排序、预筛、Xuyun和旧投影资格正向检查均通过。

源固定窗与精确地标合同的历史失败不改判；采用已单独批准的整楼uniform注册及0.0935%强body支撑扩展。两处脚接触被前景树遮住仍不确定。无新建筑投影、无新增门交互，不改变原可走格。

## 干净导入与PCK

独立最小源289项raw依赖共60231389字节，零symlink、空导入缓存。154项运行声明与receiver重建byte-exact；实际冷import、export、source及第二空目录PCK验证全部exit0，所有原路径/尺寸/SHA通过，source/packed资格状态同字节。运行声明SHA：`d04cf7325b625bda052631e2bced088645bfaf2ce5531274a8a07a05196fcf45`；receiver仍为`0292fcd96402ec0b26cd4b2d6d99cd069aa7e77a973e434f39fa6f15e1ce3534`。声明中的历史待测文字保留受测字节，当前范围以本文及对应证据为准。

Linux数据PCK88713960字节，SHA：`e133f482e5ee617acc639e975d973dccbec82ed02fbbd57a0d7ea7a6d9569e3c`。1×/2×、普通小楼/非二进制屋顶/屏外出生三视野、源/身体/缺件/恢复四态产生24对新source/PCK实际渲染采样，RGBA摘要和尺寸全部一致；两侧missing等于source、restored等于body。

独立工具显式add_file保留FileAccess及Image读取的原字节；source有64次rawImage警告，packed有16次小楼body/mask警告，均保留，不能称零warning。首CPU配置SHA拒绝和桌面/tmp namespace不可达发生于对应引擎运行之前，已保留；随后准确转移本次自行生成的缓存和PCK，901文件前后SHA不变。旧导出政策不能只换commit冒充新闭包通过；新工具单独版本化，不混入本次13运行/build文件。

## 性能与平台边界

Linux llvmpipe软件渲染同状态ABBA，1024×768逻辑窗口/2×栅格，可见楼ca55基线平均12.390FPS，新楼11.785FPS，观测成本4.88%；出生屏外10.637→10.493FPS，成本1.35%。单候选旧global→局部资格约4.5→0.95ms/次，但仍有新增高清身体代价。每变体仅两次顺序样本，不宣称统计显著或性能无损。

逻辑约50ticks/s、每显示帧1flush并不等于50FPS；软件渲染背景仍约10–12FPS。本阶段接受明确成本的可交付身体，不为不足1ms继续扩大优化范围。未验证Windows启动、Windows原生GPU、EXE或完整游戏流程。PCK通过仅证明该Linux数据包与此处限定场景，不替代这些验收。
