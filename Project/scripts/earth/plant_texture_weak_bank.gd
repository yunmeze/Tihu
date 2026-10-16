extends RefCounted
## Shared bank-owned immutable ImageTextures, with weak texture ownership.
## Callers must not update/reinitialize textures or mutate bank-owned tokens.

const MANIFEST = "res://assets/earth/first_map_review/plant_shared_bank_v1.json"
const MANIFEST_SHA = "0e4c6a9663bb4ff092088216103fdb3e3897e04a9a880566b5d0bfb214eeab8e"
const CONTRACT = "rgba8/no_mipmaps/linear/clamp/v1"

class BindingToken extends RefCounted:
	# Only the bank changes this flag. It holds no texture, image, or world.
	var active: bool = true

# The weak reference is directly to the texture, never to a temporary binding.
static var _weak: Dictionary = {}
# Values contain only immutable metadata and a bank-owned revocation token.
static var _proof: Dictionary = {}
# Never reset this serial: a later entry must not reuse a retired generation.
static var _generation: int = 0
static var hits = 0
static var misses = 0


static func rgba_hash(data: PackedByteArray) -> String:
	var ctx = HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(data)
	return ctx.finish().hex_encode()


# Compatibility API. A caller retaining only this texture still keeps a cache
# hit alive, but does NOT receive binding_valid/reset revocation enforcement.
static func acquire(path: String, digest: String, size: Vector2i) -> Texture2D:
	var binding = acquire_binding(path, digest, size)
	return binding.get("texture") as Texture2D


# A successful binding owns its texture; the bank itself never owns it strongly.
# Failure returns {}. Every request verifies current PNG and manifest bytes,
# including hits; only a cache miss decodes the complete PNG.
static func acquire_binding(path: String, digest: String, size: Vector2i) -> Dictionary:
	if not path.begins_with("res://assets/") or path.simplify_path() != path or ".." in path:
		return {}
	if size.x <= 0 or size.y <= 0 or not FileAccess.file_exists(path):
		return {}
	var raw = FileAccess.get_file_as_bytes(path)
	if rgba_hash(raw) != digest:
		return {}
	var entry = _verified_entry(path, digest, size)
	if entry.is_empty():
		return {}
	var key = path + "|" + digest + "|" + str(size) + "|" + entry.rgba_sha256 + "|" + CONTRACT
	if _weak.has(key) and _proof.has(key):
		var found = _current_texture(key, _proof[key])
		if found != null:
			hits += 1
			return _make_binding(_proof[key], found)
	# A dead weak entry or invalid metadata retires its token before replacement.
	_retire(key)
	var im = Image.new()
	if im.load_png_from_buffer(raw) != OK or im.get_size() != size:
		return {}
	im.convert(Image.FORMAT_RGBA8)
	if im.has_mipmaps() or rgba_hash(im.get_data()) != entry.rgba_sha256:
		return {}
	# This evidence comes from the SAME decoded/verified image used to create the
	# texture, with no later get_image/readback and no second decode on a hit.
	var empty_alpha = im.is_invisible()
	var result = ImageTexture.create_from_image(im)
	if result == null or result.get_size() != Vector2(size) or not result.get_rid().is_valid():
		return {}
	_generation += 1
	var proof = {
		"key": key,
		"path": path,
		"sha256": digest,
		"rgba_sha256": entry.rgba_sha256,
		"manifest_sha256": MANIFEST_SHA,
		"contract": CONTRACT,
		"size": size,
		"rid": result.get_rid(),
		"empty_alpha": empty_alpha,
		"generation": _generation,
		"token": BindingToken.new(),
	}
	proof.make_read_only()
	_weak[key] = weakref(result)
	_proof[key] = proof
	misses += 1
	return _make_binding(proof, result)


# No filesystem access, PNG decode, pixel scan, or texture readback. This checks
# bank provenance/liveness under the immutable-texture ownership contract, not
# the pixels of a texture illegally updated by an outside caller.
static func binding_valid(binding: Dictionary) -> bool:
	if not binding.is_read_only():
		return false
	var key = binding.get("key")
	if not key is String or not _weak.has(key) or not _proof.has(key):
		return false
	var proof: Dictionary = _proof[key]
	if binding.size() != proof.size() + 1 or not binding.has("texture"):
		return false
	# Object equality is token identity. Merely making an old token active again
	# cannot restore removed membership or replace the current generation/token.
	if binding.get("token") != proof.token:
		return false
	for field in proof:
		if not binding.has(field):
			return false
		# Variant equality can coerce e.g. int/float; provenance cannot.
		if typeof(binding[field]) != typeof(proof[field]) or binding[field] != proof[field]:
			return false
	var texture = _current_texture(key, proof)
	if texture == null or binding.get("texture") != texture:
		return false
	return true


# Explicit SHARED-entry revocation; never call this for a local world reset.
# Old binding dictionaries may still hold the old texture, but fail validation.
static func reset_key(path: String, digest: String, size: Vector2i) -> void:
	for key in _proof.keys():
		var proof: Dictionary = _proof[key]
		if proof.path == path and proof.sha256 == digest and proof.size == size:
			_retire(key)


# Explicit bank-wide revocation, not local-world teardown. Lifetime counters and
# the generation serial are intentionally preserved across resets.
static func reset_all() -> void:
	for key in _proof.keys():
		_retire(key)
	_weak.clear()


static func live_count() -> int:
	var count = 0
	for key in _weak.keys():
		if not _proof.has(key) or _current_texture(key, _proof[key]) == null:
			_retire(key)
		else:
			count += 1
	return count


static func _verified_entry(path: String, digest: String, size: Vector2i) -> Dictionary:
	if not FileAccess.file_exists(MANIFEST):
		return {}
	# Hash and parse the same manifest bytes, retaining the original SHA/schema
	# checks without a second manifest read between verification and parsing.
	var manifest_bytes = FileAccess.get_file_as_bytes(MANIFEST)
	if rgba_hash(manifest_bytes) != MANIFEST_SHA:
		return {}
	var spec = JSON.parse_string(manifest_bytes.get_string_from_utf8())
	if not spec is Dictionary or spec.get("schema") != "verified-plant-texture-bank-v1":
		return {}
	if not spec.get("entries") is Array or spec.entries.size() != 21:
		return {}
	var entry: Dictionary = {}
	for row in spec.entries:
		if not row is Dictionary:
			return {}
		if row.get("path") == path:
			if not entry.is_empty():
				return {}
			entry = row
	if entry.is_empty() or entry.get("sha256") != digest or entry.get("contract") != CONTRACT:
		return {}
	var declared_size = entry.get("size")
	if not declared_size is Array or declared_size.size() != 2:
		return {}
	if declared_size[0] != size.x or declared_size[1] != size.y:
		return {}
	if not entry.get("rgba_sha256") is String or entry.rgba_sha256.length() != 64:
		return {}
	return entry


static func _current_texture(key: String, proof: Dictionary) -> ImageTexture:
	if not _weak.has(key) or not proof.is_read_only() or proof.get("key") != key:
		return null
	var token = proof.get("token")
	if not token is BindingToken or not token.active:
		return null
	if not proof.get("generation") is int or proof.generation <= 0:
		return null
	var texture = _weak[key].get_ref()
	if texture == null or not texture is ImageTexture:
		return null
	if texture.get_rid() != proof.rid or not proof.rid.is_valid():
		return null
	if texture.get_size() != Vector2(proof.size):
		return null
	return texture


static func _make_binding(proof: Dictionary, texture: ImageTexture) -> Dictionary:
	# Shallow copy retains only the shared token identity; proof has no mutable
	# nested container or texture. Only the returned binding owns the texture.
	var binding = proof.duplicate()
	binding["texture"] = texture
	binding.make_read_only()
	return binding


static func _retire(key: String) -> void:
	if _proof.has(key):
		_proof[key].token.active = false
		_proof.erase(key)
	_weak.erase(key)
