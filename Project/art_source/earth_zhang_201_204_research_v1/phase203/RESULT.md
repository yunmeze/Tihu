# 单203一次实验：身份延续，原坐标微动稳定门槛未过

源203八个世界注册patch相对201最佳位移均(0,0)，有表面像素变化；实际source offset(-1,-44)已在96完整窗施加。生成仅用source203-fixed-world.png和201(-5,+1)注册身份图，不用202原图或202刚性版，未扩大为整身呼吸指令。

可用：脸/短发、夹克拼片/拉链、蓝内层、裤鞋及高低手势延续，身份可认同一人。没有新增武器/长袍/影。
仍未过：全窗下主体向右下，鞋位置不够稳定，裤袖体量略增加。相对201局部patch约：脸(+1.25,+.5)，左肩(+.75,+1.25)，右肩(+1,+1)，高手(+.5,+.5)，低手(+1.5,+1)，腰(+1,+1)，后鞋(+1,+1.75)，前鞋(+1.25,+1.75)logical。RMSE15.6–40.0、读数约1–2logical不确定性；非精确骨骼。强alpha面积1320.6875→1419.375logical²，+7.4724%；不能将面积比直接称宽度比例。
这与202的生成偏移相似，但不能直接沿用202补偿。任何203新注册须单独提案/批准；本次无额外平移/scale/bboxfit/肢体修改。201原高手源偏差(-6,+1)继续保留。204未制作。

查看201-203-pair-1x.png/-2x.png/-4x.png，201-203-toggle-1x.gif/-2x.gif/-4x.gif（每相340ms，仅两相实验），static-alpha-rgb-difference-4x.png。原坐标fail不因身份可用改写。

实际链：contract-before-generation.json/prompt_actual.txt为调用前冻结，refs顺序source203-fixed-world.png、identity201-fixed-world.png。原返回generated_images/exec-859544e4-f5d5-4a70-9b99-1e0c53b59978.png。
raw SHA5315be8918bf6d2352404db65f8abf66cd17f8edd2b7bb452e6e6c311b200365，1254方/96logical，真实D13.0625。
review.py整raw RGBa LANCZOS→384方density4，candidate203-complete-density4.png SHA49fa26e450b8269b25fd2c4da1ceb48dfb21960baa4c45cf795376dc6d746dfa。无额外注册或alpha清理，10972个raw alpha1–2保留。
track.py只诊断不改变图。无Godot/生产/Git/runtime，无自动204或重抽。
