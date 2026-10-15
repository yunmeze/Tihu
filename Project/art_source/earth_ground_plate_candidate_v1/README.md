# Earth ground plate: first raw candidate

One built-in imagegen call, 2026-10-15. `raw.png` is the unchanged returned RGB image: **1536×1024**, mapped without warp to world `[2496,960,3264,1472]`, exactly **2 texels per logical unit**. SHA256: `c1970f3dc599c43dc47dff6f1d41f3051949e4c730fd53c5fcdadcd188d55fc7`.

This is a candidate ground image, not a Godot capture, installed terrain, final layout approval, or shared lighting proof. No layer/owner export or runtime change was made.

## Inputs and operation

- Exact actual prompt: `prompt.txt`.
- Tool mode, reference hashes, actual dimensions and immutable output path: `generation.json`.
- Source floor and source semantic board provided geometry only.
- Two exact unscaled crops from the accepted Earth concept provided concrete/grass materials only. Crop coordinates and hashes are in `inputs/reference-crops.json`. No whole concept, character, staircase or building geometry was supplied as a layout reference.
- The built-in result was copied to this directory unchanged; its original generated file was retained. There was no resize, warp, color correction or second generation.

## What the raw does and does not establish

The original diagonal capped road, broad grass region and grass interval toward the left stair remain recognizable. It did not add a connector path, people, buildings, large trees, props or large cast silhouettes. It replaced the tan road with coherent neutral-gray slabs.

The approximate source centerline lies close to the generated curb. Six manual central-curb read points differ by at most 2.5 logical pixels in Euclidean distance, against source uncertainty ±3 logical pixels and generated read uncertainty ±3 raw pixels. These finite-precision observations do not prove exact road width or boundary retention. The curb reads more pronounced, and local outer material edges fluctuate outside the approximate source review band. The source semantic guide itself has per-frame approximation steps, so a color-proxy mismatch is not a surveyed geometry error. Raw was left untouched and the issue was reported instead of being warped into compliance.

Grass is finely rendered but remains rather warm-yellow, dense and high-contrast. It does not yet satisfy the intended quiet, naturally varied lawn confidently. No obvious exact mirrored tile seams were seen, but a joint hall/actor in-engine review is still required. The raw is **not accepted for production**.

## Reproducible checks

Run `python Project/art_source/earth_ground_plate_candidate_v1/review_candidate.py` from the repository root. It requires Pillow, NumPy and SciPy. It only reads raw/source and writes this directory's diagnostic copies and JSON; raw SHA is checked before and after.

- `review.json`: size/density, manual approximate curb reads, material/color-proxy scanlines and limits.
- `geometry-comparison-diagnostic.png`: left is source nearest-enlarged solely for geometry comparison; right is generated native pixels at the same world coordinates.
- `source-centerline-overlay-diagnostic.png`: a diagnostic copy with the source manual curb centerline overlaid. Never use this annotated image as artwork.

Await parent review before any correction, additional generation, 64-owner export, shadow generation or runtime integration.
