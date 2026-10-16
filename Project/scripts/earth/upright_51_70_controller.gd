extends "res://scripts/earth/south_walk_contact_controller.gd"
## Single accepted upright tree; all authority and non-A13 factories inherited.
func create_world(map_id:String):
 if map_id!="A13":return super.create_world(map_id)
 var next_world=preload("res://scripts/earth/upright_51_70_world.gd").new()
 next_world.prefer_s_walk_shadow=true
 next_world.prefer_tree_pilot=true
 return next_world
