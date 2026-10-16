# Frozen opening + partial Earth data-pack closure: d88aa02

Source commit: `d88aa02aac4244fb93e5a94d24bb3876120c287f`
Source tree: `981fb7af7f9d53fa79cce9d50cd5175f02befbf3`

This independent version does not replace the historical 44db593 toolset. It freezes 280 files (59,421,416 raw bytes), plus the original project.godot configuration. Its three roots are earth_new_game_candidate, earth_first_map_review and earth_walk_review. The frozen runtime declaration has 148 records; it is not by itself the entire export closure.

## Requirements and usage

Python 3.10+, Git, and Linux Godot **4.6.3.stable.official.7d41c59c4** on PATH as `godot`. Use an ordinary Python interpreter, not `python -O`. The build requires a **Git repository containing the frozen commit and blobs**; a source ZIP alone is insufficient. No network fetching or template installation is performed. The output directory must be new and outside Project.

From any working directory:

    python /path/to/Project/tools/export_closure_d88aa02/build_verified_data_pack.py /path/to/tihu-legend /absolute/path/to/new-output --static-only

The CPU-only form freezes exact Git blobs and validates the closed typed graph. Omit `--static-only` to perform import, real export-pack callback, source verification and empty-root PCK mount. Use another new output directory for that run. Coordinate Godot access if sharing the machine.

    python /path/to/Project/tools/export_closure_d88aa02/build_verified_data_pack.py /path/to/tihu-legend /absolute/path/to/another-new-output

All helper paths are relative to this toolset's `__file__`; generated files remain in the requested output directory. No main-project files or Git state are changed. The builder stages only enumerated runtime inputs, not the full research/archive tree. It copies owned bytes, never links live scripts.

## What is verified

The policy pins every source SHA, byte count, type and PNG dimensions. Traversal explicitly handles the R6/A00 map and atlas graph, chicken manifest, item/opening data, six-caster receiver pins, Xuyun pins, historical Earth domains and typed runtime_files records. Unknown domains/types, malformed declarations, changed bytes, missing files, or a changed closure set fail. Two SE research registration JSON files and build_flat_shadow_gate.py are explicit receiver hash-only leaves; they are included as exact raw bytes, not interpreted or executed. Provenance is not recursively traversed and art_source is never wildcarded.

The export plugin adds all 280 raw files at their original resource paths alongside normal imported resources. Verification mounts the PCK from a new empty root, checks every raw SHA/size, and requires source/packed status equality. Assertions cover 121+57 ground, 24 plant groups/81 owners, pool7/clump3, actor and walk6+6, source fallback, fixed-seed chicken spawn, all six receiver predicates, Xuyun, five opening pages, the two NPC dialogue chains and A00 publication.

The d88aa02 source was tested with Linux Godot 4.6.3: all four CLI stages exited 0 and source/packed status bytes matched. The archived verifier and three export-plugin files are byte-identical to those used in that successful run. Python packaging was relocated and CPU-checked; the complete Godot run was not repeated merely for packaging. The frozen raw closure is identical.

This is **Linux data-PCK validation only**. No Windows executable, Windows runtime, platform template installation, whole-game coverage, new artwork acceptance or native-screen visual claim is implied. Output PCK/logs/cache/source copies are runtime artifacts and must not be committed as maintenance tools. Updating the frozen input requires a separately reviewed version and complete validation; do not silently relax this policy.
