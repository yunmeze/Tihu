extends "res://scripts/earth/new_game_snapshot_controller.gd"
func create_world(map_id:String):
 return preload("res://scripts/earth/south_walk_snapshot_world.gd").new() if map_id=="A13" else super.create_world(map_id)
