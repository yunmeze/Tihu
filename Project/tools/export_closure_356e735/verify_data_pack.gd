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
 first.world.refresh()
 assert(first.world.east_ground_count()==57 and first.world.review_ground_owners.size()+first.world.east_ground_count()==178)
 assert(first.world.plant_reuse_groups.size()==24 and first.world.plant_reuse_owners.size()==81)
 assert(first.world.candidate_ready and first.world.walk_ready and first.world.e_idle_ready and first.world.s_idle_ready)
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
 # Failure seam uses a nonexistent registration, never edits source or packed assets.
 assert(not first.world.prepare_east_ground("res://missing-export-verification.json"))
 assert(first.world.east_ground_count()==0 and first.world.review_ground_owners.size()==121)
 assert(not first.world.prepare_plant_reuse("res://missing-export-verification.json"))
 first.world.refresh()
 assert(first.world.plant_reuse_groups.is_empty() and first.world.plant_reuse_owners.is_empty())
 assert(first.world.floors.size()==2553 and not first.world.textures.is_empty())
 assert(first.world.static_props_count("pool")==7 and first.world.static_props_count("clump")==3)
 first.world.prefer_candidate=false
 assert(not first.world.uses_candidate(17) and not first.world.uses_e_walk(45))
 status["missing_registration_source_fallback"]=true
 first.queue_free();await process_frame
 var walk=load("res://scenes/earth_walk_review.tscn").instantiate();root.add_child(walk);await process_frame
 assert(walk.ready_ok and walk.source_frames.size()==6 and walk.research_frames.size()==6)
 print("WALK_6_PLUS_6_PASS")
 walk.queue_free();await process_frame
 var game=load("res://scenes/earth_new_game_candidate.tscn").instantiate();root.add_child(game)
 game.set_physics_process(false)
 assert(game.prepare_inputs().ok)
 var rng=load("res://scripts/core/compat_rng.gd")
 var seeded={}
 for seed_value in 10000:
  var candidate=rng.create("pack-verification",seed_value)
  assert(candidate.ok)
  var reservation=rng.reserve(candidate.state,1)
  if reservation.transaction.rnd_values[0]<5:
   seeded=candidate.state;break
 assert(not seeded.is_empty())
 var created=game.Profile.create("pack-verification",game.cloth,game.POLICY)
 assert(created.ok)
 game.pending_creation={"state":created.state,"rng":seeded}
 assert(game.start_new_game())
 assert(game.creation_count==1 and game.map_load_count==1 and game.opening_page==0)
 assert(game.world.map.added_units.size()==1)
 assert(game.source_npc(0).ok and game.source_npc(0).source_index==0)
 assert(game.source_npc(1).ok and game.source_npc(1).source_index==1)
 assert(not game.source_npc(2).ok)
 for npc in game.world.map.npcs:assert(game.NpcIdentity.record_valid(npc) and npc.size()==6)

 game.flush_visual_refresh(true)
 var world=game.world
 assert(world.review_ground_owners.size()==121 and world.east_ground_count()==57)
 assert(world.plant_reuse_groups.size()==24 and world.plant_reuse_owners.size()==81)
 assert(world.static_props_count("pool")==7 and world.static_props_count("clump")==3)
 assert(world.e_walk_frames.size()==6 and world.xuyun_guard.slot>=0)
 assert(world.qualification.runtime_declaration_valid())
 for caster in world.qualification.contracts:
  assert(world.qualification.resource_ok.get(caster,false),caster)
  assert(world.qualifies(caster),caster)
 status["optional_snapshot"]={"ledger":world.visual_ledger.duplicate(true),"receiver_resources":world.qualification.resource_ok.duplicate(true),"xuyun":world.xuyun_guard.slot,"added_units":world.map.added_units.size()}
 game.set_process(false)
 assert(world.sort_reuse_enabled and world.owner_prefilter_enabled)
 assert(world.sort_methods_valid and world.sort_ready and world.draw_source_valid and world.owner_gate_ready)
 var ordered_optimized=var_to_bytes(world.ordered_objects())
 world.sort_reuse_enabled=false
 assert(ordered_optimized==var_to_bytes(world.ordered_objects()))
 world.sort_reuse_enabled=true
 var early_count=0
 for entry in world.objects:
  if world.early_source(entry):early_count+=1
  if entry.kind in [5,7,8,9]:assert(not world.early_source(entry))
 assert(early_count>0)
 assert(not world.early_source({"kind":-1,"order":10000}))
 for path in world.SORT_SOURCE_PINS:assert(FileAccess.get_sha256(path)==world.SORT_SOURCE_PINS[path],path)
 for path in world.ROUTE_PROOF_PINS:assert(FileAccess.get_sha256(path)==world.ROUTE_PROOF_PINS[path],path)
 var slot=world.xuyun_guard.slot
 assert(slot>=0 and world.xuyun_active)
 var original_name=world.map.npcs[slot].name
 var previous_flushes=game.visual_flushes
 world.map.npcs[slot].name="export-verification-invalid-xuyun"
 world.queue_redraw()
 await process_frame;await process_frame
 assert(game.visual_flushes==previous_flushes)
 assert(not world.xuyun_active and world.xuyun_guard.slot==-1)
 world.map.npcs[slot].name=original_name
 world.queue_redraw()
 await process_frame;await process_frame
 assert(game.visual_flushes==previous_flushes)
 assert(world.xuyun_active and world.xuyun_guard.slot==slot)
 assert(world.sort_reuse_enabled and world.owner_prefilter_enabled and world.owner_gate_ready)
 for caster in world.qualification.contracts:assert(world.qualifies(caster),caster)
 status["optimization"]={"sort_enabled":world.sort_reuse_enabled,"prefilter_enabled":world.owner_prefilter_enabled,"source_pins":true,"sorted_sequence_equal":true,"early_source_owners":early_count,"xuyun_draw_only_withdraw_restore":true}
 print("SORT_PREFILTER_SOURCE_PINS_XUYUN_DRAW_WITHDRAW_RESTORE_PASS")
 # Approved house-local contract, same fresh entry as actual draw and hit.
 assert(world.house_guard.reg.owners.size()==10 and world.house_guard.owner_orders.size()==10)
 assert(world.house_guard.local_scope_enabled and world.house_opt_skip_refresh_validation)
 assert(not world.house_opt_detach_offscreen and not world.house_opt_uniform_dedup)
 assert(world.house_active and world.house_guard.texture is CanvasTexture)
 assert(world.house_guard.texture.texture_filter==CanvasItem.TEXTURE_FILTER_LINEAR)
 var declaration=JSON.parse_string(FileAccess.get_file_as_string("res://assets/earth/snapshot_opening/snapshot_runtime_registration.json"))
 assert(declaration.runtime_files.size()==154 and declaration.house_live_scope.frames.size()==10)
 var owner285={}
 for owner in world.house_guard.reg.owners:
  if owner.index==285:owner285=owner
 assert(not owner285.is_empty())
 var order285=int(owner285.stable_source_order)
 var original_cell=world.map.cells[order285].duplicate(true)
 world.map.cells[order285][0]=int(world.map.cells[order285][0])+1
 world.queue_redraw();await process_frame;await process_frame
 assert(not world.house_active)
 var before=world.house_guard.validations
 world.hit_test_npc(Vector2(-999,-999))
 assert(not world.house_active and world.house_guard.validations>before)
 world.map.cells[order285]=original_cell
 world.queue_redraw();await process_frame;await process_frame
 assert(world.house_active)
 assert(not world.prepare_house(PackedStringArray(["res://assets/earth/house_280_289_v1/body.png"])))
 world.queue_redraw();await process_frame;await process_frame
 assert(not world.house_active and world.xuyun_active)
 assert(world.prepare_house())
 world.queue_redraw();await process_frame;await process_frame
 assert(world.house_active and world.xuyun_active)
 var original_unit=world.map.added_units[0].duplicate(true)
 world.map.added_units[0].definition_id=509
 world.refresh_house();world.refresh_xuyun()
 assert(world.house_active and not world.xuyun_active and not world.qualifies("first_tree"))
 world.map.added_units[0]=original_unit
 world.refresh_house();world.refresh_xuyun()
 assert(world.house_active and world.xuyun_active and world.qualifies("first_tree"))
 status["house"]={"owner_identities":10,"empty285_required":true,"runtime_records":154,"fresh_draw_query":true,"denied_body_withdraw_restore":true,"local_scope_independent_mon220":true,"other_guards_reject_mon220":true,"defaults_preserved":true,"linear_color":true}
 print("HOUSE154_LOCAL_IDENTITY_FRESH_FALLBACK_RESTORE_PASS")
 var inventory=JSON.stringify(game.authority.inventory)
 var random_state=JSON.stringify(game.rng_state)
 assert(not game.start_new_game())
 for i in 5:assert(game.advance_opening(1))
 assert(game.opening_page==-1)
 assert(game.interact(0))
 for target in ["A2","A3","A4","A5","OVER"]:assert(game.choose(target,game.revision))
 assert(game.authority.et[0]==2)
 assert(game.interact(1))
 for target in ["B2","B3","B4","B5","B6"]:assert(game.choose(target,game.revision))
 assert(game.world.map.id=="A00" and game.movement.position==Vector2(138,12))
 assert(game.authority.et[0]==3 and not game.stopped and game.map_load_count==2)
 assert(JSON.stringify(game.authority.inventory)==inventory and JSON.stringify(game.rng_state)==random_state)
 assert(game.world.map.npcs.filter(func(n):return n.x==94 and n.y==60).is_empty())
 assert(not game.movement.can_enter(Vector2i(39,57)))
 status["natural_opening_to_A00"]={"map":game.world.map.id,"loads":game.map_load_count,"story_et0":game.authority.et[0],"textures":game.world.textures.size(),"floors":game.world.floors.size()}
 print("OPTIONAL_SNAPSHOT_154_SIX_RECEIVERS_XUYUN_OPENING_A00_PASS")
 # Controlled map-load fixtures; this is not natural story progress to ET28.
 assert(not game.source_npc(0).ok)
 var controlled_et3=game.authority.duplicate(true)
 controlled_et3.et[0]=3
 var staged_et3=game.prepare_map(controlled_et3,"A13",[61,39],false,game.rng_state)
 assert(staged_et3.ok and game.publication_identity_valid(staged_et3))
 game.publish(staged_et3)
 game.flush_visual_refresh(true)
 var et3_identity=game.NpcIdentity.resolve(game.npc_identity,game.world.map,game.npc_source_stamp,1)
 assert(et3_identity.ok and et3_identity.source_index==2)
 assert(game.source_npc(0).ok and not game.source_npc(1).ok)
 game.movement.position=Vector2(game.world.map.npcs[1].x,game.world.map.npcs[1].y)
 assert(not game.interact(1))
 for npc in game.world.map.npcs:assert(game.NpcIdentity.record_valid(npc) and npc.size()==6)
 var controlled_et28=game.authority.duplicate(true)
 controlled_et28.et[0]=28
 var staged_et28=game.prepare_map(controlled_et28,"A13",[61,39],false,game.rng_state)
 assert(staged_et28.ok and game.publication_identity_valid(staged_et28))
 game.publish(staged_et28)
 game.flush_visual_refresh(true)
 var et28_identity=game.source_npc(1)
 assert(et28_identity.ok and et28_identity.source_index==1)
 assert(game.interact(1) and game.dialog.visible)
 game.close_dialog()
 for npc in game.world.map.npcs:assert(game.NpcIdentity.record_valid(npc) and npc.size()==6)
 status["npc_source_identity"]={"initial_source_0_1_only":true,"npc_records_six_fields":true,"ET3_runtime1_source":et3_identity.source_index,"ET3_runtime1_rejected":true,"controlled_ET28_runtime1_source":et28_identity.source_index,"controlled_ET28_interaction_allowed":true}
 print("STABLE_NPC_SOURCE_0_1_ET3_REJECT_CONTROLLED_ET28_ALLOW_PASS")
 game.queue_free();await process_frame
 var report=FileAccess.open(OS.get_environment("RESULT"),FileAccess.WRITE);report.store_string(JSON.stringify(status,"  "));report.close()
 quit()
