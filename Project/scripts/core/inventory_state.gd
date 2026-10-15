extends RefCounted
## Pure inventory snapshots. No runtime, save, template, currency, or UI authority.
## The caller replaces state.inventory only with a successful commit's inventory.

const BAG_SIZE := 42
# Integers must survive a JSON number round trip without precision loss.
const MAX_INTEGER := 9007199254740991
const MAX_JSON_DEPTH := 16
const MAX_JSON_NODES := 4096
const INVENTORY_FIELDS := ["namespace", "next_serial", "revision", "instances", "bag_slots", "equipment_slots", "recovery_ids"]
const TRANSACTION_FIELDS := ["base_inventory", "inventory", "action", "catalogue", "policy", "expected_revision", "instance_id"]

static func create(id_namespace: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var context := _context(catalogue, policy)
	if not context.ok:
		return context
	if not _token(id_namespace):
		return _error("invalid_namespace", "Use 1–64 ASCII letters, digits, underscores, hyphens, or periods.")
	var bag: Array = []
	bag.resize(BAG_SIZE)
	var equipment := {}
	for slot in context.policy.equipment_slots:
		equipment[slot] = null
	return validate({"namespace": id_namespace, "next_serial": 1, "revision": 0,
		"instances": {}, "bag_slots": bag, "equipment_slots": equipment, "recovery_ids": []}, catalogue, policy)

## Normalizes exact integral JSON floats in integer fields; never changes input.
## A successful result owns a detached inventory snapshot and computed total_weight.
static func validate(inventory: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var context := _context(catalogue, policy)
	if not context.ok:
		return context
	return _validate_inventory(inventory, context.catalogue, context.policy)

## Staging does not publish changes. All containers in the transaction are read-only.
static func stage(inventory: Variant, action: Variant, catalogue: Variant, policy: Variant, expected_revision: Variant) -> Dictionary:
	var context := _context(catalogue, policy)
	if not context.ok:
		return context
	var checked := _validate_inventory(inventory, context.catalogue, context.policy)
	if not checked.ok:
		return checked
	var expected: Variant = _integer(expected_revision)
	if expected == null:
		return _error("invalid_revision", "Expected revision must be a bounded nonnegative integer.")
	if expected != checked.inventory.revision:
		return _error("revision_conflict", "The current revision differs from the expected revision.")
	if expected == MAX_INTEGER:
		return _error("revision_exhausted", "Revision cannot be incremented safely.")
	var candidate: Dictionary = checked.inventory.duplicate(true)
	var applied := _apply(candidate, action, context.catalogue)
	if not applied.ok:
		return applied
	candidate.revision += 1
	var final_check := _validate_inventory(candidate, context.catalogue, context.policy)
	if not final_check.ok:
		return final_check
	# Capacity changes must not trap an otherwise valid inventory: permit
	# non-increasing non-ingress actions while already overweight.
	if final_check.overweight and (action.type == "acquire" or not checked.overweight or final_check.total_weight > checked.total_weight):
		return _error("weight_limit", "Ingress must fit the limit; an already-overweight inventory may only maintain or reduce counted weight.")
	var transaction := {"base_inventory": checked.inventory, "inventory": final_check.inventory,
		"action": action.duplicate(true), "catalogue": context.catalogue, "policy": context.policy,
		"expected_revision": expected, "instance_id": applied.instance_id}
	_freeze(transaction)
	return {"ok": true, "transaction": transaction}

## Replays the staged action, rather than trusting a caller-supplied candidate.
## The caller must pass its CURRENT state.inventory, then assign the result once.
static func commit(inventory: Variant, transaction: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var checked := _check_transaction(inventory, transaction, catalogue, policy)
	if not checked.ok:
		return checked
	return {"ok": true, "inventory": checked.transaction.inventory.duplicate(true),
		"instance_id": checked.transaction.instance_id}

## Discarding an uncommitted transaction is sufficient. This guarded helper returns
## a detached unchanged snapshot; it cannot restore an old base over a newer state.
static func rollback(inventory: Variant, transaction: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var checked := _check_transaction(inventory, transaction, catalogue, policy)
	if not checked.ok:
		return checked
	return {"ok": true, "inventory": checked.transaction.base_inventory.duplicate(true)}

static func _check_transaction(inventory: Variant, transaction: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	if not _shape(transaction, TRANSACTION_FIELDS):
		return _error("invalid_transaction", "Transaction fields are invalid.")
	# Replaying also validates every supplied action and current-state value.
	var replay := stage(inventory, transaction.action, catalogue, policy, transaction.expected_revision)
	if not replay.ok:
		return replay
	var fresh: Dictionary = replay.transaction
	# Validate untrusted transaction containers before deep comparison (including
	# provenance cycles). Never adopt any of these caller-supplied snapshots.
	var saved_context := _context(transaction.catalogue, transaction.policy)
	if not saved_context.ok:
		return _error("invalid_transaction", "The staged context is malformed.")
	if not _validate_inventory(transaction.base_inventory, fresh.catalogue, fresh.policy).ok or not _validate_inventory(transaction.inventory, fresh.catalogue, fresh.policy).ok:
		return _error("invalid_transaction", "The staged snapshots are malformed.")
	if typeof(transaction.instance_id) != TYPE_STRING:
		return _error("invalid_transaction", "The staged instance ID is malformed.")
	if transaction.base_inventory != fresh.base_inventory:
		return _error("base_conflict", "The current inventory differs from the staged base.")
	if transaction.catalogue != fresh.catalogue or transaction.policy != fresh.policy:
		return _error("context_conflict", "Catalogue or policy changed after staging.")
	if transaction.inventory != fresh.inventory or transaction.instance_id != fresh.instance_id:
		return _error("invalid_transaction", "The candidate does not match the replayed action.")
	return replay

static func _context(catalogue: Variant, policy: Variant) -> Dictionary:
	if not _shape(policy, ["max_weight", "equipment_slots", "weight_locations"]):
		return _error("invalid_policy", "Policy requires max_weight, equipment_slots, and weight_locations.")
	var max_weight: Variant = _integer(policy.max_weight)
	if max_weight == null or not _string_set(policy.equipment_slots) or not _string_set(policy.weight_locations):
		return _error("invalid_policy", "Weight must be bounded and slot/location lists must contain unique strings.")
	for location in policy.weight_locations:
		if location not in ["bag", "equipment", "recovery"]:
			return _error("invalid_policy", "Unsupported weight location: " + location)
	if policy.weight_locations.is_empty():
		return _error("invalid_policy", "Choose at least one weight location explicitly.")
	if typeof(catalogue) != TYPE_DICTIONARY:
		return _error("invalid_catalogue", "Catalogue must be a dictionary.")
	var normalized := {}
	for item_id in catalogue:
		if not _identifier(item_id):
			return _error("invalid_catalogue", "Catalogue item IDs must be nonempty strings.")
		var entry: Variant = catalogue[item_id]
		if not _shape(entry, ["weight", "equipment_slots", "consumable"]):
			return _error("invalid_catalogue", "Each template requires weight, equipment_slots, and consumable.")
		var weight: Variant = _integer(entry.weight)
		if weight == null or not _string_set(entry.equipment_slots) or typeof(entry.consumable) != TYPE_BOOL:
			return _error("invalid_catalogue", "Invalid weight, equipment slots, or consumable flag for " + item_id)
		for slot in entry.equipment_slots:
			if slot not in policy.equipment_slots:
				return _error("invalid_catalogue", "Template refers to a slot outside the supplied policy.")
		normalized[item_id] = {"weight": weight, "equipment_slots": _plain_array(entry.equipment_slots), "consumable": entry.consumable}
	return {"ok": true, "catalogue": normalized, "policy": {"max_weight": max_weight,
		"equipment_slots": _plain_array(policy.equipment_slots), "weight_locations": _plain_array(policy.weight_locations)}}

static func _validate_inventory(inventory: Variant, catalogue: Dictionary, policy: Dictionary) -> Dictionary:
	if not _shape(inventory, INVENTORY_FIELDS):
		return _error("invalid_inventory", "Inventory fields are invalid or unsupported.")
	if not _token(inventory["namespace"]):
		return _error("invalid_namespace", "Invalid instance namespace.")
	var serial: Variant = _integer(inventory.next_serial, 1)
	var revision: Variant = _integer(inventory.revision)
	if serial == null or revision == null:
		return _error("invalid_counter", "Serial and revision must be bounded integers.")
	if typeof(inventory.instances) != TYPE_DICTIONARY or typeof(inventory.bag_slots) != TYPE_ARRAY or inventory.bag_slots.size() != BAG_SIZE:
		return _error("invalid_inventory", "Instances must be a dictionary and bag_slots must contain exactly 42 entries.")
	if not _shape(inventory.equipment_slots, policy.equipment_slots) or typeof(inventory.recovery_ids) != TYPE_ARRAY:
		return _error("invalid_inventory", "Equipment slots must match policy; recovery_ids must be an array.")
	var instances := {}
	for instance_id in inventory.instances:
		var id_serial: Variant = _id_serial(instance_id, inventory["namespace"])
		if id_serial == null or id_serial >= serial:
			return _error("invalid_instance_id", "Instance IDs must belong to the namespace and precede next_serial.")
		var entry: Variant = inventory.instances[instance_id]
		if not _shape(entry, ["item_id", "properties", "provenance"]):
			return _error("invalid_instance", "Instance fields are invalid.")
		if not _identifier(entry.item_id) or not catalogue.has(entry.item_id):
			return _error("unknown_item", "Instance refers to an unknown template.")
		var properties := _properties(entry.properties)
		if not properties.ok:
			return properties
		if typeof(entry.provenance) != TYPE_DICTIONARY:
			return _error("invalid_provenance", "Provenance must be a JSON dictionary.")
		var provenance := _json(entry.provenance)
		if not provenance.ok:
			return provenance
		instances[instance_id] = {"item_id": entry.item_id, "properties": properties.value, "provenance": provenance.value}
	var seen := {}
	var total_weight := 0
	for kind in ["bag", "equipment", "recovery"]:
		var references: Array = inventory.bag_slots if kind == "bag" else (inventory.equipment_slots.values() if kind == "equipment" else inventory.recovery_ids)
		for instance_id in references:
			if instance_id == null and kind != "recovery":
				continue
			if typeof(instance_id) != TYPE_STRING or not instances.has(instance_id):
				return _error("missing_instance", "A location refers to an unknown or malformed instance ID.")
			if seen.has(instance_id):
				return _error("duplicate_location", "An instance occupies more than one location.")
			seen[instance_id] = true
			if kind in policy.weight_locations:
				var instance_weight: Variant = instances[instance_id].properties.weight
				var weight: int = catalogue[instances[instance_id].item_id].weight if instance_weight == null else instance_weight
				if weight > MAX_INTEGER - total_weight:
					return _error("weight_overflow", "Weight sum exceeds the exact integer bound.")
				total_weight += weight
	if seen.size() != instances.size():
		return _error("unlocated_instance", "Every live instance must occupy one supported location.")
	for slot in inventory.equipment_slots:
		var instance_id: Variant = inventory.equipment_slots[slot]
		if instance_id != null and slot not in catalogue[instances[instance_id].item_id].equipment_slots:
			return _error("incompatible_equipment", "The template does not allow this equipment slot.")
	var equipment := {}
	for slot in policy.equipment_slots:
		equipment[slot] = inventory.equipment_slots[slot]
	return {"ok": true, "total_weight": total_weight, "overweight": total_weight > policy.max_weight, "inventory": {"namespace": inventory["namespace"],
		"next_serial": serial, "revision": revision, "instances": instances,
		"bag_slots": _plain_array(inventory.bag_slots), "equipment_slots": equipment,
		"recovery_ids": _plain_array(inventory.recovery_ids)}}

static func _apply(inventory: Dictionary, action: Variant, catalogue: Dictionary) -> Dictionary:
	if typeof(action) != TYPE_DICTIONARY or not action.has("type") or typeof(action.type) != TYPE_STRING:
		return _error("invalid_action", "Action must name a supported type.")
	if action.type == "acquire":
		return _acquire(inventory, action, catalogue)
	var required := ["type", "instance_id"]
	var optional: Array = []
	match action.type:
		"move": required.append("bag_index")
		"equip": required.append("equipment_slot")
		"unequip": optional.append("bag_index")
		"consume", "remove": pass
		_: return _error("unsupported_action", "Unsupported action: " + action.type)
	if not _shape(action, required, optional) or typeof(action.instance_id) != TYPE_STRING:
		return _error("invalid_action", "Invalid action fields or instance ID.")
	var instance_id: String = action.instance_id
	if not inventory.instances.has(instance_id):
		return _error("missing_instance", "Requested instance does not exist.")
	var bag_index: int = inventory.bag_slots.find(instance_id)
	var equipment_slot: Variant = inventory.equipment_slots.find_key(instance_id)
	match action.type:
		"move":
			var destination: Variant = _integer(action.bag_index, 0, BAG_SIZE - 1)
			if destination == null:
				return _error("invalid_bag_index", "Bag index must be an integer from 0 through 41.")
			if bag_index < 0:
				return _error("wrong_location", "Only bag instances can move between bag slots.")
			if destination == bag_index:
				return _error("no_change", "Instance already occupies that slot.")
			inventory.bag_slots[bag_index] = inventory.bag_slots[destination]
			inventory.bag_slots[destination] = instance_id
		"equip":
			if not _identifier(action.equipment_slot) or not inventory.equipment_slots.has(action.equipment_slot):
				return _error("unknown_equipment_slot", "Requested equipment slot does not exist.")
			if bag_index < 0:
				return _error("wrong_location", "Equipping requires the exact instance in the bag.")
			if action.equipment_slot not in catalogue[inventory.instances[instance_id].item_id].equipment_slots:
				return _error("incompatible_equipment", "The template does not allow this equipment slot.")
			inventory.bag_slots[bag_index] = inventory.equipment_slots[action.equipment_slot]
			inventory.equipment_slots[action.equipment_slot] = instance_id
		"unequip":
			if equipment_slot == null:
				return _error("wrong_location", "Unequipping requires the exact equipped instance.")
			var destination: Variant = _destination(inventory.bag_slots, action)
			if typeof(destination) == TYPE_DICTIONARY:
				return destination
			inventory.bag_slots[destination] = instance_id
			inventory.equipment_slots[equipment_slot] = null
		"consume":
			if bag_index < 0:
				return _error("wrong_location", "Consuming requires the exact instance in the bag.")
			if not catalogue[inventory.instances[instance_id].item_id].consumable:
				return _error("not_consumable", "The supplied catalogue does not mark this template consumable.")
			inventory.bag_slots[bag_index] = null
			inventory.instances.erase(instance_id)
		"remove":
			if bag_index >= 0:
				inventory.bag_slots[bag_index] = null
			elif equipment_slot != null:
				inventory.equipment_slots[equipment_slot] = null
			else:
				inventory.recovery_ids.erase(instance_id)
			inventory.instances.erase(instance_id)
	return {"ok": true, "instance_id": instance_id}

static func _acquire(inventory: Dictionary, action: Dictionary, catalogue: Dictionary) -> Dictionary:
	if not _shape(action, ["type", "item_id", "provenance"], ["properties", "bag_index"]):
		return _error("invalid_action", "Acquire requires item_id and provenance, with optional properties and bag_index.")
	if not _identifier(action.item_id) or not catalogue.has(action.item_id):
		return _error("unknown_item", "Acquire requires a known template ID.")
	var properties := _properties(action.get("properties", {}))
	if not properties.ok:
		return properties
	if typeof(action.provenance) != TYPE_DICTIONARY:
		return _error("invalid_provenance", "Provenance must be a JSON dictionary.")
	var provenance := _json(action.provenance)
	if not provenance.ok:
		return provenance
	var destination: Variant = _destination(inventory.bag_slots, action)
	if typeof(destination) == TYPE_DICTIONARY:
		return destination
	if inventory.next_serial == MAX_INTEGER:
		return _error("serial_exhausted", "Next serial cannot be incremented safely.")
	var instance_id: String = inventory["namespace"] + ":" + str(inventory.next_serial)
	if inventory.instances.has(instance_id):
		return _error("instance_collision", "Allocated ID already exists.")
	inventory.instances[instance_id] = {"item_id": action.item_id, "properties": properties.value, "provenance": provenance.value}
	inventory.bag_slots[destination] = instance_id
	inventory.next_serial += 1
	return {"ok": true, "instance_id": instance_id}

static func _destination(bag: Array, action: Dictionary) -> Variant:
	if action.has("bag_index"):
		var index: Variant = _integer(action.bag_index, 0, BAG_SIZE - 1)
		if index == null:
			return _error("invalid_bag_index", "Bag index must be an integer from 0 through 41.")
		if bag[index] != null:
			return _error("occupied_bag_slot", "Selected bag slot is occupied.")
		return index
	var empty: int = bag.find(null)
	if empty < 0:
		return _error("bag_full", "No empty bag slot is available.")
	return empty

static func _properties(value: Variant) -> Dictionary:
	if not _shape(value, [], ["raw_proficiency", "weight"]):
		return _error("invalid_properties", "Only nullable raw_proficiency and weight are supported in this checkpoint.")
	var proficiency: Variant = value.get("raw_proficiency", null)
	if proficiency != null:
		proficiency = _integer(proficiency)
		if proficiency == null:
			return _error("invalid_properties", "Raw proficiency must be null or a bounded nonnegative integer.")
	var weight: Variant = value.get("weight", null)
	if weight != null:
		weight = _integer(weight)
		if weight == null:
			return _error("invalid_properties", "Instance weight must be null or a bounded nonnegative integer.")
	return {"ok": true, "value": {"raw_proficiency": proficiency, "weight": weight}}

static func _json(value: Variant, depth: int = 0, budget: Array = []) -> Dictionary:
	if budget.is_empty():
		budget = [MAX_JSON_NODES]
	budget[0] -= 1
	if budget[0] < 0:
		return _error("invalid_provenance", "Provenance exceeds the node budget.")
	if depth > MAX_JSON_DEPTH:
		return _error("invalid_provenance", "Provenance is too deeply nested or cyclic.")
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_STRING:
			return {"ok": true, "value": value}
		TYPE_INT:
			if value >= -MAX_INTEGER and value <= MAX_INTEGER:
				return {"ok": true, "value": value}
		TYPE_FLOAT:
			if is_finite(value) and absf(value) <= float(MAX_INTEGER):
				return {"ok": true, "value": value}
		TYPE_ARRAY:
			var array: Array = []
			for element in value:
				var checked := _json(element, depth + 1, budget)
				if not checked.ok:
					return checked
				array.append(checked.value)
			return {"ok": true, "value": array}
		TYPE_DICTIONARY:
			var dictionary := {}
			for key in value:
				if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME]:
					return _error("invalid_provenance", "Provenance dictionary keys must be strings.")
				var checked := _json(value[key], depth + 1, budget)
				if not checked.ok:
					return checked
				dictionary[str(key)] = checked.value
			return {"ok": true, "value": dictionary}
	return _error("invalid_provenance", "Provenance must contain finite, bounded JSON values only.")

static func _integer(value: Variant, minimum: int = 0, maximum: int = MAX_INTEGER) -> Variant:
	if typeof(value) == TYPE_INT:
		return value if value >= minimum and value <= maximum else null
	if typeof(value) == TYPE_FLOAT and is_finite(value) and value >= minimum and value <= maximum and floor(value) == value:
		var normalized := int(value)
		return normalized if normalized >= minimum and normalized <= maximum else null
	return null

static func _id_serial(instance_id: Variant, id_namespace: String) -> Variant:
	if typeof(instance_id) != TYPE_STRING:
		return null
	var prefix := id_namespace + ":"
	if not instance_id.begins_with(prefix):
		return null
	var suffix: String = instance_id.substr(prefix.length())
	if suffix.is_empty() or suffix.length() > 16 or not suffix.is_valid_int():
		return null
	var serial: Variant = _integer(suffix.to_int(), 1)
	return serial if serial != null and str(serial) == suffix else null

static func _token(value: Variant) -> bool:
	if typeof(value) != TYPE_STRING or value.is_empty() or value.length() > 64:
		return false
	for index in value.length():
		var code: int = value.unicode_at(index)
		if not ((code >= 48 and code <= 57) or (code >= 65 and code <= 90) or (code >= 97 and code <= 122) or code in [45, 46, 95]):
			return false
	return true

static func _identifier(value: Variant) -> bool:
	return typeof(value) == TYPE_STRING and not value.is_empty() and value.length() <= 128

static func _string_set(value: Variant) -> bool:
	if typeof(value) != TYPE_ARRAY:
		return false
	var seen := {}
	for entry in value:
		if not _identifier(entry) or seen.has(entry):
			return false
		seen[entry] = true
	return true

static func _shape(value: Variant, required: Array, optional: Array = []) -> bool:
	if typeof(value) != TYPE_DICTIONARY:
		return false
	for key in required:
		if not value.has(key):
			return false
	for key in value:
		if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME] or (key not in required and key not in optional):
			return false
	return true

# Array.duplicate retains typed-array constraints. Rebuild explicitly so a
# validated full Array[String] bag can subsequently contain null vacancies.
static func _plain_array(value: Array) -> Array:
	var output: Array = []
	for element in value:
		output.append(element)
	return output

static func _freeze(value: Variant) -> void:
	if typeof(value) == TYPE_DICTIONARY:
		for child in value.values():
			_freeze(child)
		value.make_read_only()
	elif typeof(value) == TYPE_ARRAY:
		for child in value:
			_freeze(child)
		value.make_read_only()

static func _error(code: String, detail: String) -> Dictionary:
	return {"ok": false, "error": code, "detail": detail}
