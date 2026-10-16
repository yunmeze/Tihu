extends RefCounted
## Native deep equality plus every stricter type predicate in the static receiver proof.
## Captured independent containers are recursively read-only. No Resource/Object baseline.
var baseline:Dictionary={}
var baseline_bytes=PackedByteArray()
var ready=false
func clear() -> void:
	ready=false;baseline={};baseline_bytes=PackedByteArray()
func capture(payload:Dictionary) -> bool:
	clear()
	if not safe_value(payload,[],0):return false
	baseline=payload.duplicate(true)
	freeze(baseline)
	baseline_bytes=var_to_bytes(baseline)
	ready=not baseline_bytes.is_empty()
	return ready
func matches(payload:Dictionary) -> bool:
	if not ready:return false
	# Compare complete independent containers first, including map/flags/stream order/atlas.
	if payload!=baseline:return false
	if not payload.has("objects"):
		# Generic unit-test payloads retain full type-sensitive byte semantics.
		return var_to_bytes(payload)==baseline_bytes
	# Native numeric equality is loose. The old receiver validator additionally
	# requires static owner.order to be a native int; preserve that strict gate.
	# All other proof comparisons use the same native equality / integer conversion.
	for entry in payload.objects:
		if not entry is Dictionary:return false
		if int(entry.get("kind",-1)) in [1,2,3,4,5,8] and not entry.get("order") is int:return false
	return true
func safe_value(value:Variant,ancestors:Array,depth:int) -> bool:
	if depth>64:return false
	match typeof(value):
		TYPE_NIL,TYPE_BOOL,TYPE_INT,TYPE_STRING,TYPE_STRING_NAME,TYPE_VECTOR2,TYPE_VECTOR2I:return true
		TYPE_FLOAT:return is_finite(value)
		TYPE_ARRAY,TYPE_DICTIONARY:
			for ancestor in ancestors:
				if is_same(value,ancestor):return false
			var next=ancestors.duplicate();next.append(value)
			if value is Dictionary:
				for key in value:
					if not safe_value(key,next,depth+1) or not safe_value(value[key],next,depth+1):return false
			else:
				for item in value:
					if not safe_value(item,next,depth+1):return false
			return true
		_:return false
func freeze(value:Variant) -> void:
	if value is Dictionary:
		for item in value.values():freeze(item)
		value.make_read_only()
	elif value is Array:
		for item in value:freeze(item)
		value.make_read_only()
