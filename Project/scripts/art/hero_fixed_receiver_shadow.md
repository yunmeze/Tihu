# Fixed receiver extension: SE idle + walk joint preview

Status: the joint SE preview was accepted with actual receiver y86.0 after native
flat-ground movement and depth review. This is a working visual approximation,
not a physical-ground calibration. The default source entry remains unchanged.
The existing R5 standalone idle viewer and its two-sole projection remain the
historical comparison. The new joint preview may use one fixed receiver for all
idle 13–16 and walk 51–56 frames, avoiding a projection change at start/stop.

## Explicit API

```
configure_ground_frame(body_atlas: Texture2D, region: Rect2i,
    body_to_parent: Transform2D, ground_reference: Vector2,
    ground_slope: float, cast_per_height: Vector2,
    opacity = 0.30, blur_px = 0.9,
    tint = Color(0.035, 0.045, 0.055)) -> bool
```

`ground_reference` and `ground_slope` define the fixed image-coordinate receiver
line g(x)=reference.y+slope*(x-reference.x). Neither is a boot, joint or contact
detector. Keep them constant over all phases, including idle transitions. Switch
only the explicit atlas region and exact body-to-parent transform. The actor root
remains cell point (16,64); native body origin is actor origin minus (16,64).
Alpha, scale, registration, phase duration, body sampling and body shape remain
unchanged. No helper code loads source images or measures feet at runtime.

The shader is byte-identical to the accepted idle pilot. It computes the same
affine alpha projection, one normalized 3x3 blur, one opacity-capped compositing
pass, and explicit frame-boundary/LOD guards. Original `configure_frame()` retains
its historical two-sole affine result. Fixed mode records `ground_reference` and
`ground_slope`, and never reports fictitious `sole_a` / `sole_b` parameters.

Render order and atomic replacement requirements remain floors → one shadow →
normally depth-sorted objects and replacement body. Never combine this shadow with
the source checker-bearing body. Failure clears the current shadow. The original
body+head fallback remains the caller's atomic decision.

## Source evidence and model choice

The original six RGBA frames are in `art_source/hero_se_walk_source_r5`, with the
root and visible-clothing measurements in `SE_WALK_SOURCE_ANALYSIS.json`. Source
checker pixels in the visually exposed ROI x≥64 are all (16,8,8,255), with counts
127/120/146/151/131/123. Their inclusive pixel-index bounding boxes by 51–56 are:

- (64,59)..(82,79)
- (64,58)..(81,76)
- (64,58)..(82,81)
- (64,57)..(82,81)
- (64,57)..(81,78)
- (64,58)..(81,78)

This supports a stable right/up cast, not a unique receiver slope or physical
plane. The candidate retains the independently measured source 13 cast vector
(148/279,−111/279), approximately (+0.530466,−0.397849). The ROI measurement is
read-only evidence; source RGB colors are never globally removed or classified.

Using the idle negative-slope foot line for walking puts some forward boots well
below that line. Refitting a line through every pair of visible boots would instead
force every swinging boot onto the receiver, invent hidden contact in 52 and cause
phase-dependent shadow transforms. The candidate therefore uses a fixed horizontal
line, slope 0. It is a stable 2D rendering approximation, not a recovered physical
ground plane. Visible y offsets mix ground depth and elevation; the model cannot
separate those from a single source sprite.

The selected joint-preview reference is (40,86), slope 0, giving actor-relative
reference (24,22). It is used unchanged through all ten idle/walk phases in
`scripts/art_preview.gd`. Native comparisons used y86 and y87.5; 86 was selected for
its observed contact appearance and stable movement, not because it is the exact
minimax value 86.5. No further subpixel sweep was required.

Native evidence includes the all-ten-phase comparison, an actual two-cell SE route
lasting 64 ticks through 56→51 and back to idle, and front/back tree probes. Evidence
is retained in `/workspace/shared/legend-rebuild-r5/walk-ground-long-route.jpg` and
`walk-cold-combined.log`; the production preview is documented in
`docs/SE_IDLE_WALK_ART_PREVIEW.md`. The small 51 foot/shadow interval remains an
acknowledged 2D approximation boundary, not a reason to move or deform the body.

## Pixel convention and bounded visible error

All outsole proxies below are geometric pixel edges. A last opaque row index 91
has lower edge y92. Pixel center x is x-index+0.5. Alpha≥96 is solely a reproducible
measurement threshold; the shader uses full continuous alpha without alteration.

The current v3 walk lower-visible-outsole proxies by 51–56 are:

- 51: (50.5,92)
- 52: (42.5,90)
- 53: (38.5,87)
- 54: (57.5,89)
- 55: (49.5,85)
- 56: (43.5,90)

These are visible contour proxies with approximately ±1 px uncertainty, not proof
of support or weight bearing. The second boot is hidden in 52. Both visible boots
in 53 have close y values, but that does not prove two planted contacts. The raised/
rear short boot in 51 remains displaced by projection; it is never pinned to the
receiver by its current pixel coordinates.

The walk lower-visible-edge envelope y85..92 alone has midpoint 88.5. This is a
different objective from the combined idle/walk comparison below; 88.5 is not the
selected joint-preview receiver. At y87.5, maximum lower-visible-walk-boot shadow
displacement is about 3.61 px.
New idle near/far outsole edges are y89/y81; the same fixed line displaces their
shadow samples by about 1.20/5.22 px. The far idle foot may simply occupy another
ground depth, so its receiver-relative difference is not a claim of a raised leg.
Across the idle two-foot edges plus the lower-visible walking edges, y81..92 has
midpoint 86.5 and a minimax sample displacement of about 4.41 px. This is only a
comparison aid; native contact appearance, smooth starts/stops and no double shadow
matter more than minimizing a single proxy statistic. Do not change body position
to hide these known 2D projection residuals.

## Source contract

Independent measurements and all per-foot/threshold details are recorded in
`art_source/hero_se_walk_rebuild_v1/fixed-receiver-source-contract.json` and its
`FIXED_RECEIVER_SOURCE_CONTRACT.md`. The source test recalculates these values.
Those research paths are not runtime dependencies.

## Immutable assets and tests

Walk raw SHA256: `66248cb3176c0c076572160325961dfbcd07116618b2533390c4614238660ab9`.
Walk atlas SHA256: `7c386900fe579018ef38cf00c7e160622abebef476f3ccebd9c6fd94923bcf38`.
Atlas is 768×128, six 128×128 regions in source order51–56. Root=(16,64), scale 1,
seven physics ticks per phase. The caller supplies an importable atlas path; no
runtime helper path is coupled to ignored diagnostics or `art_source`.

Run headless with a writable HOME/XDG_DATA_HOME as described in the idle contract:

- `tests/test_hero_alpha_ground_shadow.gd`: historical idle regression
- `tests/test_hero_fixed_receiver_shadow.gd`: constant projection across repeated
  idle→walk cycles, actor translation, preserved elevated-boot displacement,
  explicit-region guards, parameter bounds and historical-API equivalence
- `tests/test_hero_alpha_ground_shadow_source.py`: immutable idle/source evidence
- `tests/test_hero_fixed_receiver_shadow_source.py`: immutable walk/source/shader
  hashes, exposed checker evidence and row-index versus lower-edge convention

The runtime owner completed GPU rendering, all ten native-size phases, a 64-tick
actual flat-ground route including 56→51, starting/stopping, same-phase off/on and
real front/back object checks for the selected y86 preview. This does not extend
to stairs, platforms, elevation, geometric receivers, arbitrary directions,
original EXE movement equivalence or full walking physics. Future changes must
recheck high-screen idle-foot appearance and 51/55 lower-boot residuals.
