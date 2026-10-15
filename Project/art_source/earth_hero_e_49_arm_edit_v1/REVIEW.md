# Single49 local near-arm edit: failed preservation

One explicitly authorized built-in image edit using only raw49 as edit base plus original full49 and original sleeve-region evidence. No further generation, no animation assembly, no runtime/Git/GUI action.

Raw: raw.png,1254×1254, SHA1d03b523e7961ef211cb68e82cd576f7d4bc1b8e64b31f87e7012b6dfce9a33a.
Exact inputSHA and actual prompt saved before call in request.json / prompt.txt.

## Original registration preserved
measure.py reuses the prior scale0.1028549998260168 and translation(-1.4220149316246022,-0.25108997251065546) WITHOUT fitting output. fixed-registration-HD4-CONTROL-ONLY.png is only an inspection candidate.

The canvas stayed1254×1254, but the subject did not: alpha128 bbox changed[230,158,510,826] to[183,166,552,1024]. Height668→858,+28.4%; width280→369,+31.8%. Head, torso, hip armor, legs and boots were resynthesized outside the permitted arm area. Protected visible-union pixels outside[330,365,485,580]:129918;125920 (96.92%) differ by>8 in max premultiplied RGBA. This ignores hidden RGB and includes silhouette additions/removals. Pixel changes alone are not proof of geometric deformation; bbox and fixed-register comparison independently demonstrate subject enlargement.

## Arm and leg joint review
Arm qualitatively changes in the intended direction: descending forearm guard and low forward hand, not the high horizontal fist of walkv3. However the whole-body enlargement invalidates a claim of a successful isolated edit. Fixed-transform hand group is approximately(51.14,64.44), source approximately(43,56), not the requested small shift in the prior coordinate frame. Values are surface regions with raw±8px/source±3px uncertainty, not anatomical joint positions.

Original favorable49 leg chain cannot be called preserved. Same-transform toes are about(28.20,102.30)/(51.55,96.95), versus original study roughly(30.05,82.24)/(47.85,77.82). Knee/shin armor and boot silhouettes visibly changed. Do not rescale the edited character back and quietly call it accepted. No original legs have been pasted over it.

## Diagnostics
Project/diagnostics/earth_hero_e_49_arm_edit_v1/source-base-edit-fixed-true-1x.png
Project/diagnostics/earth_hero_e_49_arm_edit_v1/source-base-edit-fixed-true-2x.png
Project/diagnostics/earth_hero_e_49_arm_edit_v1/base-edit-raw-same-canvas.png
Project/diagnostics/earth_hero_e_49_arm_edit_v1/protected-pixel-change-map.png

## Additional permitted explanation
GLOBAL_DRIFT_EXPLANATION.json and explain_global_drift.py evaluate ONE whole-image silhouette similarity transform. This is solely to distinguish predominantly global enlargement from extra local distortion, not a revised candidate registration or pass. No individual limb fit or pointwise warp. See GLOBAL_DRIFT_REVIEW.md for interpretation.

Stop after this attempt. Local preservation has not been established by the built-in edit. No automatic repeat of the same edit method.
