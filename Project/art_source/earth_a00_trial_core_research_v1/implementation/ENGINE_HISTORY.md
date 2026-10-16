# Engine history and exact numeric correction

## Attempt 1: coordinator check only

- Inputs: core 93b7a6ebdafa17aa5c766b8b9af78154641909061c47602e3f2d3178b99bf139, tests 194be360d67d2546f10e2bbb023252d7780b1328699de19255e3f84948cd31fc.
- coordinator-job/check.log and check.exit: exit1, test line324 could not infer changed_authority type. No behavior run.
- Narrow fix: changed_authority explicitly Dictionary. No production core change.

## Attempt 2: author exclusive queued window

- Inputs pinned by author-job-02/FROZEN_INPUTS.json: same core, tests 6ec0c0b450f2404f44dabf05a7f681187a07aa4ec5fd78c37e2c6f4392d7dfb2.
- Godot v4.6.3.stable.official.7d41c59c4, headless, explicit Dummy audio and owned HOME/XDG.
- check-only exit0, ERROR scan false.
- Behavior first failed at test118/119: preserved source cell arrays were numerically correct but JSON integral-float words failed whole-Array equality against integer literals.
- The original runner did not actively monitor the log while waiting. Before the observed errors were interrupted, further portal checks executed: exact original source portal records were rejected and outside_portal_trigger negatives instead observed portal_identity_mismatch. These are a genuine production core defect, separately recorded from the test fixture defect.
- Execution session was stopped with Ctrl-C, exit130. Natural engine exit and completed assertion count are unknown. No final summary exists. This run is INCOMPLETE/FAILED, never a partial pass. The closed session could no longer be polled; the log stopped changing and no owned engine was visible before releasing the exclusive queue window.
- author-job-02/behavior.log SHA256: 9ea10c91e7b4787be2b914ff33ff7f3b0764ad8271f027e7866b6a8e09598fee. Original logs and frozen inputs are retained.

## Authorized narrow changes, tested in attempt 3

- Preserve reviewed core and interrupted test inputs under review-artifacts/.
- Fixture helper same_integer_words requires exact array length and validates each finite integral numeric value against the exact expected integer. No int truncation or tolerance.
- Production portal_record_valid requires exactly x,y,targetX,targetY,target; target must equal the original same-map string; the four coordinates must be finite integral numbers exactly equal to the bound source portal. Source index remains a native integer. Core change scope is only the old line69 comparison plus this predicate; portal trigger, movement, authority, rewards and replay behavior are unchanged.
- New positive tests cover equivalent ints/integral floats and original JSON. New negatives cover fractional values, wrong integral coordinates, NaN/infinity, booleans, strings/null, extra/missing fields, wrong map and wrong source index.
- Current core SHA256 d0e98f662c99d3f474a2d2ce2a065fda7adea0f4a23291f2ff00b03600b1b399.
- Current tests SHA256 2787f3bf052c098379a2a819c92154e27a1e44aaf92919946665b9102d0686bd.
- Next runner actively checks the log while the child lives, terminates/reaps its own process group immediately when an error is observed, stops after any failing stage, and stores exact outcome. A new explicit serial window is mandatory. The runner itself does not grant permission.

## Attempt 3: corrected numeric revision, complete pass

- Planner explicitly granted author-job-03 to this author as sole engine executor after the complete-checkout import released its engine. The root had approved both narrow fixes and required a new exclusive window.
- FROZEN_INPUTS.json records all eight owned input hashes, runner SHA, commands/environment scope and bounded stage limits. Core d0e98f66… and tests2787f3bf… match the complete hashes above.
- check-only: exit0, 0.608 seconds, ERROR scan false. Log SHA256 a9912b85473f126d3f4f63ec824170c828df3473a292f866dde86cafda5b66da.
- Behavior: natural exit0, 146.256 seconds, 539 passed / 0 failed, ERROR scan false. Log SHA256 7982e589415496510e15519ebc3db9039c22221614fb6f71385968d102e9c79c.
- Both engine children were waited/reaped, the runner naturally exited0, no additional engine was launched, and the exclusive queue window was explicitly released. No failure-driven kill was needed in this attempt.
- This is a completed pure-core/fixtures result only. It does not prove actual walking, four natural portal entries, actual Movement.path cancellation, renderer/resource loading, owner single publication, full RNG preservation, world-ID rebinding, reentrancy safety or Windows packaging.
