extends SceneTree
func _initialize():call_deferred("check")
func check():
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(OS.get_environment("ALLOWLIST")))
 if not OS.get_environment("PACK").is_empty():assert(ProjectSettings.load_resource_pack(OS.get_environment("PACK")))
 for f in manifest.files:
  assert(FileAccess.file_exists(f.path),f.path)
  assert(FileAccess.get_sha256(f.path)==f.sha256,f.path)
  assert(FileAccess.get_file_as_bytes(f.path).size()==f.bytes,f.path)
 print("EXACT_RAW_BYTES ",manifest.files.size())
 var first=load("res://scenes/earth_first_map_review.tscn").instantiate();root.add_child(first)
 await process_frame;await process_frame
 assert(first.ready_ok and first.world.review_ground_owners.size()==121 and first.world.e_walk_frames.size()==6)
 if "static_props_groups" in first.world:
  assert(first.world.static_props_count("pool")==7 and first.world.static_props_count("clump")==3)
 var status={"source_textures":first.world.textures.size(),"floor_count":first.world.floors.size(),"objects":first.world.objects.size()}
 if "static_props_groups" in first.world:
  status["pool_owners"]=first.world.static_props_count("pool");status["clump_owners"]=first.world.static_props_count("clump")
 for p in first.world.get_property_list():
  if not p.usage & PROPERTY_USAGE_SCRIPT_VARIABLE:continue
  var v=first.world.get(p.name)
  if v is bool:status[p.name]=v
  elif v is Array or v is Dictionary:status[p.name+"_count"]=v.size()
  elif v is Object and v!=null:
   var object_status={}
   for op in v.get_property_list():
    if op.usage & PROPERTY_USAGE_SCRIPT_VARIABLE and op.name in ["ready","prepared","error","failure","configured"]:object_status[op.name]=v.get(op.name)
   if not object_status.is_empty():status[p.name]=object_status
 print("FIRST_MAP_STATUS ",JSON.stringify(status))
 first.queue_free();await process_frame
 var walk=load("res://scenes/earth_walk_review.tscn").instantiate();root.add_child(walk);await process_frame
 assert(walk.ready_ok and walk.source_frames.size()==6 and walk.research_frames.size()==6)
 print("WALK_6_PLUS_6_PASS")
 var report=FileAccess.open(OS.get_environment("RESULT"),FileAccess.WRITE);report.store_string(JSON.stringify(status,"  "));report.close()
 walk.queue_free();await process_frame;quit()
