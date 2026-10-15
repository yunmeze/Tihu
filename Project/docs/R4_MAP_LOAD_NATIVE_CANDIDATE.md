# R4 optional map-load native candidate

## Entry and scope
Run `res://scenes/map_load_candidate.tscn` in Godot 4.6.3. The default R1 entry is unchanged. This fixed-camera, fixed-pose diagnostic explicitly executes the original four-map load scripts against isolated fixture story values. Function keys select fixtures; they are not natural progression. There is no save, AI, combat, monster simulation, or VB PRNG implementation in this scene.

- F1/F2: A13 ET1, explicit resolved RND 100/0, camera at original chicken position (49,53). Both STOP; only RND 0 stages the registered chicken.
- F3: A13 ET3 hides Lingyun at (62,36).
- F4: A13 ET28 starts the candidate actor at (60,39); original MOVE changes it to (61,39), STOP remains set.
- F5/F6: A00 ET3/ET4, actor (40,60). Original northern nine cells retain/clear their kind8 visuals and collision together. Other six pillars are untouched.
- F7: forced monster resource preflight failure, retaining the current world, actor, story, cursor and commit count. Only the diagnostic error notice changes.
- F8/F9: A01/A02 static maps. BT0=1 in these fixtures; A02's (35,35) boss spawn record is removed, but source spawns are not simulated/rendered.

Each fixture starts with explicit level=1, clear_count=0, game_mode=0 and BT0=1. RND values are already-resolved integers 0..100 passed to the VM; no local random conversion or retry is performed. A13 advances the diagnostic cursor once; the other scripts do not consume it.

## Publication boundary
The pure bridge validates and stages all original load events. `map_load_candidate.gd` then constructs a detached `map_load_world.gd` and movement instance, loads imported map/hero/monster textures, checks the chicken display frame and final actor cell. Only after these succeed does it replace world, movement, story, STOP and random cursor without yielding. Source map JSON is never written. The renderer uses candidate flags for both its drawing objects and A* grid.

This native adapter accepts the four registered source maps and the explicitly registered chicken. It does not claim general support for arbitrary externally supplied texture manifest schemas. Frozen pure bridge malformed/cycle rejection tests are documented separately.

## Chicken display adaptation
Original definition 508 / Mon/220 is rendered at source frame 1, North idle, with original frame offset and original checker shadow. Alive layer1/y ordering and offset use follow the reference renderer (`参考项目/src/game.js`, live unit draw loop). Original EXE initial facing/layer and full spawn lifecycle remain unproven; the fixture does not claim those are recovered. There is no animation or AI. The on-screen banner explicitly calls this a fixed-frame display adapter.

## Fresh validation, 2026-10-15
Native CUA captures in `diagnostics/r4/native` show initial ET1, hidden Lingyun, ET28 MOVE/STOP, explicit chicken absence/presence, ET3/4 gates, rejected preflight retaining ET4, and A01/A02. The same candidate was headless-tested for atomic identities and counters, the exact nine-pillar count difference, collision at (39,57), and A02 record deletion. R1 movement/scene, R2 four portals and R3 dialogue/rollback regressions were rerun with this stage. See logs and `validation.json` for outcomes and hashes. Linux software GL was tested; Windows/export runtime is untested.

Parent review: native chicken / ET3 / ET4 / rejected-preflight captures were visually reviewed. After fixing the stable custom user directory, parent reran R1 movement/scene, R2 portals, R3 opening chain and R4 scene tests successfully on Linux Godot4.6.3. The original native captures predate that path-only setting change; they are not a Windows run. See STORAGE_LOCATION.md.
