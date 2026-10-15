# Eight-direction identity continuity plan (preparation only)

Date: 2026-10-15. No new images, runtime changes or extra direction assets are authorized by this document.

## Current evidence and boundary

- Reconstructed working identity v2 is a newly generated design, not recovered original approved art. Its complete front-three-quarter body is not a pose input for future groups.
- SE idle13–16 has an optional four-frame preview with a single alpha-derived shadow. Default source remains available.
- SE walk51–56 source-only v3 is accepted as a pose candidate after all-six and15-state engine views. Moving shadow/depth acceptance is pending.
- v3 waist/shin panels differ locally from identity/idle. This is a recorded design residual, not a claim that every plate is identical.
- Other seven directions and all run assets remain original-source art in this rebuild.

## Verified source indexing

From data/hero/movement.json: direction order N, NE, E, SE, S, SW, W, NW; ID=base+direction*phase_count+phase0.

|Direction index|Facing|Idle 4|Walk 6|Run 6|
|---|---|---|---|---|
|0|N|1–4|33–38|81–86|
|1|NE|5–8|39–44|87–92|
|2|E|9–12|45–50|93–98|
|3|SE|13–16|51–56|99–104|
|4|S|17–20|57–62|105–110|
|5|SW|21–24|63–68|111–116|
|6|W|25–28|69–74|117–122|
|7|NW|29–32|75–80|123–128|

Cadence12/7/5 actor updates is the reference/current clip mapping. It is not independent proof of the original EXE action-entry clock/reset or movement speed. Never infer speed from7/5.

The original32-idle board was actually viewed for this plan: N is back, NE andNW rear-three-quarter, E andW opposite profiles, SE andSW opposite front-three-quarter, S front. No mirrored direction substitutes. Each direction's own body/head layer offsets and real original four phases are authoritative. Source artwork/checker pixels are preserved during reference extraction.

## Shared identity rules and missing back design

Already evidenced: adult East Asian short-black-haired man; clean silver-gray/black-titanium fitted plates and black technical undersuit; muted wine-red shoulders/knees; restrained thin cyan; fingerless black armored gloves; modern fitted boots; empty hands, no back sword/wings/cape.

Shared palette/material does not imply identical projected widths. E/W chest must remain narrow; NE/NW must not turn to front view because a portrait was supplied. Shoulder armor surface width is not a measured skeletal shoulder joint. Never use per-frame bbox fitting to force all directions to equal width or height.

The rear armor is not defined by the current SE design. A future **explicit new back-design reference** needs review before N/NE/NW production. Suggested design continuity, not approved fact: compact silver scapular panels linked around the ribs to the existing front shell; black technical central spine area with limited articulated plates; wine-red shoulder caps following the same construction; plain segmented rear waist; only subtle cyan seams. Avoid a new large glowing reactor, backpack, hanging plates, swords, or cloth. Source back silhouettes and camera must remain authoritative. Persistent left/right asymmetries are not established by a perspective-dependent near/far shoulder size.

Back design may later be generated as a small direction-specific design study, clearly separated from completed animation. It must not be passed as a full-body pose template when generating real phases. Once accepted, crop rear hair/neck, scapular plate, side rib panel, rear waist, elbow/glove back, knee-back/boot heel into disconnected detail swatches. No whole torso-to-leg silhouette in the material reference board.

## Direction-matched conditioning

- S/SE/SW: visible face and front armor fragments can supply identity, but source head angle and turns remain primary.
- E/W: profile face/hair should be separately direction-matched. Do not feed a large forward-facing portrait that turns the profile toward the viewer. Use small armor surface/side-glove/boot-profile swatches.
- N/NE/NW: omit frontal face entirely. Use only rear/crown hair, rear neck and the reviewed rear/side armor fragments. A front cyan chest panel must not be reproduced on the back.
- Each group uses its own original COMPLETE strip as the actual edit canvas. Fixed common crop for the group, no individual bbox scaling. Do not supply failed generated complete people, even labeled "identity only".
- All four idle or all six walk/run phases are one whole output. Source-hidden surfaces remain uncertain; do not force two independent hands/boots. Distinct source frames stay distinct, and truly identical source frames are documented instead of inventing breathing.

## Staged future direction plan

After SEwalk single-shadow/depth gate, prepare adjacent E9–12 and S17–20 source conditions. Generate at most two groups concurrently only when separately authorized. First validate their four idle phases against SE; then their own walk groups. Do not use a single direction chart to fill animation slots.

Suggested native turn sequence: E→SE→S→SE→E using their own matching phases, then NE→E→SE and S→SW→W; after reviewed back design, N→NE→E and W→NW→N, finally complete clockwise and counterclockwise loops. Original direction mapping determines the visible change; no mirrored or automatic half-cycle substitutions.

Registration: common uniform scale for each complete generated group, per-frame rigid translations from several source head/neck/chest/pelvis/visible boot surface proxies. Compare cross-direction body proportions against locked SE at native scale. Do not force uncertain cloth/armor point coordinates, normalize by head top alone, or flatten foot levels to idle.

Per-direction gates: original complete phase analysis and source SHA → full-group imagegen → actual alpha and direction/occlusion check → recorded common registration → native own idle/action/idle and full loop → adjacent direction turns → one phase-matched shadow and actual front/back object depth. An accepted pose group is not automatically a runtime/shadow pass.

## Shadow continuity

A shared right/up light direction can be compared against exposed original checker regions. Receiver parameters remain an explicit2D approximation. Idle's two static sole proxies cannot be reused as two planted contacts for walking; raised feet are not receiver anchors. Keep actor-root and ground parameters stable, then inspect actual motion/entry/exit with one mutually exclusive shadow. Terrain platforms/height remain a separate gate.

## Evidence references

- data/hero/movement.json; tools/hero/extract_movement.py
- diagnostics/hero/idle-all-phases.jpg (review only, ignored)
- art_source/hero_identity_rebuild_candidate_v1/request-manifest-v2.json
- art_source/hero_se_idle_rebuild_v1/v1-registration.json
- art_source/hero_se_walk_rebuild_v1/request-v3.json, v3-registration.json, v3-native-pose-review.json
- art_source/hero_se_walk_rebuild_v1/source_only_plan/input-provenance.json
