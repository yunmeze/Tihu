extends "res://scripts/world_view.gd"
const SAMPLE_RECT=Rect2(2496,960,768,512)
var follow_actor:=false
func screen_origin() -> Vector2:
	return get_viewport_rect().size*.5-movement.position*Vector2(48,32) if follow_actor else -SAMPLE_RECT.position

const Guard=preload("res://scripts/earth/asset_guard.gd")
var prefer_candidate:=true
var candidate_ready:=false
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
	candidate_error="" if candidate_ready else "missing or invalid four-frame candidate"
	return candidate_ready
var walk_texture:CanvasTexture
var walk_ready:=false
func prepare_walk(path:String="res://assets/earth/hero/se_walk_v1/manifest.json") -> bool:
	walk_texture=prepare_actor_group(path,51,6,7);walk_ready=walk_texture!=null
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
func prepare_ground(path:String="res://assets/earth/environment/ground_plate_v2/registration.json") -> bool:
	# One publication point; invalid preparation restores all 64 source owners.
	ground_owners=Ground.read_prepare(path,map)
	queue_redraw()
	return ground_owners.size()==64
func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float) -> void:
	if prefer_ground and ground_owners.size()==64 and pack_name==Ground.PACK:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if ground_owners.has(order):
			var item=ground_owners[order]
			draw_texture_rect(item.texture,Rect2(item.world_top_left+screen_origin(),Vector2(96,64)),false)
			return
	super._draw_frame(pack_name,index,origin,use_offset,top)
