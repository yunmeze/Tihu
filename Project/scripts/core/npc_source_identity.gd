extends RefCounted
## Pure sidecar. Never adds fields to source or prepared NPC/map dictionaries.
const MAX_NPCS := 10000
const RECORD_KEYS := ["x", "y", "appearance", "direction", "name", "script"]

static func prepare(source: Dictionary, prepared: Dictionary, events: Array) -> Dictionary:
	if not source.get("id") is String or source.id.is_empty(): return fail("Missing source map identity")
	if not source.get("npcs") is Array or source.npcs.size()>MAX_NPCS: return fail("Invalid source NPC bank")
	var mapping: Array = []
	for i in source.npcs.size():
		if not record_valid(source.npcs[i]): return fail("Invalid source NPC record")
		mapping.append(i)
	for event in events:
		if not event is Dictionary: return fail("Invalid identity event")
		if event.get("kind") != "delnpc": continue
		if not integer(event.get("x")) or not integer(event.get("y")): return fail("Invalid identity deletion")
		var remaining: Array = []
		for source_index in mapping:
			var npc: Dictionary = source.npcs[source_index]
			if npc.x!=event.x or npc.y!=event.y: remaining.append(source_index)
		mapping=remaining
	var records: Array = source.npcs.duplicate(true)
	var stamp := {"map_id":source.id,"source_fingerprint":JSON.stringify(source).sha256_text(),"records_fingerprint":JSON.stringify(records).sha256_text()}
	var identity := {"map_id":source.id,"source_fingerprint":stamp.source_fingerprint,"source_records":records,"runtime_to_source":mapping}
	if not validate(identity,prepared,stamp): return fail("Prepared NPC bank differs from source/deletion mapping")
	freeze(identity)
	freeze(stamp)
	return {"ok":true,"identity":identity,"stamp":stamp,"error":""}

static func validate(identity: Variant, map: Variant, stamp: Variant) -> bool:
	if not identity is Dictionary or identity.size()!=4 or not stamp is Dictionary or stamp.size()!=3: return false
	if not map is Dictionary or not map.get("id") is String or not map.get("npcs") is Array: return false
	if not stamp.get("map_id") is String or not stamp.get("source_fingerprint") is String or not stamp.get("records_fingerprint") is String: return false
	if stamp.source_fingerprint.length()!=64 or stamp.records_fingerprint.length()!=64: return false
	if not identity.get("map_id") is String or not identity.get("source_fingerprint") is String:return false
	if identity.get("map_id")!=stamp.map_id or map.id!=stamp.map_id or identity.get("source_fingerprint")!=stamp.source_fingerprint: return false
	if not identity.get("source_records") is Array or not identity.get("runtime_to_source") is Array: return false
	var records: Array = identity.source_records
	var mapping: Array = identity.runtime_to_source
	if records.size()>MAX_NPCS or mapping.size()!=map.npcs.size() or mapping.size()>records.size(): return false
	for record in records:
		if not record_valid(record): return false
	if JSON.stringify(records).sha256_text()!=stamp.records_fingerprint: return false
	var previous := -1
	for i in mapping.size():
		var index: Variant = mapping[i]
		if typeof(index)!=TYPE_INT or index<=previous or index>=records.size(): return false
		if not record_valid(map.npcs[i]) or map.npcs[i]!=records[index]: return false
		previous=index
	return true

static func resolve(identity: Variant, map: Variant, stamp: Variant, runtime_index: int) -> Dictionary:
	if not validate(identity,map,stamp): return fail("NPC identity sidecar is absent or stale")
	if runtime_index<0 or runtime_index>=identity.runtime_to_source.size(): return fail("NPC runtime index is outside the current map")
	return {"ok":true,"source_index":identity.runtime_to_source[runtime_index],"error":""}

static func record_valid(record: Variant) -> bool:
	if not record is Dictionary or record.size()!=RECORD_KEYS.size(): return false
	for key in ["x","y","appearance","direction"]:
		if not integer(record.get(key)): return false
	return record.get("name") is String and record.get("script") is String

static func integer(value: Variant) -> bool:
	return (typeof(value)==TYPE_INT or typeof(value)==TYPE_FLOAT) and is_finite(float(value)) and float(value)==floor(float(value)) and value>=-32768 and value<=32767

static func freeze(value: Variant) -> void:
	if value is Array:
		for child in value: freeze(child)
		value.make_read_only()
	elif value is Dictionary:
		for child in value.values(): freeze(child)
		value.make_read_only()

static func fail(message: String) -> Dictionary:
	return {"ok":false,"error":message}
