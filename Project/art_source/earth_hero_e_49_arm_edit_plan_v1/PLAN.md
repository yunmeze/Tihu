# Single49 near-arm LOCAL edit proposal, awaiting approval

## Actual three inputs
1. edit-base-raw49-UNCHANGED.png: byte-identical copy of earth_hero_e_49_control_v2/raw.png; only editing base. SHA7338f1181da26815cc9d2f3f4ec4437a6be303c112e160b00ec7d5d14c000cec.
2. source49-full128-8x.png: original full source, nearest8×, pose evidence only.
3. source49-sleeve-wrist-hand-regions.png: actual source crop[24,24,58,62], nearest16×, clean and region-annotated copies side by side. Every pixel of crop retained; no painted replacement art or hidden skeleton.

## Local scope
Raw1254×1254. Proposed inspection/edit envelope[330,365,485,580] covers near sleeve below red shoulder, forearm guard and hand plus potential newly uncovered slivers. This is a CONTEXT ENVELOPE, not permission to change torso/waist pixels inside it and not a machine mask. Keep red shoulder, head, chest, belt and hips, both legs, ankles and boots. Only minimally reconstruct surface exposed by removing the old arm silhouette. No changes to base scale or placement.

Diagnostic proposed-local-envelope.png in Project/diagnostics/earth_hero_e_49_arm_edit_plan_v1 shows scope. It is not an extra input or final art. Built-in referenced-image editing has no guaranteed pixel lock here. If unrelated content drifts, mark the control unsuccessful; do not repair by compositing old legs over new art.

## Targets and uncertainty
Original source sleeve surface roughly[34,39,43,51], cuff/wrist transition[35,50,43,54], hand group[40,53,46,59], waist reference[43,47,50,51]. Bounds uncertain±2–3 source pixels, overlap and are surfaces, not exact joints. Source low resolution does not resolve a hidden elbow. Hand group is BELOW source waist band, not chest-high. The change must be judged from visible whole sleeve/forearm route and hand envelope jointly, not a single point.

Keep prior registration fixed: scale0.1028549998260168 and its recorded crown translation from earth_hero_e_49_control_v2/MEASUREMENTS.json. No refit to an edited hand, no new per-body scale. Old hand surface approximately(389,548) maps(38.59,56.11); source representative(43,56) maps back to approximately(432,547) in raw. Thus the intended change is modestly forward, not a high fist. This is an approximate locator only: source hand±3 plus raw selection±8 yields a broad envelope; do not demand exactly43 raw pixels of anatomical motion. Shoulder/head armor differences limit crown-hand comparisons.

Compare source sleeve/wrist/hand regional relationships, preserved shoulder/chest silhouette and waist height. Require the favorable base49 leg chain to remain the same, including left ankle above-left of toe and tucked right ankle, not merely a similar foot center. Use raw difference outside allowed region as preservation evidence if canvas identical; unexpected widespread changes invalidate a claim of strict local editing. Existing base limitations remain, even if arm improves.

## Decision gate
One edit call only after explicit approval. Preserve raw/prompt/inputSHA. Research only; no animation assembly, runtime promotion, Git or GUI. A successful isolated edit would demonstrate local control, not a complete6 animation. No automatic retry.
