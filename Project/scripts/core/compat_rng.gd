extends RefCounted
## Explicit compatibility stream for resolved VM RND values. Not the VB PRNG.
## No global RNG, file I/O, clock seed, or live-state mutation.
const PROVIDER := "legend.compat-rng"
const VERSION := 1
const TRANSACTION := "legend.compat-rng-reservation"
const MAX_CURSOR := 9007199254740991
const MAX_RESERVATION := 64
const U32_MAX := 4294967295
const U32_SIZE := 4294967296
const HALF_U32 := 2147483648
const STATE_KEYS := ["provider", "version", "engine", "stream_id", "seed_words", "state_words", "cursor"]
const TRANSACTION_KEYS := ["kind", "version", "base", "count", "raw_values", "rnd_values", "checkpoints"]

## Caller must supply a unique session/stream token and an exact native int seed.
## Every current engine can create a new stream; only restoration is build-bound.
static func create(stream_id: Variant, seed_value: Variant) -> Dictionary:
	if not _token(stream_id): return _error("invalid_stream", "Supply a unique 1..64 character ASCII stream token.")
	if typeof(seed_value) != TYPE_INT: return _error("invalid_seed", "Seed must be a native signed 64-bit integer, never a JSON float.")
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	return _state_result({"provider":PROVIDER, "version":VERSION, "engine":engine_fingerprint(),
		"stream_id":stream_id, "seed_words":_words(seed_value), "state_words":_words(rng.state), "cursor":0})

## Structural admission of a caller-owned snapshot, not authentication/history proof.
## Only snapshots previously obtained from this provider may be restored.
static func validate(state: Variant) -> Dictionary:
	if not _keys(state, STATE_KEYS): return _error("invalid_state", "Unexpected RNG snapshot fields or types.")
	if typeof(state.provider) != TYPE_STRING or state.provider != PROVIDER or not _integer(state.version, VERSION, VERSION):
		return _error("unsupported_provider", "Unsupported RNG provider or version.")
	if typeof(state.engine) != TYPE_STRING or state.engine.length() > 256 or state.engine != engine_fingerprint():
		return _error("engine_mismatch", "This snapshot belongs to a different/unknown engine build; do not silently reseed.")
	if not _token(state.stream_id) or not _word_pair(state.seed_words) or not _word_pair(state.state_words) or not _integer(state.cursor, 0, MAX_CURSOR):
		return _error("invalid_state", "Invalid stream token, exact word pair, or cursor.")
	# Rebuild arrays so typed caller containers and aliases never enter output.
	return _state_result(_copy_state(state))

## Generate a detached read-only reservation. Repeating it on the same base
## yields the same draws; the caller has not advanced anything yet.
static func reserve(state: Variant, count: Variant) -> Dictionary:
	var checked := validate(state)
	if not checked.ok: return checked
	if not _integer(count, 0, MAX_RESERVATION): return _error("invalid_count", "Reservation count must be a native integer from 0 through 64.")
	if count > MAX_CURSOR - checked.state.cursor: return _error("cursor_overflow", "Reservation exceeds the bounded exact cursor.")
	var transaction := _reservation(checked.state, count)
	_freeze(transaction)
	return {"ok":true, "transaction":transaction}

## Validate the entire reservation, including unused suffixes, against the live
## base before publishing only the VM's successfully consumed prefix.
static func commit(current: Variant, transaction: Variant, consumed: Variant) -> Dictionary:
	var checked := validate(current)
	if not checked.ok: return checked
	var admitted := _admit_transaction(transaction)
	if not admitted.ok: return admitted
	if checked.state != admitted.base: return _error("stale_base", "Live RNG state/stream differs from the reservation base.")
	if not _integer(consumed, 0, transaction.count): return _error("invalid_consumed", "Consumed prefix must be a native integer within this reservation.")
	var expected := _reservation(checked.state, transaction.count)
	if not _same_candidate(transaction, expected): return _error("candidate_mismatch", "Reserved draws or checkpoints were modified.")
	var next := _copy_state(checked.state)
	if consumed > 0:
		next.state_words = _copy_words(expected.checkpoints[consumed - 1])
		next.cursor += consumed
	return _state_result(next)

## Discard a reservation, not undo an already committed stream. This performs no
## draw/replay. Candidate values are structurally checked but not trusted/used.
static func rollback(current: Variant, transaction: Variant) -> Dictionary:
	var checked := validate(current)
	if not checked.ok: return checked
	var admitted := _admit_transaction(transaction)
	if not admitted.ok: return admitted
	if checked.state != admitted.base: return _error("stale_base", "Cannot roll back after the stream has changed.")
	return checked

## Pure exact-grid conversion: nearest integer, exact halves to even.
## This declared compatibility rule is not certification of native helper ties.
static func resolve_u32(raw_value: Variant) -> Dictionary:
	if not _integer(raw_value, 0, U32_MAX): return _error("invalid_raw", "Raw draw must be an exact unsigned 32-bit native integer.")
	return {"ok":true, "value":_resolve(raw_value)}

static func engine_fingerprint() -> String:
	var info := Engine.get_version_info()
	return "%s.%s.%s:%s:%s:%s" % [info.major, info.minor, info.patch, info.status, info.build, info.hash]

static func _reservation(base: Dictionary, count: int) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	# Setting seed changes state: restore the recorded state only AFTER seed.
	rng.seed = _signed(base.seed_words)
	rng.state = _signed(base.state_words)
	var raw_values: Array = []
	var rnd_values: Array = []
	var checkpoints: Array = []
	for _index in count:
		var raw: int = rng.randi()
		raw_values.append(raw)
		rnd_values.append(_resolve(raw))
		checkpoints.append(_words(rng.state))
	return {"kind":TRANSACTION, "version":VERSION, "base":_copy_state(base), "count":count,
		"raw_values":raw_values, "rnd_values":rnd_values, "checkpoints":checkpoints}

static func _admit_transaction(transaction: Variant) -> Dictionary:
	if not _keys(transaction, TRANSACTION_KEYS): return _error("invalid_transaction", "Unexpected reservation fields or types.")
	if typeof(transaction.kind) != TYPE_STRING or transaction.kind != TRANSACTION or not _integer(transaction.version, VERSION, VERSION):
		return _error("invalid_transaction", "Unsupported reservation kind/version.")
	var base := validate(transaction.base)
	if not base.ok: return base
	if not _integer(transaction.count, 0, MAX_RESERVATION) or transaction.count > MAX_CURSOR - base.state.cursor:
		return _error("invalid_transaction", "Reservation count/cursor is out of bounds.")
	for field in ["raw_values", "rnd_values", "checkpoints"]:
		if typeof(transaction[field]) != TYPE_ARRAY or transaction[field].size() != transaction.count:
			return _error("invalid_transaction", "Reservation arrays must exactly match its bounded count.")
	for index in transaction.count:
		if not _integer(transaction.raw_values[index], 0, U32_MAX) or not _integer(transaction.rnd_values[index], 0, 100) or not _word_pair(transaction.checkpoints[index]):
			return _error("invalid_transaction", "Malformed reserved draw or checkpoint.")
	return {"ok":true, "base":base.state}

static func _same_candidate(actual: Dictionary, expected: Dictionary) -> bool:
	for index in actual.count:
		if actual.raw_values[index] != expected.raw_values[index] or actual.rnd_values[index] != expected.rnd_values[index]: return false
		for word in 2:
			if actual.checkpoints[index][word] != expected.checkpoints[index][word]: return false
	return true

static func _resolve(raw_value: int) -> int:
	var numerator: int = raw_value * 100 # <= 429496729500, safely signed 64-bit.
	@warning_ignore("integer_division")
	var quotient: int = numerator / U32_SIZE
	var remainder: int = numerator % U32_SIZE
	if remainder > HALF_U32 or (remainder == HALF_U32 and quotient % 2 == 1): quotient += 1
	return quotient

static func _words(value: int) -> Array:
	return [value & U32_MAX, (value >> 32) & U32_MAX]

static func _signed(words: Array) -> int:
	return (words[1] << 32) | words[0]

static func _copy_words(words: Array) -> Array:
	return [words[0], words[1]]

static func _copy_state(state: Dictionary) -> Dictionary:
	return {"provider":state.provider, "version":state.version, "engine":state.engine,
		"stream_id":state.stream_id, "seed_words":_copy_words(state.seed_words),
		"state_words":_copy_words(state.state_words), "cursor":state.cursor}

static func _word_pair(value: Variant) -> bool:
	return typeof(value) == TYPE_ARRAY and value.size() == 2 and _integer(value[0], 0, U32_MAX) and _integer(value[1], 0, U32_MAX)

static func _integer(value: Variant, minimum: int, maximum: int) -> bool:
	return typeof(value) == TYPE_INT and value >= minimum and value <= maximum

static func _token(value: Variant) -> bool:
	if typeof(value) != TYPE_STRING or value.is_empty() or value.length() > 64: return false
	for index in value.length():
		var code: int = value.unicode_at(index)
		if not ((code >= 48 and code <= 57) or (code >= 65 and code <= 90) or (code >= 97 and code <= 122) or code in [45, 46, 95]): return false
	return true

static func _keys(value: Variant, expected: Array) -> bool:
	if typeof(value) != TYPE_DICTIONARY or value.size() != expected.size(): return false
	for key in value:
		if typeof(key) != TYPE_STRING or key not in expected: return false
	return true

static func _state_result(state: Dictionary) -> Dictionary:
	_freeze(state)
	return {"ok":true, "state":state}

static func _freeze(value: Variant) -> void:
	if typeof(value) == TYPE_DICTIONARY:
		for child in value.values(): _freeze(child)
		value.make_read_only()
	elif typeof(value) == TYPE_ARRAY:
		for child in value: _freeze(child)
		value.make_read_only()

static func _error(code: String, detail: String) -> Dictionary:
	return {"ok":false, "error":code, "detail":detail}
