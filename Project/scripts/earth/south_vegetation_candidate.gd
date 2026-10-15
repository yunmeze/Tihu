extends RefCounted
## Atomic preparation for four individually reviewed south vegetation groups.
## Source map, draw order and shadow eligibility remain unchanged.
## Runtime authority is this fixed path/SHA table plus the separately hash-pinned
## reviewed expected scope. Incoming registrations never define their own scope.
const Identity = preload("res://scripts/earth/instance_identity_guard.gd")
const Guard = preload("res://scripts/earth/asset_guard.gd")
const SOURCE = "res://data/maps/A13.json"
const SOURCE_SHA = "d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
const EXPECTED_SCOPE = "res://assets/earth/environment/south_reuse_v1/trusted_expected_scope.json"
const EXPECTED_SCOPE_SHA = "f1e92a32aea6c5b57214cddbb32e68eb8c647be9eb51263f86b9dddca6ff4164"
const IDS = ["upright_47_66", "upright_55_57", "upright_59_61", "shrub_58_51"]
const PATHS = {
	"upright_47_66": "res://assets/earth/environment/south_reuse_v1/registration_upright_47_66.json",
	"upright_55_57": "res://assets/earth/environment/south_reuse_v1/registration_upright_55_57.json",
	"upright_59_61": "res://assets/earth/environment/south_reuse_v1/registration_upright_59_61.json",
	"shrub_58_51": "res://assets/earth/environment/south_reuse_v1/registration_shrub_58_51.json",
}
const SHAS = {
	"upright_47_66": "e807ac0ca16145ad5ec6517d13fbad1587c1dfb07b7774216a18172a08239acc",
	"upright_55_57": "67c12f90f5872690c8a21cec953140b0d285823fbeed931083304b0d430d4b98",
	"upright_59_61": "9f329b4778d3351c3f870860f86085a7429948586c8a030062a7f9e539b12b8d",
	"shrub_58_51": "1b84a0cafaee3188cd86d20df06fac22972bed7644e4015a9caf53bac09e66c9",
}
const COUNTS = {"upright_47_66": 6, "upright_55_57": 6, "upright_59_61": 6, "shrub_58_51": 4}
# Textures may be shared; group success/preference/publication never is. Every
# prepare re-reads and hashes the loose PNG before consulting this cache.
static var _texture_cache: Dictionary = {}

static func prepare(id: Variant, path: Variant, map: Variant) -> Dictionary:
	if not id is String or not PATHS.has(id) or not path is String or path != PATHS[id]:
		return {}
	if not Identity.map_identity(map):
		return {}
	var original := _verified_json(SOURCE, SOURCE_SHA)
	if original.is_empty() or not _exact_equal(map, original):
		return {}
	var scope := _scope(id)
	if scope.is_empty():
		return {}
	var registration := _verified_json(path, SHAS[id])
	if registration.is_empty():
		return {}
	return _stage(id, registration, scope, original)

static func _scope(id: String) -> Dictionary:
	var document := _verified_json(EXPECTED_SCOPE, EXPECTED_SCOPE_SHA)
	if not document.get("groups") is Array or document.groups.size() != IDS.size():
		return {}
	var found: Dictionary = {}
	var seen: Dictionary = {}
	for candidate in document.groups:
		if not candidate is Dictionary or not candidate.get("id") is String:
			return {}
		var group_id: String = candidate.id
		if not PATHS.has(group_id) or seen.has(group_id):
			return {}
		seen[group_id] = true
		if not Identity.text(candidate.get("expected_registration_path"), PATHS[group_id]) or not Identity.text(candidate.get("expected_registration_sha256"), SHAS[group_id]):
			return {}
		if not Identity.text(candidate.get("source_map_sha256"), SOURCE_SHA) or not Identity.number(candidate.get("owner_count"), COUNTS[group_id]):
			return {}
		if not candidate.get("shadow_enabled") is bool or candidate.shadow_enabled:
			return {}
		if not candidate.get("expected_owners") is Array or candidate.expected_owners.size() != COUNTS[group_id]:
			return {}
		if group_id == id:
			found = candidate
	return found

static func _stage(id: String, registration: Dictionary, scope: Dictionary, original: Dictionary) -> Dictionary:
	if not Identity.text(registration.get("instance"), id) or not Identity.text(registration.get("source_map_sha256"), SOURCE_SHA):
		return {}
	if not Identity.text(registration.get("shadow"), "DISABLED for this candidate; no gate, receiver, mask, compositor slot or cast inherited"):
		return {}
	if not registration.get("owners") is Array or registration.owners.size() != COUNTS[id]:
		return {}
	var expected_keys: Array = []
	for expected in scope.expected_owners:
		expected_keys.append(expected.key)
	if not _exact_equal(registration.get("suppress_source_keys"), expected_keys):
		return {}
	var staged: Dictionary = {}
	for i in COUNTS[id]:
		var expected: Dictionary = scope.expected_owners[i]
		var record: Variant = registration.owners[i]
		if not record is Dictionary:
			return {}
		# Match every trusted field, including texture identity, full canvas,
		# translation, flag, empty304, scale and all source suppression identities.
		for field in expected:
			if not record.has(field) or not _exact_equal(record[field], expected[field]):
				return {}
		var order := int(expected.stable_source_order)
		var cell: Array = expected.cell
		if order != int(cell[0]) * 100 + int(cell[1]) or staged.has(order):
			return {}
		if not Identity.source_cell(original.cells[order], expected.source_cell):
			return {}
		if not Identity.number(expected.flag, int(expected.source_cell[1])) or not Identity.number(expected.source_cell[2], 2) or not Identity.number(expected.source_cell[3], int(expected.frame_index)):
			return {}
		if not Identity.number(expected.layer, 1) or not Identity.number(expected.sort_y, int(cell[1])):
			return {}
		var texture := _loose_texture(expected.texture, expected.texture_sha256, expected.texture_size, expected.empty)
		if texture == null:
			return {}
		# Start with the trusted identity, not unverified incoming fields. Keep
		# texture_path because the renderer's texture key contains a Texture2D.
		var item: Dictionary = expected.duplicate(true)
		item["texture_path"] = expected.texture
		item["texture"] = texture
		item["index"] = int(expected.frame_index)
		item["origin"] = Vector2(expected.world_top_left[0], expected.world_top_left[1])
		item["size"] = Vector2(expected.texture_size[0], expected.texture_size[1]) * float(expected.scale)
		item["group_id"] = id
		staged[order] = item
	# Nothing is published until every owner and dependency passes. Callers must
	# replace that group's previous dictionary with this result, even when empty.
	return staged

static func _loose_texture(path: String, digest: String, size: Array, empty: bool) -> Texture2D:
	if not Guard.asset_path(path) or not Guard.sha256(digest) or not Guard.vector(size, 2, 1, 16384):
		return null
	if not Guard.integer(size[0], 1, 16384) or not Guard.integer(size[1], 1, 16384):
		return null
	var bytes := _verified_bytes(path, digest)
	if bytes.is_empty():
		return null
	# Decode the same hashed loose bytes, avoiding stale imported texture data.
	var image := Image.new()
	if image.load_png_from_buffer(bytes) != OK or image.get_size() != Vector2i(int(size[0]), int(size[1])) or image.is_invisible() != empty:
		return null
	var cache_key := "%s|%s|%d,%d" % [path, digest, int(size[0]), int(size[1])]
	if _texture_cache.has(cache_key):
		return _texture_cache[cache_key]
	var texture := ImageTexture.create_from_image(image)
	if texture != null:
		_texture_cache[cache_key] = texture
	return texture

static func _verified_bytes(path: String, digest: String) -> PackedByteArray:
	if not FileAccess.file_exists(path):
		return PackedByteArray()
	var bytes := FileAccess.get_file_as_bytes(path)
	var context := HashingContext.new()
	if bytes.is_empty() or context.start(HashingContext.HASH_SHA256) != OK or context.update(bytes) != OK:
		return PackedByteArray()
	return bytes if context.finish().hex_encode() == digest else PackedByteArray()

static func _verified_json(path: String, digest: String) -> Dictionary:
	var bytes := _verified_bytes(path, digest)
	if bytes.is_empty():
		return {}
	var parser := JSON.new()
	if parser.parse(bytes.get_string_from_utf8()) != OK or not parser.data is Dictionary:
		return {}
	return parser.data

static func _exact_equal(value: Variant, expected: Variant) -> bool:
	# JSON numbers may be int or float, but bool/string coercions, NaN and Inf
	# are never accepted. Traverse only the trusted shape, with exact key sets.
	if expected is int or expected is float:
		return (value is int or value is float) and is_finite(float(value)) and value == expected
	if expected is String:
		return value is String and value == expected
	if expected is bool:
		return value is bool and value == expected
	if expected is Array:
		if not value is Array or value.size() != expected.size():
			return false
		for i in expected.size():
			if not _exact_equal(value[i], expected[i]):
				return false
		return true
	if expected is Dictionary:
		if not value is Dictionary or value.size() != expected.size():
			return false
		for key in expected:
			if not value.has(key) or not _exact_equal(value[key], expected[key]):
				return false
		return true
	return expected == null and value == null
