# Main temple candidate v1: one generation, pending geometry review

Exactly one image_gen call was made. raw.png is a byte-identical copy of the generated output, SHA3c33a3ed9c80ad9031b524f73b494c9276386d9c7f7c82e763420d31211eb0fe. prompt.txt records the actual tool prompt, not an earlier draft. generation-input.json stores the sole geometry input SHA, prompt SHA, output dimensions and transparency statistics. The source-group contract was not modified.

Actual result:1372×1146 RGBA. Both perpendicular doors/stairs, compound roof and quiet temple identity remain visible. Silver-grey structure, charcoal roofs, dark-red facade and warm doors are readable. The source ground apron/checker shadow is absent. There are sparse edge alpha pixels and four bottom-edge pixels above alpha32: do not silently crop, threshold alpha or declare a fully padded silhouette. No new ground cast was added.

## Geometry diagnostic only

measure_candidate.py uses one isotropic scale0.5627120211 and translation[14.9647,-2.4586] into the original796×665 source canvas. No rotation, shear, anisotropic scale, local warping or source-owner change. Only ignored diagnostic boards contain transformed renderings; raw remains unchanged.

Eight manual visible-feature readings yield RMS12.48 source pixels and max22.12px. The source uncertainty is4–5px and candidate7–10raw pixels. New stepped/molded stair rails change feature correspondence, particularly S1/S3 upper tread points; their reads are less certain and must not be treated as surveyed exact homologues. Left eave lip displacement is about22px and left stair readings about12–19px. These exceed a claim of perfect registration and are submitted for review, not hidden by a whole-building affine transform.

The independent original-layer0 rectangle overlay shows the candidate stair support surfaces do not align perfectly with all original narrow owner strips. Existing rectangle boundaries must not be used as a semantic cutout that blindly moves portions of railings or vertical risers to layer0. A later accepted candidate requires real support/vertical-plane ownership and original layer/y sorting, plus actual actor depth tests. No30-owner candidate registration has been produced and no depth PASS is claimed.

## Evidence (ignored diagnostics)

Project/diagnostics/art_source/a13-main-temple/
- candidate-v1-preview.jpg: grey-background material/alpha view
- candidate-v1-common-scale-ab.jpg: original versus common scale/translation diagnostic
- candidate-v1-landmark-local-board.png: candidate material-read locations
- candidate-v1-layer0-rectangle-diagnostic.jpg: original support ownership boundaries over the candidate

Source preview/landmark/layer boards remain alongside these. Re-run measure_candidate.py to reproduce numerical/technical diagnostic outputs. No runtime, original assets or collision changed. No additional generation is authorized by this record.
