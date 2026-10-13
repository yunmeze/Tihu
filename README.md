# Tihu 本地测试版（运行工程）

这是开发中的阶段测试版，方便先在本地检查操作与运行。画面仍在继续调整，不代表最终完成质量。

## Windows 启动

1. 下载整个仓库（Code → Download ZIP 并解压，或 git clone）。
2. 双击根目录 `prepare.cmd`，等待显示校验和还原成功。它使用 Windows 自带 PowerShell，在本地还原模型和贴图，不会下载文件或更改执行策略。
3. 安装并打开 **Godot 4.6.3 Standard**，选择 Import，打开 **project/project.godot**。
4. 等待首次资源导入，按 **F5** 运行。运行时不需要 Blender。

这里先提供完整可运行的 Godot 工程。Blender 编辑源文件、录屏和参考图会在完整源码版本中补上。`transport/` 中是为传输拆分的资源压缩包，必须先运行 prepare，再打开 Godot。请保留全部分片。

其他平台可在仓库根目录运行 `python3 prepare.py`。解包器会校验每个分片、完整压缩包和所有还原文件的 SHA-256，并拒绝覆盖已修改的工程文件。修改过的文件请先备份，再在干净目录重新准备。

验证：原始工程通过 Godot 4.6.3 干净导入及 16 项检查；最小运行内容通过干净导入和无头启动。Windows 启动脚本已静态检查，但尚未在真实 Windows 机器执行。Windows PowerShell 需要 .NET Framework 4.7.2 或以上。

## 说明与路径

本仓库根目录的 README.md 是当前仅含运行工程的阶段测试包的权威启动说明，请以本页的准备与运行步骤为准。

`project/` 内附带说明沿用完整源码版，其中 `source/`、`tests/`、`tools/`、录屏、参考图和部分文档将在完整源码版提供，当前运行包不包含这些内容。内部旧说明中的仓库根路径实际对应当前的 `project/` 子目录。命令行启动时，请在本仓库根目录使用 `godot --path project`，或先进入 `project` 目录再运行 `godot --path .`；首次启动前仍须先运行根目录的准备脚本。
