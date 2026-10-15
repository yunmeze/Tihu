# One-round main-temple structural edit proposal

Status: analysis only. No new image generation, asset transformation, runtime registration or modification to frozen v1/source files.

## What the current evidence actually supports

The all-eight-point common fit mixes roof/eave and support landmarks: scale0.562712, RMS12.48px. Under it the front pillar is close but both left stair points move left12–19px and the left eave lip moves right22px. Opposite residuals cannot be fixed by translating the entire building.

A separate diagnostic fit using only pillar plus four stair landmarks gives scale0.533637, RMS5.70px; its worst selected support residual is right upper tread+8.35px vertically. That is a5.2% smaller scale than the whole mixed fit. This suggests a changed support-to-roof proportion, not simply a uniform projective offset of a geometrically identical building. It is a diagnostic, not a proposed final shrink: shrinking to the supports would change the roof/body and needs its own independent roof checks.

For the current uncertain upper/lower pairs, left stair vector changes [27,88] to[33.76,88.35] at the mixed scale. Its vertical depth is almost unchanged, so the existing measurements do not establish uniform left-stair deepening. Right stair vector changes[-26,89] to[-35.45,84.97]. Lateral spread/orientation and new molded side caps contribute. The new plinth is straight and visually thicker; original loose-stone/grass landscaping must not be counted as structural height. Its exact additional height remains unmeasured rather than inferred from the entire alpha bbox.

S1/S3 and cheek-cap endpoints are not exact surveyed homologues. Before interpreting a lower RMS as acceptable, compare the same tread-to-platform edge material, not a rail cap in one image against a tread in the other. Source uncertainty4–5px and candidate7–10raw pixels remain in force.

## Which map supports must remain aligned

Left staircase layer0 originals:
-3971@66,34;3974@65,35;3975@66,35;3979@65,36;3980@66,36;3985@66,37.
Right staircase layer0 originals:
-3976@73,35;3981@73,36;3982@74,36;3986@74,37;3987@75,37;3989@74,38.

All12 original flag1 cells are statically reachable from61,39 using the current original-grid blocked flags and no-corner-cut rule. Exact per-cell source paths are in support-analysis.json. This is static connectivity, not a new GUI route pass.

Critical geometry is the top tread/platform junction and bottom ground tread edge on each side, plus continuous support between these ends and the two original door thresholds. Railings/pillar bases must remain beside these supports, not move across them. The12 cells are logical movement areas; a rectangular cell or a body/ground-shadow anchor is not itself a true support-face polygon. The source-grid board makes this distinction visible. Actor offset and foot position must be tested by runtime rather than guessed from the cell origin.

## Executable single-round plan, awaiting approval

Use two inputs to one complete-building imagegen operation:
1. Original source-composite.png as the sole geometry/layout/proportion authority.
2. Candidate v1 raw.png as material/color/finish reference only; explicitly do not inherit its enlarged molded bases, wider stair cheek caps, displaced support positions or changed roof-to-base proportions.

Prompt focus: redraw the entire source building in the already accepted clean silver-grey/charcoal/muted-dark-red material direction. Preserve source two door thresholds, stair widths, upper/lower tread edges, number and orientation of stair planes, front pillar base and relative facade-arm lengths. Keep source structural plinth height/footprint and railings. No new outer landing, thick projecting rail shoe, enlarged pedestal or extra step. Keep the full original compound roof and eave layout, but let support geometry remain the first hard condition. Do not attempt to repair by expanding the footprint or hiding edges behind dark shadow.

Require genuine transparent RGBA and a generous transparent margin on all sides, including the lowest structural base. No ground apron, loose-stone landscaping blanket or checker/cast shadow. Keep actual masonry/treads; do not remove the foundation itself. No text or control-point labels in the output. No per-part transformation after generation.

## Acceptance gates for that result

- First read equivalent visible material junctions, retaining uncertainty. Prefer ≤5 source px support residuals under one common scale/translation; uncertainty regions must plausibly overlap. A consistent support-edge shift beyond8px is a hold/review condition, not something to hide by fitting other points.
- Evaluate both supports and roof/pillars independently. Do not claim success solely from a support-only RMS or mix architectural redesign into a metric.
- New support geometry must cover the original traversed stair/platform route without moving risers/rails into the actor's footpath. Preserve flags and all30 original owner layer/y semantics. No global affine or actor priority override.
- Image alpha must contain no broad ground patch; structural ends may not be clipped at the image edge. Transparent padding is not a fix for missing structural pixels.
- Only after static checks: original/new actor depth at each stair bottom/top and both thresholds, followed by actual original paths. Numeric measurements alone do not authorize runtime selection.

If one round fails these structural checks, stop and report the specific inconsistent planes. No automatic repeated redraws or arbitrary plane slicing to rescue it.
