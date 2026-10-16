extends RefCounted
## Pure, detached source-map event preparation. Caller owns one atomic publication.
const NpcIdentity = preload("res://scripts/core/npc_source_identity.gd")
const VM = preload("res://scripts/core/dialogue_vm.gd")
const MAX_JSON_NODES := 2000000 # Four-map source JSON includes all cells and byte offsets.
const MAX_JSON_DEPTH := 32
const MAX_JSON_TEXT := 8388608
const EVENT_KEYS := {"stop":["kind"],"unstop":["kind"],"move":["kind","x","y"],"delnpc":["kind","x","y"],"setmapflag":["kind","x","y","flag"],"addmon":["kind","x","y","name"]}
const MAX_ADDED_UNITS := 512 # Bounded adapter safety limit, not original game capacity.

static func prepare(source_map: Dictionary, story: Dictionary, actor: Dictionary, context: Dictionary, registry: Dictionary = {}, resource_preflight: Callable = Callable(), bind_npc_identity: bool = false) -> Dictionary:
	if not json_safe(source_map): return fail("Source map is not bounded acyclic JSON")
	var result := VM.execute(source_map.get("loadScript",""),story,"START",2048,context)
	if not result.ok: return fail("Script: "+str(result.error))
	return prepare_events(source_map,actor,result,registry,resource_preflight,bind_npc_identity)

static func prepare_events(source_map: Dictionary, actor: Dictionary, result: Dictionary, registry: Dictionary = {}, resource_preflight: Callable = Callable(), bind_npc_identity: bool = false) -> Dictionary:
	for input in [source_map,actor,result,registry]:
		if not json_safe(input): return fail("Input is not bounded acyclic JSON")
	if not exact_keys(actor,["cell","stopped","random_cursor"]): return fail("Unexpected actor fields")
	if typeof(result.get("ok"))!=TYPE_BOOL or not result.ok: return fail("Unsuccessful VM candidate")
	if not integer(source_map.get("width"),1,4096) or not integer(source_map.get("height"),1,4096): return fail("Invalid map dimensions")
	if not result.get("state") is Dictionary or not VM.execute("#end",result.state).ok: return fail("Invalid staged story")
	if not result.get("silent") is bool: return fail("Invalid silent result")
	var width := int(source_map.width)
	var height := int(source_map.height)
	if not source_map.get("cells") is Array or source_map.cells.size()!=width*height: return fail("Invalid map cells")
	for cell in source_map.cells:
		if not cell is Array or cell.size()!=4: return fail("Invalid cell shape")
		for field in cell:
			if not integer(field,-32768,32767): return fail("Invalid cell value")
	for bank in ["npcs","spawns"]:
		if not source_map.get(bank) is Array: return fail("Invalid entity bank")
		for entry in source_map[bank]:
			if not entry is Dictionary or not coordinates(entry,width,height): return fail("Invalid source entity")
	if not actor.get("cell") is Array or actor.cell.size()!=2 or not coordinates({"x":actor.cell[0],"y":actor.cell[1]},width,height): return fail("Invalid actor cell")
	if not actor.get("stopped") is bool or not integer(actor.get("random_cursor"),0,2147483647): return fail("Invalid actor control state")
	if not result.get("events") is Array or not integer(result.get("random_consumed"),0,65536): return fail("Invalid result")
	if int(actor.random_cursor)+int(result.random_consumed)>2147483647: return fail("Random cursor overflow")
	if not source_map.get("added_units",[]) is Array: return fail("Invalid added-unit bank")
	if source_map.get("added_units",[]).size()>MAX_ADDED_UNITS: return fail("Added-unit adapter capacity exceeded")
	for unit in source_map.get("added_units",[]):
		if not unit is Dictionary or not coordinates(unit,width,height): return fail("Invalid added unit")
	var prepared_map := source_map.duplicate(true)
	prepared_map.added_units=source_map.get("added_units",[]).duplicate(true)
	var prepared_actor := actor.duplicate(true)
	var registrations := {}
	# Whole event list is checked before even staging any effect.
	for event in result.events:
		if not event is Dictionary or not event.get("kind") is String: return fail("Malformed event")
		if not EVENT_KEYS.has(event.kind) or not exact_keys(event,EVENT_KEYS[event.kind]): return fail("Unexpected event shape")
		if event.kind in ["stop","unstop"]: continue
		if event.kind not in ["move","delnpc","setmapflag","addmon"]: return fail("Unsupported map event: "+event.kind)
		if not coordinates(event,width,height): return fail("Event coordinate outside map")
		if event.kind=="setmapflag" and not integer(event.get("flag"),0,2): return fail("Invalid map flag")
		if event.kind=="addmon":
			if not event.get("name") is String or not registry.has(event.name): return fail("Unregistered monster")
			if not registry[event.name] is Dictionary: return fail("Invalid monster registration")
			var definition: Dictionary=registry[event.name]
			if typeof(definition.get("name"))!=TYPE_STRING or definition.name!=event.name or not integer(definition.get("definition_id"),0,32767) or not definition.get("texture_manifest") is String: return fail("Invalid monster registration")
			if not definition.texture_manifest.begins_with("res://") or not definition.texture_manifest.ends_with(".json"): return fail("Invalid monster manifest path")
			if not registrations.has(event.name):
				if not resource_preflight.is_valid(): return fail("Monster resource preflight absent")
				var checked: Variant=resource_preflight.call(definition.duplicate(true))
				if typeof(checked)!=TYPE_BOOL or not checked: return fail("Monster resource preflight failed")
				registrations[event.name]=definition
	# Reference application orders all flag edits before remaining world effects.
	for event in result.events:
		if event.kind!="setmapflag": continue
		var cell: Array=prepared_map.cells[int(event.x)*height+int(event.y)]
		if event.flag==0:
			cell[1]=0
			if cell[2]==8:
				cell[2]=0
				cell[3]=0
		elif cell[1]==0:
			cell[1]=-1
			if event.flag==2:
				cell[2]=8
				cell[3]=1
	for event in result.events:
		match event.kind:
			"stop": prepared_actor.stopped=true
			"unstop": prepared_actor.stopped=false
			"move":
				if blocked(prepared_map,event.x,event.y): return fail("MOVE destination blocked")
				prepared_actor.cell=[int(event.x),int(event.y)]
			"delnpc":
				for bank in ["npcs","spawns","added_units"]:
					var remaining: Array=[]
					for entity in prepared_map[bank]:
						if entity.x!=event.x or entity.y!=event.y: remaining.append(entity)
					prepared_map[bank]=remaining
			"addmon":
				if blocked(prepared_map,event.x,event.y): return fail("ADDMON destination blocked")
				if prepared_map.added_units.size()>=MAX_ADDED_UNITS: return fail("Added-unit adapter capacity exceeded")
				var definition: Dictionary=registrations[event.name]
				prepared_map.added_units.append({"x":int(event.x),"y":int(event.y),"name":event.name,"definition_id":int(definition.definition_id),"texture_manifest":definition.texture_manifest,"runtime_behavior":"entity_record_only"})
	prepared_actor.random_cursor=int(actor.random_cursor)+int(result.random_consumed)
	var output := {"ok":true,"map":prepared_map,"story":result.state.duplicate(true),"actor":prepared_actor,"silent":result.silent,"events":result.events.duplicate(true),"error":""}
	if bind_npc_identity:
		var identity := NpcIdentity.prepare(source_map,prepared_map,result.events)
		if not identity.ok: return fail(identity.error)
		output.npc_identity=identity.identity
		output.npc_source_stamp=identity.stamp
	return output

static func integer(value: Variant, low: int, high: int) -> bool:
	return (typeof(value)==TYPE_INT or typeof(value)==TYPE_FLOAT) and is_finite(float(value)) and float(value)==floor(float(value)) and value>=low and value<=high

static func coordinates(value: Dictionary,width: int,height: int) -> bool:
	return integer(value.get("x"),0,width-1) and integer(value.get("y"),0,height-1)

static func blocked(map: Dictionary,x: int,y: int) -> bool:
	return int(map.cells[x*int(map.height)+y][1]) in [-1,-2,-3]

static func fail(message: String) -> Dictionary:
	return {"ok":false,"map":null,"story":null,"actor":null,"events":[],"silent":false,"error":message}

# Validate before *any* duplicate(true), including unused metadata. Ancestor identity
# catches cycles without engine recursion; shared acyclic containers remain legal.
static func json_safe(value: Variant) -> bool:
	return _json_safe(value,[],[0,0],0)

static func _json_safe(value: Variant, ancestors: Array, count: Array, depth: int) -> bool:
	count[0]+=1
	if count[0]>MAX_JSON_NODES or depth>MAX_JSON_DEPTH: return false
	match typeof(value):
		TYPE_NIL,TYPE_BOOL,TYPE_INT: return true
		TYPE_FLOAT: return is_finite(value)
		TYPE_STRING:
			count[1]+=value.length()
			return count[1]<=MAX_JSON_TEXT
		TYPE_ARRAY,TYPE_DICTIONARY:
			for parent in ancestors:
				if is_same(value,parent): return false
			ancestors.append(value)
			if value is Dictionary:
				for key in value:
					if typeof(key) not in [TYPE_STRING,TYPE_STRING_NAME]:
						ancestors.pop_back()
						return false
					count[1]+=key.length()
					if count[1]>MAX_JSON_TEXT or not _json_safe(value[key],ancestors,count,depth+1):
						ancestors.pop_back()
						return false
			else:
				for item in value:
					if not _json_safe(item,ancestors,count,depth+1):
						ancestors.pop_back()
						return false
			ancestors.pop_back()
			return true
		_: return false

static func exact_keys(value: Dictionary, keys: Array) -> bool:
	if value.size()!=keys.size(): return false
	for key in keys:
		if not value.has(key): return false
	return true
