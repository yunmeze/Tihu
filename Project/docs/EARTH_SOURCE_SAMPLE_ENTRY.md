# Earth entrance candidate: four new SE idle frames

Run `godot --path Project res://scenes/earth_sample_preview.tscn` (or open that scene in Godot). The default R1 scene and R6 natural opening remain unchanged.

This entry now offers the approved candidate SE idle sequence 13–16, directly sampled from its density-4 atlas. Building, ground, NPCs and every other actor action/direction still use original source artwork. It is not a completed new-style sample. A canonical single pose is never substituted for walking. New character shadows are deliberately absent pending the new lighting contract. Press B to compare source/new idle.

## Fixed review geometry

- World rectangle: `[2496,960,768,512]`.
- Logical viewport: 768×512; actual SubViewport raster: 1536×1024.
- Original actor starts at cell `(61,39)`; it is not moved to manufacture the composition.
- Original A13 cells, collision flags, A*, actor frames, NPC shared 17-tick clock and layer/Y/stable order remain in use.
- The window is resizable. A 3:2 letterbox preserves this exact visible rectangle; screen input is converted through its display rectangle and inverse 2× stretch.

Click to request an original-map route. Shift uses the existing reference-adapted run speed; Space stops. F switches fixed/follow camera, G toggles the source grid, H hides the explanatory HUD; B changes the retained source/new-idle preference. Routes are not restricted to the sample rectangle. Follow mode explicitly leaves unconverted surroundings as source. This is an art sample, not execution of map load scripts, NPC conversations or portals.

## New asset preparation interface

The new assets must remain detached until their whole group is prepared. `scripts/earth/asset_guard.gd` returns either all validated owner resources or an empty dictionary. Its trusted expected identities must be built from the original approved owner scope, not the incoming registration. The current actor preparation validates the complete four-frame mapping, dimensions, density, logical offset, 12-tick schedule and actual source PNG hash before publishing one CanvasTexture. Missing or malformed dependencies clear the entire candidate and retain source body/head. Movement or other directions use source automatically; returning to SE idle restores the saved B preference. Environment replacement hooks are not installed yet.

Environment registration should provide exact original key, pack, frame_index, cell, layer, sort_y, stable_source_order and source_cell, plus high-density texture path/SHA/dimensions, logical world_top_left and common scale. Building fragments must preserve raw pixels once and source ordering. Ground is a separate 64-placement sample with original rectangles/alpha; it must not be treated as a background covering object ordering. Actor interfaces require complete approved source-frame mappings and density/anchor units. New Earth illumination must be reviewed independently; the retired courtyard cast direction must not be reused by assumption.

## Fresh verification on 2026-10-15

- Headless startup and mapping/source-flags/A* test passed.
- Actual native window 1152×768: click mapped to logical `(432,320)`, cell `(61,40)`, and actor arrived.
- Actual resized window 998×698 with visible top/bottom letterbox: click mapped to logical approximately `(431.7114,287.9519)`, cell `(61,39)`, and actor returned.
- Candidate raw SHA: `60f89f65dd817ec80065de941e62e36e1068302c3f2bc4eb5014d8d56f450c02`. The source and independent 1×/2× body-only diagnostic ran two complete 12-tick loops including 16→13. The same fixed map point repeated both loops, then an original A* move used source frame 58 and arrived at 61,40.
- Ordinary-entry B toggle was checked visually. Candidate preparation/fallback/recovery passed 128 checks. Empty-cache import of the newly added actor PNG and the same tests are recorded in the stage handoff. These internal images are not a claim that the new environment style is complete.

Original movement speeds and animation schedules retain their documented reference-adaptation boundary; this stage does not establish new original-EXE timing evidence.
