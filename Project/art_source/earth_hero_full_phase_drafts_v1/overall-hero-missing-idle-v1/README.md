# N / NE hero idle first draft

Status: **next-batch candidate; not running coverage, not exact-motion acceptance**. Frozen v6, original project, Godot runtime, main/shadow files and Git were not changed.

## Deliverables
- `registered/N/body.png`: 2048×512 RGBA, four 512×512 cells, native frame IDs 1–4.
- `registered/NE/body.png`: same layout, native frame IDs 5–8.
- `registered/N-NE-overview.png`: N row above NE row.
- `registered/{N,NE}/NNN.png`: eight individual registered frames.
- `raw/{N,NE}-fourphase.png`: unchanged built-in imagegen results, each **1254×1254**, 2×2 cells of 627². The request asked for 1024²; do not conflate request with actual output.
- `provenance/{N,NE}-actualargs.json`: complete exact prompts, reference paths and tool arguments used in the two completed built-in calls.
- `provenance/original-reference-contract.json`: native body/head offsets/rects, source hashes, compositing contract and per-phase original composite hashes.
- `provenance/original-movement.json`: full original contract snapshot.
- `provenance/generated-registration.json`: actual output hashes, regions, transforms, candidate anchors, shoe material extents and silhouette differences.
- `inputs/*original*`: full legally composed references, preserving original shadow pixels; no inferred feet recentering or source pose edits.

## Registration
Logical frame 128²; density 4; physical frame 512²; draw offset [-16,-64]; actor origin logical [16,64], physical [64,256]. Both directions use exactly the same isotropic full-cell resize 627→383. N uses fixed translation [20,14]; NE uses fixed [12,16], identically across each direction's four phases. This is a whole-image registration, with no local warp, mirroring, anatomical repainting, alpha deletion, per-phase recentering, or geometry generation. The native draw origin is not a measured boot contact. Generated raw origin is an estimated art registration, explicitly recorded.

## Review
Full sheets were visually reviewed before and after registration. N is a true back view; NE is right-facing three-quarter back. Modern short-dark-haired male, black/gray combat clothing, silver armor and red shoulder accents match the actual existing S/E/SE HD identity images. All heads and boots are complete. Each direction contains four independently generated phases, with visible subtle shoulder/arm/silhouette differences. Four distinct frame hashes and nonzero silhouette XOR are recorded; these prove nonduplication, **not** exact native movement fidelity.

This is a first-draft identity/direction completion candidate. Exact breathing phase equivalence, back boot/armor anatomy and in-engine cadence/registration remain review items. Native N has outward-foot asymmetry different from generated N; no local correction was performed. Extremely low-alpha isolated generated specks are retained so the raw and registered alpha are auditable. No cast shadow was requested/generated as a separate asset. Do not claim these two directions are accepted, integrated, or running until the next integration review.

## Reproduce deterministic preparation only
`python tools/extract_references.py` extracts and composes source references.
`python tools/register_frames.py` only splits and registers already generated raster results. Neither script draws character art or generates geometry. New art was made solely by the two built-in image generation calls.
