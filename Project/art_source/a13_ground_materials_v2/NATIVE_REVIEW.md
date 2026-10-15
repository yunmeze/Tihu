# Bounded mirror terrain native diagnostic — 2026-10-15

Candidate registration SHA256 c0a29a6de8f1fca04204c90e9ce506e5dfb083285ec31e58ea6378f238ccb405. Scope remains exactly143 A13 floor placements and15 bindings, with2410 placements still source. This is a terrain candidate gate, not full-map completion or default selection.

Sole runtime operator executed the original A* route61,39→61,49→61,53, completing480 movement ticks and15 periodic samples. No source flags, road collision or object sorting were changed. The earlier async fixture re-entry failure is preserved as native-async-fixture-failed.log and excluded from passing evidence. Current native.log ends GROUND_ROUTE_PASS480 with no runtime errors reported.

The environment reviewer actually viewed court-source.png, court-new.png and route-contact.jpg. The new ground has less fine source noise and broadly matches the selected temple/tree materials. Grass still has clear leaf-grain and reflected dark-motif residuals; soil grain is more explicit than the source. The road head and narrow stone edge remain readable, with no observed tile-sized material panels inside the selected scope. Existing foreground trees and shadows retain their scene ordering. Unconverted trees/shrubs/NPC checker shadows remain source and are not newly generated ground features.

Important open boundary: moving south exposes a hard rectangular/horizontal transition from the143 candidate placements to source terrain. This is a visible bounded-scope seam. It must not be described as complete terrain continuity and has not been hidden by painting or unauthorized global replacement.

World lock: textures were cached from frozen world coordinates; movement samples show no obvious texture following the camera. world-lock.json compares nearby physical-image displacements, with the best shift consistent with the scaled world movement. The actual PNG is1082×812 rather than logical1:1, so these images do not prove exact GPU parity. The separate offline exported-atlas decode test is exactly0 RGB difference and remains a distinct result.

Evidence directory: /workspace/shared/legend-rebuild-ground/
- court-source.png, court-new.png
- route-contact.jpg, route-final-new.png, route-final-source.png
- native.log, preflight.log, world-lock.json

Pending parent selection decision. No further generation or scope expansion follows automatically from this diagnostic.
