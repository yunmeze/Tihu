# Coastal Daydream · Pelican Ride

Fresh native Godot 4.6 coastal scene, built around a Blender-authored little pelican and bicycle.

Open `project.godot` in Godot 4.6.3 and press F5, or run `godot --path /path/to/pelican-toon-coast`.

Ordinary startup opens the accepted portrait look with painted feather and stone-plane materials, worn road margins, dense authored foliage, canopy, shoreline ivy, organized swells with broken rock surf, and detailed cumulus clouds. No preview flags are required. The explicit comparison flags `--no-surf`, `--no-stone-surface`, `--no-road-wear`, and `--no-sky-sector` restore the preceding layers independently. Pass runtime flags after `--`.

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

## Import and startup

Use Godot 4.6.3 Standard to import project.godot, wait for resource import, then press F5. Test scripts, captures, caches and backup files are intentionally excluded from this source distribution.
