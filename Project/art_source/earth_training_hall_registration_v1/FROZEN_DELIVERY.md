# 冻结交付补充（不修改85项源归档）

父已确认最终材质分层和普通assets复制。生产候选入口：`res://assets/earth/environment/training_hall_v1/registration.json`。

- 源注册SHA：0b086e70162f6f79de76f311b662c7b66bb54ee6a3b4d7cf9a9cd806459a4c6c
- 普通包注册SHA：57072cc60ed9e33aa9afaeb0c7310733216e2884e0b042b043077551473e273c
- 完整透明合成SHA：be82bef2c8d7aa9e26675e69dc076acbca76f0878eaf78eee3a18e501a12464b
- 源85项精确清单：`../earth_training_hall_local_stair_plan_v1/COMPLETE_ARCHIVE_FILES.json`，清单自身SHA 20969c43159f33c72ab55fd02c270e53c54a236d97242137781c59de98429b87

85项已冻结，后续这份说明、独审报告和生产闭包都以新增文件保存，没有改冻结项。

普通包含28张原SHA owner纹理、1张完整parity图和30身份注册。3966/3978为空upper，显式empty与身份hash绑定，仍须抑源。`whole-review.png`仅作等价性诊断，正常渲染不能用整栋单sprite盖角色。生产闭包精确文件/hash在普通包`PACKAGE_FILES.json`；打包可用本目录`package_candidate.py`重放，脚本固定检查已批准源注册SHA后逐字节复制。

独审最终结论在`FINAL_INDEPENDENT_REVIEW.json`。原生接入已交独立Earth运行负责人，当前静态通过不冒充原生行走、遮挡、接地/平台阴影通过。本文及生产闭包没有修改flags、事件、source owner身份或层序。
