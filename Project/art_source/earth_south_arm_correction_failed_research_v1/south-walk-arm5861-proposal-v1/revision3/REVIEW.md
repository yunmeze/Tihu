# Revised mask proposal, still NO SOLVE

Revision3 supersedes the initial masks only as a review candidate. Initial284/291 fixed–rigid conflicts and revision2 failures remain preserved.

Changes are pixel-support classification only; raw RGBA, final leg geometry, and all six exported frames are unchanged:
- Expand distal patch support at most four raw pixels to recover clipped antialiased/material boundary cells. Added alpha≥128 cells:58L14,58R55,61L52,61R53; all additions are shown in amber on the review overlay.
-58L expansion approached the belt. All x≥181,y≥188 are excluded from its rigid class, preserving the visible belt side as fixed. This is a visible image-space exclusion, not a joint landmark.
- One-pixel incident fringe cells with alpha1–63 receive an explicit pink transition class instead of being dropped or forced rigid. Counts58L133,58R106,61L163,61R71. They remain original pixels; no coupling crosses alpha=0.
- Small high-alpha contact cells at the upper patch boundary join the dark cloth transition, limited to y<rigid_y_min+12 raw pixels. This is below the frozen shoulder/strap band. No high-alpha contact elsewhere is freed.

Every side now has zero fixed+rigid shared-vertex conflicts and zero unresolved high-alpha noncloth neighbors (PREFLIGHT.json). This is only a compatible constraint partition, not a feasible deformation: positive areas, global intersections, and possible collisions during the proposed translations have NOT been solved/tested.

Classes:0 fixed,1 visible cloth transition,2 distal skin/gauntlet translation,3 weak-alpha edge transition. All vertices outside the arm transition/rigid regions retain their existing boot-corrected positions. Fixed incidence wins at class0/transition borders; rigid incidence wins at rigid/transition borders. No fixed+rigid incidence is allowed. No shoulder, head/chest, belt or leg deformation is requested.

The intended translation hypotheses, uncertainty, independent temporal review and no-rotation limitations remain in ../PROPOSAL.md and ../CONSTRAINTS.json. Review this overlay before authorizing any solve. A compatible partition is not motion acceptance.
