# Coastal hand-painted texture set

Original image-generated albedo assets for the Pelican Toon Coast project, created on 2026-10-13 with the built-in image generation tool. No external texture library or third-party source images were used. The art was generated from written prompts and matched to the project's existing authored colors. The original generated pixels are retained; there was no post-generation repainting, resampling, color conversion, or seam repair.

## Assets

- `assets/textures/coastal_stone_painted.png`: warm peach/cream coastal stone with cool lavender-gray and sage mineral pigment.
- `assets/textures/coastal_sand_painted.png`: quiet ivory/ochre sand and earthen-path brushwork.
- `assets/textures/coastal_grass_painted.png`: soft sage/leaf-green ground coverage and warmer brush clusters.

All three files are 1254 × 1254, RGB, opaque PNG. The prompt requested 1024 × 1024; the built-in generator returned 1254 × 1254. The original dimensions were preserved. Each texture was visually inspected and decoded successfully; checksums, dimensions, file sizes, color statistics, and edge metrics are recorded in `texture_checks.json` alongside this document.

## Intended integration

Use as color/albedo textures beneath the scene's dynamic lighting. Enable repeat and mipmaps, with anisotropic filtering when available. Triplanar projection over a 2–3 meter tile is a starting point. Normalize in the shader and blend modestly with authored source colors, especially for stone: the stone brushwork has more mineral variation and fine detail than the other two textures. Leaves, flowers, and grass-blade meshes need their separate material treatment rather than these ground swatches.

These are seamless-intent textures, not numerically periodic textures. Opposite borders visually continue the general material, but are not identical pixel-for-pixel: mean absolute RGB edge discontinuity is 3–10/255. Check repetition in the actual camera and use restrained mixing/triplanar projection; do not claim that a mathematical seam-repair pass was performed. There are no baked cast shadows, large objects, text, alpha, or normal-map encoding.

Color means in `texture_checks.json` are measured directly in 8-bit PNG RGB, not linear-light values. A `source_color` texture sampler decodes sRGB in Godot, so convert reference colors consistently before division/normalization.

## Exact generation prompts

### Stone

Use case: stylized-concept
Asset type: production 3D game seamless hand-painted albedo texture tile, exactly 1024 x 1024 pixels, opaque RGB image.
Primary request: Original high-quality hand-painted coastal stone surface texture for an anime/toon coastal fantasy game. Square uninterrupted flat swatch of rock material, not a scene. Designed to map across sculpted coastal boulders and cliff faces via triplanar projection, with one tile covering about 2–3 meters.
Composition: straight-on orthographic perfectly flat surface filling every pixel; truly seamless tile wrapping all four edges; no border or frame. Organic irregular broad planes of pigment with a balanced non-focal distribution across the square. Sparse very fine broken mineral strokes and shallow vein marks. Rock character should feel weathered, rounded by sea wind, and artist-painted, not brickwork or paving.
Color palette: restrained warm peach limestone around #c6a48e, light creamy sand, with soft cool lavender-gray and muted sage-gray mineral variations. Restrained 10–15 percent value variation overall; all details subordinate to broad color patches.
Style: polished hand-painted game environment albedo, subtly visible tapered brush marks, deliberate broad brush planes and finely painted material detail. Sophisticated anime environment art, quiet and legible, no procedural speckle or photographic grain.
Lighting: purely unlit diffuse pigment color, even exposure from edge to edge. Absolutely no painted directional light, no cast shadows, no glints, no baked ambient occlusion, no normal-map colors.
Avoid: objects, isolated stones or pebbles, grass, cracks that span the tile, masonry, chunky cobblestones, gaps, dark outlines, black cracks, perspective, horizon, vignette, gradients from one side to the other, text, labels, signatures, logos, watermark, transparency.

### Sand

Use case: stylized-concept
Asset type: seamless 3D game albedo material swatch; square 1024 x 1024 pixels, opaque RGB.
Primary request: Elegant original hand-painted pale coastal sand-and-earth surface texture for a high-quality anime/toon game path. This is only a flat uninterrupted pigment material swatch, not a rendered scene or photograph. A whole tile spans about 2–3 meters of walking path. Grounded in softly brushed matte sand, subtle faded ochre soil patches, occasional tiny short painterly grit accents, gently irregular overlapping broad strokes.
Composition: perfectly straight-on orthographic evenly exposed square; seamless wrapping all four edges. Balanced non-focal color coverage, broad broken patches dominate, very sparse fine accents. No perspective or height apparent.
Color palette: mainly warm ivory ochre, pale honey sand near #dec69e, tiny subtle pink-clay and cool beige pigment changes. Tightly restrained 8–12 percent value variation. No dark speckles, no bright highlights. The texture should remain calm from afar and softly brushed up close.
Style: premium hand-painted stylized game environment, delicate layered gouache-like brushwork with very soft edges and occasional intentional short dry-brush strokes. Finely authored painted surface, not computer noise. Material color only, suitable beneath dynamic toon lighting.
Lighting: purely unlit albedo, even exposure, absolutely no cast shadow, ambient-occlusion shading, directional illumination, bump lighting, specular reflection, vignette, side-to-side gradient.
Avoid: objects, pebbles, stones, footprints, shells, plants, grass, dunes, ripples, repeated motifs, strong veins or cracks, clumps, large dark or bright patches, dots, film grain, photographic grit, text, borders, watermark, transparency.

### Grass

Use case: stylized-concept
Asset type: seamless 3D game ground albedo material swatch; square 1024 x 1024 pixels, opaque RGB.
Primary request: Original hand-painted soft sage coastal grassy meadow ground color texture for a high-quality anime/toon adventure game. This is a flat square diffuse pigment swatch, only abstract painted grass ground coverage. A whole tile covers 2–3 meters. Broad softly brushed moss/sage patches and small tapered artist's strokes gently suggest fine short grass without depicting distinct blades. Keep the painted patchwork organic, sparse in detail, and very readable.
Composition: straight-on orthographic flat surface filling all pixels, seamlessly wrapping across every edge; uniform non-focal distribution, no framing. The main scale is large quiet color masses; isolated tiny clusters of 2–4 short warm green strokes give close-up interest. No grass objects with volume.
Color palette: soft sage and leaf green near #83a572, subtle cooler moss-green shadows of pigment only and pale warm yellow-green brushed accents. Restrained 10–15 percent value variation, moderate saturation, no neon, no deep dark green. Color should suit warm ivory sun, cool lavender shade, and teal water.
Style: polished artist-painted anime game terrain albedo, restrained gouache-like brush textures, sophisticated broad painterly strokes. Calm organic surface, not noisy photorealism or a grass photograph.
Lighting: completely flat unlit pigment color, even exposure, no baked directional lighting, no cast shadows, no ambient-occlusion shading, no glossy highlights, no vignette or side-to-side gradient.
Avoid: flowers, leaves, literal grass blades, plants, bushes, objects, bare dirt holes, clumps in perspective, lines of planting, strong repeated shapes, black linework, cracks, dark speckles, procedural noise, grain, text, watermark, borders, transparency.

