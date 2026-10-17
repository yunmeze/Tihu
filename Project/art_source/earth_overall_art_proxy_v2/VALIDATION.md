# Frozen v2 validation plan — engine execution requires root approval

No new executable test fixtures are included in the runtime whitelist. Reuse the coordinator's existing complete natural-GUI A00 route and reward/rollback fixtures, adapted only to select the new scene; never replace the trial core or relax its checks.

## Render isolation

- Run only res://scenes/earth_overall_art_review_v2.tscn in a fresh approved validation copy. Default main/F5 unchanged.
- Before A00, A13 has no proxy and original visuals/registrations remain active. Confirm existing A13 qualification logs.
- On A00, authoritative world.get_script().resource_path must still be res://scripts/map_load_world.gd, with exactly one child ArtProxy and the original controller's existing identity checks passing.
- Confirm parent's self_modulate alpha zero suppresses only its own pixels; child's own alpha is original, and inherited modulate/visibility does not suppress the child. Check no duplicate hero/NPC, ground or shadow drawing. If false, reject this candidate rather than weaken identity/hash guards.
- Compare ground, building doors/stairs, three tree roots, mother's 77..80 idle feet and original hero/Mon sprites while walking and panning. Capture more than one animation cycle. The mother has a uniform source scale and per-frame rigid translation, not body deformation; measured foot anchors match but full animation remains unvalidated.
- Repeated map transactions: new source world owns a new proxy; old parent/free destroys old proxy. Verify WeakRef lifecycle and no old-world visual overlay. Parent shader/material/clipping or pre-existing children should cause source fallback, not attachment.

## Atomic asset fallback (run before staging, not after rewards)

In a disposable test copy, temporarily hide one generated PNG or change one registered texture SHA. Retain the original unchanged fixture for restoration. Candidate preparation must return its original gameplay result; no proxy is attached and original world stays visible because parent suppression happens only after successful registry preparation. Repeat with an incorrect frame contract or missing mother phase. Restore exact files/hashes before normal acceptance. These mutations belong only to the test copy and must not enter the delivery whitelist.

## Full original transaction regression

Natural character creation -> all five opening pages -> A13 natural portal -> A00; mother dialogue; chief A1–A5; exact reward item counts/instances and gold; nine NORTH flags cleared; no duplicate/replayed awards; existing stale-identity and resource rollback fixtures. After A5, HD must remain active: only exact nine -1→0 flags are accepted by the independent art contract, without changing gameplay validation. Unexpected flag changes or any changed floor/kind/index still fail art preparation.

## Acceptance limits

Fail for missing/duplicate characters, broken animation, visible holes, materially wrong doorway/root positions, severe scale issues or regressions in source transaction checks. Minor color fringes and small texture seams are recorded for later polish. All files must still match FROZEN_MANIFEST.json after normal validation; logs/screenshots/import caches stay outside the runtime whitelist.
