extends Node2D
const World=preload("res://scripts/art/preview_world_pass.gd")
const Movement=preload("res://scripts/core/movement.gd")
const Shadow=preload("res://scripts/art/hero_alpha_ground_shadow.gd")
const TreeShadow=preload("res://scripts/art/selected_tree_shadow.gd")
const ATLAS="res://assets/scifi/hero/se_idle_v1/body.png"
var worlds:Array=[]
var actor=Movement.new()
var shadow=Shadow.new()
var tree_shadow=TreeShadow.new()
var tree_cast_ready:=false
var tree_cast_on:=true
var body=Node2D.new()
var atlas:Texture2D
var walk_atlas:Texture2D
var walk_atlases:Dictionary={}
var idle_atlases:Dictionary={}
var idle_start:=13
var moving:=false
const PHASES=[9,10,11,12,13,14,15,16,17,18,19,20,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62]
var phase:=13
var new_body:=true
var shadow_on:=true
var linear:=true
var cycling:=false
var ticks:=0
var label=Label.new()
var temple_ready:=true
var temple_on:=false
var tree_ready:=true
var tree_on:=false
func _ready() -> void:
	atlas=load(ATLAS)
	walk_atlas=optional_walk("res://assets/scifi/hero/se_walk_v3/body.png")
	walk_atlases={45:optional_walk("res://assets/scifi/hero/e_walk_v1/body.png"),51:walk_atlas,57:optional_walk("res://assets/scifi/hero/s_walk_v1/body.png")}
	assert(atlas is Texture2D and atlas.get_size()==Vector2(512,128))
	idle_atlases={9:load("res://assets/scifi/hero/e_idle_v1/body.png"),13:atlas,17:load("res://assets/scifi/hero/s_idle_v1/body.png")}
	for tex in idle_atlases.values():assert(tex is Texture2D and tex.get_size()==Vector2(512,128))
	actor.direction=3
	for i in 3:
		var w=World.new()
		assert(w.setup(actor))
		w.pass_kind=i
		temple_ready=w.prepare_temple() and temple_ready
		tree_ready=w.prepare_tree() and tree_ready
		worlds.append(w)
	actor.position=Vector2(60,41)
	tree_cast_ready=tree_shadow.prepare()
	add_child(worlds[0])
	add_child(tree_shadow)
	add_child(shadow)
	add_child(worlds[1])
	body.draw.connect(draw_body)
	add_child(body)
	add_child(worlds[2])
	var canvas=CanvasLayer.new()
	add_child(canvas)
	label.position=Vector2(12,12)
	label.add_theme_color_override("font_shadow_color",Color.BLACK)
	label.add_theme_constant_override("shadow_outline_size",5)
	canvas.add_child(label)
	refresh()
	print("R5_DEPTH_GPU_READY floor-shadow-backobjects-body-frontobjects")
func optional_walk(path:String) -> Texture2D:
	if not ResourceLoader.exists(path):return null
	var tex=load(path)
	return tex if tex is Texture2D and tex.get_size()==Vector2(768,128) else null
func idle_base() -> int:
	if phase>=45:return 9+((phase-45)/6)*4
	return 9 if phase<13 else (13 if phase<17 else 17)
func walk_base() -> int:
	return 45+((phase-45)/6)*6 if phase>=45 else 45+((idle_base()-9)/4)*6
func selected_texture() -> Texture2D:
	return walk_atlases.get(walk_base()) if phase>=45 else idle_atlases.get(idle_base())
func frame_index() -> int:
	return phase-walk_base() if phase>=45 else phase-idle_base()
func draw_body() -> void:
	var origin=worlds[0].screen_origin()+actor.position*Vector2(48,32)
	if new_body:
		body.draw_texture_rect_region(selected_texture(),Rect2(origin-Vector2(16,64),Vector2(128,128)),Rect2(frame_index()*128,0,128,128))
	else:
		for name in ["body","head"]:
			var layer=worlds[0].hero.layers[name]
			var f=layer.frames[str(phase)]
			body.draw_texture_rect_region(worlds[0].textures[layer.atlas],Rect2(origin+Vector2(f.offset[0],f.offset[1]),Vector2(f.rect[2],f.rect[3])),Rect2(f.rect[0],f.rect[1],f.rect[2],f.rect[3]))
func refresh() -> void:
	for w in worlds:
		w.camera=actor.position
		w.tick=0
		w.temple_enabled=temple_on and temple_ready
		w.queue_redraw()
	var tree_ok=tree_ready and tree_cast_ready and tree_shadow.configure_at(worlds[0].screen_origin())
	if not tree_ok:tree_on=false
	for w in worlds:w.tree_enabled=tree_on and tree_ok
	tree_shadow.visible=tree_on and tree_cast_on and tree_ok
	var origin=worlds[0].screen_origin()+actor.position*Vector2(48,32)-Vector2(16,64)
	var tex=selected_texture()
	var index=frame_index()
	var group_walk=walk_atlases.get(45+((idle_base()-9)/4)*6)
	var group_idle=idle_atlases.get(idle_base())
	var group_ok=group_walk is Texture2D and group_walk.get_size()==Vector2(768,128) and group_idle is Texture2D and group_idle.get_size()==Vector2(512,128)
	var ok=group_ok and shadow.configure_ground_frame(tex,Rect2i(index*128,0,128,128),Transform2D(0,origin),Vector2(40,86),0.0,Vector2(148.0/279,-111.0/279))
	if not ok:new_body=false
	shadow.visible=new_body and shadow_on and ok
	body.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR if new_body and linear else CanvasItem.TEXTURE_FILTER_NEAREST
	body.queue_redraw()
	label.text="ART PREVIEW E/SE/S idle + walk | cell%s frame%d new%s shadow%s linear%s\n1 E / 2 SE / 3 S | C idle cycle / P phase / M selected E/SE/S route | B source / S shadow / L filter\nT temple / F5 view | G tree+cast / H tree cast / F6 tree front | F2 back / F3 front / F4 road\nHero ground86; one selected tree ground cast. Building cast / platform receivers not included."%[actor.position,phase,new_body,shadow.visible,linear]
	print("R5_DEPTH_STATE ",JSON.stringify({"cell":[actor.position.x,actor.position.y],"phase":phase,"new":new_body,"shadow":shadow.visible,"linear":linear,"cycle":cycling,"temple":temple_on and temple_ready,"tree":tree_on and tree_ready,"tree_cast":tree_shadow.visible}))
func _physics_process(delta:float) -> void:
	if moving:
		actor.step(delta)
		phase=actor.source_frame()
		if actor.path.is_empty():moving=false;phase=idle_start
		refresh()
		return
	if cycling:
		ticks+=1
		if ticks%12==0:
			phase=idle_start+(phase-idle_start+1)%4
			refresh()
func _unhandled_input(event:InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:return
	if event.keycode in [KEY_F1,KEY_F2,KEY_F3,KEY_F4,KEY_F5,KEY_F6,KEY_P,KEY_1,KEY_2,KEY_3]:
		moving=false;actor.stop()
	match event.keycode:
		KEY_1:idle_start=9;phase=9;actor.direction=2
		KEY_2:idle_start=13;phase=13;actor.direction=3
		KEY_3:idle_start=17;phase=17;actor.direction=4
		KEY_T:temple_on=not temple_on if temple_ready else false
		KEY_H:tree_cast_on=not tree_cast_on
		KEY_G:tree_on=not tree_on if tree_ready else false
		KEY_F6:actor.position=Vector2(57,35);new_body=false
		KEY_F5:actor.position=Vector2(66,35);new_body=false
		KEY_F1:actor.position=Vector2(61,39)
		KEY_F4:actor.position=Vector2(60,41)
		KEY_F2:actor.position=Vector2(61,49)
		KEY_F3:actor.position=Vector2(61,53)
		KEY_S:shadow_on=not shadow_on
		KEY_B:new_body=not new_body
		KEY_L:linear=not linear
		KEY_C:cycling=not cycling;phase=idle_start;moving=false;actor.stop()
		KEY_P:phase=PHASES[(PHASES.find(phase)+1)%PHASES.size()];idle_start=idle_base()
		KEY_M:
			actor.stop();actor.animation_tick=0;cycling=false
			idle_start=idle_base();actor.direction=2+(idle_start-9)/4
			actor.position=Vector2(59,40) if idle_start==13 else Vector2(60,41)
			var target=Vector2i(61,42) if idle_start==13 else (Vector2i(62,41) if idle_start==9 else Vector2i(60,43))
			phase=idle_start;moving=actor.request(target)
			print("ART_PREVIEW_DIRECTION_ROUTE ",actor.direction," ",moving," ",actor.path)
	refresh()
