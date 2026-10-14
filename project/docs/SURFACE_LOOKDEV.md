# Surface-detail development

These are native-engine comparisons and original project art, not a quantified
comparison to any commercial game. Scene geometry, camera, time and lighting
were fixed within each A/B pair.

## Broad stone planes

`coastal_stone_planes_1110.png` adds readable oblique divisions to the large cape
faces. Its encoded RGB mean is 209.272/153.068/117.843; the source-color sampler and
mean uniform are converted consistently by Godot, then used as a bounded ratio
around the authored rock color. This avoids importing the image's orange bias.
Current strength is 0.58, world scale 0.30, with triplanar sampling and mipmaps.
The original finer stone pigment remains a separate subordinate layer.

Native comparisons: `captures/stone_planes_1115`; mipmapped cross-view, phase and
repaired-waterline proof: `captures/surface_mipped_1132`. The latter also contains
the corrected sloping earth shoulder and two narrow three-card grass/ivy
transitions. Every transition root is resampled on actual GrassCape GrassGreen
triangles. RockPeach faces are excluded from ordinary planting ground.

The stone layer is enabled in ordinary startup. `--no-stone-surface` restores the
preceding fine-pigment-only response. The original generated PNG and its prompt,
provenance and numerical review are retained under `assets/textures` and
`assets/provenance`; image bytes were not edited.

## Road margins

The roads have constant imported UVs, so UV distance cannot identify their edges.
`RoadMarginField.gd` derives the world-XZ union boundary of the actual authored
upper road triangles. It welds shared positions, discards internal triangulation
edges and removes overlapped joins. The current 352 triangles produce 98 boundary
segments. No visible geometry, collision, planting clearance or source mesh changes
are made by the helper.

Its 768-square linear RF texture stores distance in metres, capped at 1.5 m. The
cache includes source GLB hash, road transforms and algorithm constants. Saturated
borders and texel-centre UV mapping avoid rectangular cutoffs. The test covers
overlaps, adjoining roads, quiet centres and cache determinism.

The original sparse painted gravel image is bound only near road edges, with
unequal broad patches and a quiet centre. A separate narrow dust blend extends at
most 0.18 m onto adjacent grass. It does not scatter pebble meshes or alter the path
silhouette. Comparisons are in `captures/road_wear_1135` and
`captures/road_wear_1140`; the latter increases only local chip contrast/scale and
adds the narrow dust transition. The 11:40 version was visually accepted and
promoted to ordinary startup; `--no-road-wear` is the explicit rollback.

Do not equate the numeric field tests with visual acceptance or runtime smoothness.

## Sky resolution diagnostic

Native 128- versus 512-pixel radiance-cube portrait captures were pixel-identical
(`captures/sky_resolution_1142`). The project therefore retains 128. The original
1774×887 full-sphere image has limited angular detail; a larger reflection cube
does not recover missing source pixels in this Compatibility background path.

## Higher-angular-resolution sky sector

`coastal_sky_sector_1145.png` is an original 1774×887 painted sky image, projected
onto an 80° × 40° world-direction sector rather than stretched around the full
sphere. This recovers source pixels per visible angle without enlarging the
radiance cube. A blue opening frames the face, with rounded cloud groups at the
sides. The selected strength is 0.86; grading reduces saturation slightly, with
smooth side, upper and horizon fades into the preceding panorama. The rear view
outside this sector retains the original panoramic sky. This is intentional
world-space art direction, not a camera-locked backdrop.

The first wide/short mapping (`sky_sector_1157`) was rejected for stretched cloud
ribbons. The proportion-corrected `sky_sector_1200` pair was accepted for boundary
review. The 24 native extrema in `sky_sector_grid_1203` cover its projection and
blending across the allowed camera space. A same-host ordinary wall-clock pair
measured 3.385 FPS without the sector and 3.381 FPS with it (median 292.216 and 293.882
ms). This short CPU-renderer observation shows no material measured cost change;
it does not establish smooth performance or predict GPU hardware performance.

Original image provenance, exact prompts and checksum are under
`assets/provenance/coastal_sky_sector_1145.*`. No generated pixels were edited.

The sector is now enabled on ordinary startup. `--no-sky-sector` restores the
preceding panoramic sky and overrides positive preview flags. The 218-frame,
9.083-second native orbit render covers three bounded sweeps. Eight extracted
transition samples were reviewed without a hard border or wrap line. This is
appearance evidence, not exhaustive every-frame temporal review or real-time FPS.
