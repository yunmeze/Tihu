# Earth ground plate: one grass-material edit

One built-in imagegen edit, 2026-10-15. Target was `earth_ground_plate_candidate_v1/raw.png`; the instruction allowed only grass to change, with the whole road/curb protected. No third generation was made.

`raw.png` is the unchanged returned **1536×1024 RGB** image, exactly **2 texels/logical unit** at world `[2496,960,3264,1472]`. SHA256: `7dd080bb54897b878ac7743cad1dfb865217bdb76266fc441adb56d750edcb7b`.

## Outcome: improved grass, failed non-target preservation

Grass is visibly deeper green with fewer golden, wiry highlights and lower fine-scale contrast. It remains fairly densely leafy, so this is a material candidate for joint review, not final visual acceptance.

The tool also re-rendered the pavement. The protected road/curb plus safety fringe has 244865 changed pixels out of 245083 (99.91%). A conservative road-only core, eroded 16 actual pixels inward, still has 211496 changed pixels out of 211705 (99.90%), with mean absolute RGB-channel difference **8.04/255**, maximum **195**. The issue is not merely changed blades crossing the road edge. Major path shape and seams look close, but the concrete texture was not kept pixel-identical.

Consequently this raw is **not an accepted grass-only edit**. The original v1 raw remains unchanged. No programmatic recoloring, blur, warp or pavement restoration/compositing was performed.

## Independent whole-v2 candidate review and export

The parent separately reviewed v2 as a **whole-plate** candidate, rather than demanding pixel-identical v1 pavement. Six independently inspected road-center points remain within the original finite source-read budget: maximum approximately 2.5 logical pixels, source uncertainty ±3. The capped-road shape, bottom opening and approximately186-logical-pixel grass interval remain. This does not establish exact outer-curb width or native scene acceptance. `layout-review.json` records those points; `review_layout.py` reproduces the recorded audit without fitting the image.

Following that review, `export_candidate.py` directly cuts the complete, immutable v2 raw into all64 original floor owners at **192×128 pixels / scale0.5**, preserving exact source keys, cells, four-field source records, stable order and nearest2× source alpha. Nothing from v1 is mixed back. Output: `assets/earth/environment/ground_plate_v2/registration.json`,64 tile PNGs and a byte-identical shared `plate.png` for optional later shared-canvas sampling.

`export-review.json` confirms the64 RGBA slices reconstruct v2 byte-exactly, every pixel has exactly one owner, original alpha is255 throughout this scope and all source map/manifest identities match. Runtime integration and Godot execution are left to the designated scene owner. Initial slice sampling should be nearest; the split textures have no gutters. The optional shared plate is not required for initial runtime integration. Grass remains a little busy; final judgment belongs to real scene-scale review.

## Provenance and review

- `prompt.txt`: exact actual edit prompt.
- `generation.json`: target/reference hashes, actual output dimensions and returned file path.
- `inputs/reference-crops.json`: exact unscaled medium/deep-green grass crops from the accepted concept. They provide material tone/density only, not layout or cast-shadow geometry.
- `inputs/protected-road-mask.png`: white road/curb protection guide provided to the generator; it was a reference image, not an enforced API mask.
- `review_edit.py` and `review.json`: reproducible dimension, protected-pixel, road-core and descriptive grass/footprint checks. Run `python Project/art_source/earth_ground_plate_grass_edit_v2/review_edit.py`. Requires Pillow, NumPy and SciPy. Both raw hashes are checked before and after.
- `archive-manifest.json`: explicit archive allowlist covering the v1/v2 raw research, prompts, reference crops and review code/results. Temporary annotated/side-by-side diagnostic PNGs are excluded.

The footprint color-proxy metrics and grass-luma proxies are descriptive evidence, not exact geometric registration or perceptual acceptance. Candidate export is not final visual approval. No automatic third generation is authorized.
