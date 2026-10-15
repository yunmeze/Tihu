# Earth ground v4: clean-source bounded sample candidate

One authorized built-in imagegen generation produced `raw.png`, unchanged **1536×1024 RGB**, true2 texels/logical for world`[2496,960,3264,1472]`. SHA256:`a44d861c4485cb8596fb42681441675d1b9cefb3d8c48261113325c14492ae2f`.

Unlike the prior grass edits, only three inputs were submitted: the original clean source semantic layout, the same layout with one real-sized runtime actor as a ruler, and a concept-only fine-grass/material/scale board. No v2/v3 generated grass or full scene was an imagegen input. Whole pavement material regeneration was explicitly allowed. The returned ground contains no person or person shadow.

Large curled leafy clumps and deep tuft-pits are substantially replaced by fine, short grass/granular ground texture and broad flat variation. The parent reviewed the actual same-camera joint2× scene and approved v4 as the **current independent Earth sample candidate**, not global final-art approval. Warm/yellow highlights remain for later shared-light/hall review; no independent color reroll is authorized.

## Original geometry and finite precision

The original64 floor owner identities/cells/four-field source records/order/alpha remain. Six manually read source curb centers were independently checked. The largest difference is approximately3.041 logical pixels at the top-right cap center, source`(960,582)` versus candidate`(959,576)` in actual2× pixels. Original source read uncertainty is±3 logical; current read uncertainty is±3 actual pixels, or±1.5 logical. The parent accepted this boundary-precision caveat for the bounded sample. It does not prove exact outer-curb width/alignment or a hard excess. No warp or geometric correction was made.

The capped diagonal path, bottom opening and about186-logical-pixel grass interval before the left stairs remain. No new connecting road, stair, planter or obstacle was added. Slab texture/joints and small flush drain details were fully repainted as authorized.

## Direct64-owner export

`export_candidate.py` cuts each original owner directly from the immutable raw at integer coordinates. Each output is192×128 RGBA, logical96×64, scale0.5. Source alpha is exactly nearest-expanded2× and verified255 throughout this sample. The64 images reconstruct the full raw's RGBA pixels exactly, every pixel has exactly one owner, and original map/manifest hashes match. No earlier generated pavement or grass is mixed in.

Production candidate files are under`assets/earth/environment/ground_plate_v4/`:
- `registration.json`: complete atomic64-owner scope, same guard interface as v2.
- `tile-{x}-{y}.png`:64 direct cuts.
- `plate.png`: byte-identical optional shared copy of raw; initial nearest split sampling does not depend on it.

The oldv2 resources are untouched. Only the designated runtime owner switches the independent Earth default to v4 and retains P original-source fallback, atomic whole-group failure behavior and original A* routes. `export-review.json` proves the offline reconstruction; `runtime-handoff-report.json` records the separately verified native/guard/path outcome when available. Neither this recipe nor this worker runs Godot or an original executable.

## Reproduction and minimal archive

- `prompt.txt`: exact submitted prompt, no draft marker.
- `generation.json`: exact three input paths/hashes and original tool output path.
- `review_candidate.py` / `review.json`: dimensions, recorded six-point audit, material observations and native joint-review evidence hashes. Display-luma neighbor statistics are descriptive only: v4's finer bright grain has a larger neighbor-difference proxy, so these numbers cannot establish visual calmness or blade scale.
- `export_candidate.py` / `export-review.json`: deterministic source-identity/alpha/direct-crop/reconstruction recipe and result.
- `make_archive_manifest.py`: explicit minimal source/production closure. Required prepared semantic/actor/material reference PNGs are source assets and included.
- `archive-manifest.json` / `ARCHIVE_FILES.txt`: final explicit file allowlist.

Runtime screenshots/logs remain local in`/workspace/shared/earth-ground-v4/` and any later runtime check directory. They are **excluded** from the archive, as are test scripts, temporary marked-up diagnostics, Godot imports/caches and redundant concept crops. Reports retain their hashes and conclusions only. No automatic additional generation or broad scene rollout is authorized.
