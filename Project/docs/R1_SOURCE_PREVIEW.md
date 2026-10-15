# R1: source-resource A13 preview

This is a new, bounded reconstruction after loss of the previous workspace. It is not the old completed project or a recovered save.

## Run
Godot 4.6.3: open Project/project.godot and press F6 on scenes/game.tscn, or F5. Left-click a reachable cell, hold Shift to run, Space to stop, G for collision overlay. A13 starts at 61,39. The top label explicitly identifies the free-movement preview.

Cloud validation uses `godot --audio-driver Dummy --path Project` because this machine has no audio device. Normal application sound has not been implemented. The first trial's audio-device ERROR and NPC black-key mismatch are retained as failed evidence; the extractor was corrected and textures reimported before final validation.

## Included
- Original A13 binary map: 100×100 x-major cells, original flags, layer assignment, 2553 floor placements, 1145 map objects plus 11 NPCs.
- Original map and NPC image decoding, frame offsets/crops and resource hashes. Map object top is 32−original height; map frames ignore actor offset. NPC frames use original offset. Exact source checker shadows are preserved once in their sprites.
- Original Hero/2 and Hero/Head/0 movement frames 1–128, shared draw origin, body then head, no mirroring or image regeneration.
- Stable sorting by original layer, source cell y, then original insertion order. Actor y participates in the same ordering. Floor sprites are drawn first. Culling uses each actual frame rectangle, not anchor-only culling.
- Godot AStarGrid2D with original flag collision and no diagonal corner cutting. No fabricated NPC-solid cells.

## Deliberate bounds / adapters
- No opening story, STOP, dialogue, inventory, saving, combat, portals or original game-state transactions yet. Preserved scripts are not executed. Free movement is a clearly labelled preview, not the real original new-game sequence.
- Clicks require the exact destination to be traversable and reachable. The reference browser implementation searches for a nearest reachable endpoint for blocked clicks; this behavior is not implemented here.
- Walk/run speeds 1.5625/3.125 cells/s are reference-derived adaptation, not newly verified original EXE timing. Direction and per-axis travel are retained; changing walk/run resets the clip clock in this R1 implementation rather than reference phase-preserving mode switch.
- Idle/walk/run clip cadence is 12/7/5 ticks at 50 updates/s, with source frame groups. This does not establish original transition timing parity.
- A13's 68 trailing source bytes are preserved but not interpreted. No original EXE is executed.
- No historical natural save, earned level or rewards were recreated.

## Local development validation (test fixtures intentionally excluded from Git)
`godot --headless --path Project --script res://tests/test_movement.gd`
`godot --headless --path Project --script res://tests/test_scene.gd`
Run the extractors before editor import if rebuilding from original materials. Resource validation checks the loaded source textures and all 128 body/head mappings. Scene route tests cover 61,39→61,49→61,53→61,39, with stable ordered objects at each endpoint.

Current GUI evidence is recorded separately under Project/diagnostics/r1 after final review. Headless tests are not a substitute for the native mouse and depth screenshots.

Parent independently reran movement and scene resource/order/route tests on 2026-10-15 at 03:16 UTC, both passed. Opening, walking, tree-behind/tree-front, and rejected blocked-cell native captures were reviewed. This is not a test of story, combat, or Windows.
