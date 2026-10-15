# A13 NPC original source preparation

Source-only, no new art, runtime change, EXE execution, or edits to `原版游戏/` / `参考项目/`.

Reproduce from the repository root:

```sh
python Project/tools/npc/prepare_a13_npc_source.py
```

Requires Python 3 + Pillow. Diagnostic labels use the installed Noto Sans CJK and DejaVu fonts; fonts do not affect the production RGBA. The script reuses `Project/tools/lp_original.py`, parses the original A13 map, checks all 40 required NPC source frames against both the project atlas and the read-only reference atlas, and verifies input hashes did not change. No gameplay script is executed.

## Start with these files

- `source-contract.json`: complete 11-record mapping; original byte offsets, image offsets, dimensions and RGBA hashes; current/reference timing; three-slot family checks; source-to-canvas coordinates.
- `MANUAL_VISUAL_REVIEW.json`: observations made from every complete original four-phase enlarged board, with separate visible-feature versus uncertain-anatomy statements.
- `VISUAL_REVIEW.md`: compact reading guide and production limits.
- `original_rgba/npc-XXXX.png`: all 40 exact decoded original canvases. The native black-key normalization is the existing decoder's policy; baked nonblack checker shadow remains.
- `fangzhang/source-four-pose-canvas-4x.png`: source 261, 262, 263, 264 in order, one row.
- `lingyunzi/source-four-pose-canvas-4x.png`: source 113, 114, 115, 116 in order, one row.
- Each key NPC directory also has three `source-local-*-8x.png` crops. These are original identity/material evidence, not new-style concepts or a replacement pose.
- `PRODUCTION_FILES_SHA256.json`: explicit minimal owned production file list and per-file SHA256. It excludes itself and ignored diagnostics. The parent owns Git operations; no broad add is needed.

## Pose canvas contract

Both key four-phase inputs are 2048 × 640 RGBA, produced by exact nearest-neighbor 4× enlargement of a 512 × 160 strip. Each native cell is 128 × 160 and each enlarged cell is 512 × 640. The original cell draw origin is `(32,104)` in each native cell, or `(128,416)` after 4×. This is a coordinate origin, **not** a verified sole or pelvis position.

For a source pixel `(u,v)` in phase `j`, place it at:

```text
native_strip = (j*128 + 32 + offset_x + u, 104 + offset_y + v)
enlarged_strip = native_strip * 4
world = (npc.x*48 + offset_x + u, npc.y*32 + offset_y + v)
```

The source is not auto-centered, crop-top aligned, mirrored, scaled per phase, or cleaned of checker shadow. Alpha bounding boxes include props and shadow and are not physical contact bounds. The atlas uses a separate crop offset; do not add atlas crop again when using these full original canvases.

## Two key production decisions

1. **方丈:** 261–264 are exactly identical RGBA with identical size and offset. A single remastered static pose can serve all four source indices. Keep the original index/timing interface; do not invent breathing, bouncing, alternate arm positions or cloth motion. The four-copy pose canvas documents that static source truth.
2. **凌云子:** 113–116 are four distinct source phases. Generate and review them together. Their offsets are `(9,-51), (9,-49), (9,-49), (9,-50)`; the first original canvas is 60 × 72, the others 56 × 71. Preserve registered phase differences instead of top-aligning the cropped heads or leveling the feet by a fabricated ground line.

Future clean science-fiction cultivation styling needs its own approved identity/material source. Use local excerpts from that approved identity as style evidence beside the original four-phase pose canvas. Do not feed a different NPC's complete body, a mirrored direction, or the hero's full-body concept as a new pose authority. Preserve original name, story function, visible posture, props and occlusion. This source package neither creates nor approves a new identity.

## Diagnostics, not production inputs

`Project/diagnostics/a13-npc/` contains one directory per appearance/direction group, full registered 4× boards, common-crop 6× boards, lower-detail 8× boards, complete three-slot/four-phase family boards, overview boards, key source coordinate grids, and `extraction-audit.json`. Cyan crosses appear only when the cell origin lies inside the displayed crop; no off-crop cross is drawn into the neighboring phase.

The original shadow has not been segmented. Do not use diagnostics as generated textures. A later body/shadow separation and contact review remains necessary before runtime promotion. No new preview scene or GUI was added.
