extends "res://scripts/earth/snapshot_sorted_world.gd"
# Optional conservative owner negative membership. Positive gates remain live.
const DRAW_SOURCE_PATH="res://scripts/earth/sample_world.gd"
const DRAW_SOURCE_SHA="c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2"
const ROUTE_PROOF_PINS={"res://scripts/earth/sample_world.gd": "c9139f34e1d57b1d33086c11157850454325c88078608fe13f8a081f7ddc07b2", "res://scripts/earth/lingyunzi_candidate.gd": "5c110878726bb354e20574d8a8ef092c227f2742209c9ae3cc8b4e7787509d53", "res://scripts/earth/fangzhang_candidate.gd": "8f3b21d4f24c73299b8685715f58b8a4f15cbb9b454e84a34c69d9a12831e6a8", "res://scripts/earth/instance_identity_guard.gd": "2eabae66a29b8696d7aef50ddfe5bbd27b46ad4278624c10b4a1183a2435cb0b", "res://scripts/earth/asset_guard.gd": "c5a0718736b91ceac6aea417a464840e61b33c03b19d8dc3f61272339a7cdf4e", "res://scripts/earth/first_map_world.gd": "e6a8ac3604c5ea938fbf006da1a79f195e38adf65695168ea0498db44bb37a5c"}
var owner_prefilter_enabled=true
var potential_owners:Dictionary={}
var owner_gate_ready=false
var draw_source_valid=false
var owner_set_builds=0
var owner_set_build_us=0
var early_source_calls=0
var full_chain_calls=0
func prepare_visuals()->void:
 owner_gate_ready=false
 draw_source_valid=true
 for path in ROUTE_PROOF_PINS:
  if FileAccess.get_sha256(path)!=ROUTE_PROOF_PINS[path]:draw_source_valid=false
 super.prepare_visuals()
func refresh()->void:
 owner_gate_ready=false
 super.refresh()
 if not is_inside_tree():return
 var began=Time.get_ticks_usec()
 if owner_prefilter_enabled and draw_source_valid:rebuild_owner_set()
 owner_set_build_us+=Time.get_ticks_usec()-began
func add_owner_dictionary(value:Variant)->bool:
 if not value is Dictionary:return false
 for key in value:
  if not Guard.integer(key,0,9999) or not value[key] is Dictionary:return false
  potential_owners[int(key)]=true
 return true
func rebuild_owner_set()->void:
 owner_gate_ready=false;potential_owners={}
 # Collect every prepared group even when preference/active state is off. This is
 # deliberately an over-approximation and includes intentional empty records.
 for value in [house_guard.owner_orders,shrub_owners,tree_owners,hall_owners,ground_owners,review_ground_owners,plant_reuse_owners]:
  if not add_owner_dictionary(value):return
 for bank in [south_groups]:
  if not bank is Dictionary:return
  for value in bank.values():
   if not add_owner_dictionary(value):return
 for bank in [upright_groups,grass_groups,translated_shrub_groups]:
  if not bank is Array:return
  for value in bank:
   if not add_owner_dictionary(value):return
 for bank in [static_props_groups,plant_reuse_groups]:
  if not bank is Dictionary:return
  for group in bank.values():
   if not group is Dictionary or not add_owner_dictionary(group.get("owners")):return
 if not east_ground_group.is_empty() and not add_owner_dictionary(east_ground_group.get("owners")):return
 potential_owners.make_read_only();owner_gate_ready=true;owner_set_builds+=1
func early_source(entry:Variant)->bool:
 if not owner_prefilter_enabled or not owner_gate_ready or not draw_source_valid:return false
 if not entry is Dictionary or not entry.get("kind") is int or not entry.get("order") is int:return false
 # Dynamic sources, NPC and hero retain the complete original chain.
 if entry.kind not in [1,2,3,4]:return false
 return not potential_owners.has(entry.order)
func prepare_south_group(id:Variant,path:Variant=null)->bool:
 owner_gate_ready=false
 var result=super.prepare_south_group(id,path)
 owner_gate_ready=false
 return result
func prepare_shrub(path:Variant=ShrubCandidate.PATH)->bool:
 owner_gate_ready=false
 var result=super.prepare_shrub(path)
 owner_gate_ready=false
 return result
func prepare_translated_shrub(instance:Variant,path:Variant=null)->bool:
 owner_gate_ready=false
 var result=super.prepare_translated_shrub(instance,path)
 owner_gate_ready=false
 return result
func prepare_grass_group(instance:Variant,path:Variant=null)->bool:
 owner_gate_ready=false
 var result=super.prepare_grass_group(instance,path)
 owner_gate_ready=false
 return result
func prepare_tree(path:Variant=TreeCandidate.PATH)->bool:
 owner_gate_ready=false
 var result=super.prepare_tree(path)
 owner_gate_ready=false
 return result
func prepare_upright_group(instance:Variant,path:Variant=null)->bool:
 owner_gate_ready=false
 var result=super.prepare_upright_group(instance,path)
 owner_gate_ready=false
 return result
func prepare_hall(path:String="res://assets/earth/environment/training_hall_v1/registration.json")->bool:
 owner_gate_ready=false
 var result=super.prepare_hall(path)
 owner_gate_ready=false
 return result
func prepare_ground(path:String=ReviewGuard.REGISTRATION)->bool:
 owner_gate_ready=false
 var result=super.prepare_ground(path)
 owner_gate_ready=false
 return result
func prepare_static_props(id:String,path:String=StaticPropsGuard.REGISTRATION)->bool:
 owner_gate_ready=false
 var result=super.prepare_static_props(id,path)
 owner_gate_ready=false
 return result
func prepare_east_ground(path:String=EastGroundGuard.REGISTRATION)->bool:
 owner_gate_ready=false
 var result=super.prepare_east_ground(path)
 owner_gate_ready=false
 return result
func prepare_plant_reuse(path:String=PlantReuseGuard.REGISTRATION)->bool:
 owner_gate_ready=false
 var result=super.prepare_plant_reuse(path)
 owner_gate_ready=false
 return result
func prepare_house(deny:PackedStringArray=[]) -> bool:
 owner_gate_ready=false
 var result=super.prepare_house(deny)
 owner_gate_ready=false
 return result
func _draw() -> void:
 if not owner_prefilter_enabled or not owner_gate_ready or not draw_source_valid:super._draw();return
 # Preserve current first_map_world draw-time positive gate before original sample draw.
 refresh_draw_qualifications()
 if not initialized:return
 var offset=screen_origin()
 for entry in ordered_objects():
  if entry.kind==-1:
   _draw_hero(movement.position*Vector2(48,32)+offset,movement.source_frame());continue
  if early_source(entry):
   early_source_calls+=1;_source_entry(entry,offset);continue
  full_chain_calls+=1
  var south=south_item(entry)
  if not south.is_empty():
   if not south.empty:draw_texture_rect(south.texture,Rect2(south.origin+offset,south.size),false)
   continue
  var upright=upright_item(entry)
  if not upright.is_empty():
   if not upright.empty:draw_texture_rect(upright.texture,Rect2(upright.origin+offset,upright.size),false)
   continue
  var grass=grass_item(entry)
  if not grass.is_empty():
   draw_texture_rect(grass.texture,Rect2(grass.origin+offset,grass.size),false)
   continue
  var extra_shrub=translated_shrub_item(entry)
  if not extra_shrub.is_empty():
   draw_texture_rect(extra_shrub.texture,Rect2(extra_shrub.origin+offset,extra_shrub.size),false)
   continue
  if uses_shrub(entry):
   var item=shrub_owners[entry.order]
   draw_texture_rect(item.texture,Rect2(item.origin+offset,item.size),false)
   continue
  if uses_tree(entry):
   var item=tree_owners[entry.order]
   if not item.empty:draw_texture_rect(item.texture,Rect2(item.origin+offset,item.size),false)
   continue
  if uses_lingyunzi(entry):
   var phase:int=(tick/17)%4
   draw_texture_rect_region(lingyunzi_texture,Rect2(entry.origin+offset+Vector2(-32,-104),Vector2(128,160)),Rect2(phase*512,0,512,640))
   continue
  if uses_fangzhang(entry):
   draw_texture_rect(fangzhang_texture,Rect2(entry.origin+offset+Vector2(-32,-104),Vector2(128,160)),false)
   continue
  _source_entry(entry,offset)
 if show_grid:
  for x in range(-12,13):
   for y in range(-13,14):
    var cell=Vector2i(roundi(camera.x)+x,roundi(camera.y)+y)
    if not movement.can_enter(cell):draw_rect(Rect2(Vector2(cell)*Vector2(48,32)+offset,Vector2(48,32)),Color(1,0,0,.18))
func _source_entry(entry:Dictionary,offset:Vector2)->void:
 var index:int=entry.index
 if entry.kind==7:index+=(tick/17)%4
 elif entry.kind==5:index+=(tick/8)%5
 elif entry.kind==8:
  var phase:int=(tick/8)%10;index=55+(phase if phase<5 else 9-phase)
 var frame:Dictionary=packs[entry.pack].frames.get(str(index),{})
 if frame.is_empty():return
 var top=0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
 _draw_frame(entry.pack,index,entry.origin+offset,entry.kind==7,top)
