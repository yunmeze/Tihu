# Legend — Godot 2D reconstruction

Target: Godot 4.6.x. This directory is a new reconstruction following the loss of the previous local workspace. Historical screenshots and test reports are not evidence that the missing implementation has been restored.

## Current checkpoint: R0

Original materials have been retrieved from the existing `Legend` branch. The original game and web reference directories are retained unchanged. This checkpoint records the recovery boundaries and delivery policy; it is **not yet a runnable game**.

The implementation belongs in this directory. Production assets and reproducible extraction tools are versioned. Local test fixtures, temporary files, editor caches, and runtime saves are excluded.

## Next checkpoint: R1

- Parse the original A13 map and sprite containers without executing the original executable.
- Render the original map with original layer, placement, and sprite offsets.
- Display the original protagonist and implement verified movement/obstruction behavior.
- Verify import, startup, movement, and representative occlusion in Godot before marking the checkpoint runnable.

Further checkpoints will restore original quest logic, instance inventory, save/load, combat, and the approved science-fiction 2D art direction. New art is image-generated from analyzed original frame sequences, not Blender models.

See `docs/RECOVERY_PLAN.md` for evidence and boundaries.
