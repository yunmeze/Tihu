# Instance inventory core checkpoint

`Project/scripts/core/inventory_state.gd` is a pure Godot 4.6 inventory module. It is **not connected to the R1 preview**, a dialogue VM, combat, save files, or a player initialization path. It reconstructs a bounded part of the recorded single-authority design; it does not recover the missing implementation byte-for-byte.

## Ownership and authority

A future caller keeps the only authoritative snapshot at `state.inventory`. The module has no mutable singleton, secondary bag, item-name list, quantity mirror, or file I/O. Coins belong in a separate scalar outside this inventory; there is no currency action here.

An inventory has exactly these fields:

- `namespace`: 1–64 ASCII letters, digits, `_`, `-`, or `.`.
- `next_serial`: positive integer; the next ID is `namespace:next_serial`.
- `revision`: nonnegative integer; each successfully staged action has base revision + 1.
- `instances`: instance-ID → `{item_id, properties, provenance}`.
- `bag_slots`: exactly 42 entries; each is null or one instance ID. Holes remain holes.
- `equipment_slots`: the exact slot names supplied by policy, each null or an instance ID.
- `recovery_ids`: distinct instance IDs reserved for an explicitly prepared migration/recovery snapshot.

Every live instance occurs in exactly one bag, equipment, or recovery location. Duplicate, dangling, foreign-namespace, malformed, incompatible equipped, and unlocated references are rejected. IDs use canonical positive decimal serials, without leading zeros, signs, whitespace, or suffixes; every live serial is less than `next_serial`. Allocation never searches for or reuses a freed ID.

This checkpoint has no ground structure or action. A future explicit ground adapter must extend validation and conservation together. An unknown field, including a ground collection or legacy item list, fails validation. Recovery contents can be validated or removed by exact ID; ordinary acquire, move, equip, unequip, and consume actions cannot place or operate on recovery items. There is no migration algorithm yet.

## Explicit catalogue and weight policy

The caller supplies a dictionary keyed by stable item-ID strings. Each template has exactly:

```gdscript
{"weight": 2, "equipment_slots": ["hand"], "consumable": false}
```

This is a synthetic schema example, not an original item definition. Weight must be a bounded nonnegative integer, compatible slots must be unique and declared by policy, and `consumable` must be an explicit boolean. A source record with unknown consumability or compatibility must not silently become an invented gameplay template. A later adapter should use an explicitly reviewed subset or establish those semantics first. Display names are not instance IDs.

Policy has exactly:

```gdscript
{
    "max_weight": 100,
    "equipment_slots": ["hand", "body"],
    "weight_locations": ["bag", "equipment"]
}
```

Again these values and slot labels are synthetic examples. The module supplies no original maximum-weight formula, proficiency formula, equipment taxonomy, consumption effect, or starter inventory. `weight_locations` must be a nonempty unique subset of `bag`, `equipment`, and `recovery`. An empty equipment-slot list is allowed. Bag capacity is always 42, independent of weight. The caller chooses explicitly whether equipment or migration recovery contributes to its limit.

Instance `properties` currently supports only:

- `raw_proficiency`: null when unknown; an explicitly supplied bounded nonnegative integer is retained. It is never derived from weapon type or treated as hero AP, damage, or a combat proficiency formula.
- `weight`: null means use the explicitly supplied template weight; an explicit bounded nonnegative integer, including zero, overrides it for that instance.

Omitted properties normalize to these two nulls. Unknown properties fail instead of being discarded. Original `Item0.lpRes` template weight is not proof that every mutable runtime instance always has that weight. Source template extraction remains a separate stage; this core neither reads those files nor invents mappings.

Weight is recomputed from the chosen locations and effective instance weights, with an overflow check before every addition. All operations validate both input and candidate. This includes acquire ingress, equip swaps, and unequip: moving a displaced heavier item into a weight-counted bag can fail even when total instance count is unchanged. A bounded overweight snapshot is structurally valid: validation returns `overweight: true` and its `total_weight`. This permits capacity reductions or changes in counted locations without trapping the player. Acquire must always leave the candidate within the supplied limit, including zero-weight acquisition into an already-overweight inventory. When the base is within the limit, no action may make it overweight. When the base is already overweight, non-acquire actions may maintain or reduce counted weight, even if the result remains overweight; an increase fails. This permits exact-ID consume/remove and weight-neutral moves or appropriate equip/unequip operations to help recover. This is the explicit core policy, not a claim of an original-game formula. A sum beyond the exact integer bound remains a structural error rather than a usable overweight state.

## Numeric and metadata rules

Integer fields accept native integers and **finite, exactly integral** JSON floats in the inclusive range `0..9007199254740991` (`2^53 - 1`). `next_serial` starts at 1. Bag indexes additionally require `0..41`. Accepted integer floats normalize to native integers, including negative zero to zero. Booleans, numeric strings, fractions, NaN, infinities, and values beyond the bound are rejected. Bounds are checked again after float-to-int conversion.

`next_serial == MAX_INTEGER` rejects acquire before allocation because its successor would be out of range. `revision == MAX_INTEGER` rejects all staging before any action. A serial or revision of `MAX_INTEGER - 1` may advance once to `MAX_INTEGER`. Successful removal never decrements a serial. Failed staging exposes no candidate and leaves the caller's serial and revision unchanged.

`provenance` is an explicitly supplied JSON-compatible dictionary, with no required game-specific fields. String and StringName dictionary keys are accepted for native GDScript ergonomics and normalized to strings in provenance/snapshot outputs. Schema field keys also accept StringName; item IDs, namespace, slot-name lists, and references require strings. Provenance allows null, booleans, strings, arrays, dictionaries, bounded integers, and finite floats whose absolute value is at most `MAX_INTEGER`. Fractional provenance numbers are annotations, not integer gameplay fields. Objects, Resources, Callables, other engine values, invalid dictionary keys, and nonfinite values fail. A per-provenance 16-level depth limit and 4,096-node traversal budget bound cyclic or expanded shared-container input before copying/freezing.

## Small API

All calls are static. Inputs are validated without mutation. Native typed Arrays and Dictionaries are accepted when their values meet the schema; output snapshot containers are rebuilt as generic containers, so a full `Array[String]` bag can safely gain null vacancies after consume, remove, or equip. Catalogue/policy list copies are also generic. Success has `ok: true`; failure has only `ok: false`, `error`, and a human-readable `detail`. Branch on the error code rather than the wording.

- `create(namespace, catalogue, policy)`: returns an empty validated `inventory`, `total_weight`, and `overweight: false`. It supplies no starter items, equipment, coins, or skills.
- `validate(inventory, catalogue, policy)`: returns a detached normalized `inventory`, computed `total_weight`, and `overweight` flag. Bounded overweight is a valid condition, not a structural failure.
- `stage(inventory, action, catalogue, policy, expected_revision)`: validates the base and expected revision, applies one action to a detached copy, validates the result, and returns a recursively read-only `transaction` containing the base, candidate, action, context, expected revision, and affected `instance_id`.
- `commit(current_inventory, transaction, catalogue, policy)`: replays the action against the **current authoritative** inventory, verifies base/context/candidate, then returns a detached `inventory` and affected `instance_id`.
- `rollback(current_inventory, transaction, catalogue, policy)`: validates the same guard and returns a detached unchanged base. This is cancellation of an **uncommitted** transaction, not undo of a published commit. Simply discarding a staged transaction is also sufficient.

The caller serializes publication and assigns `state.inventory = result.inventory` only after successful commit. This is a pure snapshot API, not a lock or durable database; intentionally passing an old local snapshot cannot establish that it is the real current authority. A revision guard plus whole-base comparison catches stale or changed current snapshots, even if someone altered contents without incrementing revision. Catalogue or policy drift also rejects the transaction. A forged candidate is never adopted; commit returns freshly replayed data. The module does not modify a containing `state` object.

A failed action cannot partially publish, consume a serial, remove an item, or change input bytes. Staging two actions from one base is permitted; after publishing one result, committing or rolling back the other against the new current snapshot fails. Retrying a committed transaction against the new snapshot fails too. Returned committed/rolled-back snapshots are detached from all read-only transaction containers.

## Supported actions

Actions reject unknown fields, unknown operations, malformed types, and nonexistent exact IDs.

- `{"type":"acquire", "item_id":..., "provenance":..., "properties":..., "bag_index":...}` creates exactly one instance. `properties` and `bag_index` are optional. An omitted index selects the first empty bag slot; a requested occupied slot fails. No quantity/stack or recovery spill is created.
- `{"type":"move", "instance_id":..., "bag_index":...}` moves a bag instance, swapping exact IDs if the destination is occupied. Moving to the same position returns `no_change` without incrementing revision.
- `{"type":"equip", "instance_id":..., "equipment_slot":...}` requires the exact instance in the bag and declared compatibility. An occupied equipment slot swaps its previous ID into the source item's vacated bag slot, including when the bag is full. No other slot is searched or displaced.
- `{"type":"unequip", "instance_id":..., "bag_index":...}` requires that exact equipped instance. The index is optional and must be empty; a full bag fails. Unequip does not implicitly equip an occupied bag item.
- `{"type":"consume", "instance_id":...}` removes exactly one bag instance explicitly marked consumable by the supplied catalogue. It does not apply healing, skill, quest, or combat effects.
- `{"type":"remove", "instance_id":...}` removes that exact instance and its single current bag/equipment/recovery reference. This is structural removal, not a ground drop or a quest/trade interpretation.

Common failure codes: `invalid_inventory`, `invalid_namespace`, `invalid_counter`, `invalid_instance_id`, `invalid_instance`, `unknown_item`, `invalid_properties`, `invalid_provenance`, `missing_instance`, `duplicate_location`, `unlocated_instance`, `incompatible_equipment`, `weight_overflow`, `weight_limit`, `invalid_policy`, `invalid_catalogue`, `invalid_action`, `unsupported_action`, `invalid_revision`, `revision_conflict`, `revision_exhausted`, `serial_exhausted`, `instance_collision`, `base_conflict`, `context_conflict`, `invalid_transaction`, `invalid_bag_index`, `wrong_location`, `no_change`, `unknown_equipment_slot`, `occupied_bag_slot`, `bag_full`, and `not_consumable`.

## Fresh verification and limits

On 2026-10-15, Linux Godot **4.6.3** passed the standalone parser check and **1,664 fresh assertions** in the ignored local `Project/tests/test_inventory_state.gd` harness. Synthetic fixtures exercise:

- Exact conservation, independent same-template identities, and preservation of provenance/proficiency/weight overrides.
- Full-bag ingress/unequip rejection and occupied equipment swaps into the vacated bag slot.
- Bag/equipment/recovery weight policy, instance override zero, post-swap rejection, and safe weight overflow.
- Lowered capacity and changed weight locations, consumption/removal that reduces but does not immediately resolve overweight, permitted equal-weight movement/equipment, rejection of increased-weight swaps, and rejection of zero-weight ingress while overweight.
- Failed transactions leaving state and action serialization byte-identical.
- Detached/read-only staging, replayed commits, guarded cancellation, stale/sibling/repeated commits, base/context drift, and malformed/forged transaction fields.
- JSON normalization, finite-value and type rejection, canonical IDs, boundary counters, provenance cycles, shared-container traversal budget, native typed-container ingress/normalization, and a deterministic 100-action mixed sequence.

The initial headless launch could not write its default home-data directories; rerunning with HOME/XDG directories under ignored `Project/.validation` succeeded. The fixture definitions are synthetic; passing them does not establish original combat, original consumption, original maximum-weight rules, all save migrations, natural-play restoration, Windows execution, or integration into the running preview. Local tests and caches remain ignored; only the production module and this contract document belong to this checkpoint.
