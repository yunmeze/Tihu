# Round shrub v1: one generated whole-image candidate

Built-in imagegen was called once with source-composite.png as the sole shape and
camera reference, using the saved prompt and input hashes. The returned1363x1154
RGBA is copied byte-for-byte into raw.png. No color cleanup, alpha thresholding,
local deformation, re-generation, owner partition or shadow was used to obtain it.

Parent review accepted the whole/native-size silhouette and color as a bounded
working candidate at 2026-10-15T06:38:32Z. The round crown, low foliage boundary and
leaf volume read more coherently than source; abundant yellow-green new tips are
acceptable at native size. This does not approve runtime depth or a ground shadow.

## Shared transform, not root registration

One scale **0.09442870632672333**, source-composite-local translation
**(-4.022662889518415,-4.15486307837584)**. No rotation, shear or local correction.
The source green-dominant visible envelope measures120x100, using G>R and G>B
solely as a diagnostic. Candidate alpha>=96 bbox is(46,44)..(1310,1103). The fit
centers the envelope horizontally and aligns its lower boundary to source y100.
No source pixels or candidate alpha are removed by either measurement criterion.
The actual source root remains **null**: a lower foliage envelope is not a root.

The resulting world top-left for the selected(57,38) group is
(2690.9773371104817,1138.8451369216242). Native whole/partition sampling still
requires engine review. Independent linear-filtered owner textures can reveal
seams; nearest is the first technical partition comparison.

## Retained RGBA residuals

The white/star-shaped details are not all transparent display artifacts. The
reproducible white indicator (minRGB>=210,max−min<=30) finds555raw pixels with
alpha>=192. Large components include(400,687)..(421,702),158pixels/alpha236–250,
and(443,283)..(458,298),123pixels/alpha245–251. The measured native render contains
3such pixels with nearest and5with bilinear. Parent found only tiny isolated
points at native size, without a clear glow/star-effect reading. They remain in raw.

A saturated-green edge indicator (G>=220,R<=70,B<=100) finds2,829pixels, all at
alpha1..15; none at alpha>=16. Very faint alpha reaches the left/bottom raw canvas.
Main alpha>=96 has zero edge-touching pixels. These low-alpha fringes are retained.

## Reproduce

    python3 art_source/a13_round_shrub_candidate_v1/measure_candidate.py

This rewrites only measurement JSON and ignored diagnostic boards, never raw.
`geometry-diagnostic.json` records the transform/limits; `rgba-audit.json` records
threshold definitions, alpha bins, exact component boxes and native samples.
Local review boards are under diagnostics/art_source/a13-round-shrub/:
whole-and-native-review.png and native-{neutral,grass}-strip.png. The grass strip
uses original FloorBig406, explicitly not an accepted new-ground material claim.
The native sampling screenshots/boards are local review evidence, not production.

## Technical continuation

The authorized four-owner common-canvas partition is in technical_v1/. Its
registration and README describe source sorting, exact pixel ownership, the
common-origin sampling requirement and the single-instance runtime review gate.
The immutable three-file generation package remains unchanged.
