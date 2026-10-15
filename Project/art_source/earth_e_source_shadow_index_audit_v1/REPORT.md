# E original checker-shadow index audit

## Answer
The original BMP pixel category IS unambiguously separable: palette index18, RGB(16,8,8), has no duplicate palette entry of that RGB in these packs. A reversible index18 partition is proven pixel-for-pixel for45–50. The semantic statement “every index18 pixel is shadow and never body” has very strong asset-pattern evidence but is NOT established by a native renderer shadow flag/branch. Accordingly the produced reference is explicitly named index18-excluded, not certified pure body. No runtime assets, sourcefall-back, original data, or historical input boards were modified.

## Encoding evidence
Read-only 原版游戏/Data/Hero/2.lpRes:281 records, native animated container, key171; selected45–50 contain ordinary8-bit indexed BMP images, not a separate shadow plane/record. Offsets are the original native offsets.
Body index18 counts45..50:298,327,351,338,360,309. Each selected frame's index18 pixels all occupy ONE checker parity. Their full128 y starts56 (48 starts57), with last y85. No selected index18 pixel occurs in head/chest area.

Whole-pack cross-check: index18 occurs in280 of281 body records; EVERY such record has a single checker parity, no mixed-parity exception. Palette18 is always(16,8,8), and no other palette entry duplicates thatRGB. Head0 has index18 in29 of281 records, likewise no mixed-parity cases. This suggests a consistent baked stipple-shadow convention, not a broad “all dark colors” rule. It also means index18 is not exclusively confined to the body pack globally; selected layers are checked individually.

## Drawing logic and limits
Project/tools/lp_original.py decode_frame and reference tools/extract-lp.py convert BMP palette pixels toRGBA and make exactRGB(0,0,0) transparent; they explicitly retain nonblack checker colors. Reference tools/native-color-key.py only applies that black key. Reference src/batch.js frame() draws a single texture quad using offset+crop, and its fragment shader samplesRGB/alpha without an index18 semantic branch. Thus the checked reference rendering path displays the stipple as baked sprite pixels, not an independent shadow owner.

These are decoder/reference-adaptation code, NOT the original EXE's fully verified native drawing implementation. This repository exposes original binaries, not native renderer source for this distinction. No original EXE or Windows helper was executed. The native-code helper is a disassembly utility but does not itself prove an index18 shadow branch. Do not rename reference-renderer observations as verified original-executable semantics.

## Pixel proof and technical board
audit.py directly reads indexed original BMPs; mask is exactly(indices==18), never an RGB-distance or dark-threshold classifier. For each layer:
- Every non18 RGBA pixel is unchanged.
- Keep+index18-only recompose exactly to original decoded RGBA.
- Native offsets are preserved on full128 canvas, root16,64.
- Composite body+head matches frozen source45–50 PNG byte-for-byte in RGBA.
- Composite index split also recomposes exactly.

PIXEL_PROOF.json records sourceSHA, byte offsets, all selected index18 coordinates, parity, layer counts and exact comparisons. This proves which pixels changed and reversibility; it does not by itself prove artistic semantic identity of every removed pixel.

Project/diagnostics/earth_e_source_shadow_index_audit_v1/original-index-separated-technical-board.png shows original / index18-excluded / index18-only for all6. Individual full128 evidence and both partitions are in the same diagnostics directory. Viewed: the excluded layer looks like the character silhouette; the removed layer follows the offset checker cast and small foot-adjacent patches. This visual evidence strengthens the interpretation but is not an excuse to claim a native reserved-shadow API.

## Decision
Suitable to present as a reversible, explicitly qualified technical reference for further review. Under a strict requirement for renderer-certified semantic shadow/body separation, the missing native semantic proof remains, so no “guaranteed pure body” input is promoted. No new generation authorized or performed. E walk continues complete sourcefallback.
