# SE idle/walk fixed receiver: auditable source contract

Status: source-only 2D trial. No physical-contact, terrain, continuous-loop, or native GPU acceptance is claimed.

## Decision and coordinate correction

The shadow-helper integration handoff reports that the current native preview compares the existing fixed horizontal candidates y86.0 and y87.5 through the same idle/walk sequence; final visual selection remains pending. This source-only analysis did not operate or directly validate the GUI and does not convert that relayed comparison range into visual acceptance. For each candidate, use one unchanged receiver for all ten frames: frame-local point (40,y), slope0, actor-relative point (24,y−64). The value86.5 is the joint-subset theoretical minimax reference, not a requirement to restart or add a parameter sweep. The value87.5 is the original visual compromise, not a unique decision or numerical optimum. Cast=(148/279,-111/279), opacity=.30, blur=.9, tint=(.035,.045,.055), exactly one pass. Body transform and immutable atlas remain unchanged.

All measurements use geometric texel lower edges, consistently with the old idle contract: x=mean(column+0.5), y=last alpha>=96 row+1. The walk lower visible boot edges are92/90/87/89/85/90. Their exact horizontal minimax is88.5; the y87.5 visual compromise has a maximum lower-visible-boot displacement of3.61px. Read-point uncertainty is approximately ±1px.

## What the original checker proves

All six original source frames were inspected together with the registered six-phase v3 atlas. In the constant exposed ROI x=64..95,y=50..95, every nontransparent texel is RGBA=(16,8,8,255), on even (x+y) checker parity. This is an observation limited to the ROI, not a global color-deletion rule. Source art and checker remain intact.

| Source | Exposed samples | Inclusive bbox | Centroid |
|---|---:|---|---|
| 51 | 127 | [64, 59, 82, 79] | (72.307,67.299) |
| 52 | 120 | [64, 58, 81, 76] | (71.567,66.333) |
| 53 | 146 | [64, 58, 82, 81] | (71.301,66.795) |
| 54 | 151 | [64, 57, 82, 81] | (71.106,66.179) |
| 55 | 131 | [64, 57, 81, 78] | (70.947,65.359) |
| 56 | 123 | [64, 58, 81, 78] | (71.610,66.537) |

The centroid spans only 1.361 px in x and 1.940 px in y. The exposed right boundary is x=81..82; top is y=57..59. Relative to root (16,64), this safely exposed region is x=+48..+66 and its top is y=-7..-5. It supports a stable right/up cast. The actor root is a drawing anchor, not proven ground contact.

This partial silhouette does not identify receiver slope, physical light, ground depth, support leg, or exact head-shadow correspondence. With y87.5, the source crown proxies project into/near the exposed lobe; the JSON records nearest-checker distance only as a compatibility check, never a calibration or correspondence.

## Reproducible foot-edge residuals at y=87.5

q=(x,g)+(g-y)*cast. Thus q-p=h*(.530466,.602151), |q-p|=.802483267*|h|. Positive h is a screen-space residual, not proven lift. The alpha>=96 threshold is measurement-only; shader sampling must use original continuous alpha. ROI and row/column evidence plus threshold64/96/128/192 sensitivity are in the JSON. Edge uncertainty is approximately ±1 native px.

| Frame | Foot | Edge proxy | h | Shadow minus foot (dx,dy) | Distance |
|---|---|---|---:|---|---:|
| 51 | A | [50.5, 92.0] | -4.50 | (-2.387,-2.710) | 3.611 |
| 51 | B | [35.5, 74.0] | +13.50 | (+7.161,+8.129) | 10.834 |
| 52 | A | [42.5, 90.0] | -2.50 | (-1.326,-1.505) | 2.006 |
| 53 | A | [38.5, 87.0] | +0.50 | (+0.265,+0.301) | 0.401 |
| 53 | B | [51.0, 85.0] | +2.50 | (+1.326,+1.505) | 2.006 |
| 54 | A | [29.0, 79.0] | +8.50 | (+4.509,+5.118) | 6.821 |
| 54 | B | [57.5, 89.0] | -1.50 | (-0.796,-0.903) | 1.204 |
| 55 | A | [30.5, 79.0] | +8.50 | (+4.509,+5.118) | 6.821 |
| 55 | B | [49.5, 85.0] | +2.50 | (+1.326,+1.505) | 2.006 |
| 56 | A | [43.5, 90.0] | -2.50 | (-1.326,-1.505) | 2.006 |
| 56 | B | [46.0, 80.0] | +7.50 | (+3.978,+4.516) | 6.019 |
| 13 | near | [36.0, 89.0] | -1.50 | (-0.796,-0.903) | 1.204 |
| 13 | far | [52.0, 81.0] | +6.50 | (+3.448,+3.914) | 5.216 |
| 14 | near | [36.5, 89.0] | -1.50 | (-0.796,-0.903) | 1.204 |
| 14 | far | [51.5, 81.0] | +6.50 | (+3.448,+3.914) | 5.216 |
| 15 | near | [36.5, 89.0] | -1.50 | (-0.796,-0.903) | 1.204 |
| 15 | far | [51.5, 81.0] | +6.50 | (+3.448,+3.914) | 5.216 |
| 16 | near | [36.0, 89.0] | -1.50 | (-0.796,-0.903) | 1.204 |
| 16 | far | [52.5, 81.0] | +6.50 | (+3.448,+3.914) | 5.216 |

52 has only one independently visible boot. 53 has two boots at close screen heights; neither can be called planted from this image alone. 56 has near-overlapping x positions. Cross-frame A/B labels are tracking proxies, not proof of anatomical side or support. A higher-screen idle foot may be further away on the same ground; treating it as height is an acknowledged limitation of the flat 2D approximation.

## Distinct objectives and native A/B

These are different minimax problems and must not be conflated:

- Walk screen-lower visible outsole only: y85..92 → exact horizontal minimax88.5; maximum2.809 px. This does not identify support legs.
- Joint idle both visible outsoles plus walk screen-lower visible outsole: y81..92 → exact horizontal minimax86.5; maximum4.414 px. This is the relevant joint-preview numerical comparison, still only a 2D residual objective.
- All visible feet including the short/high-screen walk foot: y74..92 → mathematical minimax83.0. This is not the intended fitting objective and would conflate swing/depth with contact.

The current native comparison is86.0 versus87.5, each held fixed across all10 frames; final visual selection remains pending. The value86.5 is retained only as a theoretical reference for the explicitly stated joint subset. This contract does not request a restart or further parameter sweep for the0.5px theoretical difference. Neither actual candidate is called the joint numerical optimum. Read points have approximately ±1px uncertainty; native acceptance is not asserted here.

## Fixed candidates and rejected fitting

| Horizontal y | Max walk lower-visible foot | Max idle foot | Max all walk feet |
|---:|---:|---:|---:|
| 86.0 | 4.815 | 4.012 | 9.630 |
| 86.5 | 4.414 | 4.414 | 10.031 |
| 87.0 | 4.012 | 4.815 | 10.432 |
| 87.5 | 3.611 | 5.216 | 10.834 |
| 88.0 | 3.210 | 5.617 | 11.235 |
| 88.5 | 2.809 | 6.019 | 11.636 |

The largest all-walk-foot number is the short/high-screen boot. It must be displayed as a residual rather than forced onto the receiver or described as a measured physical height.

Fitting a new line to the two visible feet per phase is explicitly rejected. Slopes for51/53/54/55/56 are +1.200/−.160/+.351/+.316/−4.000; 52 cannot define such a line. This causes arbitrary shearing/rotation with the swing pose and even violates the existing bounded slope contract at56. The fixed old idle13 line m=−.5,b=107 also gives the forward low boots of51/54 large negative residuals; detailed counterexamples are in JSON.

## Idle linkage and transition scope

Old idle13–16 lines have g(40)=87.000/87.133/87.133/87.061. Switching the same point to y87.5 moves its shadow by only .401/.294/.294/.353 px at x40. That small torso-center change must not be generalized to the feet: at y87.5 the near idle outsole shifts (−.796,−.903), distance1.204; far/high-screen outsole shifts (+3.448,+3.914), distance5.216. At y86 these distances become2.407 and4.012.

For the joint preview, keep exactly the same chosen line through idle16→51..56→idle13 so there is zero line-parameter jump. The body/alpha shape still changes naturally, so shadow silhouette continuity needs native review. Do not rewrite the already accepted standalone idle pilot to hide this distinction.

## Immutable inputs and implementation handoff

Walk atlas SHA256: 7c386900fe579018ef38cf00c7e160622abebef476f3ccebd9c6fd94923bcf38
Idle atlas SHA256: 91e7fb445775116ae2894900b76811757eda3898e78bf1e6881e38f933670ac9

The JSON lists every source/input hash, source ROI bounds/counts/parity, exact boot measurement windows, texel rows, geometric edge proxies, candidate transforms, all foot residuals, old-idle counterexamples and semantic limits. No generated art, raw atlas, registered atlas, registration, shader or runtime file was edited by this analysis.

Native owner must check single-shadow composition, alpha bounds, floor/object depth, feet residual appearance, all six phases, two loops and both idle transitions. No contact ellipse, duplicate source checker, per-frame receiver fit, body shift/deformation, stair/bridge or 3D receiver claim is allowed.
