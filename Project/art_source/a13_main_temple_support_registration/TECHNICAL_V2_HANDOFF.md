# Technical v2: stair-material depth correction

2026-10-15 04:46 UTC. This supersedes technical_v1 only as the next optional depth diagnostic. It does not overwrite v1, raw v2 or the source contract. No native result is claimed.

Registration: `res://art_source/a13_main_temple_support_registration/technical_v2/registration.json`
SHA256: `7942f2795adfabd133112bec4376f59bca9dc5377b6982ee1191f8c06114d7bd`

Same frozen raw, same single scale/world origin, same original30 keys/flags/layers/y/order and source suppression contract as TECHNICAL_HANDOFF.md. 27 nonempty cutouts; 3 empty keys (3966,3978,3985) remain suppressed. Do not also load v1 cutouts. Nearest/no mipmaps remains the diagnostic filter.

## Why this revision is justified
Original Building3975/3980/3981/3982/3986 are layer0 support strips that visibly include narrow vertical stair risers as well as top tread faces. The ignored `source-support-strip-materials.png` contact sheet shows these exact atlas crops. The earlier top-only mask was overconservative, not proof that every riser is a wall. The source frames remain reproducible through the frozen source-group-contract atlas rectangles and hashes.

V2 traces the visible connected staircase interior, bounded by the actual inside edges of the two stone side cheeks. Narrow inter-step risers and the lowest step front lip belong to that support component. The side cheeks, rails, walls and ambiguous shared borders stay layer1. This polygon was read from the complete material component, not constructed around actor pixels. The registration manifest records its raw coordinates and 3–6 raw-pixel boundary uncertainty. `v2-technical-v2-stair-components.jpg` shows the exact mask.

The new layer0 ownership may extend beyond an old source rectangle while keeping its original sort anchor. Some source apron owners now receive nearby real generated step pixels through same-layer nearest provenance. No new apron is generated, and no hidden face is invented to fill an empty owner.

## Static point results, not native proof
Of the four v1 boot-point late-owner risks, three now correspond to actual stair material in layer0. The right boot at cell66,36/raw[410,953] is on the cheek/stair seam and remains in layer1 owner3988 y38. Keep that uncertainty visible. Do not expand the support mask just to clear the statistic.

Native priority: original/technical_v1/technical_v2 at66,36;73,36;74,37 plus upper thresholds and the previously requested paths. Inspect actual visible ankles and normal depth. Other scenery may occlude actors and is not represented in these local static probes. Same-y source buildings precede the hero; merely being layer1 is not automatically late occlusion.

## Independent static checks
867,910 alpha-positive pixels, 998 additional transparent colored pixels; inverse reconstruction of every raw RGBA byte is identical. Every nonzero RGBA pixel has exactly one owner, zero overlaps/loss. All30 source metadata records match, crop sampling is in range, and raw-crop world compensation is exact. No source/RGB/geometry/runtime modifications.

Rebuild with `build_technical_partition_v2.py`; validate with `verify_technical_partition_v2.py`. Ignored reports: technical-v2-validation.json and technical-v2-boot-owner-probes.json.
