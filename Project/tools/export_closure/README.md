# Isolated exact-byte export closure prototype

This is a build/review tool candidate, not a Windows executable or proof of Windows startup. No export templates are installed by these tools. Production project files are not modified. Outputs are outside the repository.

## Reproduce

Requirements: existing Godot 4.6.3 editor, Python 3.12+ standard library, Git, readable repository containing the frozen commit in policy.json. No Pillow or template download is required.

```
python build_verified_data_pack.py /path/to/tihu-legend /new/outside/output-directory
```

The output directory must not exist. The wrapper archives the frozen commit into a fresh directory, generates its raw allowlist, installs this prototype plugin ONLY in that copy, selects the two research scenes and runtime dependencies, and exports a data PCK. The staging main scene is explicitly first-map, leaving the source default unchanged. A second process loads it into an empty project. All raw path/size/SHA contracts and the first-map/walk scene readiness are checked; complete recorded source-versus-pack candidate/shadow status must match. Only then is UNVERIFIED.pck renamed LINUX_DATA_PACK_VERIFIED_NOT_WINDOWS.pck. Keep test outputs/logs/PCK/cache out of Git.

To inspect a current working tree without freezing changes automatically:

```
python generate_allowlist.py /path/to/tihu-legend/Project --out /outside/current-allowlist.json
```

A differing script, changed legacy registration, unknown schema, missing adapter/required field/file, escaped path, or mismatching pinned dependency fails. The wrapper also rejects export errors or absent add_file callback, failed/timed-out packed checks, and unequal status. EditorExportPlugin has no abort-return contract in _export_begin: a callback error alone can still leave a pack on disk. Therefore build_verified_data_pack.py's validation and unverified-output rule are mandatory; do not distribute an arbitrary editor-produced pack.

## Versioned contracts

- policy.json: earth-reviewed-legacy-export-policy-v1. Explicit versioned legacy selectors distinguish runtime fields from provenance. source_commit, source_tree and SHA code/registration/asset pins bind the reviewed graph. It is a reviewed input, not regenerated automatically from whatever files happen to exist.
- generated allowlist: earth-export-raw-allowlist-v1. Exact virtual paths, sizes, SHA256, type, PNG dimensions, and required_by edges. Ordinary imported resources remain necessary alongside the raw bytes.
- future standalone registration interface: earth-runtime-files-v1. Top-level schema, runtime_files, optional status/provenance. runtime_files records contain path, sha256, bytes, type, role; PNG additionally width/height. Allowed types png/json/gdshader/gd; roles texture/registration/source-map/source-atlas/source-atlas-manifest/shader/raw-contract. Empty declarations, unknown fields/types/roles and missing/mismatched metadata fail. Provenance is deliberately not traversed. A future domain-specific registration needs an explicit audited adapter rather than being accepted because it resembles this shape.

The legacy adapter preserves source atlases/fallback and all old shadow input hashes (including raw script/shader bytes), not only seven newly selected PNGs. Source provenance evidence, owner-label masks and unused art generation composites are excluded where the runtime does not use them. The bounded raw graph is not a full semantic proof for future loaders: new code must consume the declared runtime_files contract or receive a reviewed adapter and isolated packed-runtime assertions.

## Frozen-source changes

A new commit is not approved merely by changing source_commit. Review the code diff, classify each new runtime dependency versus provenance, update supported schema/field selectors and exact pins, then regenerate. Add readiness checks for new feature consumers and repeat the external negative-validation suite and clean source/pack comparisons. Pool/fine-clump research archive presence alone must not include them. The supported earth-first-map-static-props-v1 adapter compares its runtime_files exactly against the actual guard’s group masters/source_dependencies, checks the source_map/source_manifest bindings, and verifies metadata. Provenance remains excluded. Future changes need a new reviewed frozen policy.

## Evidence for frozen source 3d1cbee54f1f5a64753148cb0908761c7a9725ec

Actual Godot 4.6.3 --export-pack callback ran without templates. 230 raw files / 42,856,110 bytes passed exact original-path SHA/size checks in a separate empty-root process. First-map 121 ground owners, 6 E frames, pool 7 owners and clump 3 owners, walk 6 source+6 research frames, 9 source atlas textures, 2,553 floor records, 1,156 objects, all existing candidate groups and five shadow gates matched source readiness. Thirteen negative cases were rejected, including future provenance exclusion and omission from the static-props runtime declaration even after updating its outer byte pin. Export mutation of the first allowlist hash logged rejection without RAW_ALLOWLIST_EXPORT_ADDED; its output is intentionally invalid.

This verifies Linux data-pack closure and engine callbacks. Native Windows executable launch, graphics/fonts/input/user-data behavior, signing/SmartScreen and clean-machine distribution remain untested. A Windows build additionally needs matching official export templates and a separate native acceptance pass.

Negative-case scripts and logs are retained outside the repository as review evidence; they are not distributed with these build tools. verify_data_pack.gd is the required packaging-integrity validator invoked by the build tool, not a standalone gameplay test suite.
