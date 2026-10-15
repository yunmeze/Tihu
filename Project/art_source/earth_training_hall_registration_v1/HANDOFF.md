# Earth训练馆30-owner候选注册

入口：`res://art_source/earth_training_hall_registration_v1/registration.json`。

状态：父已审整体结构/材质和可见局部接缝，批准独立Earth入口联合审。不是最终原生验收，不启用外部地影。

## 静态冻结结果

- 原30个Building owner，12 support/layer0与18 upper/layer1；key、cell、source_cell、flag、layer、sort_y、stable_source_order、frame_index逐字段不变。
- 28张有效纹理；upper3966、3978无候选像素，保留空owner记录并抑制对应原画。不得删key、补草裙或为凑非空编造画面。
- 唯一整图scale=0.4841293148972399；world top-left=[3007.409332733406,731.1423528112169]。来自此前冻结参考，局部编辑后没有重新拟合。
- 889,932个非零RGBA像素各分配一次；889,274个可见alpha像素。0重叠、0遗漏，完整RGBA重组逐字节等价（包含658个透明但RGB非零像素）。
- 14个明确原支撑脚点全部落layer0；侧颊、结构主脚和墙为upper。右草地边代理点仍为±2 source px读数预算内的不确定，不称完全透明。

## 运行方接口

保留旧30-owner注册接口：`texture/raw_rect/world_top_left/scale`，含完整 `suppress_source_keys`。运行应在原有owner顺序中替换每项，空owner也抑制原画，不得以整楼单sprite盖住角色。

当前Earth严格asset_guard另要求assets路径、pack、texture_size、texture_sha256且不接受空texture；本文件不能原样喂给该guard。运行方需独立适配/打包到其候选接口，或延用分组注册读取。空owner身份仍须原子保留，纹理为空不是丢失资源错误。禁止静默回退半栋、改变flags/事件或更改排序。

第一次静态/原生parity使用nearest、关闭mipmaps。各透明切片若独立linear采样会在共享边缘变暗；未验证前不得擅自改filter。比较无角色的整图与30-owner重组同屏同采样后，才检查角色/NPC的实际阶前、阶中、门槛与主脚邻域遮挡。

## 复现与限制

仓库根执行：

1. `python Project/art_source/earth_training_hall_local_assembly_review_v1/build_review.py`
2. `python Project/art_source/earth_training_hall_registration_v1/build_registration.py`
3. `python Project/art_source/earth_training_hall_registration_v1/verify_registration.py`

`validation.json` 是独立切片反向重组及世界采样网格检查。`support-material-review.png` 是材料mask人审图，不是资产。mask来自可见连续踏面/窄立面，未拿目标四边形或脚点直接填图。旧原12支撑矩形不是自动地面mask；同层原alpha provenance/最近延展只提出深度归属，不能代替原生遮挡验收。

可见残差：左上口细线、原主脚压新颊的小接触拐口，父已同意带入候选联合审；右阶原草地边读数不确定。登记栅格比例约2.0656 texels/logical unit，但这不是最终细节质量与相机/支撑配准验收。尚未实测原生行走、角色脚底排序、平台地影接收。
