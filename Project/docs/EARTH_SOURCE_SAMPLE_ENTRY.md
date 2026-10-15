# Earth entrance source-only foundation

Run `godot --path Project res://scenes/earth_sample_preview.tscn` (or open that scene in Godot). The default R1 scene and R6 natural opening remain unchanged.

This entry currently uses **only original source artwork**. It prepares a playable, correctly layered coordinate foundation; it is not a completed new-style sample. No canonical single pose has been substituted for walking or idle animation.

## Fixed review geometry

- World rectangle: `[2496,960,768,512]`.
- Logical viewport: 768×512; actual SubViewport raster: 1536×1024.
- Original actor starts at cell `(61,39)`; it is not moved to manufacture the composition.
- Original A13 cells, collision flags, A*, actor frames, NPC shared 17-tick clock and layer/Y/stable order remain in use.
- The window is resizable. A 3:2 letterbox preserves this exact visible rectangle; screen input is converted through its display rectangle and inverse 2× stretch.

Click to request an original-map route. Shift uses the existing reference-adapted run speed; Space stops. F switches fixed/follow camera, G toggles the source grid, H hides the explanatory HUD. Routes are not restricted to the sample rectangle. Follow mode explicitly leaves unconverted surroundings as source. This is an art sample, not execution of map load scripts, NPC conversations or portals.

## New asset preparation interface

The new assets must remain detached until their whole group is prepared. `scripts/earth/asset_guard.gd` returns either all validated owner resources or an empty dictionary. Its trusted expected identities must be built from the original approved owner scope, not the incoming registration. Rendering publication and replacement hooks are deliberately not yet installed: there are no new assets in this entry.

Environment registration should provide exact original key, pack, frame_index, cell, layer, sort_y, stable_source_order and source_cell, plus high-density texture path/SHA/dimensions, logical world_top_left and common scale. Building fragments must preserve raw pixels once and source ordering. Ground is a separate 64-placement sample with original rectangles/alpha; it must not be treated as a background covering object ordering. Actor interfaces require complete approved source-frame mappings and density/anchor units. New Earth illumination must be reviewed independently; the retired courtyard cast direction must not be reused by assumption.

## Fresh verification on 2026-10-15

- Headless startup and mapping/source-flags/A* test passed.
- Actual native window 1152×768: click mapped to logical `(432,320)`, cell `(61,40)`, and actor arrived.
- Actual resized window 998×698 with visible top/bottom letterbox: click mapped to logical approximately `(431.7114,287.9519)`, cell `(61,39)`, and actor returned.
- Empty-cache import/start results are recorded in the stage handoff. Source-only screenshots are internal evidence and are not presented as approved new-style results.

Original movement speeds and animation schedules retain their documented reference-adaptation boundary; this stage does not establish new original-EXE timing evidence.
