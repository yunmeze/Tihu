# Recovery plan — 2026-10-15

## Verified recovery boundary

The original game and reference web project remain available at repository commit `286c2cc3862ba8ab5a5af48e268ac9c9b6cfc9a6`. The preceding local Godot implementation, generated source art, and local checkpoints are not present in the current execution workspace. Their disappearance does not establish permanent deletion or its cause.

Retained implementation records can guide reconstruction, but are not source-code backups. Missing source art cannot be recreated byte-for-byte from screenshots, hashes, or descriptions. Every reconstructed behavior and asset must be checked again.

## Small, verifiable checkpoints

1. **R0 — recovery scaffold:** preserve original material; establish project location, ignore rules, and recovery boundaries. Not playable.
2. **R1 — source-art A13 movement:** original map parsing, rendering, character frame anchoring, path movement, and obstruction/occlusion checks.
3. **R2 — opening quest:** original script-driven dialogue, relevant portals and map conditions. Explicitly identify unsupported instructions rather than silently approximating them.
4. **R3 — inventory and saves:** single instance authority, 42 bag slots, exact item ownership, atomic transactions, validated versioned saves and recoverable failures. Never fabricate the previous natural-play save from remembered numbers.
5. **R4 onward — combat and remade art:** validate small functional slices; analyze original animation phases before generating complete coherent action groups. Review equipment grip, visual transitions, and surface-specific shadows independently.

These are scope boundaries, not completion claims or timing promises. Source findings must be rechecked against actual original files.

## Lessons retained

- Use one authoritative inventory representation; do not maintain a second mutable legacy item list.
- Register all supported maps for inventory/save location validation; do not trust a save to define its own valid map boundaries.
- Preserve original sprite offsets and draw ordering. Do not fix occlusion by globally lifting the protagonist.
- Separate body eligibility from shadow-receiver masks. Floor, platform, and step-top shadows must avoid vertical surfaces and duplicate alpha.
- Generate complete action groups from original poses. Do not splice individual poses, warp limbs, or accept numerical control-point fits instead of visual continuity.
- Missing sprite imports are a failed preflight, not a valid blank screenshot.
- Do not equate Linux tests with Windows validation, or isolated animation previews with integrated combat.

## Publication and durability

The owner authorized immediate Git checkpoints after each small completed stage on 2026-10-15. Commit only related project files and production assets. Exclude temporary/test files and caches. Push to `Legend`, then verify the remote commit and tracked file tree before proceeding. Do not force-push or erase existing history.

An in-workspace checkpoint is not an independent backup. Remote verification is mandatory for each published stage. Until R1 is explicitly validated, this project must not be advertised as runnable.
