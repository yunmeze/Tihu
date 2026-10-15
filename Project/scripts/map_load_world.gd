extends "res://scripts/world_view.gd"
# Independent adapter for the prevalidated, detached map snapshot.
var snapshot: Dictionary = {}
func read_json(path: String) -> Dictionary:
	if path=="res://__map_load_snapshot__": return snapshot
	return super.read_json(path)
func setup_snapshot(actor: RefCounted, candidate: Dictionary) -> bool:
	snapshot=candidate
	if not setup(actor,"res://__map_load_snapshot__"): return false
	for unit in map.get("added_units",[]):
		var manifest := read_json(unit.texture_manifest)
		if not manifest.get("packs") is Dictionary: return false
		if int(unit.definition_id)!=508 or not manifest.packs.has("Mon/220") or not manifest.packs["Mon/220"].frames.has("1"):
			loading_errors.append("Unsupported display adapter or missing chicken frame1")
			return false
		for name in manifest.packs:
			packs[name]=manifest.packs[name]
			for page in packs[name].pages: _load_texture(page.file)
		# Explicit display adapter: static source N idle frame1, reference alive layer1.
		objects.append({"pack":"Mon/220","index":1,"kind":9,"layer":1,"y":float(unit.y),"origin":Vector2(unit.x*48,unit.y*32),"order":int(map.width)*int(map.height)+map.npcs.size()+objects.size()})
	initialized=loading_errors.is_empty()
	return initialized
func _draw_frame(pack_name: String,index: int,origin: Vector2,use_offset: bool,top: float) -> void:
	if pack_name.begins_with("Mon/"):
		super._draw_frame(pack_name,index,origin,true,0)
	else:
		super._draw_frame(pack_name,index,origin,use_offset,top)
