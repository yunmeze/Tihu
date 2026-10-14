# Blender asset workflow

`pelican_coast.blend` is the editable source. It was built in Blender 4.3.2 through the native desktop interface. The pelican is an original chibi character; the included concept images set proportions and color direction.

## Authored geometry

- The head, body, bill and pouch use editable surface meshes, deliberate mesh reshaping and smoothing. The bill has a broad rounded planform and the pouch has a continuous convex lower surface.
- Six swept side-head feather lobes were joined to the head, voxel-remeshed in native Sculpt mode, and blended with explicit smoothing-brush strokes and mesh smoothing. Later native Draw, Grab, Flatten and Smooth strokes formed four broad down-swept crown/cheek groups on that connected surface. Two groups extend into the portrait-facing side contour with blended roots. A face mask protects the eye and bill area; the later sculpt preserves the established topology, UV coordinates and object origin.
- Each eye has a dark inset base, a warm amber iris, a smaller dark pupil and a restrained cream catchlight. Same-side components share an origin so the runtime blink keeps the assembly aligned.
- The wings began as clean closed, manually extruded cross-section lofts sweeping from shoulder to grip. Three differently sized and angled rounded feather tiers were reshaped, joined, voxel-remeshed in native Sculpt mode, and blended into one connected mesh per wing. Native proportional edits turn and broaden the shoulder fan while the hand-end vertices remain fixed against the grips. Mirrored source shapes have applied transforms and outward normals. The two unequal swept crest tufts retain tapered, edited Skin/Subdivision cages.
- A fine bill lip follows a duplicated, rounded middle perimeter of the edited bill. Three swept, overlapping tail feathers reuse and reshape the authored loft cage at different lengths and angles.
- Webbed feet use a connected lobed outline, thickness and rounded edges. Leg rest meshes are 0.32 units along local Blender Z for the runtime's two-segment cycling pose.
- The frame and fork were built with successive cross-section extrusions. Tires, rims, spokes, hubs, saddle, steering supports, grips, pedals and crank parts remain separate editable mechanical meshes.
- A toothed crank chainring, closed chain with straight tangent runs, brake lever and routed cable add readable mechanical construction. The chainring rotates with the crank; the cable and chain remain fixed.
- The coastline begins with an individually positioned polygon outline, extruded into a vertical cliff and a thin grassy ledge. The sand path is a manually extruded cross-section strip, with an S bend edited into its control cage.
- The headland and shoreline rocks use successive shaped ring extrusions, restrained edge bevels, and varied proportions. The tapered lighthouse has a banded tower, cornice, lantern, posts, roof and inset door.
- The lighthouse has a beveled balcony ledge, eight seated balusters, a continuous rounded rail, two inset framed windows and a two-level entry step.
- Foliage begins with curved, tapered blade surfaces; blades are arranged into fans and a broader foreground shrub. Daisy petals use a shaped radial outline with thickness, plus separate centers and gently bent stems. The distant land silhouettes and headland footpath are editable meshes.
- The lowest headland and near backing-wall base vertices extend to Z = -2.60, beneath the animated water surface and shallow-color transition, while their above-water silhouettes remain fixed.
- The first headland buttress has a tapered lower shoulder that overlaps the backing cliff. Its waterline was checked at the lowest, closest side-camera extreme to remove an abrupt rectangular shoreline step.
- A rising cape connects the near path to the lighthouse using individually rotated cross-sections. It has a separate grass surface, vertical rock mass, and widened submerged shelves for real water-depth transitions.
- Curved fern fronds are built from paired, tapered leaflet surfaces arranged in decreasing sizes along a bent stem. Several fronds form an overlapping clump. Staggered shoreline stacks use deliberately offset and rotated ring sections, small ledges and restrained bevels. Their rock palette stays continuous across triangulated ledges to avoid false diagonal color bands.
- Rounded broadleaf shrubs use curved, subdivided leaf surfaces with lifted center ribs, an edited branching woody stem, and different canopy scales. They are composed with fern fronds, daisies and rock outcrops into foreground, bank and cape groups.
- The near grassy bank has native proportional-edit height shaping, with foliage and rock bases seated against its actual surface. Low overlapping leaf cover, ferns and taller shrubs form uneven three-height groups.
- Unequal broad rises and a shallow hollow shape the near bank. The path has a modest crown outside the central tire-contact zone and individually widened or worn shoulders. The inner cape has three differently tapered bank spans, with its grassy surface and supporting cliff edited together and a flared lower toe.
- Two foreground shore rocks have individually bisected, filled sloping planes and a restrained chipped edge, replacing their matching flat caps. The cut planes receive a slightly warmer exposed-rock color.
- Two unequal inner-cape boundary spans extend into rounded earthen shoulders, with a small exposed break between them. Each continues beneath the water, rather than ending in a floating surface. Their join is softened by two editable subdivision levels. Grass stays on the upward lip; the steep shoulder rows use exposed-rock material, with small rooted foliage groups bridging the transition. The two large portrait-facing buttresses have separate irregular recessed seam strokes and adjacent flattened planes, sculpted after native linear subdivision. A lower-vertex mask protects the repaired shoreline; the original lower points were checked against the preceding source after the sculpt pass.
- The upper bill crown was thickened around its unchanged lip into a broader arch; nostrils were reseated against the evaluated surface. Native Grab, Flatten and explicit Smooth brush strokes add restrained cheek fullness, a broad facial plane and a downward sweep to the existing side-head feathers. This sculpt pass preserves the head's topology, UV coordinates and object origin.
- Three additional interlocking low-cover and fern groups extend the near planting into a continuous irregular bank. Smaller low cover follows the cape rail and seats the landmark bases.
- A wind-shaped headland tree uses a manually extruded branching cage, tapered branch radii, and interleaved overlapping clusters of curved broad leaves, with low cover concealing the grounded trunk base. Whole-leaf color assignment follows connected surface components rather than cutting a leaf across a height threshold.
- A short wooden coast rail follows seven individually seated posts along the headland bend. Both continuous rails are manually extruded curved cages, with rounded cross-sections and a lower second rail.
- A gently bowed 25-vertex foliage card was edited in Blender with a full UV map and a bottom-center origin. The runtime instances this mesh with cropped original atlas artwork, alongside smaller instances of the authored leaf, fern and flower meshes. Placement uses ground-surface checks and road-clearance masks; no replacement primitive geometry is generated.
- Blender coordinates are X forward, Y lateral, Z up. glTF converts this into Godot Y-up coordinates.

## Feather-flow UV contract

The principal `PelicanHead` and `PelicanBody` surfaces have native spherical UV projections authored from the forward (+X) view, centered on their object origins, with fan poles and no aspect correction. The front is U = 0.5, the near side (-Y) is U = 0.25, the far side (+Y) is U = 0.75, and the rear seam is U = 0/1. Blender V = 1 is the crown; glTF flips V so the top row of the 2:1 painted image is the crown. The source-only UV pass was checked against the prior source: mesh positions, polygon indices and transforms were unchanged.

The head has a small wrapped UV region at the pole; horizontal repeat is intentional. Keep the crown, bottom pole and central face visually quiet, and put broad feather-flow accents around the sides and lower collar. The original painted map is `assets/textures/pelican_feather_flow_0832.png`; runtime blending controls its contrast. This material treatment does not alter the authored silhouette.

## Utilities

`materials_export.py` assigns source material colors, assigns a few named face-color zones, sets shading flags, saves the source, and exports its existing evaluated geometry to `../assets/coastal_ride.glb`. It does not generate replacement mesh geometry.

The runtime creates transform pivots for imported wheel, crank, foot and limb assets. It does not create substitute visible primitives.

## Re-export

Save `source/pelican_coast.blend` after editing. From the project folder, use the validated export pipeline:

```sh
python source/export_assets.py
godot --headless --path . --editor --import --quit
```

`export_assets.py` first applies the authored palette, then uses a temporary evaluated snapshot to bake restrained scalar vertex AO. It checks that source bytes, geometry, transforms and materials are preserved before installing the final GLB. Articulated legs, feet, pedals and eyes receive neutral white AO. The same command also exports the existing UV card to `assets/foliage_card.glb`. Editable Skin/Subdivision cages remain in the `.blend`. The temporary bake does not generate replacement geometry.

`materials_export.py` can still be run alone for a quick unbaked preview, but use the complete pipeline for the production asset.

The export utility resolves paths relative to the saved `.blend`, so the whole project folder is portable. The `source/.gdignore` marker prevents Godot from automatically importing the editable Blender source in addition to the exported GLB.
