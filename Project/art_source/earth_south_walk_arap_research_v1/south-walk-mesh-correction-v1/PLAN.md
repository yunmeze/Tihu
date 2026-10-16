# Pure 2D mesh correction: stage 0 baseline

## Scope and current gate
Only independent research directory; no main repository edits or uploads. Original AI sheet is copied byte-for-byte under raw/RAW.png. Parent review of baseline is required before deformation. Godot lease has been requested from plan_first_map_review but has not been granted. No Godot process has been started.

## Observed evidence, not anatomy
Source PNGs 57–62 are literal original 128×128 windows rooted at (16,64). Original timing is 7 ticks at 50Hz = 140ms/frame, 840ms loop, no interpolation. Existing source-chain record explicitly says hidden knees/ankles and support/contact state are not observable. The terminal y pairs are (91,73),(88,73),(83,88),(73,91),(74,88),(87,83), uncertainty approximately 1 logical pixel. They are visible boot surfaces, not ground-contact or weight-bearing points. Source trousers/cuffs cannot be promoted to skeleton joints.

AI raw slots are [57,60]/[58,61]/[62,59]. Its head/torso centers in the right column are about 35 HD pixels farther right in their local window. This is a layout error separate from pose. Left-column crown reference is approximately (233,41) HD; source common crown reference (40.5,15.5) logical. These are common references, not per-frame fits. Existing motion differences remain.

## Calibration limitation
A unique shared anatomical scale cannot be established from original versus modern redraw: source small hair/head and long jacket have different shape semantics from the AI's broad hair/head, shoulder armor, and tight suit. Hair width, coat/armor width, and visible torso length give incompatible ratios. No common scale is claimed as a solved or validated proportion. Diagnostic s=.72, with .68/.76 sensitivity, is frozen for potential method testing, subject to baseline review. Neither feet nor whole-body bbox is used to solve it. Source hair crown uncertainty ±1.5 logical px, raw crown ±3 HD; width/style uncertainty is larger and cannot be represented as simple translation error.

Order of operations is separately retained:
1. Original raw slots, unchanged.
2. Column correction: right-column x minus 35 HD; left unchanged. No independent phase placement.
3. Shared scalar s and shared translation sending (233,41) to (162,62) HD. No per-frame scalar, rotation or head pinning. Source root stays (16,64) logical.
4. Only after baseline review: mesh-deformed output, separate from baseline.

The 1× and 2× baseline boards show original + all three scalar alternatives without crop-to-person or display enlargement beyond their declared scale. AI head remains visibly wider, modern torso shorter/broader, original cloth not reproduced. A foot match cannot excuse these differences.

## Conditional two-frame mesh pilot (not executed)
First phase57 (extreme) and59 (small reversed step). Use Godot Polygon2D triangulated UV mesh with raw image as texture, no 3D, no skeleton hallucination. A regular ~8HD grid covers each complete slot. Common calibration is applied to mesh destination vertices. Foot-end displacement has smooth vertical falloff from zero at visible belt/lower-trouser transition to full displacement at the boot toe; near the toe it is constant to protect the shape. Screen-left/right fields blend across the existing negative space; no cut-out assembly or hidden hip point. Upper torso and arms have zero pose displacement. Each phase's explicit visible-foot positions and uncertainty are recorded before render. The field must be inspected where armor surfaces occur; alpha is never painted or repaired.

### Driving constraints (excluded from success score)
- Shared registration reference and column shift.
- Screen-left/right visible shoe-terminal target positions, with ±1 source pixel tolerance.
- Fixed upper-area field and gradual lower-body transition.
Reaching these points merely verifies implementation, not motion fidelity.

### Independent checks
- Original hand-skin patch ranges, not used in calibration/mesh, compared to AI visible hand surfaces.
- Entire lower-limb silhouette, gap shape and direction, especially both exposed boot lengths in59. Different clothing prevents exact cuff-to-knee matching.
- Armor-panel local width/height and texture integrity; no compressed kneecap claimed correct because feet match.
- Triangle signed area, deformation singular values, and anisotropy over visible alpha; zero triangle reversal mandatory. Report worst local distortion and affected alpha area. Stop if triangles reverse or visible panel aspect changes are severe.
- Fixed head/torso visual continuity and absence of new offsets. Two isolated frames cannot prove a six-frame temporal loop.

Only if pilot survives review should all six be exported; then deliver source/baseline/mesh native1×/2× boards and exact140ms six-frame comparison. Original hard phase57→58 and60→61 temporal differences remain independent visual checks, while constrained foot deltas remain implementation checks. Never announce full fidelity from endpoint signs alone.
