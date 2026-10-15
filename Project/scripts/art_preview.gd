extends Node2D
const World=preload("res://scripts/art/preview_world_pass.gd")
const Movement=preload("res://scripts/core/movement.gd")
const Shadow=preload("res://scripts/art/hero_alpha_ground_shadow.gd")
const ATLAS="res://assets/scifi/hero/se_idle_v1/body.png"
var worlds:Array=[]
var actor=Movement.new()
var shadow=Shadow.new()
var body=Node2D.new()
var atlas:Texture2D
var phase:=13
var new_body:=true
var shadow_on:=true
var linear:=true
var cycling:=false
var ticks:=0
var label=Label.new()
const SOLES=[[[36,89],[52,81]],[[36.5,89],[51.5,81]],[[36.5,89],[51.5,81]],[[36,89],[52.5,81]]]
func _ready() -> void:
	atlas=load(ATLAS)
	assert(atlas is Texture2D and atlas.get_size()==Vector2(512,128))
	actor.direction=3
	for i in 3:
		var w=World.new()
		assert(w.setup(actor))
		w.pass_kind=i
		worlds.append(w)
	actor.position=Vector2(60,41)
	add_child(worlds[0])
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
func draw_body() -> void:
	var origin=worlds[0].screen_origin()+actor.position*Vector2(48,32)
	if new_body:
		body.draw_texture_rect_region(atlas,Rect2(origin-Vector2(16,64),Vector2(128,128)),Rect2((phase-13)*128,0,128,128))
	else:
		for name in ["body","head"]:
			var layer=worlds[0].hero.layers[name]
			var f=layer.frames[str(phase)]
			body.draw_texture_rect_region(worlds[0].textures[layer.atlas],Rect2(origin+Vector2(f.offset[0],f.offset[1]),Vector2(f.rect[2],f.rect[3])),Rect2(f.rect[0],f.rect[1],f.rect[2],f.rect[3]))
func refresh() -> void:
	for w in worlds:
		w.camera=actor.position
		w.tick=0
		w.queue_redraw()
	var origin=worlds[0].screen_origin()+actor.position*Vector2(48,32)-Vector2(16,64)
	var s=SOLES[phase-13]
	var ok=shadow.configure_frame(atlas,Rect2i((phase-13)*128,0,128,128),Transform2D(0,origin),Vector2(s[0][0],s[0][1]),Vector2(s[1][0],s[1][1]),Vector2(37.0/69.75,-27.75/69.75))
	if not ok:new_body=false
	shadow.visible=new_body and shadow_on and ok
	body.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR if new_body and linear else CanvasItem.TEXTURE_FILTER_NEAREST
	body.queue_redraw()
	label.text="R5 SE13-16 ART PREVIEW cell%s frame%d | new=%s shadow=%s linear=%s cycle=%s\nF1 edge61,39 F4 clear60,41 F2 back61,49 F3 front61,53 | S shadow B source/new L sampling C cycle P phase\nOne floor shadow before all objects; source checker only in source mode. No platform claim."%[actor.position,phase,new_body,shadow.visible,linear,cycling]
	print("R5_DEPTH_STATE ",JSON.stringify({"cell":[actor.position.x,actor.position.y],"phase":phase,"new":new_body,"shadow":shadow.visible,"linear":linear,"cycle":cycling}))
func _physics_process(_delta:float) -> void:
	if cycling:
		ticks+=1
		if ticks%12==0:
			phase=13+(phase-12)%4
			refresh()
func _unhandled_input(event:InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:return
	match event.keycode:
		KEY_F1:actor.position=Vector2(61,39)
		KEY_F4:actor.position=Vector2(60,41)
		KEY_F2:actor.position=Vector2(61,49)
		KEY_F3:actor.position=Vector2(61,53)
		KEY_S:shadow_on=not shadow_on
		KEY_B:new_body=not new_body
		KEY_L:linear=not linear
		KEY_C:cycling=not cycling
		KEY_P:phase=13+(phase-12)%4
	refresh()
