# Ocean foam/current mask provenance

- Asset: `ocean_foam_current_0928.png`
- Generated: 2026-10-13 09:29 UTC, with the built-in OpenAI `image_gen.imagegen` tool.
- Original image, no references or external source image. No external publication or upload.
- Resolution: 1254 × 1254, RGB PNG.
- File SHA-256: `40d97370057009c62670a91c74eb976c67b888254aac07c925f836864b18a320`
- Original output: `/workspace/scratch/22c897619190/generated_images/exec-a721d955-65fb-4e0b-b310-5bb4c80fe529.png`
- Processing: copied byte-for-byte; no pixel modifications, procedural painting, resizing, or filtering.

## Inspection and use

Actual saved pixels were inspected. The image has pale porous foam lace, irregular branching ribbons and elongated broad dark pockets. It contains no scene, horizon, text or watermark. It is suitable as a scalar mask when sampling `.r`.

The PNG is near-monochrome RGB, not channel-identical grayscale. Red-channel normalized range: 0.0–1.0; mean 0.253922. Luminance mean: 0.251877. Luminance below 0.2: 74.28%; above 0.7: 16.54%. This is somewhat sparser than the approximate 50–70% dark target.

Seamless intent was requested, but exact edge equality is not claimed. Opposing-edge luminance mean absolute delta: left/right 0.077463; top/bottom 0.035213. This measures boundary pixel agreement only, not engine appearance. Repeating with bilinear filtering/mipmaps and nonuniform animated sampling should be evaluated in the shader. No shader, code or project files were changed by this asset task.

Use red-channel non-color scalar data, repeat enabled, mipmaps for distance filtering. Dark ground is approximately 0.08–0.11. Thresholding should be tuned in the shader, as the map contains intermediate froth values rather than only black and white.

## Exact generation prompt

Use case: stylized-concept
Asset type: original grayscale scalar foam mask texture for a stylized Godot ocean shader, square 1024 by 1024 preferred.
Primary request: paint a seamless-intent abstract ocean foam/current texture, viewed flat from directly above. A mostly black to very dark charcoal ground has sparse broken off-white froth lace with a few broader branching foam ribbons. Elongated current flow reads mainly from left to right, gently undulating and organically branching.
Composition: cover the square with an even all-over distribution and no center focal point. About 60 percent of the tile is empty dark water mask. Form broad irregular open cells about 5 to 20 percent of the image width, elongated horizontally; the cell rims are thin clustered frothy broken edges, often incomplete. A few sweeping irregular branching medium-width ribbons connect patches of much finer foam lace, tiny porous holes and scattered small flecks. Leave many broad dark calm pockets.
Style: graphic painterly game texture, delicate and natural but clearly stylized; crisp useful shape definition, not photographic. The grayscale shape contrast is the information. Flat unlit albedo-like technical map.
Color: strictly neutral grayscale, channels equal, black dark background and very pale gray to white foam (the visual softness of cream without any color tint). Strong full-range contrast, no colored water.
Constraints: tileable seamless intent on all four edges with consistent structure crossing opposing edges; no frame or border. Texture only, no scene, no horizon, no coastline, no clouds, no objects, no shadows, no perspective, no illumination gradients, no text or symbols, no watermark.
Avoid: dense uniform noise, evenly spaced lines, thick parallel white stripes, regular cellular grid, marbling that fills every dark pocket, diagonal composition, photorealism, a single central swirl.

## Reproducibility

`transparent_background` was `false`. The model and seed were not exposed by the built-in tool. The exact prompt and tool name record provenance but do not guarantee deterministic regeneration. Full pixel statistics and metadata are in `ocean_foam_current_0928.json` and `ocean_foam_current_checks_0928.json`.
