# S59回源重画：单次失败保全

本次是独立的完整回源重画，不覆盖早期S59/六相/手臂编辑记录。只有一次生成，实际两参考及顺序见ARCHIVE.json，原字节依赖已tracked旧包的两张实际输入图，避免复制。prompt文件虽然历史名称为DRAFT，但作者确认它是REQUEST_FROZEN中的实际调用文本。

上肢手部L−R约+3、足端约+7.45，而原59足端L−R约−5，形成混合相位；六原相均不匹配，不将结果改认62或60。表面读取不确定性保留在AUDIT/RESULT；这些坐标不是关节或地面接触真值。未runtime、未局部回贴、未清alpha、未重复生成。

重放：python reproduce.py --project /path/to/Project --out /path/to/new-output
需Python/Pillow。验证实际ref原字节pins，并从tracked source59完整128窗nearest4x和approved idle17首格核RGBA。raw1254整方RGBA直接LANCZOS512，零位移/旋转/局部fit，精确PNG与RGBA输出校验。生成本身不可确定性复现。review板、测试和旧诊断脚本不进入包。
