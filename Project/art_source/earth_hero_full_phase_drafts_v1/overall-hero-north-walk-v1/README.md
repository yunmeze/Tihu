# N / NE walk first drafts — visual gate failed

Two actual built-in image_gen calls, one per direction. These are review-only candidates and MUST NOT replace runtime walk or run clips. Frozen v6/main/shadow were not edited; no Godot or Git actions.

## Source contract
Original movement.json and body/head atlas were extracted directly with source offsets, body first then head, at 128×128 root [16,64]. See provenance/original-reference-contract.json for every rect, offset, SHA and source ID. N IDs33–38; NE39–44. Walk cadence7 ticks. Runtime draw offset[-16,-64], generated density4 gives 512×512 physical frames. No second original offset may be applied. Original native root is not the foot contact.

## Pre-generation phase analysis
N source33: screen-left leg extends toward viewer, right leg forward, opposite arms. 34: narrowing support and lowered torso. 35: passing toward opposing half-cycle. 36: screen-right leg extends toward viewer, left forward; counter-swing reverses. 37: narrowing. 38: alternate passing returning to33. Body offsets are [8,-48],[8,-48],[7,-48],[7,-48],[7,-48],[7,-48]; head [20,-49],[20,-48],[20,-49],[20,-49],[20,-48],[20,-49].
NE source39: broad diagonal stance along upper-right travel axis; 40: closing stride; 41: passing, near leg largely vertical; 42: opposite broad diagonal stride with reversed arms; 43: closing/push; 44: opposite passing. Body [6,-48],[9,-48],[7,-49],[5,-48],[7,-48],[10,-49]; head [21,-49],[20,-49],[21,-49],[21,-49],[20,-49],[20,-49]. Original low resolution limits exact anatomical/contact inference; images, not semantic labels, were the pose authority.

## Outputs and mechanical registration
raw/{N,NE}-sixphase.png are untouched real 1536×1024 generation outputs. provenance/{N,NE}-actualargs.json contains exact tool arguments and referenced image paths. registered/{N,NE}/body.png are 3072×512, six frames in order, and individual source-numbered PNGs are provided. One isotropic 512→358 full-cell scale, same for both directions; one constant per-direction translation, all six phases. No frame-specific foot snapping, mirror, limb warp, programmatic painting, or alpha cleanup.

## Visual review: NOT PASSED
Both raw sheets include unwanted semitransparent brown glow around figures despite transparent-background request. RGBA alpha range0–254 is not sufficient evidence of clean transparency. Glow was preserved and not masked away. N pose2/5 show likely repeated leg ordering; NE poses0/3 appear similar leading-leg order, so opposite-half-cycle support is not reliable. No obvious detached limb, but grounded gait/cyclic continuity not accepted. Identity black/grey suit/red shoulders and directions are recognizable. No extra image iterations were made for small folds or to conceal these failures.

Run remains independent and incomplete. No claim of original pixel-perfect motion or runtime validation.


## Corrected alpha assessment
Earlier claim of a visible brown background was incorrect: view_image exposed RGB beneath alpha0. True gray alpha-composites in diagnostics show no broad glow. See provenance/alpha-review-correction.json for zero-alpha hidden-RGB counts and low-alpha fringe measurements. Raw PNGs have NOT been modified. v1 motion defects remain; v2 N screen-leg order is improved and awaits registration review. NE v2 was not called.
