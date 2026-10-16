# 候选最小闭包与 source 研究可移植清单

## 独立参考界面运行闭包（仍非 Project 服务）

- owned/project.godot、shop.tscn
- owned/scripts/shop.gd、session_adapter.gd
- owned/scripts/core/apothecary_purchase.gd、inventory_state.gd、default_warrior.gd
- owned/data/records.json、source.json
- owned/assets/panel.png、buy.png、item_{3,4,42,8,9,44,13,14,18,19,43,45}.png

该闭包可独立打开，但必须保留标题/诊断区能力限制。session_adapter 持有自己创建的测试角色、2000金币；固定 world1/epoch1 只对本独立会话有效。它不是主世界 adapter，不能原样接入真实 NPC。source.json 含原 A13 source2完整记录与脚本，core另核完整字段与scriptSHA；records.json为原13模板受限fixture。文件级 source SHA 用于追溯，实际安全边界仍为core字段/脚本/模板核验与独立可信调用方。

未来 Project 最小新增逻辑仍是 apothecary_purchase.gd，复用主树 Inventory/Profile；UI scene/controller必须改成由真实 controller 提供唯一authority与world/epoch/conversation/inventory revision。用原 catalogue 与 source sidecar替换owned fixture加载；接入口、发布新authority/撤销回调、关闭流程仍须单独授权审核。不能复制本独立adapter就称真实服务可用。

## 资源研究可移植归档

- apothecary-original-plan/REPORT.md、SOURCE_INDEX.json、NATIVE_EVIDENCE.json、必要*.asm、pharmacist-script.txt、build_evidence.py。
- apothecary-shop-ui-source/REPORT.md、UI_EVIDENCE.json、extract_ui_evidence.py、原ScriptBuy.gif/PackageBox.gif与必要事件*.asm。PNG只是无损预览；完整EXE不复制。
- 本候选 owned/data/resource_sources.json列12图标的原包offset/bytes/hash，原包总SHA已与索引核对；SOURCE_VERIFICATION.json和OUTPUT_SHA256.json用于归档完整性。
- 两个提取脚本当前仓根是固定绝对路径，迁移时需改根参数；JSON所述VA/fileoffset/hash独立于workspace。不要因脚本能解析而声称所有VB字段已证。

## 留仓外的验证文件

owned/tests、SOURCE_VERIFICATION.json、RESULTS.json、GPU验收记录、所有*.log/*.exit、launch-gpu.sh、home/cache/config/data和.godot缓存。GPU日志含完整测试角色state，无用户存档。

截图只一张原尺寸实际窗口；不是最终HD皮肤，也不证明未知选择框/Tooltip/字体/运行时原窗口全局位置。
