# Full A13 ground extension plan — source-only, no replacement exported

## Proven scope and source evidence
A13 has2553 floor placements and70 signed IDs:47 large96×64 and23 small48×32. All crop/offset pairs are0. Logical cells are48×32, so a96×64 owner covers four logical cells; use actual rectangle contacts, not guessed one-tile-per-cell adjacency.

The current optional143-placement terrain experiment uses15 IDs. Those15 occur1013 times in the entire map; the55-ID complement has1540 placements. Neither number means accepted replacement coverage.

Visual source classes, with cautious hand-read labels:
-3 pure grass IDs /909 placements: -406,-399,-591, exact RGBA aliases.
-9 pure shallow tan-earth/gravel IDs /1399 placements: -595,-594,-587,-586,-403,-402,-395,-394,-2. These can share a material family, but are not all exact pixel aliases.
-30 grass/earth transition or grass-variant IDs /146 placements. Preserve their individual visible shapes before replacing materials.
-15 narrow stone-curb IDs /64 placements. Preserve each orientation and corner.
-12 coarse-stone FloorSmall IDs /34 placements:118,129,133,136,141,142,144,154,156,157,159,160. Original assembled scenery shows a coarse rubble ring around a separate stairwell/pit object. KEEP SOURCE here; the pit is not floor material.
-1 special ID -426 /1 placement at88,22 with dark line marks. Identity unresolved, KEEP SOURCE.

No clear water-surface or regular silver-brick paving texture was found in these70 frames. This is a bounded visual finding, not a declaration about other maps or hidden objects. Original thin alpha must survive:8 small IDs contain32 pixels each with alpha240 (129,136,144,160,385,401,409,416); others are opaque. Do not flatten such frames merely because the ground looks solid.

The exact source inventory records original cells, atlas rectangles, full RGBA hashes, signed IDs and categories. The source audit script is reproducible from tracked map/atlas data and writes only ignored diagnostics. The environment reviewer also inspected the complete70-ID source contact board.

## Why broad15-ID replacement is insufficient
Actual rectangle geometry gives5011 contacts and258 unordered ID-pair types, including half-tile contacts. Current15 versus remaining55 yields472 contacts /71 pair types. Dominant boundaries: -406/-402154; -406/-39575; -406/-39425; -409/-40624; -406/-38821. These are before building/vegetation occlusion and do not imply every edge is visibly exposed.

A new arbitrary rectangular scope would reproduce the current143-edge hard cut. Extending all pure grass alone would also leave conspicuous transitions around old soil/grass-border tiles. Data production should therefore include the connected semantic transition neighborhoods, even when native review is staged by local windows.

## Proposed staged approach (requires approval before exporting replacements)
1. Freeze the chosen256-lowpass grass/soil textures and world origin0. The mirrored material period is256, reflected superperiod512. One continuous world-address function applies to every new owner irrespective of its ID, size or camera. Do not regenerate, recolor or reset texture phase per tile.
2. Use the12 pure base IDs as known material seeds. Exact source aliases from the initial15 extend evidence to -607,-597,-591,-403,-395,-394 while retaining every original signed ID/key. Source identity does not prove new external seam success.
3. Prepare source-semantic masks for30 transition/variation IDs, beginning with representative large diagonal, small48×32 and near-pure grass patterns. Preserve original source alpha separately. Masks select authored grass/soil materials only; they do not draw grass RGB or recolor source RGB. Manual source boundaries and uncertain mixture regions must be visible in a diagnostic overlay. Do not run an unreviewed global hue threshold and call its result truth. Validate the representative masks against actual adjacent base tiles before completing the30-ID table.
4. For15 curb IDs, retain the currently proven generated stone masks only where the original source frame has matching geometry or exact full-RGBA alias. Initial15 includes7 curb IDs; two exact aliases provide2 further matching shapes. The remaining6 curb shapes (-602,-601,-598,-593,-585,-582) require their own source-boundary review. Until new matching art is approved, keep actual source stone pixels inside explicit source-stone masks while the surrounding grass/soil can use new materials, clearly labeling this partial-source treatment. Do not rotate/mirror a lit curb merely because it resembles the orientation, draw procedural stones, or create hidden stone beneath source grass. If material/edge mismatch is conspicuous, that whole unresolved boundary remains source rather than being mislabeled finished.
5. The12 coarse-stone IDs and -426 retain complete original RGBA. Their35 placements are a deliberate remaining source set, not ordinary soil. Their contacts with new ground need visual inspection and, if necessary, a separately evidenced transition treatment; do not blur them into compliance or modify the independent pit object.
6. Only after source masks and adjacent edges have passed offline assembly, export an explicit2553-owner scope ledger: each key has new-base, new-base+generated-curb, new-base+source-curb, or complete-source status. Preserve original floor draw order, frame dimensions, alpha, map cell/flag/type/index and all collision/portal fields. Whole-map context coverage is not whole-map remaster acceptance.

## Validation and bounded native windows
Offline:
- Reassemble original source data and compare exact original raster first.
- Assert2553 unique owners; no sampling overrun or source field edits. Keep original per-pixel alpha where applicable.
- Evaluate all5011 actual contacts, not only ID averages, including half-width joins. Separate original source edges, material-map discontinuities, mirrored-wrap symmetry and intentional special-material borders.
- Compare road/curb inner and outer boundaries independently; original manual uncertainty is explicit. Generated stone masks must not silently move path width.
- Inspect full-map low-resolution overview for gross category errors, then native crops of all71 previously cross-set edge types and the coarse-ring/unknown regions. Overview scaling is diagnostic only, never a terrain texture.

Native after offline approval:
- Existing61,39→61,49→61,53 route, particularly old143 boundary.
- Representative -406/-402 and -406/-395 interfaces, diagonal/half-tile transitions, new curb orientations and junctions.
- Coarse stone ring and88,22 special region in source-preserving mode.
- World wrap and mirror joints with actor/building/vegetation shadows, fixed camera A/B and original reachable short routes. Unreachable windows stay read-only cameras, never force-move proof.

Any still-unclassified mask or visible source/new seam stays an explicit open item. No additional image generation or runtime/default replacement is included in this plan.

## Source boards and reproduction
Run: python Project/art_source/a13_ground_full_map_plan/audit_source.py
Ignored outputs: Project/diagnostics/art_source/a13-ground/full-map-source-audit/
Key boards: all-70-original-contact-board.png; cross-boundary-context-1..4.png; coarse-rock-formation-static-scenery-context.png; unknown-minus426-static-scenery-context.png; expanded-curb-junction-static-scenery-context.png.
