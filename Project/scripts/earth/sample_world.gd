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

func prepare_idle(path:String="res://assets/earth/hero/se_idle_v1/manifest.json") -> bool:
	candidate_ready=false;candidate_texture=null;candidate_error="missing or invalid four-frame candidate"
	if not FileAccess.file_exists(path):return false
	var parser=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path))!=OK or not parser.data is Dictionary:return false
	var reg:Dictionary=parser.data
	if not Guard.integer(reg.get("texture_density"),4,4) or not Guard.integer(reg.get("frame_ticks"),12,12):return false
	if not exact_numbers(reg.get("texture_size"),[2048,512]) or not exact_numbers(reg.get("logical_frame_size"),[128,128]) or not exact_numbers(reg.get("logical_draw_offset"),[-16,-64]) or not exact_numbers(reg.get("source_ids"),[13,14,15,16]):return false
	if not reg.get("records") is Array or reg.records.size()!=4:return false
	for i in 4:
		var record=reg.records[i]
		if not record is Dictionary or not Guard.integer(record.get("source_id"),13+i,13+i) or not exact_numbers(record.get("region_px"),[i*512,0,512,512]):return false
	var tex=Guard.texture(reg.get("texture"),reg.get("texture_size"),reg.get("texture_sha256"))
	if tex==null:return false
	var prepared=CanvasTexture.new();prepared.diffuse_texture=tex;prepared.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	candidate_texture=prepared;candidate_ready=true;candidate_error=""
	return true

func uses_candidate(index:int) -> bool:
	return candidate_ready and prefer_candidate and movement.action=="idle" and index in [13,14,15,16]

func _draw_hero(origin:Vector2,index:int) -> void:
	if uses_candidate(index):
		draw_texture_rect_region(candidate_texture,Rect2(origin-Vector2(16,64),Vector2(128,128)),Rect2((index-13)*512,0,512,512))
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
