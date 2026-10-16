extends "res://scripts/earth/south_walk_snapshot_controller.gd"
func create_world(map_id:String):
 if map_id!="A13":return super.create_world(map_id)
 var next_world=preload("res://scripts/earth/south_walk_contact_world.gd").new()
 # Explicit accepted candidate preference; body/source/receiver gates still AND.
 next_world.prefer_s_walk_shadow=true
 return next_world
func _unhandled_input(event:InputEvent)->void:
 if event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_F8 and ready_ok and world.has_method("bind_walk_shadow"):
  world.floor_pass.set_candidate_enabled(not world.floor_pass.candidate_enabled)
  request_visual_refresh();_update_status();return
 super._unhandled_input(event)
func _update_status()->void:
 super._update_status()
 if ready_ok and is_instance_valid(world) and world.has_method("bind_walk_shadow"):
  var floor_on=world.floor_pass.candidate_enabled and not world.floor_pass.candidate.is_empty()
  status.text+="\n地面："+("C24 / 草907 / 既有39 / 原1583" if floor_on else "原有地面通道")+" · F8 对照"
  status.text+="\nS步行六相 / 张四相阶段候选；上身差异保留，步行影仅接地区启用。"
func publish(staged:Dictionary)->void:
 # Validate before the inherited coalescing adapter reads staged.world.tick.
 # Success retains its exact publish/scheduling path; authority rules are inherited.
 if not publication_identity_valid(staged):
  reject("NPC publication identity is missing, changed, or stale")
  return
 super.publish(staged)
