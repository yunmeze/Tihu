# Temple technical v2: native structural review

2026-10-15 05:06 UTC. Environmental owner and sole runtime operator independently inspected the native evidence. Parent approved this as a bounded structural work candidate at05:07 UTC. Default world has not been replaced; art_preview optional T integration belongs to the runtime owner. Separate building cast remains pending.

Frozen registration: technical_v2/registration.json SHA256 `7942f2795adfabd133112bec4376f59bca9dc5377b6982ee1191f8c06114d7bd`.
Raw v2 SHA256 `3bf1876fd6b76831216668a645f4120dcbc737cfa2ba258e0fc3d2fee705c3e1` remains unchanged. Technical_v1 is retained only to demonstrate the rejected top-only depth partition.

## Native evidence
All evidence below is in `/workspace/shared/legend-rebuild-temple/` (not production assets).

- `parity-{raw,v1,v2}.png`: no-actor nearest rendering, same full-raw registration versus owner cutouts. Excluding bottom diagnostic labels, each partitioned version differs at64 pixels, maximum2 RGB levels. This is a small GPU sampling/alpha quantization result, not strict pixel-zero equality. No visible silhouette gap or cutout seam was seen. Offline full raw RGBA inverse reconstruction remains byte-exact.
- `native.log`: resource preflight true; all eight requested targets reached through original A* and unchanged flags. Sequence61,39→66,34→66,35→66,36→65,35→73,35→73,36→74,36→74,37. Cumulative movement ticks192/224/256/288/800/832/864/896. Left-to-right segment uses the actual16-cell path around the building; no teleport or collision edit.
- `66-36-detail.jpg`: source/v1/v2. V1 incorrectly slices shins at narrow risers. V2 restores continuous shins. The right boot's outer rim remains partly behind the real side cheek, while source boots are complete. Parent inspected this difference and accepted it as an explicit new-side-cheek design residual, not a reason to lower the cheek layer or cut out actor-shaped pixels.
- `right-stair-detail.jpg`: source/v1/v2 at73,36;74,36;74,37. V2 legs/boots remain continuous; v1 contains erroneous riser cuts.
- `66-34-mode2.png`: whole-scene upper-left threshold; actor standing relation and normal foreground/background composition inspected.
- `remaining-threshold-details.jpg`: source/v2 at65,35;66,35;73,35. No new body slice or broken support face observed.

Stationary comparisons force original South phase17 after arrival for equal pose. Movement itself uses original direction/phase. These are eight actual path endpoints and their normal-depth comparisons, not all hero phases, every building edge, NPC interaction, or full-map acceptance. Source NPCs, plants, floor and hero checker shadow remain visible. Candidate has no independent building cast yet.

## Retained limitations
- A single common support-fit scale/translation for the complete image; no roof-specific warp. Roof proportions, tighter outline, stair/side-cheek proportions and3-pixel raw bottom alpha margin remain design/resolution differences.
- Manual support fit RMS6.123 source pixels is within the scale of uncertain manual feature readings; it is not exact geometric correspondence.
- Five v1 empty owners become three v2 empty owners after proper continuous stair-face classification. All30 original keys remain suppressed and their original sorting anchors unchanged.
- Nearest filtering only. Any later linear-filtered owner rendering must independently guard cutout-edge alpha artifacts.
- New raw surfaces are slightly translucent in places; no alpha was normalized to hide that.
- Building cast and overall scene lighting are separate uncompleted gates.
