extends RefCounted
## CONTROLLED VISUAL PREVIEW ONLY, NOT ACCEPTED.
## Pure draw bank: no nodes, input, clocks, shadows, movement setup or gameplay writes.
const Movement = preload("res://scripts/core/movement.gd")
const OriginalWorld = preload("res://scripts/map_load_world.gd")
const MANIFEST := "res://data/art/a00_complete_hero_preview_v7.json"
const MANIFEST_SHA := "ecaf68db53372da2bf841175a2041a64578404223611609e2cfdacdebfa12ab2"
var frames: Dictionary = {}
var source_hero: Dictionary = {}
var source_world_id: int = 0
var source_actor_id: int = 0
var errors: Array[String] = []

func clear() -> void:
	frames.clear()
	source_hero.clear()
	source_world_id = 0
	source_actor_id = 0
	errors.clear()

func reject(reason: String) -> bool:
	clear()
	errors.append(reason)
	return false

func prepare(world, path: String = MANIFEST) -> bool:
	clear()
	if path != MANIFEST or not FileAccess.file_exists(path): return reject("hero manifest absent or identity")
	if FileAccess.get_sha256(path) != MANIFEST_SHA: return reject("hero manifest SHA")
	if world == null or world.get_script() != OriginalWorld or world.map.get("id") != "A00": return reject("hero source world identity")
	if world.movement == null or world.movement.get_script() != Movement: return reject("hero movement identity")
	var doc = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not doc is Dictionary or doc.get("schema") != "a00-complete-hero-preview-v7": return reject("hero schema")
	for pins in [doc.source_pins,doc.upstream_manifests]:
		for source in pins:
			if not FileAccess.file_exists(source) or FileAccess.get_sha256(source) != pins[source]: return reject("hero source SHA: "+source)
	var actor = JSON.parse_string(FileAccess.get_file_as_string("res://data/hero/movement.json"))
	if not actor is Dictionary or world.hero != actor: return reject("hero source descriptor")
	var textures: Dictionary = {}
	for record in doc.textures:
		var texture = checked_texture(record)
		if texture == null: return reject("hero image SHA/size/RGBA: "+str(record.path))
		textures[record.path] = texture
	var staged: Dictionary = {}
	for record in doc.records:
		var index := int(record.source_id)
		if staged.has(index) or not textures.has(record.texture): return reject("hero duplicate or missing texture")
		if actor.layers.body.frames.get(str(index)) != record.source_body or actor.layers.head.frames.get(str(index)) != record.source_head: return reject("hero phase source identity")
		var r: Array = record.region_px
		staged[index] = {"texture":textures[record.texture],"region":Rect2(r[0],r[1],r[2],r[3]),"action":record.action,"direction":int(record.direction)}
	if staged.size() != 128 or textures.size() != 34: return reject("hero incomplete bank")
	# Single publication point, all twenty-four preview banks prepared before any HD hero is selected.
	frames = staged
	source_hero = actor.duplicate(true)
	source_world_id = world.get_instance_id()
	source_actor_id = world.movement.get_instance_id()
	return true

func checked_texture(record: Dictionary) -> CanvasTexture:
	var path: String = record.path
	if not FileAccess.file_exists(path) or FileAccess.get_sha256(path) != record.sha256: return null
	var image := Image.load_from_file(path)
	if image == null or image.is_empty() or image.get_size() != Vector2i(record.size[0],record.size[1]): return null
	image.convert(Image.FORMAT_RGBA8)
	var hash := HashingContext.new()
	hash.start(HashingContext.HASH_SHA256)
	hash.update(image.get_data())
	if hash.finish().hex_encode() != record.rgba_sha256: return null
	var canvas := CanvasTexture.new()
	canvas.diffuse_texture = ImageTexture.create_from_image(image)
	canvas.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	return canvas

func selected(world, index: int) -> bool:
	if frames.size() != 128 or not frames.has(index) or world == null: return false
	if world.get_instance_id() != source_world_id or world.get_script() != OriginalWorld or world.map.get("id") != "A00": return false
	var actor = world.movement
	if actor == null or actor.get_script() != Movement or actor.get_instance_id() != source_actor_id: return false
	if world.hero != source_hero or index != actor.source_frame(): return false
	var frame: Dictionary = frames[index]
	return actor.action == frame.action and actor.direction == frame.direction

func try_draw(canvas: CanvasItem, world, origin: Vector2, index: int) -> bool:
	if not selected(world,index): return false
	var expected_origin: Vector2 = world.movement.position*Vector2(48,32)+world.screen_origin()
	if origin.distance_to(expected_origin) > 0.001: return false
	var frame: Dictionary = frames[index]
	canvas.draw_texture_rect_region(frame.texture,Rect2(origin+Vector2(-16,-64),Vector2(128,128)),frame.region)
	return true
