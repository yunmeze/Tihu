# S six-phase texture-suppressed visible-surface research

## Result and actual boards
All six alpha/support checks passed. Original texture is removed completely from the silhouette and core maps, while the exact index18-excluded source alpha remains unchanged. These are analytical diagrams, not generated/final art.

Diagnostic directory: Project/diagnostics/earth_s_pose_partition_research_v1
- original-full-source-full128-sixphase-4x-gray.png retains original complete body/head and baked index18 evidence.
- source-index18-excluded-full128-sixphase-4x-gray.png retains clothing texture for audit only.
- silhouette-full128-sixphase-4x-gray.png suppresses all texture.
- surface-core-full128-sixphase-4x-gray.png marks conservative visible cores.
- source-silhouette-surface-review.png stacks those four complete six-phase boards.
Transparent counterparts and per-phase128 outputs are retained. Every board uses57,58,59 /60,61,62, complete128 cells, 4× nearest display and root16,64; no crop-fit, per-phase scaling, mirroring or interpolation.

## Meaning and uncertainty
Blue marks visible sleeve interiors, pink tiny visible hand-skin cores, green tiny trouser patches above the observable material transition, gold distal boot/toe surface only. Both screen sides use the same category colors, not anatomical identities. Gray includes the entire head/torso, joint/occlusion regions, unclassified surfaces, class overlap and one-pixel uncertainty boundaries. Exact alpha edges are retained but remain gray. Nothing is identified as knee, ankle, elbow, support leg or ground contact.

Proposals come from inspected original pixels and saved surface proxies. Each proposal is eroded by1px, intersected with a1px-eroded true support, and conflicting labels become gray. Class assignment remains manually inferred, not segmentation ground truth. Both hands survive as very small cores (total2–5 pixels per phase); this conservatism deliberately avoids inventing fingers or a precise wrist. Large leg interiors stay gray rather than guessing hidden chains.58 right and61 left short boots retain only their actual distal visible patch; no shaft/ankle is invented.

57/60 retain opposite extended visible chains.61 visibly recovers from60, and62 preserves the source passing separation before57. Sleeve and hand-height exchange survive independently of leg changes, avoiding a legs-only encoding. These maps do not assert physically exact skeleton amplitudes. Boot-tip geometry alone is not a body-pose metric.

The preserved outline still includes original garment shape/protrusions: it is NOT a naked or anatomical body. Removing texture can reduce silver-waist/boot-binding appearance competition, but some depth/overlap cues are lost. Gray gaps must not be filled with fabricated joints. Model adherence improvement is untested; wait for the E45/49 method study before any S generation decision.

## Proof/reproduction
Run the sibling index audit first, then python prepare.py. COORDINATE_PROOF lists inputsSHA, exact coordinate transform, every proposed region, resulting class counts and alpha equality/support XOR0 for all6. Scripts affect only new research/diagnostic directories. Source assets, failed raw/edit evidence, registrations and runtime remain untouched. No imagegen, GUI, Git or runtime action was performed.
