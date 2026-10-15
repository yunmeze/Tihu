# S-only CPU experiment: fixed body baseline and contact lanes

Authorization: parent approved S-only CPU experiment, no GUI/production changes. Existing E/SE shadows and complete S body RGBA remain unchanged. This is shadow sampling only, unrelated to any character-layer/action proposal. No output mask may be written outside diagnostics. Prior frozen study remains immutable.

## Parameters fixed before implementation

Source is approved assets/earth/hero/s_idle_v1/body.png, SHA f0ca3b8a554c175f3d0085f4a4fa55a6d192132d6cfeb443d3242bd3ab54a12e. Four phases17–20, d4, same12tick clock and(-16,-64) draw offset.

Use previous fixed alpha>=128 bottom-row visible points; no new threshold/point selection. Left y mean83.25, right y mean87.375, pooled mean b0=85.3125. Both foot offsets from b0 are exactly ±2.0625.

All parameters shared across four phases. Source all-alpha union first has a positive-width transparent x=40 leg gap at y60; y0=60 starts lower-leg transition. y1=floor(minimum measured sole y82.75)−2=80 ends it, reserving at least2 logical pixels below the transition for contact. Linear w=clamp((y−60)/20,0,1); no per-phase parameter fit or aesthetic sweep.

A direct x-lane interpolation can fold because the gap is narrow. Instead use invariant t=1.55x−1.2y, preserved by q=p+(1.2,1.55)(b−y). In all four phases at y>=80, all positive-alpha left(x<40) texel centers have maximum t−40.15625; right(x>=40) minimum t−34.78125. Include fulltexel+bilinear support .25logical in each axis, giving invariant support margin .6875. Choose fixed blend endpoints tL=−39.46875, tR=−35.46875, exactly the remaining4logical invariant gap, without trimming alpha. f(t)=−2.0625 below tL, +2.0625 above tR, linear between. b(x,y)=85.3125+w(y)f(t).

Three shadow-sampling ownership regions: left contact lane(y>=60,t<=tL); right contact lane(y>=60,t>=tR); body/remainder including central transition lane. All use the same continuous map. Every source coordinate has exactly one owner; no soft alpha masks. In the central lane lower-leg shadows may shear, and upper parts of a visible leg may temporarily lie in a different invariant lane; labels do not claim anatomical segmentation or 3D recovery.

## Mathematical preconditions

- q=(x+1.2(b−y), y+1.55(b−y)). The physical cast input remains(1.2,.55).
- b is continuous at y60/y80 and tL/tR; its derivative may jump, but no coverage seam may arise.
- det(J)=−.55+1.55w'(y)f(t), because invariant-gradient terms cancel. Within the band: range[−.70984375,−.39015625]; outside:−.55. Strict negative margin .39015625. No clamp of a bad Jacobian or feet is allowed.
- Invariant t is preserved. For fixed t, q_y(y) is continuous and strictly decreasing across the three y intervals, with slopes matching those determinants. Thus its inverse is globally unique, not merely piecewise invertible. Solve each interval analytically; never choose a prettiest inverse or drop ambiguous samples.
- Partition same-transform reconstruction must exactly reproduce full bilinear source alpha. Sample original alpha then restrict by unique source ownership; do not filter three cut atlases independently.
- Union branch coverage first (max; only one owner under this globally one-to-one map), then original9tap blur and.25opacity. External composition remains max with Fang/Ling/tree; no extra hero slot or darkening.

## Required evidence and failure criteria

Inverse round-trip and boundary continuity; analytic negative determinant and numerical Jacobian check; complete positive-alpha texel ownership including speckles; same-transform alpha reconstruction at raw centers and fractional samples; actual boot residuals under fixed map; four same-scale old/new/off previews; local shear/condition-number report.

Build a conservative all-four-phase envelope using every alpha>0 texel's full area plus bilinear support, interval bounds of the nonlinear map, and1.8logical blur/padding. Add existing proxy reading uncertainty support. Old allowed/forbidden mask bytes and all current body bytes must remain identical. Entire envelope must fit; never clip, enlarge receiver or change source flags. This is only an exact rendering-support envelope for this fixed candidate, not all conceivable parameter errors.

If image remains too thin, bridge bends/tears, fixed contacts drift, or envelope is rejected, record the failure without a parameter sweep or production promotion. Report runtime cost estimates as estimates; CPU preview is not native performance or visual acceptance.
