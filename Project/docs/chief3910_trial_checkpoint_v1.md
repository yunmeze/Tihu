# A00 村长屋3910单片试验

这是从已发布v10和归档原raw重新构建的独立静态候选，本次恢复环境尚未完成运行验证。旧会话结果不作为这次候选的运行验收。

用Godot打开Project/project.godot，再打开res://scenes/earth_overall_chief3910_trial_v1.tscn，按F6运行当前场景。F5和原v10入口保持不变。

只恢复3910@(82,55)原完整canvas内已有raw的真实alpha：7,884个alpha值改变，其中7,296个跨过127阈值。RGB、其余49片、全部NPC/hero、原层次/排序/位置及v9 clip_uv保持不变。

3909仍未恢复，整屋外轮廓、地标偏差和动态遮挡仍未完成。这不是第一关验收，也不是新检出、Windows或导出验证通过声明。
