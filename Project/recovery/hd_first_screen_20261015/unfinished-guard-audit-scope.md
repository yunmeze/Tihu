# Stopped HD resource guard audit checkpoint

Stopped on parent instruction at 2026-10-15 07:27 UTC. No runtime/core/resource files were edited. All audit writes and Godot XDG directories are isolated under this directory. No further tests or repairs are planned.

## Scope and immutable evidence

- Source project: `/workspace/scratch/22c897619190/tihu-legend/Project`
- Helper snapshot tested: `project/scripts/art/hd_art_resources.gd`, SHA-256 `7baef61889961b97d785bb31eacf51e754579587336c03c65efc9b61bc246dbc`.
- Reference data: ordinary `assets/scifi/environment/a13_upright_tree_v1/registration.json` first six owners and exact `data/maps/A13.json`.
- Engine: Godot 4.6.3, headless, isolated minimal project with imported copies of six owner PNGs.
- The source helper had a different SHA-256 at the final check (`bc36cde51df0078457f676be5b8c66e0220f20368ae72ddcd63d9b333f799895`). Findings apply to the recorded tested snapshot; the subsequently changed file has not been re-audited.

## Confirmed unresolved findings in the tested snapshot

1. A finite JSON/GDScript coordinate `[1e100, -1e100]` is accepted for `world_top_left`, publishes all six owners, and converts to `Vector2(inf, -inf)`.
2. A positive `scale=1e-100` is accepted, publishes all six owners, and converts to zero in render-vector precision.
3. `registration.guard_contract.fields` explicitly lists `cell`, `layer`, and `sort_y`; each missing or null value is still accepted and publishes all six owners. These fields are ignored by this helper. Whether caller validation closes the contract gap was not tested.
4. A path-prefix bypass was confirmed in the final already-running probe before the stop instruction arrived: direct `res://outside.png` is rejected, but equivalent `res://assets/../outside.png`, `res://assets/scifi/../../outside.png`, and `res://assets//../outside.png` are accepted and publish all six owners when the PNG and metadata otherwise match. Canonicalized path is outside `res://assets/`.

Additional observational cases: the helper also ignores key, pack, frame_index, source_cell_index, source_map_byte_offset, and source-map ID. They were deliberately mutated to establish the helper boundary. This alone does not prove a rendering defect because callers may retain authoritative original metadata or enforce map identity.

## Completed test results

- `audit.gd`: 143 cases, 19 acceptances contrary to deliberately strict mutation expectations; the list includes the observational fields above. Baseline and reversed valid owner order accepted all six.
- Every result was either zero or six owners; no partial publication was observed.
- Required/typed malformed consumed fields, duplicates, changed source cells, absent or malformed owner hashes, dimension mismatches, invalid numeric scales, NaN and infinity were rejected.
- No `SCRIPT ERROR`, `ERROR:`, or `WARNING:` appeared in either test-run log.
- Path probe: six cases, including the three confirmed out-of-prefix traversal acceptances.

## Artifacts

- `report.json`: all 143 primary case results and render-precision conversion evidence.
- `run.log`: BEGIN/END markers and results for primary tests.
- `path-report.json`, `path-run.log`: six path cases.
- `project/audit.gd`, `project/path_audit.gd`: reproducible isolated harnesses.
- `import.log`, `import2.log`: isolated import logs.

This checkpoint is not a completed safety acceptance of the HD guard module. The unresolved findings and version mismatch require review before claiming the guard is complete.
