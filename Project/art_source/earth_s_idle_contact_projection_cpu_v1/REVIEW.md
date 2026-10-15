# S-only CPU contact projection experiment — mathematical pass, visual risk open

## Result

The new fixed shadow-only map visibly restores a wider recognizable body silhouette compared with the rejected narrow S cast. It is not approved art or a production implementation. In the lower-leg bridge, approximately1.14–1.15% of opaque texels have local anisotropy above10; maximum opaque anisotropy reaches53.18. A strictly negative Jacobian prevents folds but does **not** prevent severe shear. This risk is retained explicitly; no parameters were adjusted after viewing the result.

Only S idle17–20 is studied. E/SE ordinary shadows, all body RGBA, timing, positions, map flags and previous frozen source files remain unchanged. All new masks/images/arrays are under `diagnostics/earth-s-idle-contact-projection-cpu-v1`. No GUI, native renderer or Git was used.

## Parameter source, fixed before implementation

`PREIMPLEMENTATION_PLAN.md` was written before the executable experiment, SHA a8e576e2fa9469b994070224bfc61f63ebf85a77f74b7e22e38a81dcc122a62c.

The same eight previously measured S sole points determine b0=85.3125, left b=83.25 and right b=87.375. No new point/threshold fit was used. y60 is the first four-phase all-alpha transparent leg split at x40. y80=floor(minimum sole y82.75)−2 reserves a bottom contact band. Transition is linear over20logical pixels and unchanged across phases.

Invariant t=1.55x−1.2y. For every positive-alpha lower texel(y>=80), left/right invariant extrema plus fulltexel and bilinear support produce the common transparent interval[−39.46875,−35.46875]. f(t) interpolates fixed offsets−2.0625..+2.0625 across that interval. b=b0+w(y)f(t), q=p+(1.2,1.55)(b−y). This changes only where source alpha casts a shadow. It does not redraw, cut or warp the visible character.

The three sampling owners cover the source domain exactly: left contact lane; right contact lane; body/remainder including the central transition lane. They are mathematical ownership regions, **not anatomical layers**. In the transition above y80, invariant lanes can cross visible lower-leg alpha. That causes the reported localized shear; it is not hidden behind a claim of anatomical segmentation.

## Continuity, inverse uniqueness and alpha coverage

- b and q are continuous at y60,y80,tL,tR. One-sided derivatives can differ; the model is C0, not asserted C1.
- t is invariant under q. For fixed t, qy is continuous and strictly decreasing in source y. Analytic inverse selection is therefore globally unique; no competing inverse is discarded or visually selected.
- det(J)=−.55+1.55w'f, bounded[−.70984375,−.39015625] everywhere away from derivative joins. Both one-sided determinants at joins satisfy the same strictly negative bound.
- 200,000 random forward/inverse checks: maximum error1.5632e−13 logical units. Numerical derivative check maximum matrix error3.219e−9. Across1e−7 perturbations at each boundary, maximum mapped separation7.49e−7, consistent with continuity rather than a fixed jump.
- Source alpha>0 counts are22166/22012/22194/21987; every texel belongs to exactly one owner, including isolated low-alpha samples.
- Original full-frame bilinear alpha is sampled, then restricted by unique ownership. At source texel centers and40,000 fractional samples per phase, partition maximum and sum both exactly reproduce the original sampled alpha. Independently filtered cut atlases are not used.
- This is source-alpha preservation and complete support, **not conservation of projected area or integrated darkness**. Changing projection legitimately changes projected area.
- Every tap first forms one hero coverage from the owners. The original normalized9tap blur and opacity.25 apply once, then the result participates in external max. No new caster slot, separate contact opacity, ellipse, connecting stroke, alpha threshold deletion or per-phase foot pin is introduced.

## Contact and visual findings

Fixed proxy-to-projected-proxy displacement by phase:
- S17 maximum .4901logical
- S18 maximum .9801logical; left boot delta(+.600,+.775)
- S19 maximum .2450logical
- S20 maximum .4901logical

The original unmodified S18 left sole is higher than the fixed four-phase left baseline. This residual is retained. New shadow alpha sampled at the eight visible sole proxies ranges.0365–.1838 after blur/opacity; it is nonzero at each point, but this does not establish exact physical grounding or guarantee every sole edge has contact. No zero-gap claim is made.

`four-phase-off-old-new-2x.png` contains three rows at identical origin/scale: no shadow; rejected old S line; new map. Both shadow methods sample the same approved S atlas. The new shape has distinguishable body width and leg branches instead of one thin strip. The bridge near the feet remains a possible artificial narrowing/bend; high anisotropy is explicitly reported despite the lack of a geometric seam or fold. `contact-detail-ENLARGED-from-2x.png` is labeled enlargement, not an independent4x render.

The current experiment does not modify SE to match S, and does not solve E. A future native comparison must keep the current ordinary SE reference unchanged. CPU improvement does not establish acceptable SE↔S turning consistency.

## Complete envelope and unchanged domain

Every alpha>0 raw texel contributes its full area plus.125logical bilinear support. Nonlinear projection uses conservative interval arithmetic over each support box, plus1.8logical blur/helper padding; all four phases and visible/projected proxy read-error boxes are unioned. Independent AABB coverage and mapped-corner/midpoint checks pass. There is no thresholded silhouette envelope.

Envelope: offset(26.5,79), size104×48logical,208×96 at d2,6901 positive mask cells. This is more occupied support than the previous S line envelope despite comparable outer dimensions.

Old allowed mask bytes remain unchanged. The new envelope admits171 integer actor positions in the bounded complete scan, compared with175 for the previous S candidate. Four previously admitted positions are now rejected: (61,33),(62,35),(62,37),(65,37). No receiver expansion compensates for these losses.

Pass:61,39;63,41;61,37;63,38; fractional61.6875,39.6875.
Fail whole cast:62,36;66,35;66,36;51,39;67,45.

Qualification is geometry math, not route completion or permission to alter blocked flags. Unknown inputs, platforms, outside-domain and any partial intersection must clear the entire caster. No shadow clipping is permitted.

## Existing caster max and cost

Actual current Fang/Ling/tree textures and descriptors were CPU sampled in the hero-local output region at61,39;61,37;63,38, across all four S and four Ling phases. With static casters assumed eligible, hero/tree overlap at61,37 reaches3741 d2 samples above alpha1/255. Combined alpha stays at most.248416 in these samples and is theoretically bounded by.25. Independent over-compositing would reach about.4343. Other static eligibility rules remain separate; this test does not grant them new areas.

The new map can use one analytic inverse and one alpha texture fetch per blur tap:9 hero texture reads, not27. It adds invariant/transition arithmetic and piecewise inverse selection compared with the previous affine transform. CPU old+new preview kernels together cost roughly.17–.19seconds per352×320 phase on this executor; that is not native GPU timing.

With a verified tight208×96 output bound at2x, a future implementation would budget roughly179,712 hero texture fetches/frame, approximately182,457 allowing one extra cell per axis for fractional placement. This is a bound-based estimate, not measured shader performance. Existing four-caster shader/descriptor currently expects an affine hero, so native adoption would require separately reviewed code and hash bindings. No such runtime change is made here.

## Deliverables

- `PREIMPLEMENTATION_PLAN.md`: frozen source rules and mathematical conditions
- `experiment.py`: reproducible CPU experiment with assertions and unchanged-input checks
- `Project/diagnostics/earth-s-idle-contact-projection-cpu-v1/report.json`: complete numeric findings and input hashes
- `.../four-phase-off-old-new-2x.png`: same-scale technical comparison
- `.../contact-detail-ENLARGED-from-2x.png`: enlarged contact detail
- `.../full-four-phase-envelope.png`: diagnostic-only full support mask
- `.../phase-17-alpha.npz` through`phase-20-alpha.npz`: old/new postblur alpha arrays

No automatic follow-on parameter sweep, GPU work or promotion is authorized by this report. The localized shear issue should be reviewed before deciding whether this candidate merits native testing.
