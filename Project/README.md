# Legend — Godot 2D reconstruction

Target: Godot 4.6.x. This directory is a new reconstruction following the loss of the previous local workspace. Historical screenshots and test reports are not evidence that the missing implementation has been restored.

## Current checkpoint: R1 — source-art movement preview

Original materials have been retrieved from the existing `Legend` branch. The original game and web reference directories are retained unchanged. The A13 source-art preview is now runnable in Godot 4.6.x. Open `Project/project.godot` and press F5. Left-click to move, hold Shift to run, Space to stop. This is a bounded movement preview: story, inventory, combat, saving, and remade art are not implemented yet.

The implementation belongs in this directory. Production assets and reproducible extraction tools are versioned. Local test fixtures, temporary files, editor caches, and runtime saves are excluded.

## R1 verified scope

- Parse the original A13 map and sprite containers without executing the original executable.
- Render the original map with original layer, placement, and sprite offsets.
- Display the original protagonist and implement verified movement/obstruction behavior.
- Verify import, startup, movement, and representative occlusion in Godot before marking the checkpoint runnable.

Further checkpoints will restore original quest logic, instance inventory, save/load, combat, and the approved science-fiction 2D art direction. New art is image-generated from analyzed original frame sequences, not Blender models.

See `docs/RECOVERY_PLAN.md` for evidence and boundaries.

See `docs/R1_SOURCE_PREVIEW.md` for controls, tested behavior, and deliberate limits. Linux Godot 4.6.3 was tested; Windows has not yet been tested.
