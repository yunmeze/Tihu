extends Node
## Reconstructed source archive, not engine-validated or integrated.
## Generated 2D master recoloring only; no world mutation or CPU image transformation.
signal completed(request_id: int, ok: bool, reason: String)
const PINS_PATH := "res://data/art/barrier_phase_pins_recovered.json"
const PINS_SHA := "aaca599619346555e8209b2d7acc3db7f3fd6ab393ba2114c8774b13cf10ffca"
const TIMEOUT_MSEC := 10000
const SIZE := Vector2i(384,736)
var diagnostic_validator: Callable
var last_error: String = ""
var _serial: int = 0
var _post_draw: int = 0
var _job: Dictionary = {}
var _active: Dictionary = {}
var _retired: Array[Dictionary] = []
var _world_ref: WeakRef

func _ready() -> void:
	RenderingServer.frame_post_draw.connect(_after_draw)

func bind_world(world: Object) -> void:
	_world_ref = weakref(world)

func _now_msec() -> int:
	return Time.get_ticks_msec()

func _check_deadline(candidate: int) -> bool:
	# A callback may replace/cancel staging. Never cancel its successor.
	if _job.is_empty() or int(_job.ticket) != candidate: return false
	if _now_msec()-int(_job.started) > TIMEOUT_MSEC:
		_fail_job("No completed GPU pass within timeout; active cache unchanged")
		return false
	return true

func request_prepare() -> int:
	cancel_pending("Superseded")
	_serial += 1
	var ticket: int = _serial
	last_error = ""
	if not is_inside_tree():
		_reject_later(ticket,"Cache must be in scene tree")
		return ticket
	if RenderingServer.get_current_rendering_method() != "gl_compatibility" or get_viewport().use_hdr_2d:
		_reject_later(ticket,"Only GL Compatibility SDR 2D supported")
		return ticket
	var inputs: Dictionary = _load_verified_inputs()
	if inputs.is_empty():
		_reject_later(ticket,last_error)
		return ticket
	var branch := Node.new()
	add_child(branch)
	_job = {"ticket":ticket,"root":branch,"inputs":inputs,"entries":[],"viewports":[],
		"started":_now_msec(),"armed_after":_post_draw}
	for offset in inputs.contract.phase_hue_offset_degrees:
		_job.entries.append(_make_pass(float(offset)/360.0))
	return ticket

func _verified_bytes(path: String, expected: String) -> PackedByteArray:
	if not FileAccess.file_exists(path):
		last_error = "Missing pinned input: "+path
		return PackedByteArray()
	var data: PackedByteArray = FileAccess.get_file_as_bytes(path)
	var hasher := HashingContext.new()
	hasher.start(HashingContext.HASH_SHA256)
	hasher.update(data)
	if hasher.finish().hex_encode() != expected:
		last_error = "SHA mismatch: "+path
		return PackedByteArray()
	return data

func _load_verified_inputs() -> Dictionary:
	var bytes: PackedByteArray = _verified_bytes(PINS_PATH,PINS_SHA)
	if bytes.is_empty(): return {}
	var parsed: Variant = JSON.parse_string(bytes.get_string_from_utf8())
	if not parsed is Dictionary or parsed.get("schema") != "barrier-recovered-pins-v1":
		last_error = "Invalid input pins"
		return {}
	var pins: Dictionary = parsed
	var data: Dictionary = {}
	for path in pins.sha256:
		var checked: PackedByteArray = _verified_bytes(path,pins.sha256[path])
		if checked.is_empty(): return {}
		data[path] = checked
	var contract_value: Variant = JSON.parse_string(data[pins.contract].get_string_from_utf8())
	if not contract_value is Dictionary:
		last_error = "Invalid phase contract"
		return {}
	var contract: Dictionary = contract_value
	if contract.get("phase_hue_offset_degrees",[]).size()!=5 or contract.get("owners",[]).size()!=15:
		last_error = "Invalid phase/owner count"
		return {}
	var master_image := Image.new()
	if master_image.load_png_from_buffer(data[pins.master]) != OK or master_image.get_size()!=SIZE:
		last_error = "Invalid master PNG/dimensions"
		return {}
	var shader := Shader.new()
	shader.code = data[pins.shader].get_string_from_utf8()
	# Decode/upload only. No resize, hue transform, pixel writes or PNG export on CPU.
	return {"master":ImageTexture.create_from_image(master_image),"master_image":master_image,
		"shader":shader,"contract":contract,"pins":pins}

func _make_pass(offset: float) -> Dictionary:
	var viewport := SubViewport.new()
	viewport.size=SIZE
	viewport.world_2d=World2D.new()
	viewport.disable_3d=true
	viewport.transparent_bg=true
	viewport.use_hdr_2d=false
	viewport.msaa_2d=Viewport.MSAA_DISABLED
	viewport.render_target_clear_mode=SubViewport.CLEAR_MODE_ALWAYS
	viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED
	var material := ShaderMaterial.new()
	material.shader=_job.inputs.shader
	material.set_shader_parameter("master_texture",_job.inputs.master)
	material.set_shader_parameter("hue_offset",offset)
	var quad := ColorRect.new()
	quad.size=Vector2(SIZE)
	quad.mouse_filter=Control.MOUSE_FILTER_IGNORE
	quad.material=material
	viewport.add_child(quad)
	_job.root.add_child(viewport)
	viewport.render_target_update_mode=SubViewport.UPDATE_ONCE
	var texture: ViewportTexture=viewport.get_texture()
	var canvas := CanvasTexture.new()
	canvas.diffuse_texture=texture
	canvas.texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
	canvas.texture_repeat=CanvasItem.TEXTURE_REPEAT_DISABLED
	_job.viewports.append(viewport)
	return {"viewport":viewport,"texture":texture,"canvas":canvas,"material":material}

func _after_draw() -> void:
	_post_draw+=1
	for i in range(_retired.size()-1,-1,-1):
		if _post_draw>=int(_retired[i].retire_after):
			_destroy_bundle(_retired[i])
			_retired.remove_at(i)
	if _job.is_empty() or _post_draw<=int(_job.armed_after): return
	for viewport in _job.viewports:
		if not is_instance_valid(viewport) or not viewport.is_inside_tree():
			_fail_job("Staging viewport lost")
			return
		if RenderingServer.viewport_get_update_mode(viewport.get_viewport_rid()) != RenderingServer.VIEWPORT_UPDATE_DISABLED: return
	if not diagnostic_validator.is_valid():
		_fail_job("No diagnostic validator; cannot publish")
		return
	var candidate: int=_job.ticket
	if not _check_deadline(candidate): return
	var passed: bool=bool(diagnostic_validator.call(_job.duplicate(false)))
	if not _check_deadline(candidate): return
	if not passed:
		_fail_job("Diagnostic pixel gate rejected cache")
		return
	var previous: Dictionary=_active
	if not _check_deadline(candidate): return
	_active=_job
	_job={}
	if not previous.is_empty():
		previous.retire_after=_post_draw+2
		_retired.append(previous)
	completed.emit(candidate,true,"")

func _process(_delta: float) -> void:
	if not _job.is_empty(): _check_deadline(int(_job.ticket))

func snapshot() -> Dictionary:
	return _active.duplicate(false)

func cancel_pending(reason: String="Cancelled") -> void:
	if _job.is_empty(): return
	var ticket: int=_job.ticket
	var cancelled: Dictionary=_job
	_job={}
	_destroy_bundle(cancelled)
	_send_result.call_deferred(ticket,false,reason)

func clear() -> void:
	cancel_pending("Cleared")
	_destroy_bundle(_active)
	_active={}
	for bundle in _retired: _destroy_bundle(bundle)
	_retired.clear()

func _fail_job(reason: String) -> void:
	last_error=reason
	cancel_pending(reason)

func _reject_later(ticket: int,reason: String) -> void:
	last_error=reason
	_send_result.call_deferred(ticket,false,reason)

func _send_result(ticket: int,ok: bool,reason: String) -> void:
	completed.emit(ticket,ok,reason)

func _destroy_bundle(bundle: Dictionary) -> void:
	if bundle.is_empty(): return
	for viewport in bundle.get("viewports",[]):
		if is_instance_valid(viewport): viewport.render_target_update_mode=SubViewport.UPDATE_DISABLED
	var branch: Node=bundle.get("root")
	if is_instance_valid(branch): branch.queue_free()
	bundle.clear()

func _exit_tree() -> void:
	if RenderingServer.frame_post_draw.is_connected(_after_draw): RenderingServer.frame_post_draw.disconnect(_after_draw)
	clear()

static func phase_frame(tick: int) -> int:
	var phase: int=(tick/8)%10
	return 55+(phase if phase<5 else 9-phase)

static func _same_json(actual: Variant,expected: Variant) -> bool:
	if expected is int or expected is float:
		return (actual is int or actual is float) and is_finite(float(actual)) and float(actual)==float(expected)
	if expected is Array:
		if not actual is Array or actual.size()!=expected.size(): return false
		for i in expected.size():
			if not _same_json(actual[i],expected[i]): return false
		return true
	if expected is Dictionary:
		if not actual is Dictionary or actual.size()!=expected.size(): return false
		for key in expected:
			if not actual.has(key) or not _same_json(actual[key],expected[key]): return false
		return true
	return typeof(actual)==typeof(expected) and actual==expected

func eligible_owner(world,pack: String,index: int,origin: Vector2,use_offset: bool,top: float) -> bool:
	if _active.is_empty() or _world_ref==null or _world_ref.get_ref()!=world: return false
	if pack!="Data4" or index<55 or index>59 or use_offset or top!=-52.0: return false
	if str(world.map.get("id",""))!="A00" or not _same_json(world.map.get("height"),150): return false
	if index!=phase_frame(int(world.tick)): return false
	var contract: Dictionary=_active.inputs.contract
	if not _same_json(world.packs.get(pack,{}).get("frames",{}).get(str(index)),contract.source_frames[str(index)]): return false
	var screen: Vector2=world.screen_origin()
	for owner in contract.owners:
		var cell:=Vector2i(int(owner.cell[0]),int(owner.cell[1]))
		var base:=Vector2(cell.x*48,cell.y*32)
		if origin!=base+screen: continue
		var at: int=cell.x*150+cell.y
		if not world.map.get("cells") is Array or at>=world.map.cells.size(): return false
		var current: Array=world.map.cells[at]
		if current.size()!=4: return false
		for field in 4:
			if not _same_json(current[field],owner.tuple[field]): return false
		var matches: int=0
		for entry in world.objects:
			if entry.get("origin",Vector2.INF)!=base or str(entry.get("pack",""))!="Data4": continue
			if not _same_json(entry.get("kind"),8) or not _same_json(entry.get("index"),1): return false
			if not _same_json(entry.get("layer"),1) or not _same_json(entry.get("y"),cell.y): return false
			if not _same_json(entry.get("order"),owner.order): return false
			matches+=1
		return matches==1
	return false

func try_draw(canvas: CanvasItem,world,pack: String,index: int,origin: Vector2,use_offset: bool,top: float) -> bool:
	if not eligible_owner(world,pack,index,origin,use_offset,top): return false
	if RenderingServer.get_current_rendering_method()!="gl_compatibility" or canvas.get_viewport().use_hdr_2d: return false
	var destination:=Rect2(origin+Vector2(0,-52),Vector2(48,92))
	if destination.intersects(canvas.get_viewport_rect()):
		canvas.draw_texture_rect_region(_active.entries[index-55].canvas,destination,Rect2(Vector2.ZERO,Vector2(SIZE)),Color.WHITE,false,false)
	return true
