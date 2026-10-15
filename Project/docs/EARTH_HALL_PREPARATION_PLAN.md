# Earth hall: source identity contract, awaiting approved registration

`data/earth/a13_hall_source_scope.json` contains the 30 original A13 building owners 3966–3995, independently rebuilt from the original map and compared field-by-field with the source-art contract. There are 12 original lower-layer support owners and 18 layer1 owners. This is a trusted source scope, not approval of a generated building or an installed renderer.

## Preparation and publication

1. Read and validate registration JSON before typed calls. Bind its exact owner count/keys/cells/frame/pack/layer/sort/order/source_cell to the trusted source scope and loaded A13 map.
2. Require an approved common registration transform and per-owner image regions from the asset owner. Do not infer their position from original sprite extents, modify coordinates to expose boots, or use an unapproved raw image.
3. Preflight all textures, dimensions, hashes, numeric bounds and regions as one group. Empty owners need an explicit validated empty-owner contract, while still suppressing their matching source owner. No partially loaded group may publish.
4. Preserve the original ordered-object loop. At each matching original building owner, draw only its approved replacement parts at the same layer/Y/stable-order position. Floor rendering remains earlier. Keep source NPC and hero interleaving unchanged. Suppression is by exact owner identity, not global frame ID.
5. A failure restores all 30 source owners. Any future associated cast must use the same group gate. No new cast is part of this stage.

## Required native evidence after assets pass geometry review

- Original whole image versus split replacement GPU parity, then original/new under the same actor frame.
- Left support samples 66,34 / 65,35 / 66,35 / 66,36 and right 73,35 / 73,36 / 74,36 / 74,37 on original A* routes. Record blocked targets honestly.
- Check stairs' traversable widths and upper/lower seams against original flags; keep railings/side cheeks in their actual depth classes. Do not raise the hero to hide a layer error.
- Actual fixed sample and follow camera at true2×; actor starts61,39. The sample camera does not redefine doors or change collision geometry.
- Whole-group missing/malformed dependency fallback, source toggle, map/flag immutability, fresh import, and unchanged R1/R6 entry regressions.

As of this preparation, the new hall's stair widths/context seams have not passed the full geometry gate. The ordinary Earth entry continues rendering the original hall. The file supplies no guessed candidate transform.
