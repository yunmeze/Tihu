# E46/49 minimal layered2D study plan, parts generation pending

User authorized layered2D prototype method. This stage prepares inputs and identity crops only. No new component imagegen, masks that alter art, rig, composited poses, runtime/Git/GUI. Existing full-character failures remain frozen.

## Minimal five unique art items
1. Shared core: same approved E idle9 head, neck, chest, back, compact waist/belt, red shoulder cover. One fixed identity and silhouette for both poses. Needs narrowly scoped imagegen reconstruction where idle near sleeve hides torso. No programmatic painting of hidden torso.
2. Arm46: ONE complete visible upper sleeve + silver forearm guard + wrist/glove, with source low backward/near-neutral hand group.
3. Arm49: ONE complete sleeve/guard/hand variant, source low modest forward pose. Different painted shape, not rotated46 to fake shortening.
4. Lower46: ONE pelvis-to-both-boots pose image, including both thigh/pants/shin/boot chains and their internal occlusion. Keeps long right visible chain and lifted left rear boot.
5. Lower49: ONE pelvis-to-both-boots pose image, different overlap and short tucked right chain, left toe lower.

This uses whole lower pairs deliberately: no knee/ankle joints and no rotation of one shin to invent perspective. It minimizes assembly to upper-arm/shoulder and waist interfaces. No far-hand item for these2 frames: original endpoints are unlocated. A visible far-sleeve remnant, if needed by source silhouette, belongs to the core/lower variant as an explicitly reviewed surface, not a new imagined hand.

A shoulder-cover/waist-front overlay may be CUT BY MASK from the SAME shared-core art, not another designed item. Thus5 unique generated pictures, potentially6 sprite layers after deterministic disjoint masking of core. Any unchanged pixels must be identical in these split copies; no double-alpha overlay.

## Source anchors: logical128 coordinates
Both crowns(39,16), source actor root(16,64), not feet.46 near hand group(37,56),49(43,56), uncertainty±3.
46 left visible kneecloth(32,65),ankle(26,72),toe(31,77); right(43,65),(40,84),(48,87).
49 left(34,66),(26,76),(31,83); right(44,64),(40,75),(48,77).
Ankle/knee proxies±3,toe±2. Right-minus-left toe difference46(+17,+10),49(+17,-6). These denote screen-visible surfaces, not permanent anatomical identities, bones or load-bearing.

Shoulder cloth joining area roughlyx33..40,y29..35; waist joining area roughlyx34..47,y47..53. THESE ARE PRODUCTION ASSUMPTIONS inferred from visible apparel, not source anatomical joints. Source white cloth and new armor may have different material edges. Unknown hidden shoulder/hip geometry is not reconstructed as a skeleton.

## Fixed coordinate/scale contract
Each future component delivered on full128 logical /512HD4 canvas; preserve original root(16,64)/(64,256), shared body size. Source sheets retain full128, no tight-crop normalization.
Approved idle9 identity crown(40,15) can establish common core registration with a single(-1,+1)logical rigid shift toward source46/49 crown. This DOES NOT prove torso/waist matches; verify torso fit before making pieces. Waist-height differences must be addressed as a documented art-interface design choice, not solved by stretching or shifting body around to rescue feet.

Prefer generate all5 items at one declared art scale in one coordinated sheet, then record actual cell bounds. If tool ignores requested scale, allow ONE common raw→HD4 normalization for the entire sheet only, evaluated against shared core. No independent arm/lower resizing, no per-pose shrinking. A malformed item's scale makes that item/set fail; do not repair with local scale.
Both poses use identical core transform. Initially all piece rotations0; changes allowed only explicit2D rigid translations/rotations, never to mimic depth shortening.46→49 is an image replacement of arm and entire lower pair. No mesh deformation, per-frame limbscale or3D.

## Layer and overlap assumptions
Proposed back-to-front: lower-pair -> core-back -> near-arm -> core-front shoulder cover and narrow belt overlay. Core-front split mask must NOT broadly cover the forearm/hand: source low sleeve-to-hand route remains visible.

Shoulder: arm image extends2–3logical px under shoulder cover, concealed overlap only; actual arm outside cover follows source visible route.
Waist: lower-pair contains2–3logical px hidden waistband extension under core belt. Both poses share the same waist attachment band; no requirement to force their toe roots to a common ground line.
These overlap margins are authoring allowances, NOT original data. If source silhouette exposes a gap, fix by authorized imagegen art of that seam area rather than extend pixels with stretching/cloning.
Opaque overlapping pieces do not need crossfade; semi-transparent antialias seams must be inspected at1×/2× on light/dark/gray.

## Permitted proposed postprocess (after parts approval/generation)
- Keep raw unchanged withSHA. Record source rectangle for each piece before crop.
- Pure crop and transparent padding preserve pixel locations; any output offset is explicit. No automatic per-piece centering.
- Separate background using a saved alpha mask only when the intended component boundary is visually verified. Never delete by generic dark/skin/metal color threshold.
- Transparent edge cleanup restricted to a logged band at the isolated part silhouette, maximum1logical px/4HD4 px. Save BEFORE/AFTER and mask, count changed pixels. Do not erode actual silhouette to meet anchors.
- Core-back/front split masks must sum to the original core alpha (no double-alpha darkening). Exact recomposition check before use.
- Seam cleanup may remove residual fringe or select an already-generated overlap region; no programmatic drawing of new anatomy or texture. Missing exposed torso pixels require a separately approved narrow art edit, not painting/fill from code.
- No composition from earlier failed full-body versions. All new art identity derives from approved E idle.

## Required test after separate part-generation authorization
Static46/49 pair, raw-part sheet, masks, before/after crop, source same-scale pair, light/dark/gray alpha, frozen shared core invariance, waist/shoulder contact and full leg+hand phase. Any movement of head/torso between poses is explicit failure. Research assembly only; no ordinary runtime promotion. Runner alone owns GUI if a later Godot diagnostic is approved.

## Actual inspected inputs
source46-left49-right-full128-6x.png: cleaned-by-index source geometry, original shadow semantics still qualified.
approved-E-idle-design-only.png: approved design fragments only.
approved-E-idle9-HD4-full128.png: authoritative common identity/scale, not walk pose.

diagnostics/earth_e_layered_46_49_plan_v1/identity-study-crops.png contains unmodified inspection crops, NOT prepared deployable limbs. Do not send the fullidle as walk-pose authority. Next parent review decides exact component-generation layout and count before tool use; this plan itself is not imagegen permission.
