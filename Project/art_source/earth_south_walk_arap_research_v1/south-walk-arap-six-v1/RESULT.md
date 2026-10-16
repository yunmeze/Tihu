# Six-phase south walk: bounded 2D mesh candidate

## Result
Godot exported all six 512×512 transparent frames (57–62); CPU gates retain all source nonzero-alpha support, zero flipped triangles, zero boundary intersections or nonshared contacts, and zero core driver residual. GPU input hashes passed before/after; exit 0 and completion marker. Only VSync warning. This establishes a feasible textured mesh candidate, not original-animation fidelity or main-game acceptance.

Reviewed actual 1×/2× source/common-base/ARAP boards, three backgrounds, and the three requested transition pairs. No obvious holes, white fringes, or the earlier 59 toe horizontal shear at these sizes. Visible knee and boot armor remains legible. Low-alpha fringe anisotropy remains extreme in some triangles (maximum ~54.17), so geometric feasibility does not erase sampling risk. No further shape adjustment is made.

## Evidence and scope
- SOURCE_BASE_ARAP_SIX_1X.png / 2X.png: original, undeformed shared baseline, actual Godot export.
- ARAP_SIX_THREE_BACKGROUNDS_1X.png / 2X.png: dark, gray, light compositing.
- TRANSITIONS_58_59__61_62__62_57_1X.png / 2X.png: independent transition review.
- SOURCE_BASE_ARAP_LOOP_140MS_1X.gif / 2X.gif: six original phases, each 140 ms, 840 ms loop; GIF metadata read back. Prescribed-phase playback only, not measured game/display timing.
- SIX_CPU_GATE.json: complete per-frame hard gates and distortion statistics.
- REVIEW_AUDIT.json: timing metadata and rendered driven extrema.
- HELDOUT_HAND_READS.json: independent visible skin-patch readings, not wrist/joint estimates.

## Motion limitations
58→59 and 61→62 visible hand swing differs from the original: modern AI art has somewhat larger discrete transitions. Head/chest/arms were not warped to hide this. 62→57 leg ordering is readable in the pair, but static pairs and fitted endpoints do not establish a smooth loop. The exact source foot-terminal trajectory is a driving constraint, never an independent acceptance metric. Source anatomy hidden by long clothing cannot validate AI knees or hip centers.

One global 0.72 design scale and one shared origin are retained. Raw right-column −35 HD layout normalization is separately documented; no per-frame full-body scaling or pinned heads. Original small-head/long-clothing silhouette differs from modern broad-shoulder armor by design. This candidate does not claim original body proportions restored.

## Numerical cautions
ARAP used bounded iterations rather than proven energy convergence. Full-alpha fringe support was preserved with local feasibility repair and core fixed. 62's unchanged core-supported fringe minimum area ratio is 0.182456, above the original hard 0.1 gate; other frames reach 0.2. No low-alpha waiver, discarded pixels, or invented texture was used. Source-cell support preservation does not imply identical destination alpha counts after texture filtering.

## Next decision
Review the whole prescribed loop, optionally the separate native 50 Hz / seven-tick phase preview. Native preview is standalone and cannot establish main-game integration or runtime performance. No repository assets, animation indices, main-game code, or uploaded files are changed. All failed earlier mesh attempts and raw crops remain intact.


## Native preview outcome
Official five-loop run plus separate observation hold exited 0, input hashes unchanged. Actual viewport/window 768×464, content scale disabled; 1×128² and 2×256² targets verified in screenshot. Thirty events followed 57–62 five times, seven physics ticks per phase. Observed wall phase intervals ranged 106.429–215.352 ms (median 140.611; first 215.352), and four loop-onset intervals were 880.692 / 833.648 / 848.224 / 840.588 ms. This does not establish exact 140 ms display or main-game timing. The official reviewer captured one live phase only; continuous dynamic visual review remains open.

## Remaining issues, ranked
1. Original versus AI arms/upper-body are not the same per-phase posture. Independent hand-patch readings and transition boards show larger swings at 58→59 and 61→62. Foot fitting cannot establish whole-body fidelity.
2. Loop continuity, especially these transitions and 62→57, still needs continuous human review of the supplied GIF or longer native observation. Neither individual stills nor phase logs prove visual smoothness.
3. Extreme weak-alpha fringe anisotropy can create filtering artifacts at other scales/backgrounds; no obvious defects were seen at the reviewed 1×/2× three backgrounds.
4. Main-game integration and timing remain untested. The exported PNG candidate requires no runtime mesh, but is not installed.
