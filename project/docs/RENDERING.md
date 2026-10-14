# Stylized rendering implementation

All visible 3D meshes are Blender-authored resources in `assets/coastal_ride.glb` or its standalone `assets/foliage_card.glb` template library. The runtime creates no replacement primitives, CSG, ArrayMesh, ImmediateMesh, or procedural terrain geometry.

## Character materials

`coastal_toon.gdshader` keeps the authored albedo and uses native ambient plus two softened direct-light bands. Real light attenuation and cast shadows remain active. Small material-specific native fill inputs tint ivory shadows cool and keep pouch shadows warm orange; direct-light gains compensate so illuminated areas stay bounded. No whole-image exposure boost or screen-wide outline filter is used.

Highlight strength and size distinguish matte feathers/rubber from bill, painted frame, metal and eyes. `colored_outline.gdshader` is a subpixel-to-one-pixel inverted-hull pass only on principal hero shapes. It reuses the imported mesh and uses tinted contours. The restrained narrow ivory rim is key-facing; broad white halos are avoided.

Native color review is performed on the actual Godot viewport, with the lit ivory, cooler shade, orange pouch shadows and eye catchlights checked together. Head-patch clipping checks supplement visual review; they do not establish correctness for every possible camera or light configuration.

The principal head/body use a new original feather-flow albedo mapped by Blender-authored sphere UVs with a rear seam and clean facial region. A measured neutral-color ratio adds bounded pigment only; it never increases light or exposure. Mipmaps and horizontal repeat handle the authored seam coordinates. Both beauty and rear views were checked natively.

The same aligned image supplies a restrained, low-frequency normal response at strength `0.004`. Four explicit LOD samples estimate the broad pigment gradient, with a derivative-derived tangent frame because the imported meshes do not contain tangents. The central face, poles and rear wrap seam are masked; the normalization is resolution-invariant. This changes shading only, never silhouette or vertex position. `--no-feather-relief` restores pigment-only feathers. The native comparison under `captures/feather_relief_corrected_1050` showed a small craft gain rather than a large style change.

The principal bill and mint-painted bicycle have separate narrow warm highlights (`0.48` and `0.52` strengths), while feet, pouch and feathers keep their matte response. Shared source colors cannot transfer the bill's sheen to feet/legs. The ivory key-facing edge response is bounded at `0.17`. `--no-material-finish` restores the preceding material response. The isolated native pair is under `captures/material_finish_1050`; lighting, exposure and geometry were held fixed.

The rock family also has a separate original broad-plane image, mapped at `0.30`
world scale with `0.58` influence. It supplies oblique medium-scale seams and
subtle chipped accents; the earlier image remains subordinate fine pigment.
Both use measured source-color means, preserving each authored stone palette.
Mipmapped beauty, rear, motion-phase and shoreline-corner proofs are in
`captures/surface_mipped_1132`. `--no-stone-surface` restores the earlier stone.

A sky-resolution diagnostic compared 128- and 512-pixel radiance cubes with fixed
native portrait frames. The images were pixel-identical, so the ordinary 128
setting remains. See `captures/sky_resolution_1142`. Radiance resolution is not a
substitute for source panorama angular detail ([Godot Sky documentation](https://docs.godotengine.org/en/4.6/classes/class_sky.html)).

## Coast and atmosphere

`coastal_painted_toon.gdshader` uses world-space triplanar sampling for the generated painted stone, grass and sand images. Each is normalized around its measured sRGB mean and mixed with the Blender material color, keeping that palette authoritative. Mipmaps and anisotropic filtering reduce distant shimmer. Large procedural pigment fields are disabled on these textured terrain surfaces. Leaves retain their authored color zones and gentle spatial variation.

The texture images and exact generation provenance live in `assets/textures/`. They are newly generated material art, not commercial-game assets. Their edge differences are small but not mathematically zero, so the low-contrast mix and actual native tiling review matter.

Authored leaves, ferns and flower parts receive a small height-anchored vertex bend. The same ride clock drives water and wind; pause freezes all of them. Ground shelves, cliffs and buildings are not moved by wind.

`distant_land.gdshader` gives distant authored silhouettes a restrained, low-contrast atmospheric treatment. This avoids an unnaturally dark underside at the pale water horizon. `pastel_sky.gdshader` mixes an original painted cumulus panorama with the pale-to-blue gradient. Azimuth and elevation mapping place cloud groups in the visible sky, while the horizon stays quiet. Explicit panorama LOD sampling avoids the false coarse-mip seam at the angular mapping discontinuity. The sky texture does not contribute to native ambient lighting, preserving the verified character palette. Its source and prompt are documented in `assets/textures/SKY_PANORAMA_PROVENANCE.md`.

## Water

`coastal_surf_water.gdshader` runs on the authored Ocean mesh. It combines asymmetric turquoise wave faces and blue troughs, uneven clustered crest highlights, a restrained reflection of the painted sky, distance haze and broken shore surf. `ShorelineField.gd` builds a cached scalar distance field from the actual authored shoreline triangles, allowing porous foam to spill locally around projecting rocks without tracing every screen-depth edge. The previous `coastal_water.gdshader` remains available with `-- --no-surf`. See `WATER_LOOKDEV.md` for field bounds, provenance and native comparison evidence.

Both shaders retain world-space depth reconstruction and the upward-seabed slope gate. Steep submerged walls are excluded from shallow tint so finite wall silhouettes do not become detached cyan cuffs. The full shallow fade ends at one metre and immediate scene-depth contact occupies only 0.085 metres. The richer shader adds world-space surf within approximately 1.55 metres of actual mean-level shoreline intersections. This is a stylized contact approximation, not a fluid simulation. Submerged shelves still need continuous authored geometry and multi-camera native review.

The material uses an opaque-looking transparent pass to access scene depth, with correct Compatibility NDC reconstruction. It does not use refraction or screen-space reflections. It manages its own distant color fade, so native fog is disabled on the water to avoid a second dark horizon band.

## Contact shading

Godot 4.6 Compatibility supports a simplified SSAO implementation with Radius and Intensity controls. `-- --ao-preview` enables a restrained native A/B candidate (radius 0.18, intensity 0.55); the native comparison showed negligible benefit for this scene, so normal launches leave it off.

The production GLB carries scalar baked AO in `COLOR.r`, generated on an evaluated export copy without changing the editable source. Strength is limited to 0.22 on the hero and 0.12 on mechanical materials, and albedo/fill are multiplied once. Native A/B review accepted subtle bill-root, wing and bike overlap separation while keeping the large cream surfaces clean. `-- --no-vertex-ao` disables it for comparison.

Static assembly groups are baked separately from articulated joints. Legs, feet, pedals and eyes retain neutral white data to avoid rest-pose contact ghosts. `tests/ao_checks.gd` verifies bounded grayscale data on every imported surface, actual local contact values on the head and neutrality of those animated parts. The source authoring/export notes describe the copy-only bake.

## Presentation camera

The three presets share a bounded presentation-side orbit, modest elevation limits and gentle zoom. The side angle remains accessible so the layered wing and bicycle read clearly. Camera switches interpolate direction and distance separately, with a smoothly moving target, rather than taking a straight chord through the rider. `presentation_camera_checks.gd` samples the extrema and all preset transitions; native checks must also confirm that terrain edges and occlusion remain intentional.

## Painted foliage cards and placed cover

`CoastalPlanting.gd` places deterministic, art-directed clusters of existing Blender mesh resources. It queries the transformed authored terrain and road triangles with a spatial grid, reserves a road margin and an open hero corridor, and limits added solid triangles. It creates placement nodes and MeshInstances only. The inexpensive bowed card comes from the Blender-authored `FoliageCardTemplate` in `assets/foliage_card.glb` or the complete scene export; it is not a generated quad.

`foliage_atlas.gdshader` uses the original RGBA atlas, exact measured tile rectangles, per-tile root corrections and alpha scissor at 0.45. Shared tile/tint materials support double-sided lighting and root-anchored wind driven by the ride clock. Texture mipmaps and native alpha-border import handling are enabled. The unmodified source contains low-alpha green fringe, so unrestricted blending is intentionally not used. Actual native cutout/mipmap review is required in addition to the numerical alpha checks. Generation provenance and mapping are in `assets/textures/FOLIAGE_ATLAS_PROVENANCE_0724.md` and its JSON companion.

The accepted planting, small-leaf canopy, ledge ivy and shared-resource MultiMesh batching are enabled in ordinary startup. Original source nodes remain indexed but their draw is hidden after exact-transform batching. `-- --no-planting`, `-- --no-canopy`, `-- --no-ledge` and `-- --no-batch` provide diagnostic comparisons. For a packaged Godot export, use Export all resources or explicitly include the atlas JSON, selected PNG, and authored card GLB; string-loaded metadata dependencies must not be omitted by an Export selected scenes preset. The source-project package includes them directly. Do not treat headless placement tests as evidence that density, card angle, or silhouette integration is visually accepted.

## Look-development profiles

Ordinary startup uses the accepted warm look: lower cool ambient, stronger warm directional light, material-specific bounded fills and differentiated bill/paint/metal highlights. Native exposure stays 1.0. `-- --look-cel` is a diagnostic graphic-band comparison; it was rejected for the harsh forehead stripe and is not the production style. `-- --baseline-look` retains the unplanted, preaccepted lighting rollback. Other explicit preview flags remain useful for isolated comparisons. Native captures of alternatives are diagnostic, not delivery images.

## Verification

Headless checks validate runtime controls, material bindings, original imported mesh resources, foot/pedal bounds throughout the cycle, pause clocks, texture imports, AO data and camera bounds. They do not establish GPU color, silhouette, tiling, contact foam or motion quality. Native screenshots and Movie Maker output are reviewed separately; see `NATIVE_CAPTURE.md`.

This is an original compact stylized scene using anime-game rendering principles. It does not recreate a commercial game's proprietary rendering or establish a numerical percentage of its production quality.

## Official references

- Spatial shaders: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html
- Compatibility shader pipeline and fragment/light color conversion: https://github.com/godotengine/godot/blob/4.6-stable/drivers/gles3/shaders/scene.glsl
- Depth reconstruction and Compatibility NDC: https://docs.godotengine.org/en/4.6/tutorials/shaders/advanced_postprocessing.html
- Fragment derivative functions: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/shader_functions.html
- Depth/screen textures: https://docs.godotengine.org/en/4.6/tutorials/shaders/screen-reading_shaders.html
- Compatibility SSAO: https://docs.godotengine.org/en/4.6/tutorials/3d/environment_and_post_processing.html#screen-space-ambient-occlusion-ssao

- Alpha cutout and double-sided shader inputs: https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html
- Texture mipmap and alpha-border import: https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html

## Native profiling

`tests/native_frame_profile.gd` is graphical-only wall-clock measurement, with three seconds of warm-up and twelve seconds of sampling. Reports include adapter/driver, render counters, viewport, source and GLB hashes. Movie Maker/fixed-FPS runs are rejected. Actual performance is hardware-specific.

On the verification desktop, the adapter is Mesa llvmpipe (LLVM 19.1.7), a CPU software renderer. Early same-asset diagnostic passes measured 3.83 FPS unbatched versus 3.98 FPS batched, despite draw calls falling from 2,652 to 1,338. Removing MSAA or shadows separately roughly doubled speed. Those diagnostic records predate final feather/default promotion, so they are not final-candidate benchmarks.

`-- --software-preview` uses FXAA and a 2048 shadow atlas with low-cost filtering; `--compact-preview` additionally requests 960×600. Both retain the authored meshes, planting and materials. The normal mode retains 4× MSAA and 4096 shadows. Offline Movie Maker frames are never evidence of real-time FPS.
