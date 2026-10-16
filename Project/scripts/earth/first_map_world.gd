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
