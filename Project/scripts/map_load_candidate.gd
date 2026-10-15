extends "res://scripts/game_root.gd"
const Bridge=preload("res://scripts/core/map_load_bridge.gd")
const VM=preload("res://scripts/core/dialogue_vm.gd")
const PreparedWorld=preload("res://scripts/map_load_world.gd")
const MAPS={"A13":"res://data/maps/A13.json","A00":"res://data/maps/A00.json","A01":"res://data/maps/A01.json","A02":"res://data/maps/A02.json"}
var story: Dictionary=VM.initial_state()
var stopped := false
var random_cursor := 0
var registry: Dictionary={}
var view_cell=Vector2(61,39)
var case_name := "preflight"
var commits := 0
var preflight_override: Callable=Callable()
func _ready() -> void:
	super._ready()
	var definition=world.read_json("res://data/monsters/a13-chicken.json")
	registry={"彩蛋鸡":definition}
	apply_case("A13",1,100,[61,39],Vector2(61,39))
func resources(definition: Dictionary) -> bool:
	if preflight_override.is_valid(): return preflight_override.call(definition)
	if not FileAccess.file_exists(definition.texture_manifest): return false
	var json:=JSON.new()
	if json.parse(FileAccess.get_file_as_string(definition.texture_manifest))!=OK or not json.data is Dictionary: return false
	var manifest: Dictionary=json.data
	if not manifest.get("packs") is Dictionary: return false
	for pack in manifest.packs.values():
		for page in pack.pages:
			if not ResourceLoader.exists(page.file) or not load(page.file) is Texture2D: return false
	return true
func apply_case(map_id: String,et: int,draw: int,cell: Array,camera_cell: Vector2) -> bool:
	if not MAPS.has(map_id): return false
	var parser:=JSON.new()
	if parser.parse(FileAccess.get_file_as_string(MAPS[map_id]))!=OK: return false
	var next_story:=VM.initial_state()
	next_story.merge({"level":1,"clear_count":0,"game_mode":0})
	next_story.et[0]=et
	next_story.bt[0]=1
	var candidate=Bridge.prepare(parser.data,next_story,{"cell":cell,"stopped":false,"random_cursor":random_cursor},{"map_load":true,"rnd_values":[draw]},registry,resources)
	if not candidate.ok: return rejected(candidate.error)
	var next_world=PreparedWorld.new()
	var next_actor=Movement.new()
	if not next_world.setup_snapshot(next_actor,candidate.map):
		var errors=str(next_world.loading_errors)
		next_world.free()
		return rejected("Renderer preflight "+errors)
	var destination:=Vector2i(candidate.actor.cell[0],candidate.actor.cell[1])
	if not next_actor.can_enter(destination):
		next_world.free()
		return rejected("Final actor cell blocked")
	next_actor.position=Vector2(destination)
	# No yielding or failure-prone preparation after this publication boundary.
	var old_world=world
	world=next_world
	movement=next_actor
	story=candidate.story
	stopped=candidate.actor.stopped
	random_cursor=candidate.actor.random_cursor
	view_cell=camera_cell
	case_name="%s inputET%d explicitRND%d"%[map_id,et,draw]
	remove_child(old_world)
	add_child(world)
	move_child(world,0)
	old_world.queue_free()
	world.camera=view_cell
	world.tick=0
	world.queue_redraw()
	commits+=1
	notice="Prepared map/state/actor/cursor committed together."
	print("R4_NATIVE_COMMIT ",JSON.stringify({"case":case_name,"et0":story.et[0],"stop":stopped,"cell":candidate.actor.cell,"cursor":random_cursor,"npcs":world.map.npcs.size(),"source_spawns":world.map.spawns.size(),"added":world.map.added_units.size(),"objects":world.objects.size()}))
	_update_status()
	return true
func rejected(message: String) -> bool:
	notice="REJECTED (previous world/state/cursor retained): "+message
	print("R4_NATIVE_REJECT ",message)
	_update_status()
	return false
func _physics_process(_delta: float) -> void:
	# Fixed pose/camera diagnostic. Keyboard switches explicit fixtures only.
	if not ready_ok: return
	world.camera=view_cell
	world.queue_redraw()
	_update_status()
func _update_status() -> void:
	status.text="R4 map-load DIAGNOSTIC | %s | ET%d STOP=%s cursor=%d\nF1 no chicken | F2 chicken | F3 hidden Lingyun | F4 ET28 MOVE | F5 gate ET3 | F6 gate ET4\nF7 failed spawn preflight | F8 A01 | F9 A02 | fixed source frame1 chicken, NO AI/combat, NO VB PRNG\n%s"%[case_name,story.et[0],stopped,random_cursor,notice]
func _unhandled_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo: return
	match event.keycode:
		KEY_F1: apply_case("A13",1,100,[61,39],Vector2(49,53))
		KEY_F2: apply_case("A13",1,0,[61,39],Vector2(49,53))
		KEY_F3: apply_case("A13",3,100,[61,39],Vector2(61,39))
		KEY_F4: apply_case("A13",28,100,[60,39],Vector2(61,39))
		KEY_F5: apply_case("A00",3,100,[40,60],Vector2(39,57))
		KEY_F6: apply_case("A00",4,100,[40,60],Vector2(39,57))
		KEY_F7:
			preflight_override=func(_definition):return false
			apply_case("A13",1,0,[61,39],Vector2(49,53))
			preflight_override=Callable()
		KEY_F8: apply_case("A01",3,100,[51,111],Vector2(51,111))
		KEY_F9: apply_case("A02",3,100,[35,36],Vector2(35,35))
