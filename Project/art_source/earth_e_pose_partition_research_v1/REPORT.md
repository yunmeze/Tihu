# E six-phase texture-suppressed pose research, no generation

## Delivered research boards
All visual outputs are diagnostic analysis, not final artwork or production assets.

Project/diagnostics/earth_e_pose_partition_research_v1/silhouette-full128-sixphase-4x-gray.png
Project/diagnostics/earth_e_pose_partition_research_v1/surface-core-full128-sixphase-4x-gray.png
Project/diagnostics/earth_e_pose_partition_research_v1/source-index18-excluded-full128-sixphase-4x-gray.png
Project/diagnostics/earth_e_pose_partition_research_v1/source-silhouette-surface-review.png

The last board stacks all six source frames, then exact silhouettes, then conservative visible-surface cores, all in the same coordinates. Transparent versions and individual128 frames also retained. Gray composites are preferable for inspection because transparent-viewer background may match unknown-region gray.

## What is and is not derived
Geometry comes ONLY from the audited index18-excluded source45–50 alpha. Alpha is copied byte-for-byte for each silhouette and surface map, so no original exterior edge is moved, enlarged, interpolated or replaced. Full128 canvas retained. Every cell displayed at4× nearest, no per-phase cropping or normalization. Index18's shadow meaning remains a strong inference, not original-renderer semantic certification.

All white-cloth, silver-waist and original material shading textures are removed in the silhouette and partition views. This does NOT remove the outer shape of those garments: the source silhouette still includes actual garment protrusions. “Texture-suppressed source silhouette” is accurate; “naked/anatomical body shape” is not.

Colors mark conservative manually read visible surface cores only:
- blue: visible near sleeve interior
- pink: visible near-hand group interior
- green: limited central upper-trouser surface
- gold: visible distal boot/toe surface
- ivory: small recognizable head interior
- gray: unknown/unclassified surfaces and uncertainty bands

Source-derived polygons/boxes are intersected with exact source alpha. A1px boundary of each proposed class is gray; overlaps also become unknown. These color boundaries are analytical proposals, not certified clothing-seam or anatomical boundaries. Torso/knees/shins, obscured limbs and broad lower-body interiors deliberately remain gray rather than invent hidden segmentation. No hip/knee/elbow skeleton, bilateral anatomical IDs, or ground-contact state is introduced. Boot classes are distal surface cores, not full foot outlines.

COORDINATE_PROOF.json records sourceSHA, all region proposals, class counts, uncertainty counts and exact-alpha checks. prepare.py reproduces all boards from the existing audited source partitions. Source support XOR=0 for each of6 frames. This verifies exact outer geometry and provenance, not correctness of every semantic color assignment.

## Usefulness compared with original textured input
45/48: exact outline makes opposite boot-height arrangement visible without a long silver stripe implying an armored thigh. Original short stride span remains untouched.
46/49: complete silhouettes preserve different long/short visible leg outlines; same-colored distal boot surfaces show height differences without pretending to identify permanent left/right anatomy.
47/50: negative space and distinct passing-foot order remain readable. No separating line is painted where limbs actually overlap.
Near hand sequence: the small pink regions retain the low hand-group progression33→37→44→49→43→36, with unchanged source outlines. Blue sleeve cores show backward-to-forward visible surface route without introducing the generic high horizontal fist.

The simplification reduces texture competition but also loses internal overlap/depth cues, especially knees/shins and near/far trouser surface exchange. Because hidden geometry is intentionally unknown, this is NOT a complete deterministic pose-control representation. Pairwise interpretation still needs the original pixel board as audit evidence; it should not be filled with invented bones to appear more complete.

## Recommendation / gate
This is a genuinely different visual encoding from repeating the old fully textured image+prompt, but no model comparison has been run, so improved generation adherence is unproven. Review the actual board before deciding whether a bounded control study is worthwhile. No prompt was submitted, no final art generated, no historical/production file changed. E walk stays full sourcefallback.
