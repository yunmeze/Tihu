# 58 translation-only CPU diagnostic: stopped at feasibility gate

No GPU request;61 not solved. Existing six PNG frames and source raw remain unchanged.

The approved revision3 masks have zero fixed/rigid shared-vertex conflicts. On the existing full-alpha final leg mesh,40,670 external fixed vertices stayed exactly unchanged;7,505 gauntlet vertices had translation-only drivers;1,385 cloth/fringe vertices were free. All source nonzero-alpha pixel cells were preserved.

First target stage was20% of the requested translation. Its initial full step produced270 flipped triangles (minimum relative area−1.75556), rejected immediately. Backtracking retained only positive-area, globally nonintersecting states, but after15 accepted iterations it stalled at minimum relative area0.10000018;24 further reductions could not pass the unchanged >0.1 gate. Stage driver residual remained1.23704HD; full requested-target residual8.61038HD. No target-reaching solution was produced.

The retained partial state has zero flips, zero full-boundary crossings/nonshared touching, and zero external fixed motion. These facts do not make it an accepted correction. Residual target error is large, and no visual trial is justified.

## Limiting support
LIMITING_TRIANGLES.json and FAILURE_LOCATOR_4X.png locate the first limiting cell at raw(135,158), alpha1, class3 edge transition, immediately outside the left metal forearm. Other compressed cells are near raw(285,230), alpha4 and(286,232–233), alpha2, beside the inner right-hand fringe/torso gap. This points to the one-cell weak-alpha transition being squeezed between a moving gauntlet and fixed exterior support, rather than a need to move shoulder/chest or alter fist orientation.

The first failed trial and all216 rejected backtracking attempts are retained. No weak-alpha exemption, pixel deletion, target weakening, or area-threshold relaxation was applied.

## Next technical option, not executed
A wider, explicitly bounded weak-alpha support-domain extension might let the outer fringe accompany the arm, while all visible chest/shoulder/leg material and the rigid gauntlet remain fixed/translated as approved. It requires a new frozen mask and protected-region preflight. It must not silently free torso pixels or couple across alpha=0. The current result alone does not prove such an extension can reach the target with zero intersections. No expansion or new solve is undertaken here.

This task tests a±2 logical-pixel uncertain phase-pacing hypothesis, not recovery of a unique original pose. Center residual is not independent acceptance; retained plate rigidity, unchanged body, and prospective whole-loop distribution remain separate review concerns.
