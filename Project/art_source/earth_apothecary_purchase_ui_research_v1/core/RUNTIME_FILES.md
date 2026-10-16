# 最小runtime文件与owned耦合

## 可供未来审查的唯一新增逻辑文件

owned/scripts/core/apothecary_purchase.gd -> 拟Project/scripts/core/apothecary_purchase.gd。
此文件自含13模板受限adapter、单件prepare/commit，不读文件、不生成UI、不改变NPC入口。当前尚未复制/集成到Project，不能称运行服务可用。

## 复用而非复制新增的现有依赖

- Project/scripts/core/inventory_state.gd：stage/commit/validate及MAX_INTEGER。
- Project/scripts/core/default_warrior.gd：adapt_cloth/project/create、STATE_KEYS、内部_bounded helper。直接使用内部helper是当前候选耦合，未来主profile变更必须重跑兼容测试。
- owned同名文件仅为隔离真实引擎测试逐字复制，runtime发布不能新增第二套库存或默认profile。

## 真实数据依赖（调用方提供，不能发布测试fixture替代）

- Project/data/items/catalogue.json：调用方准确筛选原ID252,3,4,42,8,9,44,13,14,18,19,43,45，传13个原record。核心核验所用字段和全部39 raw words；原catalogue不可放宽为任意template。
- Project/data/maps/A13.json原始npcs[2]完整六字段记录，或已验证NpcIdentity sidecar.source_records[2]；不可取压缩后的runtime_npcs[2]冒充source2。
- 主NpcIdentity.resolve、当前world实例、npc_epoch、conversation revision、authority.inventory.revision：可信会话adapter构建CURRENT context。
- 唯一authority：真实controller拥有的角色金币与库存。commit返回新authority和next_conversation_revision，未来adapter必须原子发布并撤销旧回调。

当前Project缺少上述13record筛选/药师会话adapter/单件购买callback/成功发布接缝；source入口仍只0/1。核心仅可作为待集成数据候选，不可只复制文件就宣称商店已开放。

## 仅owned测试依赖，不进入runtime

owned/data/records.json、owned/data/source_npc.json：由原数据精确提取的fixture，仅tests加载。
owned/tests/purchase_core_test.gd、owned/project.godot、verify_fixtures.py、FIXTURE_CHECKS.json、RESULTS.json、headless.log、headless.exit、HOME/XDG目录：全部留外。

## 独立source研究归档

recovery-work/apothecary-original-plan/中的REPORT.md、SOURCE_INDEX.json、NATIVE_EVIDENCE.json、pharmacist-script.txt、小段*.asm、build_evidence.py与按需UI联系表可归档source研究；不属于runtime资源。只记录原EXE路径、SHA、必要原字节片段，不复制完整EXE。apothecary-shop-ui-source为下一阶段原UI资源/坐标/事件链证据，与购买核心测试分开。
