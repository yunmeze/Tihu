extends "res://scripts/earth/sample_world.gd"
## Optional research scene; inherited movement, sorting and shadow gates are intact.
const ReviewGuard=preload("res://scripts/earth/first_map_guard.gd")
var review_guard=ReviewGuard.new()
var review_ground_owners:Dictionary={}
var review_ground_texture:CanvasTexture
var validated_floor_stream:Array=[]
var e_walk_frames:Array=[]
var e_walk_error:="尚未加载"
var review_ground_error:="尚未加载"
func _init() -> void:
	floor_pass.free()
	floor_pass=preload("res://scripts/earth/first_map_floor_pass.gd").new()
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json") -> bool:
	static_props_groups.clear();static_props_errors={"pool":"尚未加载","clump":"尚未加载"}
	review_ground_owners.clear();review_ground_texture=null;e_walk_frames.clear()
	e_walk_error="尚未加载";review_ground_error="尚未加载"
	return super.setup(actor,map_path)
func prepare_ground(path:String=ReviewGuard.REGISTRATION) -> bool:
	# Never call the inherited old-64 preparation, including on reload failure.
	ground_owners.clear();review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear()
	var group=review_guard.prepare_ground(path,map,packs,floors)
	review_ground_error=review_guard.failure
	if not group.is_empty():
		review_ground_owners=group.owners;review_ground_texture=group.texture
		validated_floor_stream=floors.duplicate(true)
	floor_pass.queue_redraw()
	return review_ground_owners.size()==121
func prepare_e_walk(path:String=ReviewGuard.REGISTRATION) -> bool:
	e_walk_frames.clear()
	e_walk_frames=review_guard.prepare_e_walk(path)
	e_walk_error=review_guard.failure
	queue_redraw()
	return e_walk_frames.size()==6
func uses_e_walk(index:int) -> bool:
	return prefer_candidate and movement.action=="walk" and index>=45 and index<=50 and e_walk_frames.size()==6
func _draw_hero(origin:Vector2,index:int) -> void:
	if uses_e_walk(index):
		draw_texture_rect(e_walk_frames[index-45],Rect2(origin-Vector2(16,64),Vector2(128,128)),false)
		return
	# Existing supported 18 full-frame phases or complete original body + head.
	super._draw_hero(origin,index)
func actor_mode() -> String:
	if not prefer_candidate:return "角色：完整原版（B）"
	if uses_e_walk(movement.source_frame()):return "角色：E 步行研究稿（完整画布）"
	if uses_candidate(movement.source_frame()):return "角色：既有 18 相位研究稿（完整画布）"
	return "角色：当前动作使用原版"

func validate_review_ground_stream() -> void:
	if not review_ground_owners.is_empty() and floors!=validated_floor_stream:
		review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear()
		review_ground_error="运行时完整地面序列变化，整组已撤回"


# Optional source-bound static props; no per-owner textures or sort changes.
const StaticPropsGuard=preload("res://scripts/earth/static_props_guard.gd")
var static_props_guard=StaticPropsGuard.new()
var static_props_groups:Dictionary={}
var static_props_errors:Dictionary={"pool":"尚未加载","clump":"尚未加载"}
var prefer_review_pool:=true
var prefer_review_clump:=true
var review_camera_top_left:=SAMPLE_RECT.position
var review_camera_label:="出生点"

func screen_origin() -> Vector2:
	return super.screen_origin() if follow_actor else -review_camera_top_left

func prepare_static_props(id:String,path:String=StaticPropsGuard.REGISTRATION) -> bool:
	if id not in ["pool","clump"]:return false
	static_props_groups.erase(id)
	var group=static_props_guard.prepare(id,map,objects,packs,path)
	static_props_errors[id]=static_props_guard.failure
	if not group.is_empty():static_props_groups[id]=group
	queue_redraw()
	return not group.is_empty()

func refresh() -> void:
	var snapshot=static_props_guard.refresh_snapshot(static_props_groups.values(),objects)
	for id in ["pool","clump"]:
		if static_props_groups.has(id) and not static_props_guard.live_valid(static_props_groups[id],map,objects,packs,snapshot):
			static_props_groups.erase(id);static_props_errors[id]=static_props_guard.failure
	super.refresh()

func static_props_count(id:String) -> int:
	var preferred=prefer_review_pool if id=="pool" else prefer_review_clump
	return static_props_groups[id].owners.size() if preferred and static_props_groups.has(id) else 0

func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float) -> void:
	if not use_offset:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		for id in ["pool","clump"]:
			if static_props_count(id)==0:continue
			var group:Dictionary=static_props_groups[id]
			if not group.owners.has(order):continue
			var owner:Dictionary=group.owners[order]
			if owner.pack!=pack_name or owner.index!=index:continue
			# Cross-owner taps use the unchanged master. Geometry shares half-open edges.
			draw_texture_rect_region(group.texture,Rect2(owner.origin+screen_origin(),owner.size),owner.region,Color.WHITE,false,false)
			return
	super._draw_frame(pack_name,index,origin,use_offset,top)
