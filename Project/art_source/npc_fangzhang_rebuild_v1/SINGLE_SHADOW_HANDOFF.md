# A13 key NPC single-shadow candidate

Status: the parent accepted the complete pure-pose comparison. These are **offline
single-shadow candidates**, awaiting native contact/occlusion review. The immutable
bodies, registration and prior pose interfaces are unchanged. Historical static
review cautions remain provenance, not a reversal of the parent’s pose decision.

## Closed entry point

`res://art_source/npc_fangzhang_rebuild_v1/npc-single-shadow-diagnostic-set.json`
lists the two `single-shadow-candidate.json` files with exact hashes. Read each
existing `v1-pose-interface.json` for frame rectangles. The current atlas hashes are
unchanged; this stage introduces no new character image or runtime resource.

| Candidate | Fixed frame-local reference | Fixed slope | Source-correlated visible edges |
|---|---:|---:|---|
| 方丈 / Fangzhang | (44,118) | 12/17 = 0.705882353 | candidate (44,118)/(61,130); source (43.5,119)/(59.5,129) |
| 凌云子 / Lingyunzi | (56,125) | 0 | source both boots y125 in all four phases; candidate alpha8..128 edges also y125 |

All coordinates refer to the unchanged 128×160 frame; root=(32,104), body draw
offset=(-32,-104). The reference is respectively (12,14)/(24,21) relative to the
original NPC cell origin. It is not the root or a newly chosen anatomical pivot.

Call the existing `HeroAlphaGroundShadow.configure_ground_frame()` with the exact
same body transform and atlas region as the candidate body. Use each NPC’s fixed
reference/slope, common cast `(148/279,-111/279)`, opacity `.30`, blur `.9`, tint
`(.035,.045,.055)`. Fangzhang’s line is algebraically identical to the old
two-sole API with fixed anchors `(44,118)` and `(61,130)`; fixed mode simply makes
the shared four-phase parameter contract explicit. Do not copy hero receiver y86.

Only the explicit region changes with the shared 50Hz clock: phase=floor(tick/17)%4.
Fangzhang’s four IDs261–264 keep sharing one rectangle. Lingyunzi113–116 keep their
four original registered rectangles. Do not add original offset/crop again, refit
the receiver, recenter feet, change scale, or adjust body pixels by phase.

## Why these two different lines

Fangzhang’s original and candidate soles occupy two visibly staggered screen
depths. The source boot ROIs contain solid footwear adjoining the checker shadow;
last solid rows are54 and64, whose lower edges become119 and129 after original
offset. Candidate rows117 and129 give edges118 and130. The selected fixed sloped
line keeps both reviewed candidate edge proxies unmoved. A horizontal y124 line
would displace each endpoint’s shadow sample by approximately4.815px. That
alternative is recorded, not selected. The source-edge discrepancy is retained,
approximately1.09px maximum projected sample displacement under the candidate
line, within the source-reading uncertainty. This is a static 2D rendering proxy,
not proof that both legs bear weight or a reconstructed physical ground plane.

Lingyunzi’s source raw left/right edges are y72/70/70/71 in113/114/115/116.
After the respective source offsets (-51/-49/-49/-50) and common root104, both
boots are y125 in every phase. The prior whole-image bottom125/126 observation
included checker pixels and must not be treated as a moving sole. Candidate
alpha8,32,96,128 edges all reach125; the broad alpha224 contour ends124, so the
fine toe edge carries about1px of contact ambiguity. Keep y125 fixed; y124 is only
a recorded threshold-sensitivity comparison, not a phase-dependent fallback.

Proxy convention: bottom edge is last-row-index+1; x uses pixel centers. Source
proxies have about±2px manual uncertainty; candidate proxies about±1px. Color
`(16,8,8,255)` is excluded **only in reviewed source boot measurement ROIs**, never
globally, never in a texture, never by the shader. The checker remains unchanged
in all original comparisons. Candidate alpha thresholds are measurement-only.

## Common cast evidence and compositing boundary

Reviewed source regions to the right of the bodies contain checker pixels only:
Fangzhang x≥44 has204 pixels per phase; Lingyunzi x≥32 has209/203/190/196. Their
right/up extent corroborates the established cast direction. It does not uniquely
solve light magnitude, ground slope, elevation or the NPC’s physical pose. The
shared cast ratio is inherited from the established art direction and hero/tree
rendering, with per-NPC receiver parameters independently measured here.

The shader consumes the candidate’s full unchanged continuous alpha. Exactly one
shadow pass goes after floor and before the normal object/body pass. Suppress the
entire original checker-bearing NPC sprite only while the new body+shadow pair is
valid. Any asset/region/configuration failure restores the complete original NPC
and clears the new shadow atomically. No extra ellipse/contact blob, source checker
overlay, shadow in raw, body tint or hidden pixel cleanup is permitted.

Keep original NPC cell placement, name, story, clicking, collision, layer and stable
depth semantics. No R6 promotion in this stage. This flat 2D proxy does not solve
stair/platform receivers or projected shadows onto other characters/buildings.
Lingyunzi’s richer gold ornament/tassels remain an accepted-to-review design
residual; a shadow test must not silently repair the costume.

## Prior runtime evidence supplement

`runtime-pose-evidence-review.json` records the observed artifacts and hashes.
Logs cover0/17/34/51/68/85/102/119 and completion136. Pixel comparisons repeat at
+68; Fangzhang is static and Lingyunzi changes through four phases. The51→68 seam
was exercised; the final135→136 seam is not drawn by the stopping script. Capture
waits pause its counter, so this proves logical update coverage, not uninterrupted
wall-clock cadence. Both runtime atlases exactly match the candidate hashes.

The prior captures are1082×812 against configured1024×768 canvas_items viewport.
`all-eight-native.png` is an unresized crop of that capture; its name does not prove
exact 1screen-pixel/world-pixel sampling. The parent’s pose gate stays accepted.
Next single-shadow review should establish exact1× viewport/window dimensions and
inspect both NPCs. The prior `four-phase-live.jpg` contains Fangzhang only.

## Next native gate for the sole runtime owner

1. Show exact1× off/on comparisons, all four phases and complete17tick loops through
   3→0. Confirm Fangzhang body and shadow remain static and Lingyunzi’s receiver
   remains fixed while its alpha silhouette breathes.
2. Inspect both soles/feet, crown cast and any weak-alpha fringe; no double checker,
   detached contact, body cut, phase-dependent projection or invented foot motion.
3. Check normal NPC/object front/back ordering without relocating roots, and keep
   platform/elevation claims outside this flat projection test.
4. On any required failure, retain the pure-pose-approved bodies and report the
   shadow limitation; never hide it with body warping or new generation.

Offline annotated foot boards are in ignored
`diagnostics/a13-npc/single-shadow-v1/*-all-four-boots-fixed-line-6x.png`.
Cyan is the proposed receiver; orange marks the measured edge proxies. These
technical overlays are not a shadow rendering acceptance test.

Reproduce measurements with:
`python Project/art_source/npc_fangzhang_rebuild_v1/prepare_single_shadow_contract.py`
from the repository root. It checks raw/atlas/source hashes and leaves them intact.
`GIT_SAVE_SINGLE_SHADOW.json` is the explicit minimal stage list; include itself.
