# Organized swells and authored-shore surf candidate

The 2026-10-13 sea refinement is enabled in ordinary startup after native
three-camera, repaired-shoreline and sampled-motion review. `-- --no-surf` selects
the byte-preserved earlier `coastal_water.gdshader` rollback. The explicit
`-- --surf-preview` flag remains available for diagnostic lighting profiles.

## Technique

- `coastal_surf_water.gdshader` retains Compatibility world-depth reconstruction,
  upward-seabed gating, and the narrow depth-contact mask.
- Warped asymmetric wave faces provide turquoise leading planes and deeper blue
  troughs. Smaller crest accents follow the same phase and have unequal spatial
  breaks rather than one continuous contour or evenly spaced dashes.
- Distant displacement fades to zero before the horizon. Color, surf and fine
  highlights have independent distance falloffs.
- Sky reflection remains bounded. A restrained extra specular region uses the
  actual directional key vector and analytic surface normal.
- `ShorelineField.gd` intersects transformed authored cliff/shore-rock triangles
  with the mean sea height (-0.72 m). It rasterizes minimum world-XZ distance into
  a 384-square linear float scalar texture, capped at 2.8 m. The shader uses this
  field for textured surf within approximately 1.55 m of actual shore, independent
  of camera-projected submerged wall silhouettes. No visible geometry is created.
- The field is cached in the normal Godot user-data directory by source GLB hash
  and algorithm version (currently 2, adding material-based mixed-slope support).
  Reimport the source GLB after a Blender export before running the scene. New
  source exports automatically get a new field. Its border is fully faded, so
  clamped sampling cannot produce a rectangular foam boundary.
- Original `ocean_foam_current_0928.png` is sampled as red-channel scalar data,
  without `source_color`, with mipmaps and repeat. Its generation prompt and pixel
  provenance accompany the texture. It is not a commercial-game asset.

## Evidence and limits

`captures/surf_compare_0933` and `captures/surf_compare_0944` contain actual native
paused-camera A/B pairs plus source/shader fingerprints. Geometry, lighting,
camera and time are identical within each pair; only the water material changes.
The second pair established the broader swell hierarchy. Crest-only breakup was
then reviewed in `captures/surf_regressions_0948`, containing three presets, the
previously failing exact shoreline-corner view and three later animation phases.
`captures/surf_regressions_1022` confirms the final earlier far-wave contrast fade
on the subsequent authored source revision. The fade spans 14–36 metres and leaves
the local surf masks unchanged.

The three-second motion check is a native offline Movie Maker render, not a
real-time FPS claim. The CPU software-renderer limitation still applies. The
11:13 UTC ordinary wall-clock profiles with the new shader measured 3.75 FPS in
quality mode and 9.17 FPS in compact preview on llvmpipe; see `VERIFICATION.md` for
the source fingerprints and the limited scope of those CPU-host measurements.

The shoreline field approximates contact at the mean water level, while the
original depth mask provides immediate animated contact. It represents only
authored static shoreline objects with Cliff, RockShore or RockStack name prefixes,
plus rock/stone/earth material surfaces on mixed meshes such as GrassCape. Distant
backdrop meshes are excluded. The 11:09 source contributes 992 intersections,
including 88 from GrassCape's lower stone slope.
It is not a fluid simulation, a dynamically updated collision field, SSR or local
object reflection. If shoreline objects become articulated, extend the field
contract rather than letting their cached contact remain in a rest pose.

`tests/shoreline_field_checks.gd` verifies float-data range, faded borders, imported
mipmaps and retained depth protections. Headless checks cannot establish visual
quality, temporal shimmer or absence of every camera-dependent artifact.
