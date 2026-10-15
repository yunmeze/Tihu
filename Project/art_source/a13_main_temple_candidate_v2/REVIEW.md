# Temple v2: one authorized redraw, geometry not accepted

One image_gen operation used original source geometry as input1 and v1 materials as input2. Prompt and input hashes are recorded. raw.png is immutable generated RGBA1372×1147, SHA3bf1876fd6b76831216668a645f4120dcbc737cfa2ba258e0fc3d2fee705c3e1. No second retry or runtime modification.

Both doors/stairs and the material language remain clear, with no broad soil apron or checker cast. However the result still visibly inherits enlarged molded stair shoes and the thick plinth from v1. It did not reliably return to original relative support geometry. Absence of a dirty ground patch is not sufficient for structural acceptance.

Manual source/material-point reads retain source4–5px/candidate7–10rawpx uncertainty. The front pillar's lower corner is partly obscured by the railing finial: its visible lower-left white-column edge is used, not the finial center. Upper-tread correspondence is still less certain. No metric is exact survey evidence.

Common8-point scale0.560485/translation[6.688,-1.308] gives RMS12.28/max21.58 source px, essentially no useful structural improvement over v1. Independent diagnostic fits:
- Support group scale0.533688, RMS6.12; right upper tread still approximately9.2px vertical residual.
- Roof/eave group scale0.577507, RMS4.00; applying that common fit to supports leaves left stair approximately27–32px displaced.

These fits are deliberately independent checks, not pieces of a composite transformation. No independent roof/support scale is applied. Their incompatibility and visible thick-stair/plinth inheritance keep v2 out of runtime. The original layer0 strip overlay remains diagnostic only; no30-owner candidate partition is created.

No alpha>32 pixels touch the four edges, but requested generous margin was not fully delivered; exact measured bounds/margins are in independent-support-roof-check.json. This threshold is measurement only: original alpha/RGB were never modified, cropped or thresholded.

Ignored evidence: diagnostics/art_source/a13-main-temple/candidate-v2-preview.jpg, candidate-v2-common-scale-ab.jpg, candidate-v2-landmark-local-board.png and candidate-v2-layer0-rectangle-diagnostic.jpg. Reproduce numerical checks with measure_candidate.py followed by check_groups.py. The raw/source/v1 files and original source contract remain unchanged. Result is submitted as research, pending parent decision; no further generation is implied.
