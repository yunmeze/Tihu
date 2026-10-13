# Original restrained pelican feather-flow albedo candidate

Generated on 2026-10-13 at approximately 08:32 UTC using the built-in `image_gen` tool in new-image mode. No CLI/API fallback, outside texture library, or third-party asset was used. The native scene checkpoint and internal paintover were visually consulted to understand the cute character and desired painted material language. Neither was supplied as an image-generation input, and the paintover is only a concept, never runtime evidence.

## Selected candidate and exact generation input

- `assets/textures/pelican_feather_flow_0832.png`: original opaque RGB PNG, 1774 × 887 pixels, exact 2:1 aspect ratio.
- `assets/textures/pelican_feather_flow_prompt_0825.txt`: complete exact generation prompt. The prompt was prepared at 08:25 and updated to the verified authored UV contract before generation at 08:31.
- `assets/textures/pelican_feather_flow_0832.json`: measured color, clean-front, pole and seam statistics; checksum; mapping contract; review notes.
- Original output: `/workspace/scratch/22c897619190/generated_images/exec-acbd8e43-85ae-49bc-aaa8-a309660bcfec.png`.
- SHA-256: `a11c032581a4c51c93fd089c8b663827d474962251e55061e0475112f54f4750`.
- RGB pixel-array SHA-256: `c6fae9e33672d9c284ae9aa9f8a40f891071d9519de82e604531dd94c7fcbf42`.

The prompt requested 2048 × 1024 pixels, while the tool returned 1774 × 887. The actual original pixels and dimensions are preserved by a byte-identical copy, with no resampling, repainting, color conversion, alpha modification or seam edits. This is the only generated feather-flow variant in this pass.

## Visual intent and observed result

Warm ivory ground carries broad pale cream and desaturated lavender feather-flow masses on both sides and around the lower collar. The front face area is almost uniform, without eyes, bill, anatomy, drawn outlines, ink, scene elements or text. Feather sweeps read as broad curved pigment shapes with tapered tips, not photographic feather strands. The sides and lower collar contain more marks than the blank face; their contrast and scale must be judged on the actual character, not from this flat map alone.

The returned ground is slightly warmer/yellower than the prompt's nominal ivory. Whole-image mean sRGB is `(239.4421, 224.3595, 201.6265)` in 0–255 units. Corresponding normalized sRGB mean is `(0.93898868, 0.87984113, 0.79069199)`. Mean after pixelwise sRGB-to-linear conversion is `(0.86742259, 0.74910906, 0.58923630)`; this is not the conversion of the sRGB mean.

The clean-front rectangle, image UV `(0.34, 0.20)` through `(0.66, 0.70)`, has RGB standard deviations `(1.0529, 1.3092, 1.4260)` in 0–255 units. The upper and lower 3% pole strips are also quiet, each with per-channel standard deviation approximately one value or less. They still contain small pigment variation and must be reviewed for pole pinching.

## Authored UV integration contract

This candidate uses the confirmed native Blender Sphere Projection contract on both PelicanHead and PelicanBody. The builder verified cardinal UV samples from saved source and recorded them in `/workspace/shared/feather_uv_contract_0830.json`. No analytical object-local projection is required for this texture.

- Front Blender +X: U = 0.5, equator V = 0.5.
- Near side Blender -Y: U = 0.25, equator V = 0.5.
- Far side Blender +Y: U = 0.75, equator V = 0.5.
- Rear seam: U = 0/1.
- Crown: Blender V = 1, glTF/PNG top-down V = 0.
- Bottom: Blender V = 0, glTF/PNG top-down V = 1.
- Use the same semantic mapping for both meshes; broad patterns may stretch differently with their proportions.

Read the image as sRGB (`source_color`), use linear mipmapped sampling and enable texture repeat. The head's seam-crossing UVs can exceed U = 1, making horizontal repeat necessary. Review extreme V sampling at the poles; the image has quiet top and bottom strips rather than intentionally matching top/bottom edges.

Start with restrained material influence to protect the existing ivory identity and let native toon light remain authoritative. A color-neutral detail workflow can normalize the sampled linear pigment by the measured linear mean before gently mixing it into the established ivory albedo. This is integration advice, not a claim that any particular shader or strength has been accepted.

## Seam and acceptance limits

The left/right edges are close but not numerically identical. Across corresponding extreme-edge RGB pixels, mean absolute difference is 1.1368/255, 95th percentile is 3/255 and maximum is 17/255. Some feather tips approach the edges, so check the rear join in an actual orbit/rear view. No seamlessness guarantee is made from these statistics alone.

This deliverable is a material candidate requiring native render review. It does not prove a final look, runtime fidelity, frame rate, performance improvement or visual acceptance. No renderer scripts, Blender files, GLB geometry or GUI state were modified by this texture pass.
