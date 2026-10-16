extends "res://scripts/earth/first_map_floor_pass.gd"
## Revoke before inherited floor transitions; inherited rendering is unchanged.
signal ground_revoked
var ground_generation=0
var ground_token:Dictionary={"active":false,"generation":0}
func revoke_ground()->void:
 ground_token.active=false
 ground_generation+=1
 ground_token={"active":false,"generation":ground_generation}
 ground_revoked.emit()
func prepare_candidate()->bool:
 revoke_ground()
 return super.prepare_candidate()
func set_candidate_enabled(value:bool)->void:
 revoke_ground()
 super.set_candidate_enabled(value)
 if value and not candidate.is_empty():ground_token.active=true
func _draw()->void:
 if ground_token.active and (not candidate_enabled or candidate.is_empty() or world.floors!=candidate.floors or world.map.cells!=candidate.cells or material!=candidate.material):revoke_ground()
 super._draw()
func _notification(what:int)->void:
 if what==NOTIFICATION_PREDELETE:revoke_ground()
