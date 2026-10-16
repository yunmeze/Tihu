# Owned药师单件购买数据核心候选

## 范围与状态

只在本目录实现。没有修改Project主树、白名单、源NPC、VM、main scene、UI或运行入口。不含REME/REPET、卖出、使用药品、拆药包、数量/全部、堆叠、腰带模型或存档接线。

主实现owned/scripts/core/apothecary_purchase.gd。owned依赖inventory_state.gd/default_warrior.gd为当前主树逐字复制；verify_fixtures.py仅核实依赖及源fixture，不替代实际GDScript业务测试。

测试owned/tests/purchase_core_test.gd已在planner批准的独立30秒窗口运行：Godot4.6.3 headless+Dummy，exit0，190项断言全部通过，无ERROR/WARNING。使用owned HOME/XDG，约1.7秒结束并归还窗口。见RESULTS.json与headless.log。这是实际GDScript数据核心测试，不代表主UI或真实服务已接通。

## 接口

- prepare(authority, records, context, {item_id: "3"}) -> {ok,ticket} 或 {ok:false,error}
- commit(CURRENT authority, records, CURRENT context, ticket) -> {ok,authority,instance_id,next_conversation_revision} 或失败
- 输入永远不修改。prepare用真实Inventory.stage/commit在分离快照构建候选，不发布。commit根据当前authority和context全量比较旧base并重新prepare重放，只返回新authority。唯一发布责任在调用方。
- 调用方必须串行提交并将返回的authority、next_conversation_revision一起发布；不可传旧快照冒充CURRENT。
- context由可信会话owner构建，不能来自UI或网络payload。包括map_id=A13、source_index=2、完整source record、固定script_sha、world、epoch、conversation_revision、inventory_revision。数值身份不是密码；本模块不是不可信客户端的认证系统。入口adapter仍需真实NpcIdentity.resolve校验世界和source sidecar，并保证原药师会话确实打开。UI只提交商品ID，不能选择价格、数量、NPC身份或context。
- ticket递归只读并重放比较；不使用crypto签名。内部可信调用方不得任意构造替代有效会话/票据。

## 13模板受限适配

source records仅布衣252与药师12种商品，名称/ID/价格/重量/type/icon/HP/MP和39原始words逐项验证；不放开全部720模板。布衣仍走原Profile.adapt_cloth。药物只允许购买，adapter的consumable=false是本阶段能力边界，非断言原药品不可使用；Core没有generic consume入口，不能拿此目录开放使用。

完整authority.inventory先由真实Inventory.validate验证：所有实例必须唯一占一个位置、无悬挂或重复引用，重量包含背包和全部equipment，并检查溢出。仅允许一件布衣在armor、其他equipment空、药品在bag、无recovery。重量override仅null或等于原模板重量；未知override、额外位置、额外装备fail closed，不忽略。

随后构造不发布的cloth-only投影调用未修改Profile.project验证非inventory字段；药品不会从真实authority删除。最后与Profile.create初始战士基线比对：level1、普通模式、experience0、原base/技能/点数等完全一致，允许名字、金币与有效范围当前HP/MP变化。不是通用职业/升级角色adapter。

原重量cap=25；原空槽42。已经有相同药也必须另占槽。原失败优先级：合法输入先空槽，再重量，再金币。空槽用尽、总重超25或缺钱不发布任何数据。药包独立模板，单件扣原价。

## 与原EXE差异

保持正常购买结果及失败条件顺序。原EXE在调用GIVE前扣钱且调用者未见退款检查；本候选内部错误全回滚是明确安全增强，不宣称复现原bug。没有RNG输入或随机调用；本阶段药品购买不消费随机数。若以后涉及会耗RNG的模板，不能沿用此无RNG契约。

## 测试限制

初始战士布衣重2、每药至少重1，所以正常可达购买状态在触及42槽前通常先受25负重限制。测试用结构合法但overweight的42药fixture验证“槽不足优先于负重/金币”原优先级，不通过零重伪造来制造自然可达满包；不能将该fixture称实际购买路径。

不包含完整原商店UI事件、source映射adapter集成或真实鼠标验收；这些要在独立候选被批准接线后另测。
