# Three bounded A13 transition pilots

Status: parent visually accepted radius1 as a working material mask for these three instances on 2026-10-15; native validation remains pending. This is not whole-map terrain approval.

The three *-contract.json files preserve the preceding manual seed/read evidence, including their historical diagnostic-only status. They were not silently rewritten as exact semantic truth. The subsequent decision accepts simplifying small source-noise islands while preserving the visible major grass/earth direction and narrow opening. No larger blur radius is authorized.

Run `python Project/art_source/a13_ground_transition_pilots_v1/export_candidate.py` from the repository root. It reads tracked original map/atlas, the source-inventory, the tracked historical 768 binding/stone package, and immutable v2 grass/soil raws. It derives256 lowpass directly from each whole raw; no ignored diagnostic input is required. Output is assets/scifi/environment/a13_ground_transition_pilots_v1.

34 exact neighboring placements form three isolated test areas. The source mode uses original resources. Base mode uses proven base material/curb mappings within this scope. Pilot mode differs only at -405@28,46, -407@62,36, and +385@76,20. Original source alpha is independently retained, including 32 alpha240 pixels at +385. No collision, placement rectangle, or ordering changes. Outer isolated scope edges are not acceptance targets for full-map continuity.

The local source RGB classifier uses Gaussian radius1 solely to infer grass/earth material weights from manually read seed regions. It does not blur or repaint either material raw. Weight sum is255; final material RGB is the explicit weighted mixture of two world-sampled materials. -407 has no confidently identified bare-earth seed and deliberately remains all-grass, with source ambiguity recorded. Do not generalize these seeds to the other27 transition IDs.

Sensitivity: fragmented raw 0.5 crossings are not reliable road-edge measurements. For separate analysis only, averaging local cross-sections around the manually read macro boundary gives radius0→1 shift at most0.683px (-405) and1.133px (+385). These are mask sensitivity values, not exact source semantic accuracy. The approximate source read lines have ±10px/±7px uncertainty; irregular top/bottom endpoints differ beyond those bands in some sections, and the +385 left edge has no stable half-weight crossing. Preserve those limitations and use actual neighboring visible envelopes for native judgment. No diagnostic profile averaging is applied to the masks.

Native requirements: same-scene source/base/pilot views of each instance, actual reachable short routes where possible, unchanged road width and original alpha, no abrupt local neighbor seam. Unreachable views must be labeled as camera-only. Existing trees/buildings/shadows should remain identical across modes. No default renderer changes are part of this package.
