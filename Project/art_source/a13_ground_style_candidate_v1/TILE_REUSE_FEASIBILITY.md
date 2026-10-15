# Ground v1 reuse feasibility — 2026-10-15

Status: style reference accepted; single-ID tile closure rejected after offline reassembly. This does not alter terrain or runtime.

## Controlled evidence
The 20-placement generated context was uniformly sampled at 480/1717 with zero translation. Position-specific cuts reconstruct that sampled context exactly. Original atlas/context/reused-ID reconstructions of all 143 placements also have zero error. The reuse defect is therefore not a crop-coordinate defect.

The context supplies 13 IDs. The first viewport additionally requires -594 at three placements and -586 at one placement. Their original RGBA is identical, but both remain explicit source fallback in this diagnostic. Six generated occurrences of grass -406 have different pixels (pairwise tile RGB MAE 12.26–15.05, edge ring 13.01–16.95 out of 255); -577 and -608 each also have two inconsistent generated occurrences.

A numerical search of 24 same-ID sample choices preserves 17 of 31 original position adjacencies. Twelve nonrepeated-ID adjacency pairs preserve their local generated neighbor pixels, but this is not a repeatable terrain set. Reuse of the least-discontinuous grass sample still creates obvious 96×64 dark-clump repetition. Road extension has rectangular lighting/material bands; four source-fallback placements add a further style break. The complete 143-placement comparison was visually reviewed. Lower average adjacent-pixel variation than the noisy source is not evidence of seamlessness.

## Bounded next design proposal, not implemented
Separate material repetition from original placement geometry. Evaluate a shared, low-contrast grass field and natural road-soil field sampled in continuous world coordinates, with explicit original road/grass/stone-edge semantic boundaries. Original cell/flag/placement/road width remain authoritative. Stone curb geometry must come from visible source edge evidence, not an inferred broad bounding box. Generated RGB stays immutable; any compositing mask is a separately reviewable technical semantic artifact, not painted repair to texture pixels.

First prove this on the same 20-placement road head and then the original 143 placements. Unknown edge pixels remain marked; do not silently convert every tan source pixel into pavement. A shared base would need its own generation approval and repeat/edge tests before any runtime use. No new generation is authorized by this document.

Acceptance must include native-scale repeated grass without obvious tile-sized clumps, both orientations of long road edge, curved/capped road head, joins into the four currently missing-ID placements, and shared-world sampling consistency across all neighboring placements. No per-tile brightness correction, independent generation per tile, or full-patch overlay may substitute for this evidence.

## Reproduction and limits
Ignored diagnostic: Project/diagnostics/art_source/a13-ground/tile-reuse-v1/audit.py, report.json and README.md. Boards: first-screen-comparison.png, context-comparison-board.png, grass-six-samples-board.png, worst-seams-board.png. Run the audit from the repository root. These are floor-only offline rasters, not native GUI or gameplay evidence.

Raw SHA256: 968d30767e40486774ab13de38f5203fa4c4765247b253d7df9e620e6301b86e. Raw and original assets remain unchanged.
