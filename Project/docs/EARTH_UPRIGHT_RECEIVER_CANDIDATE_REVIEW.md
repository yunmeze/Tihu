# Two-patch receiver candidate: CPU review required

## Decision

**Left patch passes this explicitly approved2D approximation; bottom patch fails. Neither is installed.** Existing four-caster receiver masks, helper and compositor are unchanged. A future six-slot diagnostic may have only the left new slot eligible; the bottom new slot must stayzero unless new evidence resolves its contact uncertainty without moving its body/root or clipping its shadow.

The left grass/stone-edged road is treated as coplanar decorative ground by parent approval. This is a rendering approximation, not evidence of original physical elevation. Source flags, navigation and RGBA remain unchanged.

| Patch | Full nominal envelope | Root-error envelope | Forbidden overlap nominal / error | CPU result |
|---|---:|---:|---:|---|
|left (2319,1311,605,190)|134420 cells|213244 cells|0 /0|passes under approved road-border approximation|
|bottom (2847,1631,605,190)|134420 cells|213244 cells|165 /2747|fails, whole cast disabled|

All counts are half-logical raster cells. Full envelopes, including error cases, are independently asserted inside their proposed patches before mask testing; no out-of-patch truncation earns a pass. The bottom nominal165 conflicts are all unknown material transition+4. Under root uncertainty,522 cells also hit positively identified nonflat material seeds+4; known/unknown dilation overlaps, so those counts are not additive.

## Source-backed material labeling

Only Debris57,58,59 require nonflat material exclusions in these patches. All126 Building and379 Wall owner frame bounds were checked in the prior source review, with zero intersections and no unresolved frames. The floor coverage remains opaque and continuous.

Manual per-frame source-pixel curves identify a conservative subset of the visible grass/soil apron. The admitted region is positive-alpha source pixels strictly above the supplied apron curve. The adjacent transition band and everything not classified remains forbidden. Known nonflat seeds are the clearly visible top stone/vertical/water band below a separate interior curve, limited to source rows<45; they are evidence of actual material, not a complete optimistic segmentation of the entire pool. All remaining pool pixels are unknown and forbidden, including water or lower rim not separately traced. Both known and unknown forbidden pixels receive4logical AABB expansion before union.

This scheme preserves all real pool material and uncertainty. It deliberately cannot “prove pass” by guessing that green/brown pixels are flat. No alpha threshold removes material, and no whole Debris owner is dropped. Curves are source-pixel annotations, not body texture changes. The49 previously measured nominal contact texels of Debris58 lie in reviewed grass apron, but the shadow remains too close to the unclassified transition after4logical clearance.

The nominal envelope is7logical cell-center units from the **interior known nonflat seed**. This is not a certified7logical distance from the true stone boundary: unclassified transition material is closer. The uncertainty envelope reaches the known seed itself, so refining only grass-apron labeling cannot establish robustness for the current root uncertainty.

## Root uncertainty test

Actual density4.5, raw size1162×1353, root(560,1329), cast(1.2,.55), opacity.25 and logical blur.8 remain unchanged. Nominal envelope already includes bilinear support, blur and safety1logical.

The registered raw-root uncertainty9px/4.5=2logical plus source-root uncertainty4logical are conservatively tested as a fixed-body ground-line perturbation±6logical. Its projection displacement is±7.2 inx and±9.3 iny. The test uses the encompassing Cartesian box, including combinations outside the correlated perturbation line, so is conservative. It also encloses a separate source-origin perturbation±4 plus raw-ground-line perturbation±2, whose displacement bounds are±6.4x,±7.1y. This is a confidence test, not a change to registration or per-frame foot/root snapping.

Full error-envelope bounds:

- Left: [2322.088889,1311.905556,2920.355556,1499.594444].
- Bottom: [2850.088889,1631.905556,3448.355556,1819.594444].

Each lies within its605×190 proposal, with at least0.9055logical clearance to the top patch boundary. The two patches are independent; old receiver domains must not be enlarged implicitly. Offscreen presentation clipping remains separate from world receiver eligibility.

## Candidate files and review images

Producer: art_source/earth_upright_receiver_candidate_v1/build_candidate.py. Run it from any directory; outputs are only diagnostics/earth-upright-receiver-candidate. Source snapshot candidate.json records source-pixel curve vertices, patch geometry, uncertainty assumptions and test counts. SOURCE_SHA256.json binds source map, atlas, registrations, source renderer and preceding measurement files. MASK_SHA256.json binds the current diagnostic outputs.

Review:

- left_50_41-candidate-overlay.png
- bottom_61_51-candidate-overlay.png
- debris-57-material-labels.png
- debris-58-material-labels.png
- debris-59-material-labels.png

Overlay colors: blue nominal full envelope; amber additional error envelope; red forbidden pool material+4. The base is the unchanged source floor. Source-material labels: green reviewed apron; red known nonflat top seeds; amber unknown, which remains forbidden. Black background is transparent source area. Material maps are technical annotations, never production art.

Each patch also has allowed.png, forbidden.png, nominal-envelope.png and root-error-envelope.png with instance prefix. Masks are1210×380 at density2, world-aligned. The left forbidden mask is empty under the explicitly approved road approximation; the bottom forbidden mask has4464cells. These are **candidate diagnostics**, not runtime resources, and no slot is automatically enabled.

## Proposed review boundary

Review the left approximation and full/error-envelope overlay before authorizing a new slot/GPU experiment. Preserve exact six-owner identity checks, source/candidate toggles, complete world-domain gate, true4.5 raw-region mathematics and max-after-blur single-blend semantics. Bottom should staydisabled; changing root/opacity/cast or eroding the material trace to force it through is outside this proposal. If a future accurate root measurement reduces uncertainty, that requires separate source evidence and a new review, not a parameter fit to the pool boundary.
