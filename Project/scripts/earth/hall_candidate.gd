extends RefCounted
## Frozen original identities; candidate geometry never defines suppression scope.
const Guard=preload("res://scripts/earth/asset_guard.gd")
const Ground=preload("res://scripts/earth/ground_candidate.gd")
const PACK="Map/Res/Building"
const SCOPE="res://data/earth/a13_hall_source_scope.json"
const SCOPE_SHA="4288603a7dfd0ccc90a3bebf71473aca47a0bd57c448d6c33480b3f8952ff59e"
const REGISTRATION_SHA="57072cc60ed9e33aa9afaeb0c7310733216e2884e0b042b043077551473e273c"
const EMPTY_ORDERS=[6132,7735]
static func read_json(path:String) -> Variant:
	if not FileAccess.file_exists(path):return null
	var p=JSON.new()
	return p.data if p.parse(FileAccess.get_file_as_string(path))==OK else null
static func scope(source:Dictionary) -> Dictionary:
	if FileAccess.get_sha256(SCOPE)!=SCOPE_SHA:return {}
	var trusted=read_json(SCOPE)
	if not trusted is Dictionary or not trusted.get("owners") is Array or trusted.owners.size()!=30:return {}
	if source.get("id")!="A13" or source.get("width")!=100 or source.get("height")!=100 or not source.get("cells") is Array or source.cells.size()!=10000:return {}
	var expected={}
	for item in trusted.owners:
		var order=int(item.stable_source_order)
		if not Ground.same_numbers(source.cells[order],item.source_cell):return {}
		expected[order]=item
	return expected
static func prepare(reg:Variant,source:Dictionary) -> Dictionary:
	var expected=scope(source)
	if expected.size()!=30 or not reg is Dictionary or not reg.get("owners") is Array or reg.owners.size()!=30:return {}
	var normal=[];var normal_expected={};var empty={};var seen={}
	for item in reg.owners:
		if not item is Dictionary or not Guard.integer(item.get("stable_source_order"),0,9999):return {}
		var order=int(item.stable_source_order)
		if not expected.has(order) or seen.has(order) or not item.get("empty") is bool:return {}
		seen[order]=true
		var identity=expected[order]
		for key in ["pack","key"]:
			if not item.get(key) is String or item[key]!=identity[key]:return {}
		for key in ["frame_index","layer","sort_y"]:
			if not Guard.integer(item.get(key),0,65535) or item[key]!=identity[key]:return {}
		for key in ["cell","source_cell"]:
			if not Ground.same_numbers(item.get(key),identity[key]):return {}
		if item.empty:
			if not order in EMPTY_ORDERS:return {}
			for key in ["texture","texture_size","texture_sha256","world_top_left","raw_rect"]:
				if not item.has(key) or item[key]!=null:return {}
			if not Guard.integer(item.get("visible_pixel_count"),0,0) or not Guard.integer(item.get("nonzero_rgba_pixel_count"),0,0):return {}
			empty[order]={"empty":true}
		else:
			if order in EMPTY_ORDERS:return {}
			normal.append(item);normal_expected[order]=identity
	var prepared=Guard.prepare_owners(normal,source,normal_expected)
	if prepared.size()!=28 or empty.size()!=2:return {}
	for order in prepared:prepared[order].empty=false
	prepared.merge(empty)
	return prepared
static func read_prepare(path:String,source:Dictionary) -> Dictionary:
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path)!=REGISTRATION_SHA:return {}
	return prepare(read_json(path),source)
