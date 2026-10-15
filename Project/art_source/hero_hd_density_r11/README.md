# HD texture density pilot for existing30 accepted phases

The approved raw designs contain more detail than the prior128-cell registered atlases. Baking them to128 and later enlarging those textures loses that detail. This pilot replays the identical raw-cell partition, uniform scale and per-phase translation directly at4 texels per logical pixel. It does not change body proportions, phase shapes, root position, animation timing, or screen/world footprint.

## Reproduce and validate

Run `python Project/tools/hero/build_hd_registered_atlases.py` from repository root. Each of six E/SE/S idle/walk groups checks raw SHA, rebuilds the complete raw rectangles byte-exact, and replays the128 output byte-exact against its frozen atlas before producing512-cell output. Source raw and registration paths/SHA are listed in the diagnostic manifest. No old128 image is used to construct the HD output.

Output: `assets/scifi/diagnostics/hero_hd4/manifest.json` and six `*_body.png` atlases. These remain diagnostics pending actual HD engine review. Original source and selected ordinary preview atlases remain unchanged.

## Renderer contract

Each texture frame is512×512, but covers128×128 logical pixels. Logical root(16,64) maps to texture root(64,256). Use source region512 and sprite scale0.25 with uncentered texture offset(-64,-256), or draw that region into the original logical rectangle(-16,-64,128,128). Never keep the old128 region against the512 atlas, and never draw a512 region at scale1. The current 12/7 tick timing is unchanged.

The HD display must actually render the world to the HD target. Enlarging a1024 low-resolution offscreen viewport after rendering will still lose detail even with high-density textures. Keep the same camera/world footprint for A/B, change render-target density, and sample the new body linearly. UI should be drawn at its intended output resolution.

## Shadow contract

The single-shadow receiver remains logical y86 with cast(148/279,-111/279). Prefer computing geometry in logical128 coordinates and only sampling512-pixel alpha UV. If the projection helper operates entirely in texture coordinates, multiply receiver/root/heights/blur by4, then scale the rendered shadow by0.25. Thus receiver344 and blur3.6 correspond to logical86 and0.9. Do not multiply cast direction, opacity, actor world coordinates, or logical animation offsets. Mixing512 texture height with old logical receiver86 gives an incorrect, oversized projection.

## Evidence and limits

`diagnostics/hero/hd4/*-density-comparison.jpg` compares the old128 texture enlarged4× against the direct raw-derived512 frame at the same displayed dimensions. Actual views of SEidle, Ewalk and Sidle show retained face/armor detail. This is an offline texture-density test, not engine or shadow acceptance. Runtime must review actual HD screen, movement, direction changes and normal depth before adoption. All earlier pose/design residuals remain; higher density does not fix them or establish new directions.
