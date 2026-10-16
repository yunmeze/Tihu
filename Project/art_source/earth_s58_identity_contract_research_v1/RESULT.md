# S58 single generation: mixed result, not runtime-approved

The crossed phase is recognizable: screen-left hand higher and left boot lower, right leg foreshortened. Three central silver plates, substantial black abdomen, red shoulders and knee/upper-shin armor remain. However this is not a clean adjacent-sequence pass: the left long boot/leg extends too low and its recovery into59 is exaggerated; the right visible lower-leg presentation is less extremely short than the original. No second sampling or correction was performed.

## Actual chain and mapping

One built-in imagegen call using only frozen REF01_SOURCE58_FULL_512.png and REF02_IDENTITY_GENERIC.png, exactly PROMPT.txt and REQUEST_FROZEN.json. RAW.png is byte-identical to returned `/workspace/scratch/22c897619190/generated_images/exec-e1bfbf71-bdb8-4909-ad26-c41e78d2847c.png`.
Raw SHA256 e06e89843b1dcd4f32d7b1adef06b511714004cb25457e34e4ce376ed09c8bb8.
1254x1254 RGBA. Whole canvas only: logical coordinates raw*128/1254; display512 uses PIL LANCZOS 512/1254. No crop-to-bounds, translation, fitting, warp, patch, or alpha cleanup. No border alpha-positive pixels in58. Existing59 bottom alpha1 remains intact.

## Full-body visual review before points

At1x and2x,58→59→60 reads as alternating leg exposure and changing arm swing, not three idle copies. In58 the left sleeve/forearm/hand chain bends forward coherently while the right chain hangs lower. No disconnected hand or visibly amputated right lower leg. The left long leg is visibly extended further than the source, and the58→59 left recovery is too large. The right knee shell is complete and rounded with a short band/boot below it; this is coherent modern construction, but shows more distinct armor/ankle/boot surfaces than source58's tiny terminal patch. Source cuff is not a modern anatomical knee, so this alone does not establish a precise joint error. It remains a visible-length/foreshortening concern.

The face/hair and main chest construction stay recognizable.58 face/chest/shoulders sit modestly lower than59 although original58/59 head placement is unchanged. This is not whole-body proof of a scale change.58 left forearm has a broad bright shield,59 has a different smaller asymmetric cuff/plate presentation; right forearm metal also changes extent. Outer-thigh plates remain longer/larger than the identity board's restrained construction and vary across frames. No runtime identity/registration pass is claimed.

## Held independent visible surfaces (logical128; screen sides)

Alpha128 terminal points are boot surfaces, not contact or ankle joints. Uncertainty ±0.75 each, source ±1.
58 L=(37.461,93.907), R=(46.648,76.555). Original L=(35,88),R=(46,73). Absolute y errors +5.907,+3.555.
59 L=(36.593,84.823),R=(46.750,91.254).
58→59 new delta L=(-0.868,-9.085),R=(+0.102,+14.699); original L=(0,-5),R=(0,+15). Right delta is close and its common low placement resembles59/60; left recovery discrepancy ~4.08 is materially larger than that common shift.
59→60 new delta L=(+0.459,-8.676),R=(+1.174,+2.756); original L=(0,-10),R=(0,+3). Do not independently translate58 to fix one side.

Manual skin-terminal y (not cuff or skeleton), ±1.5:58 L51,R56;59 L55,R50;60 L58,R48. Thus58→59 L+4,R-6 vs original+4,-4;59→60 L+3,R-2 vs original+2,-2. Hand-height order exchanges correctly, but new58 right hand has extra low displacement. Modern58 cuff edges around L47,R53, ±2, are material edges only.

Approximate same-modern surface anchors, ±1.5:58 face center around(40,26),59 around(40,24.5),60 around(41,28);58 red-cap centers y30,59 y28,60 y30.5;58 broad chest center y36.5,59 y35,60 y37;58 black waist center y48.5,59 y47.5,60 y49.3. These coarse visual locations characterize a small upper-body bounce and are not a predeclared registration fit. Hair tops58~15,59~13.5 are silhouettes, not anatomy. Three major silver plates remain countable in all three; black gaps and waist remain, with local contour/detail drift.

## Review files and limitations

THREE_PHASE_COMPARE_1X/2X.png: full original58/59/60 then fixed-canvas new58/59/60.
THREE_PHASE_140MS_1X/2X.gif: original/new paired, each phase140ms, then a700ms blank END card. This is an incomplete three-phase sample, not a full cycle; blank prevents pretending60→58 is the real wrap.
UPPER_58_59_GRID.png and LOWER_58_59_GRID.png: independent enlarged readouts, never generation inputs.
AUDIT.json contains exact canvas/alpha/terminal data; audit.py regenerates boards and mapping. Source checker is retained only in source evidence. No fit or transformation applied, no source joints invented. Art quality and complete phase judgment precede endpoint numbers. Await root decision; no automatic57/61/62 or retry.
