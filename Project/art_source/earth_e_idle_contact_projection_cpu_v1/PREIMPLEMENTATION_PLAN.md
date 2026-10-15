# E-only feasibility experiment, fixed before rendering

Source: unchanged E idle9–12 d4 actual RGBA. Fixed light (1.2,.55), opacity .25, ground-space blur .8. No runtime activation, GPU, character alteration or generated art.

Four-phase boot reads are frozen from original E study, near ROI [29,81,45,91], far [41.5,73,51,80]. Near mean bottom87.5, far79.5625, pooled B83.53125, D3.96875. Read-point uncertainty ±(1,.75) logical.

Important negative result: whole near/far boot alpha center t ranges [-54.46875,-31.95625],[-31.33125,-15.55625]. Expanded by .6875 per side for full texel/bilinear support they OVERLAP .75. Therefore this experiment cannot model the entire two boots as disjoint constant-height contact patches separated by transparency.

Experimental alternative is explicitly contact-core only. t=1.55x−1.2y; local core limits derive from all four boot points and ±(1,.75) read box plus .6875 support: TL=max(t_near)+3.1375=−38.50625; TR=min(t_far)−3.1375=−29.36875. f falls linearly from +3.96875 to −3.96875 across this band. This band crosses real lower-leg/boot alpha. It is NOT a transparent partition or accurate physical reconstruction. No alpha is removed.

Fixed transition y60..76. y60 is the visible knee/upper-shin boundary below the hanging hand and upper trouser area in the common four-frame source; coordinate identification uncertainty about1–2 logical pixels. End76 is floor(min farsole79.5−.75 readerror)−2 logical clearance. This begins above the separated-feet gap and spans knee/shin armor; it deliberately changes their shadow sampling. Using only separated lower boots would give an insufficient transition height. No post-render tuning.

L16 gives determinant range −.93447265625..−.16552734375 (exact formula −.55+1.55*f/L). Minimal no-fold L>11.184659. Boundary sensitivity ±1 each gives L14 and min margin .1106027; ±2 gives L12 and margin .0373698 with fixed measured boot heights. Joint boot-height uncertainty ±.75 would require L>13.2983; hence ±2 transition reading and boot uncertainty together can lose the guarantee. These are uncertainty costs, not alternate prettier parameter sets.

Use fixed map q=p+(1.2,1.55)*(B+w(y)f(t)−y), unique invariant-t inverse, full source alpha including far alpha1 speckles. Owner labels are sampling restrictions only. Verify identity reconstruction, continuity, numerical inverse, Jacobian and full texel interval coverage. Fullalpha envelopes include bilinear .125 support, ±1.8 ground padding and both projected/visible foot readerror boxes. Use original conservative receiver, no expansion or opaque cropping. Compare no shadow / rejected old slope / candidate at identical scale; assess S/SE size change without changing either.
