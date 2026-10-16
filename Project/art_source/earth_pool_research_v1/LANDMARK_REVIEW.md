# Read-only uniform-registration diagnosis

## Corrected interpretation

Different output resolution alone is **not** a geometry failure: a single full-canvas density mapping can accommodate a supported square output size. The original rejection still applies to the **frozen placement**, but neither the resolution mismatch nor the earlier alpha IoU proves nonuniform shape deformation. The source alpha contains a grass apron absent from this candidate, so alpha-bound fitting would be inappropriate.

The dominant mismatch appears to be uniform scale and translation. Exact geometry remains unproven. Raw remains unchanged; no registration, transformed output, adoption, split, cleanup or second generation was made.

## Method

Manually read homologous visible rim features in the source native coordinate system and the raw image. Fit only scalar density plus XY translation, with no rotation, anisotropy, warp, source-apron alpha, or bounding-box optimization. Three training landmarks: upper outer rim crown, left outer rim extremum, right outer rim extremum. Hold out four rim features (deep notch, front basin bottom, neck shoulder, lower-left bank) and all six aquatic patch centroids. Complete points and predictions are in landmark-diagnostic.json; reproducible numeric calculation in diagnose_landmarks.py.

Manual uncertainty: approximately ±4 source logical units per axis and ±8 raw pixels per axis, due to low-resolution source stones and ambiguous patch centroids. These are conservative visual-read tolerances, not statistical confidence intervals. Numbers below do not warrant subpixel precision despite stored floating-point arithmetic.

## Findings

- Fitted raw density: approximately 3.232 pixels per source logical unit.
- Fitted raw position of source-group origin: approximately (109.19,259.35).
- Proposed diagnostic map: world = (3086,1800) + (raw − (109.19,259.35)) / 3.232.
- Training RMS: 2.98 logical units; maximum 3.99.
- Held-out rim RMS: 5.23 logical units; maximum 7.20 at deep notch. At density2 these are 10.45 and 14.39 pixels.
- Held-out plants RMS: 5.05 logical units; maximum 7.62 at lower-left patch. At density2 these are 10.10 and 15.24 pixels.
- Notch residual points inward-left/down relative to the scalar prediction; lower-left bank residual differs. Could be modest local deformation, stone-boundary ambiguity, or manual-read error. No evidence here establishes zero deformation.
- Patch layout is substantially retained under scalar mapping. Five of six patch residuals point rightward, so foliage may have a small common drift relative to rim registration. Individual plant size/leaf counts are not guaranteed by centroid agreement.

A scalar registration is **plausible as a separate research proposal**, not justified as exact production registration by these coarse measurements. Recommended interpretation is approximately preserved design plus changed framing, with possible several-logical-unit local drift. Further explicit source/candidate rim-coordinate inspection would be necessary before asserting precise notch, waterline, height or plant agreement. Do not disguise this uncertainty with a fitted outline.

## Alpha at actual density2

Inspecting raw edges shows contamination on left/bottom at alpha=1 only; top/right edges are zero. Mapping the full raw canvas uniformly at the fitted density onto an approximately 776×776 density2 diagnostic grid (nearest sampling, in-memory analysis only) leaves 14 contaminated left-edge pixels and 7 bottom-edge pixels. No edge pixels exceed alpha8. This is a strict exterior-alpha failure but visually negligible; no contamination removed. Main solid object is not clipped. Counts depend on downsampling phase/filter; raw alpha=1 evidence is authoritative. No density2 image was saved and this analysis is not an adopted output mapping.

## Separate proposal, not executed

Retain original raw and frozen mapping evidence. If a later decision permits revising registration, use one scalar density/translation for the entire raw canvas, never a per-owner or per-region fit. At this stage the measured scalar map is an approximate proposal with residuals above; it does not authorize an exact-match claim, outline rescue, alpha cleanup or splitting.
