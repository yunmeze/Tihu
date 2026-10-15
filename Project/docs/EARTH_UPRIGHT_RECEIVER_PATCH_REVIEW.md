# Upright-tree receiver patch review, source RGBA only

## Result and current decision

The two proposed605×190 world patches have complete, non-overlapping opaque source-floor coverage. All126 source Building owners and379 Wall owners were checked globally with the actual renderer's crop/top placement, with no missing frames; none of their frame rectangles intersects either review patch. This does **not** establish one flat receiver across every visible material.

- Left patch Rect(2319,1311,605,190): grass transitions across a diagonal stone-edged dirt road. The complete shadow traverses both terrain tile families. The curb's true elevation is not supplied by the source bitmap or collision flag. Keep this cast disabled until that boundary is explicitly accepted as a coplanar decorative border, or represented by supported separate geometry. Do not cut its shadow at the curb.
- Bottom patch Rect(2847,1631,605,190): opaque grass FloorBig406 throughout. Three Debris pieces are a stone-rimmed pool/depression with grass/soil aprons. The nominal full shadow directly touches only49 source texels in the upper grass/soil apron of Debris58, not the visible stone/water core. This makes a semantic refinement plausible, but it is not an approved receiver or an automatic reason to drop the whole Debris owner.

Both casts remain off under the current sample-bound receiver. No runtime mask, renderer, source art, current four-caster contract or shadow geometry was changed by this review.

## Exact map/frame evidence

Source map A13 uses x-major order x*100+y. Review inventory is a full-map rendered-frame scan, not an owner-cell rectangle search. The frame origin for these non-NPC objects is cell*(48,32)+crop+(0,32-original_height). Floor top is0. No frame.offset is applied. Source floor records have negative floor IDs mapped to FloorBig and absolute frame ID. Each review patch has114950/114950 floor pixels at alpha255, maximum coverage1, no gaps or overlaps.

| Debris | Map cell / order | Original source cell | Source rendered bounds xyxy | Positive pixels within bottom605×190 patch | Full nominal shadow direct cells / +4 cells |
|---|---|---|---|---:|---:|
|57|(66,62) /6662|[-406,1,1,57]|[3168,1803,3216,2015]|393|0 /153|
|58|(67,63) /6763|[0,1,1,58]|[3216,1800,3264,2041]|800|167 /855|
|59|(68,63) /6863|[0,-2,1,59]|[3264,1813,3312,2048]|75|0 /0|

All listed positive pixels have alpha255. These are genuine opaque material pixels, not low-alpha noise. Source flag1 places57/58 in draw layer0; flag−2 also places59 in draw layer0 according to layer_for_flag (flags1 and−2 both map to0). Those layer tags and blocked/walkable flags alone are not physical height labels. All three AABBs intersect the expanded review window and all have actual RGBA there; relative to the **nominal shadow**,57/59 have no direct material overlap,58 does. No “AABB-only” finding should be generalized from one query shape to another.

Debris58 direct contact list is archived in debris-contact.json:49 source texels, local x7–36,y0–6, world x3223–3252,y1800–1806. Four quarter-pixel sample cells per raw texel are not necessarily all covered, hence167 envelope cells rather than196. The diagnostic top crop marks exactly these49 texels red; surrounding source pixels show grass/soil. The stones and dark pool below must remain physical exclusions. Debris57 enters only the conservative4logical expansion. Debris59 is outside even that nominal expanded intersection.

## Material and reception interpretation

Left source floor IDs406 plus577,581,586,587,594,595,604,608 form grass, road and the diagonal stone border. Full shadow overlaps non406 tiles, so the “grass only” interpretation is false. The source-floor layer provides continuous paint, but cannot tell whether the stone border is a raised curb. Inspecting a whole floor tile as opaque does not make its entire area a step, either. An exclusion traced along real border material, with the existing4logical clearance, is the smallest sensible conservative candidate; a whole-tile exclusion is a safe but much larger approximation. A crossing cast must fail as a whole if it hits that exclusion.

Bottom floor406 is a plausible flat grass receiver away from the pool. Debris57–59 combine material classes in one frame: visible grass apron, raised stone perimeter, dark depressed water and foreground details. A future explicit mask may retain real stones/water/vertical rim and4logical clearance while treating **reviewed coplanar apron pixels** as ground. This requires a source-backed per-frame semantic trace; no alpha threshold distinguishes these all-opaque materials. Keep unclassified pixels forbidden. Do not remove an entire owner or all layer1 material. The49 nominal contact texels are evidence for reviewing the apron, not a license to exclude every green/brown pixel.

The fixed root remains raw(560,1329), density4.5, with registered raw uncertainty±9px and source uncertainty±4logical. The recommended review margin10logical was derived from these uncertainties. Even though nominal contact lies above the visible stone core, an unreviewed uncertainty neighborhood may reach the rim. Exact stone-boundary clearance has **not** been certified here; a final traced material mask and distance calculation are required before choosing whether the bottom cast can pass.

Source object aprons are drawn after the ground shadow. A coplanar apron can visually cover a physically valid shadow; that is a draw-order/art-composition limitation, not proof that it is raised. Likewise tree/shrub canopy screen overlap is not itself a ground receiver. This review does not infer reception solely from later screen occlusion and does not alter body pixels or source checker suppression. Candidate/source toggles require exact current owner/resource checks and safe whole-cast fallback.

## Minimum next bounded proposal

1. Retain the two disconnected world windows rather than enlarging the old sample rectangle. Current masks and SE/Fang gates stay unchanged.
2. For the left window, resolve the diagonal stone border's semantics first. If elevation is real or unresolved, keep it forbidden+4 and evaluate the whole envelope. A segmented/raised receiver requires separate support geometry approval; no cropping workaround.
3. For the bottom window, trace only the three pool frames' real stone/water/vertical surfaces plus4; retain uncertain pixels. Explicitly review the49 contacted apron texels and uncertainty neighborhood. Recompute full-envelope overlap and minimum clearance against the trace, including source toggle state.
4. Cross-check source and current candidate plant/body draw ownership. Bind A13, original atlas frames/pages, floor records, registration, six source identities per tree, and every reviewed material trace. Do not infer flatness from navigation flags.
5. Only after these CPU material traces and their overlays are reviewed should any newreceiver or6-slot GPU trial be considered. Existing4.5 input proposal remains unchanged.

This is the smallest honest exclusion proposal supported by current source evidence. A finished allowed mask is deliberately not claimed: exact curb and pool-rim traces are the remaining geometrical evidence, rather than an engine change or whole-map audit.

## Reproduction and diagnostic files

Source study: art_source/earth_upright_receiver_review_v1. Run review.py, intersections.py, then debris_contact.py; all outputs go to diagnostics/earth-upright-receiver-review. The latter two reuse the previously archived upright-shadow measurement producer, which also refreshes its ignored diagnostic outputs only.

Review images: left_50_41-source-context.png, bottom_61_51-source-context.png, corresponding floor.png and floor-coverage.png; debris-57/58/59-4x.png; debris-58-contact-top.png. These are original RGBA technical composites/crops, not generated art. report.json records every floor/plant/debris source identity, original source cell, frame bounds, atlas page SHA, direct and+4 intersection counts. debris-contact.json enumerates exact direct-contact texels.
