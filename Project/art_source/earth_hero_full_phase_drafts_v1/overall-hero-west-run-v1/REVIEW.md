# West/south run first art coverage, not acceptance

Four genuine built-in image generations, one per S/SW/W/NW, each six distinct full character drawings. Raw1536x1024, 3x2; registered3072x512, six512px slots. Original run IDs105–128, five actor ticks each. No idle frame substituted. No runtime/Godot/main/shadow/v6/Git changes.

Original-authority source, native offsets, source SHA, actual tool arguments and output paths, phase analysis, registration and input hashes are preserved. Identity is the same black tactical fabric, metallic gray plates, red shoulder character. New west idle assets are costume/view references, not action authority.

## Alpha QA
All four raw PNGs are RGBA, alpha extrema0..254. The brown atmosphere visible in direct raw previews is invisible RGB under alpha0, NOT an opaque background. All four are separately composited over neutral gray in qa/ without modifying raw pixels; broad brown vignette disappears. Alpha is never cleaned, thresholded or repainted. Fine edge translucency remains. Quantified alpha bins in registration-contract.json distinguish low alpha pixels from invisible RGB.

## Registration and uncertainty
All24 cells use the exact same uniform342/512 scale. One fixed whole-cell translation for each direction, unchanged across all six phases. The translations are provisional actor framing, not anatomical foot anchors. No per-phase foot locking or scale changes; generated running rise/fall is retained. Original root16,64 and logical128-square contract preserved. Generated head horizontal positions drift across columns, notably W; this cannot be corrected faithfully through a shared translation. No claim of exact original pose registration.

## Visual review / first-pass defects to refine after overall coverage
- S: phases0/3 do alternate the forward leg, but phases4/5 deviate from original leg/arm succession. Phase4 puts screen-left leg forward while screen-left arm also leads; phase5 resembles phase3 rather than restoring intended opposite reach. Broad sprint energy is present; exact six-phase fidelity is not accepted.
- SW: all six are recognizably sprinting with folded trailing knees. Front knee/arm occlusions and hip counterrotation differ from source; phase0/3 arm swap is clearer than anatomical leg swap, which remains uncertain. Needs source-aligned joint review.
- W: near arm swaps between phase0 and3; leg silhouettes in those open strides remain very similar with ambiguous leg identity. Wide strides are stronger than source in places. Torso rotates toward front in phases2/3 and head/cell x drifts. This is not a perfectly locked side camera.
- NW: clear rear three-quarter running, airborne heel recovery in phases1/4; body yaw varies, and phase0/3 open-stride leg identity remains uncertain despite arm reversal. Original modest bob is exaggerated in lower-row relative placement.
- All: image generator enlarged character from requested~285px to~420px; whole-sheet uniform registration restores approximate game scale. Six unique image hashes do not prove six correct poses. No claims of runtime/collision/contact validation.

Do not silently promote this first coverage candidate to a completed animation. No second generation attempted, per first-pass breadth-first instruction.
