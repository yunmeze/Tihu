extends Node
## Independently runnable, bounded Earth art sample with complete source fallback.
const World=preload("res://scripts/earth/sample_world.gd")
const Movement=preload("res://scripts/core/movement.gd")
const LOGICAL=Vector2i(768,512)
const RASTER=Vector2i(1536,1024)
var raster=SubViewport.new()
var display=TextureRect.new()
var actor=Movement.new()
var world=World.new()
var hud=Label.new()
var ready_ok:=false
var last_request:Dictionary={}
var show_hud:=true
func _ready() -> void:
	get_window().content_scale_size=LOGICAL
	get_window().content_scale_aspect=Window.CONTENT_SCALE_ASPECT_KEEP
	get_window().size=Vector2i(1152,768)
	get_window().unresizable=false
	raster.size=RASTER;raster.size_2d_override=LOGICAL;raster.size_2d_override_stretch=true
	raster.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	add_child(raster)
	actor.position=Vector2(61,39);actor.direction=3
	ready_ok=world.setup(actor)
	if ready_ok:
		raster.add_child(world);world.prepare_idle();world.prepare_walk();world.prepare_e_idle();world.prepare_s_idle();world.prepare_ground();world.prepare_hall();world.prepare_fangzhang();world.prepare_lingyunzi();world.prepare_tree();world.prepare_shrub();world.prepare_upright_group(0);world.prepare_upright_group(1);world.prepare_translated_shrub(0);world.prepare_translated_shrub(1);world.prepare_grass_group(0);world.prepare_grass_group(1)
		for id in world.SouthCandidate.IDS:world.prepare_south_group(id)
	else:world.free()
	display.expand_mode=TextureRect.EXPAND_IGNORE_SIZE
	display.texture=raster.get_texture();display.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	display.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(display)
	var canvas=CanvasLayer.new();add_child(canvas);canvas.add_child(hud)
	hud.position=Vector2(8,8);hud.add_theme_color_override("font_shadow_color",Color.BLACK)
	hud.add_theme_constant_override("shadow_outline_size",5)
	get_viewport().size_changed.connect(fit_display)
	fit_display();update_hud()
	print("EARTH_SOURCE_SAMPLE_READY ",ready_ok," logical=",LOGICAL," raster=",RASTER," fixed_world=",World.SAMPLE_RECT," actor=",actor.position)
func fit_display() -> void:
	var available=get_viewport().get_visible_rect().size
	var factor=minf(available.x/LOGICAL.x,available.y/LOGICAL.y)
	display.size=Vector2(LOGICAL)*factor;display.position=(available-display.size)*.5
func map_display_point(point:Vector2) -> Dictionary:
	if not ready_ok or not Rect2(display.position,display.size).has_point(point):return {"ok":false}
	var physical=(point-display.position)/display.size*Vector2(RASTER)
	var logical=raster.get_stretch_transform().affine_inverse()*physical
	return {"ok":true,"logical":logical,"cell":world.to_cell(logical)}
func _input(event:InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and event.pressed:
		var mapped=map_display_point(event.position)
		if mapped.ok:
			var accepted=actor.request(mapped.cell)
			last_request={"logical":mapped.logical,"cell":mapped.cell,"accepted":accepted}
			print("EARTH_SOURCE_REAL_CLICK ",last_request)
			world.refresh();update_hud()
	if event is InputEventKey and event.pressed and not event.echo and ready_ok:
		match event.keycode:
			KEY_F:world.follow_actor=not world.follow_actor
			KEY_SPACE:actor.stop()
			KEY_G:world.show_grid=not world.show_grid
			KEY_H:show_hud=not show_hud
			KEY_B:world.prefer_candidate=not world.prefer_candidate
			KEY_P:world.prefer_ground=not world.prefer_ground
			KEY_T:world.prefer_hall=not world.prefer_hall
			KEY_S:world.prefer_shadow=not world.prefer_shadow
			KEY_N:world.prefer_npcs=not world.prefer_npcs
			KEY_V:world.prefer_tree=not world.prefer_tree
			KEY_J:world.prefer_shrub=not world.prefer_shrub
			KEY_K:world.prefer_grass=not world.prefer_grass
		world.refresh();update_hud()
func _physics_process(delta:float) -> void:
	if not ready_ok:return
	actor.step(delta,Input.is_key_pressed(KEY_SHIFT))
	world.tick+=1;world.refresh();update_hud()
func update_hud() -> void:
	hud.visible=show_hud
	hud.text="EARTH ENTRANCE CANDIDATE: 18 NEW E/S IDLE + SE IDLE/WALK FRAMES / OTHER ACTIONS SOURCE\n1536x1024 raster / 768x512 logical | Hall + two NPCs + six trees/four shrubs/two grass groups / other art source | Five bounded casts: SE/S-idle hero + four scene casters, one max-alpha light; Ling/first tree require valid new hall; left upright uses its own patch.\nClick A* | Shift run | Space stop | F follow | G grid | H HUD | B actor | P ground | T hall | S new shadows | N NPCs | V trees | J shrubs | K grass\nCamera: %s | actor %s | Outside sample terrain remains source; four bounded south vegetation groups reuse selected bodies."%["FOLLOW" if ready_ok and world.follow_actor else "FIXED [2496,960,768,512]",actor.position]
	if ready_ok:hud.text+="\nSE idle ready %s / preferred %s / active %s"%[world.candidate_ready,world.prefer_candidate,world.uses_candidate(actor.source_frame())]
	if ready_ok:hud.text+=" / walk6 %s / ground64 %s / hall30 %s"%[world.walk_ready,world.prefer_ground and world.ground_owners.size()==64,world.prefer_hall and world.hall_owners.size()==30]
	if ready_ok:hud.text+=" / max-shadow slots SE-or-S/Fang/Ling/first/left %s"%[world.shadow_compositor.active_slots]
	if ready_ok:hud.text+=" / Fangzhang %s"%[world.prefer_fangzhang and world.fangzhang_texture!=null]
	if ready_ok:hud.text+=" / tree7 %s upright6/6 %s/%s"%[world.prefer_tree and world.tree_owners.size()==7,world.prefer_tree and world.upright_groups[0].size()==6,world.prefer_tree and world.upright_groups[1].size()==6]
	if ready_ok:hud.text+=" / Lingyunzi %s"%[world.prefer_npcs and world.lingyunzi_texture!=null]
	if ready_ok:hud.text+=" / shrub4 %s"%[world.prefer_shrub and world.shrub_owners.size()==4]
	if not ready_ok:hud.text+="\nSource preparation failed; no candidate published."
