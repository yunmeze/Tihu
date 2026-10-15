# Two approved NPCs: direct-raw4× texture density

This is a deterministic technical derivative, not new art generation or a new pose
fit. The accepted 1× assets and all old source stages stay untouched. Entry point:
`res://art_source/npc_fangzhang_density4_v1/npc-density4-set.json`.

## Texture and logical coordinates

| | Old texture | New texture | Unchanged logical draw size |
|---|---|---|---|
| Fangzhang | 128×160, one cell shared by261–264 | 512×640, one cell shared by261–264 | 128×160 |
| Lingyunzi | 512×160, four128×160 cells | 2048×640, four512×640 cells | 128×160 per phase |

The new atlas is sampled **directly from immutable generated raw**, one bicubic
sampling pass per equal original cell. It is not an enlargement of the small
accepted atlas. The old raw-to-logical scale and translation are both multiplied4
in texture coordinates. No phase is recentered/refitted/retimed. The script first
reproduces the old 1× RGBA exactly to prove the same registration was used.

Logical root=(32,104), draw_offset=(-32,-104), world cell positions and sort order
stay unchanged. Texture root becomes(128,416). Draw each512×640 source rectangle
into a128×160 logical destination at `npc_world_origin+(-32,-104)`.
Alternatively use a512×640 Sprite2D region with scale(.25,.25) and the same logical
position. Do not multiply the logical draw offset again or add old source offsets.
Use linear texture filtering. 50Hz/17tick/68tick shared timing remains unchanged.

## Fixed shadow units

| | Logical reference | HD texture reference | Slope |
|---|---|---|---|
| Fangzhang | (44,118) | (176,472) | 12/17 |
| Lingyunzi | (56,125) | (224,500) | 0 |

For HD alpha, give the existing projection helper a texture-space region512×640,
the HD reference above, unchanged slope and cast(148/279,-111/279), and a
`body_to_parent` whose linear basis is(.25,0)/(0,.25), with origin equal to the
body’s logical top-left. Opacity.30 and tint(.035,.045,.055) do not change.
This gives exactly the same logical projection geometry: P4(4p)/4=P1(p).
The validation file tests multiple points, including both fixed sole proxies.

**Blur needs an explicit runtime choice.** The old.9 logical-pixel kernel becomes
3.6 texture pixels. The current helper caps blur at3, so blindly reusing it would
yield.75 logical pixels; passing.9 would yield only.225 logical pixels. Do not
silently call either equivalent. Runtime can add bounded HD support for3.6 texture
pixels, preserving.9 logically, or keep the already-approved native shadow alpha
at its original128×160 region, scale1, and logical reference. If keeping native
shadow alpha, never apply the HD reference to that small texture. One shadow only.

The .25 body transform has determinant.0625, safely above the existing.025 helper
minimum. Each512×640 region is below the2048 frame-size limit. Projection slopes
and determinants are unchanged. Texture dimensions/explicit region guards must
be updated together; no atlas-neighbor sampling or extra per-phase translation.

Higher-density alpha and sampling can shift subpixel contour coverage. The
per-foot alpha8/32/96/128/224 edge readings are diagnostics only. They do not refit
the accepted receiver or redefine anatomical contact. Exact logical projection
invariance is not a claim of pixel-identical blur or new physical foot knowledge.

## Display gate

The next runtime owner should test a genuine2× logical-to-output transform with
the HD texture sampling directly at the final resolution. Upscaling a completed
low-resolution viewport, old128×160 atlas, screenshot or diagnostic board does
not establish an HD rendering pipeline. Texture density4× and window scale2× are
independent; do not change world layout, cells, click geometry or pose to fill the
screen. Keep existing source/body/shadow toggles and whole-group fallback.

Ignored `diagnostics/a13-npc/density4-v1/*-old-vs-density4-at-logical2x.png` compares
old atlas→2× with raw→4×→2× as an offline illustration only, not runtime acceptance.
The final engine gate must inspect both NPCs, complete17tick loops, contact,
front/back ordering and native output dimensions under the chosen display path.

Reproduce: `python Project/art_source/npc_fangzhang_density4_v1/register_density4.py`.
Use `GIT_SAVE_DENSITY4.json` plus itself as the minimal new-stage list. No ordinary
asset path is replaced or selected by this research stage.
