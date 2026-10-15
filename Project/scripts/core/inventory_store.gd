extends RefCounted
## Explicit-directory append-only inventory generations. No runtime integration.
## Writers must cooperate with this protocol; readers never modify the store.
const Codec = preload("res://scripts/core/inventory_codec.gd")
const Inventory = preload("res://scripts/core/inventory_state.gd")
const MAGIC := "LEGEND-INVENTORY-GENERATION/1"
const LOCK_NAME := ".inventory-write-lock"
const MAX_GENERATIONS := 128
const MAX_SCAN_ENTRIES := 512
const MAX_HEADER_BYTES := 256
const MAX_RECORD_BYTES := Codec.MAX_BYTES + MAX_HEADER_BYTES
const MAX_TOTAL_READ_BYTES := 16 * 1024 * 1024
const EMPTY_HEAD := {"max_generation": 0, "valid_generation": 0, "digest": ""}

func load_inventory(directory: Variant, id_namespace: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var prepared := _prepare(directory, id_namespace, catalogue, policy)
	if not prepared.ok:
		return prepared
	return _scan(prepared.path, id_namespace, catalogue, policy)

func save_inventory(directory: Variant, id_namespace: Variant, inventory: Variant, catalogue: Variant, policy: Variant, expected_head: Variant) -> Dictionary:
	var prepared := _prepare(directory, id_namespace, catalogue, policy)
	if not prepared.ok:
		return prepared
	var encoded := Codec.encode(inventory, catalogue, policy)
	if not encoded.ok:
		return encoded
	if encoded.inventory["namespace"] != id_namespace:
		return _error("namespace_mismatch", "Candidate does not belong to the explicit store namespace.")
	if not _valid_head(expected_head):
		return _error("invalid_head", "An exact head token from load (or EMPTY_HEAD) is required.")
	var root: String = prepared.path
	var context := {"root": root, "lock": root.path_join(LOCK_NAME)}
	context.temp = context.lock.path_join("pending.tmp")
	if _exists(context.lock):
		return _error("store_locked", "Writer lock exists; it will not be reclaimed automatically.")
	if _fault("before_lock", context) != OK:
		return _error("write_failed", "Stopped before acquiring writer lock.")
	var lock_error := DirAccess.make_dir_absolute(context.lock)
	if lock_error != OK:
		return _error("store_locked" if _exists(context.lock) else "lock_failed", "Could not exclusively create writer lock.")
	# Only this successful mkdir grants cleanup/write ownership of the lock.
	if _fault("after_lock", context) != OK:
		return _finish(_error("write_failed", "Stopped after acquiring writer lock."), context, false)
	var scanned := _scan(root, id_namespace, catalogue, policy)
	if not scanned.ok and scanned.get("error") != "no_valid_generation":
		return _finish(scanned, context, false)
	if scanned.generation_count > 0 and not scanned.ok:
		return _finish(scanned, context, false)
	if scanned.head != expected_head:
		return _finish(_error("stale_head", "Store changed since the supplied head was observed."), context, false)
	if scanned.generation_count >= MAX_GENERATIONS:
		return _finish(_error("generation_limit", "Generation limit reached; no history is automatically deleted."), context, false)
	if scanned.head.max_generation >= Inventory.MAX_INTEGER:
		return _finish(_error("generation_exhausted", "Generation counter cannot advance safely."), context, false)
	var generation: int = scanned.head.max_generation + 1
	context.generation = generation
	context.target = root.path_join(_filename(generation))
	if _exists(context.target):
		return _finish(_error("target_exists", "The new generation path is occupied; it will not be overwritten."), context, false)
	var record := _make_record(encoded.bytes, generation)
	var written := _write_candidate(context, record, id_namespace, catalogue, policy)
	if not written.ok:
		return _finish(written, context, written.get("temp_owned", false))
	if _fault("before_rename", context) != OK:
		return _finish(_error("write_failed", "Stopped before publication."), context, true)
	# Godot has no portable no-replace rename. The mkdir lock excludes cooperating
	# writers; the explicit absence check avoids the Windows overwrite branch.
	if _exists(context.target):
		return _finish(_error("target_exists", "Generation appeared before publication; refusing overwrite."), context, true)
	var rename_error := _rename(context.temp, context.target)
	var warnings: Array = []
	if rename_error != OK:
		# An error after actual publication must not invite a duplicate retry.
		var reconciled := _read_record(context.target, generation, id_namespace, catalogue, policy, [MAX_TOTAL_READ_BYTES])
		if reconciled.ok and reconciled.bytes == record:
			warnings.append({"error": "rename_reported_error", "detail": "Publication was verified despite a rename error."})
		elif _exists(context.temp) and not _exists(context.target):
			return _finish(_error("rename_failed", "Publication failed; earlier generations remain untouched."), context, true)
		else:
			var uncertain := _error("commit_uncertain", "Publication outcome cannot be established; reload read-only before recovery.")
			uncertain.committed = null
			uncertain.lock_pending = true
			uncertain.path = context.target
			return uncertain
	if _fault("after_rename", context) != OK:
		warnings.append({"error": "post_commit_check_failed", "detail": "Publication committed; a later checkpoint failed."})
	var result := {"ok": true, "committed": true, "generation": generation, "path": context.target,
		"inventory": encoded.inventory, "total_weight": encoded.total_weight, "overweight": encoded.overweight,
		"head": {"max_generation": generation, "valid_generation": generation, "digest": _digest(record)}, "warnings": warnings}
	return _finish(result, context, true)

func _write_candidate(context: Dictionary, record: PackedByteArray, id_namespace: String, catalogue: Variant, policy: Variant) -> Dictionary:
	if _exists(context.temp):
		return _error("temp_exists", "Owned staging directory unexpectedly contains a pending path.")
	if _fault("before_write", context) != OK:
		return _error("write_failed", "Stopped before writing candidate.")
	var file := FileAccess.open(context.temp, FileAccess.WRITE)
	if file == null:
		var failed := _error("write_failed", "Could not open candidate file.")
		failed.temp_owned = true
		return failed
	var stored := file.store_buffer(record)
	var write_error := file.get_error()
	var after_write := _fault("after_write", context)
	if not stored or write_error != OK or after_write != OK:
		file.close()
		return _owned_error("write_failed", "Candidate write failed.")
	if _fault("before_flush", context) != OK:
		file.close()
		return _owned_error("write_failed", "Stopped before flush.")
	file.flush()
	var flush_error := file.get_error()
	var after_flush := _fault("after_flush", context)
	file.close()
	if flush_error != OK or after_flush != OK:
		return _owned_error("write_failed", "Candidate flush/checkpoint failed.")
	if _fault("before_verify", context) != OK:
		return _owned_error("write_failed", "Stopped before candidate reread.")
	var checked := _read_record(context.temp, context.generation, id_namespace, catalogue, policy, [MAX_TOTAL_READ_BYTES])
	if not checked.ok:
		checked.temp_owned = true
		return checked
	if checked.bytes != record:
		return _owned_error("verification_mismatch", "Candidate bytes changed after write.")
	if _fault("after_verify", context) != OK:
		return _owned_error("write_failed", "Stopped after candidate verification.")
	return {"ok": true}

func _scan(root: String, id_namespace: String, catalogue: Variant, policy: Variant) -> Dictionary:
	var directory := DirAccess.open(root)
	if directory == null:
		return _error("read_failed", "Store directory cannot be opened.")
	directory.include_hidden = true
	directory.include_navigational = false
	if directory.list_dir_begin() != OK:
		return _error("read_failed", "Store directory cannot be enumerated.")
	var candidates: Array = []
	var entries := 0
	var maximum := 0
	while true:
		var name := directory.get_next()
		if name.is_empty(): break
		entries += 1
		if entries > MAX_SCAN_ENTRIES:
			directory.list_dir_end()
			return _error("scan_limit", "Directory entry limit exceeded; no partial scan is accepted.")
		var generation: Variant = _generation(name)
		if generation == null: continue
		candidates.append({"generation": generation, "path": root.path_join(name)})
		maximum = maxi(maximum, generation)
		if candidates.size() > MAX_GENERATIONS:
			directory.list_dir_end()
			return _error("generation_limit", "Recognized generation count exceeds the limit.")
	directory.list_dir_end()
	candidates.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.generation > b.generation)
	var rejected: Array = []
	var budget := [MAX_TOTAL_READ_BYTES]
	var barrier := ""
	for candidate in candidates:
		var checked := _read_record(candidate.path, candidate.generation, id_namespace, catalogue, policy, budget)
		if checked.ok:
			var head := {"max_generation": maximum, "valid_generation": candidate.generation, "digest": _digest(checked.bytes)}
			if not barrier.is_empty():
				var blocked := _error(barrier, "A newer incompatible generation prevents automatic rollback or continued writing.")
				blocked.head = head
				blocked.rejected = rejected
				blocked.generation_count = candidates.size()
				blocked.recoverable = {"generation": candidate.generation, "path": candidate.path, "digest": head.digest}
				return blocked
			return {"ok": true, "inventory": checked.inventory, "total_weight": checked.total_weight,
				"overweight": checked.overweight, "generation": candidate.generation, "path": candidate.path,
				"source": "latest" if candidate.generation == maximum else "fallback", "head": head,
				"rejected": rejected, "generation_count": candidates.size()}
		if checked.error in ["read_budget", "structure_limit", "instance_limit"]:
			checked.rejected = rejected
			checked.head = {"max_generation": maximum, "valid_generation": 0, "digest": ""}
			checked.generation_count = candidates.size()
			return checked
		rejected.append({"generation": candidate.generation, "path": candidate.path, "error": checked.error, "detail": checked.detail})
		if checked.error in ["unsupported_store_version", "unsupported_version", "unsupported_format"]:
			barrier = "unsupported_newer_version"
		elif checked.error in ["generation_mismatch", "namespace_mismatch"] and barrier.is_empty():
			barrier = "incompatible_generation"
		elif checked.get("schema_status", "unknown") != "known" and barrier.is_empty():
			barrier = "compatibility_unknown"
	var failed := _error(barrier if not barrier.is_empty() else "no_valid_generation", "No automatically adoptable inventory generation was found.")
	failed.head = {"max_generation": maximum, "valid_generation": 0, "digest": ""}
	failed.rejected = rejected
	failed.generation_count = candidates.size()
	return failed

# Fixed ordered ASCII preheader is independently bounded. It authenticates no
# local writer; its checksum detects accidental damage, not malicious tampering.
static func _make_record(payload: PackedByteArray, generation: int) -> PackedByteArray:
	var header := "%s\ncodec-format:%s\ncodec-version:%d\ngeneration:%d\npayload-bytes:%d\npayload-sha256:%s\n\n" % [MAGIC, Codec.FORMAT, Codec.VERSION, generation, payload.size(), _digest(payload)]
	var bytes := header.to_utf8_buffer()
	bytes.append_array(payload)
	return bytes

static func _inspect_header(prefix: PackedByteArray, generation: int) -> Dictionary:
	var first := prefix.find(10)
	if first < 0 or first > 64:
		return _error("invalid_record", "Generation header is incomplete or oversized.")
	for index in first:
		if prefix[index] < 32 or prefix[index] > 126:
			return _error("invalid_record", "Header must be printable ASCII with LF separators.")
	var magic := prefix.slice(0, first).get_string_from_ascii()
	if magic != MAGIC:
		return _error("unsupported_store_version" if magic.begins_with("LEGEND-INVENTORY-GENERATION/") else "invalid_record", "Unsupported or malformed store schema.")
	var end := -1
	for index in range(first + 1, prefix.size() - 1):
		if prefix[index] == 10 and prefix[index + 1] == 10:
			end = index + 2
			break
	if end < 0 or end > MAX_HEADER_BYTES:
		return _error("invalid_record", "Complete fixed preheader was not found within its limit.")
	for index in end:
		if prefix[index] != 10 and (prefix[index] < 32 or prefix[index] > 126):
			return _error("invalid_record", "Header must be printable ASCII with LF separators.")
	var lines := prefix.slice(0, end - 2).get_string_from_ascii().split("\n")
	if lines.size() != 6 or not lines[1].begins_with("codec-format:") or not lines[2].begins_with("codec-version:") or not lines[3].begins_with("generation:") or not lines[4].begins_with("payload-bytes:") or not lines[5].begins_with("payload-sha256:"):
		return _error("invalid_record", "Preheader requires the exact ordered schema, generation, length, and digest fields.")
	if lines[1] != "codec-format:" + Codec.FORMAT:
		return _error("unsupported_format", "Preheader declares an unsupported codec format.")
	if lines[2] != "codec-version:" + str(Codec.VERSION):
		return _error("unsupported_version", "Preheader declares an unsupported codec version.")
	if lines[3] != "generation:" + str(generation):
		return _error("generation_mismatch", "Filename and preheader generation disagree.")
	var length_text: String = lines[4].trim_prefix("payload-bytes:")
	if length_text.is_empty() or length_text.length() > 16:
		return _error("invalid_record", "Payload length must be a canonical bounded positive integer.")
	for character in length_text:
		if character not in "0123456789": return _error("invalid_record", "Payload length must be decimal digits.")
	var length := length_text.to_int()
	if length <= 0 or length > Inventory.MAX_INTEGER or str(length) != length_text:
		return _error("invalid_record", "Payload length is noncanonical or out of range.")
	var digest: String = lines[5].trim_prefix("payload-sha256:")
	if digest.length() != 64:
		return _error("invalid_record", "Payload digest must be 64 lowercase hexadecimal digits.")
	for character in digest:
		if character not in "0123456789abcdef": return _error("invalid_record", "Payload digest must be lowercase hexadecimal.")
	return {"ok": true, "schema_status": "known", "end": end, "length": length, "digest": digest}

func _read_record(path: String, generation: int, id_namespace: String, catalogue: Variant, policy: Variant, budget: Array) -> Dictionary:
	if _is_link(path) or DirAccess.dir_exists_absolute(path):
		return _error("invalid_path", "Generation cannot be a directory or symbolic link.")
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return _error("read_failed", "Generation file cannot be opened.")
	var size := file.get_length()
	var prefix_size := mini(size, MAX_HEADER_BYTES)
	if prefix_size > budget[0]:
		file.close()
		return _error("read_budget", "Header probe exceeds total read budget.")
	var prefix := file.get_buffer(prefix_size)
	budget[0] -= prefix.size()
	if prefix.size() != prefix_size or file.get_error() != OK:
		file.close()
		return _error("short_read", "Preheader could not be read completely.")
	# Schema recognition precedes every v1 payload size/semantic constraint.
	var header := _inspect_header(prefix, generation)
	if not header.ok:
		file.close()
		return header
	if size > MAX_RECORD_BYTES or size - header.end > Codec.MAX_BYTES:
		file.close()
		return _error("byte_limit", "Body exceeds the inspection limit; compatibility cannot be cross-checked safely.")
	if size - prefix.size() > budget[0]:
		file.close()
		return _error("read_budget", "Total read budget exhausted; no partial fallback is accepted.")
	var remainder := file.get_buffer(size - prefix.size())
	budget[0] -= remainder.size()
	var read_error := file.get_error()
	var ending_size := file.get_length()
	file.close()
	if remainder.size() != size - prefix.size() or read_error != OK or ending_size != size:
		return _known_record_error("short_read", "Known-schema body changed or could not be read completely.")
	var bytes := prefix
	bytes.append_array(remainder)
	var payload := bytes.slice(header.end)
	# Even a stale hash/length must not conceal a parseable future body schema.
	var schema := Codec.inspect_schema(payload)
	if schema.get("schema_status") == "incompatible" or schema.get("error") == "structure_limit":
		return schema
	if payload.size() != header.length:
		return _known_record_error("length_mismatch", "Known-schema payload length does not match its preheader.")
	if _digest(payload) != header.digest:
		return _known_record_error("checksum_mismatch", "Known-schema payload digest does not match its preheader.")
	var decoded := Codec.decode(payload, catalogue, policy)
	if not decoded.ok:
		# A complete compatible preheader allows recovery from malformed body
		# text, including truncation and invalid UTF-8. Explicit future schemas
		# and inspection-budget errors above never enter this fallback branch.
		decoded.schema_status = "known"
		return decoded
	if decoded.inventory["namespace"] != id_namespace:
		return _error("namespace_mismatch", "Generation belongs to a different inventory namespace.")
	decoded.bytes = bytes
	return decoded

static func _known_record_error(code: String, detail: String) -> Dictionary:
	var result := _error(code, detail)
	result.schema_status = "known"
	return result

func _prepare(directory: Variant, id_namespace: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	var checked := Inventory.create(id_namespace, catalogue, policy)
	if not checked.ok: return checked
	if typeof(directory) != TYPE_STRING or directory.is_empty() or directory.begins_with("res://"):
		return _error("invalid_path", "An explicit absolute or user:// directory is required.")
	var path: String = ProjectSettings.globalize_path(directory) if directory.begins_with("user://") else directory
	if not path.is_absolute_path(): return _error("invalid_path", "Relative store directories are unsupported.")
	path = path.simplify_path().trim_suffix("/")
	if path.is_empty() or path == "." or not DirAccess.dir_exists_absolute(path) or _is_link(path):
		return _error("invalid_path", "Caller must provide an existing dedicated directory without a link at its root.")
	return {"ok": true, "path": path}

func _finish(result: Dictionary, context: Dictionary, temp_owned: bool) -> Dictionary:
	var warnings: Array = result.get("warnings", [])
	if _fault("before_cleanup", context) != OK:
		warnings.append({"error": "cleanup_failed", "detail": "Writer lock requires explicit cleanup."})
	else:
		if temp_owned and _exists(context.temp):
			if DirAccess.dir_exists_absolute(context.temp) or DirAccess.remove_absolute(context.temp) != OK:
				warnings.append({"error": "cleanup_failed", "detail": "Owned pending file could not be removed."})
		if DirAccess.remove_absolute(context.lock) != OK:
			warnings.append({"error": "cleanup_failed", "detail": "Owned writer lock could not be removed; it was not recursively deleted."})
		if _fault("after_cleanup", context) != OK:
			warnings.append({"error": "cleanup_check_failed", "detail": "Cleanup checkpoint failed after attempted release."})
	result.warnings = warnings
	result.lock_pending = _exists(context.lock)
	if not result.has("committed"): result.committed = false
	return result

func _rename(from: String, to: String) -> Error:
	return DirAccess.rename_absolute(from, to)

# Protected deterministic fault seam for isolated test subclasses, not a saved
# input field or a caller-selected runtime hook. Production always returns OK.
func _fault(_point: String, _context: Dictionary) -> Error:
	return OK

static func _valid_head(value: Variant) -> bool:
	if typeof(value) != TYPE_DICTIONARY or value.size() != 3 or not value.has_all(["max_generation", "valid_generation", "digest"]): return false
	for key in ["max_generation", "valid_generation"]:
		if typeof(value[key]) != TYPE_INT or value[key] < 0 or value[key] > Inventory.MAX_INTEGER: return false
	if value.valid_generation > value.max_generation or typeof(value.digest) != TYPE_STRING: return false
	if value.valid_generation == 0: return value.digest == ""
	if value.digest.length() != 64: return false
	for character in value.digest:
		if character not in "0123456789abcdef": return false
	return true

static func _filename(generation: int) -> String:
	return "inventory-%016d.dat" % generation

static func _generation(name: String) -> Variant:
	if not name.begins_with("inventory-") or not name.ends_with(".dat") or name.length() != 30: return null
	var digits := name.substr(10, 16)
	for character in digits:
		if character not in "0123456789": return null
	var generation := digits.to_int()
	return generation if generation > 0 and generation <= Inventory.MAX_INTEGER and _filename(generation) == name else null

static func _is_link(path: String) -> bool:
	var parent := DirAccess.open(path.get_base_dir())
	return parent != null and parent.is_link(path.get_file())

static func _exists(path: String) -> bool:
	return FileAccess.file_exists(path) or DirAccess.dir_exists_absolute(path) or _is_link(path)

static func _digest(bytes: PackedByteArray) -> String:
	var hashing := HashingContext.new()
	hashing.start(HashingContext.HASH_SHA256)
	hashing.update(bytes)
	return hashing.finish().hex_encode()

static func _error(code: String, detail: String) -> Dictionary:
	return {"ok": false, "error": code, "detail": detail, "committed": false}

static func _owned_error(code: String, detail: String) -> Dictionary:
	var result := _error(code, detail)
	result.temp_owned = true
	return result
