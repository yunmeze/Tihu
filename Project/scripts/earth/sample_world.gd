extends "res://scripts/world_view.gd"
const SAMPLE_RECT=Rect2(2496,960,768,512)
var follow_actor:=false
var flat_map_bound:=false
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json") -> bool:
	flat_map_bound=false
	var ok=super.setup(actor,map_path)
	flat_map_bound=ok and map_path=="res://data/maps/A13.json" and FileAccess.get_sha256(map_path)=="d09549838963c8157307cc5406d3118baf69259d82459bcba0a3a8be5b34aa27"
	return ok
func screen_origin() -> Vector2:
	return get_viewport_rect().size*.5-movement.position*Vector2(48,32) if follow_actor else -SAMPLE_RECT.position

const Guard=preload("res://scripts/earth/asset_guard.gd")
var prefer_candidate:=true
var candidate_ready:=false
var idle_shadow_bound:=false
var walk_shadow_bound:=false
var candidate_texture:CanvasTexture
var candidate_error:="not prepared"

static func exact_numbers(value:Variant,expected:Array) -> bool:
	if not value is Array or value.size()!=expected.size():return false
	for i in expected.size():
		if not Guard.number(value[i],-16384,16384) or value[i]!=expected[i]:return false
	return true

func prepare_actor_group(path:String,first:int,count:int,phase_ticks:int) -> CanvasTexture:
	if not FileAccess.file_exists(path):return null
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return null
	var reg:Dictionary=parser.data
	var ids=[]
	for i in count:ids.append(first+i)
	if not Guard.integer(reg.get("texture_density"),4,4) or not Guard.integer(reg.get("frame_ticks"),phase_ticks,phase_ticks):return null
	if not exact_numbers(reg.get("texture_size"),[count*512,512]) or not exact_numbers(reg.get("logical_frame_size"),[128,128]) or not exact_numbers(reg.get("logical_draw_offset"),[-16,-64]) or not exact_numbers(reg.get("source_ids"),ids):return null
	if not reg.get("records") is Array or reg.records.size()!=count:return null
	for i in count:
		var record=reg.records[i]
		if not record is Dictionary or not Guard.integer(record.get("source_id"),first+i,first+i) or not exact_numbers(record.get("region_px"),[i*512,0,512,512]):return null
	var tex=Guard.texture(reg.get("texture"),reg.get("texture_size"),reg.get("texture_sha256"))
	if tex==null:return null
	var prepared=CanvasTexture.new();prepared.diffuse_texture=tex;prepared.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	return prepared
func prepare_idle(path:String="res://assets/earth/hero/se_idle_v1/manifest.json") -> bool:
	candidate_texture=prepare_actor_group(path,13,4,12)
	candidate_ready=candidate_texture!=null
	idle_shadow_bound=candidate_ready and path=="res://assets/earth/hero/se_idle_v1/manifest.json" and FileAccess.get_sha256(path)=="3672409856c27b1e81d543b8a0a29063e16170b2cafbaf55f5d6351fb1e9b5a3"
	candidate_error="" if candidate_ready else "missing or invalid four-frame candidate"
	return candidate_ready
var walk_texture:CanvasTexture
var walk_ready:=false
func prepare_walk(path:String="res://assets/earth/hero/se_walk_v1/manifest.json") -> bool:
	walk_texture=prepare_actor_group(path,51,6,7);walk_ready=walk_texture!=null
	walk_shadow_bound=walk_ready and path=="res://assets/earth/hero/se_walk_v1/manifest.json" and FileAccess.get_sha256(path)=="127727940bd2651460bbe90396f80e7c75d89a7d8675f5d3467e5a5f46e229d7"
	return walk_ready
func uses_candidate(index:int) -> bool:
	if not prefer_candidate:return false
	return (candidate_ready and movement.action=="idle" and index>=13 and index<=16) or (walk_ready and movement.action=="walk" and index>=51 and index<=56)
func _draw_hero(origin:Vector2,index:int) -> void:
	if uses_candidate(index):
		var walking=movement.action=="walk"
		var atlas=walk_texture if walking else candidate_texture
		var first=51 if walking else 13
		draw_texture_rect_region(atlas,Rect2(origin-Vector2(16,64),Vector2(128,128)),Rect2((index-first)*512,0,512,512))
	else:super._draw_hero(origin,index)

const Ground=preload("res://scripts/earth/ground_candidate.gd")
var prefer_ground:=true
var ground_owners:Dictionary={}
func prepare_ground(path:String="res://assets/earth/environment/ground_plate_v4/registration.json") -> bool:
	# One publication point; invalid preparation restores all 64 source owners.
	ground_owners=Ground.read_prepare(path,map)
	queue_redraw()
	return ground_owners.size()==64
func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float) -> void:
	if prefer_hall and hall_owners.size()==30 and pack_name==Hall.PACK:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if hall_owners.has(order):
			var item=hall_owners[order]
			if not item.empty:draw_texture_rect(item.texture,Rect2(item.world_top_left+screen_origin(),item.texture.get_size()*item.scale),false)
			return
	if prefer_ground and ground_owners.size()==64 and pack_name==Ground.PACK:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if ground_owners.has(order):
			var item=ground_owners[order]
			draw_texture_rect(item.texture,Rect2(item.world_top_left+screen_origin(),Vector2(96,64)),false)
			return
	super._draw_frame(pack_name,index,origin,use_offset,top)

const Hall=preload("res://scripts/earth/hall_candidate.gd")
var prefer_hall:=true
var hall_owners:Dictionary={}
func prepare_hall(path:String="res://assets/earth/environment/training_hall_v1/registration.json") -> bool:
	hall_owners=Hall.read_prepare(path,map)
	queue_redraw()
	return hall_owners.size()==30


# Explicit flat-ground pass: floors -> one candidate shadow -> original objects.
const DensityShadow=preload("res://scripts/art/density_alpha_ground_shadow.gd")
var floor_pass=preload("res://scripts/earth/sample_floor_pass.gd").new()
var flat_gate=preload("res://scripts/earth/flat_shadow_gate.gd").new()
var hero_shadow=DensityShadow.new()
var prefer_shadow:=true
func _ready():
	floor_pass.world=self;floor_pass.z_index=-2;floor_pass.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;add_child(floor_pass)
	hero_shadow.z_index=-1;add_child(hero_shadow)
	flat_gate.prepare()
func refresh() -> void:
	super.refresh();floor_pass.queue_redraw();update_shadow()
func update_shadow() -> void:
	var frame=movement.source_frame()
	var bound=walk_shadow_bound if movement.action=="walk" else idle_shadow_bound
	if not prefer_shadow or not flat_map_bound or not bound or not uses_candidate(frame) or not flat_gate.allows(movement.position):
		hero_shadow.clear_frame();return
	var walking=movement.action=="walk";var tex=walk_texture if walking else candidate_texture;var first=51 if walking else 13
	hero_shadow.configure_density_ground_frame(tex.diffuse_texture,Rect2i((frame-first)*128,0,128,128),4,Transform2D(0,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64)),Vector2(40,85.2463),-.342818,Vector2(1.2,.55),.25,.8)
func _draw() -> void:
	if not initialized:return
	var offset=screen_origin()
	for entry in ordered_objects():
		if entry.kind==-1:
			_draw_hero(movement.position*Vector2(48,32)+offset,movement.source_frame());continue
		var index:int=entry.index
		if entry.kind==7:index+=(tick/17)%4
		elif entry.kind==5:index+=(tick/8)%5
		elif entry.kind==8:
			var phase:int=(tick/8)%10;index=55+(phase if phase<5 else 9-phase)
		var frame:Dictionary=packs[entry.pack].frames.get(str(index),{})
		if frame.is_empty():continue
		var top=0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		_draw_frame(entry.pack,index,entry.origin+offset,entry.kind==7,top)
	if show_grid:
		for x in range(-12,13):
			for y in range(-13,14):
				var cell=Vector2i(roundi(camera.x)+x,roundi(camera.y)+y)
				if not movement.can_enter(cell):draw_rect(Rect2(Vector2(cell)*Vector2(48,32)+offset,Vector2(48,32)),Color(1,0,0,.18))
