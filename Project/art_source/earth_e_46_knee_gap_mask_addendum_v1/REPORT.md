# 主根遗漏弧缝mask追加提案：复用同一生成patch，无新生图

结论：同一已映射patch在遗漏弧缝位置有连续黑布，足够补齐主要弧缝，不需要再生成。诊断三列为冻结失败／同patch对应内容／仅新增mask的预览。当前研究资产与失败档均未改。

新增域精确为49个HD4像素（约3.06逻辑像素面积），全部在x146–175,y266–271的狭带内；按原alpha<128、排除原已用mask取曲线缺口，另显式排除(175,267)外部透明点。不是把30×6包络全涂满。PROPOSAL.json列出全部逐像素坐标及每行x，ADDITIONAL-GAP-ONLY-PROPOSED-mask.png保存精确mask。

49点与原alpha>=128保护面相交0，与旧补片mask相交0；相同patch这些位置alpha249–253，亲看为匹配黑布，不是银甲或新增装饰。沿同60/1298等比映射，位置不变、不扭曲、不涂色、不重采样对点。预览仅在这49点让同patch置于原半透明边下，其他像素不变。

查看Project/diagnostics/earth_e_46_knee_gap_mask_addendum_v1/：
- failed-samepatch-proposed-{gray,light,dark}.png
- exact-added-pixels-pink.png

原膝偏差与靴长残差不因补缝消失。另记录父级材质观察：46胫甲对照明显偏金黄，共用core黑银红。高光位置/背光银灰支持暖光反射因素，但旧生成胫甲的大面积黄铜色也可能涉及固有材质身份偏移，不能一概称正常暖光或断言全身身份通过。当前不改色域，后续统一材质单独审。

等待父级审49点追加mask，未落到静态候选或普通资产，未新生图/Git/GUI。
