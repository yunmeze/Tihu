extends "res://scripts/game_root.gd"
# Explicit diagnostic scene; no story script, save, AI or inventory execution.
# Only original same-map house portals are supported in this stage.
var portal_ready_tick := 0
var transfers: Array = []

func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if ready_ok: check_portal()

func check_portal() -> bool:
	if tick < portal_ready_tick: return false
	for portal in world.map.portals:
		var source := Vector2(float(portal.x),float(portal.y))
		if movement.position.distance_to(source)>=0.25: continue
		var target_map: String = world.map.id if portal.target=="当前地图" else str(portal.target).split(" ")[0]
		if target_map!=world.map.id:
			notice="External portal %s preserved; not enabled in this diagnostic"%target_map
			return false
		var destination := Vector2i(int(portal.targetX),int(portal.targetY))
		if not movement.can_enter(destination):
			notice="Original portal landing is blocked; transfer refused"
			return false
		var from: Vector2 = movement.position
		movement.stop()
		movement.position=Vector2(destination)
		portal_ready_tick=tick+150
		transfers.append({"tick":tick,"source":[portal.x,portal.y],"from":[from.x,from.y],"destination":[destination.x,destination.y]})
		print("R2_ORIGINAL_HOUSE_PORTAL ",JSON.stringify(transfers.back()))
		notice="Original house portal %s -> %s"%[source,destination]
		world.refresh()
		_update_status()
		return true
	return false
