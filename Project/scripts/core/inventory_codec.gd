extends RefCounted
## Inventory-only persistence envelope. Pure bytes in/out; no paths or file I/O.
const Inventory = preload("res://scripts/core/inventory_state.gd")
const FORMAT := "legend.inventory"
const VERSION := 1
const MAX_BYTES := 4 * 1024 * 1024
const MAX_INSTANCES := 4096
const MAX_NODES := 131072
const MAX_DEPTH := 24
const MAX_NUMBER_CHARS := 128

static func encode(inventory: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	if typeof(inventory) != TYPE_DICTIONARY or typeof(inventory.get("instances")) != TYPE_DICTIONARY:
		return _error("invalid_inventory", "Inventory must contain an instances dictionary.")
	if inventory.instances.size() > MAX_INSTANCES:
		return _error("instance_limit", "Instance count exceeds the codec limit.")
	# Bound traversal and output before core normalization and JSON allocation.
	var bounded := _measure(inventory, [0, 256], 0)
	if not bounded.ok:
		return bounded
	var checked := Inventory.validate(inventory, catalogue, policy)
	if not checked.ok:
		return checked
	if not _integer_numbers_only(checked.inventory):
		return _error("unsupported_fractional_metadata", "Codec v1 supports only exact integer-valued metadata numbers.")
	var envelope := {"format": FORMAT, "version": VERSION, "inventory": checked.inventory}
	var bytes := JSON.stringify(envelope, "", true, true).to_utf8_buffer()
	if bytes.size() > MAX_BYTES:
		return _error("byte_limit", "Encoded inventory exceeds the byte limit.")
	# Verify exactly what will be persisted, not merely the pre-serialization input.
	var verified := decode(bytes, catalogue, policy)
	if not verified.ok:
		return verified
	if not _same_json_value(checked.inventory, verified.inventory):
		return _error("precision_loss", "The engine cannot round-trip these metadata numbers exactly; no bytes were returned.")
	return {"ok": true, "bytes": bytes, "inventory": verified.inventory,
		"total_weight": verified.total_weight, "overweight": verified.overweight}

static func decode(bytes: Variant, catalogue: Variant, policy: Variant) -> Dictionary:
	if typeof(bytes) != TYPE_PACKED_BYTE_ARRAY:
		return _error("invalid_bytes", "Decode requires a PackedByteArray.")
	if bytes.is_empty() or bytes.size() > MAX_BYTES:
		return _error("byte_limit", "Encoded inventory is empty or exceeds the byte limit.")
	if not _valid_utf8(bytes) or (bytes.size() >= 3 and bytes[0] == 0xef and bytes[1] == 0xbb and bytes[2] == 0xbf):
		return _error("invalid_utf8", "Input must be strict UTF-8 without a byte-order mark.")
	if bytes.find(0) >= 0:
		return _error("invalid_json", "Raw NUL bytes are not valid JSON text.")
	var source: String = bytes.get_string_from_utf8()
	# First pass checks syntax, duplicate keys, depth/nodes, and instance count
	# before any instance-record dictionaries are materialized by the second pass.
	var preflight := Parser.new(source, false).parse()
	if not preflight.ok:
		return preflight
	var parsed := Parser.new(source, true).parse()
	if not parsed.ok:
		return parsed
	var envelope: Variant = parsed.value
	if typeof(envelope) != TYPE_DICTIONARY or envelope.size() != 3 or not envelope.has_all(["format", "version", "inventory"]):
		return _error("invalid_envelope", "Envelope requires exactly format, version, and inventory.")
	if typeof(envelope.format) != TYPE_STRING or envelope.format != FORMAT:
		return _error("unsupported_format", "This is not an inventory-only envelope.")
	if typeof(envelope.version) != TYPE_INT or envelope.version != VERSION:
		return _error("unsupported_version", "Inventory envelope version is unsupported.")
	var checked := Inventory.validate(envelope.inventory, catalogue, policy)
	if not checked.ok:
		return checked
	return checked

static func _measure(value: Variant, budget: Array, depth: int) -> Dictionary:
	budget[0] += 1
	if depth > MAX_DEPTH or budget[0] > MAX_NODES:
		return _error("structure_limit", "Input exceeds the depth or traversal budget.")
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_FLOAT:
			budget[1] += 32
		TYPE_STRING, TYPE_STRING_NAME:
			# Conservative pre-allocation bound, including JSON escaping.
			budget[1] += 2 + 6 * value.length()
		TYPE_ARRAY:
			budget[1] += 2 + value.size()
			for child in value:
				var result := _measure(child, budget, depth + 1)
				if not result.ok:
					return result
		TYPE_DICTIONARY:
			budget[1] += 2 + value.size() * 2
			for key in value:
				var result := _measure(key, budget, depth + 1)
				if not result.ok:
					return result
				result = _measure(value[key], budget, depth + 1)
				if not result.ok:
					return result
		_:
			return _error("invalid_value", "Only bounded JSON-compatible values are encodable.")
	if budget[1] > MAX_BYTES:
		return _error("byte_limit", "Input exceeds the conservative encoding-size budget.")
	return {"ok": true}

# Codec v1 deliberately narrows core metadata to integer-valued numbers. This
# avoids engine decimal-to-float drift; future binary-float support needs a new,
# explicit format rather than a silent schema expansion.
static func _integer_numbers_only(value: Variant) -> bool:
	if typeof(value) == TYPE_FLOAT:
		return is_finite(value) and floor(value) == value and absf(value) <= float(Inventory.MAX_INTEGER)
	if typeof(value) == TYPE_DICTIONARY:
		for child in value.values():
			if not _integer_numbers_only(child): return false
	elif typeof(value) == TYPE_ARRAY:
		for child in value:
			if not _integer_numbers_only(child): return false
	return true

# Preserve all content while allowing the documented exact integral-float/int
# normalization (including signed zero). No successful encode may lose values.
static func _same_json_value(left: Variant, right: Variant) -> bool:
	var left_type := typeof(left)
	var right_type := typeof(right)
	if left_type in [TYPE_INT, TYPE_FLOAT] and right_type in [TYPE_INT, TYPE_FLOAT]:
		if left == 0 and right == 0:
			return true
		if left_type == TYPE_FLOAT and right_type == TYPE_FLOAT:
			return var_to_bytes(left) == var_to_bytes(right)
		return left == right
	if left_type != right_type:
		return false
	if left_type == TYPE_DICTIONARY:
		if left.size() != right.size(): return false
		for key in left:
			if not right.has(key) or not _same_json_value(left[key], right[key]): return false
		return true
	if left_type == TYPE_ARRAY:
		if left.size() != right.size(): return false
		for index in left.size():
			if not _same_json_value(left[index], right[index]): return false
		return true
	return left == right

static func _valid_utf8(bytes: PackedByteArray) -> bool:
	var index := 0
	while index < bytes.size():
		var first: int = bytes[index]
		if first < 0x80:
			index += 1
			continue
		var count := 0
		var lower := 0x80
		var upper := 0xbf
		if first >= 0xc2 and first <= 0xdf:
			count = 2
		elif first >= 0xe0 and first <= 0xef:
			count = 3
			if first == 0xe0: lower = 0xa0
			if first == 0xed: upper = 0x9f
		elif first >= 0xf0 and first <= 0xf4:
			count = 4
			if first == 0xf0: lower = 0x90
			if first == 0xf4: upper = 0x8f
		else:
			return false
		if index + count > bytes.size() or bytes[index + 1] < lower or bytes[index + 1] > upper:
			return false
		for offset in range(2, count):
			if bytes[index + offset] < 0x80 or bytes[index + offset] > 0xbf:
				return false
		index += count
	return true

static func _error(code: String, detail: String) -> Dictionary:
	return {"ok": false, "error": code, "detail": detail}

class Parser:
	extends RefCounted
	var source: String
	var build: bool
	var position := 0
	var nodes := 0
	var failure: Dictionary = {}

	func _init(text: String, materialize: bool) -> void:
		source = text
		build = materialize

	func parse() -> Dictionary:
		var value: Variant = _value([], 0)
		_space()
		if failure.is_empty() and position != source.length():
			_fail("invalid_json", "Trailing content after JSON value.")
		return {"ok": true, "value": value} if failure.is_empty() else failure

	func _value(path: Array, depth: int) -> Variant:
		_space()
		nodes += 1
		if depth > MAX_DEPTH or nodes > MAX_NODES:
			return _fail("structure_limit", "JSON depth or node limit exceeded.")
		if position >= source.length():
			return _fail("invalid_json", "Unexpected end of JSON.")
		var character := source[position]
		if character == "{": return _object(path, depth)
		if character == "[": return _array(path, depth)
		if character == '"': return _string()
		for literal in ["null", "true", "false"]:
			if source.substr(position, literal.length()) == literal:
				position += literal.length()
				return null if literal == "null" else literal == "true"
		if character == "-" or character in "0123456789":
			return _number(path)
		return _fail("invalid_json", "Unexpected JSON token.")

	func _object(path: Array, depth: int) -> Variant:
		position += 1
		var object := {}
		var seen := {}
		_space()
		if _take("}"): return object if build else null
		while failure.is_empty():
			_space()
			if position >= source.length() or source[position] != '"':
				return _fail("invalid_json", "Object key must be a string.")
			var key: Variant = _string()
			if not failure.is_empty(): return null
			if seen.has(key): return _fail("duplicate_key", "Duplicate object keys are not accepted.")
			seen[key] = true
			if path == ["inventory", "instances"] and seen.size() > MAX_INSTANCES:
				return _fail("instance_limit", "Instance count exceeds the codec limit.")
			_space()
			if not _take(":"): return _fail("invalid_json", "Missing colon after object key.")
			var value: Variant = _value(path + [key], depth + 1)
			if not failure.is_empty(): return null
			if build: object[key] = value
			_space()
			if _take("}"): return object if build else null
			if not _take(","): return _fail("invalid_json", "Missing comma between object members.")
		return null

	func _array(path: Array, depth: int) -> Variant:
		position += 1
		var array: Array = []
		_space()
		if _take("]"): return array if build else null
		while failure.is_empty():
			var value: Variant = _value(path + ["[]"], depth + 1)
			if not failure.is_empty(): return null
			if build: array.append(value)
			_space()
			if _take("]"): return array if build else null
			if not _take(","): return _fail("invalid_json", "Missing comma between array values.")
		return null

	func _string() -> Variant:
		var start := position
		position += 1
		while position < source.length():
			var code := source.unicode_at(position)
			position += 1
			if code == 34:
				return JSON.parse_string(source.substr(start, position - start))
			if code < 32: return _fail("invalid_json", "Unescaped control character in string.")
			if code != 92: continue
			if position >= source.length(): return _fail("invalid_json", "Truncated string escape.")
			var escape := source[position]
			position += 1
			if escape in ['"', "\\", "/", "b", "f", "n", "r", "t"]: continue
			if escape != "u": return _fail("invalid_json", "Unknown string escape.")
			var scalar := _hex4()
			if not failure.is_empty(): return null
			if scalar == 0: return _fail("invalid_json", "NUL codepoints are not supported by this text codec.")
			if scalar >= 0xd800 and scalar <= 0xdbff:
				if source.substr(position, 2) != "\\u": return _fail("invalid_json", "Unpaired high surrogate.")
				position += 2
				var low := _hex4()
				if not failure.is_empty(): return null
				if low < 0xdc00 or low > 0xdfff: return _fail("invalid_json", "Invalid surrogate pair.")
			elif scalar >= 0xdc00 and scalar <= 0xdfff:
				return _fail("invalid_json", "Unpaired low surrogate.")
		return _fail("invalid_json", "Unterminated string.")

	func _hex4() -> int:
		if position + 4 > source.length():
			_fail("invalid_json", "Truncated Unicode escape.")
			return 0
		var scalar := 0
		for index in 4:
			var digit := "0123456789abcdef".find(source[position].to_lower())
			if digit < 0:
				_fail("invalid_json", "Invalid Unicode escape.")
				return 0
			scalar = scalar * 16 + digit
			position += 1
		return scalar

	func _number(path: Array) -> Variant:
		var start := position
		_take("-")
		if not _take("0"):
			if not _digit(false): return _fail("invalid_json", "Invalid JSON number.")
			while _digit(true): pass
		if _take("."):
			if not _digit(true): return _fail("invalid_json", "Fraction requires digits.")
			while _digit(true): pass
		if _take("e") or _take("E"):
			if not _take("+"): _take("-")
			if not _digit(true): return _fail("invalid_json", "Exponent requires digits.")
			while _digit(true): pass
		if position - start > MAX_NUMBER_CHARS:
			return _fail("structure_limit", "Numeric token exceeds its character limit.")
		var token := source.substr(start, position - start)
		var integer: Variant = _exact_integer(token)
		var integer_field := path == ["version"] or path in [["inventory", "next_serial"], ["inventory", "revision"]]
		if path.size() == 5 and path[0] == "inventory" and path[1] == "instances" and path[3] == "properties" and path[4] in ["weight", "raw_proficiency"]:
			integer_field = true
		if integer != null: return integer
		if integer_field: return _fail("invalid_integer", "Integer field is fractional or outside the exact bound.")
		return _fail("unsupported_fractional_metadata", "Codec v1 supports only bounded exact integer metadata numbers.")

	func _digit(allow_zero: bool) -> bool:
		if position >= source.length(): return false
		var code := source.unicode_at(position)
		if code >= (48 if allow_zero else 49) and code <= 57:
			position += 1
			return true
		return false

	func _space() -> void:
		while position < source.length() and source[position] in [" ", "\t", "\r", "\n"]:
			position += 1

	func _take(character: String) -> bool:
		if position < source.length() and source[position] == character:
			position += 1
			return true
		return false

	func _fail(code: String, detail: String) -> Variant:
		if failure.is_empty():
			failure = {"ok": false, "error": code, "detail": detail, "offset": position}
		return null

	# Exact decimal integer normalization, before binary-float rounding can erase a
	# fractional part. Supports JSON integral forms such as 1.0, 10e-1, and -0.0.
	static func _exact_integer(token: String) -> Variant:
		var negative := token.begins_with("-")
		var magnitude := token.substr(1) if negative else token
		var parts := magnitude.to_lower().split("e")
		var mantissa: String = parts[0]
		var fraction := mantissa.length() - mantissa.find(".") - 1 if mantissa.contains(".") else 0
		var digits := mantissa.replace(".", "").trim_prefix("+")
		while digits.begins_with("0"):
			digits = digits.substr(1)
		if digits.is_empty():
			return 0
		var exponent := 0
		if parts.size() == 2:
			var exponent_text: String = parts[1]
			var exponent_digits := exponent_text.trim_prefix("-").trim_prefix("+")
			while exponent_digits.begins_with("0"):
				exponent_digits = exponent_digits.substr(1)
			if exponent_digits.length() > 5:
				return null
			exponent = exponent_text.to_int()
		var shift := exponent - fraction
		if shift < 0:
			if -shift >= digits.length():
				return null
			for index in range(digits.length() + shift, digits.length()):
				if digits[index] != "0":
					return null
			digits = digits.left(digits.length() + shift)
		else:
			if digits.length() + shift > 16:
				return null
			digits += "0".repeat(shift)
		if digits.length() > 16 or (digits.length() == 16 and digits.casecmp_to(str(Inventory.MAX_INTEGER)) > 0):
			return null
		var integer := digits.to_int()
		return -integer if negative else integer
