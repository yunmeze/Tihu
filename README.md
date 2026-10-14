# Tihu · 完整项目测试版

包含 Godot 运行工程、可编辑 Blender 源文件、模型与贴图、导出工具、项目文档及设计参考图。测试文件、截图录屏、缓存、备份和临时文件不包含在本次发布中。

这是 2026-10-13 21:39（UTC+8）的可用源文件阶段，配套当时的代码和资源；并非最终完成版。之后报告过的改动未在当前可用工作区找到，本包不声称包含那些改动。完整文件与校验值见 transport/manifest.json，版本说明见 project/docs/PACKAGE_VERSION.md。

## Windows 运行

1. 下载整个测试分支 ZIP 并解压，或克隆此分支。
2. 双击根目录 prepare.cmd，等待校验及还原成功。它使用 Windows 自带 PowerShell，在本地还原全部文件，不联网下载，也不更改执行策略。
3. 用 Godot 4.6.3 Standard 导入 project/project.godot，等待资源导入，按 F5。运行不需要 Blender。
4. 编辑模型时，用 Blender 4.3.2 打开还原后的 project/source/pelican_coast.blend。重新导出方式见 project/source/ASSET_WORKFLOW.md。

其他平台在仓库根目录运行 python3 prepare.py，再打开 Godot。全部资源以 transport/ 中的小分片保存，必须保留完整并先准备。源代码与文档可直接在 project/ 浏览；准备后，全部资源和 Blender 文件也在此目录。

解包器验证每个分片、完整压缩包和所有文件的 SHA-256，拒绝覆盖修改过的文件。请使用干净目录准备，保留自己改动的备份。Windows 脚本沿用已静态检查的版本，但尚未在真实 Windows 机器执行；需要 .NET Framework 4.7.2 或以上。
