# Controlled data-pack candidate: 44db593

Frozen source commit: 44db593064164f8d43a6e75dc0a0b9510a470d53.
This is a separately reviewed candidate, not an update to the historical 3d1cbee policy.

Python static closure: 235 files, 44,656,421 bytes. Versioned east-ground-v1 and plant-reuse-v1 adapters compare actual owner/tile access sets, source dependencies, and runtime_files exactly; provenance is not traversed. Existing real runtime shadow dependencies remain included even when also mentioned as provenance elsewhere. Unknown schemas, changed code/registration hashes, missing declarations, invalid roles/types/dimensions and missing files fail closed.

Build into a NEW directory outside Project:

    python build_verified_data_pack.py /path/to/tihu-legend /path/to/new-output

Godot 4.6 is required. This executes a real export-pack callback and mounts the data pack into an empty project; no export templates are installed by this tool. Raw files retain original paths/bytes through add_file, alongside normal imported resources. Successful checks require 178 ground owners, 24 plant groups/81 owners, pool7/clump3, actor18+E6, source fallback and walk6+6, with matching source/packed status. Godot4.6 Linux data-pack build passed: real export callback added235 raw files; empty-project mount verified all rawbytes and all listed readiness/fallback assertions; source/packed status matched exactly. No Windows executable validation is claimed.

Keep all generated outputs outside Project. Do not archive PCKs, staging trees, logs or negative tests as source tools. Updating a frozen source requires explicit review of new consumers and schema adapters, exact commit/tree and dependency pins, then full source/packed validation. Never silently accept changed bytes by weakening the historical policy.

From the repository root, run:

    python Project/tools/export_closure_44db593/build_verified_data_pack.py . /absolute/path/to/new-output-outside-Project

The scripts self-locate policy,plugin and verifier beside their own __file__. Moving this exact toolset does not change the frozen source or staged res://addons/raw_allowlist paths. Historical Project/tools/export_closure remains unchanged.
