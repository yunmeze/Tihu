extends "res://scripts/game_root.gd"
## Bounded NPC dialogue fixture; full map load scripts are deliberately outside this entry.
const VM = preload("res://scripts/core/dialogue_vm.gd")
var story: Dictionary = VM.initial_state()
var stopped := true
var current_npc := -1
var current_view: Dictionary = {}
var revision := 0
var dialog := Control.new()
var paragraph := Label.new()
var speaker := Label.new()
var choices := Control.new()
var images: Dictionary = {}
var event_log: Array = []
var target_map_paths := {"A00":"res://data/maps/A00.json"}

func _ready() -> void:
	story.et[0]=1
	super._ready()
	var canvas := CanvasLayer.new()
	add_child(canvas)
	canvas.add_child(dialog)
	dialog.position=Vector2(250,520)
	dialog.size=Vector2(523,216)
	dialog.mouse_filter=Control.MOUSE_FILTER_STOP
	var background := TextureRect.new()
	background.texture=load("res://assets/ui/original_dialog.png")
	background.mouse_filter=Control.MOUSE_FILTER_IGNORE
	dialog.add_child(background)
	var font := SystemFont.new()
	font.font_names=PackedStringArray(["Noto Sans CJK SC","Noto Sans CJK","sans-serif"])
	for label in [speaker,paragraph]:
		label.add_theme_font_override("font",font)
		label.add_theme_font_size_override("font_size",17)
		label.add_theme_color_override("font_color",Color("efe0b8"))
		label.mouse_filter=Control.MOUSE_FILTER_IGNORE
		dialog.add_child(label)
	speaker.position=Vector2(20,8)
	paragraph.position=Vector2(20,35)
	paragraph.size=Vector2(480,120)
	paragraph.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	dialog.add_child(choices)
	choices.mouse_filter=Control.MOUSE_FILTER_IGNORE
	dialog.hide()
	_update_status()

func _physics_process(delta: float) -> void:
	if not ready_ok: return
	tick+=1
	if not stopped and not dialog.visible: movement.step(delta,Input.is_key_pressed(KEY_SHIFT))
	world.tick=tick
	world.refresh()
	_update_status()

func _update_status() -> void:
	status.text="R3 NPC story candidate | ET0=%d | STOP=%s | %s (%.2f, %.2f)\nA13/A00 map load scripts NOT executed; no save/combat. Only the two opening NPCs.\n%s"%[story.et[0],stopped,world.map.get("id","?"),movement.position.x,movement.position.y,notice]

func _unhandled_input(event: InputEvent) -> void:
	if not ready_ok: return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode==KEY_ESCAPE:
		close_dialog()
		return
	if event is InputEventMouseButton and event.pressed and event.button_index==MOUSE_BUTTON_LEFT:
		if dialog.visible: return
		var index := npc_at(event.position)
		if index>=0:
			interact(index)
		elif stopped:
			notice="STOP: movement blocked; NPC conversation remains available."
		else:
			movement.request(world.to_cell(event.position))

func npc_at(point: Vector2) -> int:
	# Reverse actual depth order; opaque foreground prevents clicking through it.
	var entries: Array=world.ordered_objects()
	entries.reverse()
	for entry in entries:
		if entry.kind==-1: continue
		var index: int=entry.index
		if entry.kind==7: index+=(tick/17)%4
		elif entry.kind==5: index+=(tick/8)%5
		elif entry.kind==8:
			var phase: int=(tick/8)%10
			index=55+(phase if phase<5 else 9-phase)
		var pack: Dictionary=world.packs[entry.pack]
		var frame: Dictionary=pack.frames.get(str(index),{})
		if frame.is_empty(): continue
		var top: float=0.0 if entry.kind==7 else (-52.0 if entry.kind==8 else 32.0-float(frame.original[1]))
		var origin: Vector2=entry.origin+world.screen_origin()+Vector2(frame.crop[0],frame.crop[1]+top)
		if entry.kind==7: origin+=Vector2(frame.offset[0],frame.offset[1])
		var local: Vector2=point-origin
		if local.x<0 or local.y<0 or local.x>=frame.rect[2] or local.y>=frame.rect[3]: continue
		var file: String=pack.pages[int(frame.page)].file
		if not images.has(file): images[file]=world.textures[file].get_image()
		var color: Color=images[file].get_pixel(int(frame.rect[0]+local.x),int(frame.rect[1]+local.y))
		if color.a<0.1: continue
		# Original checker-shadow pixels must not acquire NPC interaction ownership.
		if entry.kind==7 and color.r8==16 and color.g8==8 and color.b8==8: continue
		if entry.kind!=7: return -1
		return int(entry.order)-int(world.map.width)*int(world.map.height)
	return -1

func interact(index: int) -> bool:
	if world.map.id!="A13" or index not in [0,1] or dialog.visible: return false
	var npc: Dictionary=world.map.npcs[index]
	if movement.position.distance_to(Vector2(npc.x,npc.y))>5.0: return false
	return apply_page(index,"START")

func choose(target: String, expected_revision: int) -> bool:
	if not dialog.visible or current_npc<0 or expected_revision!=revision: return false
	var allowed := false
	for button in current_view.buttons:
		if button.target==target: allowed=true
	if not allowed: return false
	return apply_page(current_npc,target)

func apply_page(index: int, process: String) -> bool:
	var result: Dictionary=VM.execute(world.map.npcs[index].script,story,process)
	if not result.ok:
		notice="Script rejected: "+str(result.error)
		return false
	return commit_candidate(result,index)

func commit_candidate(result: Dictionary,index: int) -> bool:
	var next_stop := stopped
	var next_world = null
	var next_movement = null
	var destination = null
	# Check every event before preparing or publishing any state.
	for event in result.events:
		match event.kind:
			"stop": next_stop=true
			"unstop": next_stop=false
			"close": pass
			"tomap":
				if destination!=null or not target_map_paths.has(event.map): return reject("Unsupported map event")
				destination=event
			_: return reject("Unsupported event: "+str(event.kind))
	if destination!=null:
		next_world=WorldView.new()
		next_movement=Movement.new()
		if not next_world.setup(next_movement,target_map_paths[destination.map]):
			var problem := str(next_world.loading_errors)
			next_world.free()
			return reject("Target resource preflight: "+problem)
		var cell := Vector2i(destination.x,destination.y)
		if next_world.map.id!=destination.map or not next_movement.can_enter(cell):
			next_world.free()
			return reject("Invalid target coordinate")
		next_movement.position=Vector2(cell)
	# Commit: all potentially failing work above; no load-script execution is implied.
	story=result.state.duplicate(true)
	stopped=next_stop
	revision+=1
	movement.stop()
	if next_world!=null:
		var old_world=world
		world=next_world
		movement=next_movement
		remove_child(old_world)
		add_child(world)
		move_child(world,0)
		old_world.queue_free()
		images.clear()
		world.tick=tick
		world.refresh()
		close_dialog()
	else:
		current_npc=index
		current_view=result.duplicate(true)
		if result.closed: close_dialog()
		else: render_dialog()
	event_log.append({"page":result.page,"et0":story.et[0],"stop":stopped,"map":world.map.id,"events":result.events.duplicate(true)})
	print("R3_COMMIT ",JSON.stringify(event_log.back()))
	notice="NPC page committed. Map load scripts remain outside this diagnostic."
	_update_status()
	return true

func reject(message: String) -> bool:
	notice=message+"; original state retained."
	print("R3_REJECT ",notice)
	return false

func close_dialog() -> void:
	dialog.hide()
	current_npc=-1
	current_view={}
	revision+=1

func render_dialog() -> void:
	for child in choices.get_children():
		choices.remove_child(child)
		child.queue_free()
	speaker.text=world.map.npcs[current_npc].name
	paragraph.text="\n".join(current_view.text).replace("\ue810"," ")
	for record in current_view.buttons:
		var button := Button.new()
		button.text=record.label
		button.position=Vector2(20+int(record.x)*16,20+int(record.y)*16)
		button.add_theme_font_override("font",paragraph.get_theme_font("font"))
		button.add_theme_font_size_override("font_size",17)
		button.add_theme_color_override("font_color",Color("efd369"))
		button.pressed.connect(choose.bind(record.target,revision))
		choices.add_child(button)
	dialog.show()
