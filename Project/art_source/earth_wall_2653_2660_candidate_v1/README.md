# Minimal source closure: wall2653–2660 @18,17

This is a publication proposal, not an installed runtime change. Proposed location: `Project/art_source/earth_wall_2653_2660_candidate_v1/`. A complete normal `Project` checkout is required. Nothing used by reconstruction is read from `recovery-work` or a fixed workspace path.

Only three new complete raw images are included: accepted structured main, the failed complete-cap image whose eave is sampled under a new design, and accepted bounded ridge. Their actual prompts, tool arguments, input SHA and result metadata are preserved. The three exact guide images are included. Actual call files retain historical absolute locations as provenance; `SOURCE_CLOSURE.json` supplies the ordered, portable reference map used to resolve the actual images.

M2/M3 are **not copied again**. Their identical raw bytes and actual-call records are SHA-pinned at `Project/art_source/earth_wall_surface_material_research_v1/m2` and `m3`. The exact accepted house material reference is pinned at `Project/assets/earth/house_280_289_v1/body.png`. Original Wall atlas/map/manifest and the already-published fixed source and geometry contract are also resolved by Project-relative path and SHA. Missing or different dependencies stop reconstruction; there is no download or generation fallback.

## Offline reconstruction

When placed under the proposed Project location:

`python rebuild.py --out /an/owned/output`

When reviewing this owned folder before publication:

`python rebuild.py --project-root /path/to/Project --out /an/owned/output`

Python3, NumPy and Pillow are needed. The pinned test environment is Python3.12.14, NumPy2.3.5, Pillow12.3.0. Project discovery walks ancestors looking for `assets/original/manifest.json` and `data/maps/A13.json`; no checkout-specific absolute path is embedded in the program. It verifies35 image/source/call inputs, then deterministically rebuilds the accepted D2 artwork and eight original-owner slices. The accepted RGBA and PNG SHA are stored in `REBUILD_RECIPE.json`, so no extra reference copy of the full CPU result is needed.

The source package contains no review board, engine screenshot or test log. Reconstruction emits technical proof data alongside runtime assets into the chosen output directory; those proof images/logs are not automatically publication inputs. The separate publication manifest selects only the required runtime assets and registration.

## Fixed scope and accepted limits

Only A13's original eight2653–2660 owners rooted18,17 may use this candidate. Source alpha, original rectangles/order, all four flag0 tails, collision cells, foreground plant and both outside neighbors remain unchanged. The main, eave, M2 and M3 windows remain as reviewed. Ridge U lighting modulation and the missing exactly placed lower contact shade are accepted artistic deviations; neither seamlessness nor full guide-contract conformance is claimed. Complete-cap layoutFAIL remainsFAIL.

Runtime integration and Godot/native acceptance are separate. No image generation is authorized by this source package. This remains an unintegrated candidate.

## Write safety

The output must be a fresh, nonexistent directory whose parent already exists. An existing directory is rejected even when empty. Every input path must be a normalized relative dependency path; inputs and all output ancestors are inspected with `lstat`, with symlinks and non-ordinary filesystem objects rejected. Before each write, the output directory identity and every ancestor are checked again. Each file is exclusively created (`xb`), never overwritten. PNG encoding and sampling parameters are unchanged. All source files are read-only inputs. A failed build may leave its newly created partial output for inspection; choose another fresh directory when retrying.
