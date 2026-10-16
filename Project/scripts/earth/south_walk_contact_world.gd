extends "res://scripts/earth/south_walk_snapshot_world.gd"
const WalkCompositor=preload("res://scripts/earth/s_walk_contact_v3_compositor.gd")
const WalkShadowGate=preload("res://scripts/earth/s_walk_contact_v3_gate.gd")
const WalkQualification=preload("res://scripts/earth/s_walk_contact_v3_qualification.gd")
var south_snapshot_guard=preload("res://scripts/earth/snapshot_south_guard.gd").new()
var south_snapshot_errors:Dictionary={}
var prefer_snapshot_south=true
var prefer_s_walk_shadow=false
var s_walk_shadow_gate=WalkShadowGate.new()
var s_walk_qualification=WalkQualification.new()
var s_walk_shadow_ready=false
var s_walk_shadow_last_reason="not prepared"
func _init()->void:
 super()
 plant_reuse_guard=preload("res://scripts/earth/snapshot_plant_shared_guard.gd").new()
 shadow_compositor.free();shadow_compositor=WalkCompositor.new()
 south_walk_guard.bank_revoked.connect(revoke_walk_shadow)
func revoke_walk_shadow()->void:
 s_walk_shadow_ready=false;s_walk_shadow_last_reason="body bank revoked"
 shadow_compositor.clear_walk()
func prepare_s_walk(path:Variant=SouthWalkGuard.MANIFEST)->bool:
 revoke_walk_shadow()
 var ok=super.prepare_s_walk(path)
 if is_inside_tree():bind_walk_shadow()
 return ok
func prepare_visuals()->void:
 floor_pass.world=self
 floor_pass.set_candidate_enabled(false)
 revoke_walk_shadow();s_walk_shadow_gate.reset()
 super.prepare_visuals()
 s_walk_qualification.prepare();s_walk_qualification.prepare_snapshot(map,objects)
 bind_walk_shadow()
 if floor_pass.prepare_candidate():floor_pass.set_candidate_enabled(true)
func bind_walk_shadow()->bool:
 s_walk_shadow_ready=false
 var bindings=south_walk_bindings()
 if bindings.size()!=6:return false
 if not s_walk_shadow_gate.prepare() or not s_walk_shadow_gate.bind_frames(bindings):return false
 if not shadow_compositor.bind_s_walk_frames(bindings):return false
 s_walk_shadow_ready=true;return true
func _ready()->void:
 super._ready()
 bind_walk_shadow()
func refresh()->void:
 validate_snapshot_south()
 super.refresh()
 if not is_inside_tree():return
 var id=movement.source_frame();var body=south_walk_body(id)
 var valid=prefer_s_walk_shadow and prefer_shadow and s_walk_shadow_ready and uses_s_walk(id)
 if valid:valid=source_methods_valid and snapshot_atlas_matches(packs,atlas_qualification.original) and s_walk_qualification.allows("hero_s_walk_contact_v3",map,objects)
 if valid:valid=s_walk_shadow_gate.matches_body(body,id) and s_walk_shadow_gate.allows(movement.position)
 s_walk_shadow_last_reason="admitted" if valid else "inactive or body/source/receiver gate rejected"
 shadow_compositor.set_s_walk(valid,body,movement.position*Vector2(48,32)+screen_origin()-Vector2(16,64),id)
func _notification(what:int)->void:
 if what==NOTIFICATION_PREDELETE:
  # Each listed Node is created by this world's inherited instance fields.
  # Detached failed stages never reach _ready/add_child; parented children remain
  # under normal Node destruction. RefCounted guards/textures are never freed here.
  for node in [floor_pass,hero_shadow,fangzhang_shadow,lingyunzi_shadow,first_tree_shadow,left_upright_shadow,shadow_compositor]:
   if is_instance_valid(node) and node.get_parent()==null:node.free()
func prepare_south_group(id:Variant,path:Variant=null)->bool:
 owner_gate_ready=false
 if not id is String or not SouthCandidate.PATHS.has(id):return false
 if path==null:path=SouthCandidate.PATHS[id]
 south_groups[id]=south_snapshot_guard.prepare(id,path,map,objects)
 if south_groups[id].size()!=SouthCandidate.COUNTS[id]:south_snapshot_errors[id]=south_snapshot_guard.failure
 else:south_snapshot_errors.erase(id)
 update_south_active();queue_redraw()
 return south_groups[id].size()==SouthCandidate.COUNTS[id]
func validate_snapshot_south()->void:
 var geometry_ok=south_snapshot_guard.compatible(map)
 for id in south_groups.keys():
  if south_groups[id].is_empty():continue
  if not geometry_ok or not south_snapshot_guard.owners_valid(south_groups[id],map,objects):
   south_snapshot_errors[id]=south_snapshot_guard.failure;south_groups[id]={};owner_gate_ready=false
 update_south_active()
func refresh_draw_qualifications()->void:
 validate_snapshot_south()
 super.refresh_draw_qualifications()
func south_item(entry:Variant)->Dictionary:
 return super.south_item(entry) if prefer_snapshot_south else {}
