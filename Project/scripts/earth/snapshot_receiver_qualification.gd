extends RefCounted
const CONTRACT="res://assets/earth/snapshot_opening/receiver_contract.json"
const CONTRACT_SHA="0292fcd96402ec0b26cd4b2d6d99cd069aa7e77a973e434f39fa6f15e1ce3534"
const RUNTIME_REGISTRATION="res://assets/earth/snapshot_opening/snapshot_runtime_registration.json"
const RUNTIME_REGISTRATION_SHA="f88a085b5abe779a9ad3097f3dec3778037045a85cfb0c754a348653af90bdfd"
const ExactCache=preload("res://scripts/earth/snapshot_exact_cache.gd")
var static_cache=ExactCache.new()
var static_verdicts:Dictionary={}
var _scope_fast=false
func snapshot_payload(map:Dictionary,objects:Array) -> Dictionary:
	return {"map":map,"objects":objects,"source":source,"contracts":contracts}
func prepare_snapshot(map:Dictionary,objects:Array) -> bool:
	static_cache.clear();static_verdicts={}
	var context=build_context(map,objects)
	if not context.error.is_empty():return false
	for name in contracts:static_verdicts[name]=static_allows(name,map,context)
	static_verdicts.make_read_only()
	return static_cache.capture(snapshot_payload(map,objects))
var source:Dictionary={}
var contracts:Dictionary={}
var resource_ok:Dictionary={}
var reasons:Dictionary={}
func prepare() -> bool:
	static_cache.clear();static_verdicts={}
	if not runtime_declaration_valid():
		for name in contracts:resource_ok[name]=false
		return false
	if FileAccess.get_sha256(CONTRACT)!=CONTRACT_SHA:return false
	contracts=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	source=JSON.parse_string(FileAccess.get_file_as_string("res://data/maps/A13.json"))
	revalidate_resources()
	return true
func revalidate_resources() -> void:
	if not runtime_declaration_valid():
		for name in contracts:resource_ok[name]=false
		return
	if FileAccess.get_sha256(CONTRACT)!=CONTRACT_SHA:
		for name in contracts:resource_ok[name]=false
		return
	for name in contracts:
		resource_ok[name]=true
		for path in contracts[name].pins:
			if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=contracts[name].pins[path]:resource_ok[name]=false;break
func reject(name:String,reason:String) -> bool:
	reasons[name]=reason;return false
# Scope exists only during one synchronous snapshot_world.refresh; never survives it.
var _scope_active=false
var _scope_map:Dictionary={}
var _scope_objects:Array=[]
var _scope_context:Dictionary={}
func begin_refresh_scope(map:Dictionary,objects:Array) -> void:
	end_refresh_scope()
	_scope_fast=static_cache.matches(snapshot_payload(map,objects))
	_scope_context={} if _scope_fast else build_context(map,objects)
	_scope_map=map;_scope_objects=objects;_scope_active=true
func end_refresh_scope() -> void:
	_scope_active=false;_scope_fast=false;_scope_context={};_scope_map={};_scope_objects=[]
func build_context(map:Dictionary,objects:Array) -> Dictionary:
	for key in ["id","width","height","sourceSha256"]:
		if map.get(key)!=source.get(key):return {"error":"map identity"}
	if not map.get("cells") is Array or map.cells.size()!=10000:return {"error":"cells structure"}
	for i in 10000:
		var a=map.cells[i];var b=source.cells[i]
		if not a is Array or a.size()!=4 or a[0]!=b[0] or a[2]!=b[2] or a[3]!=b[3]:return {"error":"unknown changed geometry"}
	var groups={1:"Map/Res/Debris",2:"Map/Res/Plant",3:"Map/Res/Wall",4:"Map/Res/Building",5:"Map/Res/Dynamic",8:"Data4"}
	var by_order={}
	for entry in objects:
		if not entry is Dictionary:return {"error":"actual entry structure"}
		var order=entry.get("order",-1)
		if groups.has(int(entry.get("kind",-1))):
			if not order is int or order<0 or order>=10000:return {"error":"unbound static entry"}
			var source_cell=source.cells[order]
			if entry.get("kind")!=int(source_cell[2]) or entry.get("pack")!=groups.get(int(source_cell[2]),"") or entry.get("index")!=int(source_cell[3]) or entry.get("origin")!=Vector2(int(order/100)*48,(order%100)*32):return {"error":"unknown actual static geometry"}
		elif entry.get("kind")==7:
			var npc_index=int(order)-10000
			if npc_index<0 or npc_index>=map.npcs.size():return {"error":"unbound actual NPC entry"}
			var npc=map.npcs[npc_index]
			if entry.get("origin")!=Vector2(npc.x*48,npc.y*32) or entry.get("index")!=1+int(npc.appearance)*12+int(npc.direction)*4:return {"error":"actual NPC differs"}
		elif entry.get("kind")==9:
			if map.get("added_units",[]).size()!=1 or entry.get("pack")!="Mon/220" or entry.get("index")!=1 or entry.get("origin")!=Vector2(49*48,53*32):return {"error":"unknown actual unit geometry"}
		else:return {"error":"unknown actual entry"}
		if not by_order.has(order):by_order[order]=[]
		by_order[order].append(entry.duplicate(true))
	var npc_seen={}
	for npc in map.npcs:
		var key=str(npc.x)+","+str(npc.y)
		if npc not in source.npcs or npc_seen.has(key):return {"error":"unknown/duplicate NPC"}
		npc_seen[key]=true
	var units=map.get("added_units",[])
	if units.size()>1:return {"error":"unknown added units"}
	for unit in units:
		if unit!={"x":49,"y":53,"name":"彩蛋鸡","definition_id":508,"texture_manifest":"res://assets/original/monsters/a13-chicken/manifest.json","runtime_behavior":"entity_record_only"}:return {"error":"unknown added unit bounds"}
	for entries in by_order.values():
		for entry in entries:entry.make_read_only()
		entries.make_read_only()
	by_order.make_read_only()
	return {"error":"","by_order":by_order}
func allows(name:String,map:Dictionary,objects:Array) -> bool:
	if not contracts.has(name) or not resource_ok.get(name,false):return reject(name,"contract/source/legacy resource SHA")
	var in_scope=_scope_active and is_same(map,_scope_map) and is_same(objects,_scope_objects)
	var exact=_scope_fast if in_scope else static_cache.matches(snapshot_payload(map,objects))
	if exact:
		reasons[name]="exact type-sensitive snapshot; dynamic original gates still required"
		return static_verdicts.get(name,false)
	var context=_scope_context if in_scope else build_context(map,objects)
	return static_allows(name,map,context)
func static_allows(name:String,map:Dictionary,context:Dictionary) -> bool:
	if not context.error.is_empty():return reject(name,context.error)
	var c=contracts[name]
	for order in c.cell_orders:
		if map.cells[int(order)]!=source.cells[int(order)]:return reject(name,"local receiver/caster owner cell")
	var expected={}
	var groups={1:"Map/Res/Debris",2:"Map/Res/Plant",3:"Map/Res/Wall",4:"Map/Res/Building",5:"Map/Res/Dynamic",8:"Data4"}
	for value in c.cell_orders:
		var order=int(value);var cell=source.cells[order]
		if cell[3]>0 and groups.has(int(cell[2])):
			expected[order]={"pack":groups[int(cell[2])],"index":int(cell[3]),"kind":int(cell[2]),"layer":0 if int(cell[1]) in [1,-2] else (2 if int(cell[1])==2 else 1),"y":float(order%100),"origin":Vector2(int(order/100)*48,(order%100)*32),"order":order}
	for order in expected:
		var actual=context.by_order.get(order,[])
		if actual.size()!=1 or actual[0]!=expected[order]:return reject(name,"actual owner stream missing/duplicate/different")
	if c.caster.has("npc"):
		var pos=c.caster.npc
		var wanted=source.npcs.filter(func(n):return n.x==pos[0] and n.y==pos[1])
		var found=map.npcs.filter(func(n):return n.x==pos[0] and n.y==pos[1])
		if wanted!=found:return reject(name,"caster NPC missing/changed")
	reasons[name]="local invariant; AND original runtime gates";return true

func runtime_declaration_valid() -> bool:
	if FileAccess.get_sha256(RUNTIME_REGISTRATION)!=RUNTIME_REGISTRATION_SHA:return false
	var document=JSON.parse_string(FileAccess.get_file_as_string(RUNTIME_REGISTRATION))
	if not document is Dictionary or document.get("schema")!="earth-runtime-files-v1" or not document.get("runtime_files") is Array:return false
	var declared={}
	for item in document.runtime_files:
		if not item is Dictionary or not item.get("path") is String or declared.has(item.path):return false
		declared[item.path]=item
	if not declared.has(CONTRACT):return false
	var root=declared[CONTRACT]
	if root.get("role")!="registration" or root.get("type")!="json" or root.get("sha256")!=CONTRACT_SHA:return false
	if not FileAccess.file_exists(CONTRACT) or FileAccess.get_file_as_bytes(CONTRACT).size()!=root.get("bytes") or FileAccess.get_sha256(CONTRACT)!=CONTRACT_SHA:return false
	var receiver=JSON.parse_string(FileAccess.get_file_as_string(CONTRACT))
	if not receiver is Dictionary:return false
	for caster in receiver.values():
		if not caster is Dictionary or not caster.get("pins") is Dictionary:return false
		for path in caster.pins:
			if path=="res://tools/earth/build_flat_shadow_gate.py":continue # Exact SHA remains in frozen CONTRACT and revalidate_resources; explicit export adapter leaf.
			if not declared.has(path) or declared[path].get("sha256")!=caster.pins[path]:return false
	return true
