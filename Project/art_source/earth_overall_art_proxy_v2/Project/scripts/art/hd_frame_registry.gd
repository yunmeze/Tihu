extends RefCounted
## Opt-in 2D full-source-canvas replacements. No movement, ticks, sorting or shadows.
## The entire manifest publishes atomically. Any invalid group restores source art.
var entries: Dictionary = {}
var errors: Array[String] = []
var map_id := ""
var world_instance_id: int = 0
var owner_index: Dictionary = {}
var texture_cache: Dictionary = {}

func clear() -> void:
	entries.clear()
	errors.clear()
	map_id = ""
	world_instance_id = 0
	owner_index.clear()
	texture_cache.clear()

func key(pack: String, index: int, cell: Vector2i, offset: bool) -> String:
	return "%s|%d|%d,%d|%s" % [pack,index,cell.x,cell.y,str(offset)]

func prepare(world, manifest_path: String) -> bool:
	clear()
	if not FileAccess.file_exists(manifest_path):
		errors.append("Missing HD manifest")
		return false
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
	if not parsed is Dictionary or parsed.get("schema") != "hd-frame-registry-v1":
		errors.append("Invalid HD manifest schema")
		return false
	if not parsed.get("source_map") is String: return false
	var path: String = parsed.source_map
	if not path.begins_with("res://data/maps/") or not FileAccess.file_exists(path): return false
	if FileAccess.get_sha256(path) != parsed.get("source_map_sha256", ""): return false
	var source = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not source is Dictionary: return false
	for field in ["id", "width", "height", "npcs", "texture_manifest"]:
		if source.get(field) != world.map.get(field):
			errors.append("Source map mismatch: " + field)
			return false
	if not _same_art_cells(source,world.map):
		errors.append("Source cell art mismatch")
		return false
	if not parsed.get("groups") is Array: return false
	map_id = str(world.map.id)
	world_instance_id = world.get_instance_id()
	for stream in ["floor", "object"]:
		var owners: Array = world.floors if stream == "floor" else world.objects
		for owner in owners:
			var owner_key: String = stream+"|"+key(str(owner.pack),0,Vector2i(roundi(owner.origin.x/48),roundi(owner.origin.y/32)),false)
			if not owner_index.has(owner_key): owner_index[owner_key] = []
			owner_index[owner_key].append(owner)
	for group in parsed.groups:
		var staged: Dictionary = _prepare_group(world, group)
		if staged.is_empty():
			errors.append("Rejected group: " + str(group.get("id", "unnamed") if group is Dictionary else "invalid"))
			continue
		var duplicate := false
		for k in staged:
			if entries.has(k): duplicate = true
		if duplicate:
			errors.append("Duplicate owner group")
			continue
		entries.merge(staged)
	if not errors.is_empty(): entries.clear()
	return errors.is_empty()

func _prepare_group(world, group: Variant) -> Dictionary:
	if not group is Dictionary: return {}
	var cell = group.get("cell")
	if not cell is Array or cell.size() != 2: return {}
	if not _integer(cell[0]) or not _integer(cell[1]): return {}
	if not group.get("pack") is String: return {}
	var pack: String = group.pack
	if not world.packs.has(pack): return {}
	if group.get("stream") not in ["floor", "object"]: return {}
	var owner_key: String = str(group.stream)+"|"+key(pack,0,Vector2i(cell[0],cell[1]),false)
	var found: Array = owner_index.get(owner_key,[])
	if found.size() != 1: return {}
	var owner: Dictionary = found[0]
	var kind: int = int(owner.get("kind", 0))
	var offset := kind == 7
	var expected: Array = []
	if kind == 7:
		for i in 4: expected.append(int(owner.index)+i)
	elif kind == 5:
		for i in 5: expected.append(int(owner.index)+i)
	elif kind == 8:
		for i in 5: expected.append(55+i)
	else: expected.append(int(owner.index))
	var frames = group.get("frames")
	if not frames is Array or frames.size() != expected.size(): return {}
	var staged: Dictionary = {}
	for i in expected.size():
		var record = frames[i]
		if not record is Dictionary or record.get("index") != expected[i]: return {}
		var frame: Dictionary = world.packs[pack].frames.get(str(expected[i]), {})
		if frame.is_empty() or record.get("source_frame") != frame: return {}
		if not record.get("texture") is String: return {}
		var texture_path: String = record.texture
		if not texture_path.begins_with("res://assets/earth/") or not FileAccess.file_exists(texture_path): return {}
		if not record.get("texture_sha256") is String: return {}
		var cache_key: String = texture_path+"|"+record.texture_sha256
		if not texture_cache.has(cache_key):
			if FileAccess.get_sha256(texture_path) != record.texture_sha256: return {}
			if not ResourceLoader.exists(texture_path): return {}
			var loaded = load(texture_path)
			if not loaded is Texture2D: return {}
			var wrapper := CanvasTexture.new()
			wrapper.diffuse_texture = loaded
			wrapper.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
			texture_cache[cache_key] = {"raw":loaded,"canvas":wrapper}
		var texture: Texture2D = texture_cache[cache_key].raw
		# Native generated atlas regions may have fractional pixel density; never upscale.
		var logical_size := Vector2(frame.original[0], frame.original[1])
		var region := Rect2(Vector2.ZERO, texture.get_size())
		if record.has("region_px"):
			var r = record.region_px
			if not r is Array or r.size() != 4: return {}
			for value in r:
				if not _number(value): return {}
			region = Rect2(float(r[0]),float(r[1]),float(r[2]),float(r[3]))
			if region.size.x <= 0 or region.size.y <= 0: return {}
			if not Rect2(Vector2.ZERO, texture.get_size()).grow(0.01).encloses(region): return {}
			region = region.intersection(Rect2(Vector2.ZERO, texture.get_size()))
		else:
			var density = record.get("density")
			if not _number(density) or density <= 1 or density > 32: return {}
			if texture.get_size() != logical_size*float(density): return {}
		var actual_density := region.size/logical_size
		if actual_density.x <= 1 or actual_density.y <= 1: return {}
		# Keep source aspect; allow only small native-output rounding differences.
		if absf(actual_density.x/actual_density.y-1.0) > 0.03: return {}
		var canvas: CanvasTexture = texture_cache[cache_key].canvas
		var top := 0.0 if offset or group.stream == "floor" else (-52.0 if kind == 8 else 32.0-logical_size.y)
		var draw_offset := Vector2(0, top)
		if offset: draw_offset += Vector2(frame.offset[0], frame.offset[1])
		# Optional whole-frame rigid image registration; source offsets stay unchanged.
		if record.has("alignment_logical"):
			var alignment = record.alignment_logical
			if pack != "Npc" or not offset: return {}
			if not alignment is Array or alignment.size() != 2: return {}
			for value in alignment:
				if not _number(value) or absf(float(value)) > 8: return {}
			draw_offset += Vector2(float(alignment[0]),float(alignment[1]))
		staged[key(pack,expected[i],Vector2i(cell[0],cell[1]),offset)] = {
			"texture":canvas,"size":logical_size,"region":region,"offset":draw_offset,"top":top,"source":frame.duplicate(true)}
	return staged

func try_draw(canvas: CanvasItem, world, pack: String, index: int, origin: Vector2, use_offset: bool, top: float) -> bool:
	if entries.is_empty() or str(world.map.get("id", "")) != map_id or world.get_instance_id() != world_instance_id: return false
	var grid: Vector2 = (origin-world.screen_origin())/Vector2(48,32)
	var cell := Vector2i(roundi(grid.x),roundi(grid.y))
	if grid.distance_to(Vector2(cell)) > 0.001: return false
	var entry: Dictionary = entries.get(key(pack,index,cell,use_offset), {})
	if entry.is_empty() or top != entry.top: return false
	if world.packs.get(pack, {}).get("frames", {}).get(str(index)) != entry.source: return false
	var destination := Rect2(origin+entry.offset,entry.size)
	if destination.intersects(canvas.get_viewport_rect()): canvas.draw_texture_rect_region(entry.texture,destination,entry.region,Color.WHITE,false,false)
	return true

static func _integer(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floorf(float(value))

static func _number(value: Variant) -> bool:
	return (value is int or value is float) and is_finite(float(value))

# Original A00 A5 opens exactly nine gate flags; keep all art fields immutable.
# Gameplay authorization remains exclusively in the existing Trial/Bridge gates.
static func _same_art_cells(source: Dictionary, current: Dictionary) -> bool:
	if not source.get("cells") is Array or not current.get("cells") is Array: return false
	if source.cells.size() != current.cells.size(): return false
	var north := [[37,55],[37,56],[38,56],[38,57],[39,57],[39,58],[40,58],[40,59],[41,59]]
	var allowed: Dictionary = {}
	if source.get("id") == "A00":
		for cell in north: allowed[int(cell[0])*int(source.height)+int(cell[1])] = true
	for i in source.cells.size():
		var a = source.cells[i]
		var b = current.cells[i]
		if not a is Array or not b is Array or a.size() != 4 or b.size() != 4: return false
		if a[0] != b[0] or a[2] != b[2] or a[3] != b[3]: return false
		if a[1] != b[1] and not (allowed.has(i) and a[1] == -1 and b[1] == 0): return false
	return true
