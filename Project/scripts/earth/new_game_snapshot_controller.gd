extends "res://scripts/new_game_candidate.gd"
var raster=SubViewport.new()
var display=TextureRect.new()
const LOGICAL=Vector2(1024,768)
func _ready() -> void:
	get_window().content_scale_size=Vector2i(1024,768)
	get_window().content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	raster.size=Vector2i(2048,1536);raster.size_2d_override=Vector2i(LOGICAL);raster.size_2d_override_stretch=true
	raster.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	add_child(raster)
	display.texture=raster.get_texture();display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	display.mouse_filter=Control.MOUSE_FILTER_IGNORE;display.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(display)
	get_viewport().size_changed.connect(fit_display)
	fit_display()
	super._ready()
	get_window().title="Optional original opening + partial Earth art | E shadow unvalidated"
func fit_display() -> void:
	var available=get_viewport().get_visible_rect().size
	var factor=minf(available.x/LOGICAL.x,available.y/LOGICAL.y)
	display.size=LOGICAL*factor;display.position=(available-display.size)*0.5
func world_host():return raster
func create_world(map_id:String):
	return preload("res://scripts/earth/snapshot_world.gd").new() if map_id=="A13" else LoadedWorld.new()
func map_display_point(point:Vector2) -> Dictionary:
	if not Rect2(display.position,display.size).has_point(point):return {"ok":false}
	return {"ok":true,"logical":(point-display.position)/display.size*LOGICAL}
func npc_at(point:Vector2) -> int:
	if world.has_method("hit_test_npc"):return world.hit_test_npc(point)
	return super.npc_at(point)
func _unhandled_input(event:InputEvent) -> void:
	if event is InputEventMouseButton:
		var mapped=map_display_point(event.position)
		if not mapped.ok:return
		if event.pressed and event.button_index==MOUSE_BUTTON_LEFT and ready_ok and not dialog.visible and opening_page<0:
			flush_visual_refresh(true)
		var copy=event.duplicate();copy.position=mapped.logical
		super._unhandled_input(copy)
	else:super._unhandled_input(event)

# Optional visual scheduling contract v6: validate the latest state at each actual
# flush. An undisplayed transient mutation between flushes need not latch failure.
var visual_pending:=false
var visual_requests:int=0
var visual_flushes:int=0
var visual_last_tick:int=-1
var visual_last_world:int=0
func request_visual_refresh() -> void:
	visual_requests+=1
	visual_pending=true
func _process(_delta:float) -> void:
	flush_visual_refresh()
func flush_visual_refresh(force:bool=false) -> void:
	if not ready_ok or not is_instance_valid(world):return
	if not force and not visual_pending:return
	world.tick=tick
	world.refresh()
	visual_flushes+=1
	visual_last_tick=tick
	visual_last_world=world.get_instance_id()
	visual_pending=false
func publish(staged:Dictionary) -> void:
	# Base publication refresh is already synchronous after attachment. Keep it;
	# pending work for the detached old world must never execute later.
	staged.world.tick=tick
	super.publish(staged)
	visual_flushes+=1
	visual_pending=false
	visual_last_tick=tick
	visual_last_world=world.get_instance_id()
func reprepare_visuals() -> void:
	# Explicit resource reload entry: no content hashing is deferred across drawing.
	if not ready_ok or not is_instance_valid(world):return
	if world.has_method("prepare_visuals"):world.prepare_visuals()
	flush_visual_refresh(true)
func commit_candidate(result:Dictionary,index:int) -> bool:
	var committed=super.commit_candidate(result,index)
	# Non-map dialogue commits can stop the actor and change its visible action.
	if committed:request_visual_refresh()
	return committed
