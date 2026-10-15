extends Node2D
const Movement = preload("res://scripts/core/movement.gd")
const WorldView = preload("res://scripts/world_view.gd")
@export var initial_map_path := "res://data/maps/A13.json"
@export var initial_cell := Vector2(61,39)
@export var preview_title := "R1 · original A13 source preview · story/STOP not yet implemented"
var movement = Movement.new()
var world = WorldView.new()
var status := Label.new()
var tick := 0
var ready_ok := false
var notice := "Left click: exact reachable cell | Hold Shift: run | G: collision overlay | Space: stop"

func _ready() -> void:
	add_child(world)
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := PanelContainer.new()
	panel.position=Vector2(12,12)
	panel.mouse_filter=Control.MOUSE_FILTER_IGNORE
	canvas.add_child(panel)
	status.add_theme_font_size_override("font_size",16)
	status.mouse_filter=Control.MOUSE_FILTER_IGNORE
	panel.add_child(status)
	movement.position=initial_cell
	ready_ok=world.setup(movement,initial_map_path)
	if not ready_ok:
		status.text="R1 RESOURCE PREFLIGHT FAILED\n"+"\n".join(world.loading_errors)
		push_error(status.text)
		return
	print("R1_SOURCE_READY map=%s cell=%s floors=%d objects=%d"%[world.map.id,movement.position,world.floors.size(),world.objects.size()])
	_update_status()

func _physics_process(delta: float) -> void:
	if not ready_ok: return
	tick+=1
	movement.step(delta,Input.is_key_pressed(KEY_SHIFT))
	world.tick=tick
	world.refresh()
	_update_status()

func _unhandled_input(event: InputEvent) -> void:
	if not ready_ok: return
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT:
		var target: Vector2i=world.to_cell(event.position)
		var accepted: bool=movement.request(target)
		notice="Target %s: %s"%[target,"route accepted" if accepted else "blocked / unreachable (unchanged)"]
		print("R1_CLICK cell=%s accepted=%s"%[target,accepted])
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode==KEY_SPACE: movement.stop()
		if event.keycode==KEY_G: world.show_grid=not world.show_grid

func _update_status() -> void:
	status.text=preview_title+"\nCell %.3f, %.3f | %s d%d frame%d | remaining %d\n%s"%[movement.position.x,movement.position.y,movement.action,movement.direction,movement.source_frame(),movement.path.size(),notice]
