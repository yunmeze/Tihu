# Main temple: conservative source-referenced ground-shadow evidence

Status: offline research only. No runtime connection or native acceptance.
This is a **source-referenced 2D ground-shadow fragment**, not physical lighting
reconstructed for the new roof. Source and generated body RGBA are unchanged.
The hero/tree helpers, shaders and parameters are unchanged.

## What the two boards show

- `source-new-mask-board.jpg`: native-size source on original floors with spatial
  fences; registered new building with reviewed-ROI/new-exclusion overlays; offline ON/OFF.
  Cyan is the inspected ROI before source safety removal, not the final allowed receiver.
- `receiver-detail-board.png`: enlarged source, new building, original checker
  support, softened alpha and offline result. Enlarged panels are nearest-neighbor
  inspection, not additional image detail.

The visible result is a small, continuous right-side grass shadow fragment. The
lower-left edge retains a stepped truncation from the conservative source fences.
It does not provide a convincing complete building/contact shadow on its own.
The higher/back source shadow and all uncertain hidden/apron areas remain absent.
Do not expand the masks to improve the appearance without new receiver evidence.

## Verified source and receiver

The original 30-owner temple composite is rebuilt directly from original atlas
rectangles, in recorded source draw order. Reconstructed RGBA SHA256:
`b5a499e6c2285f5ed2cbee9c73fa83be03af26a9cb8a0d1d447155cd005c990a`.
The evidence canvas is 796x665 at world origin (2948,642); rectangles are half-open.

Spatially inspected source-local rectangles, with checker counts:

- (680,310)..(796,350): 1,284
- (684,350)..(796,360): 495
- (700,360)..(796,370): 249
- (728,370)..(796,390): 24

All 2,052 nontransparent source pixels inside these rectangles equal
RGBA(8,0,0,255), with odd (x+y) checker parity. This color is checked **only within
these spatial fences**. It is not a safe global architectural-color selector.

All 8,080 fenced pixels receive opaque original FloorBig:406 grass. The exact
floor contributions are 160/800/768/5,808/544 pixels from cells (74,28), (74,30),
(76,28), (76,30), (76,32). The script enumerates all original scenery placements,
all applicable animation phases and all original NPC phases using world_view's
coordinate rules. Only temple owners 3983, 3984 and 3978 contribute visible pixels
inside the fences; every contribution is checker. No other object or structural
material enters them. This proves an external grass-floor receiver in the 2D
rendering contract, not independently measured physical elevation/normals.

## Two conservative exclusion masks

1. Source safety: every original nonzero-alpha pixel outside the verified checker
   set is treated as potential structure **or unknown**, including unclassified
   shadow/apron pixels. Dilate that set by a Euclidean 2-native-pixel disk. No
   global RGB segmentation is involved. This removes cross-band near-wall cases
   that cannot be detected from each rectangle's horizontal clearance alone.
2. New-building safety: register the complete immutable raw with the accepted
   scale 0.533687668884736 and world origin (2979.8431118835333,
   665.2144416536717). Nearest pixel-center sampling of **all alpha>0**, filling
   enclosed holes, then the same 2-pixel dilation protects walls, roof, stairs,
   plinth, doors/interiors and edges. This is a receiver veto, not a surveyed
   contact-footprint mask and not a body-alpha edit.

The source safety mask rejects 117 checker points; the new-building safety mask
covers 87 checker points (these sets can overlap). New material is mostly alpha
253, so simple draw-before-object ordering would not strictly prevent leakage.
The mask is needed even for those nearly opaque interiors.

## One-pass softening with bounded support

- Start with the original binary half-density checker in the fenced ROIs.
- A transparent checker gap is eligible only when original checker pixels bracket
  it at distance 1 on opposite horizontal or vertical sides. This fills known
  checker sampling gaps; it does not extend the observed exterior envelope.
- Apply one normalized Gaussian, sigma 1.25 native pixels, truncate 3 sigma;
  compensate the checker density by 2 and apply an opacity cap of 0.30.
- After softening, intersect with the observed/bracketed envelope and verified
  receiver, and subtract both source safety and new-building safety exclusions.
- Serialize one L8 alpha. The current rounded maximum is 76/255; the floating
  operation is capped at 0.30. No layered shadows/contact blobs are stacked.

Current output: 3,765 nonzero alpha pixels, 1,097.93 opaque-pixel-equivalent alpha
sum. Protected structure, unknown receiver and outside-envelope leakage counts
are all zero in the native CPU evidence grid. That is not a GPU/subpixel/filter
proof. Camera and sampling footprints still need a separate runtime review if
this fragment is ever considered useful enough to integrate.

## Reproduce and audit

Run from Project:

    python3 art_source/a13_main_temple_shadow_reference_v1/build_evidence.py

The script writes only this evidence directory. `reference-contract.json` records
input and source atlas hashes, every source/floor owner contribution, whole-scene
receiver audit, pixel conventions, registration, classification, mask parameters,
counts, limitations and the five mask hashes. It does not import Godot or alter
runtime files. No image generation, source pixel painting, geometric deformation,
whole-alpha projection, or fabricated 3D heights occur.

If subsequently approved for a diagnostic: draw this single matte after floors
and before **all** objects, including layer0 stairs, retaining original owner
sorting. Keep all 30 old temple owners suppressed together so their checker is
not doubled. A full source fallback must restore the complete original group.
Close normal runtime resource paths separately; these are research dependencies.
