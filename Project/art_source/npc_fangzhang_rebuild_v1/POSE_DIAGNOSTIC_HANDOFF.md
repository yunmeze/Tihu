# A13 two-NPC pose-only handoff

The parent inspected both raws and the static source-coordinate review, and authorized a bounded original-size pose diagnostic. Earlier static review cautions remain evidence, not an automatic rejection of the complete animation. About-one-native-pixel phase differences lie near manual reading uncertainty and must be judged in the full17tick loop.

This handoff does not promote normal-world NPC art. Only the designated runtime owner should create/run the diagnostic. The art worker has not touched Godot, runtime scripts, GUI, R6, NPC interaction, story or shadows.

## Closed entry point

Read `res://art_source/npc_fangzhang_rebuild_v1/npc-pose-diagnostic-set.json`, then each of the two listed `v1-pose-interface.json` files. Each interface identifies its exact raw, atlas, original NPC record, appearance/direction, frame IDs, original metadata, shared registration, timing and file hashes.

Both atlases have native128 × 160 cells with source cell draw origin `(32,104)`. The candidate destination is:

```text
position = npc_world_cell_origin + Vector2(-32,-104)
size = Vector2(128,160)
atlas_region = interface.frames[str(source_id)].rect
```

Do **not** add native source offset or atlas crop again to the candidate; those coordinates were used when constructing its fixed canvas. They remain in the manifest as evidence. Use the normal source manifest offset+crop only for the original-side comparison. This avoids both double motion and per-frame top/bottom recentering.

- 方丈: atlas128 × 160. Source IDs261,262,263,264 all reference the same rect `[0,0,128,160]` and same RGBA. One static pose, unchanged17tick source indexing.
- 凌云子: atlas512 × 160. Source IDs113,114,115,116 map to four sequential128px cells. All four use the exact same scale and XY translation fitted from source113's manually read visible material landmarks. No per-frame adjustment or scaling was introduced.
- Candidate texture filter: linear. Original source comparison: nearest. Both are native world-pixel dimensions; default comparison scale1. An enlarged aid may be separate but must not replace native judgment.

## Exact timing and display

Use one shared50Hz simulation clock for both subjects and their originals:

```text
phase = floor(tick / 17) % 4
source_id = first_source_id + phase
```

Loop68ticks = 1.36seconds, order0,1,2,3. Show at least two complete cycles including3→0. A manual freeze/phase advance can help inspect original113–116 and the four new cells, but is not a loop pass. Preserve any pause/resume semantics of the diagnostic explicitly rather than altering the clip cadence.

The first diagnostic should be a simple source-versus-new pose comparison on neutral ground/background. Do not install a world override or add new ground shadows. Original checker stays on the original comparison only; the generated side contains body alpha only. Do not modify clicks, names, map positions, original NPC visibility/scripts or R6.

## What to look for

方丈: original bent-leg/arm relationship and the two visible boot placements; no new breathing despite advancing four source indices. Strong raw contour is not visibly hard-clipped. Parent measured only8 top-edge pixels with alpha>32, none above128; left edge has none above16, and other borders have none. Low-alpha contact is preserved. Candidate canvas adds transparent margin by registration, not raw repaint.

凌云子: inspect the whole small loop, especially114→115→116→113 crown height, robe/hand motion and nearly fixed generated foot line. The fixed first-phase fit recorded roughly0,2.35,3.24,0.11 top changes versus source0,2,2,1, and generated bottoms0,0,0,0 versus source0,1,1,0. Those observations must stay visible; do not align feet or hats individually to make the numbers disappear. Also judge whether gold embroidery and tassel detail read too busy at native size. No large-image-only rejection or automatic acceptance.

## Review evidence and reproduction

Run `python Project/art_source/npc_fangzhang_rebuild_v1/prepare_pose_diagnostic.py` from repository root. It verifies immutable raw hashes, reuses the recorded common transform, builds only candidate atlases/interfaces, validates all four index mappings and clock boundaries, and writes neutral source/new all-four boards:

- `Project/diagnostics/a13-npc/pose-interface-v1/fangzhang-four-native-source-v1-1x.png`
- `Project/diagnostics/a13-npc/pose-interface-v1/lingyunzi-four-native-source-v1-1x.png`
- Matching3× aids in the same directory

Technical validation is not engine verification. `pose-interface-validation.json` explicitly leaves `runtime_loop_viewed:false`. Return native screenshots/loop observations and any blocker to the parent before further promotion, motion correction, new generation, or shadow work.
