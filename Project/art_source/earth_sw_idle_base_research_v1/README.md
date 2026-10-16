# SW idle base: source-only research

Three original AI outputs are preserved without alpha edits, cropping, resizing or registration baked into the files. No scene, engine integration or accepted four-phase animation is supplied.

- fourphase: root's single two-reference call. Fixed layout, phase differences and far-hand interpretation failed.
- single-base: one call using original SW21 plus the old sheet's first cell. RAW ae23f86c… failed source pose; its mesh constraint candidates also failed.
- local-edit: one call using ONLY that same old sheet first cell (8f5f02…), not ae23. RAW f38646c… failed the pixel-local edit contract. Root separately accepted its new single-texture design and one common registration as a research candidate. These are separate judgments.

The common fit uses all four visible proxies, with no independent heldout set: scale 0.07796116579948255 native pixels/raw pixel, translation (-4.993200252594207,-3.4558992428450352), no rotation. Near-hand residual is +2.147 native y within the recorded combined tolerance; it is not exact source pose. Shoes are visible endpoints, not proved floor contacts. Weak alpha and hidden RGB remain. Filter footprints still need validation. Do not reuse ae23 constraints for f386 or infer that new phase work is included.

## Portable evidence replay

Use Python 3 with Pillow and NumPy, plus a Git repository retaining the commits/blobs in DEPENDENCIES.json:

    python replay_sources.py --repo /path/to/tihu-legend --report /outside/archive/sw-replay.json
    OPENBLAS_NUM_THREADS=1 python replay_bounded_paths.py --report /outside/archive/bounded-replay.json

The first command checks every archive hash and Git dependency; reconstructs the actual source sheet, SW21 reference, first-cell extraction and material-fragment board byte-exact; and recalculates the common fit numerically. The second recalculates only the two already-failed finite 201-step geometric paths and compares their complete numeric result. It is not a new solver search or animation replay. Original nonlinear solver experiments and all preview/rendering tests are omitted; those historical conclusions remain reports, not an included runnable suite.

DEPENDENCIES.json pins small metadata and already-published atlases; no EXE or large original pack is copied. Actual input PNG bytes are preserved. PATH_MAP.json maps original call paths to local archive files or verified Git blobs; historical absolute paths in frozen REQUEST/report files are provenance strings only, never executable dependencies. Original status strings such as ROOT_ACCEPTANCE_PENDING remain untouched; current acceptance scope is the separate statement above.

.gdignore keeps this research out of editor import. Nothing in this package activates runtime changes. All new phase work is excluded.
