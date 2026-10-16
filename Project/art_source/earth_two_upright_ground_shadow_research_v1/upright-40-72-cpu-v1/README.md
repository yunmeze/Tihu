# Upright 40,72 CPU-only receiver preparation

This is a second instance study, not a runtime enablement or a new unified release. First-tree 51,70 artifacts are unchanged. Inputs refer to the old approved unified-v2 resources preserved in the frozen first-tree staging. Final stable plant-bank migration requires a new reviewed execution closure and shared revoke token; these research paths must not become runtime paths.

## Reproduce
Run build_cpu.py, verify_semantics.py, sample_edges.py, then cpu_gate.py from this directory with Python, NumPy and Pillow. The gate's missing-owner304/mask/ground-registration negatives must fail. No Godot is invoked. FILES_SHA256.json freezes this deliverable, excluding itself.

## Evidence and limits
- Fixed root (1956,2318), raw root (560,1329), density4.5; same raw776650 positive-alpha pixels, including142511 weak1..127. Six owner textures reconstruct raw exactly;304 stays empty to suppress the original cast.
- Cast (+1.2,+.55), blur .8 logical, opacity .25 unchanged. Full alpha + bilinear/filter + fixed root-error support is recomputed, not inferred from opaque-only silhouette. Patch[1840,2302,2444,2496), grid1208x388 at2pixels/logical.
- Nominal134420 maskcells; error213252. This is8 cells more than translating the first-tree raster: world floating-point boundary rounding is recomputed conservatively. Exact per-box coverage verification passes. Do not substitute a translated raster without recomputing bounds.
-18 actual floor owners are all frame406,96x64,RGBA hash checked against the inventory and ground manifest. Every pixel alpha255. Their union covers every error-support cell; background fill never enters coverage. Modern grass768x768 also all alpha255, separately pinned.
- Full-support FAIL remains:25 half-logical cells intersect the original pool56@50,76 full-positive-alpha apron plus5logical. Centers x2432.25..2438.25,y2462.75..2464.75 are listed exactly in CPU_ALPHA_EDGE_RESULT.json. Nominal support does not intersect. All25 actual nine-tap samples alpha0;101637 positive samples remain101637 and removed alpha mass0. Allowed mask has213227 cells.
- Pool padding includes off-patch source57 before dilation. The independent padded reconstruction matches. Earlier local-only dilation was detected by this check and corrected before freeze; inside the tree envelope the25-cell result was unchanged. The exclusion is the whole old pool RGBA including grass-colored apron plus5, not exactly a stone boundary plus5. No color-key extraction.
- The semantic board depicts ORIGINAL source reference, not the modern live tree and not an actual new shadow screenshot. Blue is nominal, amber root error, red pool exclusion. Native results are absent by design.

## Foreground bamboo and baked-image risk
Original bamboo316–322 spans11 local owners;10 intersect the error support,317@42,81 has0. Actual source alpha is binary0/255 for all11, with transparent leaf gaps; there are no fractional source alpha pixels. Filtering may create fractional edges, so preserve normal RGBA object ordering above the ground pass. Do not claim alpha statistics identify baked shadows. The reference visibly contains checker/dark baked patterns; those RGB pixels stay in the original foreground. A ground-shadow max pass deduplicates only generated casts, not baked RGB. Leaf-gap coverage and possible darkening under filtered edges remain later visual observation items. No procedural removal or foreground-shadow overlay is proposed.

## Shared two-instance implementation draft
One immutable decoded upright raw bank, validated once on load and once at shared binding, feeds both51,70 and40,72. Reuse the texture/RID/generation and raw-alpha proof; do not perform six texture readbacks per tree per frame. Each instance retains its own six-owner identity,304-empty requirement, fixed origin/root, local floor identities, pool exclusion, receiver mask region, active state and failure reason.

Use one raw sampler and one nearest receiver-mask atlas sampler for the class. Two bordered atlas regions preserve each approved world rect; explicit bounds reject outside and prevent atlas bleed. Each admitted instance evaluates the same nine-tap alpha using its own origin and receiver region. Combine both with existing shadows through the existing single final max and one darkening output. Do not add two transparent passes or sum alpha. Atlas storage is an implementation option only; no atlas/runtime shader was generated here.

Failure policy: a shared raw/bank mismatch revokes both; an individual owner/mask/source-region mismatch revokes only that tree. Ground mode/generation changes revoke dependent admissions immediately. Whole shadow clear must still clear both; old five slots, idle and hero v3 qualification remain independent. Old51,70 accepted ground-only clipping stays exact until explicitly migrated and reviewed.

The other three upright instances near roads have no expanded receiver authorization. No native run, new runtime integration, performance matrix, or publication was performed.
