# Review F1/F2/F3 revision

Based on `../a00-trial-review-v1/REPORT.md`, after parent authorization. The initial F1/F2/F3 revision changed tests/docs only, retaining core SHA 93b7a6ebdafa17aa5c766b8b9af78154641909061c47602e3f2d3178b99bf139. A later engine attempt exposed a separate production portal JSON-number comparison defect. The parent explicitly approved the narrow predicate correction recorded in portal_numeric.diff; see ENGINE_HISTORY.md. The VM remains unchanged.

## F1: invalid source stand tiles

PRE_REVIEW_FIXTURE_ISSUES.json retains the old test SHA, the original chief (75,55) and mother (67,74) flag-2 cells and the review identity. The corrected test uses manually placed, source-walkable (74,54)/(67,76). It checks the fixture's source flag before assigning position. No actual Movement route, native click or A13-to-A00 transition is executed by these tests.

## F2: portal and publication limits

Four original portal records have synthetic input/output transaction checks only. No independent natural traversal claim remains. Original (64,72) is also a walkable raw neighbor of portal2 (63,71), but reaching it diagonally crosses the solid corner (63,72). With current Movement's no-corner-cut rule, portal2's sole legal one-step neighbor is portal3 (64,71). The review wording was clarified with the reviewer; the automatic portal3-first limitation is unchanged.

movement_reset is asserted only as a request returned by the pure core. There is no Movement.path here to cancel. core.commit returns detached values and does not consume the ticket or publish state. The integration owner must swap once, expose its new CURRENT state, and reject subsequent stale callbacks. Actual paths, world-ID rebinding, complete rng_state, reentrancy prevention, detached scene setup failures and final publication remain separate unimplemented work.

## F3: error identity and late boundary

Every negative now asserts an exact error code, including VM error.code. Money, bag, resource, map identity, target, stale ticket and source failures must reach their named boundary. The serial/revision/weight fixtures additionally call the same Inventory stage/commit primitive on an isolated probe, require successful actions 1–5 and failure on action6, and assert the fifth result reached the exact ceiling. The full Core.stage still must return the prefixed expected error and leave the complete live snapshot unchanged.

Resource failure is followed by restage/replay with a restored callback against the same live baseline and captured request. Expected IDs are :2–:7, next_serial/revision 8, gold100/ET4 and nine cleared gates. Success is returned without mutating that old baseline; this explicitly tests the pure-return boundary rather than pretending publication occurred.

## Status

75 source/dependency/fixture-scope checks plus four completed-run identity checks passed (79 total). Prior engine evidence is: first check exit1 (test type inference), second check exit0 after explicit Dictionary type; behavior failed and was interrupted with session exit130, no completed assertion total. The current fixture/core numeric revision completed author-job-03 in its explicitly granted exclusive window: check exit0, behavior exit0, 539 passed / 0 failed, both ERROR scans clear; both engine children reaped and queue released. No main/source/art/branch/remote changes were made.
