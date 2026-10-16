# Current review: improved candidate, pending root decision

This geometry/ground-contact review supersedes earlier blanket rejection wording in `REPORT.md` and `candidate-board.png`. No additional generation occurred. No adoption, cleanup, forced clipping, owner split or integration occurred.

## Correct output-size interpretation
1254×1254 is acceptable under the permitted uniform whole-canvas mapping. It preserves aspect and gives density9.796875 raw pixels per logical unit. It is NOT independently a failure. For the actual2× board, the complete untouched raw is uniformly resampled to256×256; source logical padded canvas is128×128. World canvas origin is(3031.5,1744); in the source-context2× canvas its integer placement is(181,136). No object-bbox fitting or repositioning occurs.

## Actual2× context evidence
`ground-context-actual2x-board.png` shows source and candidate on identical original ground, then with identical surrounding original objects. Four standalone panels are also provided. These are exact2× offline source-ground compositions, not native runtime acceptance or accepted Earth-ground review. Original checker shadow is retained in source panels and absent from candidate panels; this large dark source area must not be mistaken for plant-body mass or root footprint. No source shadow was copied under the new plant.

## Main silhouette and branch-direction assessment
The candidate preserves low-left/raised-right orientation, distributed fan-shaped stem groups, high right tip and the main source clefts. Green herbaceous stems are a substantial improvement over attempt1. Newly drawn leaves need not overlap old pixel leaves; earlier global IoU is diagnostic only and is not a design-fidelity rejection gate.

Approximate local body extrema from explicit windows (logical units, source checker excluded by exact color; allow roughly1–3 units source-mark ambiguity):
- Left-low spray retains its left extent near0. Its upper local extent shifts28→25.08, approximately2.9 units higher; this is not a3-unit ground shift.
- Left-upper spray: x-min11→10.42; y-min16→17.52. Broad position retained.
- Central crown: y-min13→12.52. Broad height retained.
- High-right tip: y-min0→−1.46; x-min in the high-tip window71→72.28. Slight top extension, not a global scale error.
- Far-right spray: x-max100→104.13; lower local extent33→39.47. Approximately4.1 units extra right reach and6.5 units lower reach. This is the clearest local foliage deviation and exceeds the certainty available for its original1–3-unit tip marks. It stays largely inside existing right-owner drawing space; it is foliage, not ground contact.

These are region-conditioned extrema, not traced one-to-one branches. Exact individual branching remains redrawn, but there is no demonstrated wholesale wrong silhouette.

## Large openings
Source-body fill→candidate alpha≥128 fill in fixed logical windows:
- Upper-left cleft[24,12,34,25]:2.31%→2.42%, preserved open.
- Upper-central cleft[56,10,65,23]:13.68%→15.28%, broadly preserved.
- Lower-left opening[29,55,38,64]:11.11%→7.90%, slightly more open.
- Lower-right opening[65,61,72,69]:0%→0%, preserved empty.
These explicit openings provide stronger design evidence than leaf-pixel IoU. Fine internal leaflet spacing still differs, as expected from a new rendering.

## Basal/ground-contact proxies
Source approximate visible stem ends versus candidate, all group-local:
- Left(26,63)→(27.16,65.50): displacement(+1.16,+2.50), magnitude2.76 units.
- Central(51,69)→(52.38,72.03): displacement(+1.38,+3.03), magnitude3.33 units.
- Right-central(62,66)→(63.91,66.72): displacement(+1.91,+0.72), magnitude2.04 units.
All are inside the previously stated4–6-unit source-proxy uncertainty. Thus no decisive physical root displacement is established. Candidate central stem does extend slightly lower, roughly0.24 units past logical y72 at alpha≥128; do not silently shift the entire plant to compensate.

The fourth source proxy(73,59) is weak: its status as an independent ground contact is not established by the small original raster. It may describe a visible lower branch rather than a separate root. Lack of a fourth obvious candidate ground contact is therefore unresolved evidence, not an automatic missing-root failure. Three spatial owners do not imply three botanical roots, and four manual inspection marks do not prove four roots. Preserve exact owner registration independently.

## Body spill and alpha
At alpha≥128,4.282 logical square units,0.228% of candidate body, lie outside the union of the three original draw rectangles. These are small top/basal/edge protrusions, not a large footprint expansion. Spill ranges reach x≈−0.09,y≈−1.46 and y≈72.24. The aggregate spill bbox spans separated tips and must not be interpreted as a filled extra region. Far-right foliage extension is mostly within the existing owner rectangles.

This small unowned body spill still needs an explicit registration/ownership solution before installation. Do not force-mask clip it, fit its bbox or move roots. The current task does not authorize changing owner bounds or installing it.

Raw low-alpha noise extends farther; it is almost invisible in the actual2× composites but remains a technical alpha-hygiene issue. No alpha cleanup was performed. Correct alpha composites show predominantly legitimate pale leaf highlights. Do not claim a broad neon matte failure based on the raw black preview.

## Decision and confidence
Candidate is viable for further parent review, with substantial herbaceous morphology improvement and broadly retained major openings/contacts. No adoption yet. Main decision points: whether the local right spray extension is acceptable, how to resolve tiny owner-boundary spill without clipping/deforming, and whether any stronger source-ground-contact evidence is needed. No further image generation recommended within this task.

High confidence: uniform mapping validity, actual2× placement, opening preservation and small spill quantity. Moderate: correspondence of main branch masses and three basal proxies. Low: independent fourth-root interpretation and exact botanical branching from the small source. Native owner reconstruction, depth and movement remain untested.
