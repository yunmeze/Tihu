# Ground v3: scale-edit research, rejected replacement

One authorized built-in imagegen call produced `raw.png`, unchanged **1536×1024 RGB**, at true2 texels per logical unit for world`[2496,960,3264,1472]`. SHA256:`230071981a79e850b8b0dd99aa0c4fa8e69408770cde2620aa451bc609be87d3`.

The edit used the empty v2 plate plus a same-frame true-size actor reference, concept material/scale references and an advisory pavement protection guide. It contains no person or person shadow. However, it still reads as dense curly/wiry grass and identifiable leafy clusters. Some dark hollows are reduced, but short-cut lawn scale was not achieved. The parent inspected the raw and rejected replacing production v2.

Pavement was also re-rendered:211705 road-core pixels were measured;210900 changed (99.62%), mean absolute RGB difference5.64/255. This is disclosed as a non-target change, separately from geometric judgment. The six original source center reads remain within approximately2.5 logical pixels at maximum, inside the original±3 logical manual-read budget. Capped shape, bottom opening and about186-logical-pixel grass interval remain; exact outer-edge/curb width is not established.

The display-luma neighbor-difference proxy increases from14.04(v2) to16.48(v3), despite reduced dark-clump volume. It is only a descriptive statistic, not perceptual acceptance. Actual1×/2× scene-scale evidence confirms the busy grass remains.

## Evidence and boundary

- `prompt.txt` is the actual submitted prompt; `generation.json` records references, output path, dimensions and hashes.
- `review_candidate.py` reproduces the pixel metrics and recorded manual source-center audit without changing either raw.
- `evidence/v2-1x.png`, `v3-1x.png`, `v2-2x.png`, `v3-2x.png` are real Godot captures by the designated runtime owner, same camera, actorcell61,39 and SEframe13. No screenshot substitute or image-generation mockup.
- `evidence/native.log` confirms the comparison and unchanged production v2. The diagnostic renderer used the original64 owner identities to sample the shared candidate plate; no v3 production registration was made.
- `archive-manifest.json`/`ARCHIVE_FILES.txt` give the minimal explicit archive allowlist. ALL runtime screenshots/logs under`evidence/` remain local and are excluded, as are temporary marked-up geometry diagnostics and Godot caches/imports. Their SHA256 and conclusions remain in`review.json`; these paths do not imply archive closure. Required prepared actor-scale/material input images are retained as generation assets, not runtime test captures.

No raw blur, recolor, warp, resizing, pavement restoration, v1/v2 mixing or production replacement was performed. No automatic fourth generation. The next ungenerated input proposal is `art_source/earth_ground_clean_regen_plan_v4/`, which removes v2/v3 grass from generation imagery and permits road material regeneration from clean source semantics.
