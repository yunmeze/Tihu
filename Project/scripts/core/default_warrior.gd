extends RefCounted
## Pure, reference-derived normal default profile. No I/O, runtime, or saves.
## The caller owns exactly state.inventory. Derived/VM views are detached read-only.
const Inventory = preload("res://scripts/core/inventory_state.gd")
const PROFILE := "reference-normal-warrior-v1"
const CLOTH_ID := "252" # Core IDs are canonical strings; original record index is 252.
const CLOTH_RECORD_SHA256 := "fac0ac19177946c941c53cc5ada1df4a747739fedfd04da5b519fe6bdc944cdf"
const RANGE_KEYS := ["attack", "tao", "magic", "defense", "magic_defense"]
const PROPERTY_KEYS := ["fast_attack", "fast_cast", "physical_evade", "magic_evade", "accuracy", "freeze", "burn", "poison", "paralysis", "vampire", "reflect", "luck"]
const CACHED_TOTALS := {"hp":25,"mp":5,"attack":[1,3],"tao":[0,1],"magic":[0,1],"defense":[0,3],"magic_defense":[0,1],"accuracy":7,"capacity":25}
const CLOTH_RAW := [9,767,2,3,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2]
const STATE_KEYS := ["profile", "character", "et", "bt", "entry", "inventory", "unknown_native"]
const CHARACTER_KEYS := ["name", "class", "gender", "level", "experience", "gold", "hp", "mp", "skill_points", "attribute_points", "skills", "active_skill", "game_mode", "clear_count", "base"]

## Accept only the audited source record, never guess rules for other templates.
## Unused extraction metadata is not copied or interpreted.
static func adapt_cloth(record: Variant) -> Dictionary:
	if typeof(record) != TYPE_DICTIONARY:
		return _error("invalid_template", "Supply extracted catalogue record 252 explicitly.")
	if not _source_integer(record.get("id"), 252) or typeof(record.get("name")) != TYPE_STRING or record.name != "布衣":
		return _error("unsupported_template", "This adapter supports only the reviewed cloth template 252.")
	if typeof(record.get("rawFields")) != TYPE_ARRAY or record.rawFields.size() != 39:
		return _error("invalid_template", "Cloth requires its 39 original source words.")
	for index in 39:
		if not _source_integer(record.rawFields[index], CLOTH_RAW[index]):
			return _error("template_mismatch", "Cloth source words differ from the audited record.")
	for key in ["type", "icon", "hp", "mp", "weight"]:
		var expected: int = {"type":9,"icon":767,"hp":0,"mp":0,"weight":2}[key]
		if not _source_integer(record.get(key), expected):
			return _error("template_mismatch", "Decoded template fields disagree with source words.")
	for index in RANGE_KEYS.size():
		var key: String = "magicDefense" if index == 4 else RANGE_KEYS[index]
		var pair: Variant = record.get(key)
		if typeof(pair) != TYPE_ARRAY or pair.size() != 2:
			return _error("template_mismatch", "Decoded cloth ranges are missing.")
		for end in 2:
			if not _source_integer(pair[end], CLOTH_RAW[6 + 2 * index + end]):
				return _error("template_mismatch", "Decoded cloth ranges disagree with source words.")
	if not _keys(record.get("requirements"), ["level", "attack", "tao", "magic"]):
		return _error("template_mismatch", "Cloth needs all four explicit zero requirements.")
	for value in record.requirements.values():
		if not _source_integer(value, 0): return _error("template_mismatch", "Cloth requirements differ from the reviewed record.")
	if not _string_array(record.get("compatible_slots_reference"), ["armor"]):
		return _error("template_mismatch", "Only the source-supported named armor slot is admitted.")
	var result := {"ok":true,"catalogue":{CLOTH_ID:{"weight":2,"equipment_slots":["armor"],"consumable":false}},
		"equipment_ranges":{"attack":[0,0],"tao":[0,0],"magic":[0,0],"defense":[0,1],"magic_defense":[0,0]},
		"raw_usage_counter":0}
	_freeze(result)
	return result

## Policy is an explicit caller decision. Profile capacity 25 is NOT inferred to
## mean 25 bag slots or any unverified native weight-location rule.
static func create(id_namespace: Variant, cloth_record: Variant, policy: Variant) -> Dictionary:
	var rules := adapt_cloth(cloth_record)
	if not rules.ok: return rules
	var empty := Inventory.create(id_namespace, rules.catalogue, policy)
	if not empty.ok: return empty
	var acquired := _commit_action(empty.inventory, {"type":"acquire","item_id":CLOTH_ID,
		"properties":{"raw_proficiency":rules.raw_usage_counter,"weight":2},
		"provenance":{"grant":"normal_default_creation","source_record":252,"source_record_sha256":CLOTH_RECORD_SHA256,"raw_proficiency_semantics":"raw36_usage_counter"}}, rules.catalogue, policy)
	if not acquired.ok: return acquired
	var equipped := _commit_action(acquired.inventory, {"type":"equip","instance_id":acquired.instance_id,"equipment_slot":"armor"}, rules.catalogue, policy)
	if not equipped.ok: return equipped
	var base := CACHED_TOTALS.duplicate(true)
	for key in RANGE_KEYS:
		for end in 2: base[key][end] -= rules.equipment_ranges[key][end]
	for key in PROPERTY_KEYS:
		if not base.has(key): base[key] = 0
	var et: Array = []
	var bt: Array = []
	et.resize(30)
	bt.resize(30)
	et.fill(0)
	bt.fill(-1)
	et[0] = 1
	var state := {"profile":PROFILE,
		"character":{"name":"英雄","class":"战士","gender":0,"level":1,"experience":0,"gold":0,
			"hp":25,"mp":5,"skill_points":1,"attribute_points":1,"skills":[],"active_skill":null,
			"game_mode":0,"clear_count":0,"base":base},
		"et":et,"bt":bt,"entry":{"map_id":"A13","cell":[61,39],"direction":4,"opening":{"kind":"opening","phase":"reading","page":0},"unlocked_maps":["A00","A13"]},
		"inventory":equipped.inventory,"unknown_native":{"hero_ap":null,"full_record":null}}
	var views := project(state, cloth_record, policy)
	if not views.ok: return views
	return {"ok":true,"state":state,"catalogue":rules.catalogue,"derived":views.derived,"vm_projection":views.vm_projection,
		"total_weight":views.total_weight,"overweight":views.overweight}

## Recompute views after caller-owned inventory/flag/stat changes. This is not a
## save validator or a progression/combat engine; other templates need a new adapter.
static func project(state: Variant, cloth_record: Variant, policy: Variant) -> Dictionary:
	var rules := adapt_cloth(cloth_record)
	if not rules.ok: return rules
	if not _bounded(state, 0, [0]) or not _keys(state, STATE_KEYS) or typeof(state.profile) != TYPE_STRING or state.profile != PROFILE:
		return _error("invalid_profile_state", "Expected bounded default-profile state with exactly one inventory authority.")
	if not _character_valid(state.character) or not _entry_valid(state.entry):
		return _error("invalid_profile_state", "Character or entry fields are invalid or outside this profile boundary.")
	if not _keys(state.unknown_native, ["hero_ap", "full_record"]) or typeof(state.unknown_native.hero_ap) != TYPE_NIL or typeof(state.unknown_native.full_record) != TYPE_NIL:
		return _error("unknown_native_field", "Unreconstructed native fields must remain explicitly unknown.")
	for bank in ["et", "bt"]:
		if typeof(state[bank]) != TYPE_ARRAY or state[bank].size() != 30:
			return _error("invalid_flags", "ET and BT must contain exactly 30 native integers.")
		for value in state[bank]:
			if not _integer(value, -32768, 32767): return _error("invalid_flags", "Flags must be signed 16-bit native integers.")
	var checked := Inventory.validate(state.inventory, rules.catalogue, policy)
	if not checked.ok: return checked
	var derived: Dictionary = state.character.base.duplicate(true)
	derived.set_bonus = 0 # The only admitted equipment is cloth, never a set.
	for instance_id in checked.inventory.equipment_slots.values():
		if instance_id == null: continue
		for key in RANGE_KEYS:
			for end in 2:
				derived[key][end] += rules.equipment_ranges[key][end]
				if derived[key][end] > 32767: return _error("stat_overflow", "Derived range exceeds signed 16-bit nonnegative bounds.")
	var projection := {"et":_plain_array(state.et),"bt":_plain_array(state.bt),"level":state.character.level,
		"clear_count":state.character.clear_count,"game_mode":state.character.game_mode}
	_freeze(derived)
	_freeze(projection)
	return {"ok":true,"derived":derived,"vm_projection":projection,"total_weight":checked.total_weight,"overweight":checked.overweight}

static func _commit_action(inventory: Dictionary, action: Dictionary, catalogue: Dictionary, policy: Variant) -> Dictionary:
	var staged := Inventory.stage(inventory, action, catalogue, policy, inventory.revision)
	if not staged.ok: return staged
	return Inventory.commit(inventory, staged.transaction, catalogue, policy)

static func _character_valid(character: Variant) -> bool:
	if not _keys(character, CHARACTER_KEYS): return false
	if typeof(character.name) != TYPE_STRING or character.name.is_empty() or character.name.length() > 64: return false
	if typeof(character["class"]) != TYPE_STRING or character["class"] != "战士" or not _integer(character.gender, 0, 0): return false
	if not _integer(character.level, 1, 130) or not _integer(character.game_mode, 0, 0) or not _integer(character.clear_count, 0, 32767): return false
	for key in ["experience", "gold", "skill_points", "attribute_points"]:
		if not _integer(character[key], 0, Inventory.MAX_INTEGER): return false
	# Skill acquisition is intentionally outside this single initial profile.
	if typeof(character.skills) != TYPE_ARRAY or not character.skills.is_empty() or typeof(character.active_skill) != TYPE_NIL: return false
	if not _keys(character.base, ["hp", "mp", "capacity"] + RANGE_KEYS + PROPERTY_KEYS): return false
	for key in ["hp", "mp", "capacity"] + PROPERTY_KEYS:
		if not _integer(character.base[key], 0, 32767): return false
	for key in ["hp", "mp"]:
		if not _integer(character[key], 0, character.base[key]): return false
	for key in RANGE_KEYS:
		var pair: Variant = character.base[key]
		if typeof(pair) != TYPE_ARRAY or pair.size() != 2 or not _integer(pair[0], 0, 32767) or not _integer(pair[1], pair[0], 32767): return false
	return true

static func _entry_valid(entry: Variant) -> bool:
	if not _keys(entry, ["map_id", "cell", "direction", "opening", "unlocked_maps"]): return false
	# A creation candidate requests this exact destination. Map-load validation
	# and STOP/world publication remain the existing runtime adapter's job.
	if typeof(entry.map_id) != TYPE_STRING or entry.map_id != "A13" or not _integer(entry.direction, 4, 4): return false
	if typeof(entry.cell) != TYPE_ARRAY or entry.cell.size() != 2 or not _integer(entry.cell[0], 61, 61) or not _integer(entry.cell[1], 39, 39): return false
	if not _keys(entry.opening, ["kind", "phase", "page"]): return false
	return typeof(entry.opening.kind) == TYPE_STRING and entry.opening.kind == "opening" and typeof(entry.opening.phase) == TYPE_STRING and entry.opening.phase == "reading" and _integer(entry.opening.page, 0, 0) and _string_array(entry.unlocked_maps, ["A00","A13"])

static func _string_array(value: Variant, expected: Array) -> bool:
	if typeof(value) != TYPE_ARRAY or value.size() != expected.size(): return false
	for index in expected.size():
		if typeof(value[index]) != TYPE_STRING or value[index] != expected[index]: return false
	return true

static func _source_integer(value: Variant, expected: int) -> bool:
	return typeof(value) in [TYPE_INT, TYPE_FLOAT] and is_finite(float(value)) and value == expected

static func _integer(value: Variant, low: int, high: int) -> bool:
	return typeof(value) == TYPE_INT and value >= low and value <= high

static func _keys(value: Variant, keys: Array) -> bool:
	return typeof(value) == TYPE_DICTIONARY and value.size() == keys.size() and value.has_all(keys)

static func _plain_array(source: Array) -> Array:
	var result: Array = []
	for value in source: result.append(value)
	return result

static func _bounded(value: Variant, depth: int, count: Array) -> bool:
	count[0] += 1
	if depth > 24 or count[0] > 32768: return false
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT: return true
		TYPE_FLOAT: return is_finite(value)
		TYPE_STRING, TYPE_STRING_NAME: return value.length() <= 65536
		TYPE_ARRAY:
			for child in value:
				if not _bounded(child, depth + 1, count): return false
			return true
		TYPE_DICTIONARY:
			for key in value:
				if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME] or not _bounded(key, depth + 1, count) or not _bounded(value[key], depth + 1, count): return false
			return true
	return false

static func _freeze(value: Variant) -> void:
	if typeof(value) == TYPE_DICTIONARY:
		for child in value.values(): _freeze(child)
		value.make_read_only()
	elif typeof(value) == TYPE_ARRAY:
		for child in value: _freeze(child)
		value.make_read_only()

static func _error(code: String, detail: String) -> Dictionary:
	return {"ok":false,"error":code,"detail":detail}
