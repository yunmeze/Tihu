# Independent grass/soil material v1 — provisional rejection

Each material was generated exactly once from the approved assembled-context style reference. Both immutable raw images are 1254×1254. No RGB correction, offset blending, edge painting or extra generation was performed.

## Result
The shared-world sampling approach removes the 96×64 per-ID repetition and four old-soil fallback patches from the original 143-placement diagnostic. It does not make these particular raw materials seamless. Independent repeated-material boards reveal recurring grass dark bands and a visible vertical soil boundary. At a world period of 768, edge jump minus adjacent internal gradient is grass V/H 8.93/5.37 and soil 7.14/3.54 RGB levels. A 512-period numerical improvement is confounded by resampling and is not seamlessness acceptance. At 768 and 1024 the grass details are also too conspicuous and gravel grains too large compared with the source game scale.

No runtime/default promotion. Keep both raw files as research; further image generation/editing requires a new decision.

## Offline assembly boundary
The 20-placement and 143-placement diagnostics use explicit 512/768/1024 world periods with a shared world origin and uniform texture sampling. They preserve original placement rectangles and source IDs. Source road geometry is traced from the original visible curb centerline with ±3 source-pixel manual uncertainty. An 11-pixel technical ribbon retains pixels of the already generated narrow curb under its frozen uniform registration; it is not newly drawn stone art. This ribbon can carry old candidate soil/grass fringes and needs closer semantic validation before production. The generated curb centerline differs slightly from the source centerline; the existing manual RMS measurement is not a guarantee of exact road-width preservation. No native runtime tests have been made.

The two absent context IDs (-594 and -586) have identical original pure-soil pixels and are represented by the same shared soil material only in the new diagnostic. Grass aliases -406/-399 share a common grass field. All 20 and 143 placement masks cover their tested complete-tile context exactly once, with no uncovered or duplicate pixels. This is coverage, not aesthetic acceptance.

## Reproduce and inspect
Ignored diagnostic paths:
- Project/diagnostics/art_source/a13-ground/materials-v1-tiling/audit.py and report.json: repeated-material measurements and boards.
- Project/diagnostics/art_source/a13-ground/world-material-v1/assemble.py and report.json: semantic-mask composition and all three world-period rasters.
- world-material-v1/period-comparison-context.jpg: native-scale density comparison.
- world-material-v1/first143-comparison.jpg: source versus shared-material assembly at period768.

Original assets, map fields, source RGB and generated raw files remain unchanged. These tests do not claim that a large image stretched over the map is acceptable; the explicit material periods are independent of map size.
