extends "res://scripts/earth/south_walk_contact_world.gd"
## Independent v5 migration; controlled lifecycle, one tree only.
const PilotCompositor=preload("res://scripts/earth/upright_51_70_compositor.gd")
const PilotGate=preload("res://scripts/earth/upright_51_70_gate.gd")
const PilotQualification=preload("res://scripts/earth/upright_51_70_qualification.gd")
var tree_plant_generation=0
var tree_plant_token:Dictionary={"active":false,"generation":0}
var tree_gate=PilotGate.new()
var tree_qualification=PilotQualification.new()
var prefer_tree_pilot=false
var tree_ready=false
var tree_reason="not prepared"
var _tree_needs_prepare=true
func _init()->void:
 super()
 shadow_compositor.free();shadow_compositor=PilotCompositor.new()
 tree_gate.revoked.connect(_tree_revoked)
 floor_pass.free();floor_pass=preload("res://scripts/earth/upright_ground_lifecycle.gd").new()
 floor_pass.world=self
 floor_pass.ground_revoked.connect(_ground_revoked)
 shadow_compositor.tree_world=weakref(self)
func _tree_revoked()->void:
 tree_ready=false
 if is_instance_valid(shadow_compositor):shadow_compositor.clear_tree()
func revoke_tree_plant()->void:
 tree_plant_token.active=false
 tree_plant_generation+=1
 tree_plant_token={"active":false,"generation":tree_plant_generation}
 tree_gate.reset();_tree_needs_prepare=true
func _ground_revoked()->void:
 tree_gate.reset();_tree_needs_prepare=true
func setup(actor:RefCounted,map_path:String="res://data/maps/A13.json")->bool:
 revoke_tree_plant()
 return super.setup(actor,map_path)
func prepare_visuals()->void:
 revoke_tree_plant()
 super.prepare_visuals()
func prepare_plant_reuse(path:String=PlantReuseGuard.REGISTRATION)->bool:
 revoke_tree_plant()
 var result=super.prepare_plant_reuse(path)
 tree_plant_token.active=plant_reuse_groups.has("upright_tree_51_70")
 _tree_needs_prepare=true
 return result
func _exit_tree()->void:
 south_snapshot_guard.reset_all()
 # Publication removes the old world before deferred deletion. Revoke immediately.
 revoke_tree_plant()
func _notification(what:int)->void:
 if what==NOTIFICATION_PREDELETE:
  tree_plant_token.active=false
  tree_gate.reset()
 # Godot delivers _notification through the inheritance chain automatically.
func prepare_tree_pilot(deny:PackedStringArray=[])->bool:
 shadow_compositor.clear_tree();tree_ready=false
 if not tree_qualification.prepare():tree_reason=tree_qualification.error;return false
 tree_ready=tree_gate.prepare(tree_qualification.contract,self,deny)
 tree_reason=tree_gate.error;_tree_needs_prepare=false;return tree_ready
func refresh()->void:
 super.refresh()
 if not is_inside_tree():return
 if _tree_needs_prepare:prepare_tree_pilot()
 var enable=prefer_tree_pilot and prefer_shadow and tree_ready
 shadow_compositor.set_tree(enable,tree_gate,screen_origin(),self)
 tree_reason=tree_gate.error

func south_item(entry:Variant)->Dictionary:
 # Check the enclosing group id at the actual lookup too, without file hashing
 # or re-running source JSON preparation in a draw.
 if entry is Dictionary and Guard.integer(entry.get("order"),0,9999):
  var order=int(entry.order)
  for id in SouthCandidate.IDS:
   var group=south_groups.get(id,{})
   if group.has(order) and not south_snapshot_guard.permit_group_valid(group,id):
    south_snapshot_guard.revoke_group(id)
    south_groups[id]={};owner_gate_ready=false;update_south_active()
 var item=super.south_item(entry)
 if item.is_empty() or south_snapshot_guard.item_valid(item):return item
 var id=item.get("group_id","")
 if south_groups.has(id):
  south_groups[id]={};owner_gate_ready=false;update_south_active()
 return {}

func validate_snapshot_south()->void:
 var geometry_ok=south_snapshot_guard.compatible(map)
 for id in south_groups.keys():
  if south_groups[id].is_empty():continue
  if not geometry_ok or not south_snapshot_guard.owners_valid(south_groups[id],map,objects,id):
   south_snapshot_errors[id]=south_snapshot_guard.failure
   south_snapshot_guard.revoke_group(id)
   south_groups[id]={};owner_gate_ready=false
 update_south_active()
