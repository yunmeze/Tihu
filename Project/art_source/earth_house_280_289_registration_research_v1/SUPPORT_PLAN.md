# Frozen uniform candidate: ground/support review and proposed ten-owner partition

Transform locked exactly as fit-results.json. No new fitting, raw changes or local deformation.

## Contact and entrance
Door center residual(+3.65,+12.91) is an elevated facade point, not ground footprint. Current map lists no portal at this small house (portals are elsewhere); do not invent a doorway interaction or move any map entry. It still visibly lowers the door and remains an art discrepancy, independent of walking.

Three central contact proxies after transform all remain in original blocked cells: left19,23; front23,27; right25,25. The two visible base-edge polylines (600 samples each) touch only the same12 blocked cells as source. Thus the earlier gross rawcanvas invasion of24,29/27,26 is removed by this roof-trained uniform mapping without fitting feet.

However do NOT declare precise no-conflict: expanding manual contact uncertainty by±5logical square reaches walkable20,25;21,26;22,27;24,27;25,26 for candidate, versus25,26 for source. These narrow border uncertainties require actual actor-boot native comparison. They are not an established broad extra platform, nor proof all walking clearance is preserved. The frontbase residual7.62y approaches cell-edge portions along adjacent diagonal walls; preserve source collision and test each ambiguous border. No new platform/stair is present; foundation remains thin but its exact contour matters.

## Fullbody ownership, without source-alpha clipping
The original ten frame rectangles are nonoverlapping on candidate strong support. At density2,271551 strongalpha pixels total;254 (0.0935%) lie outside original rectangle union, maximum distance4.25logical.421 pixels of anyalpha are outside. These must be explicitly supported, not silently erased. Perowner exact strong support and extensions are in SUPPORT_REVIEW.json. Owner285 carries zero strong newbody pixels (original tile is principally shadow), but its original identity remains in the atomic10-owner qualification.

Executable CPU proposal support_review.py assigns each canvas sample inside an original rectangle to that originalowner; outside chooses nearest originalrectangle (stable source-order tie break). This is a PROPOSED render contract, not yet runtime. Strong extensions are at most4.5logical on an owner bbox; no sourcecell/flag/layer/sort/order changes. proposed-owner-partition2x.png visualizes fullalpha allocation. Tiny/faint alpha remains in full master and must also receive ownership, not be filtered away.

Runtime plan if root authorizes: one shared complete transformed texture at original density2, sampled with original fullcanvasUV. Each originalowner draws only its disjoint ownership domain at its original stream position. Ownership masking occurs AFTER common fulltexture filtering, no independently clamped owner texture edges. A shared fullcanvas owner-index map can implement the CPU domain (nearest integer index, never linear blended IDs), with each draw selecting its assigned ID. A1-alpha/outside support remains assigned through whole512canvas; bounded support may be optimized only after exact pixel comparison. No10 independent image crops, no opaque-source-alpha clipping, no firstowner wholebuilding shortcut. Any one identity/frame/hash/dependency violation falls all10 back to source. Source checker shadow not reused; no new shadow.

Native must verify owner seam atfractional camera/1×2×/linear, complete actor occlusion on originalstream, and source/candidate identical movement over ambiguous cells listed above. CPU current fullbody-at-firstowner context is insufficient to certify these. This proposal changes render support explicitly but not collision or door semantics.
