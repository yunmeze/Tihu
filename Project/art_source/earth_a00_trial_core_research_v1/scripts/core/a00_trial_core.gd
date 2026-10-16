extends RefCounted
## Isolated, bounded A00 trial transaction. No I/O, scene, save, combat, or RNG.
## The trusted session owner supplies CURRENT authority/context, never UI payloads.
## Only authority.inventory owns items. Stage/replay copies are unpublished values.
## Atomic failure is this reconstruction's engineering contract, not native evidence.
const Inventory = preload("res://scripts/core/inventory_state.gd")
const Profile = preload("res://scripts/core/default_warrior.gd")
const VM = preload("res://scripts/core/dialogue_vm.gd")
const Bridge = preload("res://scripts/core/map_load_bridge.gd")
const Identity = preload("res://scripts/core/npc_source_identity.gd")
const SOURCE_JSON_SHA := "0f921a2714cab0a29383a8a25631b515b2de98fa38c02ed4701f0a19d3355868"
const SOURCE_BINARY_SHA := "906f33edb6d0c7181629ba37296829a6b8adaf9cde2637ffc4c2530e2c5c352f"
const NPCS := {
 1: {"name":"海曦村长", "x":75, "y":54, "appearance":10, "direction":1, "sha":"5d878f446b2d326b0b5a094cbf0e0fd48b6a63408bef35481374f76a6e4d5bd4"},
 3: {"name":"妈妈", "x":67, "y":75, "appearance":6, "direction":1, "sha":"767959faa11f8e080b5a9b75ebfa606416e7632822ccd3a2268c1bae71146879"}}
const MEDICINES := [
 [0,"金创药小",6,20,0,10,"b94caae4a24fec21c462bad80276282286547b30c2228dce3106ce305d5407dc"],
 [5,"魔法药小",13,0,30,5,"c94c746f423b561498d7a04c6d022288f20aedf5f56cda19f4083e7978e1f084"]]
const NORTH := [[37,55],[37,56],[38,56],[38,57],[39,57],[39,58],[40,58],[40,59],[41,59]]
const HOUSE_PORTALS := [[135,15,64,72],[135,16,64,72],[63,71,136,15],[64,71,136,15]]
const POLICY := {"max_weight":25,"equipment_slots":["helmet","necklace","armor","boots","braceletLeft","braceletRight","ringLeft","ringRight","shield","weapon"],"weight_locations":["bag","equipment"]}
const CONTEXT_KEYS := ["map","identity","stamp","world","epoch","revision","actor","dialogue"]
const TICKET_KEYS := ["base_fingerprint","intent","authority","context","view","movement_reset","granted_ids"]
const COMMON_INTENT := ["kind","world","epoch","revision"]

## Strict bootstrap for the already-committed A13->A00 arrival. No teleport API.
## Birth-entry metadata in authority is unchanged, as in the existing runtime.
static func attach_arrival(authority: Variant, sources: Variant, actor: Variant, world: Variant, epoch: Variant, revision: Variant, preflight: Callable) -> Dictionary:
 var inputs := admit_sources(sources)
 if not inputs.ok: return inputs
 var view := project(authority,inputs.rules)
 if not view.ok: return view
 if not actor_valid(actor) or actor.position != [138,12] or actor.stopped: return fail("invalid_arrival")
 if not counter(world,1) or not counter(epoch) or not counter(revision): return fail("invalid_generation")
 var loaded := rebuild(authority,inputs.source,actor,view.vm_projection)
 if not loaded.ok: return fail("map_preparation_failed")
 var context := {"map":loaded.map,"identity":loaded.npc_identity,"stamp":loaded.npc_source_stamp,
  "world":world,"epoch":epoch,"revision":revision,"actor":actor.duplicate(true),"dialogue":null}
 if not resources_ready(preflight,context.map): return fail("resource_preparation_failed")
 return {"ok":true,"context":context,"vm_projection":view.vm_projection}

## UI intent is only a current-generation action, never script text or coordinates.
static func stage(authority: Variant, sources: Variant, context: Variant, intent: Variant, preflight: Callable) -> Dictionary:
 var inputs := admit_sources(sources)
 if not inputs.ok: return inputs
 var view := project(authority,inputs.rules)
 if not view.ok: return view
 var checked := validate_context(authority,inputs.source,context,view.vm_projection)
 if not checked.ok: return checked
 if not Profile._bounded(intent,0,[0]) or not intent is Dictionary or not intent.get("kind") is String: return fail("invalid_intent")
 var keys: Array = COMMON_INTENT.duplicate()
 match intent.kind:
  "interact": keys.append("runtime_index")
  "choose": keys.append("target")
  "portal": keys.append("portal_index")
  "cancel": pass
  _: return fail("unsupported_intent")
 if not shape(intent,keys): return fail("invalid_intent")
 for key in ["world","epoch","revision"]:
  if typeof(intent[key])!=TYPE_INT or intent[key]!=context[key]: return fail("stale_intent")
 var next_authority: Dictionary = authority.duplicate(true)
 var next_context: Dictionary = context.duplicate(true)
 var page_view: Variant = null
 var granted_ids: Array = []
 if intent.kind == "portal":
  if context.dialogue != null or context.actor.stopped: return fail("portal_unavailable")
  if not counter(intent.portal_index) or intent.portal_index >= HOUSE_PORTALS.size(): return fail("unsupported_portal")
  var portal: Dictionary = inputs.source.portals[int(intent.portal_index)]
  var exact: Array = HOUSE_PORTALS[int(intent.portal_index)]
  if not portal_record_valid(portal,intent.portal_index): return fail("portal_identity_mismatch")
  # Strict R2 adapter threshold, not an assertion about the original EXE radius.
  if Vector2(context.actor.position[0],context.actor.position[1]).distance_to(Vector2(exact[0],exact[1])) >= 0.25: return fail("outside_portal_trigger")
  if Bridge.blocked(context.map,exact[2],exact[3]): return fail("blocked_portal_destination")
  next_context.actor.position=[exact[2],exact[3]]
  next_context.epoch+=1
 elif intent.kind == "cancel":
  if context.dialogue == null: return fail("dialogue_not_open")
  next_context.dialogue=null
 else:
  var source_index: int = -1
  var runtime_index: int = -1
  var process: String = "START"
  if intent.kind == "interact":
   if context.dialogue != null or not counter(intent.runtime_index): return fail("interaction_unavailable")
   runtime_index=int(intent.runtime_index)
  else:
   if context.dialogue == null or typeof(intent.target)!=TYPE_STRING: return fail("dialogue_not_open")
   runtime_index=context.dialogue.runtime_index
   process=intent.target
   if process not in allowed_targets(context.dialogue,authority.et[0]): return fail("unoffered_target")
  var resolved := Identity.resolve(context.identity,context.map,context.stamp,runtime_index)
  if not resolved.ok or not NPCS.has(resolved.source_index): return fail("unauthorized_npc_source")
  source_index=int(resolved.source_index)
  var record: Dictionary = context.map.npcs[runtime_index]
  if not npc_valid(record,source_index): return fail("npc_source_mismatch")
  if intent.kind == "interact" and Vector2(context.actor.position[0],context.actor.position[1]).distance_to(Vector2(record.x,record.y)) > 5.0: return fail("npc_out_of_range")
  var reward_page: bool = source_index==1 and authority.et[0]==3 and process=="A5"
  var result := VM.execute(record.script,view.vm_projection,process,2048,{"a00_trial_rewards":reward_page})
  if not result.ok: return fail("dialogue_execution_failed")
  var expected_et: Array = authority.et.duplicate()
  if reward_page: expected_et[0]=4
  if result.state.et!=expected_et or result.state.bt!=authority.bt: return fail("unexpected_flag_effect")
  for field in ["level","clear_count","game_mode"]:
   if result.state[field]!=view.vm_projection[field]: return fail("readonly_projection_changed")
  var expected_events: Array = []
  if reward_page:
   expected_events=[{"kind":"trial_money","amount":100},{"kind":"trial_give","item_id":"0","quantity":3},{"kind":"trial_give","item_id":"5","quantity":3}]
   for cell in NORTH: expected_events.append({"kind":"setmapflag","x":cell[0],"y":cell[1],"flag":0})
  elif process=="OVER": expected_events=[{"kind":"close"}]
  if result.events!=expected_events or result.random_consumed!=0: return fail("unexpected_dialogue_effect")
  next_authority.et=result.state.et.duplicate()
  next_authority.bt=result.state.bt.duplicate()
  var map_events: Array = []
  for event in result.events:
   match event.kind:
    "trial_money":
     if next_authority.character.gold > Inventory.MAX_INTEGER-event.amount: return fail("money_overflow")
     next_authority.character.gold+=event.amount
    "trial_give":
     for ordinal in event.quantity:
      var action := {"type":"acquire","item_id":event.item_id,"properties":{"raw_proficiency":null,"weight":null},
       "provenance":{"grant":"a00_source1_trial_a5","source_record":1,"script_sha":NPCS[1].sha,"source_item":int(event.item_id),"ordinal":ordinal}}
      var staged := Inventory.stage(next_authority.inventory,action,inputs.rules.catalogue,POLICY,next_authority.inventory.revision)
      if not staged.ok: return fail("inventory_"+str(staged.error))
      var item := Inventory.commit(next_authority.inventory,staged.transaction,inputs.rules.catalogue,POLICY)
      if not item.ok: return fail("inventory_"+str(item.error))
      next_authority.inventory=item.inventory
      granted_ids.append(item.instance_id)
    "setmapflag": map_events.append(event)
  if not map_events.is_empty():
   var bridge_result: Dictionary = result.duplicate(true)
   bridge_result.events=map_events
   var mapped := Bridge.prepare_events(context.map,bridge_actor(context.actor),bridge_result)
   if not mapped.ok: return fail("map_event_preparation_failed")
   next_context.map=mapped.map
  page_view=result.duplicate(true)
  next_context.dialogue=null if result.closed else {"source_index":source_index,"runtime_index":runtime_index,"page":result.page}
 next_context.revision+=1
 var final_view := project(next_authority,inputs.rules)
 if not final_view.ok: return final_view
 var final_context := validate_context(next_authority,inputs.source,next_context,final_view.vm_projection)
 if not final_context.ok: return final_context
 if not resources_ready(preflight,next_context.map): return fail("resource_preparation_failed")
 var ticket := {"base_fingerprint":fingerprint([authority,sources,context]),"intent":intent.duplicate(true),
  "authority":next_authority,"context":next_context,"view":page_view,"movement_reset":true,"granted_ids":granted_ids}
 Identity.freeze(ticket)
 return {"ok":true,"transaction":ticket}

## Caller must pass live/current inputs. Returned replay values are the only output
## eligible for one atomic owner swap; never publish transaction.authority directly.
static func commit(authority: Variant, sources: Variant, context: Variant, transaction: Variant, preflight: Callable) -> Dictionary:
 if not Bridge.json_safe(transaction) or not shape(transaction,TICKET_KEYS): return fail("invalid_transaction")
 if not Bridge.json_safe([authority,sources,context]): return fail("invalid_current_state")
 if typeof(transaction.base_fingerprint)!=TYPE_STRING or transaction.base_fingerprint!=fingerprint([authority,sources,context]): return fail("stale_transaction")
 var replay := stage(authority,sources,context,transaction.intent,preflight)
 if not replay.ok: return replay
 if replay.transaction!=transaction: return fail("transaction_mismatch")
 return {"ok":true,"authority":replay.transaction.authority.duplicate(true),
  "context":replay.transaction.context.duplicate(true),"view":replay.transaction.view.duplicate(true) if replay.transaction.view!=null else null,
  "movement_reset":true,"granted_ids":replay.transaction.granted_ids.duplicate()}

static func admit_sources(sources: Variant) -> Dictionary:
 if not shape(sources,["a00_text","records"]) or typeof(sources.a00_text)!=TYPE_STRING: return fail("invalid_sources")
 if sources.a00_text.length()>2000000 or sources.a00_text.sha256_text()!=SOURCE_JSON_SHA: return fail("map_source_mismatch")
 var source: Variant = JSON.parse_string(sources.a00_text)
 if not source is Dictionary or source.id!="A00" or source.sourceSha256!=SOURCE_BINARY_SHA: return fail("map_source_mismatch")
 var rules := adapt_records(sources.records)
 if not rules.ok: return rules
 return {"ok":true,"source":source,"rules":rules}

static func adapt_records(records: Variant) -> Dictionary:
 if not Profile._bounded(records,0,[0]) or not records is Array or records.size()!=3: return fail("invalid_records")
 var by_id := {}
 for record in records:
  if not record is Dictionary or not numeric(record.get("id"),0,32767): return fail("invalid_records")
  var id: String = str(int(record.id))
  if by_id.has(id): return fail("duplicate_record")
  by_id[id]=record
 if not by_id.has_all(["0","5","252"]): return fail("unsupported_records")
 var cloth := Profile.adapt_cloth(by_id["252"])
 if not cloth.ok: return cloth
 var catalogue: Dictionary = cloth.catalogue.duplicate(true)
 for row in MEDICINES:
  var record: Dictionary = by_id[str(row[0])]
  if record.get("name")!=row[1] or record.get("raw_record_sha256")!=row[6]: return fail("medicine_source_mismatch")
  if not record.get("raw_record_hex") is String or digest(record.raw_record_hex.hex_decode())!=row[6]: return fail("medicine_bytes_mismatch")
  if not record.get("rawFields") is Array or record.rawFields.size()!=39: return fail("medicine_source_mismatch")
  for i in 39:
   var expected: int = {0:3,1:row[2],4:row[3],5:row[4],38:1}.get(i,0)
   if not numeric(record.rawFields[i],expected,expected): return fail("medicine_source_mismatch")
  for field in {"type":3,"icon":row[2],"hp":row[3],"mp":row[4],"weight":1,"price":row[5]}:
   var expected: int = {"type":3,"icon":row[2],"hp":row[3],"mp":row[4],"weight":1,"price":row[5]}[field]
   if not numeric(record.get(field),expected,expected): return fail("medicine_source_mismatch")
  # Reward storage only. This API does not authorize healing/consumption.
  catalogue[str(row[0])]={"weight":1,"equipment_slots":[],"consumable":false}
 return {"ok":true,"catalogue":catalogue,"cloth_ranges":cloth.equipment_ranges}

## Explicit three-template extension. Reuses profile validators directly; never
## builds a filtered inventory mirror merely to satisfy the old cloth-only view.
static func project(authority: Variant, rules: Dictionary) -> Dictionary:
 if not Profile._bounded(authority,0,[0]) or not shape(authority,Profile.STATE_KEYS): return fail("invalid_authority")
 if authority.profile!=Profile.PROFILE or not Profile._character_valid(authority.character) or not Profile._entry_valid(authority.entry): return fail("invalid_profile")
 if authority.unknown_native!={"hero_ap":null,"full_record":null}: return fail("unknown_native_field")
 for bank in ["et","bt"]:
  if not authority[bank] is Array or authority[bank].size()!=30: return fail("invalid_flags")
  for value in authority[bank]:
   if typeof(value)!=TYPE_INT or value < -32768 or value > 32767: return fail("invalid_flags")
 if authority.et[0] not in [3,4]: return fail("outside_trial_stage")
 var checked := Inventory.validate(authority.inventory,rules.catalogue,POLICY)
 if not checked.ok: return checked
 if not checked.inventory.recovery_ids.is_empty(): return fail("unsupported_recovery")
 for instance in checked.inventory.instances.values():
  if instance.properties.weight!=null and instance.properties.weight!=rules.catalogue[instance.item_id].weight: return fail("unsupported_weight_override")
  if instance.item_id in ["0","5"] and instance.properties.raw_proficiency!=null: return fail("unsupported_medicine_properties")
 var derived: Dictionary = authority.character.base.duplicate(true)
 derived.set_bonus=0
 for instance_id in checked.inventory.equipment_slots.values():
  if instance_id==null: continue
  if checked.inventory.instances[instance_id].item_id!="252": return fail("unsupported_equipment")
  for key in Profile.RANGE_KEYS:
   for end in 2:
    derived[key][end]+=rules.cloth_ranges[key][end]
    if derived[key][end]>32767: return fail("stat_overflow")
 var projection := {"et":authority.et.duplicate(),"bt":authority.bt.duplicate(),"level":authority.character.level,"clear_count":authority.character.clear_count,"game_mode":authority.character.game_mode}
 Identity.freeze(projection)
 Identity.freeze(derived)
 return {"ok":true,"vm_projection":projection,"derived":derived,"total_weight":checked.total_weight}

static func validate_context(authority: Dictionary, source: Dictionary, context: Variant, projection: Dictionary) -> Dictionary:
 if not Bridge.json_safe(context) or not shape(context,CONTEXT_KEYS): return fail("invalid_context")
 if not counter(context.world,1) or not counter(context.epoch) or not counter(context.revision) or not actor_valid(context.actor): return fail("invalid_context")
 var expected := rebuild(authority,source,context.actor,projection)
 if not expected.ok: return fail("map_rebuild_failed")
 if context.map!=expected.map or context.identity!=expected.npc_identity or context.stamp!=expected.npc_source_stamp: return fail("map_identity_mismatch")
 if not Identity.validate(context.identity,context.map,context.stamp): return fail("npc_identity_mismatch")
 if context.dialogue!=null:
  var dialogue: Variant = context.dialogue
  if not shape(dialogue,["source_index","runtime_index","page"]) or typeof(dialogue.source_index)!=TYPE_INT or typeof(dialogue.runtime_index)!=TYPE_INT or typeof(dialogue.page)!=TYPE_STRING: return fail("invalid_dialogue")
  var resolved := Identity.resolve(context.identity,context.map,context.stamp,dialogue.runtime_index)
  if not resolved.ok or resolved.source_index!=dialogue.source_index or not NPCS.has(resolved.source_index): return fail("invalid_dialogue")
  if allowed_targets(dialogue,authority.et[0]).is_empty(): return fail("invalid_dialogue")
 return {"ok":true}

static func allowed_targets(dialogue: Dictionary, et0: int) -> Array:
 if dialogue.source_index==1:
  if et0==3: return {"A1":["A2"],"A2":["A3"],"A3":["A4"],"A4":["A5"]}.get(dialogue.page,[])
  if et0==4 and dialogue.page in ["START","A5"]: return ["OVER"]
 if dialogue.source_index==3:
  if et0==3 and dialogue.page=="A1": return ["OVER"]
  if et0==4: return {"A2":["A3"],"A3":["OVER"]}.get(dialogue.page,[])
 return []

static func rebuild(authority: Dictionary, source: Dictionary, actor: Dictionary, projection: Dictionary) -> Dictionary:
 var loaded := Bridge.prepare(source,projection,bridge_actor(actor),{"map_load":true},{},Callable(),true)
 if not loaded.ok or loaded.story.et!=authority.et or loaded.story.bt!=authority.bt or loaded.actor.random_cursor!=actor.random_cursor: return fail("unexpected_load_effect")
 return loaded

static func bridge_actor(actor: Dictionary) -> Dictionary:
 return {"cell":[roundi(actor.position[0]),roundi(actor.position[1])],"stopped":actor.stopped,"random_cursor":actor.random_cursor}

static func actor_valid(actor: Variant) -> bool:
 if not shape(actor,["position","stopped","random_cursor"]) or typeof(actor.stopped)!=TYPE_BOOL: return false
 if not actor.position is Array or actor.position.size()!=2: return false
 for value in actor.position:
  if typeof(value) not in [TYPE_INT,TYPE_FLOAT] or not is_finite(float(value)) or value<0 or value>149: return false
 return typeof(actor.random_cursor)==TYPE_INT and actor.random_cursor>=0 and actor.random_cursor<=2147483647

## Original JSON may materialize exact integers as float Variants. Validate each
## field without array type-equality, truncation, tolerance or string coercion.
static func portal_record_valid(record: Variant, source_index: Variant) -> bool:
 if typeof(source_index)!=TYPE_INT or source_index<0 or source_index>=HOUSE_PORTALS.size(): return false
 if not shape(record,["x","y","targetX","targetY","target"]): return false
 if typeof(record.target)!=TYPE_STRING or record.target!="当前地图": return false
 var exact: Array = HOUSE_PORTALS[source_index]
 var fields := ["x","y","targetX","targetY"]
 for i in fields.size():
  if not numeric(record[fields[i]],exact[i],exact[i]): return false
 return true

static func npc_valid(record: Dictionary, source_index: int) -> bool:
 if not Identity.record_valid(record) or not NPCS.has(source_index): return false
 var expected: Dictionary = NPCS[source_index]
 if record.script.sha256_text()!=expected.sha: return false
 for key in ["name","x","y","appearance","direction"]:
  if record[key]!=expected[key]: return false
 return true

static func resources_ready(preflight: Callable, map: Dictionary) -> bool:
 if not preflight.is_valid(): return false
 var ready: Variant = preflight.call(map.duplicate(true))
 return typeof(ready)==TYPE_BOOL and ready

static func shape(value: Variant, keys: Array) -> bool:
 return typeof(value)==TYPE_DICTIONARY and value.size()==keys.size() and value.has_all(keys)
static func numeric(value: Variant, low: int, high: int) -> bool:
 return typeof(value) in [TYPE_INT,TYPE_FLOAT] and is_finite(float(value)) and value==floor(float(value)) and value>=low and value<=high
static func counter(value: Variant, low: int=0) -> bool:
 return typeof(value)==TYPE_INT and value>=low and value<Inventory.MAX_INTEGER-1
static func fingerprint(value: Variant) -> String:
 return digest(var_to_bytes(value))
static func digest(bytes: PackedByteArray) -> String:
 var hashing := HashingContext.new()
 hashing.start(HashingContext.HASH_SHA256)
 hashing.update(bytes)
 return hashing.finish().hex_encode()
static func fail(code: String) -> Dictionary:
 return {"ok":false,"error":code}
