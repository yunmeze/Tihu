# SW/W/NW walk first draft

18 generated frames delivered as isolated art candidates, not approved runtime replacements. Built-in image_gen was called exactly once for each direction, using original six-phase composites plus matching newly generated idle and established SE identity. No further generation, mirror, Blender, procedural painting, local warp or alpha cleanup was used.

## Findings
- SW: complete six figures, correct down-left orientation and matching outfit. Phases 0 and 3 visibly repeat the same leading-leg relationship; phase 4 also maintains it. This is not a valid alternating two-half walk cycle. Hold for pose correction.
- W: complete figures, matching identity, left-facing. Arm swing changes between halves but phase 0/3 leg-layer order does not reliably switch; phase 0 extension reads too large/floaty relative to grounded original walking. Hold for gait review.
- NW: complete figures, matching rear identity, away-left direction. Phase 0/3 repeats same lifted up-left boot and extended lower-right support. Phase 2 reads near-idle; phase 5 retains backward raised boot. Hold for faithful cycle correction.
- All source originals were composited using body then head and native offsets at root [16,64], preserved at 128 square, with nearest-neighbor enlargement only for reference. Full phase descriptions are in POSE_ANALYSIS.md.
- All generated figures preserve six distinct pixel images; distinct images do NOT establish distinct correct walking phases.

## Alpha correction
The raw image viewer displays a brown vignette, but that broad background is hidden RGB under alpha=0. Actual RGBA composition onto gray confirms no broad visible brown halo in any of the three sheets. For example raw pixel (100,100) is SW=(14,10,7,0), W=(22,17,13,0), NW=(13,9,7,0). Alpha range is 0–254 in all three; therefore every nonzero pixel is technically partial alpha and that count cannot diagnose background contamination. Diagnostic gray composites are saved under provenance, without changing raw or output alpha. No claim of an opaque background defect remains.

## Registration
Raw sheets are 1536x1024, three by two 512-square cells. Every cell is resized to 338-square (one uniform scale 0.66015625 across all 18), placed at [0,24] in a 512-square RGBA output. Every direction has the exact same fixed translation for every phase. This retains generated bob and foot motion without per-phase recentering or anchoring; it cannot restore original pose motion that image generation failed to match. Registration is provisional, not a claim of gait correctness. Six-horizontal output sheets are 3072x512, logical 128x128, density4, draw offset[-16,-64], root[16,64], 7 actor ticks per phase. Sources and generated cells are fully recorded in registration-contract.json and original-reference-contract.json.

No live asset, main, shadow, Godot project configuration, v6, or Git operation was touched. Entire folder is a next-batch review package.
