# 凌云子 v1: complete four-phase static review

Status: first complete-group raw retained; **hold for phase/style review, not runtime-approved**. Exactly one built-in image-generation call produced all four phases. No individual phase was regenerated, replaced, stretched, or independently fitted.

## Evidence and identity

- Immutable `raw-v1.png`: RGBA2172 × 724, SHA256 `e8ed826d7fc5582d0a0910b8c885dee42581650a68723ac8ed8e4697f453f30f`.
- Four equal543 × 724 cells, intended left-to-right source113,114,115,116. The entire sheet remains the one raw artifact.
- Actual prompt/payload is `tool-request.json`. Inputs were the complete original four-phase pose canvas plus three local original tall-headwear/sleeve/hands crops. No hero full-body image or another NPC's body was used.
- Tall head-attached crown silhouette, gray wide sleeves, purple/indigo front garment, overlapping front hands and two tan/gold boots remain recognizable across all four cells. No beard, sword, long staff, large light core, ground or cast shadow was added.
- The generated costume has more gold embroidery, decorative fasteners and multiple hanging tassel details than the unresolved source. This leans more ornate traditional fantasy than the requested restrained technical-cloth treatment. Those details are a design expansion and should be explicitly reviewed, not silently accepted as original evidence.

## Common scale and coordinates

The shared reviewer script is `../npc_fangzhang_rebuild_v1/review_static_candidates.py`. It derives one uniform scale and translation from four manually read visible features in phase0 only: crown top, overlapping hands, and the two visible boot-toe areas. That exact transform is then applied unchanged to all four543px cells.

- Generated-to-original uniform scale: `0.11178785283458711`
- Translation into raw source113 coordinates: `(-15.490136860633637,-4.017450799088628)`
- Shared reference offset is source113 `(9,-51)`, plus native diagnostic cell origin `(32,104)`.
- Original per-phase offsets are **not** added again to the new cells, which would double-count the motion already in the sheet.
- First-phase landmark residual maximum is about1.04 source pixels, with manual reading uncertainty ±2 source pixels / ±12 generated pixels. This is not a solved foot-ground anchor or a full-pose equivalence proof.

## Phase discrepancy that prevents an animation pass

Source113–116 crown/top relative vertical offsets are `(0,2,2,1)` native pixels. Using alpha≥128 top contours, the raw candidate under one common scale gives approximately `(0,2.35,3.24,0.11)`.

- Phase114 is close to the source's downward offset.
- Phase115 is about1.24 native pixels lower than the source's equal-height114/115 relationship.
- Phase116 returns almost to113's height, whereas the source returns only partway, about1 native pixel lower than113.

The source visible bottom progression is `(0,1,1,0)`; all four candidate strong-alpha bottoms are at the same raw row, giving `(0,0,0,0)`. The four bodies therefore keep a nearly fixed bottom while varying upper-body/hat height. This is not the full original per-phase geometry. No per-frame translation or rescale was applied to disguise it. The raw grouping is retained for review, not declared animation-complete.

These are crown/top and visible-extent measurements, not exact anatomical support points. Source checker shadow is retained in the source boards and excluded from any claimed foot-contact solution. The source's precise hands/boot contact points remain uncertain.

## Transparency

True alpha0 background exists, with no obvious baked checker or visible cast-shadow shape in the viewed body sheet. Alpha≥128 phase-local bounds are `[147,37,398,676]`, `[146,58,399,676]`, `[145,66,399,676]`, `[142,38,394,676]`; hats, boots and hands have clear strong-alpha margins inside their cells.

There are24,935 alpha1–7 pixels across the raw sheet, including faint outliers. Whole-sheet alpha≥1 bounds reach `[0,29,2163,724]`, but alpha≥8 bounds tighten to `[146,35,2024,678]`. Most body alpha is252–253, not255. This does not prove a solid background; it does mean the raw matte is not a clean binary silhouette. No thresholding or alpha correction was performed.

## Review files and remaining gate

The complete source/generated group can be viewed at one native scale in `Project/diagnostics/a13-npc/remaster-v1/lingyunzi-native-source-generated-1x.png` and `...-3x.png`. All four phases were viewed together, along with the raw gray-background and coordinate boards. Diagnostic files are not production assets.

Keep this candidate as the one permitted first attempt. Resolve the ornate-detail/style choice and four-phase discrepancy before requesting any new generation or promoting art. Future runtime would preserve the original17tick cadence and original name/story placement, but no runtime, shadow, interaction or GUI change is part of this stage.
