extends "res://scripts/earth/upright_51_70_controller.gd"
## Opt-in leaf adapter. Published opening/render parents and default VM stay frozen.
## Single live authority/inventory; trial_context() is an ephemeral projection.
const ExecutionGate = preload("res://scripts/a00_trial_runtime/execution_gate.gd")
const EXECUTION_PATH = "res://data/a00_trial_runtime_execution_leaves.json"
const EXECUTION_SHA = "5adbdd8437e496b20621824fb82a8a16f29ae372328a7f3c16bd84580db1794e"
const Trial = preload("res://scripts/a00_trial_runtime/a00_trial_core.gd")
var trial_sources: Dictionary = {}
var trial_rules: Dictionary = {}
var trial_dialogue: Variant = null
var trial_busy := false
var trial_active := false
var trial_adoptions := 0
var trial_last_error := ""
var trial_portal_ready_tick := 0
var trial_portal_log: Array = []
# A failure-only seam: returning true never bypasses the real resource check.
var trial_failure_probe: Callable = Callable()

func _ready() -> void:
	super._ready()
	get_window().title = "Legend | A00 source trial candidate | A01 exit not implemented"
	opening_text.text = "按原数据创建角色，阅读五页前世今生，再进入原双 NPC 剧情。\n\n海曦村可拜访妈妈和村长，按原对话领取试炼物品。\n\n兼容随机算法尚未复原原 VB 序列；北口通往 A01 尚未实现，无战斗、保存或怪物 AI。"
	_update_status()

func prepare_inputs() -> Dictionary:
	var execution = ExecutionGate.verify(EXECUTION_PATH,EXECUTION_SHA)
	if not execution.ok: return execution
	var inherited = super.prepare_inputs()
	if not inherited.ok: return inherited
	var catalogue = ResourceCheck.read("res://data/items/catalogue.json")
	if not catalogue.ok: return catalogue
	if not catalogue.value.get("records") is Array or catalogue.value.records.size() <= 252:
		return {"ok":false,"error":"Missing trial source records"}
	var inputs = {"a00_text":FileAccess.get_file_as_string(MAPS.A00),
		"records":[catalogue.value.records[0],catalogue.value.records[5],catalogue.value.records[252]]}
	var admitted = Trial.admit_sources(inputs)
	if not admitted.ok: return admitted
	trial_sources = inputs
	trial_rules = admitted.rules
	return {"ok":true}

func create_world(map_id: String):
	# The A13 published TreeWorld chain is inherited without replacing its pins.
	# A00 must retain the original non-tree adapter.
	return LoadedWorld.new() if map_id == "A00" else super.create_world(map_id)

func prepare_map(candidate_authority: Dictionary, map_id: String, cell: Array, next_stop: bool, base_rng: Dictionary) -> Dictionary:
	var prepared = super.prepare_map(candidate_authority,map_id,cell,next_stop,base_rng)
	if not prepared.ok or map_id != "A00": return prepared
	# Exact integral coordinates, without float-array equality or truncation.
	var position_cell = prepared.movement.position
	if position_cell != Vector2(138,12):
		prepared.world.free()
		return {"ok":false,"error":"Trial requires natural A00 arrival"}
	var actor = {"position":[138,12],"stopped":prepared.stopped,"random_cursor":int(prepared.rng.cursor)}
	var attached = Trial.attach_arrival(prepared.authority,trial_sources,actor,
		prepared.world.get_instance_id(),npc_epoch+1,revision+1,trial_resources)
	if not attached.ok:
		prepared.world.free()
		return attached
	if attached.context.map != prepared.world.map or attached.context.identity != prepared.npc_identity or attached.context.stamp != prepared.npc_source_stamp:
		prepared.world.free()
		return {"ok":false,"error":"Trial arrival identity differs from detached world"}
	prepared["trial_arrival"] = attached.context
	return prepared

func publish(staged: Dictionary) -> void:
	# Check before any inherited display adapter can touch staged.world.
	if not publication_identity_valid(staged):
		reject("Stale publication identity")
		return
	if staged.world.map.id == "A00":
		if not staged.has("trial_arrival") or staged.trial_arrival.world != staged.world.get_instance_id() or staged.trial_arrival.epoch != npc_epoch+1 or staged.trial_arrival.revision != revision+1:
			reject("Unbound A00 arrival")
			return
	super.publish(staged)
	trial_active = world.map.id == "A00"
	trial_dialogue = null
	_update_status()

func trial_context() -> Dictionary:
	return {"map":world.map,"identity":npc_identity,"stamp":npc_source_stamp,
		"world":npc_world_id,"epoch":npc_epoch,"revision":revision,
		"actor":{"position":[movement.position.x,movement.position.y],"stopped":stopped,"random_cursor":consumed_total},
		"dialogue":trial_dialogue.duplicate(true) if trial_dialogue != null else null}

func trial_resources(candidate_map: Dictionary) -> bool:
	if trial_failure_probe.is_valid():
		var permitted: Variant = trial_failure_probe.call(candidate_map.duplicate(true))
		if typeof(permitted) != TYPE_BOOL or not permitted: return false
	return ResourceCheck.check(candidate_map).ok

func trial_intent(kind: String, extra: Dictionary = {}) -> bool:
	# Public dispatcher arguments cannot override the action or generation that
	# the owner binds. Validate before any work or possible publication.
	var expected_keys: Variant = {"interact":["runtime_index"],"choose":["target"],"portal":["portal_index"],"cancel":[]}.get(kind)
	if expected_keys == null or extra.size() != expected_keys.size() or not extra.has_all(expected_keys): return false
	match kind:
		"interact":
			if typeof(extra.runtime_index) != TYPE_INT or extra.runtime_index < 0: return false
		"choose":
			if typeof(extra.target) != TYPE_STRING: return false
		"portal":
			if typeof(extra.portal_index) != TYPE_INT or extra.portal_index < 0 or extra.portal_index >= 4: return false
	if trial_busy or preparing or not trial_active or not ready_ok or not is_instance_valid(world): return false
	if world.map.id != "A00" or world.get_instance_id() != npc_world_id or not trial_live_host_valid(): return false
	trial_busy = true
	trial_last_error = ""
	var base = trial_context().duplicate(true)
	var base_rng = rng_state.duplicate(true)
	var intent = {"kind":kind,"world":base.world,"epoch":base.epoch,"revision":base.revision}
	for key in extra: intent[key] = extra[key]
	var staged = Trial.stage(authority,trial_sources,base,intent,trial_resources)
	if not staged.ok: return trial_fail(str(staged.error))
	var ticket = staged.transaction
	var prepared = prepare_trial_world(ticket.context)
	if not prepared.ok: return trial_fail(str(prepared.error))
	# Replay after all real detached preparation; the CURRENT inputs are supplied.
	var replay = Trial.commit(authority,trial_sources,trial_context(),ticket,trial_resources)
	if not replay.ok:
		prepared.world.free()
		return trial_fail(str(replay.error))
	var final_projection = Trial.project(replay.authority,trial_rules)
	if not final_projection.ok:
		prepared.world.free()
		return trial_fail(str(final_projection.error))
	if rng_state != base_rng or trial_context() != base or not trial_publication_valid(prepared,replay):
		prepared.world.free()
		return trial_fail("publication_binding_changed")
	# No load, await, callback, or further fallible preparation inside adopt.
	adopt_trial(prepared,replay,final_projection.vm_projection)
	trial_busy = false
	if kind == "portal":
		trial_portal_ready_tick = tick+150
		trial_portal_log.append({"tick":tick,"source_index":intent.portal_index,
			"from":base.actor.position,"to":replay.context.actor.position})
		print("A00_HOUSE_PORTAL ",JSON.stringify(trial_portal_log.back()))
	print("A00_TRIAL_COMMIT ",JSON.stringify({"kind":kind,"page":trial_dialogue.page if trial_dialogue != null else "",
		"et0":authority.et[0],"gold":authority.character.gold,"granted_ids":replay.granted_ids,
		"world":npc_world_id,"epoch":npc_epoch,"revision":revision}))
	notice = "原 A00 脚本事务已提交；A01 北出口尚未实现。"
	_update_status()
	return true

func prepare_trial_world(context: Dictionary) -> Dictionary:
	var checked = ResourceCheck.check(context.map)
	if not checked.ok: return checked
	var actor = Movement.new()
	var candidate = create_world("A00")
	if candidate.get_script() != LoadedWorld:
		candidate.free()
		return {"ok":false,"error":"Wrong A00 tree factory"}
	if not candidate.setup_snapshot(actor,context.map.duplicate(true)):
		var error = str(candidate.loading_errors)
		candidate.free()
		return {"ok":false,"error":"detached_setup_failed: "+error}
	var position_value = Vector2(context.actor.position[0],context.actor.position[1])
	if not actor.can_enter(Vector2i(roundi(position_value.x),roundi(position_value.y))) or not NpcIdentity.validate(context.identity,candidate.map,context.stamp):
		candidate.free()
		return {"ok":false,"error":"detached_actor_identity_failed"}
	actor.position = position_value
	actor.direction = movement.direction
	actor.stop()
	candidate.tick = tick
	return {"ok":true,"world":candidate,"movement":actor}

func trial_live_host_valid() -> bool:
	var host = world_host()
	return is_instance_valid(host) and host.is_inside_tree() and not host.is_queued_for_deletion() and is_instance_valid(world) and world.is_inside_tree() and not world.is_queued_for_deletion() and world.get_parent() == host

func trial_publication_valid(prepared: Dictionary, replay: Dictionary) -> bool:
	# Validate every value consumed by adopt or post-adopt reporting first.
	if not Trial.shape(replay,["ok","authority","context","view","movement_reset","granted_ids"]): return false
	if replay.ok != true or typeof(replay.movement_reset) != TYPE_BOOL or not replay.granted_ids is Array: return false
	if not Trial.shape(replay.context,Trial.CONTEXT_KEYS) or not Trial.actor_valid(replay.context.actor): return false
	if replay.context.dialogue != null:
		if not Trial.shape(replay.context.dialogue,["source_index","runtime_index","page"]): return false
		if not replay.view is Dictionary or not replay.view.get("buttons") is Array or not replay.view.get("text") is Array: return false
	if not trial_live_host_valid(): return false
	if not replay.get("movement_reset",false) or npc_epoch >= 9007199254740989: return false
	var candidate = prepared.world
	if not is_instance_valid(candidate) or candidate == world or candidate.is_inside_tree() or candidate.get_parent() != null or candidate.is_queued_for_deletion(): return false
	if not candidate.initialized or candidate.map != replay.context.map: return false
	if not NpcIdentity.validate(replay.context.identity,candidate.map,replay.context.stamp): return false
	if prepared.movement.position != Vector2(replay.context.actor.position[0],replay.context.actor.position[1]): return false
	if not prepared.movement.path.is_empty() or replay.context.actor.random_cursor != consumed_total: return false
	return true

func adopt_trial(prepared: Dictionary, replay: Dictionary, projection: Dictionary) -> void:
	var old_world = world
	# Rebind identities to the real detached object's new ID; every publication
	# advances epoch, including dialogue-only commits that replace the world.
	authority = replay.authority
	story = projection
	world = prepared.world
	movement = prepared.movement
	stopped = replay.context.actor.stopped
	npc_identity = replay.context.identity
	npc_source_stamp = replay.context.stamp
	npc_world_id = world.get_instance_id()
	npc_epoch = maxi(npc_epoch+1,replay.context.epoch)
	revision = replay.context.revision
	trial_dialogue = replay.context.dialogue
	current_view = replay.view if replay.view != null else {}
	current_npc = trial_dialogue.runtime_index if trial_dialogue != null else -1
	dialog_world_id = npc_world_id if trial_dialogue != null else 0
	dialog_epoch = npc_epoch if trial_dialogue != null else -1
	old_world.get_parent().remove_child(old_world)
	world_host().add_child(world)
	world_host().move_child(world,0)
	old_world.queue_free()
	images.clear()
	visual_pending = false
	visual_last_world = npc_world_id
	visual_last_tick = tick
	world.refresh()
	visual_flushes += 1
	trial_adoptions += 1
	if trial_dialogue != null: render_dialog()
	else: dialog.hide()

func trial_fail(error: String) -> bool:
	trial_last_error = error
	trial_busy = false
	return reject("A00 transaction rejected: "+error)

func source_npc(index: int) -> Dictionary:
	if not trial_active: return super.source_npc(index)
	if not is_instance_valid(world) or world.map.id != "A00" or world.get_instance_id() != npc_world_id: return {"ok":false}
	var resolved = NpcIdentity.resolve(npc_identity,world.map,npc_source_stamp,index)
	if not resolved.ok or resolved.source_index not in [1,3]: return {"ok":false}
	return resolved

func interact(index: int) -> bool:
	if not trial_active: return super.interact(index)
	if dialog.visible or not source_npc(index).ok: return false
	return trial_intent("interact",{"runtime_index":index})

func choose(target: String, expected_revision: int) -> bool:
	if not trial_active: return super.choose(target,expected_revision)
	if not dialog.visible or expected_revision != revision or dialog_world_id != npc_world_id or dialog_epoch != npc_epoch or not source_npc(current_npc).ok: return false
	return trial_intent("choose",{"target":target})

func apply_page(index: int, process: String) -> bool:
	if trial_active: return reject("Direct A00 page execution is not authorized")
	return super.apply_page(index,process)

func commit_candidate(result: Dictionary,index: int) -> bool:
	if trial_active: return reject("A00 requires a bound replay transaction")
	return super.commit_candidate(result,index)

func close_dialog() -> void:
	if not trial_active:
		super.close_dialog()
		_update_status()
		return
	if trial_dialogue != null:
		trial_intent("cancel")
		return
	# Arrival closes the previous A13 dialogue without inventing a trial cancel.
	dialog.hide()
	current_npc = -1
	current_view = {}
	dialog_world_id = 0
	dialog_epoch = -1
	_update_status()

func render_dialog() -> void:
	super.render_dialog()
	# Bind the actual rendered generation for A13 and A00, including callbacks
	# retained by a cancelled/old button after its world has been detached.
	for i in choices.get_child_count():
		var button = choices.get_child(i)
		for connection in button.pressed.get_connections(): button.pressed.disconnect(connection.callable)
		button.pressed.connect(trial_callback.bind(current_view.buttons[i].target,npc_world_id,npc_epoch,revision))
	_update_status()

func trial_callback(target: String, expected_world: int, expected_epoch: int, expected_revision: int) -> bool:
	if trial_busy or expected_world != npc_world_id or expected_epoch != npc_epoch or expected_revision != revision: return false
	return choose(target,expected_revision)

func _physics_process(delta: float) -> void:
	if trial_busy: return
	super._physics_process(delta)
	if trial_active and ready_ok and opening_page < 0 and not dialog.visible and not stopped: check_trial_portals()

func _unhandled_input(event: InputEvent) -> void:
	if trial_busy: return
	super._unhandled_input(event)

func check_trial_portals() -> bool:
	if trial_busy or not trial_active or dialog.visible or stopped or tick < trial_portal_ready_tick: return false
	for i in world.map.portals.size():
		var portal = world.map.portals[i]
		if movement.position.distance_to(Vector2(portal.x,portal.y)) >= 0.25: continue
		if i < 4: return trial_intent("portal",{"portal_index":i})
		# Preserve external source records; this stage has no A01/A03 factory or
		# map transition. Opening the nine gate flags is not an implemented exit.
		notice = "原出口 %s 尚未实现；当前仍在 A00。"%str(portal.target)
		_update_status()
		return false
	return false

func _update_status() -> void:
	super._update_status()
	if trial_active and not authority.is_empty():
		status.text = "A00 试炼候选 | ET%d | 钱 %d | 背包实例 %d | (%.2f, %.2f)\n妈妈可选；村长原 A1–A5。A01 北出口尚未实现，无战斗/保存。\n%s"%[authority.et[0],authority.character.gold,authority.inventory.instances.size(),movement.position.x,movement.position.y,notice]
	status.visible = not (overlay.is_visible_in_tree() or dialog.is_visible_in_tree())
