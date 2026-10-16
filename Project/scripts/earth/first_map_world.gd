extends "res://scripts/earth/sample_world.gd"
## Optional research scene; inherited movement, sorting and shadow gates are intact.
const ReviewGuard=preload("res://scripts/earth/first_map_guard.gd")
var review_guard=ReviewGuard.new()
var review_ground_owners:Dictionary={}
var review_ground_texture:CanvasTexture
var validated_floor_stream:Array=[]
var review_ground_contract:Dictionary={}
var review_ground_registration:=""
var e_walk_frames:Array=[]
var e_walk_error:="尚未加载"
var review_ground_error:="尚未加载"
func _init() -> void:
	floor_pass.free()
	floor_pass=preload("res://scripts/earth/first_map_floor_pass.gd").new()
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json") -> bool:
	east_ground_group.clear();plant_reuse_groups.clear();plant_reuse_owners.clear();review_ground_contract.clear()
	static_props_groups.clear();static_props_errors={"pool":"尚未加载","clump":"尚未加载"}
	review_ground_owners.clear();review_ground_texture=null;e_walk_frames.clear()
	e_walk_error="尚未加载";review_ground_error="尚未加载"
	var ok=super.setup(actor,map_path)
	prepare_xuyun()
	return ok
func prepare_ground(path:String=ReviewGuard.REGISTRATION) -> bool:
	# Never call the inherited old-64 preparation, including on reload failure.
	ground_owners.clear();review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear();review_ground_contract.clear()
	var group=review_guard.prepare_ground(path,map,packs,floors)
	review_ground_error=review_guard.failure
	if not group.is_empty():
		review_ground_owners=group.owners;review_ground_texture=group.texture
		validated_floor_stream=floors.duplicate(true)
		review_ground_contract=review_guard.registration(path);review_ground_registration=path
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
	refresh_xuyun()
	var snapshot=static_props_guard.refresh_snapshot(static_props_groups.values()+plant_reuse_groups.values(),objects)
	validate_review_ground_stream()
	validate_review_ground_live(snapshot)
	if not east_ground_group.is_empty() and not east_ground_guard.live_valid(east_ground_group,map,packs,floors,snapshot):
		east_ground_group.clear();east_ground_error=east_ground_guard.failure
	for id in plant_reuse_groups.keys():
		if not plant_reuse_guard.live_valid(plant_reuse_groups[id],map,objects,packs,snapshot):
			plant_reuse_errors[id]=plant_reuse_guard.failure;plant_reuse_groups.erase(id)
	plant_reuse_owners.clear()
	if prefer_plant_reuse:
		for group in plant_reuse_groups.values():plant_reuse_owners.merge(group.owners)
	for id in ["pool","clump"]:
		if static_props_groups.has(id) and not static_props_guard.live_valid(static_props_groups[id],map,objects,packs,snapshot):
			static_props_groups.erase(id);static_props_errors[id]=static_props_guard.failure
	super.refresh()

func static_props_count(id:String) -> int:
	var preferred=prefer_review_pool if id=="pool" else prefer_review_clump
	return static_props_groups[id].owners.size() if preferred and static_props_groups.has(id) else 0

func _draw_frame(pack_name:String,index:int,origin:Vector2,use_offset:bool,top:float) -> void:
	if prefer_npcs and xuyun_active and use_offset and pack_name=="Npc" and index in [237,238,239,240] and origin-screen_origin()==Vector2(1392,1344):
		var body=xuyun_guard.descriptor()
		draw_texture_rect_region(body.texture,Rect2(body.origin+screen_origin(),body.size),body.region)
		return
	if not use_offset:
		var cell=(origin-screen_origin())/Vector2(48,32)
		var order=roundi(cell.x)*100+roundi(cell.y)
		if pack_name=="Map/Res/Plant" and plant_reuse_owners.has(order):
			var owner:Dictionary=plant_reuse_owners[order]
			if owner.pack==pack_name and owner.index==index:
				if not owner.empty:draw_texture_rect(owner.texture,Rect2(owner.origin+screen_origin(),owner.size),false)
				return
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

# Independent research extensions; existing caster gates never consult these groups.
const EastGroundGuard=preload("res://scripts/earth/east_ground_guard.gd")
const PlantReuseGuard=preload("res://scripts/earth/plant_reuse_guard.gd")
var east_ground_guard=EastGroundGuard.new()
var plant_reuse_guard=PlantReuseGuard.new()
var east_ground_group:Dictionary={}
var east_ground_error:="尚未加载"
var plant_reuse_groups:Dictionary={}
var plant_reuse_owners:Dictionary={}
var plant_reuse_errors:Dictionary={}
var prefer_east_ground:=true
var prefer_plant_reuse:=true

func prepare_east_ground(path:String=EastGroundGuard.REGISTRATION) -> bool:
	east_ground_group=east_ground_guard.prepare(map,packs,floors,path)
	east_ground_error=east_ground_guard.failure
	floor_pass.queue_redraw()
	return not east_ground_group.is_empty()

func prepare_plant_reuse(path:String=PlantReuseGuard.REGISTRATION) -> bool:
	plant_reuse_groups=plant_reuse_guard.prepare(map,objects,packs,path)
	plant_reuse_errors=plant_reuse_guard.errors.duplicate(true)
	if not plant_reuse_guard.failure.is_empty():plant_reuse_errors["group"]=plant_reuse_guard.failure
	refresh()
	return plant_reuse_groups.size()==24

func east_ground_count() -> int:
	return east_ground_group.owners.size() if prefer_ground and prefer_east_ground and not east_ground_group.is_empty() else 0

func validate_review_ground_live(snapshot:Dictionary) -> void:
	if review_ground_owners.is_empty():return
	var reason="" if StaticPropsGuard.Identity.map_identity(map) else "121 地块源地图身份变化"
	for path in [review_ground_registration,review_ground_contract.source_map.path,review_ground_contract.source_manifest.path,review_ground_contract.ground.texture]:
		if not static_props_guard.snapshot_file_available(path,snapshot):reason="121 地块依赖缺失";break
	if reason.is_empty():
		for owner in review_ground_contract.ground.owners:
			var order=int(owner.stable_source_order)
			if not map.get("cells") is Array or order>=map.cells.size() or not StaticPropsGuard.Identity.source_cell(map.cells[order],owner.source_cell):
				reason="121 地块源单元变化";break
			var pack=packs.get(owner.pack)
			if not pack is Dictionary or not pack.get("frames") is Dictionary or not pack.get("pages") is Array:
				reason="121 地块源图集结构变化";break
			var frame=pack.frames.get(str(int(owner.frame_index)))
			if not frame is Dictionary or frame.get("crop")!=owner.crop or frame.get("rect")!=owner.atlas_rect or frame.get("original")!=owner.original_size:
				reason="121 地块源帧变化";break
			var page=frame.get("page")
			if not (page is int or page is float) or not is_finite(float(page)) or float(page)!=floorf(float(page)) or page<0 or page>=pack.pages.size():
				reason="121 地块源图集页索引变化";break
			if not pack.pages[int(page)] is Dictionary or pack.pages[int(page)].get("file")!=owner.atlas_page or not static_props_guard.snapshot_file_available(owner.atlas_page,snapshot):
				reason="121 地块源图集页变化或缺失";break
	if not reason.is_empty():
		review_ground_owners.clear();review_ground_texture=null;validated_floor_stream.clear();review_ground_error=reason

# Static source-equivalent 237–240 body; unchanged 17-tick source clock and sort.
const XuyunGuard=preload("res://scripts/earth/xuyun_guard.gd")
var xuyun_guard=XuyunGuard.new()
var xuyun_active=false
func prepare_xuyun(deny:PackedStringArray=[]) -> bool:
	xuyun_guard.reload(deny)
	refresh_xuyun()
	return xuyun_active
func refresh_xuyun() -> void:
	xuyun_active=initialized and xuyun_guard.valid(map,packs,objects)
func uses_xuyun(entry:Dictionary) -> bool:
	return prefer_npcs and xuyun_active and xuyun_guard.owns(entry)
func _draw() -> void:
	refresh_xuyun()
	super._draw()
