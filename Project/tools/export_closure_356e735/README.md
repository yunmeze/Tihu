# Frozen house-local Linux data-PCK closure: 356e735

Source commit: `356e73551b29e596263407514b0c8dc06bda51b6`
Source tree: `8bb2d8940594623066fc3d2a212723d34d8aae48`

This independent version freezes 289 raw files (60,231,389 bytes), plus the original project.godot configuration. The runtime registration contains 154 typed records. It preserves the opening, partial Earth map, six receiver predicates, stable NPC identity, Xuyun, and the building frames 280–289 local house scope. Historical toolsets remain unchanged. Later runtime changes require a separately reviewed version and new validation; this version always exports the pinned commit, even when the checkout's HEAD is newer.

## Requirements and usage

Python 3.10+ without `-O`, Git with the pinned commit and all required Git blobs, and Linux Godot **4.6.3.stable.official.7d41c59c4**. Git LFS pointer-only inputs are insufficient because blob SHA/size checks fail. No network fetching or template installation occurs. A source ZIP alone is insufficient. `GODOT_BIN` can select the engine executable; otherwise `godot` is used.

From any working directory (relative paths are supported):

    python /path/to/Project/tools/export_closure_356e735/build_verified_data_pack.py /path/to/repository /path/to/new-output --static-only

Omit `--static-only` for cold import, real export plugin callback, source execution, and empty-root PCK mount. Use a different new output directory for each run. Outputs must be outside the source Project. Coordinate shared-machine engine access before the full run.

    python /path/to/Project/tools/export_closure_356e735/build_verified_data_pack.py /path/to/repository /path/to/another-new-output

The builder reads exact Git blobs, never live project scripts or borrowed .godot caches. All helper paths resolve relative to this toolset; no research directory or absolute workspace path is required. Only explicitly enumerated runtime files are staged; it does not copy the full repository. Build files, imported resources, logs and PCK stay in the output directory. Allow roughly 500 MB free disk for a full run, plus any checkout; the raw static stage is approximately 61 MB.

## Fail-closed guarantees

Policy identity, commit/tree, 289 distinct paths, every resource SHA/size/type, PNG dimensions, and the final closed dependency set are checked. Unknown policies, schemas/domains, and runtime record types fail. The exact 154-record registration, receiver guard pin, house local-scope flags, ten owners, frames 280–289, body/mask/source/atlas pins remain checked. House registration and owner-bounds bytes are pinned. Missing resources, wrong SHA and path traversal fail. `python -O` is rejected because the inherited validators use assertions.

Traversal remains explicit for R6/A00, atlas pages, chicken, opening/items, historical Earth domains and typed runtime records. Provenance is not recursively traversed and art_source is never wildcarded. The two SE research registration JSONs and build_flat_shadow_gate.py remain exact hash-only leaves; they are not executed or recursively interpreted. The optional registration builder/inventory is not part of this runtime closure and is not rerun by this exporter.

The unchanged export plugin injects all 289 raw files at their original resource paths alongside imported resources. The source and packed verifiers require all raw SHA/size checks, unchanged six-receiver protections, Xuyun withdrawal/restoration, house fresh-invalid fallback/restoration and local identity behavior, opening/A00, and stable NPC source0/source1 authorization. Controlled ET3/ET28 tests are fixtures, not a claim of natural game progression. All engine stages must exit zero without ERROR, SCRIPT ERROR or Parse Error; expected raw Image.load_from_file export warnings alone are not success or failure. Source/packed status bytes must match and source input hashes must remain unchanged after execution.

## Validation and limits

CPU validation passed on the pinned Git blobs and on a new clean sparse checkout. The checkout shared only its Git object database with the existing repository to save disk; it had no imported cache and `git status --porcelain` was empty. A relocated copy of this entire tool directory, invoked with relative script/repository/output paths, passed. Nine negative tests passed: missing required body, corrupted body SHA, bad declared dependency SHA, unknown policy/house/runtime schema, unknown record type, weakened house scope, and path traversal; baseline was restored afterward.

Full cold engine validation of this portable tool version passed on 2026-10-16, using the relocated tool directory and clean sparse checkout with relative CLI paths. Import, export, source and empty-root packed stages all exited zero, required success markers were present, every raw resource matched, and source/packed status files were byte-identical. The output occupied approximately 181 MiB; the conservative 500 MB space recommendation remains.

This run produced data-PCK SHA256 `504c3c5f32fafcb17887d2120a44ef1e6a0aab67357563aaa31276d7ccbdafd1`. The earlier research-only PCK SHA256 was `e133f482e5ee617acc639e975d973dccbec82ed02fbbd57a0d7ea7a6d9569e3c`. These hashes differ; byte-identical PCK reproducibility across fresh imports is not promised. Integrity is established by exact raw-resource checks and source/packed behavior equality, not by requiring the historical container hash.

The version probe emitted `Fontconfig error: No writable cache directories` on stderr while returning the required engine version. None of the four actual engine-stage logs contained that diagnostic, ERROR:, SCRIPT ERROR or Parse Error. This environment diagnostic is disclosed rather than silently conflated with runtime test failure or hidden.

This is Linux data-PCK tooling, **not a Windows executable**. Windows runtime/export, platform templates, whole-game coverage, native GUI appearance, fresh artwork acceptance and full atlas-type hardening are outside this version's validation. Do not publish generated PCK, .godot cache, logs or staged source copies as maintenance tooling.
