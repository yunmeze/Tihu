# S59局部身份参考板：身份未过，独立失败研究

原59完整窗是姿态参考，身份只给approved idle17的脸/发、肩胸、腰腹、靴局部裁片。实际板原字节保留，源59实际ref依赖旧tracked包。单次raw/prompt/request未改；MANIFEST历史proposal状态是调用前证据，实际调用已由作者确认。

手差约+5、足差约−7.45，交叉方向较前次改善，但膝上胫甲遗漏、黑裤延长、腹部银片增加，角色身份未通过。不能称严格单变量A/B：参考板缺少腿甲，prompt也将原dark/silver lower-leg armor弱化成boots，输入合同存在缺口。不是runtime素材，不从失败raw拼接修补。

重放：python reproduce.py --project /path/to/Project --out /path/to/new-output
Python/Pillow核两个actualref字节；从tracked idle17首512格按冻结矩形重建四个原裁片，并逐像素核统一nearest2x内容在actual板对应位置。板文字本身原PNG字节保留，避免字体环境差异；不伪称字体可移植重建。raw整1254RGBA统一LANCZOS512，零平移/旋转/局部fit，输出PNG/RGBA精确验证。无review板/测试/runtime诊断；生成本身不保证可重放。
