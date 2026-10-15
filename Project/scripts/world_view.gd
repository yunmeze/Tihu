extends Node2D
const GROUPS := {1:"Map/Res/Debris",2:"Map/Res/Plant",3:"Map/Res/Wall",4:"Map/Res/Building",5:"Map/Res/Dynamic",8:"Data4"}
var map: Dictionary
var packs: Dictionary
var hero: Dictionary
var textures: Dictionary = {}
var floors: Array = []
var objects: Array = []
var movement: RefCounted
var tick := 0
var camera := Vector2(61,39)
var show_grid := false
var initialized := false
var loading_errors: Array[String] = []

func read_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		loading_errors.append("Missing " + path)
		return {}
	var value = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not value is Dictionary:
		loading_errors.append("Invalid JSON " + path)
		return {}
	return value

func setup(actor: RefCounted, map_path: String = "res://data/maps/A13.json") -> bool:
	initialized = false
	loading_errors.clear()
	floors.clear()
	objects.clear()
	textures.clear()
	movement = actor
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	map = read_json(map_path)
	packs = read_json(map.get("texture_manifest","res://assets/original/manifest.json")).get("packs",{})
	hero = read_json("res://data/hero/movement.json")
	if map.is_empty() or packs.is_empty() or hero.is_empty(): return false
	for pack in packs.values():
		for page in pack.pages: _load_texture(page.file)
	for layer in hero.layers.values(): _load_texture(layer.atlas)
	if not loading_errors.is_empty(): return false
	var h := int(map.height)
	var flags: Array = []
	for cell in map.cells: flags.append(cell[1])
	movement.configure(int(map.width),h,flags)
	for x in int(map.width):
		for y in h:
			var c: Array = map.cells[x*h+y]
			var floor_id := int(c[0])
			if floor_id != 0:
				floors.append({"pack":"Map/Res/FloorBig" if floor_id<0 else "Map/Res/FloorSmall","index":absi(floor_id),"origin":Vector2(x*48,y*32)})
			var kind := int(c[2])
			if int(c[3])>0 and GROUPS.has(kind):
				objects.append({"pack":GROUPS[kind],"index":int(c[3]),"kind":kind,"layer":layer_for_flag(int(c[1])),"y":float(y),"origin":Vector2(x*48,y*32),"order":x*h+y})
	for i in map.npcs.size():
		var n: Dictionary = map.npcs[i]
		objects.append({"pack":"Npc","index":1+int(n.appearance)*12+int(n.direction)*4,"kind":7,"layer":1,"y":float(n.y),"origin":Vector2(float(n.x)*48,float(n.y)*32),"order":int(map.width)*h+i})
	initialized = true
	queue_redraw()
	return true

func _load_texture(path: String) -> void:
	if textures.has(path): return
	if not ResourceLoader.exists(path):
		loading_errors.append("Not imported " + path)
		return
	var resource = load(path)
	if not resource is Texture2D:
		loading_errors.append("Not a Texture2D " + path)
		return
	textures[path] = resource

static func layer_for_flag(flag: int) -> int:
	if flag in [1,-2]: return 0
	if flag == 2: return 2
	return 1

func screen_origin() -> Vector2:
	return get_viewport_rect().size*Vector2(0.5,0.54)-camera*Vector2(48,32)

func to_cell(screen: Vector2) -> Vector2i:
	var p := (screen-screen_origin())/Vector2(48,32)
	return Vector2i(roundi(p.x),roundi(p.y))

func refresh() -> void:
	camera = movement.position
	queue_redraw()

func ordered_objects() -> Array:
	var ordered := objects.duplicate()
	ordered.append({"kind":-1,"layer":1,"y":movement.position.y,"order":int(map.width)*int(map.height)+map.npcs.size()})
	ordered.sort_custom(func(a,b):
		if a.layer != b.layer: return a.layer < b.layer
		if a.y != b.y: return a.y < b.y
		return a.order < b.order)
	return ordered

func _draw() -> void:
	draw_rect(get_viewport_rect(),Color("20291f"))
	if not initialized: return
	var offset := screen_origin()
	for floor_entry in floors: _draw_frame(floor_entry.pack,floor_entry.index,floor_entry.origin+offset,false,0)
	for entry in ordered_objects():
		if entry.kind == -1:
			_draw_hero(movement.position*Vector2(48,32)+offset,movement.source_frame())
			continue
		var index: int = entry.index
		if entry.kind == 7: index += (tick/17)%4
		elif entry.kind == 5: index += (tick/8)%5
		elif entry.kind == 8:
			var phase: int = (tick/8)%10
			index=55+(phase if phase<5 else 9-phase)
		var frame: Dictionary = packs[entry.pack].frames.get(str(index),{})
		if frame.is_empty(): continue
		var top := 0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		_draw_frame(entry.pack,index,entry.origin+offset,entry.kind==7,top)
	if show_grid:
		for x in range(-12,13):
			for y in range(-13,14):
				var cell := Vector2i(roundi(camera.x)+x,roundi(camera.y)+y)
				if not movement.can_enter(cell): draw_rect(Rect2(Vector2(cell)*Vector2(48,32)+offset,Vector2(48,32)),Color(1,0,0,0.18))

func _draw_frame(pack_name: String,index: int,origin: Vector2,use_offset: bool,top: float) -> void:
	var pack: Dictionary = packs[pack_name]
	var frame: Dictionary = pack.frames.get(str(index),{})
	if frame.is_empty(): return
	var rect: Array = frame.rect
	var pos := origin+Vector2(float(frame.crop[0]),float(frame.crop[1])+top)
	if use_offset: pos += Vector2(float(frame.offset[0]),float(frame.offset[1]))
	var destination := Rect2(pos,Vector2(float(rect[2]),float(rect[3])))
	if not destination.intersects(get_viewport_rect()): return
	draw_texture_rect_region(textures[pack.pages[int(frame.page)].file],destination,Rect2(float(rect[0]),float(rect[1]),float(rect[2]),float(rect[3])))

func _draw_hero(origin: Vector2,index: int) -> void:
	for name in ["body","head"]:
		var layer: Dictionary = hero.layers[name]
		var frame: Dictionary = layer.frames[str(index)]
		var r: Array = frame.rect
		var pos := origin+Vector2(float(frame.offset[0]),float(frame.offset[1]))
		draw_texture_rect_region(textures[layer.atlas],Rect2(pos,Vector2(float(r[2]),float(r[3]))),Rect2(float(r[0]),float(r[1]),float(r[2]),float(r[3])))
