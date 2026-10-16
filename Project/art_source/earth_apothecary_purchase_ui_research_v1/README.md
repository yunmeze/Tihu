# Apothecary single-item purchase and original-skin UI research

Source archive only. It preserves the core implementation, original UI byte/coordinate evidence, and isolated UI implementation. It does not connect the main NPC service, healing, pet healing, all occupations, upgraded characters, save data or the full original UI.

## Contract and differences
Only an initial level1 normal warrior with original cloth is supported. Inventory has42 single-instance bag slots, weight capacity25; each purchase is one separately allocated item, never a stack or bundle decomposition. Thirteen exact original records comprise cloth252 plus12 stock items. Input validation and full inventory ownership/weight checks precede slot→weight→gold rejection. prepare stages without mutation; commit revalidates current authority/context and atomically returns new authority and conversation revision. Caller must publish both together and revoke old callbacks; trusted context is not authentication of an untrusted client.

The original EXE deducts gold before GIVE, with no refund check observed in that caller. This research instead rolls back internal failures atomically. That safety improvement is explicit, not an exact emulation of the original failure behavior. No RNG is consumed for this restricted purchase contract. Tests of42 filled slots include an overweight structural fixture, not a naturally reachable capacity25 purchase sequence.

Original-skin reference only:329x147 panel,16 slots,32px cell spacing evidence,67x21 buy button. Global(24,90), diagnostics, tooltips, close/reopen controls and test purse2000 are research presentation choices. Exact original global position/font/full control visibility and event names remain unresolved. Display-only U+E810 indentation substitution leaves source script bytes unchanged. No original EXE is copied or executed.

## Reproduction
Python3 + Pillow:
- `python verify_original_evidence.py --repo /path/to/tihu-legend` checks the existing EXE SHA and retained VA/file-offset byte ranges, original GIF/control/event records,12 icon byte slices and decoded image identity. It does not regenerate disassembly text or infer additional VB semantics.
- `python materialize.py --repo /path/to/tihu-legend --output /new/external/project` verifies pinned repository dependencies and creates an independent research project from the unchanged core/UI scripts and source resources. The13records and A13 source2 JSON are reconstructed byte-exact; existing inventory/profile code is copied from pinned Git sources, not duplicated in this archive.

This archival pass actually ran both CPU commands. No Godot or original EXE was started. Existing historical evidence is summarized with original file SHA in VALIDATION_HISTORY.json:190 core checks,23 UI checks, actual mouse purchase2000→1965 and1→2 instances. Original first UI failure is retained in the summary. Those results belong to the original isolated execution, not a newly executed engine replay. Tests/logs/screenshots/GPU fixtures are external and excluded.

The first materializer attempt preserved correct source data but failed its byte hash because source.json had originally been compact JSON rather than indented JSON. The selected recipe fixes only serialization and a clean second output matched both original data hashes. This did not alter the three frozen candidate GD scripts.

Historical REPORT/README files describe earlier stage timing; this top-level scope and VALIDATION_HISTORY summarize the final boundary. Original absolute evidence paths are provenance. DEPENDENCIES supplies portable repo-relative input pins. Inspect the independent research project only with an approved engine window; do not install it as the main game.
