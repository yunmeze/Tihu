# A13 main temple: source group and proposed design input

Status: source preparation only. No new building image, registration transformation or runtime change has been made. Parent review of this evidence precedes image generation.

## Complete minimal scope

Original Building3966–3995:30 distinct A13 owner keys,12 layer0 and18 layer1. Preserve each original cell, flag, row-y order and stable source order. The assembled source bounds are world[2948,642,3744,1307], canvas796×665. All30 have nonempty alpha. Per-piece original canvas/crop/resource offsets and atlas coordinates are in source-group-contract.json.

The reference render adds cell[48,32] plus [0,32-original_height] and crop, ignoring resource frame offset for Building objects. This contract must not be replaced with the actor offset rule.

Layer0 pieces are the walkable stair/platform strips, not an arbitrary whole-building back layer. Source layer1 contains the compound roof, walls, pillars, railings, remaining floor-edge structure and baked apron/shadow. A new image cannot simply be assigned as one large layer1 sprite, which would swallow the character on the stair/platform. Source flags and sorting remain the authority; original layer0 supports need independent ownership even if their visible pixels are narrow.

## Structure to keep

- Compound multi-ridge temple roof, its front corner and two perpendicular facade arms.
- Both visible door openings, both stone stair flights and their different orientations.
- Platform edges, pillar lower ends and surrounding railing layout.
- The temple's quiet religious/community function. Nearby original actors remain 方丈64,37, 凌云子62,36, 道童76,37 with original scripts/visibility untouched.
- No new military towers, gun ports, sealed doors or invented interaction objects.

## Proposed art direction, pending generation approval

A clean science-fiction cultivation courtyard: silver-grey stone and restrained engineering metal, muted dark red panels, warm interior window/door light and cool shadows. Preserve the recognizable temple composition rather than converting it into a fortress. The accepted identity-rebuild-v2 character is a new working identity reference, not a recovered historical concept.

The future building output must be genuinely transparent around and within its structural silhouette. Do not bake a rectangular/diamond ground apron, large grass field, checker cast shadow or surrounding map terrain into it. Keep structural stone plinth and actual stair treads; small justified contact grass/stone can remain only where it does not form an occluding floor sheet. A separate single ground projection will be considered after structure/depth validation.

## Control evidence and uncertainty

source-landmark-local-board.png contains actual original RGBA-derived local crops with manual visible-feature points. C0 samples the white corner pillar's bottom cut; S0/S2 the lowest visible stone-tread edges; S1/S3 the upper tread/platform junctions; E0/E2 the visible eave lips and E1 the front roof end. These are physical material samples, not adjacent soil or alpha-only bbox extrema.

Every point has a4–5px manual-read region and alpha/contributing original owners in the contract. Eave lip samples are not claimed to be exact upturned-tip extrema. The manual error floor is explicit; do not quote a subpixel fitted RMS as exact geometry proof. The stone landscaping skirt and source checker projection are not feet.

A future candidate should first use a common scale/translation and compare independent real landmarks. If different facade/platform planes disagree materially, do not force one global affine transform across the entire multi-plane structure. A separately justified true-plane projection or a full structural image edit needs a documented correspondence; no arbitrary local vertex pulling, fake depth faces or actor sort override.

## Required later checks

1. Source/new same-scale plate and separate uncertainty-aware pillar/stair/eave measurements.
2. Recover generated pixel ownership for the30 original keys, especially12 layer0 stair strips; no invented polygons just to make every owner nonempty.
3. Same-coordinate source/new actor depth on both stairs/platforms and near original NPCs, using actually reachable points identified by the runtime owner. This preparation does not assert those routes are already tested.
4. Check door holes, stair support, front railing/pillars, true alpha, source checker suppression and sampling bounds.
5. Only after structure: single ground cast on/off and a real original path, with original flags/NPC interaction preserved.

## Reproduce evidence

Run python Project/tools/prepare_a13_main_temple_source.py. Production scope is this plan, source-group-contract.json and the extractor. Ignored technical boards are generated in Project/diagnostics/art_source/a13-main-temple:
- source-preview.jpg and source-composite.png
- source-landmark-board.jpg and source-landmark-local-board.png
- source-layer0-layer1.jpg

Original materials and runtime are read-only for this stage. No imagegen call has been made.
