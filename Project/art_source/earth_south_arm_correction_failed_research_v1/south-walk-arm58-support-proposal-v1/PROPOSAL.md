# Read-only support-domain correction proposal

The58 CPU failure has two different fringe causes, not one background category. On the4-neighbor graph of actual alpha>0 pixels:
- raw(135,158), alpha1: distance9 to visible moving gauntlet,27 to fixed visible material. The frozen exterior there likely pins an arm-associated tail.
- raw(285,230), alpha4: distance13 to moving gauntlet,3 to fixed material. raw(286,232–233), alpha2: distance12–13 to moving gauntlet,4 to fixed material. These are closer to the fixed torso side.

Distances are image-support adjacency measurements, not proof of anatomy or true occlusion ownership. They never cross alpha0. The old rigid region contained2104 weak-alpha cells,229 of them closer to fixed visible material. Blindly widening the rigid patch is therefore the wrong correction.

## Proposed partition, not yet generated or solved
1. Keep the complete visible gauntlet/skin mechanical core (alpha≥64) rigid with the same translation-only hypotheses. Keep all original alpha/RGB for rendering;64 is a mechanical partition threshold, not a cutout.
2. Preserve existing fixed visible material, all fixed head/shoulder/strap/leg support, and the fixed torso-side visible boundary. Do not reset the successful leg mesh.
3. Classify weak-alpha arm-edge support using geodesic adjacency to moving versus fixed material seeds. Arm-associated tails should be eligible for displacement extension rather than arbitrarily fixed one cell beyond the hand-drawn polygon.
4. Keep weak-alpha cells clearly attached to the fixed torso/head/legs fixed. Treat equal/near-equal ownership as an explicitly shown uncertain transition zone, never silently attach it to the arm. If maintaining a fixed torso-side fringe leaves no valid transition corridor, report that incompatibility instead of moving the torso.
5. A harmonic or bounded smooth extension over the eligible original pixel-cell graph may provide the fringe displacement. Boundary displacement originates only from known moving/fixed surface support. No synthetic alpha cells, hole filling, links across alpha0, hidden joints, or inferred palm rotations.
6. Before solving: freeze a new ownership/mask overlay and seed list; verify fixed/rigid shared-vertex conflicts0; identify all uncertain attachment cells; prove protected-region support unchanged. Changing low-alpha ownership cannot be justified merely by requiring the target to succeed.
7. After explicit approval, positive-area/full-boundary-contact backtracking remains mandatory. Preserve rejected paths. Do not loosen the0.1 gate or reduce the hand translation invisibly.

This is a revised technical support strategy, not a new motion target. The ±2px source uncertainty, no-rotation design differences, and whole-loop independent review remain unchanged. No additional solve or GPU export has been performed.
