# Source-only research archive

当前最佳整身设计研究候选；固定窗、相间动作及完整动画仍FAIL。

实际raw、prompt、送图refs与当时合同原字节保留；RESULT是归档时快照。不是运行时资产或动画验收。

运行 `python reproduce.py --output /path/out`，只需Python与Pillow。固定整窗映射，不清alpha、不独立fit、不镜像。catalog输出只是原512槽精确拆分，保持[57,60]/[58,61]/[62,59]，不播放或事后换相。NPC使用完整1254窗预乘alpha LANCZOS至384。

原诊断图、GIF、测试harness和运行闭包不随包归档。原RESULT中指向这些外部审核证据的路径不是replay依赖。
