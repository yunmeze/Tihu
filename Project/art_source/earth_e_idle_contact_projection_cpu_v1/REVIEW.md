# E idle invariant-contact CPU feasibility, v1

## Decision

CPU map is continuous and uniquely invertible at the fixed measured parameters. It is **not ready for GPU or ordinary promotion**. The distal E silhouette remains notably thin relative to S/SE, and whole-boot contact support bands overlap. The alternative stabilizes only local sole cores while distorting a substantial visible knee/shin/boot region. Do not tune the parameters or widen the domain to force visual acceptance.

Only unchanged E idle9–12 is sampled. Production E shadow remains off. No production code/assets, SE/S source body, source timing/position or old receiver masks were changed. CPU-derived visualizations are technical diagnostics, not generated character art.

## Real four-phase contact evidence

Original frozen near boot ROI [29,81,45,91], far [41.5,73,51,80], logical128 frame, actual d4 alpha. Visible bottom proxy is mean x of bottom alpha>=128 row, lower pixel edge y:

| phase | near | far |
|---|---|---|
|9|(40.875,87.5)|(44.875,79.75)|
|10|(40.625,87.5)|(44.75,79.5)|
|11|(40.4583333333,87.5)|(44.75,79.5)|
|12|(40,87.5)|(44.625,79.5)|

These are visual proxies, not recovered physical soles. Reading uncertainty ±1x/.75y. Four-phase means near87.5, far79.5625, pooled B83.53125. No per-frame reanchoring.

Whole ROI nonzero-alpha t=1.55x−1.2y center ranges: near[-54.46875,-31.95625], far[-31.33125,-15.55625]. Gap .625 is smaller than 2×.6875 fulltexel/bilinear support: expanded ranges overlap by .75. Thus there is NO proven transparent separation permitting both entire boots to be assigned independent constant-height planes.

Sole proxy error boxes remain disjoint in t. For each point expand ±(1,.75), then another .6875 support: near upper bound TL−38.50625; far lower bound TR−29.36875. These define **contact cores**, not complete boot silhouettes. Interpolation between them crosses visible boot pixels (phase9 near285 opaque pixels, far7; full per-phase counts in diagnostic JSON). No source alpha is erased to conceal this.

## Parameter provenance and price of invertibility

All values were recorded in PREIMPLEMENTATION_PLAN.md before rendering.

Transition y60..76, L16: start is the visible knee/upper-shin boundary in the four-phase source, below hanging hand/upper trouser area (manual anatomy boundary uncertainty about1–2px). End76 = floor(min farsole79.5−.75 reading error)−2 clearance. This transition is above the feet’s transparent split. It acts on visible knee/shin armor:2567–2625 opaque texels per phase, about19–20% of opaque source. The t bridge further affects1108–1145 opaque lower-body texels. It is a shadow-only sampling approximation, not a character layer edit.

No-fold requires L>1.55×3.96875/.55=11.184659. Current L16 gives strict margin .165527. Holding heights fixed, ±1 start/end reading uncertainty (L14 worst) leaves .110603; ±2 (L12) leaves only .037370. Including ±.75 sole-height uncertainty gives Dmax4.71875 and requires L>13.298295. Joint±2 transition reading plus boot-height error can therefore invalidate the robust no-fold guarantee. We do not expand the transition into thigh/hand/torso to hide this uncertainty.

## Exact map and inverse

p=(x,y), t=1.55x−1.2y, f=3.96875−7.9375 clamp((t+38.50625)/9.1375,0,1), w=clamp((y−60)/16,0,1).

b=83.53125+w f; h=b−y; q=p+(1.2,1.55)h. Negative h is retained, never clipped.

Inverse uses invariant t=1.55qx−1.2qy and same f:
- q0=96.4734375; q1=87.6734375+1.55f.
- qy>=q0: y=(129.4734375−qy)/.55.
- qy<=q1: y=(129.4734375+1.55f−qy)/.55.
- otherwise y=(qy−129.4734375+5.8125f)/(−.55+.096875f).
- x=(t+1.2y)/1.55.

For fixed t, qy is strictly decreasing. Jacobian determinant range[-.93447265625,-.16552734375]. Boundaries are C0 continuous, derivative may jump. 200k-point inverse residual≤1.99e−13; numerical Jacobian residual≤2.93e−9; boundary epsilon distances≤3.08e−7. Labels for near/far/remainder are exclusive restrictions of one original bilinear-alpha sample. Same-transform sum and max reconstruct original alpha exactly, including fractional samples and every alpha1 speck.

At each ground q, sample9 taps q+(.8i,.8j), invert EACH tap, raw p×4, reject outside[0,512)² before clamping[.5,511.5], add raw phase region (512i,0), divide2048×512, bilinearLOD0. Weights[1,2,1]²/16. Union ownership first, blur then opacity.25 once. No source-space blur shortcut or added opacity.

## Measured visual/geometry costs

Four phase full-alpha texel counts14425/14101/14262/14306, all retained; alpha1 counts412/273/371/352. E12 distant specks still affect envelope: projected minx12.325. Their visibility being tiny does not authorize dropping them.

Nominal foot-proxy displacement: E9 .367543, E10–12 .122514 logical. Across the fixed reading-error box, maximum displacements rise to1.837715 /1.592687 /1.592687 /1.592687. This is not exact foot pinning.

Opaque anisotropy>10:746/720/705/696 texels, about5.2–5.6% (S experiment~1.15%). Max35.44077. Source x31.875..44.375,y72.625..87.125 (raw rows290..348), projected q around[41.857,79.935,48.002,94.094]. It includes shin and near boot, not merely invisible gap. Technical source overlay identifies fixed boundaries for inspection.

Same2x source/ground-space comparison SE13→S17→E9→S17→SE13 keeps approved S and original SE formulas untouched. Visual threshold1/255 is diagnostic only:
- total visible shadow area: SE1548.5,S1015.5,E751.25 logical².
- distal x>=65 perpendicular-to-light width: SE24.696,S16.022,E8.333.
- distal area: SE1166,S770.75,E461.5 logical².

E is still approximately half S’s distal thickness. The upper body has w=0, so adjusting only foot transition will not widen the distal side-view body silhouette. This is a genuine orientation/source-plane limitation rather than a reason to reuse SE envelope, increase opacity, discard alpha or warp body. Static comparison predicts visible turn contraction; temporal native acceptability remains unknown.

## Whole-envelope receiver qualification

Every nonzero texel’s full footprint plus .125bilinear support is mapped with conservative interval arithmetic; pad±1.8 ground (.8 kernel plus safety), add both original and projected ±(1,.75) sole reading boxes. d2 interval raster verified to cover all rectangles.

Envelope offset(9.5,75.5),size119×49,238×98 bitmap,5955positive cells. SHA313bbc55f8cd9870528bfe1b21a6bb7c165ac198915f7288e3ba8983d2da4601. Original conservative allowed/forbidden receiver unchanged:159 integer positions qualify, versus S171. Complete coordinate list in report.json. Fractional qualification checks floor/ceil area overlap, not center-only probes. Pass61,39 /63,41 /61,37 /63,38 /61.6875,39.6875. Fail62,36 /66,35 /66,36 /51,39 /67,45. Never clip the shadow to pass.

Current cost estimate: nine nonlinear inverses inside a future complete238×98 d2 AABB would be~209916 evaluations/frame; no runtime implementation or measured GPU timing. Current CPU previews do not imply max-compositor/native acceptance.

## Deliverables and next boundary

Diagnostics directory diagnostics/earth-e-idle-contact-projection-cpu-v1 contains four-phase off/old/new same2x preview, SE/S/E turn strip, enlarged contacts, source ROI/transition overlay, full envelope, phase alpha NPZs, numeric reports and logs. Old E−1.839979 comparator preserves its fullalpha and is labelled rejected.

Recommendation: parent review the thin distal silhouette and overlapping whole-boot support limitation before authorizing anything further. E remains CPU-only. No more parameter exploration was performed after viewing this candidate.
