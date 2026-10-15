# Earth entrance candidate: SE idle and 64 ground owners

Run `godot --path Project res://scenes/earth_sample_preview.tscn` (or open that scene in Godot). The default R1 scene and R6 natural opening remain unchanged.

This entry now offers the approved candidate SE idle sequence 13–16, directly sampled from its density-4 atlas. The bounded v2 ground plate replaces exactly 64 original FloorBig owners. Building, NPCs, vegetation and every other actor action/direction still use original source artwork. It is not a completed new-style sample. A canonical single pose is never substituted for walking. New character shadows are deliberately absent pending the new lighting contract. Press B to compare source/new idle.

## Fixed review geometry

- World rectangle: `[2496,960,768,512]`.
- Logical viewport: 768×512; actual SubViewport raster: 1536×1024.
- Original actor starts at cell `(61,39)`; it is not moved to manufacture the composition.
- Original A13 cells, collision flags, A*, actor frames, NPC shared 17-tick clock and layer/Y/stable order remain in use.
- The window is resizable. A 3:2 letterbox preserves this exact visible rectangle; screen input is converted through its display rectangle and inverse 2× stretch.

Click to request an original-map route. Shift uses the existing reference-adapted run speed; Space stops. F switches fixed/follow camera, G toggles the source grid, H hides the explanatory HUD; B changes the retained source/new-idle preference; P independently switches all 64 ground owners. Routes are not restricted to the sample rectangle. Follow mode explicitly leaves unconverted surroundings as source. This is an art sample, not execution of map load scripts, NPC conversations or portals.

## New asset preparation interface

The new assets must remain detached until their whole group is prepared. `scripts/earth/asset_guard.gd` returns either all validated owner resources or an empty dictionary. Its trusted expected identities must be built from the original approved owner scope, not the incoming registration. The current actor preparation validates the complete four-frame mapping, dimensions, density, logical offset, 12-tick schedule and actual source PNG hash before publishing one CanvasTexture. Missing or malformed dependencies clear the entire candidate and retain source body/head. Movement or other directions use source automatically; returning to SE idle restores the saved B preference. The ground hook overrides only the original floor-frame drawing call, retaining its exact order before every object. Trusted scope is independently derived from original A13 cells at x52..66/y30..44, both step2. It requires exactly 64 identities, original source_cell, world origin cell*[48,32], 192×128 texture and scale .5; any failed record restores the entire source ground group. Tiles use nearest sampling of the direct 2× plate crops; no repeating texture or camera-relative UV is introduced.

Environment registration should provide exact original key, pack, frame_index, cell, layer, sort_y, stable_source_order and source_cell, plus high-density texture path/SHA/dimensions, logical world_top_left and common scale. Building fragments must preserve raw pixels once and source ordering. Ground is a separate 64-placement sample with original rectangles/alpha; it must not be treated as a background covering object ordering. Actor interfaces require complete approved source-frame mappings and density/anchor units. New Earth illumination must be reviewed independently; the retired courtyard cast direction must not be reused by assumption.

## Fresh verification on 2026-10-15

- Headless startup and mapping/source-flags/A* test passed.
- Actual native window 1152×768: click mapped to logical `(432,320)`, cell `(61,40)`, and actor arrived.
- Actual resized window 998×698 with visible top/bottom letterbox: click mapped to logical approximately `(431.7114,287.9519)`, cell `(61,39)`, and actor returned.
- Candidate raw SHA: `60f89f65dd817ec80065de941e62e36e1068302c3f2bc4eb5014d8d56f450c02`. The source and independent 1×/2× body-only diagnostic ran two complete 12-tick loops including 16→13. The same fixed map point repeated both loops, then an original A* move used source frame 58 and arrived at 61,40.
- Ordinary-entry B toggle was checked visually. Candidate preparation/fallback/recovery passed 128 checks. Empty-cache import of the newly added actor PNG and the same tests are recorded in the stage handoff. These internal images are not a claim that the new environment style is complete.

Original movement speeds and animation schedules retain their documented reference-adaptation boundary; this stage does not establish new original-EXE timing evidence.

## Ground v2 bounded native stage

Registration `assets/earth/environment/ground_plate_v2/registration.json` uses 64 exact source identities. Its source review measured six curb centers within approximately 2.5 logical pixels (manual source uncertainty ±3); this is an art-layout tolerance, not a collision alteration. All flags remain original. Shared full-plate PNG is provenance/optional comparison data, not loaded by this renderer. No new ground or actor shadow is added.

Actual GPU captures at 768×512 and 1536×1024 compare the same SE frame13 and world rectangle with ground on/off. Four original A* legs 61,39→66,35→61,39→61,43→61,39 completed 576 movement ticks; moving and unsupported idle directions visibly use original body/head. No piece seams were apparent in the reviewed joint image. Source building/vegetation/checker shadows remain visible and must not be described as the completed Earth style. Ground malformed/preparation/recovery checks: 101 PASS; actor regression: 128 PASS.

Parent review accepts this as an engineering candidate checkpoint only: grass scale/frequency still attracts too much attention and its visual design is not approved. The new 64 PNGs were imported into the existing isolated source-stage checkout with no previous cache for these textures; the 101 checks passed there. This is an incremental fresh-texture import, not a claim of rebuilding every historical resource cache.
