# 两枚方块的只读定位

原文段首字符为 U+E810 U+E810，属于Unicode私用区。按当前严格GB18030解码/回编码对应原字节 D7 FA D7 FA。

原源：原版游戏/Data/Map/A13.lpMap，SHA256 e1cc7189fc96e04312b935422ec511a078b1fbe6259b97b9e3c279732becb3e3。原包xor key=187；文件offset82785起存储字节6c416c4175690b7070510a58，xor解码为d7fad7faced2b0cbcbeab1e3，即段首两私用字符+“我八岁便”。它们确实来自原文件，不是JSON/Godot引入的乱码。

当前候选把原文本直接交Label，未为U+E810提供显示映射；实际截图显示两方块。系统NotoSansCJK-Regular.ttc全部10个font cmap均无U+E810（fontTools只读检查），与缺字占位一致。其余中文正常。没有证据说明它是未解析的#script opcode；它出现在普通文本段首。

原引擎如何显示D7FA未完全核实：可能是旧字库空白/段首缩进约定，但不能只从位置宣布已证。主Project/scripts/opening_candidate.gd:199已经在显示层使用replace("\ue810"," ")，这是现有兼容处理先例，不是原引擎证明。

推荐后续获批时仅对显示文本建立明确的U+E810→空白兼容映射并写注释；源record.script保持逐字不变，脚本SHA不能变化。不要直接从原数据删除，不要把兼容映射称为原生字体精确还原。随后root明确批准仅显示层映射；已在shop.gd的Label输入执行替换，session_adapter.reference_menu及source.json保持原文，待短测试与实际图确认。


最终显示兼容复验：glyph-headless.exit=0，23/23通过，无ERROR/WARNING；actual-glyph-window.jpg已由官方桌面截图并独立目视确认段首不再方块，gpu-glyph.exit=0，ERROR0，仍有1条相同V-Sync驱动警告。未重复交易链，旧actual-purchase-window.jpg与gpu.log保持原交易证据。source2脚本SHA再次核对不变。
