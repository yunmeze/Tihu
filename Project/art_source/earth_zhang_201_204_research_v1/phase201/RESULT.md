# 张天师单201 attempt1

一次授权生图完成，供root审图；无四相复制、runtime或后处理变形。

可用设计：灰色短拉链训练夹克、蓝内层、独立深色裤腿与紧凑鞋，独立成熟脸和自然短发。左屏高前伸手/右屏低手和前后错步仍成立，未知小延伸读作手旁小轮廓，没有放大成武器。无长袍/重甲/道具/地面影。

未通过精确源姿态注册：人工可见点±3logical，高前手(-1,0)、脸(+5,-4)、低手(+6,+1)、左屏后鞋(+10,0)、前鞋(+8,+1)。原古冠未计入头高比较。手位置相近但躯干/鞋整体靠右，不能单一平移全部救回；没有拟合、移位或缩放校正。independent-points-4x.png与landmark-review.json保留读点和误差。小图仍可判断现代造型价值，但脚位置/相对手身关系须root另判。

查看samecoords-1x.png/-2x.png/-4x.png（左源右新）；actual-source-ground-2x.png为原A13真实全流，仅替record4当前201，CPU1x后nearest2x。原地面/楼体保持源版本，未模拟生产样区新楼。

## 实际输入链
contract-before-generation.json冻结两refs：primary-source.png（原201完整96方窗）与source-reading.png（原可见点阅读）；prompt_actual.txt为实际完整调用文本含末尾换行。未提供其他NPC或失败候选ref。
原返回 /workspace/scratch/22c897619190/generated_images/exec-eb9c89f0-3ef8-4dbe-9fc7-4edf135c3a8b.png。
generated-raw.png SHA256 df57d40731f05c24bd302d3dcb5fc2eee040da4c16291daff8e714075dae7127。
raw1254方，对应96logical完整窗，实际13.0625像素/logical。
review.py对整raw RGBa LANCZOS均匀→384方density4，worldorigin(1668,1032)，mapanchor(12,56)，无bboxfit或alpha清理。candidate201-complete-density4.png SHA814b3d6dcadfd88405f5997f8073e8746c6d929a774d920571a701523f880364。
8442个raw alpha1–2全部保留。没有程序改肢、影子、强轮廓剪切或合成回贴。

这是单201设计。源201–204为四种微动，202原offset+1logical，不能同图复用冒称四相完成；后续动作仍待授权和制作。
