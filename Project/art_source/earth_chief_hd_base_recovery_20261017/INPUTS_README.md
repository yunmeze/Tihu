# 村长生成参考输入精确恢复 V2

本包恢复的是两张历史生成输入，文件 SHA256 均与已保存工具来源记录完全一致，不是仅 RGBA 一样的重新编码近似件。

- `inputs/frame-125.png`：68×70 RGBA，SHA256 `701aab9ce8fda25b0dd10b479a5f8f2553552687a3b4a9b9f68e635056343aa0`
- `inputs/earth-hero-S-idle-phase17.png`：512×512 RGBA，SHA256 `6371d05af2239971836cfe30846e0d84b086e7020af69a6c9b2ad44a9e155f92`

第一张由原版 `Npc.lpRes` record 125 按现存解码器重提取，完整保留身体与右侧棋盘影；offset 仍单列为 `(-1,-47)`。第二张是 Earth S idle 已保存 atlas 的首个 512×512 精确裁片，对应源 17，仅为材质/光照参考。

`SOURCE_INPUT_PINS.json` 保存源依赖的 SHA256、Git blob、冻结提交、RGBA 哈希及旧工具路径到可移植输入文件的映射。`INPUT_CLOSURE_ADDENDUM.json` 将这些精确输入与现有两次生成的实际 prompt/args 和 raw 对应。`ARCHIVE_ALLOWLIST.json` 是本包唯一发布清单；没有把临时验证或四相研究混入这次输入闭包。

现有 `earth_chief_hd_base_recovery_20261017/raw/v1.png` 与 `raw/v2.png` 都是 NOT_ACCEPTED。输入闭包补齐只修复可追溯性，不给任一图姿态/美术批准，不代表可以启动四相 warp。旧未上传 accepted 村长图仍未找回。

复现：

`PYTHONDONTWRITEBYTECODE=1 python tools/recover_exact_inputs.py --repo /absolute/path/to/tihu-legend-recovered --out /absolute/path/outside-repo`

脚本先验证全部源 pin，再在独立输出目录写这两张图，并分别核对文件字节 SHA 与 RGBA SHA。输出路径位于源仓内会被拒绝。此任务没有运行 Godot、生图、写主仓或推送 Git。
