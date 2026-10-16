# Frozen opening + partial Earth data-pack closure: ca55cfc

Source commit: `ca55cfc7805cea135b9ff4273cca0557c270474b`
Source tree: `256a61df2b622c37387a6862c473364a3ea54036`

This independent version does not replace the historical 44db593, d88aa02 or 19e2952 toolsets. It freezes 283 files (59,441,936 raw bytes), plus the original project.godot configuration. Its three roots are earth_new_game_candidate, earth_first_map_review and earth_walk_review. The frozen runtime declaration has 148 records; it is not by itself the entire export closure.

## Requirements and usage

Python 3.10+, Git, and Linux Godot **4.6.3.stable.official.7d41c59c4** on PATH as `godot`. Use an ordinary Python interpreter, not `python -O`. The build requires a **Git repository containing the frozen commit and blobs**; a source ZIP alone is insufficient. No network fetching or template installation is performed. The output directory must be new and outside Project.

From any working directory:

    python /path/to/Project/tools/export_closure_ca55cfc/build_verified_data_pack.py /path/to/tihu-legend /absolute/path/to/new-output --static-only

The CPU-only form freezes exact Git blobs and validates the closed typed graph. Omit `--static-only` to perform import, real export-pack callback, source verification and empty-root PCK mount. Use another new output directory for that run. Coordinate Godot access if sharing the machine.

    python /path/to/Project/tools/export_closure_ca55cfc/build_verified_data_pack.py /path/to/tihu-legend /absolute/path/to/another-new-output

All helper paths are relative to this toolset's `__file__`; generated files remain in the requested output directory. No main-project files or Git state are changed. The builder stages only enumerated runtime inputs, not the full research/archive tree. It copies owned bytes, never links live scripts.

## What is verified

The policy pins every source SHA, byte count, type and PNG dimensions. Traversal explicitly handles the R6/A00 map and atlas graph, chicken manifest, item/opening data, six-caster receiver pins, Xuyun pins, historical Earth domains and typed runtime_files records. Unknown domains/types, malformed declarations, changed bytes, missing files, or a changed closure set fail. Two SE research registration JSON files and build_flat_shadow_gate.py are explicit receiver hash-only leaves; they are included as exact raw bytes, not interpreted or executed. Provenance is not recursively traversed and art_source is never wildcarded.

The export plugin adds all 283 raw files at their original resource paths alongside normal imported resources. Verification mounts the PCK from a new empty root, checks every raw SHA/size, and requires source/packed status equality. Assertions cover 121+57 ground, 24 plant groups/81 owners, pool7/clump3, actor and walk6+6, source fallback, fixed-seed chicken spawn, all six receiver predicates, Xuyun, five opening pages, the two NPC dialogue chains and A00 publication.

The ca55cfc toolset was run from this versioned directory against the fixed Git commit with Linux Godot 4.6.3. Import/export/source/empty-root mount all exited 0; all 283 raw files matched and source/packed status bytes were identical. The verifier also passed enabled sorting/prefilter routing, unchanged 4+6 source proof SHA pins, sorted sequence equivalence, dynamic/NPC/hero path retention, and Xuyun withdrawal/restoration on redraw with no visual refresh. The three export-plugin files remain unchanged from the prior validated toolset. Godot emitted its usual raw Image.load_from_file export warnings; the real raw-byte callback and empty-root packed execution passed, so those warnings were not silently treated as proof of failure or success. No SCRIPT ERROR, ERROR or Parse Error was accepted.

Stable NPC identity assertions additionally require the original A13 source0/source1 authorization boundary and unchanged six-field NPC records. After the natural opening reaches A00, controlled fixtures reload A13 at ET3 and ET28: at ET3 runtime slot1 resolves to source2 and interaction is rejected even at zero distance; at ET28 source1 remains authorized and opens dialogue. These are controlled map-load tests, not a claim of natural game progress to ET28. Both source and packed executions passed with identical results. The helper, map-load bridge and base new-game controller are pinned to this commit; the 148-record registration and receiver document remain unchanged.

This is **Linux data-PCK validation only**. No Windows executable, Windows runtime, platform template installation, whole-game coverage, new artwork acceptance or native-screen visual claim is implied. Output PCK/logs/cache/source copies are runtime artifacts and must not be committed as maintenance tools. Updating the frozen input requires a separately reviewed version and complete validation; do not silently relax this policy.
