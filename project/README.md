# Coastal Daydream · Pelican Ride

## Interim local-test build · 2026-10-13

This is a testable work-in-progress checkpoint. Art refinement continues separately; this is not a final release or a claim that the visual target has been achieved.

Tested with **Godot 4.6.3 Standard**, using the GL Compatibility renderer. The project declares Godot 4.6 compatibility. Import `project.godot`, let the first asset import finish, and press **F5**. The committed GLB files are ready to use; Blender is only needed to edit and re-export the source. See [Windows local-test instructions](docs/LOCAL_TEST_WINDOWS.md) or [中文开始使用](开始使用.md).

The verification computer used CPU software rendering. Its measured FPS does not predict performance on your GPU; test that locally. The included MP4 is an offline native frame render, not a real-time performance recording.

Fresh native Godot 4.6 coastal scene, built around a Blender-authored little pelican and bicycle.

Open `project.godot` in Godot 4.6.3 and press F5, or run `godot --path /path/to/pelican-toon-coast`.

Ordinary startup opens the current portrait look with painted feather/terrain materials, dense authored foliage, canopy and shoreline ivy. No preview flags are required.

For the lower-cost software-rendering preview, run `godot --path . -- --software-preview --compact-preview`. It keeps the same art but uses FXAA, lower-resolution shadows and a 960×600 window.

## Controls

- Space: pause/resume
- +/− or Up/Down: pace
- 1/2/3: postcard/follow/portrait camera
- Mouse drag: bounded presentation orbit; wheel: gentle zoom
- R: reset to the portrait view
- F12: save the actual native viewport to `captures/toon_coast_camera1.png`, 2 or 3

The small bottom control strip is clickable. Pause stops pedaling, wheels, water and foliage together; camera navigation stays available. This is a compact illustrated ride loop, not an explorable world or bicycle physics simulator. Camera motion stays within the authored presentation side. The demo is silent.

## Sources

- `source/`: editable Blender source and authoring/export notes
- `assets/coastal_ride.glb`: the complete authored scene mesh library
- `assets/foliage_card.glb`: the same Blender-authored bowed foliage template as a standalone library
- `scripts/`: fresh runtime, toon material assignments and native HUD
- `shaders/`: material-family cel shading, selective colored silhouette, depth-contact water and sky
- `assets/textures/`: newly generated painted material images and provenance
- `docs/RENDERING.md`: rendering decisions and verified official Godot references
- `tools/`: deterministic native engine preview recording and MP4 encoding

## Checks

Run `sh tools/check_project.sh` for all technical checks, including authored-card placement, batching, UV materials and complete eye-assembly blink. Additional runtime arguments may be appended for a look-development variant. Native visual review is separate.

```
godot --headless --path . --editor --import --quit
godot --headless --path . --script res://tests/runtime_checks.gd
godot --headless --path . --script res://tests/material_checks.gd
godot --headless --path . --script res://tests/composition.gd
godot --headless --path . --script res://tests/coast_checks.gd
godot --headless --path . --script res://tests/texture_checks.gd
godot --headless --path . --script res://tests/ao_checks.gd
godot --headless --path . --script res://tests/water_checks.gd
godot --headless --path . --script res://tests/presentation_camera_checks.gd
godot --headless --path . --script res://tests/look_profile_checks.gd
godot --headless --path . --script res://tests/planting_checks.gd
godot --headless --path . --script res://tests/atlas_checks.gd -- --planting-preview
```

Use actual engine captures to judge visual quality; passing headless checks alone does not establish that the scene looks correct.
