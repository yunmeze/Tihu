extends Node2D
## Exact A13 records 0/1 only. Both bodies and both shadows fail as one group.
const Shadow=preload("res://scripts/art/hero_alpha_ground_shadow.gd")
const SUBJECTS=["fangzhang","lingyunzi"]
const CELLS=[Vector2(64,37),Vector2(62,36)]
const APPEARANCES=[21,9]
const DIRECTIONS=[2,1]
const FIRST=[261,113]
const HASHES=["b921d590ab2e53550bf6225eb0c83a15bd2adf3e9e30f603ab268fc2ac79ce46","517e11d9d9661966d154d9272dfa0c643bf02e3e550d66b3172b22ed8b367c85"]
var bodies:Array=[]
var shadows:Array=[]
var atlases:Array=[]
var prepared:=false
func _init() -> void:
	for n in 2:
		var body=Sprite2D.new();body.centered=false;body.region_enabled=true;body.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR;body.visible=false;bodies.append(body)
		var shadow=Shadow.new();add_child(shadow);shadows.append(shadow)
func fail() -> bool:
	prepared=false;visible=false
	for body in bodies:body.visible=false;body.texture=null
	for shadow in shadows:shadow.visible=false
	atlases.clear()
	return false
func prepare(source_map:Dictionary,paths:Array=[]) -> bool:
	fail()
	if not paths.is_empty() and paths.size()!=2:return false
	if source_map.get("id")!="A13" or not source_map.get("npcs") is Array or source_map.npcs.size()<2:return false
	for n in 2:
		var original=source_map.npcs[n]
		if not original is Dictionary:return false
		if original.get("x")!=CELLS[n].x or original.get("y")!=CELLS[n].y or original.get("appearance")!=APPEARANCES[n] or original.get("direction")!=DIRECTIONS[n]:return false
		var path="res://assets/scifi/npc/"+SUBJECTS[n]+"_v1/manifest.json" if paths.is_empty() else paths[n]
		if not path is String or not FileAccess.file_exists(path):return fail()
		var parser=JSON.new()
		if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return fail()
		var config:Dictionary=parser.data
		# Explicit production contract is checked before any frame or path use.
		if not config.get("schema") is String or config.get("schema")!="lp-a13-selected-npc-body-shadow-v1" or not config.get("npc") is Dictionary:return fail()
		var npc:Dictionary=config.npc
		if not npc.get("map_id") is String or not npc.get("name") is String or npc.name!=original.get("name") or npc.get("map_id")!="A13" or not eqnum(npc.get("record_index"),n) or not eqnum(npc.get("appearance"),APPEARANCES[n]) or not eqnum(npc.get("direction_slot"),DIRECTIONS[n]):return fail()
		if not eqvec(npc.get("cell"),[CELLS[n].x,CELLS[n].y]) or not eqnum(npc.get("stable_order"),10000+n) or not eqnum(npc.get("layer"),1) or not eqnum(npc.get("sort_y"),CELLS[n].y):return fail()
		if not eqvec(config.get("draw_offset"),[-32,-104]) or not eqvec(config.get("frame_size"),[128,160]):return fail()
		if not config.get("animation") is Dictionary or not config.get("shadow") is Dictionary:return fail()
		var anim:Dictionary=config.animation
		if not eqnum(anim.get("fps"),50) or not eqnum(anim.get("frame_ticks"),17) or not eqnum(anim.get("phase_count"),4) or not eqnum(anim.get("loop_ticks"),68) or not anim.get("global_clock") is bool or not anim.global_clock:return fail()
		var sh:Dictionary=config.shadow
		if not eqvec(sh.get("ground_reference"),[44,118] if n==0 else [56,125]) or not eqnum(sh.get("ground_slope"),12.0/17 if n==0 else 0):return fail()
		if not eqvec(sh.get("cast_per_height"),[148.0/279,-111.0/279]) or not eqnum(sh.get("opacity"),.30) or not eqnum(sh.get("blur_radius_px"),.9):return fail()
		if not config.get("texture_sha256") is String or not config.get("sampling") is String or not config.get("atomic_group") is String or config.get("texture_sha256")!=HASHES[n] or config.get("sampling")!="linear" or config.get("atomic_group")!="a13-key-npcs-v1":return fail()
		var texture_path=config.get("texture")
		if not texture_path is String or not ResourceLoader.exists(texture_path,"Texture2D"):return fail()
		var tex=load(texture_path)
		if not tex is Texture2D or tex.get_size()!=Vector2(128 if n==0 else 512,160):return fail()
		if not config.get("frames") is Dictionary:return fail()
		for p in 4:
			var f=config.frames.get(str(FIRST[n]+p))
			if not f is Dictionary or not eqvec(f.get("rect"),[0 if n==0 else p*128,0,128,160]):return fail()
		atlases.append(tex)
	prepared=true
	return true
func configure_at(offset:Vector2,tick:int) -> bool:
	if not prepared or atlases.size()!=2:return fail()
	var phase=posmod(tick/17,4)
	for n in 2:
		if not atlases[n] is Texture2D or atlases[n].get_size()!=Vector2(128 if n==0 else 512,160):return fail()
		var region=Rect2i(0 if n==0 else phase*128,0,128,160)
		var origin=CELLS[n]*Vector2(48,32)+offset-Vector2(32,104)
		if not shadows[n].configure_ground_frame(atlases[n],region,Transform2D(0,origin),Vector2(44,118) if n==0 else Vector2(56,125),12.0/17 if n==0 else 0.0,Vector2(148.0/279,-111.0/279),.30,.9):return fail()
		bodies[n].texture=atlases[n];bodies[n].region_rect=region;bodies[n].position=origin
	return true

func eqnum(value:Variant,expected:float) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and is_equal_approx(float(value),expected)
func eqvec(value:Variant,expected:Array) -> bool:
	if not value is Array or value.size()!=expected.size():return false
	for i in expected.size():
		if not eqnum(value[i],expected[i]):return false
	return true
