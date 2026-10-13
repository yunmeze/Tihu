# Coastal cumulus sky panorama

## Provenance and technical facts

- Asset: `assets/textures/coastal_cumulus_panorama.png`
- Created: 2026-10-13, using the built-in `image_gen` tool (not the CLI/API fallback).
- Original art generated from the written prompt below. No external stock assets or source photographs were used.
- Original generation file: `generated_images/exec-b1180ff5-760a-4fa0-a9a4-51ff2dcdfe59.png` in the parent workspace. The project asset is a byte-for-byte copy; no resizing, repainting, color transformation, or seam repair was performed.
- Requested size: 2048 × 1024; actual native output: 1774 × 887, exact 2:1 ratio, RGB PNG, 1,548,697 bytes.
- SHA-256: `c25d7c961c52430478265c0583eff583f1264254f603503417b4f2a57767b379`
- Verified by visual inspection and successful Pillow RGB decoding. Quantitative checks are in `sky_panorama_checks.json`.

## Intended use and limitations

This is a painterly full equirectangular sky backdrop. Sample horizontally by azimuth with a `source_color` sampler so Godot decodes the image's sRGB values. Use mipmaps and linear filtering. The upper half contains cream-lit, blue-shaded cumulus; the lower half has featureless atmospheric color and is intended to be hidden or replaced by the shader's authored horizon and lower-sky gradient.

The generator placed the main cloud silhouettes over approximately v = 0.25–0.52, and the featureless lower-sky transition near v = 0.54. This differs slightly from the requested exact v = 0.50 horizon. A shader remap should use the useful low cloud band rather than directly displaying the nominal horizon pixel. Preserve the scene's analytic horizon fade to avoid a visible join with the water.

The largest clusters are around u = 0.23 and u = 0.78; the broad central blue gap is useful for calm character and lighthouse framing. The upper sky is somewhat richer blue than the requested color: center-top pixel RGB is (84, 157, 209). The shader may gently grade or blend the backdrop to match its analytic sky.

Horizontal tiling was requested, but the image is seamless-intent, not numerically periodic. Mean absolute RGB edge discontinuity is 2.39/255 over the full height and 3.14/255 over the upper half. Check the wrap direction in the actual camera or keep it outside the principal view. No numerical seam repair is claimed.

## Exact generation prompt

Use case: stylized-concept
Asset type: production game sky texture, original painterly stylized cumulus 360-degree equirectangular panorama, intended 2048 x 1024 pixels (2:1 aspect ratio), opaque RGB.
Primary request: A beautiful, understated hand-painted blue coastal sky for a premium anime-toon fantasy adventure game. This image is ONLY the sky backdrop texture: a full spherical equirectangular panorama with horizon exactly at the vertical midpoint. Left and right borders match as a horizontally wrapping panorama. Clear broad cloud spacing and quiet values will complement an ivory pelican, teal sea, warm limestone, and sage grass.
Composition and projection: Equirectangular sky map, horizontal axis azimuth 0–360 degrees. Zenith at the top edge, horizon at exactly 50% image height, nadir at bottom. The entire lower half is a completely plain continuation of pale horizon atmosphere, smooth near-uniform pale cyan, no clouds or objects below horizon. Upper half contains only 3–4 separated graceful soft cumulus groups. The most useful cloud silhouettes and detail occur in the narrow band from 32% to 48% of the full image height, just above the midpoint horizon. Gentle high blue-sky negative space fills the upper quarter. Keep broad blue gaps between all groups; do not form a continuous cloud wall. Rounded organic asymmetrical sculptural cloud lobes have readable large shape design; small distant cloud wisps are very sparse. Keep the horizontal extreme edges predominantly matching clear sky to support wrapping.
Style and surface: polished painterly anime game environment background, delicately hand-brushed matte color planes, soft but intentional silhouette edges, rounded cumuliform volume, subtly stylized broad light and shade planes, restrained internal detail. Artist-authored gouache-like visual richness without paper grain or noisy microtexture. A serene clear maritime day with warm sun high to the upper left, but no visible sun disc.
Color and lighting: airy gentle azure and blue-cyan upper sky around #6faace; horizon around #c7e3e6; creamy warm ivory sunlit cloud tops, pale restrained powder-blue/lavender-gray undersides; soft reflected cyan. Mild warm atmospheric glow near horizon without a localized hotspot. Moderate saturation, refined luminous depth, no near-white overexposure and no harsh contrast. Cloud forms stay subtly separated from the horizon haze.
Constraints: Sky only; no landscape, sea, ocean, water, mountains, islands, vegetation, buildings, characters, birds, stars, moon, sun disc, lens flare, text, labels, frame, logo, signature, watermark or transparency. No black contours, photorealistic HDR, dramatic storm clouds, sunset, heavy orange tint, rays, heavy grain, excessive wispy microdetail, opaque fog wall or broad washed-out white band. This is a seamless-horizontal production backdrop panorama, not a framed landscape illustration.
