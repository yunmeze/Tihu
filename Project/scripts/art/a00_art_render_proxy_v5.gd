extends "res://scripts/map_load_world.gd"
## EXPERIMENTAL pure visual child. All source files, world identity and gameplay stay intact.
## Native validation must verify CanvasItem.self_modulate affects only the parent draw.
const Registry = preload("res://scripts/art/hd_frame_registry_v5.gd")
var hd_registry = Registry.new()
var source_ref: WeakRef
var original_self_modulate := Color.WHITE
var activated := false

func bind_detached(source, manifest_path: String) -> bool:
	if source.get_script().resource_path != "res://scripts/map_load_world.gd": return false
	if str(source.map.get("id","")) != "A00" or source.get_child_count() != 0: return false
	if source.material != null or source.clip_children != CanvasItem.CLIP_CHILDREN_DISABLED: return false
	source_ref = weakref(source)
	original_self_modulate = source.self_modulate
	_sync_visual_state(source)
	set_process_input(false)
	set_process_unhandled_input(false)
	set_process_unhandled_key_input(false)
	set_physics_process(false)
	# Registry checks the detached render arrays only; it never configures movement.
	if not hd_registry.prepare(self,manifest_path): return false
	return not hd_registry.entries.is_empty()

func activate_parent_suppression() -> void:
	var source = _source()
	if source == null or get_parent() != source: return
	self_modulate = original_self_modulate
	# self_modulate is deliberately used instead of inherited modulate/visibility.
	source.self_modulate = Color(original_self_modulate.r,original_self_modulate.g,original_self_modulate.b,0)
	activated = true
	set_process(true)
	queue_redraw()

func _source():
	return null if source_ref == null else source_ref.get_ref()

func _process(_delta: float) -> void:
	# Visual redraw only. No movement/tick advance, input, authority or transaction work.
	if _source() == null:
		queue_free()
		return
	queue_redraw()

func _sync_visual_state(source) -> void:
	map = source.map
	packs = source.packs
	hero = source.hero
	textures = source.textures
	floors = source.floors
	objects = source.objects
	movement = source.movement
	tick = source.tick
	camera = source.camera
	show_grid = source.show_grid
	initialized = source.initialized
	texture_filter = source.texture_filter
	light_mask = source.light_mask

func screen_origin() -> Vector2:
	var source = _source()
	return Vector2.ZERO if source == null else source.screen_origin()

func _draw() -> void:
	var source = _source()
	if not activated or source == null: return
	# Read authority-owned visual state at draw time, never a cached old-world snapshot.
	_sync_visual_state(source)
	super._draw()

func _draw_frame(pack_name: String,index: int,origin: Vector2,use_offset: bool,top: float) -> void:
	if hd_registry.try_draw(self,self,pack_name,index,origin,use_offset,top): return
	super._draw_frame(pack_name,index,origin,use_offset,top)

func _exit_tree() -> void:
	var source = _source()
	if activated and source != null:
		source.self_modulate = original_self_modulate
	activated = false
