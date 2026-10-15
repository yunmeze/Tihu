# E/S idle fixed-shadow CPU study — split decision

## Decision and boundary

S: prepared for independent native diagnostic only. No ordinary activation or art approval. Detached interface: `s_diagnostic_candidate/manifest.json`. It binds the current approved S body, four IDs17–20, 12-tick schedule, (-16,-64) draw offset, current world code and the existing receiver chain. The interface is not a production manifest.

E: CPU research only; **do not enter GPU or production with this proposed line**. Do not clip low-alpha pixels, clamp slope to the helper limit, borrow SE geometry, shift body or pin feet per phase. A later method decision is required.

This study changed no production assets/scripts, map, original source, timing or Git. Initial measurements emitted JSON/NPZ only; the parent subsequently explicitly requested same-scale technical previews, which were built from existing pixels and CPU alpha projection. No generated art or GUI was used. Original frozen archives remain untouched.

## Actual visible sole proxies (logical local frame coordinates)

Measurements read the actual approved d4 atlas, not its earlier raw registration. Fixed ROIs (x0,y0,x1,y1): E near(29,81,45,91), far(41.5,73,51,80); S left(26,78,38,87), right(42,80,54,91). Within each ROI, use the bottommost alpha>=128 row, mean x of its retained texel centers, and that row's lower edge as y. All bottom rows are strictly inside their ROIs. Alpha thresholds only diagnose uncertainty; alpha>=128 is fixed before fitting, not selected to pass a gate. Every alpha>0 pixel remains in the actual projection and envelope.

| Phase | Near/left sole | Far/right sole |
|---|---|---|
| E9 | (40.875,87.500) | (44.875,79.750) |
| E10 | (40.625,87.500) | (44.750,79.500) |
| E11 | (40.4583,87.500) | (44.750,79.500) |
| E12 | (40.000,87.500) | (44.625,79.500) |
| S17 | (32.125,83.500) | (47.875,87.250) |
| S18 | (31.750,82.750) | (48.125,87.500) |
| S19 | (32.000,83.250) | (48.125,87.250) |
| S20 | (32.125,83.500) | (48.000,87.500) |

These are visible lower-contour proxies, not measured physical contacts or surveyed ground. Manual ROI/interpretation allowance is ±1 x / ±.75 y logical units; d4 grid is .25 units. The original E registration's boot surface terminals near y85.5/77.6 are not the actual d4 bottom contours near87.5/79.5, and were not silently substituted.

One least-squares line fits all eight points per direction, fixed for every phase:
- E ref(40,88.35161219824812), slope −1.8399792088740314; maximum y residual .851612, RMS .456457, maximum projected proxy displacement1.669355.
- S ref(40,85.30847442818121), slope +.2576365964009885; maximum y residual .432973, RMS .206750, maximum projected proxy displacement .848726.
- Cast(1.2,.55), opacity.25, logical blur.8, raw blur3.2, tint(.035,.045,.055) remain common and fixed. Sun does not rotate with facing.

## Matrix/height and uncertainty

For line y=s*x+b, the legacy helper uses A=[[1+1.2s,-1.2],[1.55s,-.55]], T=[1.2b,1.55b]. Its determinant is1.2s−.55. Both nominal matrices are invertible; an affine map does not locally fold. E det−2.757975; S det−.240836. S is more compressed than SE, so visual thinness still needs native review. Do not change light to make it thicker.

E is close to the helper's absolute-slope limit2. Threshold64/128/192/254 fits give−1.733712/−1.839979/−1.770591/−1.434548. A conservative systematic pair-mean uncertainty calculation using ±1x/±.75y gives slope interval−4.1751..−1.0283, not a confidence interval or authorized alternate line. This exceeds the helper bound and is a method risk.

S corresponding threshold slopes are+.262371/+.257637/+.254194/+.253881. The same conservative bound is+.14558..+.40089, below the singular slope .458333 and within helper2; smallest possible absolute determinant within that bound remains approximately .069. This does not authorize varying S line parameters at runtime.

E has1.92–2.30% of opaque alpha>=128 texels below its proxy line; minimum proxy height−6.0733. Such texels project toward the opposite side of the receiver line. No geometry is discarded, reflected, height-clamped or rescued. S minimum−.41746, below-line fraction .0099–.1176%; this is a residual rather than proof of true grounding. See `uncertainty-and-overlap.json`.

## Why E's full envelope is tall

The full four-phase E envelope is offset(33,64), size122×144.5 logical units,15686 d2 cells. E11 and E12 contain retained alpha=1 isolated pixels. E12 texel(45,93) determines its furthest projected y; its full-alpha per-phase height is141.35, while alpha>=128 diagnostic height is77.17. E11's corresponding heights are124.95 and76.67. Thresholded values explain attribution only and never replace the envelope. Steep E geometry also makes the opaque projected body approximately77 units tall, compared with about46 for S. No fold or special forward-height model is responsible for the outlier support.

S full-alpha envelope: offset(25.5,80),size106×47.5,4549 d2 cells before measurement-error support. Its detached candidate adds actual and projected proxy uncertainty rectangles plus the same1.8 padding, yielding4575 d2 cells and unchanged bounds. This is **read-error support with an exact fixed rendering line**, not an envelope authorizing all possible slopes. Every alpha>0 texel gets its full .25 square, .125 bilinear half-texel support and1.8 logical expansion (.8 blur+1 helper padding). Independent integral-image coverage checks cover every emitted AABB. No SE envelope participates.

## Known receiver and spatial results

The existing immutable allowed mask is1536×1024 at d2 over world[2496,960,768,512]. It contains1,330,424 allowed cells =332,606 logical square units;242,440 forbidden cells. The same original+new hall footprints expanded by4 logical units remain excluded. All existing runtime dependency hashes matched in this study. No receiver mask or old gate was changed, and v2's broader static receiver is not granted to E/S.

Whole-envelope eligibility at integer anchor cells (scan x50..69,y28..47 contains the entire feasible support range): E127, S175; only121/167 respectively have original flag0. This is placement math, **not** proof of route reachability. The blocked-flag positions are not a reason to alter collision. S's error-expanded envelope retains175 allowed integer anchors.

Both nominal direction envelopes pass61,39;63,41;61,37;63,38 and fractional61.6875,39.6875. Both reject62,36;66,35;66,36;51,39;67,45. Unknown, outside, malformed input, source body, or platform involvement must disable the whole cast. Fractional cell-area overlap uses floor/ceil support; no rounded center sampling, clipping through doors, or dropping only offending pixels.

## Other shadows and minimal hero-slot qualification

Five explicit locations x four hero phases x both directions were CPU-rendered with the existing9-tap kernel. All four Ling phases were included in pair comparisons. At61,37 the maximum tree overlap above alpha1/255 is5930 d2 samples for E,2200 for S. E at63,38 also overlaps the tree by up to762 samples. At61,39 and63,41 these sample cases have no other-caster overlap. Lack of overlap there is not a global claim: the separate conservative-envelope scan lists potential Fang/Ling/tree intersections throughout eligible positions.

Existing common-light max after each caster's blur still caps opacity at.25 regardless of overlap. Do not add opacity or a fifth slot. The minimal extension is a mutually exclusive S qualification branch supplying the existing hero slot0; SE remains its existing branch and E remains off. Keep [hero,Fang,Ling,tree] descriptors, reset the hero descriptor every evaluation, bind S atlas+manifest+full group+line+envelope+unchanged receiver SHA before publication. Other slots retain independent gates/preferences and original draw order. No duplicate source checker is allowed when the new S body supplies its own complete head/body.

The detached contract lists missing-resource, all-or-none fallback, source/S-toggle, return-to-supported-direction, fractional boundary, stair and turn tests. It grants no ordinary promotion. Packed export, unknown receiver and original-EXE timing equivalence remain unverified and must not be advertised.

## Evidence and technical previews

- `measurements.json`: exact source-byte8-frame checks, real atlas hashes, all phase points, matrices, envelopes, eligible anchors and CPU overlap samples.
- `uncertainty-and-overlap.json`: systematic read-error interval, negative proxy heights, and conservative static overlap opportunities.
- `alpha-envelope-attribution.json`: every phase's full/thresholded alpha bounds and outlier source texels.
- `s_diagnostic_candidate/manifest.json` and `envelope.png`: detached S input package, current SHA chain and native checklist.
- `Project/diagnostics/earth-es-idle-shadow-study-v1/{e,s}-source-body-fixed-shadow-2x.png`: original complete frame / unchanged candidate atlas / candidate+CPU projection at the same2× logical scale and same frame origin. Orange line is a proxy, red marker is visible sole, green is its projection. Original checker remains only in the explicitly original row.

The original source proof decodes body+head directly from lpRes at native offsets into128×128 and byte-compares all8 complete frames with frozen source inputs. Index18 partitions recompose exactly, but its shadow semantics remain a strong inference, not original native-renderer proof. No indexed/color threshold removal is applied to any candidate atlas.

## Freeze decision after parent image review

Parent inspected both CPU boards and authorized the sole native runner to test S independently after its current tree test. E remains CPU-only with no GPU or production activation. **Invertibility and conservative coverage do not prove a visually reasonable shadow shape.** S appears thin/long while E is wider, and the facing transition changes apparent form substantially despite unchanged sunlight; native turning, contact, outline and shared-light consistency remain visual acceptance requirements. This freezes research inputs, not art acceptance.
