# Next input-method analysis only

## Finding
Full128 cells spend much input area on empty space. Body height is roughly72/128=56% of cell height; width about42/128=33%. At4× the body is about288px tall, versus about576px with8× fixed-crop rendering. A denser presentation can improve visibility of wrist/sleeve and ankle/toe surfaces, but there is no controlled evidence that empty space caused the failures. The source checker shadow overlaps the region beside the torso/legs and could compete with body boundaries; it cannot be proved responsible. v3 has genuine variation but substituted a generic bent-arm gait, indicating pose interpretation beyond simple resolution.

Important counterexample: v1 already used ONE shared crop[12,8,76,96] at8× (64×88 cells), not independently normalized frames, and also failed. Therefore returning to that crop alone is NOT a meaningfully new control method and should not justify a fourth full6 blind draw.

## Safe fixed crop option
Reuse the established common[12,8,76,96] crop for every source frame, all at8× nearest-neighbor. Transform is q=8*(p-(12,8)); original root16,64 maps32,448, then add sheet-cell offset. Keep full128 originals and hashes as unmodified evidence. No per-frame tight boxes or scale normalization. No pixels within that common crop are edited. Body containment must be checked against all6 source body/head layers before conditioning; alpha includes checker shadow so alpha bbox alone is insufficient to prove containment. If body edges fail containment, enlarge the ONE common box for all6 rather than clip or inpaint.

The fixed crop reduces empty padding but does not eliminate shadow within the crop. Do not automatically mask it out: any overlapping ambiguous real-body pixels must remain. A named annotation can identify shadow as ignored historical content without repainting the actual source. A clean-body extraction needs separate evidence/approval if not available as an original layer.

## Meaningful next constraint change to propose, not execute
Before any complete6 retry, isolate the observed failure mode: a source-derived sleeve/forearm/wrist/hand REGION relationship, alongside the FULL SAME-POSE source and both legs. A fixed common upper-body crop for all phases (for example[24,20,58,61], subject to inspection) enlarges the actual sleeves; it is additional analysis, not final art and not a precise hidden skeleton. Show source hand GROUP envelopes with visible sleeve contour and chest/waist reference bands; do not connect a fabricated hidden elbow. Explicitly distinguish the source long low forearm route from the generated bent high-hand route. No rejected raw used as main pose authority.

Use small approved control research only if parent later authorizes: choose45 and49 because they test backward and forward hands while preserving materially different leg chains. Require BOTH leg/ankle/toe regions and sleeve/wrist/hand route in the same result. Compare original coordinate-mapped common crops, not normalized anatomical landmarks. Do not combine separately generated body parts or isolated approved frames into a claimed full animation.

If this new region-level constraint succeeds across the two contrasting phases, prepare a fresh full6 plan using same commoncrop and phase-specific upper-body evidence, keeping source order and full128 registration map. If not, stop imagegen repetition and report the control limitation. No tool has demonstrated exact pose locking; a longer prompt or larger crop is not a guarantee.

This document prepares analysis only. No new boards, source masking, imagegen, runtime, Git or GUI actions.
