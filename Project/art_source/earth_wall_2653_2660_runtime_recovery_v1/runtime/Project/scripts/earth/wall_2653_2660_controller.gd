extends "res://scripts/earth/upright_51_70_controller.gd"
## Separate opt-in scene; existing main scene and parent controller remain pinned.
func create_world(map_id:String):
 if map_id!="A13":return super.create_world(map_id)
 var next_world=preload("res://scripts/earth/wall_2653_2660_world.gd").new()
 next_world.prefer_s_walk_shadow=true
 next_world.prefer_tree_pilot=true
 next_world.prefer_wall=true
 return next_world
