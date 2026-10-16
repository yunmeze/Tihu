# Read-only feasibility: silhouette-domain 2D deformation

## Decision
Worth a bounded CPU-only prototype on57 and59. This is a different mesh domain and optimization method, not continued tuning of the failed rectangular blend. No new solver, image output, dependency installation or GPU run was performed in this assessment.

## Real texture evidence
Both source AI frames contain a single connected foreground at alpha thresholds64,128,200. At alpha128,57 has36,540 foreground pixels and59 has39,534. The lower region y>=230 contains13,630 and15,791 foreground pixels respectively. Alpha16 adds only one/two isolated one-pixel fragments besides the main component. Thus there is enough real visible texture to attempt a connected-surface deformation, including both boot/toe surfaces; texture synthesis is not needed for the modest endpoint deltas in this pilot. This does not mean every requested projected pose is recoverable from this texture.

The leg gap is observable raster background, becoming narrow near the crotch and wider below. It must be excluded from the mechanical domain, rather than assigning an interpolation field across it. The two legs can remain connected through the original visible trousers higher up. No anatomical hip, knee, ankle, joint angle or support state needs to be introduced.

## Dependencies verified locally
Available: Pillow, NumPy, SciPy; scipy.sparse.linalg.spsolve, scipy.optimize.minimize and scipy.spatial.Delaunay import successfully. Not installed: cv2, shapely, triangle, skimage, trimesh, igl. No installation was attempted.

A conservative first mesh can be built directly from the occupied-pixel domain using shared square-grid corners and two positive triangles per supported cell. This avoids requiring a constrained-Delaunay package and avoids accidentally closing a concave gap with ordinary Delaunay. Start with 1–2HD cells, keeping fine boundary geometry and checking connectivity; a full foreground raster mesh may be tens of thousands of vertices, so freeze the upper body and solve only the lower variable region. A sparse linear solve is plausible, but timing and memory are unmeasured. Do not claim the regular raster mesh is optimal or guaranteed to preserve every antialias fringe.

Preserve raw texture bytes. Establish the mechanical main component from robust alpha, then audit coverage of the actual non-negligible alpha fringe. A rendering-only boundary fringe may inherit nearby surface motion without adding mechanical edges across the leg gap. Excluded raw alpha contribution must be measured and disclosed; no quiet erosion, hole filling or painting. Mesh construction fails if it cannot keep the original visible silhouette coverage and leg-gap topology simultaneously.

## Proposed bounded algorithm
1. Retain exactly the approved shared.72 calibration and column correction. No phase-specific global fit.
2. Mesh only real foreground surface with open leg-gap boundary. Verify no edge/triangle crosses unsupported gap and no disconnected accidental fragments; verify source texture coverage.
3. Freeze head, torso and hands in baseline coordinates; attach the lower mesh through its visible upper-cloth boundary. This is a material constraint, not a hidden hip joint.
4. Define explicit small visible shoe-toe/armor-panel patches. Apply near-rigid shape terms within each patch, allowing different patches to move relative to one another through real cloth/boot bands. Do not weld an entire shin into a fabricated rigid bone. Freeze patch selections before seeing output.
5. Fit lower-cloth deformation with local/global ARAP energy using proper2D rotations, sparse global solves and positional constraints. Ordinary ARAP is only a distortion preference, not a flip guarantee. Add positive signed-area checks at every proposed update, determinant margin, continuation from baseline toward target in small steps and backtracking line search. If no acceptable step exists, fail instead of projecting through a fold.
6. Add boundary-segment self-intersection/cross-leg overlap checks. Positive individual triangle areas do not alone prove global nonintersection. No opacity or depth-order trick to hide collisions.
7. Measure all active triangles, including boundary coverage; report area-weighted high-strain fraction as well as max singular values and panel patch Procrustes residual. Keep drives and independent acceptance separate.

A full SLIM/barrier-energy implementation is a possible stronger successor if simple ARAP plus conservative acceptance stalls, but is not a trivial switch or currently installed solver. It should not be silently approximated while claiming the published guarantees.

## Constraints versus evaluation
Driven: common registration, fixed upper boundary, visible boot-terminal targets, local patch rigidity preferences. Matching these is not independent proof. Boot target uncertainty remains±1 logical pixel; patch boundaries are visible modern materials, not source joint locations.
Independent: un-driven shoe/armor boundary samples, retained local plate aspect/edge straightness, source whole-leg projection and inter-leg gap shape, skin-hand patches, visible source cuff/boot-length patterns without conflating them with modern armor knees, no collisions or alpha loss, and eventual interphase continuity. Hold out boundary samples from the chosen rigidity patches where possible; disclose that region rigidity itself is an objective and cannot be scored as an independent anatomical correspondence.

## Risks and stopping rules
- ARAP may preserve the wrong original pose too strongly or put stretch into adjacent cloth. If target placement needs newly exposed/hidden surfaces, a warp cannot invent correct texture or occlusion.
- Footpoint motion remains insufficient to infer original whole-leg projection. Independent visual mismatch can fail even with low energy and perfect endpoints.
- Thin pixel features and contour simplification can disconnect or bridge geometry. Reject topology/coverage errors before solve.
- Any inverted triangle, boundary collision, visible mesh crack, significant visible alpha loss or obvious armor/toe shear fails. Do not allow folds merely because a sample centroid is transparent.
- Fix upper body; do not let the solver compensate for leg constraints by moving head, hands or torso.
- Two frames cannot establish six-frame gait,140ms temporal continuity or original bounce. Do not expand until both CPU geometry and native1×/2× pilot review are acceptable.

## Minimum next scope
Only CPU mesh construction and solver on57 and59; no new image generation, no other phases, no repository change, no GPU initially. Deliver topology/coverage maps, frozen drive/holdout ledger, orientation and overlap checks, patch distortion values and target residuals. If and only if those pass, request the existing serialized Godot lease for a two-frame Dummy-audio export to a new owned revision directory. Stop after this short method test for review.

## Primary references
ARAP original research/project: https://igl.ethz.ch/projects/ARAP/ and https://igl.ethz.ch/projects/ARAP/arap_web.pdf
Locally injective mapping methods/barrier distinction: https://igl.ethz.ch/projects/slim/ and https://igl.ethz.ch/projects/LIM/
Constrained planar triangulation/domain boundaries: https://doc.cgal.org/Manual/latest/doc_html/cgal_manual/Triangulation_2/Chapter_main.html
SciPy spatial API: https://docs.scipy.org/doc/scipy/reference/spatial.html
These references support method choices, not a claim that our future implementation inherits their guarantees.
