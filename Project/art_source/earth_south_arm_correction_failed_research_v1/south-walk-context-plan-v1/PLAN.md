# Minimal pure-2D in-context south-walk diagnosis (proposal only)

## Aim
Review the unchanged leg-only57–62 candidate in an actual A13 walking context. Arm translation experiments are stopped; do not include their partial outputs. Keep the original source renderer as fallback. No main runtime integration, atlas replacement, mesh solving, image generation, collision changes or new shadow design.

## Verified current behavior to preserve
- Project/scripts/core/movement.gd: WALK_SPEED1.5625 grid cells/second; direction4 is screen-south Vector2i(0,1); current source_frame() gives57–62. Each physics step increments5 animation units and each phase spans35, hence7ticks at the configured50Hz.
- movement.gd explicitly describes itself as R1 reference-adapted movement, not original EXE timing parity. Call this the current project's reference speed/collision behavior, not verified original-binary behavior.
- Collision configure() reads map flags−1/−2/−3 and occupied cells; AStar diagonal mode only if no obstacles. Reuse its full unchanged configuration and route request; do not create a visually similar open path that omits occupancy.
- Project/project.godot sets50 physics ticks/second. Current world projection uses grid position×(48,32). S therefore travels50 logical screen pixels/second under straight walking; a42tick loop traverses1.3125 cells /42 logical screen pixels. These are kinematic references, not foot-contact constraints.
- Current candidate draw contract in scripts/earth/sample_world.gd is128×128 logical canvas, offset(−16,−64), HD4 texture512×512. Preserve it exactly for the six proposed south frames.

## Isolated owned project
Freeze a snapshot of the current diagnostic A13 scene/map/actor/render dependencies into a new owned workspace project (copy-on-write or read-only source dependencies only; do not edit repository resources). Do not use the large production scene as a modified main entry. An owned subclass overrides only the hero draw branch when action==walk, direction==4, phase57–62, all six candidate SHA/dimensions valid, and the diagnostic toggle is enabled. Every other action/direction and any preparation failure calls the unchanged superclass renderer. Atomically load six frames: no partial group or mixing failed arm trials.

The movement instance, map flags, occupied NPC cells, interaction/door bounds, draw sorting and camera transform are shared by source/candidate comparison. Toggle art without resetting position, action or animation units. A fresh independently stepped actor is not needed and risks divergent paths.

## Smallest route and view
1. CPU-read current A13 data and occupancy first. Choose one verified passable straight south corridor of at least8 cells near existing ground/objects; record exact start/end, collision/occupancy hashes and route. Do not invent coordinates before checking the map. The scene uses the original environment, not a flat gray mockup.
2. Run at normal speed for at least five full loops, with one start and stop. Observe true1x first. No per-frame centering or camera easing to hide bob. A fixed camera is preferable for foot-vs-ground observation; use the same camera for both render modes.
3. Compare source versus candidate by toggling art on the same tick/position, or render two synchronized views sharing the same actor state and camera. If two views, label any viewport cropping and actual raster scaling. Offer a true2x pixel crop of the same view only as secondary inspection, not a larger character in the world.
4. Include one blocked-cell request (rejected under original collision) and one non-S/idle interval to verify native fallback. No need to build a full eight-direction animation prototype.
5. If the original corridor contains a tree/building occlusion, retain normal y-sort. Do not route through solid objects just to obtain an occlusion screenshot.

## Evidence and acceptance
Log tick, monotonic timestamp, action, direction, phase, world position, path acceptance, selected art branch and actual window/viewport dimensions. Verify source and candidate toggles share the same position/phase/collision trace. Treat seven ticks as scheduling evidence; actual display intervals must be measured separately.

Visually judge gait relative to ground travel: stride readability, apparent sliding, leg proportions, knee/boot projection, body bob and58→59/61→62/62→57 transitions. Do not move the root to make soles look anchored. The endpoint driver match is irrelevant to independent acceptance. Upper-body posture is still not source-identical; preserve that limitation and compare the unchanged arm behavior in context.

Original source may contain baked dithered shadow while the modern candidate does not. Inspect the actual renderer's shadow path before implementation; preserve existing environment/occlusion behavior, add no guessed candidate shadow, and label any unmatched hero-shadow treatment as a confound. A boot terminal is not a verified ground-contact point.

Any missing/corrupt candidate frame should visibly and atomically fall back to the original source group; assert no partial candidate group. Validate the invalid-asset case with an owned fixture, never by deleting or corrupting source files.

## Gates / execution order
This is a plan, not permission to modify the main runtime. On approval: freeze minimal owned scene/dependencies and candidate hashes, CPU route/guard tests, then request planner's serial check-only lease. Actual short GPU launch remains with the official desktop planner after parse0. Record a short continuous view if available rather than claiming dynamic acceptance from isolated screenshots. Stop with a diagnostic result; do not promote assets or replace runtime selection automatically.
