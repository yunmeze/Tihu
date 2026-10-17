# A01 ordinary animation core v1

This is a NEW independent GDScript implementation from the archived, pinned A01 animation contract. There is no recovered core hash or prior engine-test result. It is outside the frozen source repository and is not wired to the default runtime, scene, map, AI, combat, or resource loader.

## Source checkpoint 01

- src/a01_animation_core.gd: pure-data RefCounted static API
- docs/API.md: exact entry, snapshot, event, and boundary contract
- SOURCE_PINS.json: fixed original source identities and contract dependency hashes
- evidence/: supplemental +0xb4 pause proof, checked against fixed original EXE bytes
- SOURCE_ARCHIVE_MANIFEST.json: explicit Git source archive allowlist and file hashes
- .gdignore: prevents archive directories from being imported accidentally

The archive is ONLY archive_files listed in SOURCE_ARCHIVE_MANIFEST.json plus the manifest itself. local/** contains fixtures, runners, development scripts and logs and is excluded. Do not recursively archive this directory. No project.godot, cache, .uid, temporary project or test runner belongs in the source archive.

State, phase, stored_frame, previous_state and clock remain separate. Walk uses five emitted phases in six allocated slots. Pursuit and wander entries differ. Attack/hurt completion retains the final frame. Death keeps state145/phase8 and returns clear_occupancy/publish_corpse events; it does not change a world or remove a corpse.

Validation status at this checkpoint: source hashes and fixed b4 instruction bytes checked; implementation written; engine parse and behavior tests NOT RUN. Local table fixtures will be handed to the sole engine coordinator after static review. No Godot or original EXE was executed by the implementation worker. No source-repository change, staging, commit or push was performed.

Boundaries: no original Hz/seconds conversion, no complete AI/damage/status system, no appearance888, no automatic corpse deletion, and no claim that the conditional hurt clock0/phase0 entry covers all external damage paths. q is an explicit effective source value0/1. See docs/API.md for deliberately unsupported states, overflow and record0 cases.
