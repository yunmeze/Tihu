# A00 trial core v1 — isolated candidate

## Result

Implemented a small source-bound, replayable A00 trial core under `owned/`; the published repository is unchanged. Source/fixture verification passed 75 static checks after the exact numeric-identity fix; four additional retained-run identity checks bring the final static total to 79. The first check-only run failed on a test type inference; the explicitly typed revision parsed successfully. Its behavior run encountered errors and was interrupted (session exit130, no final assertion count). The corrected numeric revision then completed author-job-03: check exit0; behavior exit0, 539 passed / 0 failed, both ERROR scans clear. The engine children were reaped and the exclusive window released. Native UI, performance and Windows remain unverified.

This is not a playable A00 release. It provides the isolated transaction core and integration contract needed for a later reviewed runtime adapter. Existing published main still permits only A13 source NPC0/1 and still uses the original cloth-only profile.

## Files

- `owned/scripts/core/a00_trial_core.gd`: strict source admission, three-template authority projection, exact A00 arrival attachment, natural dialogue intent gating, same-map house portal intents, pure stage and replay commit.
- `owned/scripts/core/dialogue_vm.gd`: the existing VM with one explicit opt-in A00 extension. Only CHANGE money + 100 and the two exact GIVE names/counts can emit staged reward events. Default behavior remains fail-closed. The low-level VM is not the public source-authorization boundary; A00 core is.
- `owned/tests/test_a00_trial_core.gd`: behavior/replay/failure test suite, revised after independent review and an incomplete engine attempt; the latest numeric revision passed 539 assertions. Synthetic actor fixtures use source-walkable (74,54) and (67,76); this is not movement/path validation.
- Four byte-identical read-only small core dependencies: inventory_state, default_warrior, npc_source_identity and map_load_bridge. They are not symlinks. There is no large Project clone, source-data clone, texture copy, .godot cache or new image.
- `verify_static.py`, `STATIC_CHECKS.json`: read-only source re-decode and dependency checks. Writers reject a symlink at the target or any ancestor and stay under this owned root.
- `BASELINE.json`, `dialogue_vm.diff`, `portal_numeric.diff`, `OUTPUT_SHA256.json`: baseline/source references, reviewable VM and narrow core deltas, artifact identities.
- `ENGINE_HISTORY.md`, `review-artifacts/`, `coordinator-job/`, `author-job-02/`, `author-job-03/`: fixed prior inputs, logs and incomplete/failing engine evidence. `run_serial_headless.py` is the next-window fail-fast runner, not an engine authorization.

## Authority and replay

`attach_arrival` admits only an already-committed natural A00 arrival at (138,12), ET3/ET4, with STOP off. It does not modify the A13 runtime or claim to execute A13 itself.

The trusted integration owner supplies CURRENT authority and context on every request. The context carries the prepared map/identity sidecar, world ID, epoch, revision, actual actor position, STOP/RNG projection and a tiny dialogue cursor. Neither context nor VM view owns an inventory. Only authority.inventory stores instances. `project` validates that same inventory against a narrow catalogue containing cloth252 and medicines0/5; it calls the existing default profile's non-inventory validators directly and does not create a filtered inventory mirror.

`stage` clones only unpublished values. The A5 reward is six existing Inventory.stage/commit acquisitions on the candidate authority, with deterministic unique IDs. Item ID0 is the canonical string "0", never a false/empty marker. Medicines are admitted for reward storage only; this does not enable healing, consumption or stacking.

`commit` takes the current inputs again, fingerprints their complete content, replays the original intent against exact source bytes, validates resource availability again and compares the entire replayed ticket. Only replay-owned outputs are returned. The future runtime must prepare its detached world/actor successfully, then replace authority, world/map, movement, source sidecars and dialogue in one owner-controlled publication. A returned result is not itself live publication, and movement_reset must be honored to cancel old routes.

The mandatory resource callback must be trusted and read-only. It gets a detached map. Current tests use a synthetic true/false callback; this is not artwork/resource-loader validation. A later scene adapter must use actual resource preflight/setup and prevent reentrant publication. Main's current Profile.project and NPC service must not be bypassed or globally opened.

## Provenance

Authoritative design investigation: `../a00-next-stage-plan/REPORT.md` and `SOURCE_INDEX.json`, each maintained separately. This candidate re-read original A00.lpMap and Item0.lpRes, checked parsed-map equality for all decoder fields, source NPC1/3 identities, the original four portal records, A1–A5 offered buttons, A5 instruction order, nine closed gate cells and raw item0/item5 record bytes. Exact baseline hashes are in BASELINE.json.

- Original A00.lpMap: 906f33edb6d0c7181629ba37296829a6b8adaf9cde2637ffc4c2530e2c5c352f
- Project A00.json: 0f921a2714cab0a29383a8a25631b515b2de98fa38c02ed4701f0a19d3355868
- Chief source1 script: 5d878f446b2d326b0b5a094cbf0e0fd48b6a63408bef35481374f76a6e4d5bd4
- Mother source3 script: 767959faa11f8e080b5a9b75ebfa606416e7632822ccd3a2268c1bae71146879
- Item0 bytes [10,106): b94caae4a24fec21c462bad80276282286547b30c2228dce3106ce305d5407dc
- Item5 bytes [494,590): c94c746f423b561498d7a04c6d022288f20aedf5f56cda19f4083e7978e1f084

Original text proves A5 entry performs the reward, mother is optional and ET4 START cannot regrant. Original executor rollback/capacity/overflow behavior is unknown. The all-or-nothing transaction, MAX_INTEGER ceiling, template whitelist and 0.25 portal trigger are explicit engineering safeguards/adaptations. A01 name-versus-ID conflict is untouched; no monster lookup, AI, combat, death event, drop or timer behavior is implemented.

## Engine checks and numeric revision

See ENGINE_HISTORY.md for exact prior inputs, logs and exits. The original JSON parser materializes coordinate words as numeric float Variants. Whole-Array type equality incorrectly rejected preserved fixture cells and, independently, exact original portal records. The parent approved separate narrow corrections: fixture comparisons now validate every word as finite/integral and exactly equal; the production portal predicate validates its exact five fields, same-map target and four finite/integral coordinates against the bound original record. No truncation, tolerance or string coercion is used. Fractional, wrong-coordinate, nonfinite, bool/string/null, extra/missing-field and wrong-map cases are explicitly rejected by new tests.

Only a newly granted exclusive serial window may execute the runner. It uses owned HOME/all XDG directories, headless display, explicit Dummy audio, per-stage time bounds and active log monitoring that terminates the engine process group on the first ERROR/SCRIPT ERROR/FAIL. It records input hashes, PID, command, exit and scan. Prior failed logs are never overwritten. A completed exit0 and final zero-failure assertion summary are required before claiming behavior passed. The current revision completed that authorized window in author-job-03: check0 (0.608s), behavior0 (146.256s), 539/0 assertions, clear ERROR scans. No later run is authorized implicitly.

The repository argument is read-only input; tests write no files. The pure replay approach rebuilds original A00 for strict map validation and has not been performance-measured.

## Remaining work

1. Targeted review of portal_numeric.diff after the completed serialized 539-assertion pure-core run.
2. Narrow runtime adapter that keeps the existing opening authority, feeds actual actor/world identity, honors movement_reset, validates detached world resources and atomically publishes replayed output.
3. Native validation of actually reachable portal entries, optional mother and chief routes/buttons; explicitly resolve portal2/portal3 precedence without changing original records. Add A5 late resource failure, ET4 close/reopen, stale callbacks and collision/render consistency.
4. Cold-package/Windows checks and separate A00 visual scope. No expansion to A01 combat while the source identity conflict remains unresolved.

## Independent review fixes (F1/F2/F3)

The review at `../a00-trial-review-v1/REPORT.md` found the previous chief (75,55) and mother (67,74) test positions had source flag -2 and were not reachable under current Movement. `PRE_REVIEW_FIXTURE_ISSUES.json` preserves both old cells, the old test SHA and the review SHA. Tests now manually place the actor only at verified walkable (74,54)/(67,76) for transaction checks. They do not execute Movement.request/step, traverse the house-to-NPC route or prove native clickability.

Four portal records still receive synthetic transaction tests. Portal2 (63,71) has only portal3 (64,71) as a legal one-step Movement neighbor after corner-blocking, so normal automatic portal3 activation can prevent reaching portal2 separately. There is no claim of four independent natural traversals. `movement_reset=true` is a returned instruction, not a demonstrated path cancellation.

Every authored negative test now asserts its exact error code. Separate isolated Inventory probes require acquisitions 1–5 to succeed, acquisition 6 to fail with the intended serial/revision/weight error, and the fifth result to reach the exact corresponding ceiling. Resource failure tests then restore the callback and retry against the same untouched live baseline: expected IDs remain :2–:7, next_serial/revision 8, gold100, ET4 and the nine gates. These assertions completed in author-job-03 as part of the 539/0 run. The interrupted predecessor remains incomplete/failed and is not substituted for that result.

`core.commit` is pure: repeated calls using the same old base can return the same successful values. Global exactly-once publication comes only from the owner synchronously adopting the first output, advancing CURRENT context and rejecting the subsequent stale ticket. No final runtime owner, actual world-ID rebinding, complete RNG-state proof, reentrancy guard or detached world setup integration is included here. Those are still mandatory before runtime acceptance.

No tracked main files, original sources, assets, branches, commits, remote refs or publication state were changed by this work.
