# Pure normal default warrior profile

This checkpoint adds `scripts/core/default_warrior.gd`. It constructs **one reference-derived normal default warrior**, before map-load effects or world publication. It is preparation for a later real game entry. It does not change the default scene, implement UI/character selection, run combat, save a complete character, migrate a historical save, or recreate a lost level-four character. The audited inventory core/codec/store remain unchanged.

## Authority and API

All methods are pure and accept values explicitly; there are no file reads, filesystem writes, global random draws, or implicit namespace generation.

- `adapt_cloth(record)` accepts the extracted `Project/data/items/catalogue.json` record at original index **252**. It checks the identity, all 39 source words, decoded ranges/scalars, four requirements, and named armor slot against the reviewed cloth record. It returns a recursively read-only core catalogue containing only string ID `"252"`, plus the reviewed equipment ranges and usage counter. Other templates fail rather than receiving guessed consumption/equipment rules. Unused extraction metadata is not copied or interpreted.
- `create(namespace, cloth_record, policy)` constructs an empty core inventory, acquires one cloth instance, and equips that exact ID in `armor`, using the core's normal stage/commit boundary for both operations. Any failure returns no partial game state. Success returns `state`, read-only `catalogue`, read-only `derived`, read-only `vm_projection`, `total_weight`, and `overweight`.
- `project(state, cloth_record, policy)` validates the bounded supported state and recomputes derived statistics and the VM query snapshot from the current authority. It does not replace or mutate the supplied state. This narrow projection supports the reviewed warrior/normal profile and cloth subset; adding skills, other classes/modes/items, stat-affix rules, or complete progression is a separate stage.

`state.inventory` is the **only live inventory authority**. There is no player inventory mirror, template/name quantity list, independent equipment-ID dictionary, belt bag, or storage bag. Gold is a scalar at `state.character.gold`, never an item instance. Derived totals are not stored in authoritative state. Recompute them after an inventory/base-stat change; an earlier read-only view is deliberately just a snapshot.

The caller supplies an explicit policy accepted by `inventory_state.gd`, including `max_weight`, `equipment_slots`, and `weight_locations`; `armor` must be present. There is **no default inferred native weight policy**. The source capacity statistic is 25, while the core has its separately audited fixed 42 bag positions. The reference portrait game later overrides carrying with 50 warrior stack slots and disables weight constraints; that adaptation is not imported. Initialization honors the supplied ingress policy and can fail if it cannot acquire/equip the required cloth. Subsequent projection accepts structurally valid overweight inventories so recovery remains possible.

The successful initial inventory has one instance `<namespace>:1`, `next_serial=2`, `revision=2`, 42 empty nullable bag positions, armor containing that instance ID, all other policy equipment slots null, and no recovery IDs. Revision 2 records the two core initialization transactions; it is not a character level or persistence generation. Namespace uniqueness remains the caller's responsibility.

## Exact source-backed defaults

The module names snake_case fields explicitly. Its compact state is not the original native record layout.

| State/value | Evidence |
|---|---|
| name `英雄`, class `战士`, gender 0, normal mode 0 | `参考项目/src/character.js:22–24` default arguments and normal creation assignment |
| level 1, experience 0, gold 0 | `character.js:12`, retained by the actual `createNewCharacter` path; fresh function execution checked |
| current HP 25, MP 5 | `character.js:18,24`; checked-in `initial-character-reference.json`; source comments/native static evidence corroborate HP/MP writes in creation branch starting `0x593085` |
| skills `[]`, active skill null, skill points 1, attribute points 1, clear count 0 | `character.js:24` explicitly replaces legacy fixture values |
| one equipped cloth 252, empty bag, no weapon/potions | `character.js:24`; source catalogue record252 identifies 布衣; `initial-character-reference.json.normal_creation_reference` |
| ET0=1, ET1–29=0 | Actual `createGame`, `参考项目/src/game.js:67–69`, sets ET0=1; `npc-fields.js:21–22` defines missing ET query values as 0 |
| BT0–29=-1 | `npc-fields.js:21–22` explicitly defines absent BT query values as -1; matches the current pure VM bank contract |
| entry request A13, cell `[61,39]` | `opening.js:2` parses source `#To A13 61 39`; original `Config.dat` opening record independently redecoded at offset96, total850 bytes |
| entry direction 4 | `参考项目/src/combat.js:42`, reference map-entry initialization; not a reconstructed native record-offset claim |
| opening `{kind:"opening",phase:"reading",page:0}` | `game.js:69` normal creation candidate |
| unlocked maps `["A00","A13"]` | A00 retained from `character.js:12`, then `game.js:68` adds the opening destination |
| `unknown_native.hero_ap=null`, `full_record=null` | Explicit unknowns in `initial-character-reference.json`; no native full-save claim |

`createNewCharacter` internally calls a legacy fixture helper. The **normal path overwrites** the helper's wood sword, five HP potions, three MP potions, learned basic sword skill, MP15, and cached base. The completed normal `createGame` also replaces the helper's intermediate ET0=3 with ET0=1. Those legacy/intermediate values are not starter rewards or the game-entry state.

The entry fields are a pending creation destination, not proof that map resources or the destination have been prepared. A13's original load script produces STOP when ET0=1; this factory neither executes nor bakes that side effect into character attributes. The existing map-load adapter must validate and atomically publish actual world/flag/control changes later.

## Base and derived statistics

The warrior reference row contains **cloth-inclusive cached totals**:

| Statistic | Unequipped base | With initial cloth |
|---|---:|---:|
| HP / MP maximum | 25 / 5 | 25 / 5 |
| attack | 1–3 | 1–3 |
| tao | 0–1 | 0–1 |
| magic | 0–1 | 0–1 |
| defense | **0–2** | **0–3** |
| magic defense | 0–1 | 0–1 |
| accuracy / capacity statistic | 7 / 25 | 7 / 25 |

`character.js:25–26` subtracts cloth's five range pairs when creating base statistics. `native-stats.js:26–36` adds equipped instance ranges/properties back. The factory follows those two separate steps; it never uses cached defense 0–3 as an unequipped base and then adds cloth again.

The supported auxiliary properties (`fast_attack`, `fast_cast`, physical/magic evade, freeze, burn, poison, paralysis, vampire, reflect, luck) default to 0 as in `native-stats.js:28`; cloth contributes zero to every one. `set_bonus=0` is a derived result for this cloth-only subset, not an implementation of arbitrary equipment sets. Base and derived numeric values are bounded nonnegative native integers; derived range overflow is rejected.

The existing core's nullable `raw_proficiency` property is seeded from the explicitly supplied cloth **raw word36=0**, with provenance stating `raw36_usage_counter`. This is preserved raw item usage data, **not heroAP, weapon proficiency skill, or damage bonus**. Instance weight is explicitly 2 from raw word38. Future unknown raw values remain a separate unresolved boundary; no combat interpretation is inferred.

## Why cloth is explicitly nonconsumable

The adapter's only catalogue entry is:

```json
{"252":{"weight":2,"equipment_slots":["armor"],"consumable":false}}
```

This `false` is reviewed specifically for 布衣, not a fallback for unknown templates. `character.js:2,31–35` maps type9 to named armor equipment and checks raw31–34 requirements (all four zero on cloth). `consumables.js:8–17` admits named special consumables, type5 teleport items, type6 packages, or type3/4 restores. Cloth/type9 matches none. `special-consumables.js:6–8` and `special-box-rules.js:2` enumerate special names and do not include 布衣.

Source record252 has nonzero raw words only at 0=9, 1=767, 2=2, 3=3, 13=1, 38=2. The 39-word fingerprint is checked before producing rules. Its original disk record is offset24204, length92, SHA-256 `fac0ac19177946c941c53cc5ada1df4a747739fedfd04da5b519fe6bdc944cdf`. Native numeric equipment-slot IDs and complete instance/save layouts remain unresolved. Named armor is the explicit reference-supported contract.

## Read-only VM boundary

The query snapshot contains exactly `et`, `bt`, `level`, `clear_count`, and `game_mode`, matching the currently supported `dialogue_vm.gd` queries. Its dictionary and both arrays are read-only and detached. No inventory, character bag, gold balance, or mutable player object is passed into the VM. Unsupported future money/stat/item commands are not silently implemented by this factory.

The VM can return a detached candidate with changed flags. That is **not** automatic authorization to replace authoritative game state: the later adapter must validate all candidate events and publish allowed state/world changes atomically. A VM candidate cannot grant inventory items through this projection.

## Verification and provenance

Fresh Linux Godot4.6.3 tests passed **2,186 assertions** after the discriminator/type-boundary correction. They cover exact initialization/grant conservation; all 42 bag positions and 60 flags; one-instance equip/unequip/re-equip without duplicate defense; lowered-policy overweight projection; read-only/detached views; VM flag candidate isolation; namespace independence; no implicit old-state import; finite/type/word-fingerprint rejection; cyclic/malformed state rejection without mutation; derived overflow; the existing inventory-only codec boundary; and a root/character/entry/nested-discriminator/array-element/template wrong-type matrix. Every rejected value returns a structured result without Godot script errors.

The ignored harness also compares against the checked-in initial reference JSON and a fresh oracle made by directly executing unchanged reference `createNewCharacter`, `nativeAttributes`, `openingDestination`, and `scriptValue` functions. The two normal `createGame` ET/unlocked-map assignments were replayed explicitly; no browser renderer or save operation was run. The original executable was never executed.

Source fingerprints checked in this stage:

- `Project/data/items/initial-character-reference.json`: `e56e0db6442635c3a7311fd41a5a4f9a441971024041282d715b0b5ac4aa0cb6`
- `Project/data/items/catalogue.json`: `284d0946ce9c9dda164472397c42fdd5207a0723abd2f9afac702de5ab8adf57`
- `参考项目/src/character.js`: `76a51e6e4720dd0e8df084ba14dfb6b947478702ae4c65a2d6998ea34aec83e7`
- `参考项目/src/native-stats.js`: `cdf637abc9bbb0772c748dd4261f25eb6817cc44c3580a0d0abbf3c79de94557`
- `参考项目/src/game.js`: `04c7c32827e205f39dba7c0091ba96ebcd14e19f4ed841a8c347bdd2e9788577`
- `参考项目/src/opening.js`: `bce712dc7f3f82aa9f77bf8cb2570630eb51347997a8bec73a47cadaacd40d86`
- `参考项目/src/npc-fields.js`: `879470b1e6141222434b9f7fbcbef0a671b1b9207dcb1814938fefda9c51d65d`
- Original `Config.dat`: `53adb0ec6983a0a3cb15fe544f4f138dcdcbd6cae707322910727a6805f9c54d`; independently decoded opening text SHA-256 `11e2e7b4a02001b25a2b145dcd441c1bb8c873e1bf0fc94b1717aa4ae79a7c89`, identical to reference story data.

This stage deliberately does not instantiate the reference's belt/storage/dimension-box collections, quest reset banks, pets, ground items, appearance menu, or full native fields. Those systems require their own authority contracts. It neither imports the legacy helper's inventory nor invents missing native-save values.
