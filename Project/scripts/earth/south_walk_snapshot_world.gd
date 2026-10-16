extends "res://scripts/earth/snapshot_zhang_world.gd"
const SouthWalkGuard=preload("res://scripts/earth/south_walk_candidate_guard.gd")
var south_walk_guard=SouthWalkGuard.new()
var south_walk_ready=false
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json")->bool:
 south_walk_ready=false;south_walk_guard.reset()
 return super.setup(actor,map_path)
func prepare_visuals()->void:
 south_walk_ready=false;south_walk_guard.reset()
 super.prepare_visuals()
 prepare_s_walk()
func prepare_s_walk(path:Variant=SouthWalkGuard.MANIFEST)->bool:
 south_walk_ready=false
 south_walk_ready=south_walk_guard.prepare(path)
 queue_redraw()
 return south_walk_ready
func uses_s_walk(index:int)->bool:
 return prefer_candidate and south_walk_ready and south_walk_guard.selected(movement,hero,index)
func south_walk_identity(index:int)->Dictionary:
 return south_walk_guard.body_identity(index) if uses_s_walk(index) else {}
func south_walk_bindings()->Dictionary:
 var result:Dictionary={}
 if not south_walk_ready or not south_walk_guard.bank_complete():return result
 for id in range(57,63):result[id]=south_walk_guard.body_identity(id)
 return result
func south_walk_body(index:int)->Texture2D:
 return south_walk_guard.body_identity(index).get("texture") if south_walk_guard.bank_complete() else null
func _draw_hero(origin:Vector2,index:int)->void:
 if uses_s_walk(index):
  draw_texture_rect(south_walk_guard.canvas(index),Rect2(origin-Vector2(16,64),Vector2(128,128)),false)
  return
 super._draw_hero(origin,index)
func actor_mode()->String:
 if uses_s_walk(movement.source_frame()):return "角色：S 步行六相腿部候选（上身姿态差异，步行影按接地区资格启用）"
 return super.actor_mode()
