# Temple v2 support registration: optional technical candidate

## Frozen input and whole-building registration
- Raw: `res://art_source/a13_main_temple_candidate_v2/raw.png`, SHA256 `3bf1876fd6b76831216668a645f4120dcbc737cfa2ba258e0fc3d2fee705c3e1`.
- Registration: `res://art_source/a13_main_temple_support_registration/technical_v1/registration.json`.
- Every raw pixel uses the same scale **0.533687668884736** and raw-canvas world origin **[2979.8431118835334,665.2144416536716]**. No rotation, shear or independent roof adjustment.
- Each cutout's `world_top_left` already includes raw crop compensation. Draw the complete PNG there at `scale`; do not add source crop/offset again.
- Apply the original `layer`, `sort_y`, `stable_source_order` for each source key. Suppress all 30 original keys, including empty entries. Leave all other map objects, NPCs, flags and movement unchanged.
- Nearest filtering/no mipmaps is required for this diagnostic. Separate linear-filtered cutouts may darken their shared mask boundaries; any later linear method needs its own parity gate.

## Pixel/depth partition
25 PNG cutouts and 5 explicit empty owners. All 867,910 pixels with alpha>0 are assigned exactly once. 998 alpha=0 pixels carrying nonzero RGB are also preserved. Independent inverse reassembly is byte-identical to the full raw RGBA, including partial alpha. No painted pixels, geometry warp, alpha threshold or old baked shadow is introduced.

The new visible landing/tread interiors are manually traced, with 3–6 raw-pixel boundary uncertainty; only those top pixels enter layer0. Rails, stair cheeks, risers, walls and uncertain border pixels remain layer1. Original layer-specific alpha ownership supplies the source key, with nearest same-layer provenance where the new silhouette extends beyond old visible pixels. This is an explicit depth inference, not a claim that old rectangles define new faces. Source x/y/layer/flags are exact. Raster crops may extend the original source rectangles.

Empty source owners: 3979/3985/3989 correspond to removed apron in the mapped lower support region; 3966/3978 are no longer hit by the tighter generated outer roof/body outline. They remain suppressed; no replacement pixels are invented.

## Per-cell support interpretation (stationary original South phase17)
Actual boot samples are original body local [10,64]/[24,69], with source offset [7,-47], hence actor-origin-relative [17,17]/[31,22], each ±2 px. Actor draw origin is not a boot point. These readings do not prove every moving phase.

- 66,34 and 66,35: upper/middle stair top.
- 73,35 and 73,36 and 74,36: right landing/upper/middle tread.
- 65,35 and 66,36 and 74,37: real tread/outer-edge boundary; prioritize native checks.
- 65,36 and 66,37 and 75,37 and 74,38: source grass/apron or mixed outer ground. New transparency reveals map ground; it is not automatically a missing support face.

## Requested sole-runtime sequence
1. Preflight all cutout hashes/imports and exact 30 source keys; use an isolated optional loader. Default world unchanged.
2. Fixed camera/actor hidden: full raw vs partitioned raw, same nearest filter and scale/origin. Exclude labels and compare scene pixels. Static byte parity alone does not prove Godot filtering parity.
3. Source vs candidate at left upper/middle/edge cells 66,34; 66,35; 65,35; 66,36. Right 73,35; 73,36; 74,36; 74,37. Use same phase17 and original sorting. Verify actual boots/rails/door thresholds, not only draw origin.
4. Original A* from61,39 to reachable stair targets, with original flags/NPC obstacles. Any dynamic obstruction/rejection must be retained, not bypassed. Static source BFS reached the 12 support-owner cells, but this is not native route proof.
5. Retain source fallback, original NPCs and normal depth. Do not add shadow yet; candidate generation has no ground cast. Report roof proportions, tight bottom padding and front stair/cheek design differences rather than hiding them.

## Reproduction
`python Project/art_source/a13_main_temple_support_registration/build_technical_partition.py`
`python Project/art_source/a13_main_temple_support_registration/verify_technical_partition.py`

Independent report: ignored `Project/diagnostics/art_source/a13-main-temple/technical-v1-validation.json`.
Top-mask board: ignored `v2-layer0-top-interiors.jpg` in that directory.

This is a candidate for native depth tests, not accepted production registration. Parent approved this technical route after inspecting source/v2 support-foot boards; earlier raw REVIEW records the earlier all-landmark gate and remains unchanged.

## Decision timeline (UTC, 2026-10-15)
- v2 raw research REVIEW was written before a 30-owner partition existed, while all-landmark/common registration was not accepted. It is preserved as historical research evidence.
- By04:36 the parent had inspected support-fit boot boards and authorized one whole-building support registration plus technical face/depth partition. Roof differences remain design residuals.
- 04:41 independent inverse RGBA/owner/UV validation passed for technical_v1. Native filtering and walking/depth remain pending. This later technical package does not retroactively turn the raw research gate into a native acceptance.
